#!/usr/bin/env python3
"""
依赖分析脚本 / Dependency Analyzer Script

分析现有资源的依赖关系，发现相关的新资源：
1. 分析 package.json / requirements.txt / Cargo.toml 等依赖文件
2. 发现常用的相关库
3. 识别生态系统中的核心依赖

用法 / Usage:
    python scripts/dependency_analyzer.py [--analyze] [--discover]
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import requests
import yaml

# 项目根目录 / Project root
PROJECT_ROOT = Path(__file__).parent.parent


def load_categories() -> dict:
    """加载分类定义 / Load category definitions"""
    categories_file = PROJECT_ROOT / "templates" / "categories.yaml"
    with open(categories_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return {cat['id']: cat['prefix'] for cat in data['categories']}


def load_existing_resources() -> List[dict]:
    """加载现有资源 / Load existing resources"""
    resources = []
    csv_file = PROJECT_ROOT / 'THE_RESOURCES_TABLE.csv'

    if csv_file.exists():
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                resources.append(row)

    return resources


def load_existing_urls() -> Set[str]:
    """加载所有已存在的 URL / Load all existing URLs"""
    urls = set()

    # 从 CSV 加载
    csv_file = PROJECT_ROOT / 'THE_RESOURCES_TABLE.csv'
    if csv_file.exists():
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get('PrimaryLink', '').strip().rstrip('/').lower()
                if url:
                    urls.add(url)

    # 从 pending 加载
    pending_file = PROJECT_ROOT / 'candidates' / 'pending_resources.json'
    if pending_file.exists():
        with open(pending_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for res in data.get('resources', []):
                url = res.get('PrimaryLink', '').strip().rstrip('/').lower()
                if url:
                    urls.add(url)

    return urls


def extract_github_info(url: str) -> Optional[Tuple[str, str]]:
    """从 URL 提取 GitHub owner/repo / Extract GitHub owner/repo from URL"""
    if 'github.com' not in url:
        return None

    parts = url.rstrip('/').split('/')
    try:
        github_index = next(i for i, p in enumerate(parts) if 'github.com' in p)
        if len(parts) > github_index + 2:
            owner = parts[github_index + 1]
            repo = parts[github_index + 2].replace('.git', '')
            return (owner, repo)
    except (StopIteration, IndexError):
        pass

    return None


class DependencyAnalyzer:
    """依赖分析器 / Dependency Analyzer"""

    # 相关的包名模式
    RELEVANT_PATTERNS = [
        r'anthropic',
        r'claude',
        r'mcp[-_]?',
        r'model[-_]?context[-_]?protocol',
        r'llm[-_]?',
        r'ai[-_]?assistant',
    ]

    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'AwesomeClaudeCode-Bot/1.0'

        if self.github_token:
            self.session.headers['Authorization'] = f'Bearer {self.github_token}'

        self.categories_prefix = load_categories()
        self.existing_urls = load_existing_urls()

        # 依赖统计
        self.dependency_counts = Counter()
        self.dependency_sources = defaultdict(list)

    def _get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """
        获取仓库文件内容 / Get repository file content

        Args:
            owner: 仓库所有者 / Repository owner
            repo: 仓库名 / Repository name
            path: 文件路径 / File path

        Returns:
            文件内容或 None / File content or None
        """
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return response.text

            # 尝试 master 分支
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{path}"
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return response.text

        except requests.exceptions.RequestException:
            pass

        return None

    def _parse_package_json(self, content: str) -> List[str]:
        """解析 package.json 依赖 / Parse package.json dependencies"""
        dependencies = []

        try:
            data = json.loads(content)

            # 合并所有依赖
            for key in ['dependencies', 'devDependencies', 'peerDependencies']:
                deps = data.get(key, {})
                dependencies.extend(deps.keys())

        except json.JSONDecodeError:
            pass

        return dependencies

    def _parse_requirements_txt(self, content: str) -> List[str]:
        """解析 requirements.txt 依赖 / Parse requirements.txt dependencies"""
        dependencies = []

        for line in content.split('\n'):
            line = line.strip()

            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue

            # 移除版本约束
            package = re.split(r'[<>=!~\[]', line)[0].strip()
            if package:
                dependencies.append(package)

        return dependencies

    def _parse_pyproject_toml(self, content: str) -> List[str]:
        """解析 pyproject.toml 依赖 / Parse pyproject.toml dependencies"""
        dependencies = []

        # 简单的 TOML 解析
        # 查找 dependencies 部分
        dep_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if dep_match:
            deps_str = dep_match.group(1)
            # 提取包名
            packages = re.findall(r'"([^"]+)"', deps_str)
            for pkg in packages:
                # 移除版本约束
                package = re.split(r'[<>=!~\[]', pkg)[0].strip()
                if package:
                    dependencies.append(package)

        return dependencies

    def _parse_cargo_toml(self, content: str) -> List[str]:
        """解析 Cargo.toml 依赖 / Parse Cargo.toml dependencies"""
        dependencies = []

        # 查找 [dependencies] 部分
        in_deps = False
        for line in content.split('\n'):
            line = line.strip()

            if line.startswith('[dependencies]'):
                in_deps = True
                continue
            elif line.startswith('[') and in_deps:
                in_deps = False

            if in_deps and '=' in line:
                package = line.split('=')[0].strip()
                if package:
                    dependencies.append(package)

        return dependencies

    def _is_relevant_package(self, package: str) -> bool:
        """检查包是否相关 / Check if package is relevant"""
        package_lower = package.lower()

        for pattern in self.RELEVANT_PATTERNS:
            if re.search(pattern, package_lower):
                return True

        return False

    def analyze_repository(self, owner: str, repo: str) -> List[str]:
        """
        分析单个仓库的依赖 / Analyze dependencies of single repository

        Args:
            owner: 仓库所有者 / Repository owner
            repo: 仓库名 / Repository name

        Returns:
            相关依赖列表 / List of relevant dependencies
        """
        relevant_deps = []

        # 尝试各种依赖文件
        dep_files = [
            ('package.json', self._parse_package_json),
            ('requirements.txt', self._parse_requirements_txt),
            ('pyproject.toml', self._parse_pyproject_toml),
            ('Cargo.toml', self._parse_cargo_toml),
        ]

        for filename, parser in dep_files:
            content = self._get_file_content(owner, repo, filename)
            if content:
                deps = parser(content)
                for dep in deps:
                    if self._is_relevant_package(dep):
                        relevant_deps.append(dep)
                        self.dependency_counts[dep] += 1
                        self.dependency_sources[dep].append(f"{owner}/{repo}")

        return relevant_deps

    def analyze_all_resources(self) -> Dict[str, List[str]]:
        """
        分析所有资源的依赖 / Analyze dependencies of all resources

        Returns:
            资源到依赖的映射 / Mapping of resources to dependencies
        """
        resources = load_existing_resources()
        results = {}

        print(f"   分析 {len(resources)} 个资源...")

        for i, res in enumerate(resources):
            url = res.get('PrimaryLink', '')
            github_info = extract_github_info(url)

            if not github_info:
                continue

            owner, repo = github_info
            print(f"   [{i+1}/{len(resources)}] {owner}/{repo}...", end=' ')

            deps = self.analyze_repository(owner, repo)

            if deps:
                results[f"{owner}/{repo}"] = deps
                print(f"找到 {len(deps)} 个相关依赖")
            else:
                print("无相关依赖")

        return results

    def get_popular_dependencies(self, min_count: int = 2) -> List[Tuple[str, int]]:
        """
        获取常用依赖 / Get popular dependencies

        Args:
            min_count: 最小出现次数 / Minimum occurrence count

        Returns:
            依赖及其出现次数列表 / List of dependencies and their counts
        """
        return [(dep, count) for dep, count in self.dependency_counts.most_common()
                if count >= min_count]

    def discover_related_packages(self) -> List[dict]:
        """
        发现相关的包/库 / Discover related packages/libraries

        Returns:
            发现的候选资源列表 / List of discovered candidate resources
        """
        candidates = []

        # 获取常用依赖
        popular = self.get_popular_dependencies(min_count=2)

        print(f"\n📦 发现 {len(popular)} 个常用相关依赖:")

        for dep, count in popular:
            print(f"   - {dep} (出现 {count} 次)")

            # 尝试找到包的 GitHub 仓库
            package_url = self._find_package_repo(dep)

            if package_url and package_url.lower() not in self.existing_urls:
                candidate = self._create_candidate(dep, package_url, count)
                if candidate:
                    candidates.append(candidate)

        return candidates

    def _find_package_repo(self, package: str) -> Optional[str]:
        """
        尝试找到包的 GitHub 仓库 / Try to find package's GitHub repository

        Args:
            package: 包名 / Package name

        Returns:
            GitHub URL 或 None / GitHub URL or None
        """
        # 尝试 npm
        npm_url = f"https://registry.npmjs.org/{package}"
        try:
            response = self.session.get(npm_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                repo = data.get('repository', {})
                if isinstance(repo, dict):
                    url = repo.get('url', '')
                elif isinstance(repo, str):
                    url = repo
                else:
                    url = ''

                if 'github.com' in url:
                    # 清理 URL
                    url = re.sub(r'^git\+', '', url)
                    url = re.sub(r'\.git$', '', url)
                    url = re.sub(r'^git://', 'https://', url)
                    return url
        except Exception:
            pass

        # 尝试 PyPI
        pypi_url = f"https://pypi.org/pypi/{package}/json"
        try:
            response = self.session.get(pypi_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                info = data.get('info', {})
                project_urls = info.get('project_urls', {}) or {}

                # 检查各种可能的 URL
                for key in ['Repository', 'Source', 'Homepage', 'GitHub']:
                    url = project_urls.get(key, '')
                    if 'github.com' in url:
                        return url

                # 检查 home_page
                home_page = info.get('home_page', '')
                if 'github.com' in home_page:
                    return home_page
        except Exception:
            pass

        return None

    def _create_candidate(self, package: str, url: str, usage_count: int) -> Optional[dict]:
        """
        创建候选资源 / Create candidate resource

        Args:
            package: 包名 / Package name
            url: GitHub URL
            usage_count: 使用次数 / Usage count

        Returns:
            候选资源或 None / Candidate resource or None
        """
        # 生成资源 ID
        category_id = 'ecosystem'  # 依赖通常归类为生态系统
        prefix = self.categories_prefix.get(category_id, 'eco')
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        resource_id = f"{prefix}-{url_hash}"

        today = datetime.now().strftime('%Y/%m/%d')

        # 获取仓库信息
        github_info = extract_github_info(url)
        author = ''
        author_url = ''

        if github_info:
            owner, repo = github_info
            author = owner
            author_url = f"https://github.com/{owner}"

        return {
            'ID': resource_id,
            'DisplayName': package,
            'DisplayName_ZH': package,
            'Category': category_id,
            'SubCategory': 'general',
            'PrimaryLink': url,
            'SecondaryLink': '',
            'Author': author,
            'AuthorProfile': author_url,
            'IsActive': 'TRUE',
            'DateAdded': today,
            'LastModified': today,
            'LastChecked': today,
            'License': '',
            'Description': f"A dependency commonly used in Claude Code ecosystem (used by {usage_count} resources)",
            'Description_ZH': f"Claude Code 生态系统中常用的依赖包（被 {usage_count} 个资源使用）",
            'Tags_ZH': '',
            'IsPinned': 'FALSE',
            'Section': 'community',
            # 元数据
            '_source': 'dependency-analysis',
            '_discovered_at': datetime.now().isoformat(),
            '_status': 'pending',
            '_usage_count': usage_count,
            '_used_by': self.dependency_sources.get(package, [])[:5],
        }


def add_to_pending(resources: List[dict]) -> int:
    """添加资源到待审核队列 / Add resources to pending queue"""
    pending_file = PROJECT_ROOT / 'candidates' / 'pending_resources.json'

    if pending_file.exists():
        with open(pending_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "_comment": "候选资源队列 - 待审核的资源",
            "_schema_version": "1.0",
            "resources": []
        }

    existing_urls = {r.get('PrimaryLink', '').lower() for r in data['resources']}
    added_count = 0

    for res in resources:
        url = res.get('PrimaryLink', '').lower()
        if url and url not in existing_urls:
            data['resources'].append(res)
            existing_urls.add(url)
            added_count += 1

    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return added_count


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description='Dependency Analysis')
    parser.add_argument('--analyze', action='store_true', help='Analyze dependencies')
    parser.add_argument('--discover', action='store_true', help='Discover related packages')
    parser.add_argument('--dry-run', action='store_true', help='Do not modify files')
    parser.add_argument('--min-count', type=int, default=2, help='Minimum usage count')
    args = parser.parse_args()

    print("📦 依赖分析 / Dependency Analysis")
    print("=" * 50)

    analyzer = DependencyAnalyzer()

    if args.analyze:
        print("\n🔬 分析资源依赖...")
        results = analyzer.analyze_all_resources()

        print("\n📊 分析完成")
        print(f"   分析了 {len(results)} 个仓库")
        print(f"   发现 {len(analyzer.dependency_counts)} 个相关依赖")

        # 显示常用依赖
        popular = analyzer.get_popular_dependencies(args.min_count)
        if popular:
            print(f"\n📈 常用依赖 (出现 >= {args.min_count} 次):")
            for dep, count in popular:
                print(f"   - {dep}: {count} 次")

    if args.discover:
        if not analyzer.dependency_counts:
            print("\n⚠️ 请先运行 --analyze 分析依赖")
            return 1

        print("\n🔍 发现相关包...")
        candidates = analyzer.discover_related_packages()

        if candidates:
            print(f"\n📦 发现 {len(candidates)} 个候选资源:")
            for c in candidates:
                print(f"   - {c['DisplayName']}: {c['PrimaryLink']}")

            if not args.dry_run:
                added = add_to_pending(candidates)
                print(f"\n✅ 已添加 {added} 个资源到候选队列")
            else:
                print("\n[Dry Run] 跳过保存")
        else:
            print("\n📭 未发现新的相关包")

        return 0

    # 默认显示帮助
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
