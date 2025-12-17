#!/usr/bin/env python3
"""
关联项目发现脚本 / Related Repository Discovery Script

从现有资源发现关联项目（依赖、Fork、相似项目等）。
Discovers related repositories from existing resources (dependencies, forks, similar projects, etc.).

用法 / Usage:
    python scripts/discover_related_repos.py [--dry-run] [--limit N] [--type TYPE]
"""

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import requests
import yaml

# 项目根目录 / Project root
PROJECT_ROOT = Path(__file__).parent.parent


def load_config() -> dict:
    """加载发现配置 / Load discovery configuration"""
    config_file = PROJECT_ROOT / "config" / "discovery.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


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

    # 从 rejected 加载
    rejected_file = PROJECT_ROOT / 'candidates' / 'rejected_resources.json'
    if rejected_file.exists():
        with open(rejected_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for res in data.get('resources', []):
                url = res.get('PrimaryLink', '').strip().rstrip('/').lower()
                if url:
                    urls.add(url)

    return urls


def extract_github_info(url: str) -> Optional[Tuple[str, str]]:
    """
    从 URL 提取 GitHub owner/repo 信息
    Extract GitHub owner/repo from URL

    Returns: (owner, repo) or None
    """
    if 'github.com' not in url:
        return None

    # 解析 URL
    parts = url.rstrip('/').split('/')
    try:
        github_index = next(i for i, p in enumerate(parts) if 'github.com' in p)
        if len(parts) > github_index + 2:
            owner = parts[github_index + 1]
            repo = parts[github_index + 2]
            # 移除可能的 .git 后缀
            repo = repo.replace('.git', '')
            return (owner, repo)
    except (StopIteration, IndexError):
        pass

    return None


def get_repo_info(owner: str, repo: str, token: Optional[str] = None) -> Optional[dict]:
    """获取仓库信息 / Get repository info"""
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass

    return None


def get_forks(owner: str, repo: str, token: Optional[str] = None, limit: int = 30) -> List[dict]:
    """
    获取仓库的 Fork 列表 / Get repository forks

    Args:
        owner: 仓库所有者 / Repository owner
        repo: 仓库名 / Repository name
        token: GitHub token
        limit: 最大数量 / Maximum count

    Returns:
        Fork 列表 / List of forks
    """
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    params = {
        'sort': 'stargazers',
        'per_page': min(100, limit)
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()[:limit]
    except requests.exceptions.RequestException:
        pass

    return []


def get_stargazers_also_starred(
    owner: str,
    repo: str,
    token: Optional[str] = None,
    sample_size: int = 20
) -> List[dict]:
    """
    获取 Star 了该项目的用户也 Star 的其他项目（相似项目发现）
    Get other projects starred by users who starred this project (similar project discovery)

    这是一个简化实现，只采样部分用户
    This is a simplified implementation that only samples some users
    """
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    # 获取部分 stargazers
    stargazers_url = f"https://api.github.com/repos/{owner}/{repo}/stargazers"
    params = {'per_page': sample_size}

    try:
        response = requests.get(stargazers_url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            return []

        stargazers = response.json()
    except requests.exceptions.RequestException:
        return []

    # 收集这些用户 Star 的其他项目
    related_repos = {}  # {full_name: repo_info}

    for user in stargazers[:10]:  # 限制只查看前 10 个用户
        username = user.get('login')
        if not username:
            continue

        starred_url = f"https://api.github.com/users/{username}/starred"
        params = {'per_page': 30}

        try:
            response = requests.get(starred_url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                for starred_repo in response.json():
                    full_name = starred_repo.get('full_name', '')
                    # 排除原仓库
                    if full_name.lower() != f"{owner}/{repo}".lower():
                        if full_name not in related_repos:
                            related_repos[full_name] = starred_repo
        except requests.exceptions.RequestException:
            continue

    return list(related_repos.values())


def filter_related_repo(
    repo: dict,
    config: dict,
    existing_urls: Set[str],
    is_fork: bool = False
) -> Tuple[bool, str]:
    """
    过滤关联仓库 / Filter related repository

    Returns: (passed, reason)
    """
    github_config = config['github']
    related_config = config.get('related_discovery', {})

    # 检查 URL 是否已存在
    html_url = repo.get('html_url', '').strip().rstrip('/').lower()
    if html_url in existing_urls:
        return False, "已存在 / Already exists"

    # 检查是否在排除列表中
    full_name = repo.get('full_name', '').lower()
    excluded_repos = [r.lower() for r in github_config.get('excluded_repos', [])]
    if full_name in excluded_repos:
        return False, "在排除列表中 / In exclusion list"

    # 检查 Star 数
    stars = repo.get('stargazers_count', 0)
    if is_fork:
        min_stars = related_config.get('fork_min_stars', 10)
    else:
        min_stars = github_config.get('min_stars', 3)

    if stars < min_stars:
        return False, f"Star 数不足 ({stars} < {min_stars})"

    # 检查是否被归档
    if repo.get('archived', False):
        return False, "已归档 / Archived"

    return True, "通过 / Passed"


def calculate_relevance_score(repo: dict, source_repo: dict, relation_type: str) -> int:
    """
    计算关联仓库的相关性评分
    Calculate relevance score for related repository
    """
    score = 0

    # 基于关系类型加分
    if relation_type == 'fork':
        score += 20  # Fork 基础分较低，需要更多其他指标
    elif relation_type == 'similar':
        score += 30

    # 基于 Star 数加分
    stars = repo.get('stargazers_count', 0)
    if stars >= 100:
        score += 25
    elif stars >= 50:
        score += 20
    elif stars >= 20:
        score += 15
    elif stars >= 10:
        score += 10

    # 检查名称/描述中是否包含相关关键词
    name = repo.get('name', '').lower()
    description = (repo.get('description') or '').lower()
    combined = f"{name} {description}"

    keywords = ['claude', 'anthropic', 'mcp', 'llm', 'ai-assistant']
    for keyword in keywords:
        if keyword in combined:
            score += 15
            break

    # 最近更新加分
    pushed_at = repo.get('pushed_at')
    if pushed_at:
        pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
        now = datetime.now(pushed_date.tzinfo)
        days_since_push = (now - pushed_date).days

        if days_since_push <= 30:
            score += 10
        elif days_since_push <= 90:
            score += 5

    return min(100, score)


def infer_category(repo: dict, source_category: str, config: dict) -> str:
    """推断分类，优先使用源仓库的分类 / Infer category, prefer source repo's category"""
    # 如果是 Fork，继承源分类
    if repo.get('fork', False):
        return source_category

    # 基于名称和描述推断
    name = repo.get('name', '').lower()
    description = (repo.get('description') or '').lower()
    combined = f"{name} {description}"

    if 'mcp' in combined or 'model-context-protocol' in combined:
        return 'mcp-servers'
    if 'hook' in combined:
        return 'hooks'
    if 'workflow' in combined:
        return 'workflows'
    if 'tool' in combined or 'extension' in combined:
        return 'tooling'

    # 默认使用源分类或 ecosystem
    return source_category or 'ecosystem'


def generate_resource_id(category_id: str, url: str, categories_prefix: dict) -> str:
    """生成资源 ID / Generate resource ID"""
    prefix = categories_prefix.get(category_id, 'res')
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{prefix}-{url_hash}"


def create_candidate_from_repo(
    repo: dict,
    source_resource: dict,
    relation_type: str,
    config: dict,
    categories_prefix: dict,
    relevance_score: int
) -> dict:
    """创建候选资源 / Create candidate resource"""
    url = repo.get('html_url', '')
    source_category = source_resource.get('Category', 'ecosystem')
    category_id = infer_category(repo, source_category, config)
    resource_id = generate_resource_id(category_id, url, categories_prefix)

    today = datetime.now().strftime('%Y/%m/%d')
    owner = repo.get('owner', {})

    description = repo.get('description') or ''
    if len(description) > 200:
        description = description[:197] + '...'

    return {
        'ID': resource_id,
        'DisplayName': repo.get('name', ''),
        'DisplayName_ZH': repo.get('name', ''),
        'Category': category_id,
        'SubCategory': 'general',
        'PrimaryLink': url,
        'SecondaryLink': repo.get('homepage', '') or '',
        'Author': owner.get('login', ''),
        'AuthorProfile': owner.get('html_url', ''),
        'IsActive': 'TRUE',
        'DateAdded': today,
        'LastModified': today,
        'LastChecked': today,
        'License': repo.get('license', {}).get('spdx_id', '') if repo.get('license') else '',
        'Description': description,
        'Description_ZH': '',
        'Tags_ZH': '',
        'IsPinned': 'FALSE',
        'Section': 'community',
        # 元数据
        '_source': 'related-discovery',
        '_source_repo': source_resource.get('PrimaryLink', ''),
        '_relation_type': relation_type,
        '_discovered_at': datetime.now().isoformat(),
        '_status': 'pending',
        '_relevance_score': relevance_score,
        '_stars': repo.get('stargazers_count', 0),
        '_language': repo.get('language', ''),
    }


def add_to_pending(resource: dict, pending_file: Path) -> bool:
    """添加到待审核队列 / Add to pending queue"""
    if pending_file.exists():
        with open(pending_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "_comment": "候选资源队列 - 待审核的资源",
            "_schema_version": "1.0",
            "resources": []
        }

    data['resources'].append(resource)

    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return True


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description='Discover related repositories')
    parser.add_argument('--dry-run', action='store_true', help='Do not modify files')
    parser.add_argument('--limit', type=int, default=10, help='Maximum resources to add')
    parser.add_argument('--type', choices=['forks', 'similar', 'all'], default='all',
                        help='Type of relation to discover')
    args = parser.parse_args()

    print("🔗 关联项目发现 / Related Repository Discovery")
    print("=" * 50)

    # 获取 GitHub token
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("⚠️  未设置 GITHUB_TOKEN，API 速率限制较低")

    # 加载配置和数据
    print("\n📂 加载配置和数据...")
    config = load_config()
    categories_prefix = load_categories()
    existing_resources = load_existing_resources()
    existing_urls = load_existing_urls()

    # 过滤出 GitHub 资源
    github_resources = []
    for res in existing_resources:
        url = res.get('PrimaryLink', '')
        github_info = extract_github_info(url)
        if github_info:
            github_resources.append((res, github_info))

    print(f"   现有 GitHub 资源: {len(github_resources)} 个")

    if not github_resources:
        print("\n📭 没有可分析的 GitHub 资源")
        return 0

    # 发现关联项目
    candidates = []
    pending_file = PROJECT_ROOT / 'candidates' / 'pending_resources.json'

    # 发现 Fork 项目
    if args.type in ['forks', 'all']:
        print("\n🍴 发现 Fork 项目...")
        for resource, (owner, repo) in github_resources[:20]:  # 限制分析数量
            print(f"   分析 {owner}/{repo}...")

            forks = get_forks(owner, repo, token, limit=10)
            for fork in forks:
                passed, reason = filter_related_repo(fork, config, existing_urls, is_fork=True)
                if not passed:
                    continue

                score = calculate_relevance_score(fork, resource, 'fork')
                if score >= 30:  # 相关性阈值
                    candidates.append((fork, resource, 'fork', score))

    # 发现相似项目
    if args.type in ['similar', 'all']:
        print("\n🔄 发现相似项目...")
        for resource, (owner, repo) in github_resources[:10]:  # 相似项目发现更耗时，限制更多
            print(f"   分析 {owner}/{repo} 的相似项目...")

            similar = get_stargazers_also_starred(owner, repo, token, sample_size=10)
            for sim_repo in similar:
                passed, reason = filter_related_repo(sim_repo, config, existing_urls)
                if not passed:
                    continue

                score = calculate_relevance_score(sim_repo, resource, 'similar')
                if score >= 40:  # 相似项目需要更高的相关性
                    candidates.append((sim_repo, resource, 'similar', score))

    # 去重和排序
    seen_urls = set()
    unique_candidates = []
    for repo, source, rel_type, score in candidates:
        url = repo.get('html_url', '').lower()
        if url not in seen_urls:
            seen_urls.add(url)
            unique_candidates.append((repo, source, rel_type, score))

    unique_candidates.sort(key=lambda x: x[3], reverse=True)
    unique_candidates = unique_candidates[:args.limit]

    print(f"\n📊 发现 {len(unique_candidates)} 个候选关联项目")

    if not unique_candidates:
        print("\n📭 没有发现新的关联项目")
        return 0

    # 创建候选资源
    print(f"\n📦 创建候选资源...")
    added_count = 0

    for repo, source_resource, relation_type, score in unique_candidates:
        resource = create_candidate_from_repo(
            repo, source_resource, relation_type,
            config, categories_prefix, score
        )

        print(f"\n   📌 {resource['DisplayName']}")
        print(f"      URL: {resource['PrimaryLink']}")
        print(f"      关系: {relation_type} (来自 {source_resource.get('DisplayName', 'unknown')})")
        print(f"      Stars: {resource['_stars']} ⭐")
        print(f"      相关性: {score}/100")

        if args.dry_run:
            print("      [Dry Run] 跳过添加")
        else:
            add_to_pending(resource, pending_file)
            added_count += 1
            print("      ✅ 已添加到候选队列")

    print(f"\n✅ 完成！添加了 {added_count} 个关联项目")

    # 输出供 GitHub Actions 使用
    print(f"::set-output name=discovered_count::{len(unique_candidates)}")
    print(f"::set-output name=added_count::{added_count}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
