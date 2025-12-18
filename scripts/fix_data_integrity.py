#!/usr/bin/env python3
"""
数据完整性修复脚本
Fix data integrity issues in THE_RESOURCES_TABLE.csv

功能 Features:
1. 修复重复ID（生成唯一ID）
2. 补充缺失的Description字段
3. 尝试补充Author和License信息
4. 清理和验证数据

使用 Usage:
    python scripts/fix_data_integrity.py
    python scripts/fix_data_integrity.py --dry-run  # 预览不保存
"""

import csv
import hashlib
import re
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

def generate_unique_id(display_name, primary_link, category_prefix):
    """生成唯一资源ID"""
    content = f"{display_name}{primary_link}"
    hash_value = hashlib.sha256(content.encode('utf-8')).hexdigest()[:8]
    return f"{category_prefix}-{hash_value}"

def get_category_prefix(category):
    """获取分类前缀"""
    prefix_map = {
        'official-resources': 'of',
        'skills': 'skill',
        'workflows': 'w',
        'tooling': 'tool',
        'statusline': 'status',
        'hooks': 'hook',
        'slash-commands': 'cmd',
        'claude-md-files': 'claude',
        'alternative-clients': 'alt',
        'mcp-servers': 'mcp',
        'open-source-projects': 'proj',
        'case-studies': 'case',
        'ecosystem': 'eco',
    }
    return prefix_map.get(category, 'res')

def extract_domain(url):
    """从URL提取域名"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        return domain.replace('www.', '')
    except:
        return ''

def generate_description(row):
    """根据资源信息自动生成描述"""
    display_name = row.get('DisplayName', '')
    display_name_zh = row.get('DisplayName_ZH', '')
    primary_link = row.get('PrimaryLink', '')
    category = row.get('Category', '')

    domain = extract_domain(primary_link)

    # 生成英文描述
    desc_en = ''
    if 'github.com' in primary_link.lower():
        if 'claude-code' in display_name.lower() or 'claude code' in display_name.lower():
            desc_en = "A resource for Claude Code development and usage"
        elif 'mcp' in display_name.lower() or 'server' in display_name.lower():
            desc_en = "MCP server implementation for Claude Code integration"
        elif 'tool' in category:
            desc_en = "Development tool for Claude Code"
        elif 'workflow' in category:
            desc_en = "Workflow and knowledge guide for Claude Code"
        else:
            desc_en = "Open source project related to Claude Code"
    elif 'anthropic.com' in domain or 'claude.ai' in domain:
        desc_en = "Official Anthropic documentation and resources"
    elif 'context7.com' in domain:
        desc_en = f"Mirror and documentation for {display_name}"
    elif 'discord' in domain:
        desc_en = "Community discussion and support platform"
    else:
        # 根据分类生成通用描述
        category_desc = {
            'official-resources': 'Official documentation and resources',
            'workflows': 'Workflow and knowledge guide',
            'tooling': 'Development tool and utility',
            'mcp-servers': 'MCP server implementation',
            'open-source-projects': 'Open source project',
            'case-studies': 'Case study and real-world example',
            'ecosystem': 'Ecosystem resource and integration',
        }
        desc_en = category_desc.get(category, f"Resource for {display_name}")

    # 生成中文描述
    desc_zh = ''
    if 'github.com' in primary_link.lower():
        if 'claude-code' in display_name.lower() or 'claude code' in display_name.lower():
            desc_zh = "Claude Code 开发和使用资源"
        elif 'mcp' in display_name.lower() or 'server' in display_name.lower():
            desc_zh = "Claude Code 集成的 MCP 服务器实现"
        elif 'tool' in category:
            desc_zh = "Claude Code 开发工具"
        elif 'workflow' in category:
            desc_zh = "Claude Code 工作流和知识指南"
        else:
            desc_zh = "与 Claude Code 相关的开源项目"
    elif 'anthropic.com' in domain or 'claude.ai' in domain:
        desc_zh = "Anthropic 官方文档和资源"
    elif 'context7.com' in domain:
        desc_zh = f"{display_name_zh} 的镜像和文档"
    elif 'discord' in domain:
        desc_zh = "社区讨论和支持平台"
    else:
        category_desc_zh = {
            'official-resources': '官方文档和资源',
            'workflows': '工作流和知识指南',
            'tooling': '开发工具和实用程序',
            'mcp-servers': 'MCP 服务器实现',
            'open-source-projects': '开源项目',
            'case-studies': '案例研究和实际示例',
            'ecosystem': '生态系统资源和集成',
        }
        desc_zh = category_desc_zh.get(category, f"{display_name_zh} 资源")

    return desc_en, desc_zh

def extract_author_from_github_url(url):
    """从GitHub URL提取作者"""
    try:
        if 'github.com' in url:
            parts = url.split('github.com/')
            if len(parts) > 1:
                path_parts = parts[1].split('/')
                if len(path_parts) > 0:
                    author = path_parts[0]
                    author_profile = f"https://github.com/{author}"
                    return author, author_profile
    except:
        pass
    return '', ''

def fix_data_integrity(csv_path, output_path=None, dry_run=False):
    """修复CSV数据完整性问题"""

    if output_path is None:
        output_path = csv_path

    print("=" * 60)
    print("数据完整性修复脚本 | Data Integrity Fix Script")
    print("=" * 60)

    # 读取CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\n✓ 读取了 {len(rows)} 个资源")

    # 检查重复ID
    ids = [r['ID'] for r in rows]
    duplicates = {id: count for id, count in Counter(ids).items() if count > 1}

    if duplicates:
        print(f"\n⚠ 发现 {len(duplicates)} 个重复ID，影响 {sum(duplicates.values())} 行")
        for id, count in list(duplicates.items())[:3]:
            print(f"  - {id}: {count} 次")

    # 修复数据
    fixed_rows = []
    seen_ids = set()
    stats = {
        'fixed_duplicate_ids': 0,
        'added_descriptions': 0,
        'added_authors': 0,
        'added_licenses': 0,
    }

    for i, row in enumerate(rows, 1):
        # 修复重复ID
        original_id = row['ID']
        if row['ID'] in seen_ids:
            # 生成新的唯一ID
            category = row['Category']
            prefix = get_category_prefix(category)
            new_id = generate_unique_id(
                row['DisplayName'] + str(i),  # 加入索引确保唯一性
                row['PrimaryLink'],
                prefix
            )
            row['ID'] = new_id
            stats['fixed_duplicate_ids'] += 1
            print(f"  修复重复ID: {original_id} → {new_id}")

        seen_ids.add(row['ID'])

        # 补充Description
        if not row.get('Description') or row['Description'].strip() == '':
            desc_en, desc_zh = generate_description(row)
            row['Description'] = desc_en
            row['Description_ZH'] = desc_zh
            stats['added_descriptions'] += 1
        elif not row.get('Description_ZH') or row['Description_ZH'].strip() == '':
            _, desc_zh = generate_description(row)
            row['Description_ZH'] = desc_zh
            stats['added_descriptions'] += 1

        # 补充Author（从GitHub URL）
        if (not row.get('Author') or row['Author'].strip() == '') and 'github.com' in row['PrimaryLink']:
            author, author_profile = extract_author_from_github_url(row['PrimaryLink'])
            if author:
                row['Author'] = author
                row['AuthorProfile'] = author_profile
                stats['added_authors'] += 1

        # 设置默认的Author（对于非GitHub资源）
        if not row.get('Author') or row['Author'].strip() == '':
            if 'anthropic.com' in row['PrimaryLink'] or 'claude.ai' in row['PrimaryLink']:
                row['Author'] = 'Anthropic'
                row['AuthorProfile'] = 'https://www.anthropic.com'
                stats['added_authors'] += 1
            elif 'context7.com' in row['PrimaryLink']:
                row['Author'] = 'Context7'
                row['AuthorProfile'] = 'https://context7.com'
                stats['added_authors'] += 1

        # 更新LastChecked
        row['LastChecked'] = datetime.now().strftime('%Y-%m-%d')

        fixed_rows.append(row)

    # 显示统计
    print("\n修复统计 | Fix Statistics:")
    print(f"  - 修复重复ID: {stats['fixed_duplicate_ids']}")
    print(f"  - 添加描述: {stats['added_descriptions']}")
    print(f"  - 添加作者: {stats['added_authors']}")
    print(f"  - 总资源数: {len(fixed_rows)}")

    # 保存
    if not dry_run:
        fieldnames = list(rows[0].keys())
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(fixed_rows)

        print(f"\n✓ 已保存到: {output_path}")
    else:
        print("\n⚠ 预览模式，未保存更改（使用 --dry-run=false 保存）")

    # 验证结果
    print("\n验证结果 | Validation:")
    final_ids = [r['ID'] for r in fixed_rows]
    final_duplicates = {id: count for id, count in Counter(final_ids).items() if count > 1}

    if final_duplicates:
        print(f"  ⚠ 仍有 {len(final_duplicates)} 个重复ID")
    else:
        print("  ✓ 所有ID唯一")

    empty_desc = sum(1 for r in fixed_rows if not r.get('Description') or r['Description'].strip() == '')
    print(f"  - 缺失英文描述: {empty_desc}")

    empty_desc_zh = sum(1 for r in fixed_rows if not r.get('Description_ZH') or r['Description_ZH'].strip() == '')
    print(f"  - 缺失中文描述: {empty_desc_zh}")

    empty_author = sum(1 for r in fixed_rows if not r.get('Author') or r['Author'].strip() == '')
    print(f"  - 缺失作者: {empty_author}")

    return fixed_rows

if __name__ == '__main__':
    import sys

    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    csv_path = 'THE_RESOURCES_TABLE.csv'
    fix_data_integrity(csv_path, dry_run=dry_run)
