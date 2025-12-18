#!/usr/bin/env python3
"""
迁移现有资源到 CSV 格式 / Migrate existing resources to CSV format

此脚本从 AwesomeClaudeCode 的 README.md 中提取资源
并生成符合新架构的 THE_RESOURCES_TABLE.csv 文件

This script extracts resources from AwesomeClaudeCode's README.md
and generates THE_RESOURCES_TABLE.csv following the new architecture
"""

import csv
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import yaml


def load_categories(categories_file: Path) -> Dict:
    """加载分类定义 / Load category definitions"""
    with open(categories_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # 创建分类查找字典 / Create category lookup dictionary
    categories = {}
    for cat in data["categories"]:
        categories[cat["id"]] = cat
        # 添加中文名称作为别名 / Add Chinese name as alias
        if "name_zh" in cat:
            categories[cat["name_zh"]] = cat

    return categories


def generate_resource_id(name: str, prefix: str) -> str:
    """
    生成资源唯一 ID / Generate unique resource ID
    格式 / Format: prefix-hash8
    """
    hash_input = name.lower().strip()
    hash_value = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{hash_value}"


def extract_link_and_text(line: str) -> Optional[Dict[str, str]]:
    """
    从 Markdown 行中提取链接和文本
    Extract link and text from Markdown line

    支持格式 / Supported formats:
    - [Name](url) - description
    - [Name](url) 📌 官方 - description
    - **[Name](url)** - description
    """
    # 匹配 Markdown 链接格式
    # Match Markdown link format
    link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    match = re.search(link_pattern, line)

    if not match:
        return None

    name = match.group(1).strip()
    url = match.group(2).strip()

    # 提取描述（链接后的文本）
    # Extract description (text after link)
    description_start = match.end()
    remaining = line[description_start:].strip()

    # 移除可能的徽章和分隔符
    # Remove possible badges and separators
    remaining = re.sub(r"^[📌🔥⭐]*\s*", "", remaining)
    remaining = re.sub(r"^\s*官方\s*", "", remaining)
    remaining = re.sub(r"^\s*-\s*", "", remaining)

    description = remaining.strip()

    # 检查是否为官方资源（有 📌 或 "官方" 标记）
    # Check if official resource (has 📌 or "官方" marker)
    is_pinned = "📌" in line or "官方" in line

    return {"name": name, "url": url, "description": description, "is_pinned": is_pinned}


def parse_readme(readme_file: Path, categories: Dict) -> List[Dict]:
    """
    解析 README.md 并提取资源
    Parse README.md and extract resources
    """
    with open(readme_file, "r", encoding="utf-8") as f:
        content = f.read()

    resources = []
    current_category = None
    current_section = None

    # 分类映射：中文标题 -> category ID
    # Category mapping: Chinese title -> category ID
    category_mapping = {
        "官方资源": "official-resources",
        "Anthropic 文档与 API": "official-resources",
        "Anthropic SDK 库": "official-resources",
        "Anthropic 教程与示例": "official-resources",
        "安装与配置": "workflows",
        "入门教程": "workflows",
        "高级功能": "workflows",
        "最佳实践": "workflows",
        "案例研究": "case-studies",
        "第三方工具": "tooling",
        "生态系统": "ecosystem",
        "MCP 服务器": "mcp-servers",
        "开源项目": "open-source-projects",
    }

    # 按行处理
    # Process line by line
    lines = content.split("\n")

    for line in lines:
        # 检测二级标题（分类）
        # Detect level-2 heading (category)
        if line.startswith("## "):
            section_title = line[3:].strip()
            # 移除 emoji
            section_title = re.sub(r"^[^\w\s]+\s*", "", section_title)

            # 查找对应的分类 ID
            current_category = None
            for key, cat_id in category_mapping.items():
                if key in section_title:
                    current_category = cat_id
                    current_section = section_title
                    break

            continue

        # 提取资源链接
        # Extract resource links
        if current_category and line.strip().startswith("-"):
            resource_data = extract_link_and_text(line)

            if resource_data:
                category_info = categories.get(current_category, {})
                prefix = category_info.get("prefix", "res")

                # 生成唯一 ID
                # Generate unique ID
                resource_id = generate_resource_id(resource_data["name"], prefix)

                # 检查是否为官方资源（在官方资源分类中）
                # Check if official resource (in official-resources category)
                is_official = current_category == "official-resources" or resource_data["is_pinned"]

                resource = {
                    "ID": resource_id,
                    "DisplayName": resource_data["name"],
                    "DisplayName_ZH": resource_data["name"],  # 将被手动更新 / To be manually updated
                    "Category": current_category,
                    "SubCategory": "general",
                    "PrimaryLink": resource_data["url"],
                    "SecondaryLink": "",
                    "Author": "",  # 需要手动补充 / To be manually added
                    "AuthorProfile": "",
                    "IsActive": "TRUE",
                    "DateAdded": datetime.now().strftime("%Y-%m-%d"),
                    "LastModified": datetime.now().strftime("%Y-%m-%d"),
                    "LastChecked": "",
                    "License": "",  # 需要手动补充 / To be manually added
                    "Description": resource_data["description"],
                    "Description_ZH": resource_data["description"],
                    "Tags_ZH": current_section if current_section else "",
                    "IsPinned": "TRUE" if is_official else "FALSE",
                    "Section": "official" if is_official else "community",
                }

                resources.append(resource)

    return resources


def write_csv(resources: List[Dict], output_file: Path):
    """
    写入 CSV 文件
    Write CSV file
    """
    if not resources:
        print("⚠️ 警告：没有提取到资源 / Warning: No resources extracted")
        return

    fieldnames = [
        "ID",
        "DisplayName",
        "DisplayName_ZH",
        "Category",
        "SubCategory",
        "PrimaryLink",
        "SecondaryLink",
        "Author",
        "AuthorProfile",
        "IsActive",
        "DateAdded",
        "LastModified",
        "LastChecked",
        "License",
        "Description",
        "Description_ZH",
        "Tags_ZH",
        "IsPinned",
        "Section",
    ]

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resources)

    print(f"✅ 成功写入 {len(resources)} 条资源到 {output_file}")
    print(f"✅ Successfully wrote {len(resources)} resources to {output_file}")


def generate_migration_report(resources: List[Dict], output_file: Path):
    """
    生成迁移报告
    Generate migration report
    """
    report = []
    report.append("# 资源迁移报告 / Resource Migration Report")
    report.append(f"\n生成时间 / Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n总资源数 / Total Resources: {len(resources)}")

    # 按分类统计
    # Statistics by category
    category_counts = {}
    official_count = 0

    for res in resources:
        cat = res["Category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if res["IsPinned"] == "TRUE":
            official_count += 1

    report.append(f"\n官方资源 / Official Resources: {official_count}")
    report.append(f"社区资源 / Community Resources: {len(resources) - official_count}")

    report.append("\n## 分类统计 / Category Statistics\n")
    for cat, count in sorted(category_counts.items()):
        report.append(f"- {cat}: {count}")

    report.append("\n## 需要手动补充的字段 / Fields Requiring Manual Input\n")
    report.append("以下字段需要手动补充：")
    report.append("The following fields require manual input:")
    report.append("1. **Author** - 资源作者名称 / Resource author name")
    report.append("2. **AuthorProfile** - 作者主页链接 / Author profile link")
    report.append("3. **License** - 许可证类型（如 MIT, Apache-2.0）/ License type (e.g., MIT, Apache-2.0)")
    report.append("4. **DisplayName_ZH** - 审核并优化中文显示名 / Review and optimize Chinese display name")
    report.append("5. **Description_ZH** - 审核并优化中文描述 / Review and optimize Chinese description")

    report.append("\n## 后续步骤 / Next Steps\n")
    report.append("1. 审查生成的 CSV 文件 / Review generated CSV file")
    report.append("2. 手动补充作者和许可证信息 / Manually add author and license info")
    report.append("3. 优化中文字段翻译 / Optimize Chinese field translations")
    report.append("4. 运行验证脚本检查数据完整性 / Run validation script to check data integrity")
    report.append("5. 生成 README.md / Generate README.md")

    report_content = "\n".join(report)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n📄 迁移报告已生成: {output_file}")
    print(f"📄 Migration report generated: {output_file}")

    # 同时打印到控制台
    # Also print to console
    print("\n" + "=" * 60)
    print(report_content)
    print("=" * 60)


def main():
    """主函数 / Main function"""
    # 设置路径
    # Setup paths
    project_root = Path(__file__).parent.parent
    readme_file = project_root / "README.md"
    categories_file = project_root / "templates" / "categories.yaml"
    output_csv = project_root / "THE_RESOURCES_TABLE.csv"
    report_file = project_root / "MIGRATION_REPORT.md"

    print("🚀 开始迁移资源 / Starting resource migration...")
    print(f"📖 读取 README: {readme_file}")
    print(f"📋 读取分类定义: {categories_file}")

    # 检查文件是否存在
    # Check if files exist
    if not readme_file.exists():
        print(f"❌ 错误：README.md 不存在: {readme_file}")
        return

    if not categories_file.exists():
        print(f"❌ 错误：categories.yaml 不存在: {categories_file}")
        return

    # 加载分类
    # Load categories
    categories = load_categories(categories_file)
    print(f"✅ 加载了 {len(categories)} 个分类")

    # 解析 README
    # Parse README
    resources = parse_readme(readme_file, categories)
    print(f"✅ 提取了 {len(resources)} 个资源")

    # 写入 CSV
    # Write CSV
    write_csv(resources, output_csv)

    # 生成报告
    # Generate report
    generate_migration_report(resources, report_file)

    print("\n✨ 迁移完成！/ Migration complete!")
    print("\n下一步：")
    print("Next steps:")
    print(f"1. 检查 {output_csv}")
    print(f"2. 阅读 {report_file}")
    print("3. 手动补充元数据")
    print("4. 运行 'make generate' 生成 README")


if __name__ == "__main__":
    main()
