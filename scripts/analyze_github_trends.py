#!/usr/bin/env python3
"""
GitHub 趋势分析脚本 / GitHub Trends Analysis Script

分析现有资源的 Star/Fork 趋势，发现快速增长的项目。
Analyzes Star/Fork trends of existing resources to discover rapidly growing projects.

用法 / Usage:
    python scripts/analyze_github_trends.py [--report] [--update-metadata]
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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


def load_trends_history() -> dict:
    """加载趋势历史数据 / Load trends history data"""
    history_file = PROJECT_ROOT / "candidates" / "trends_history.json"
    if history_file.exists():
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"_comment": "GitHub 资源趋势历史 / GitHub resource trends history", "repos": {}, "last_updated": None}


def save_trends_history(history: dict):
    """保存趋势历史数据 / Save trends history data"""
    history_file = PROJECT_ROOT / "candidates" / "trends_history.json"
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_existing_resources() -> List[dict]:
    """加载现有资源 / Load existing resources"""
    resources = []
    csv_file = PROJECT_ROOT / "THE_RESOURCES_TABLE.csv"

    if csv_file.exists():
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                resources.append(row)

    return resources


def extract_github_info(url: str) -> Optional[Tuple[str, str]]:
    """从 URL 提取 GitHub owner/repo / Extract GitHub owner/repo from URL"""
    if "github.com" not in url:
        return None

    parts = url.rstrip("/").split("/")
    try:
        github_index = next(i for i, p in enumerate(parts) if "github.com" in p)
        if len(parts) > github_index + 2:
            owner = parts[github_index + 1]
            repo = parts[github_index + 2].replace(".git", "")
            return (owner, repo)
    except (StopIteration, IndexError):
        pass

    return None


def get_repo_stats(owner: str, repo: str, token: Optional[str] = None) -> Optional[dict]:
    """
    获取仓库统计信息 / Get repository statistics

    Returns: {stars, forks, watchers, open_issues, pushed_at, ...}
    """
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "watchers": data.get("watchers_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "pushed_at": data.get("pushed_at"),
                "updated_at": data.get("updated_at"),
                "archived": data.get("archived", False),
                "description": data.get("description"),
                "language": data.get("language"),
                "topics": data.get("topics", []),
            }
        elif response.status_code == 404:
            return {"error": "not_found"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    return None


def get_star_history(owner: str, repo: str, token: Optional[str] = None, days: int = 30) -> List[dict]:
    """
    获取 Star 历史（通过 stargazers API）
    Get star history (via stargazers API)

    注意：这是一个简化实现，GitHub API 不直接提供历史数据
    Note: This is a simplified implementation, GitHub API doesn't provide historical data directly
    """
    # GitHub 不提供 Star 历史 API，这里只能获取最近的 stargazers
    # 完整的 Star 历史需要使用第三方服务如 star-history.com
    return []


def calculate_growth_metrics(current_stats: dict, previous_stats: dict, days_elapsed: int) -> dict:
    """
    计算增长指标 / Calculate growth metrics

    Returns: {
        star_growth: 绝对增长,
        star_growth_rate: 日均增长率,
        star_growth_percent: 百分比增长,
        fork_growth: Fork 增长,
        activity_score: 活跃度评分
    }
    """
    if not previous_stats or days_elapsed <= 0:
        return {
            "star_growth": 0,
            "star_growth_rate": 0,
            "star_growth_percent": 0,
            "fork_growth": 0,
            "activity_score": 0,
        }

    current_stars = current_stats.get("stars", 0)
    previous_stars = previous_stats.get("stars", 0)
    star_growth = current_stars - previous_stars

    star_growth_rate = star_growth / days_elapsed if days_elapsed > 0 else 0

    if previous_stars > 0:
        star_growth_percent = (star_growth / previous_stars) * 100
    else:
        star_growth_percent = 100 if star_growth > 0 else 0

    fork_growth = current_stats.get("forks", 0) - previous_stats.get("forks", 0)

    # 计算活跃度评分
    activity_score = 0

    # 基于 Star 增长
    if star_growth >= 50:
        activity_score += 40
    elif star_growth >= 20:
        activity_score += 30
    elif star_growth >= 10:
        activity_score += 20
    elif star_growth >= 5:
        activity_score += 10

    # 基于最近更新
    pushed_at = current_stats.get("pushed_at")
    if pushed_at:
        pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        now = datetime.now(pushed_date.tzinfo)
        days_since_push = (now - pushed_date).days

        if days_since_push <= 7:
            activity_score += 30
        elif days_since_push <= 30:
            activity_score += 20
        elif days_since_push <= 90:
            activity_score += 10

    # 基于 Fork 增长
    if fork_growth >= 10:
        activity_score += 20
    elif fork_growth >= 5:
        activity_score += 10

    # 基于 issues 活跃度
    open_issues = current_stats.get("open_issues", 0)
    if open_issues > 0:
        activity_score += min(10, open_issues)

    return {
        "star_growth": star_growth,
        "star_growth_rate": round(star_growth_rate, 2),
        "star_growth_percent": round(star_growth_percent, 2),
        "fork_growth": fork_growth,
        "activity_score": min(100, activity_score),
    }


def analyze_resource(
    resource: dict, trends_history: dict, token: Optional[str] = None, config: Optional[dict] = None
) -> Optional[dict]:
    """
    分析单个资源的趋势 / Analyze trends for a single resource

    Returns: 分析结果或 None
    """
    url = resource.get("PrimaryLink", "")
    github_info = extract_github_info(url)

    if not github_info:
        return None

    owner, repo = github_info
    full_name = f"{owner}/{repo}"

    # 获取当前统计
    current_stats = get_repo_stats(owner, repo, token)

    if not current_stats or current_stats.get("error"):
        return {
            "resource_id": resource.get("ID"),
            "full_name": full_name,
            "status": "error",
            "error": current_stats.get("error", "unknown") if current_stats else "api_error",
        }

    # 检查是否已归档
    if current_stats.get("archived"):
        return {
            "resource_id": resource.get("ID"),
            "full_name": full_name,
            "status": "archived",
            "current_stats": current_stats,
        }

    # 获取历史数据
    repo_history = trends_history.get("repos", {}).get(full_name, {})
    previous_snapshot = repo_history.get("last_snapshot")

    # 计算时间间隔
    days_elapsed = 0
    if previous_snapshot:
        last_check = repo_history.get("last_check")
        if last_check:
            last_date = datetime.fromisoformat(last_check)
            days_elapsed = (datetime.now() - last_date).days

    # 计算增长指标
    growth_metrics = calculate_growth_metrics(current_stats, previous_snapshot, days_elapsed)

    return {
        "resource_id": resource.get("ID"),
        "resource_name": resource.get("DisplayName"),
        "full_name": full_name,
        "url": url,
        "status": "active",
        "current_stats": current_stats,
        "previous_stats": previous_snapshot,
        "days_elapsed": days_elapsed,
        "growth_metrics": growth_metrics,
    }


def update_trends_history(trends_history: dict, analysis_results: List[dict]) -> dict:
    """更新趋势历史 / Update trends history"""
    now = datetime.now().isoformat()

    for result in analysis_results:
        if result.get("status") != "active":
            continue

        full_name = result.get("full_name")
        current_stats = result.get("current_stats", {})

        if full_name not in trends_history["repos"]:
            trends_history["repos"][full_name] = {"snapshots": [], "first_seen": now}

        repo_entry = trends_history["repos"][full_name]

        # 添加新快照
        snapshot = {
            "timestamp": now,
            "stars": current_stats.get("stars", 0),
            "forks": current_stats.get("forks", 0),
            "watchers": current_stats.get("watchers", 0),
            "open_issues": current_stats.get("open_issues", 0),
        }

        repo_entry["snapshots"].append(snapshot)

        # 只保留最近 30 个快照
        if len(repo_entry["snapshots"]) > 30:
            repo_entry["snapshots"] = repo_entry["snapshots"][-30:]

        repo_entry["last_snapshot"] = {
            "stars": current_stats.get("stars", 0),
            "forks": current_stats.get("forks", 0),
        }
        repo_entry["last_check"] = now

    trends_history["last_updated"] = now

    return trends_history


def generate_trends_report(analysis_results: List[dict], config: dict) -> str:
    """生成趋势报告 / Generate trends report"""
    trends_config = config.get("trends", {})
    fast_growth_threshold = trends_config.get("fast_growth_threshold_percent", 50)

    report_lines = [
        "# GitHub 资源趋势报告 / GitHub Resource Trends Report",
        f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n分析资源数: {len(analysis_results)}",
        "\n---\n",
    ]

    # 分类统计
    active_count = sum(1 for r in analysis_results if r.get("status") == "active")
    archived_count = sum(1 for r in analysis_results if r.get("status") == "archived")
    error_count = sum(1 for r in analysis_results if r.get("status") == "error")

    report_lines.extend(
        [
            "## 状态统计 / Status Statistics",
            f"- 活跃: {active_count}",
            f"- 已归档: {archived_count}",
            f"- 错误: {error_count}",
            "\n---\n",
        ]
    )

    # 快速增长项目
    active_results = [r for r in analysis_results if r.get("status") == "active"]
    fast_growing = [
        r for r in active_results if r.get("growth_metrics", {}).get("star_growth_percent", 0) >= fast_growth_threshold
    ]
    fast_growing.sort(key=lambda x: x.get("growth_metrics", {}).get("star_growth_percent", 0), reverse=True)

    report_lines.extend([f"## 快速增长项目 / Fast Growing Projects (>{fast_growth_threshold}% 增长)", ""])

    if fast_growing:
        report_lines.append("| 项目 | Stars | 增长 | 增长率 | 活跃度 |")
        report_lines.append("|------|-------|------|--------|--------|")
        for r in fast_growing[:10]:
            metrics = r.get("growth_metrics", {})
            stats = r.get("current_stats", {})
            report_lines.append(
                f"| [{r.get('resource_name', r.get('full_name'))}]({r.get('url')}) | "
                f"{stats.get('stars', 0)} | "
                f"+{metrics.get('star_growth', 0)} | "
                f"{metrics.get('star_growth_percent', 0)}% | "
                f"{metrics.get('activity_score', 0)} |"
            )
    else:
        report_lines.append("*没有快速增长的项目*")

    report_lines.append("\n---\n")

    # Top 活跃项目
    by_activity = sorted(
        active_results, key=lambda x: x.get("growth_metrics", {}).get("activity_score", 0), reverse=True
    )

    report_lines.extend(["## 最活跃项目 / Most Active Projects", ""])

    report_lines.append("| 项目 | Stars | 活跃度 | 最近更新 |")
    report_lines.append("|------|-------|--------|----------|")
    for r in by_activity[:10]:
        metrics = r.get("growth_metrics", {})
        stats = r.get("current_stats", {})
        pushed_at = stats.get("pushed_at", "")
        if pushed_at:
            pushed_at = pushed_at[:10]  # 只显示日期部分
        report_lines.append(
            f"| [{r.get('resource_name', r.get('full_name'))}]({r.get('url')}) | "
            f"{stats.get('stars', 0)} | "
            f"{metrics.get('activity_score', 0)} | "
            f"{pushed_at} |"
        )

    report_lines.append("\n---\n")

    # 已归档项目警告
    if archived_count > 0:
        report_lines.extend(["## ⚠️ 已归档项目 / Archived Projects", ""])
        for r in analysis_results:
            if r.get("status") == "archived":
                report_lines.append(f"- {r.get('resource_name', r.get('full_name'))}: {r.get('url')}")

    return "\n".join(report_lines)


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description="Analyze GitHub trends")
    parser.add_argument("--report", action="store_true", help="Generate trends report")
    parser.add_argument("--update-history", action="store_true", help="Update trends history")
    parser.add_argument("--limit", type=int, default=50, help="Maximum resources to analyze")
    parser.add_argument("--output", type=str, help="Output file for report")
    args = parser.parse_args()

    print("📈 GitHub 趋势分析 / GitHub Trends Analysis")
    print("=" * 50)

    # 获取 GitHub token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("⚠️  未设置 GITHUB_TOKEN，API 速率限制较低")

    # 加载配置和数据
    print("\n📂 加载配置和数据...")
    config = load_config()
    trends_history = load_trends_history()
    existing_resources = load_existing_resources()

    # 过滤出 GitHub 资源
    github_resources = []
    for res in existing_resources:
        url = res.get("PrimaryLink", "")
        if "github.com" in url:
            github_resources.append(res)

    github_resources = github_resources[: args.limit]
    print(f"   将分析 {len(github_resources)} 个 GitHub 资源")

    # 分析资源
    print("\n🔬 分析资源趋势...")
    analysis_results = []

    for i, resource in enumerate(github_resources):
        print(f"   [{i + 1}/{len(github_resources)}] {resource.get('DisplayName', 'Unknown')}...", end=" ")

        result = analyze_resource(resource, trends_history, token, config)

        if result:
            analysis_results.append(result)
            status = result.get("status", "unknown")
            if status == "active":
                metrics = result.get("growth_metrics", {})
                print(
                    f"✅ Stars: {result.get('current_stats', {}).get('stars', 0)}, "
                    f"活跃度: {metrics.get('activity_score', 0)}"
                )
            elif status == "archived":
                print("📦 已归档")
            else:
                print(f"❌ {result.get('error', 'error')}")
        else:
            print("⏭️ 跳过（非 GitHub）")

    # 更新历史
    if args.update_history:
        print("\n💾 更新趋势历史...")
        trends_history = update_trends_history(trends_history, analysis_results)
        save_trends_history(trends_history)
        print("   ✅ 历史已更新")

    # 生成报告
    if args.report:
        print("\n📊 生成趋势报告...")
        report = generate_trends_report(analysis_results, config)

        if args.output:
            output_file = Path(args.output)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"   ✅ 报告已保存到: {output_file}")
        else:
            print("\n" + report)

    # 输出摘要
    active_count = sum(1 for r in analysis_results if r.get("status") == "active")
    archived_count = sum(1 for r in analysis_results if r.get("status") == "archived")

    print("\n✅ 分析完成！")
    print(f"   活跃: {active_count}, 已归档: {archived_count}")

    # 输出供 GitHub Actions 使用
    print(f"::set-output name=analyzed_count::{len(analysis_results)}")
    print(f"::set-output name=active_count::{active_count}")
    print(f"::set-output name=archived_count::{archived_count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
