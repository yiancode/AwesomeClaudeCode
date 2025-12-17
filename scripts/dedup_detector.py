#!/usr/bin/env python3
"""
重复检测脚本 / Duplicate Detection Script

检测候选资源与现有资源之间的重复，使用多种策略：
1. URL 规范化匹配
2. 名称相似度（Jaccard/编辑距离）
3. 描述相似度
4. GitHub owner/repo 匹配

用法 / Usage:
    python scripts/dedup_detector.py [--check-pending] [--report]
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import yaml

# 项目根目录 / Project root
PROJECT_ROOT = Path(__file__).parent.parent


def load_config() -> dict:
    """加载 AI 配置 / Load AI configuration"""
    config_file = PROJECT_ROOT / "config" / "ai_config.yaml"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def normalize_url(url: str, config: dict = None) -> str:
    """
    规范化 URL / Normalize URL

    Args:
        url: 原始 URL / Original URL
        config: 配置 / Configuration

    Returns:
        规范化后的 URL / Normalized URL
    """
    if not url:
        return ''

    config = config or {}
    dedup_config = config.get('deduplication', {})

    # 基本清理
    url = url.strip()

    # 移除协议
    url = re.sub(r'^https?://', '', url)

    # 移除 www
    if dedup_config.get('strip_www', True):
        url = re.sub(r'^www\.', '', url)

    # 移除末尾斜杠
    if dedup_config.get('strip_trailing_slash', True):
        url = url.rstrip('/')

    # 转小写
    if dedup_config.get('lowercase', True):
        url = url.lower()

    # 移除查询参数和锚点
    url = re.sub(r'[?#].*$', '', url)

    # 移除 .git 后缀
    url = re.sub(r'\.git$', '', url)

    return url


def extract_github_repo(url: str) -> Optional[Tuple[str, str]]:
    """
    从 URL 提取 GitHub owner/repo / Extract GitHub owner/repo from URL

    Returns: (owner, repo) or None
    """
    normalized = normalize_url(url)

    if 'github.com' not in normalized:
        return None

    # 匹配 github.com/owner/repo
    match = re.search(r'github\.com/([^/]+)/([^/]+)', normalized)
    if match:
        return (match.group(1).lower(), match.group(2).lower())

    return None


def jaccard_similarity(str1: str, str2: str) -> float:
    """
    计算 Jaccard 相似度 / Calculate Jaccard similarity

    Args:
        str1: 字符串1 / String 1
        str2: 字符串2 / String 2

    Returns:
        相似度 (0-1) / Similarity (0-1)
    """
    if not str1 or not str2:
        return 0.0

    # 分词
    words1 = set(re.findall(r'\w+', str1.lower()))
    words2 = set(re.findall(r'\w+', str2.lower()))

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    计算 Levenshtein 编辑距离 / Calculate Levenshtein edit distance

    Args:
        s1: 字符串1 / String 1
        s2: 字符串2 / String 2

    Returns:
        编辑距离 / Edit distance
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def name_similarity(name1: str, name2: str) -> float:
    """
    计算名称相似度 / Calculate name similarity

    结合 Jaccard 和归一化编辑距离
    Combines Jaccard and normalized edit distance

    Args:
        name1: 名称1 / Name 1
        name2: 名称2 / Name 2

    Returns:
        相似度 (0-1) / Similarity (0-1)
    """
    if not name1 or not name2:
        return 0.0

    name1 = name1.lower().strip()
    name2 = name2.lower().strip()

    # 完全匹配
    if name1 == name2:
        return 1.0

    # Jaccard 相似度
    jaccard = jaccard_similarity(name1, name2)

    # 归一化编辑距离
    max_len = max(len(name1), len(name2))
    edit_dist = levenshtein_distance(name1, name2)
    normalized_edit = 1 - (edit_dist / max_len)

    # 加权平均
    return 0.4 * jaccard + 0.6 * normalized_edit


def load_existing_resources() -> List[dict]:
    """加载现有资源 / Load existing resources"""
    resources = []

    # 从 CSV 加载
    csv_file = PROJECT_ROOT / 'THE_RESOURCES_TABLE.csv'
    if csv_file.exists():
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['_source'] = 'csv'
                resources.append(row)

    return resources


def load_pending_resources() -> List[dict]:
    """加载待审核资源 / Load pending resources"""
    pending_file = PROJECT_ROOT / 'candidates' / 'pending_resources.json'
    if pending_file.exists():
        with open(pending_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            resources = data.get('resources', [])
            for r in resources:
                r['_source'] = 'pending'
            return resources
    return []


def load_rejected_resources() -> List[dict]:
    """加载已拒绝资源 / Load rejected resources"""
    rejected_file = PROJECT_ROOT / 'candidates' / 'rejected_resources.json'
    if rejected_file.exists():
        with open(rejected_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            resources = data.get('resources', [])
            for r in resources:
                r['_source'] = 'rejected'
            return resources
    return []


class DuplicateDetector:
    """重复检测器 / Duplicate Detector"""

    def __init__(self, config: dict = None):
        """
        初始化检测器 / Initialize detector

        Args:
            config: 配置 / Configuration
        """
        self.config = config or load_config()
        self.dedup_config = self.config.get('deduplication', {})

        # 相似度阈值
        self.name_threshold = self.dedup_config.get('name_similarity_threshold', 0.85)
        self.desc_threshold = self.dedup_config.get('description_similarity_threshold', 0.80)

        # 加载资源
        self.existing_resources = load_existing_resources()
        self.rejected_resources = load_rejected_resources()

        # 构建索引
        self._build_indexes()

    def _build_indexes(self):
        """构建索引以加速查找 / Build indexes for faster lookup"""
        self.url_index = {}  # normalized_url -> resource
        self.github_index = {}  # (owner, repo) -> resource
        self.name_index = defaultdict(list)  # first_word -> [resources]

        all_resources = self.existing_resources + self.rejected_resources

        for res in all_resources:
            url = res.get('PrimaryLink', '')

            # URL 索引
            normalized = normalize_url(url, self.config)
            if normalized:
                self.url_index[normalized] = res

            # GitHub 索引
            github_repo = extract_github_repo(url)
            if github_repo:
                self.github_index[github_repo] = res

            # 名称索引（用于加速相似度搜索）
            name = res.get('DisplayName', '')
            if name:
                words = name.lower().split()
                if words:
                    self.name_index[words[0]].append(res)

    def check_url_duplicate(self, url: str) -> Optional[dict]:
        """
        检查 URL 重复 / Check URL duplicate

        Args:
            url: 要检查的 URL / URL to check

        Returns:
            重复的资源或 None / Duplicate resource or None
        """
        normalized = normalize_url(url, self.config)
        if normalized in self.url_index:
            return self.url_index[normalized]
        return None

    def check_github_duplicate(self, url: str) -> Optional[dict]:
        """
        检查 GitHub 仓库重复 / Check GitHub repository duplicate

        Args:
            url: 要检查的 URL / URL to check

        Returns:
            重复的资源或 None / Duplicate resource or None
        """
        github_repo = extract_github_repo(url)
        if github_repo and github_repo in self.github_index:
            return self.github_index[github_repo]
        return None

    def check_name_similarity(self, name: str) -> List[Tuple[dict, float]]:
        """
        检查名称相似度 / Check name similarity

        Args:
            name: 要检查的名称 / Name to check

        Returns:
            相似资源列表 [(resource, similarity), ...] / List of similar resources
        """
        similar = []

        if not name:
            return similar

        # 使用索引缩小搜索范围
        words = name.lower().split()
        candidates = set()

        for word in words[:3]:  # 只用前3个词
            for res in self.name_index.get(word, []):
                candidates.add(id(res))

        # 如果候选太少，搜索所有
        if len(candidates) < 10:
            all_resources = self.existing_resources + self.rejected_resources
        else:
            all_resources = [r for r in (self.existing_resources + self.rejected_resources)
                           if id(r) in candidates]

        for res in all_resources:
            res_name = res.get('DisplayName', '')
            similarity = name_similarity(name, res_name)

            if similarity >= self.name_threshold:
                similar.append((res, similarity))

        # 按相似度排序
        similar.sort(key=lambda x: x[1], reverse=True)

        return similar

    def check_description_similarity(self, description: str) -> List[Tuple[dict, float]]:
        """
        检查描述相似度 / Check description similarity

        Args:
            description: 要检查的描述 / Description to check

        Returns:
            相似资源列表 [(resource, similarity), ...] / List of similar resources
        """
        similar = []

        if not description or len(description) < 20:
            return similar

        all_resources = self.existing_resources + self.rejected_resources

        for res in all_resources:
            res_desc = res.get('Description', '') or res.get('Description_ZH', '')
            if not res_desc:
                continue

            similarity = jaccard_similarity(description, res_desc)

            if similarity >= self.desc_threshold:
                similar.append((res, similarity))

        similar.sort(key=lambda x: x[1], reverse=True)

        return similar[:5]  # 只返回前5个

    def check_resource(self, resource: dict) -> dict:
        """
        检查单个资源的所有重复可能 / Check all duplicate possibilities for a single resource

        Args:
            resource: 要检查的资源 / Resource to check

        Returns:
            检查结果 / Check result
        """
        url = resource.get('PrimaryLink', '')
        name = resource.get('DisplayName', '')
        description = resource.get('Description', '') or resource.get('Description_ZH', '')

        result = {
            'resource_id': resource.get('ID', ''),
            'resource_name': name,
            'resource_url': url,
            'is_duplicate': False,
            'duplicate_type': None,
            'matched_resource': None,
            'similarity_score': 0,
            'checks': {}
        }

        # 1. URL 精确匹配
        url_match = self.check_url_duplicate(url)
        result['checks']['url'] = {
            'passed': url_match is None,
            'matched': url_match.get('DisplayName') if url_match else None
        }

        if url_match:
            result['is_duplicate'] = True
            result['duplicate_type'] = 'url_exact'
            result['matched_resource'] = url_match
            result['similarity_score'] = 1.0
            return result

        # 2. GitHub 仓库匹配
        github_match = self.check_github_duplicate(url)
        result['checks']['github'] = {
            'passed': github_match is None,
            'matched': github_match.get('DisplayName') if github_match else None
        }

        if github_match:
            result['is_duplicate'] = True
            result['duplicate_type'] = 'github_repo'
            result['matched_resource'] = github_match
            result['similarity_score'] = 1.0
            return result

        # 3. 名称相似度
        name_similar = self.check_name_similarity(name)
        result['checks']['name'] = {
            'passed': len(name_similar) == 0,
            'similar': [(r.get('DisplayName'), s) for r, s in name_similar[:3]]
        }

        if name_similar:
            best_match, best_score = name_similar[0]
            if best_score >= 0.95:  # 非常相似
                result['is_duplicate'] = True
                result['duplicate_type'] = 'name_similar'
                result['matched_resource'] = best_match
                result['similarity_score'] = best_score
                return result

        # 4. 描述相似度
        desc_similar = self.check_description_similarity(description)
        result['checks']['description'] = {
            'passed': len(desc_similar) == 0,
            'similar': [(r.get('DisplayName'), s) for r, s in desc_similar[:3]]
        }

        if desc_similar:
            best_match, best_score = desc_similar[0]
            if best_score >= 0.95:  # 非常相似
                result['is_duplicate'] = True
                result['duplicate_type'] = 'description_similar'
                result['matched_resource'] = best_match
                result['similarity_score'] = best_score
                return result

        return result

    def check_all_pending(self) -> List[dict]:
        """
        检查所有待审核资源 / Check all pending resources

        Returns:
            检查结果列表 / List of check results
        """
        pending = load_pending_resources()
        results = []

        for resource in pending:
            result = self.check_resource(resource)
            results.append(result)

        return results


def generate_report(results: List[dict]) -> str:
    """
    生成重复检测报告 / Generate duplicate detection report

    Args:
        results: 检查结果列表 / List of check results

    Returns:
        报告内容 / Report content
    """
    lines = [
        "# 重复检测报告 / Duplicate Detection Report",
        f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n检查资源数: {len(results)}",
        "\n---\n"
    ]

    # 统计
    duplicates = [r for r in results if r['is_duplicate']]
    passed = [r for r in results if not r['is_duplicate']]

    lines.extend([
        "## 统计摘要 / Summary",
        f"- 检查总数: {len(results)}",
        f"- 发现重复: {len(duplicates)}",
        f"- 通过检查: {len(passed)}",
        "\n---\n"
    ])

    # 重复列表
    if duplicates:
        lines.extend([
            "## ⚠️ 发现的重复 / Duplicates Found",
            ""
        ])

        lines.append("| 资源 | 重复类型 | 匹配资源 | 相似度 |")
        lines.append("|------|---------|---------|--------|")

        for r in duplicates:
            matched = r.get('matched_resource', {})
            matched_name = matched.get('DisplayName', 'Unknown') if matched else 'Unknown'
            lines.append(
                f"| {r['resource_name']} | {r['duplicate_type']} | "
                f"{matched_name} | {r['similarity_score']:.2f} |"
            )

        lines.append("\n---\n")

    # 通过列表
    if passed:
        lines.extend([
            "## ✅ 通过检查 / Passed",
            ""
        ])

        for r in passed:
            lines.append(f"- {r['resource_name']}")

    return '\n'.join(lines)


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description='Duplicate detection')
    parser.add_argument('--check-pending', action='store_true', help='Check pending resources')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--output', type=str, help='Output file for report')
    parser.add_argument('--url', type=str, help='Check specific URL')
    parser.add_argument('--name', type=str, help='Check specific name')
    args = parser.parse_args()

    print("🔍 重复检测 / Duplicate Detection")
    print("=" * 50)

    # 加载配置
    config = load_config()
    detector = DuplicateDetector(config)

    print(f"\n📊 已加载 {len(detector.existing_resources)} 个现有资源")
    print(f"   已加载 {len(detector.rejected_resources)} 个已拒绝资源")

    # 单个 URL 检查
    if args.url:
        print(f"\n🔗 检查 URL: {args.url}")
        result = detector.check_url_duplicate(args.url)
        if result:
            print(f"   ⚠️ 发现重复: {result.get('DisplayName')}")
        else:
            print("   ✅ 未发现重复")

        github_result = detector.check_github_duplicate(args.url)
        if github_result:
            print(f"   ⚠️ GitHub 重复: {github_result.get('DisplayName')}")

        return 0

    # 单个名称检查
    if args.name:
        print(f"\n📝 检查名称: {args.name}")
        similar = detector.check_name_similarity(args.name)
        if similar:
            print("   相似资源:")
            for res, score in similar[:5]:
                print(f"   - {res.get('DisplayName')} (相似度: {score:.2f})")
        else:
            print("   ✅ 未发现相似资源")

        return 0

    # 检查所有待审核
    if args.check_pending:
        print("\n📋 检查待审核资源...")
        results = detector.check_all_pending()

        duplicates = [r for r in results if r['is_duplicate']]
        print(f"\n   检查完成: {len(results)} 个资源")
        print(f"   发现重复: {len(duplicates)} 个")

        if duplicates:
            print("\n   重复列表:")
            for r in duplicates:
                matched = r.get('matched_resource', {})
                print(f"   - {r['resource_name']} ({r['duplicate_type']})")
                print(f"     匹配: {matched.get('DisplayName', 'Unknown')}")

        # 生成报告
        if args.report:
            report = generate_report(results)

            if args.output:
                output_file = Path(args.output)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"\n   📄 报告已保存: {output_file}")
            else:
                print("\n" + report)

        return 0

    # 默认：显示帮助
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
