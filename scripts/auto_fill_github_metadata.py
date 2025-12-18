#!/usr/bin/env python3
"""
自动从 GitHub 提取 Author 和 License 信息
Auto-extract Author and License from GitHub repositories
"""

import csv
import os
import re
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

try:
    from github import Github, GithubException

    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("⚠️ PyGithub 未安装。运行: pip install PyGithub")
    print("⚠️ PyGithub not installed. Run: pip install PyGithub")


def parse_github_url(url: str) -> Optional[Tuple[str, str]]:
    """
    从 GitHub URL 提取 owner 和 repo
    Extract owner and repo from GitHub URL

    Returns: (owner, repo) or None
    """
    if not url or "github.com" not in url:
        return None

    # 匹配 github.com/owner/repo 格式
    # Match github.com/owner/repo format
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)

    if match:
        owner = match.group(1)
        repo = match.group(2).rstrip(".git")  # 移除 .git 后缀
        return (owner, repo)

    return None


def fetch_github_metadata(owner: str, repo: str, github_token: Optional[str] = None) -> Dict:
    """
    从 GitHub API 获取仓库元数据
    Fetch repository metadata from GitHub API
    """
    if not GITHUB_AVAILABLE:
        return {"error": "PyGithub not available"}

    try:
        # 使用 token（如果提供）以避免速率限制
        # Use token (if provided) to avoid rate limits
        if github_token:
            g = Github(github_token)
        else:
            g = Github()  # 匿名访问，速率限制 60 req/hour

        # 获取仓库信息
        # Get repository info
        repository = g.get_repo(f"{owner}/{repo}")

        # 提取元数据
        # Extract metadata
        metadata = {
            "author": owner,
            "author_profile": f"https://github.com/{owner}",
            "license": repository.license.spdx_id if repository.license else "",
            "description": repository.description or "",
            "stars": repository.stargazers_count,
            "language": repository.language or "",
            "updated_at": repository.updated_at.strftime("%Y-%m-%d") if repository.updated_at else "",
        }

        return metadata

    except GithubException as e:
        return {"error": f"GitHub API Error: {e.status} - {e.data.get('message', 'Unknown error')}"}
    except Exception as e:
        return {"error": str(e)}


def update_csv_with_github_data(csv_path: Path, github_token: Optional[str] = None, dry_run: bool = False):
    """
    更新 CSV 文件中的 GitHub 元数据
    Update CSV file with GitHub metadata
    """
    # 读取 CSV
    # Read CSV
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        resources = list(reader)
        fieldnames = reader.fieldnames

    updated_count = 0
    skipped_count = 0
    error_count = 0

    print(f"\n🔍 处理 {len(resources)} 条资源...")
    print(f"🔍 Processing {len(resources)} resources...\n")

    for idx, resource in enumerate(resources, start=1):
        url = resource.get("PrimaryLink", "")
        current_author = resource.get("Author", "").strip()
        current_license = resource.get("License", "").strip()

        # 如果已有 Author 和 License，跳过
        # Skip if Author and License already exist
        if current_author and current_license:
            skipped_count += 1
            continue

        # 解析 GitHub URL
        # Parse GitHub URL
        github_info = parse_github_url(url)

        if not github_info:
            # 非 GitHub 链接，跳过
            # Not a GitHub link, skip
            continue

        owner, repo = github_info
        print(f"[{idx}/{len(resources)}] {owner}/{repo}...")

        # 获取元数据
        # Fetch metadata
        metadata = fetch_github_metadata(owner, repo, github_token)

        if "error" in metadata:
            print(f"  ❌ {metadata['error']}")
            error_count += 1
            continue

        # 更新字段
        # Update fields
        if not current_author:
            resource["Author"] = metadata["author"]
            resource["AuthorProfile"] = metadata["author_profile"]

        if not current_license and metadata["license"]:
            resource["License"] = metadata["license"]

        # 如果描述为空，可以考虑使用 GitHub 的描述（可选）
        # Optionally use GitHub description if empty (optional)
        if not resource.get("Description", "").strip() and metadata["description"]:
            resource["Description_ZH"] = metadata["description"]

        print(f"  ✅ Author: {metadata['author']}, License: {metadata['license'] or 'N/A'}")
        updated_count += 1

        # 速率限制：避免 API 限制
        # Rate limiting: avoid API limits
        if (idx % 5 == 0) and not github_token:
            print("  ⏱️  等待 1 秒（避免速率限制）...")
            time.sleep(1)

    print("\n📊 统计 / Statistics:")
    print(f"  ✅ 更新 / Updated: {updated_count}")
    print(f"  ⏭️  跳过 / Skipped: {skipped_count}")
    print(f"  ❌ 错误 / Errors: {error_count}")

    if dry_run:
        print("\n⚠️ DRY RUN 模式：不写入文件")
        print("⚠️ DRY RUN mode: Not writing to file")
        return

    # 写回 CSV
    # Write back to CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resources)

    print(f"\n✅ CSV 文件已更新: {csv_path}")
    print(f"✅ CSV file updated: {csv_path}")


def main():
    """主函数 / Main function"""
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "THE_RESOURCES_TABLE.csv"

    # 从环境变量获取 GitHub token（可选）
    # Get GitHub token from environment (optional)
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("💡 提示: 设置 GITHUB_TOKEN 环境变量可提高 API 速率限制")
        print("💡 Tip: Set GITHUB_TOKEN environment variable to increase API rate limit")
        print("   无 token: 60 请求/小时 | With token: 5000 请求/小时")
        print()

    if not GITHUB_AVAILABLE:
        print("❌ 需要安装 PyGithub:")
        print("   pip install PyGithub")
        return 1

    # 运行更新
    # Run update
    update_csv_with_github_data(csv_path, github_token, dry_run=False)

    print("\n✨ 完成！/ Done!")
    print("\n下一步 / Next steps:")
    print("1. 查看 CSV 文件检查更新")
    print("   Check CSV file to review updates")
    print("2. 手动补充非 GitHub 资源的 Author 和 License")
    print("   Manually add Author and License for non-GitHub resources")
    print("3. 运行验证脚本: python3 scripts/validate_csv.py")
    print("   Run validation script: python3 scripts/validate_csv.py")


if __name__ == "__main__":
    main()
