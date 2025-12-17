#!/usr/bin/env python3
"""
从候选队列创建资源 PR / Create Resource PR from Candidate Queue

从 pending_resources.json 读取待审核资源，
将其添加到 CSV 并创建 Pull Request。

Usage:
    python scripts/create_resource_pr.py [--all | --resource-id <id>]
    python scripts/create_resource_pr.py --approve <resource_id>
    python scripts/create_resource_pr.py --reject <resource_id> --reason "原因"
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# 项目根目录 / Project root
PROJECT_ROOT = Path(__file__).parent.parent

# CSV 字段顺序（必须与现有 CSV 匹配）
CSV_FIELDS = [
    'ID', 'DisplayName', 'DisplayName_ZH', 'Category', 'SubCategory',
    'PrimaryLink', 'SecondaryLink', 'Author', 'AuthorProfile',
    'IsActive', 'DateAdded', 'LastModified', 'LastChecked',
    'License', 'Description', 'Description_ZH', 'Tags_ZH',
    'IsPinned', 'Section'
]


def load_pending_resources(pending_file: Path) -> List[dict]:
    """加载待审核资源 / Load pending resources"""
    if not pending_file.exists():
        return []

    with open(pending_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('resources', [])


def save_pending_resources(resources: List[dict], pending_file: Path):
    """保存待审核资源 / Save pending resources"""
    data = {
        "_comment": "候选资源队列 - 待审核的资源 / Candidate resource queue - resources pending review",
        "_schema_version": "1.0",
        "resources": resources
    }
    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_rejected_resources(rejected_file: Path) -> List[dict]:
    """加载已拒绝资源 / Load rejected resources"""
    if not rejected_file.exists():
        return []

    with open(rejected_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('resources', [])


def save_rejected_resources(resources: List[dict], rejected_file: Path):
    """保存已拒绝资源 / Save rejected resources"""
    data = {
        "_comment": "已拒绝的资源 - 用于去重检测 / Rejected resources - used for deduplication",
        "_schema_version": "1.0",
        "resources": resources
    }
    with open(rejected_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clean_resource_for_csv(resource: dict) -> dict:
    """
    清理资源数据，移除元数据字段
    Clean resource data, remove metadata fields
    """
    csv_resource = {}
    for field in CSV_FIELDS:
        csv_resource[field] = resource.get(field, '')
    return csv_resource


def append_resource_to_csv(resource: dict, csv_file: Path):
    """
    将资源追加到 CSV 文件
    Append resource to CSV file
    """
    csv_resource = clean_resource_for_csv(resource)

    # 读取现有数据以检查是否需要添加表头
    file_exists = csv_file.exists() and csv_file.stat().st_size > 0

    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(csv_resource)


def run_git_command(cmd: List[str], cwd: Optional[Path] = None) -> tuple:
    """
    执行 Git 命令
    Execute Git command
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def create_branch_and_pr(resources: List[dict], csv_file: Path) -> tuple:
    """
    创建分支、添加资源到 CSV、创建 PR
    Create branch, add resources to CSV, create PR

    Returns: (success, message)
    """
    if not resources:
        return False, "没有待处理的资源 / No resources to process"

    # 生成分支名
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    resource_count = len(resources)
    branch_name = f"auto/add-resources-{timestamp}"

    print(f"📌 创建分支: {branch_name}")

    # 确保在最新的 main 分支上
    success, output = run_git_command(['git', 'fetch', 'origin', 'main'])
    if not success:
        print(f"   ⚠️ fetch 警告: {output}")

    success, output = run_git_command(['git', 'checkout', 'main'])
    if not success:
        return False, f"切换到 main 分支失败: {output}"

    success, output = run_git_command(['git', 'pull', 'origin', 'main'])
    if not success:
        print(f"   ⚠️ pull 警告: {output}")

    # 创建新分支
    success, output = run_git_command(['git', 'checkout', '-b', branch_name])
    if not success:
        return False, f"创建分支失败: {output}"

    # 添加资源到 CSV
    print(f"\n📝 添加 {resource_count} 个资源到 CSV...")
    for resource in resources:
        append_resource_to_csv(resource, csv_file)
        print(f"   ✅ {resource['DisplayName']}")

    # 提交更改
    success, output = run_git_command(['git', 'add', str(csv_file)])
    if not success:
        return False, f"git add 失败: {output}"

    # 构建提交消息
    resource_names = ', '.join([r['DisplayName'] for r in resources[:3]])
    if resource_count > 3:
        resource_names += f" 等 {resource_count} 个资源"

    commit_msg = f"feat: 添加新资源 - {resource_names}\n\n"
    commit_msg += "自动从 Issue 提交中添加的资源:\n"
    for r in resources:
        issue_num = r.get('_source_issue', 'N/A')
        commit_msg += f"- {r['DisplayName']} (#{issue_num})\n"

    success, output = run_git_command(['git', 'commit', '-m', commit_msg])
    if not success:
        return False, f"git commit 失败: {output}"

    # 推送分支
    print(f"\n🚀 推送分支到远程...")
    success, output = run_git_command(['git', 'push', '-u', 'origin', branch_name])
    if not success:
        return False, f"git push 失败: {output}"

    # 创建 PR（使用 gh CLI）
    print(f"\n📬 创建 Pull Request...")

    pr_title = f"✨ 添加 {resource_count} 个新资源"
    pr_body = f"""## 📦 新资源提交

本 PR 自动生成，包含以下待审核资源：

| 名称 | 分类 | 来源 Issue |
|------|------|-----------|
"""
    for r in resources:
        issue_num = r.get('_source_issue', 'N/A')
        issue_link = f"#{issue_num}" if issue_num != 'N/A' else 'N/A'
        pr_body += f"| {r['DisplayName']} | {r['Category']} | {issue_link} |\n"

    pr_body += """
## ✅ 审核清单

- [ ] 资源链接有效
- [ ] 分类正确
- [ ] 描述准确
- [ ] 无重复资源

---
🤖 此 PR 由 Issue 自动化流程生成
"""

    # 使用 gh CLI 创建 PR
    success, output = run_git_command([
        'gh', 'pr', 'create',
        '--title', pr_title,
        '--body', pr_body,
        '--base', 'main',
        '--head', branch_name,
        '--label', 'resource-submission,automated'
    ])

    if not success:
        # 可能是没有 gh CLI，输出手动创建说明
        print(f"   ⚠️ 无法自动创建 PR: {output}")
        print(f"   请手动创建 PR: {branch_name} -> main")
        return True, f"分支已推送: {branch_name}，请手动创建 PR"

    print(f"   ✅ PR 创建成功: {output}")
    return True, output


def approve_resource(resource_id: str, pending_file: Path, csv_file: Path) -> tuple:
    """
    批准单个资源（添加到 CSV）
    Approve single resource (add to CSV)
    """
    resources = load_pending_resources(pending_file)

    # 查找资源
    target = None
    remaining = []
    for r in resources:
        if r['ID'] == resource_id:
            target = r
        else:
            remaining.append(r)

    if not target:
        return False, f"未找到资源: {resource_id}"

    # 添加到 CSV
    append_resource_to_csv(target, csv_file)

    # 从待审核列表移除
    save_pending_resources(remaining, pending_file)

    return True, f"已批准资源: {target['DisplayName']}"


def reject_resource(resource_id: str, reason: str, pending_file: Path, rejected_file: Path) -> tuple:
    """
    拒绝资源（移到已拒绝列表）
    Reject resource (move to rejected list)
    """
    resources = load_pending_resources(pending_file)
    rejected = load_rejected_resources(rejected_file)

    # 查找资源
    target = None
    remaining = []
    for r in resources:
        if r['ID'] == resource_id:
            target = r
        else:
            remaining.append(r)

    if not target:
        return False, f"未找到资源: {resource_id}"

    # 添加拒绝原因和时间
    target['_rejected_at'] = datetime.now().isoformat()
    target['_reject_reason'] = reason
    target['_status'] = 'rejected'

    # 添加到已拒绝列表
    rejected.append(target)

    # 保存
    save_pending_resources(remaining, pending_file)
    save_rejected_resources(rejected, rejected_file)

    return True, f"已拒绝资源: {target['DisplayName']}"


def list_pending(pending_file: Path):
    """列出待审核资源 / List pending resources"""
    resources = load_pending_resources(pending_file)

    if not resources:
        print("📭 没有待审核的资源")
        return

    print(f"📋 待审核资源 ({len(resources)} 个):\n")
    print(f"{'ID':<20} {'名称':<30} {'分类':<20} {'Issue':<10}")
    print("-" * 80)

    for r in resources:
        issue_num = r.get('_source_issue', 'N/A')
        print(f"{r['ID']:<20} {r['DisplayName']:<30} {r['Category']:<20} #{issue_num:<10}")


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description='Create PR from pending resources')
    parser.add_argument('--all', action='store_true', help='Process all pending resources')
    parser.add_argument('--resource-id', type=str, help='Process specific resource')
    parser.add_argument('--approve', type=str, help='Approve resource by ID')
    parser.add_argument('--reject', type=str, help='Reject resource by ID')
    parser.add_argument('--reason', type=str, default='', help='Rejection reason')
    parser.add_argument('--list', action='store_true', help='List pending resources')
    parser.add_argument('--dry-run', action='store_true', help='Do not create PR')
    args = parser.parse_args()

    pending_file = PROJECT_ROOT / 'candidates' / 'pending_resources.json'
    rejected_file = PROJECT_ROOT / 'candidates' / 'rejected_resources.json'
    csv_file = PROJECT_ROOT / 'THE_RESOURCES_TABLE.csv'

    # 列出待审核资源
    if args.list:
        list_pending(pending_file)
        return 0

    # 批准资源
    if args.approve:
        success, msg = approve_resource(args.approve, pending_file, csv_file)
        print(f"{'✅' if success else '❌'} {msg}")
        return 0 if success else 1

    # 拒绝资源
    if args.reject:
        if not args.reason:
            print("❌ 拒绝资源需要提供原因 (--reason)")
            return 1
        success, msg = reject_resource(args.reject, args.reason, pending_file, rejected_file)
        print(f"{'✅' if success else '❌'} {msg}")
        return 0 if success else 1

    # 处理资源创建 PR
    resources = load_pending_resources(pending_file)

    if args.resource_id:
        # 只处理指定的资源
        resources = [r for r in resources if r['ID'] == args.resource_id]

    if not resources:
        print("📭 没有待处理的资源")
        return 0

    print(f"🚀 准备处理 {len(resources)} 个资源...")

    if args.dry_run:
        print("\n[Dry Run] 将处理以下资源:")
        for r in resources:
            print(f"  - {r['ID']}: {r['DisplayName']}")
        return 0

    success, msg = create_branch_and_pr(resources, csv_file)

    if success:
        # 从待审核列表移除已处理的资源
        remaining = load_pending_resources(pending_file)
        processed_ids = {r['ID'] for r in resources}
        remaining = [r for r in remaining if r['ID'] not in processed_ids]
        save_pending_resources(remaining, pending_file)

        print(f"\n✅ 完成: {msg}")
        return 0
    else:
        print(f"\n❌ 失败: {msg}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
