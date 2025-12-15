#!/usr/bin/env python3
"""
双语 README 生成器 / Bilingual README Generator
简化版：专注于核心功能 / Simplified: Focus on core features
"""

import csv
import hashlib
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml


def load_categories(categories_file: Path) -> List[Dict]:
    """加载分类定义 / Load category definitions"""
    with open(categories_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['categories']


def load_resource_overrides(overrides_file: Path) -> Dict:
    """加载资源覆盖配置 / Load resource overrides configuration"""
    if not overrides_file.exists():
        return {}

    with open(overrides_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return data.get('overrides', {}) if data else {}


def load_csv_resources(csv_file: Path, overrides: Optional[Dict] = None) -> List[Dict]:
    """加载 CSV 资源 / Load CSV resources"""
    resources = []
    overrides = overrides or {}

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 只包含活跃资源 / Only include active resources
            if row.get('IsActive', '').upper() == 'TRUE':
                # 应用资源覆盖 / Apply resource overrides
                resource_id = row['ID']
                if resource_id in overrides:
                    override_data = overrides[resource_id]
                    # 跳过验证标记，不影响生成 / Skip validation flag doesn't affect generation
                    for key, value in override_data.items():
                        if key != 'skip_validation' and key != 'reason':
                            row[key] = value

                resources.append(row)
    return resources


def fix_duplicate_ids(resources: List[Dict]) -> List[Dict]:
    """
    修复重复 ID 问题 / Fix duplicate ID issues
    为重复的 ID 添加序号后缀 / Add numeric suffixes to duplicate IDs
    """
    id_counter = Counter(r['ID'] for r in resources)
    id_usage = {}  #追踪每个 ID 的使用次数

    for resource in resources:
        original_id = resource['ID']

        if id_counter[original_id] > 1:
            # 这个 ID 有重复，添加后缀
            if original_id not in id_usage:
                id_usage[original_id] = 1
            else:
                id_usage[original_id] += 1

            # 添加序号后缀（从第二个重复开始）
            if id_usage[original_id] > 1:
                suffix = id_usage[original_id]
                new_id = f"{original_id}-{suffix}"
                resource['ID'] = new_id
                print(f"🔧 修复重复 ID: {original_id} → {new_id}")

    return resources


def render_resource(resource: Dict) -> str:
    """
    渲染单个资源 / Render single resource
    优先显示中文 / Prefer Chinese display
    """
    # 优先使用中文名称和描述 / Prefer Chinese name and description
    name = resource.get('DisplayName_ZH') or resource.get('DisplayName')
    desc = resource.get('Description_ZH') or resource.get('Description')
    url = resource.get('PrimaryLink', '')
    author = resource.get('Author', '').strip()
    license_info = resource.get('License', '').strip()

    # 基础渲染 / Basic rendering
    parts = [f"- **[{name}]({url})**"]

    # 添加作者信息 / Add author info
    if author:
        author_profile = resource.get('AuthorProfile', '').strip()
        if author_profile:
            parts.append(f" by [{author}]({author_profile})")
        else:
            parts.append(f" by {author}")

    # 添加许可证 / Add license
    if license_info:
        parts.append(f" `{license_info}`")

    # 描述 / Description
    if desc:
        parts.append(f" - {desc}")

    return ''.join(parts)


def render_category(category: Dict, resources: List[Dict]) -> str:
    """
    渲染分类区块 / Render category block
    """
    # 分类标题（双语）/ Category title (bilingual)
    title_zh = category.get('name_zh', category['name'])
    title_en = category['name']
    icon = category.get('icon', '')

    # 创建锚点 / Create anchor
    anchor = category['id']

    lines = []
    lines.append(f"\n## {icon} {title_zh}")
    lines.append(f"*{title_en}*\n")

    # 描述（双语）/ Description (bilingual)
    desc_zh = category.get('description_zh', '')
    if desc_zh:
        lines.append(f"> {desc_zh}\n")

    # 过滤属于该分类的资源 / Filter resources for this category
    category_resources = [
        r for r in resources
        if r['Category'] == category['id']
    ]

    if not category_resources:
        lines.append("_暂无资源 / No resources yet_\n")
        return '\n'.join(lines)

    # 按子分类组织 / Organize by subcategory
    subcategories = category.get('subcategories', [])

    if subcategories:
        for subcat in subcategories:
            subcat_name = subcat['name']
            subcat_name_zh = subcat.get('name_zh', subcat_name)

            # 过滤该子分类的资源 / Filter resources for this subcategory
            subcat_resources = [
                r for r in category_resources
                if r.get('SubCategory', '').strip() == 'general' or
                   r.get('SubCategory', '').strip() == subcat['id']
            ]

            if subcat_resources:
                lines.append(f"\n### {subcat_name_zh}")
                if subcat_name != subcat_name_zh:
                    lines.append(f"*{subcat_name}*")
                lines.append("")

                for resource in subcat_resources:
                    lines.append(render_resource(resource))

                lines.append("")
    else:
        # 无子分类，直接列出资源 / No subcategories, list resources directly
        for resource in category_resources:
            lines.append(render_resource(resource))
        lines.append("")

    return '\n'.join(lines)


def generate_toc(categories: List[Dict], resources: List[Dict]) -> str:
    """
    生成目录 / Generate table of contents
    """
    lines = []
    lines.append("## 📚 目录 | Contents\n")

    for category in categories:
        title_zh = category.get('name_zh', category['name'])
        icon = category.get('icon', '')
        anchor = category['id']

        # 统计该分类的资源数量 / Count resources in this category
        count = len([r for r in resources if r['Category'] == category['id']])

        lines.append(f"- {icon} [{title_zh}](#{anchor}) ({count})")

    return '\n'.join(lines) + "\n"


def generate_stats(resources: List[Dict], categories: List[Dict]) -> str:
    """
    生成统计信息 / Generate statistics
    """
    total = len(resources)
    official = len([r for r in resources if r.get('IsPinned') == 'TRUE'])
    community = total - official

    # 按分类统计 / Statistics by category
    category_counts = {}
    for category in categories:
        cat_id = category['id']
        count = len([r for r in resources if r['Category'] == cat_id])
        if count > 0:
            category_counts[category.get('name_zh', category['name'])] = count

    lines = []
    lines.append("## 📊 统计 | Statistics\n")
    lines.append(f"- **总资源数 | Total Resources**: {total}")
    lines.append(f"- **官方资源 | Official**: {official}")
    lines.append(f"- **社区资源 | Community**: {community}")
    lines.append("")
    lines.append("**分类分布 | Category Distribution**:")
    lines.append("")

    for cat_name, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- {cat_name}: {count}")

    return '\n'.join(lines) + "\n"


def load_template(template_file: Path) -> str:
    """加载 README 模板 / Load README template"""
    if not template_file.exists():
        # 如果模板不存在，返回默认模板 / Return default template if not exists
        return """# 🚀 Awesome Claude Code

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Anthropic-blue)](https://claude.ai/code)

> 精心策划的 Claude Code 资源、工具和最佳实践列表
> A curated list of Claude Code resources, tools, and best practices

{{STATS}}

{{TOC}}

---

{{CONTENT}}

---

## 🤝 贡献 | Contributing

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 许可证 | License

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<div align="center">
  <b>⭐ 如果这个项目对你有帮助，请给一个 Star！</b><br>
  <sub>用 ❤️ 构建，由 Claude Code 社区维护</sub>
</div>
"""

    with open(template_file, 'r', encoding='utf-8') as f:
        return f.read()


def generate_readme(
    csv_path: Path,
    categories_path: Path,
    template_path: Path,
    output_path: Path,
    overrides_path: Optional[Path] = None
):
    """
    生成 README.md / Generate README.md
    """
    print("🚀 开始生成 README...")
    print("🚀 Starting README generation...\n")

    # 加载资源覆盖 / Load resource overrides
    overrides = {}
    if overrides_path and overrides_path.exists():
        print("📖 加载资源覆盖配置...")
        overrides = load_resource_overrides(overrides_path)
        print(f"   ✅ 加载了 {len(overrides)} 个资源覆盖规则")

    # 加载数据 / Load data
    print("📖 加载分类定义...")
    categories = load_categories(categories_path)
    print(f"   ✅ 加载了 {len(categories)} 个分类")

    print("📖 加载资源数据...")
    resources = load_csv_resources(csv_path, overrides)
    print(f"   ✅ 加载了 {len(resources)} 个资源")

    # 修复重复 ID / Fix duplicate IDs
    print("\n🔧 修复重复 ID...")
    resources = fix_duplicate_ids(resources)

    # 加载模板 / Load template
    print("\n📄 加载模板...")
    template = load_template(template_path)

    # 生成各个部分 / Generate sections
    print("⚙️  生成统计信息...")
    stats = generate_stats(resources, categories)

    print("⚙️  生成目录...")
    toc = generate_toc(categories, resources)

    print("⚙️  生成内容...")
    content_parts = []
    for category in categories:
        # 只渲染有资源的分类 / Only render categories with resources
        cat_resources = [r for r in resources if r['Category'] == category['id']]
        if cat_resources:
            content_parts.append(render_category(category, resources))

    content = '\n'.join(content_parts)

    # 替换模板占位符 / Replace template placeholders
    print("✨ 组装 README...")
    readme = template
    readme = readme.replace('{{STATS}}', stats)
    readme = readme.replace('{{TOC}}', toc)
    readme = readme.replace('{{CONTENT}}', content)

    # 替换日期占位符 / Replace date placeholders
    current_date = datetime.now().strftime('%Y-%m-%d')
    readme = readme.replace('<!--UPDATE_DATE-->', current_date)

    # 写入文件 / Write file
    print(f"\n💾 写入文件: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(readme)

    print("\n✅ README.md 生成成功！")
    print("✅ README.md generated successfully!")
    print(f"\n📊 总计: {len(resources)} 个资源，{len(categories)} 个分类")


def main():
    """主函数 / Main function"""
    project_root = Path(__file__).parent.parent

    csv_path = project_root / 'THE_RESOURCES_TABLE.csv'
    categories_path = project_root / 'templates' / 'categories.yaml'
    template_path = project_root / 'templates' / 'README.template.md'
    overrides_path = project_root / 'templates' / 'resource-overrides.yaml'
    output_path = project_root / 'README.md'

    # 检查文件是否存在 / Check if files exist
    if not csv_path.exists():
        print(f"❌ 错误：CSV 文件不存在: {csv_path}")
        return 1

    if not categories_path.exists():
        print(f"❌ 错误：分类文件不存在: {categories_path}")
        return 1

    try:
        generate_readme(csv_path, categories_path, template_path, output_path, overrides_path)
        return 0
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
