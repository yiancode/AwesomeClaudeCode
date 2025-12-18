#!/usr/bin/env python3
"""
GitHub Topics 资源发现脚本 / GitHub Topics Resource Discovery Script

通过 GitHub Topics 和关键词搜索发现与 Claude Code 相关的新项目。
Discovers new Claude Code related projects via GitHub Topics and keyword search.

用法 / Usage:
    python scripts/discover_github_topics.py [--dry-run] [--limit N]
"""

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests
import yaml

# 项目根目录 / Project root
PROJECT_ROOT = Path(__file__).parent.parent


def load_config() -> dict:
    """加载发现配置 / Load discovery configuration"""
    config_file = PROJECT_ROOT / "config" / "discovery.yaml"
    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_categories() -> dict:
    """加载分类定义 / Load category definitions"""
    categories_file = PROJECT_ROOT / "templates" / "categories.yaml"
    with open(categories_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {cat["id"]: cat["prefix"] for cat in data["categories"]}


def load_existing_urls() -> Set[str]:
    """
    加载所有已存在的资源 URL（CSV + pending + rejected）
    Load all existing resource URLs (CSV + pending + rejected)
    """
    urls = set()

    # 从 CSV 加载
    csv_file = PROJECT_ROOT / "THE_RESOURCES_TABLE.csv"
    if csv_file.exists():
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("PrimaryLink", "").strip().rstrip("/").lower()
                if url:
                    urls.add(url)

    # 从 pending 加载
    pending_file = PROJECT_ROOT / "candidates" / "pending_resources.json"
    if pending_file.exists():
        with open(pending_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for res in data.get("resources", []):
                url = res.get("PrimaryLink", "").strip().rstrip("/").lower()
                if url:
                    urls.add(url)

    # 从 rejected 加载
    rejected_file = PROJECT_ROOT / "candidates" / "rejected_resources.json"
    if rejected_file.exists():
        with open(rejected_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for res in data.get("resources", []):
                url = res.get("PrimaryLink", "").strip().rstrip("/").lower()
                if url:
                    urls.add(url)

    return urls


def load_discovery_log() -> dict:
    """加载发现日志 / Load discovery log"""
    log_file = PROJECT_ROOT / "candidates" / "discovery_log.json"
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "_comment": "资源发现日志 / Resource discovery log",
        "last_run": None,
        "discovered_repos": [],
        "stats": {"total_discovered": 0, "total_added": 0, "total_skipped": 0},
    }


def save_discovery_log(log: dict):
    """保存发现日志 / Save discovery log"""
    log_file = PROJECT_ROOT / "candidates" / "discovery_log.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def github_search(query: str, token: Optional[str] = None, max_results: int = 50) -> List[dict]:
    """
    执行 GitHub 搜索 / Execute GitHub search

    Args:
        query: 搜索查询 / Search query
        token: GitHub token（可选）/ GitHub token (optional)
        max_results: 最大结果数 / Maximum results

    Returns:
        仓库列表 / List of repositories
    """
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos = []
    page = 1
    per_page = min(100, max_results)

    while len(repos) < max_results:
        url = "https://api.github.com/search/repositories"
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": per_page, "page": page}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if not items:
                break

            repos.extend(items)
            page += 1

            # 检查是否还有更多结果
            if len(items) < per_page:
                break

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ GitHub API 请求失败: {e}")
            break

    return repos[:max_results]


def search_by_topic(topic: str, config: dict, token: Optional[str] = None) -> List[dict]:
    """
    按 Topic 搜索仓库 / Search repositories by topic

    Args:
        topic: GitHub topic
        config: 配置 / Configuration
        token: GitHub token

    Returns:
        仓库列表 / List of repositories
    """
    github_config = config["github"]
    min_stars = github_config.get("min_stars", 3)
    max_results = github_config.get("max_results_per_query", 50)

    query = f"topic:{topic} stars:>={min_stars}"
    return github_search(query, token, max_results)


def search_by_keyword(keyword: str, config: dict, token: Optional[str] = None) -> List[dict]:
    """
    按关键词搜索仓库 / Search repositories by keyword

    Args:
        keyword: 搜索关键词 / Search keyword
        config: 配置 / Configuration
        token: GitHub token

    Returns:
        仓库列表 / List of repositories
    """
    github_config = config["github"]
    min_stars = github_config.get("min_stars", 3)
    max_results = github_config.get("max_results_per_query", 50)

    query = f"{keyword} in:name,description,readme stars:>={min_stars}"
    return github_search(query, token, max_results)


def filter_repo(repo: dict, config: dict, existing_urls: Set[str]) -> Tuple[bool, str]:
    """
    过滤仓库 / Filter repository

    Args:
        repo: 仓库信息 / Repository info
        config: 配置 / Configuration
        existing_urls: 已存在的 URL / Existing URLs

    Returns:
        (是否通过, 原因) / (passed, reason)
    """
    github_config = config["github"]

    # 检查是否在排除列表中
    full_name = repo.get("full_name", "").lower()
    excluded_repos = [r.lower() for r in github_config.get("excluded_repos", [])]
    if full_name in excluded_repos:
        return False, "在排除列表中 / In exclusion list"

    # 检查所有者是否在排除列表中
    owner = repo.get("owner", {}).get("login", "").lower()
    excluded_owners = [o.lower() for o in github_config.get("excluded_owners", [])]
    if owner in excluded_owners:
        return False, "所有者在排除列表中 / Owner in exclusion list"

    # 检查是否已存在
    html_url = repo.get("html_url", "").strip().rstrip("/").lower()
    if html_url in existing_urls:
        return False, "已存在 / Already exists"

    # 检查 Star 数
    stars = repo.get("stargazers_count", 0)
    min_stars = github_config.get("min_stars", 3)
    if stars < min_stars:
        return False, f"Star 数不足 ({stars} < {min_stars})"

    # 检查项目年龄
    created_at = repo.get("created_at")
    if created_at:
        created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        now = datetime.now(created_date.tzinfo)
        age_days = (now - created_date).days

        min_age = github_config.get("min_age_days", 7)
        if age_days < min_age:
            return False, f"项目太新 ({age_days} < {min_age} 天)"

        max_age = github_config.get("max_age_days", 365)
        if age_days > max_age:
            return False, f"项目太旧 ({age_days} > {max_age} 天)"

    # 检查是否被归档
    if repo.get("archived", False):
        return False, "已归档 / Archived"

    return True, "通过 / Passed"


def calculate_relevance_score(repo: dict, config: dict) -> int:
    """
    计算相关性评分 / Calculate relevance score

    Args:
        repo: 仓库信息 / Repository info
        config: 配置 / Configuration

    Returns:
        相关性评分 (0-100) / Relevance score (0-100)
    """
    score = 0
    indicators = config["github"].get("relevance_indicators", {})

    # 检查高相关性指标
    high_indicators = indicators.get("high", [])
    description = (repo.get("description") or "").lower()
    name = repo.get("name", "").lower()
    topics = [t.lower() for t in repo.get("topics", [])]

    for indicator in high_indicators:
        indicator_lower = indicator.lower()
        if indicator_lower in name or indicator_lower in description:
            score += 30
        if indicator_lower in topics:
            score += 20

    # 检查中等相关性指标
    medium_indicators = indicators.get("medium", [])
    for indicator in medium_indicators:
        indicator_lower = indicator.lower()
        if indicator_lower in name:
            score += 15
        if indicator_lower in description:
            score += 10
        if indicator_lower in topics:
            score += 10

    # 基于 Star 数加分
    stars = repo.get("stargazers_count", 0)
    if stars >= 100:
        score += 15
    elif stars >= 50:
        score += 10
    elif stars >= 20:
        score += 5

    # 基于最近更新加分
    pushed_at = repo.get("pushed_at")
    if pushed_at:
        pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        now = datetime.now(pushed_date.tzinfo)
        days_since_push = (now - pushed_date).days

        if days_since_push <= 7:
            score += 10
        elif days_since_push <= 30:
            score += 5

    return min(100, score)


def infer_category(repo: dict, config: dict) -> str:
    """
    推断资源分类 / Infer resource category

    Args:
        repo: 仓库信息 / Repository info
        config: 配置 / Configuration

    Returns:
        分类 ID / Category ID
    """
    inference = config.get("category_inference", {})
    topic_mapping = inference.get("topic_mapping", {})
    default_category = inference.get("default_category", "ecosystem")

    # 基于 Topics 推断
    topics = repo.get("topics", [])
    for topic in topics:
        if topic in topic_mapping:
            return topic_mapping[topic]

    # 基于名称和描述推断
    name = repo.get("name", "").lower()
    description = (repo.get("description") or "").lower()
    combined = f"{name} {description}"

    if "mcp" in combined or "model-context-protocol" in combined:
        return "mcp-servers"
    if "hook" in combined:
        return "hooks"
    if "slash" in combined or "command" in combined:
        return "slash-commands"
    if "workflow" in combined:
        return "workflows"
    if "tool" in combined or "extension" in combined or "plugin" in combined:
        return "tooling"
    if "skill" in combined:
        return "skills"

    return default_category


def generate_resource_id(category_id: str, url: str, categories_prefix: dict) -> str:
    """生成资源 ID / Generate resource ID"""
    prefix = categories_prefix.get(category_id, "res")
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{prefix}-{url_hash}"


def create_candidate_from_repo(repo: dict, config: dict, categories_prefix: dict, relevance_score: int) -> dict:
    """
    从仓库信息创建候选资源 / Create candidate resource from repository info

    Args:
        repo: 仓库信息 / Repository info
        config: 配置 / Configuration
        categories_prefix: 分类前缀映射 / Category prefix mapping
        relevance_score: 相关性评分 / Relevance score

    Returns:
        候选资源字典 / Candidate resource dict
    """
    url = repo.get("html_url", "")
    category_id = infer_category(repo, config)
    resource_id = generate_resource_id(category_id, url, categories_prefix)

    today = datetime.now().strftime("%Y/%m/%d")
    owner = repo.get("owner", {})

    description = repo.get("description") or ""
    # 截断过长的描述
    if len(description) > 200:
        description = description[:197] + "..."

    return {
        "ID": resource_id,
        "DisplayName": repo.get("name", ""),
        "DisplayName_ZH": repo.get("name", ""),  # 需要人工翻译
        "Category": category_id,
        "SubCategory": "general",
        "PrimaryLink": url,
        "SecondaryLink": repo.get("homepage", "") or "",
        "Author": owner.get("login", ""),
        "AuthorProfile": owner.get("html_url", ""),
        "IsActive": "TRUE",
        "DateAdded": today,
        "LastModified": today,
        "LastChecked": today,
        "License": repo.get("license", {}).get("spdx_id", "") if repo.get("license") else "",
        "Description": description,
        "Description_ZH": "",  # 需要人工翻译
        "Tags_ZH": "",
        "IsPinned": "FALSE",
        "Section": "community",
        # 元数据
        "_source": "github-discovery",
        "_discovered_at": datetime.now().isoformat(),
        "_status": "pending",
        "_relevance_score": relevance_score,
        "_stars": repo.get("stargazers_count", 0),
        "_language": repo.get("language", ""),
        "_topics": repo.get("topics", []),
    }


def add_to_pending(resource: dict, pending_file: Path) -> bool:
    """添加资源到待审核队列 / Add resource to pending queue"""
    if pending_file.exists():
        with open(pending_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "_comment": "候选资源队列 - 待审核的资源 / Candidate resource queue - resources pending review",
            "_schema_version": "1.0",
            "resources": [],
        }

    data["resources"].append(resource)

    with open(pending_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return True


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description="Discover GitHub resources")
    parser.add_argument("--dry-run", action="store_true", help="Do not modify files")
    parser.add_argument("--limit", type=int, default=10, help="Maximum resources to add")
    parser.add_argument("--topics-only", action="store_true", help="Only search by topics")
    parser.add_argument("--keywords-only", action="store_true", help="Only search by keywords")
    args = parser.parse_args()

    print("🔍 GitHub 资源发现 / GitHub Resource Discovery")
    print("=" * 50)

    # 获取 GitHub token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("⚠️  未设置 GITHUB_TOKEN，API 速率限制较低")
        print("⚠️  GITHUB_TOKEN not set, API rate limit is lower")

    # 加载配置
    print("\n📂 加载配置...")
    config = load_config()
    categories_prefix = load_categories()
    existing_urls = load_existing_urls()
    discovery_log = load_discovery_log()

    print(f"   已有资源数: {len(existing_urls)}")

    github_config = config["github"]
    all_repos = {}  # 使用字典去重，key 为 full_name

    # 按 Topics 搜索
    if not args.keywords_only:
        topics = github_config.get("topics", [])
        print(f"\n🏷️  搜索 Topics ({len(topics)} 个)...")

        for topic in topics:
            print(f"   搜索 topic:{topic}...")
            repos = search_by_topic(topic, config, token)
            for repo in repos:
                full_name = repo.get("full_name", "")
                if full_name and full_name not in all_repos:
                    all_repos[full_name] = repo
            print(f"      找到 {len(repos)} 个仓库，累计 {len(all_repos)} 个")

    # 按关键词搜索
    if not args.topics_only:
        queries = github_config.get("search_queries", [])
        print(f"\n🔎 搜索关键词 ({len(queries)} 个)...")

        for query in queries:
            print(f'   搜索 "{query}"...')
            repos = search_by_keyword(query, config, token)
            for repo in repos:
                full_name = repo.get("full_name", "")
                if full_name and full_name not in all_repos:
                    all_repos[full_name] = repo
            print(f"      找到 {len(repos)} 个仓库，累计 {len(all_repos)} 个")

    print(f"\n📊 共发现 {len(all_repos)} 个唯一仓库")

    # 过滤和评分
    print("\n🔬 过滤和评分...")
    candidates = []

    for full_name, repo in all_repos.items():
        passed, reason = filter_repo(repo, config, existing_urls)
        if not passed:
            continue

        score = calculate_relevance_score(repo, config)
        if score < 20:  # 相关性评分过低
            continue

        candidates.append((repo, score))

    # 按相关性评分排序
    candidates.sort(key=lambda x: x[1], reverse=True)
    candidates = candidates[: args.limit]

    print(f"   符合条件的候选: {len(candidates)} 个")

    if not candidates:
        print("\n📭 没有发现新的候选资源")
        return 0

    # 创建候选资源
    print(f"\n📦 创建候选资源 (限制 {args.limit} 个)...")
    pending_file = PROJECT_ROOT / "candidates" / "pending_resources.json"
    added_count = 0

    for repo, score in candidates:
        resource = create_candidate_from_repo(repo, config, categories_prefix, score)

        print(f"\n   📌 {resource['DisplayName']}")
        print(f"      URL: {resource['PrimaryLink']}")
        print(f"      分类: {resource['Category']}")
        print(f"      Stars: {resource['_stars']} ⭐")
        print(f"      相关性: {score}/100")

        if args.dry_run:
            print("      [Dry Run] 跳过添加")
        else:
            add_to_pending(resource, pending_file)
            added_count += 1
            print("      ✅ 已添加到候选队列")

            # 更新发现日志
            discovery_log["discovered_repos"].append(
                {
                    "full_name": repo.get("full_name"),
                    "url": resource["PrimaryLink"],
                    "discovered_at": datetime.now().isoformat(),
                    "relevance_score": score,
                }
            )

    # 保存发现日志
    if not args.dry_run:
        discovery_log["last_run"] = datetime.now().isoformat()
        discovery_log["stats"]["total_discovered"] += len(candidates)
        discovery_log["stats"]["total_added"] += added_count
        save_discovery_log(discovery_log)

    print(f"\n✅ 完成！添加了 {added_count} 个新候选资源")

    # 输出供 GitHub Actions 使用
    print(f"::set-output name=discovered_count::{len(candidates)}")
    print(f"::set-output name=added_count::{added_count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
