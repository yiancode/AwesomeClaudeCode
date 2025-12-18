#!/usr/bin/env python3
"""
Issue 自动处理脚本 / Issue Automatic Processing Script

从 GitHub Issue 表单解析资源提交，并添加到候选队列。
Parses resource submissions from GitHub Issue forms and adds them to the candidate queue.

用法 / Usage:
    python scripts/process_issue.py --issue-number 123 --issue-body "..."
    或 / or:
    设置环境变量 ISSUE_NUMBER 和 ISSUE_BODY
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
import yaml


# 项目根目录 / Project root
PROJECT_ROOT = Path(__file__).parent.parent

# 分类名称映射（从 Issue 表单选项到 category ID）
# Category name mapping (from Issue form options to category IDs)
CATEGORY_MAPPING = {
    "🏛️ 官方资源 / Official Documentation": "official-resources",
    "🤖 代理技能 / Agent Skills": "skills",
    "🧠 工作流与知识指南 / Workflows & Knowledge Guides": "workflows",
    "🧰 工具 / Tooling": "tooling",
    "📊 状态栏 / Status Lines": "statusline",
    "🪝 钩子 / Hooks": "hooks",
    "🔪 斜杠命令 / Slash-Commands": "slash-commands",
    "📂 CLAUDE.md 文件 / CLAUDE.md Files": "claude-md-files",
    "📱 替代客户端 / Alternative Clients": "alternative-clients",
    "🔌 MCP 服务器 / MCP Servers": "mcp-servers",
    "📦 开源项目 / Open Source Projects": "open-source-projects",
    "📂 案例研究 / Case Studies": "case-studies",
    "🌐 生态系统 / Ecosystem": "ecosystem",
}

# 子分类映射 / Subcategory mapping
SUBCATEGORY_MAPPING = {
    "通用 / General": "general",
    "API 与文档 / API & Documentation": "api-docs",
    "SDK 库 / SDK Libraries": "sdk-libraries",
    "教程与示例 / Tutorials & Examples": "tutorials",
    "最佳实践 / Best Practices": "best-practices",
    "IDE 集成 / IDE Integrations": "ide-integrations",
    "使用监控 / Usage Monitors": "usage-monitors",
    "编排器 / Orchestrators": "orchestrators",
    "版本控制与 Git / Version Control & Git": "version-control-git",
    "代码分析与测试 / Code Analysis & Testing": "code-analysis-testing",
    "上下文加载与预热 / Context Loading & Priming": "context-loading-priming",
    "文档与变更日志 / Documentation & Changelogs": "documentation-changelogs",
    "持续集成 / 部署 / CI / Deployment": "ci-deployment",
    "项目与任务管理 / Project & Task Management": "project-task-management",
    "特定语言 / Language-Specific": "language-specific",
    "特定领域 / Domain-Specific": "domain-specific",
    "项目脚手架与 MCP / Project Scaffolding & MCP": "project-scaffolding-mcp",
    "文件系统 / Filesystem": "filesystem",
    "云服务 / Cloud Services": "cloud-services",
    "数据库 / Databases": "databases",
    "API 集成 / API Integrations": "api-integrations",
    "模板 / Templates": "templates",
    "扩展 / Extensions": "extensions",
    "Web 开发 / Web Development": "web-development",
    "移动开发 / Mobile Development": "mobile-development",
    "数据科学 / Data Science": "data-science",
    "DevOps": "devops",
    "学习资源 / Learning Resources": "learning-resources",
    "社区 / Community": "community",
    "第三方工具 / Third-party Tools": "third-party-tools",
    "其他 / Miscellaneous": "miscellaneous",
}


def load_categories() -> dict:
    """
    加载分类定义以获取 prefix 映射
    Load category definitions to get prefix mapping
    """
    categories_file = PROJECT_ROOT / "templates" / "categories.yaml"
    with open(categories_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # 创建 category_id -> prefix 映射
    return {cat['id']: cat['prefix'] for cat in data['categories']}


def generate_resource_id(category_id: str, url: str, categories_prefix: dict) -> str:
    """
    生成资源 ID / Generate resource ID
    格式: {prefix}-{hash8}
    """
    prefix = categories_prefix.get(category_id, 'res')
    # 使用 URL 生成 hash
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{prefix}-{url_hash}"


def parse_issue_body(body: str) -> dict:
    """
    解析 Issue 表单内容 / Parse Issue form content

    GitHub Issue 表单使用特定格式:
    ### 标签名
    值

    ### 另一个标签
    另一个值
    """
    result = {}

    # 使用正则匹配 ### 标题 和其后的内容
    # Match ### headers and their content
    pattern = r'###\s*(.+?)\s*\n(.*?)(?=###|\Z)'
    matches = re.findall(pattern, body, re.DOTALL)

    for label, value in matches:
        # 清理标签和值
        label = label.strip()
        value = value.strip()

        # 移除 "无响应" / "_No response_" 占位符
        if value.lower() in ['_no response_', '无响应', '']:
            value = ''

        result[label] = value

    return result


def extract_descriptions(description_text: str) -> tuple:
    """
    从描述文本中分离中英文描述
    Separate Chinese and English descriptions from description text

    Returns: (description_zh, description_en)
    """
    if not description_text:
        return '', ''

    lines = description_text.strip().split('\n')
    desc_zh = ''
    desc_en = ''

    current_lang = None
    current_text = []

    for line in lines:
        line_lower = line.lower().strip()

        # 检测语言标记
        if '中文描述' in line or 'chinese description' in line_lower:
            if current_lang == 'en' and current_text:
                desc_en = ' '.join(current_text).strip()
            current_lang = 'zh'
            current_text = []
        elif '英文描述' in line or 'english description' in line_lower:
            if current_lang == 'zh' and current_text:
                desc_zh = ' '.join(current_text).strip()
            current_lang = 'en'
            current_text = []
        elif line.strip():
            current_text.append(line.strip())

    # 处理最后一段
    if current_lang == 'zh' and current_text:
        desc_zh = ' '.join(current_text).strip()
    elif current_lang == 'en' and current_text:
        desc_en = ' '.join(current_text).strip()
    elif current_text and not desc_zh:
        # 如果没有明确标记，假设是中文
        desc_zh = ' '.join(current_text).strip()

    return desc_zh, desc_en


def validate_url(url: str, timeout: int = 10) -> tuple:
    """
    验证 URL 是否可访问
    Validate if URL is accessible

    Returns: (is_valid, status_code, error_message)
    """
    if not url:
        return False, 0, "URL 为空 / URL is empty"

    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, 0, "URL 格式无效 / Invalid URL format"

        headers = {
            'User-Agent': 'AwesomeClaudeCode-Bot/1.0 (+https://github.com/yiancode/AwesomeClaudeCode)'
        }

        response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)

        if response.status_code < 400:
            return True, response.status_code, None
        else:
            return False, response.status_code, f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        return False, 0, "请求超时 / Request timeout"
    except requests.exceptions.ConnectionError:
        return False, 0, "连接失败 / Connection failed"
    except Exception as e:
        return False, 0, str(e)


def check_duplicate(url: str, pending_file: Path, rejected_file: Path) -> tuple:
    """
    检查 URL 是否已存在（在待审核或已拒绝列表中）
    Check if URL already exists (in pending or rejected list)

    Returns: (is_duplicate, location)
    """
    # 规范化 URL
    normalized_url = url.rstrip('/').lower()

    # 检查待审核列表
    if pending_file.exists():
        with open(pending_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for res in data.get('resources', []):
                if res.get('PrimaryLink', '').rstrip('/').lower() == normalized_url:
                    return True, 'pending'

    # 检查已拒绝列表
    if rejected_file.exists():
        with open(rejected_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for res in data.get('resources', []):
                if res.get('PrimaryLink', '').rstrip('/').lower() == normalized_url:
                    return True, 'rejected'

    # 检查主 CSV
    csv_file = PROJECT_ROOT / 'THE_RESOURCES_TABLE.csv'
    if csv_file.exists():
        import csv
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('PrimaryLink', '').rstrip('/').lower() == normalized_url:
                    return True, 'csv'

    return False, None


def extract_github_info(url: str) -> dict:
    """
    从 GitHub URL 提取作者信息
    Extract author info from GitHub URL
    """
    result = {'author': '', 'author_profile': ''}

    parsed = urlparse(url)
    if 'github.com' not in parsed.netloc:
        return result

    # 提取 owner/repo
    path_parts = [p for p in parsed.path.split('/') if p]
    if len(path_parts) >= 1:
        owner = path_parts[0]
        result['author'] = owner
        result['author_profile'] = f"https://github.com/{owner}"

    return result


def create_candidate_resource(parsed_data: dict, issue_number: int, categories_prefix: dict) -> dict:
    """
    从解析的 Issue 数据创建候选资源
    Create candidate resource from parsed Issue data
    """
    # 提取字段（使用多种可能的标签名）
    name = (parsed_data.get('资源名称 / Resource Name') or
            parsed_data.get('资源名称') or
            parsed_data.get('Resource Name', '')).strip()

    url = (parsed_data.get('资源链接 / Resource URL') or
           parsed_data.get('资源链接') or
           parsed_data.get('Resource URL', '')).strip()

    category_raw = (parsed_data.get('主分类 / Primary Category') or
                    parsed_data.get('主分类') or
                    parsed_data.get('Primary Category', '')).strip()

    subcategory_raw = (parsed_data.get('子分类 / Subcategory (可选 / Optional)') or
                       parsed_data.get('子分类') or
                       parsed_data.get('Subcategory', '')).strip()

    description_raw = (parsed_data.get('资源描述 / Resource Description') or
                       parsed_data.get('资源描述') or
                       parsed_data.get('Resource Description', '')).strip()

    author = (parsed_data.get('作者 / Author (可选 / Optional)') or
              parsed_data.get('作者') or
              parsed_data.get('Author', '')).strip()

    author_profile = (parsed_data.get('作者主页 / Author Profile (可选 / Optional)') or
                      parsed_data.get('作者主页') or
                      parsed_data.get('Author Profile', '')).strip()

    license_info = (parsed_data.get('许可证 / License (可选 / Optional)') or
                    parsed_data.get('许可证') or
                    parsed_data.get('License', '')).strip()

    secondary_link = (parsed_data.get('备用链接 / Secondary Link (可选 / Optional)') or
                      parsed_data.get('备用链接') or
                      parsed_data.get('Secondary Link', '')).strip()

    # 映射分类
    category_id = CATEGORY_MAPPING.get(category_raw, 'ecosystem')
    subcategory_id = SUBCATEGORY_MAPPING.get(subcategory_raw, 'general')

    # 分离中英文描述
    desc_zh, desc_en = extract_descriptions(description_raw)
    if not desc_en:
        desc_en = desc_zh  # 如果没有英文，使用中文

    # 如果没有提供作者信息，尝试从 GitHub URL 提取
    if not author and 'github.com' in url:
        github_info = extract_github_info(url)
        author = github_info['author']
        if not author_profile:
            author_profile = github_info['author_profile']

    # 生成资源 ID
    resource_id = generate_resource_id(category_id, url, categories_prefix)

    # 当前日期
    today = datetime.now().strftime('%Y/%m/%d')

    # 构建资源对象
    resource = {
        'ID': resource_id,
        'DisplayName': name,
        'DisplayName_ZH': name,  # Issue 提交通常是中文名
        'Category': category_id,
        'SubCategory': subcategory_id,
        'PrimaryLink': url,
        'SecondaryLink': secondary_link,
        'Author': author,
        'AuthorProfile': author_profile,
        'IsActive': 'TRUE',
        'DateAdded': today,
        'LastModified': today,
        'LastChecked': today,
        'License': license_info,
        'Description': desc_en,
        'Description_ZH': desc_zh,
        'Tags_ZH': '',
        'IsPinned': 'FALSE',
        'Section': 'community',
        # 元数据（不会写入 CSV）
        '_source_issue': issue_number,
        '_submitted_at': datetime.now().isoformat(),
        '_status': 'pending',
    }

    return resource


def add_to_pending(resource: dict, pending_file: Path) -> bool:
    """
    添加资源到待审核队列
    Add resource to pending queue
    """
    # 加载现有数据
    if pending_file.exists():
        with open(pending_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "_comment": "候选资源队列 - 待审核的资源 / Candidate resource queue - resources pending review",
            "_schema_version": "1.0",
            "resources": []
        }

    # 添加新资源
    data['resources'].append(resource)

    # 保存
    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return True


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description='Process GitHub Issue for resource submission')
    parser.add_argument('--issue-number', type=int, help='Issue number')
    parser.add_argument('--issue-body', type=str, help='Issue body content')
    parser.add_argument('--dry-run', action='store_true', help='Do not modify files')
    args = parser.parse_args()

    # 从参数或环境变量获取
    issue_number = args.issue_number or int(os.environ.get('ISSUE_NUMBER', 0))
    issue_body = args.issue_body or os.environ.get('ISSUE_BODY', '')

    if not issue_number or not issue_body:
        print("❌ 错误：需要提供 issue-number 和 issue-body")
        print("❌ Error: issue-number and issue-body are required")
        sys.exit(1)

    print(f"📋 处理 Issue #{issue_number}...")
    print(f"📋 Processing Issue #{issue_number}...")

    # 加载分类配置
    categories_prefix = load_categories()

    # 解析 Issue 内容
    print("\n🔍 解析 Issue 内容...")
    parsed = parse_issue_body(issue_body)

    if not parsed:
        print("❌ 无法解析 Issue 内容")
        print("❌ Failed to parse Issue content")
        sys.exit(1)

    print(f"   找到 {len(parsed)} 个字段")

    # 提取 URL 进行验证
    url = (parsed.get('资源链接 / Resource URL') or
           parsed.get('资源链接') or
           parsed.get('Resource URL', '')).strip()

    if not url:
        print("❌ 未找到资源链接")
        print("❌ Resource URL not found")
        sys.exit(1)

    print(f"\n🔗 验证 URL: {url}")

    # 检查重复
    pending_file = PROJECT_ROOT / 'candidates' / 'pending_resources.json'
    rejected_file = PROJECT_ROOT / 'candidates' / 'rejected_resources.json'

    is_dup, dup_location = check_duplicate(url, pending_file, rejected_file)
    if is_dup:
        print(f"⚠️  发现重复资源 (在 {dup_location} 中)")
        print(f"⚠️  Duplicate resource found (in {dup_location})")
        # 输出结果供 GitHub Actions 使用
        print("::set-output name=status::duplicate")
        print(f"::set-output name=duplicate_location::{dup_location}")
        sys.exit(0)  # 不是错误，只是重复

    # 验证 URL 可访问性
    is_valid, status_code, error = validate_url(url)
    if not is_valid:
        print(f"⚠️  URL 验证失败: {error}")
        print(f"⚠️  URL validation failed: {error}")
        # 仍然可以继续，但标记状态
        print("::set-output name=url_status::invalid")
        print(f"::set-output name=url_error::{error}")
    else:
        print(f"   ✅ URL 有效 (HTTP {status_code})")

    # 创建候选资源
    print("\n📦 创建候选资源...")
    resource = create_candidate_resource(parsed, issue_number, categories_prefix)

    print(f"   ID: {resource['ID']}")
    print(f"   名称: {resource['DisplayName']}")
    print(f"   分类: {resource['Category']}/{resource['SubCategory']}")
    print(f"   作者: {resource['Author']}")

    if args.dry_run:
        print("\n🔍 [Dry Run] 资源内容:")
        print(json.dumps(resource, ensure_ascii=False, indent=2))
        sys.exit(0)

    # 添加到待审核队列
    print("\n💾 添加到待审核队列...")
    add_to_pending(resource, pending_file)

    print("\n✅ 处理完成！")
    print("✅ Processing complete!")

    # 输出结果供 GitHub Actions 使用
    print("::set-output name=status::success")
    print(f"::set-output name=resource_id::{resource['ID']}")
    print(f"::set-output name=resource_name::{resource['DisplayName']}")
    print(f"::set-output name=category::{resource['Category']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
