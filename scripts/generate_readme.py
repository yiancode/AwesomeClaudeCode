#!/usr/bin/env python3
"""
双语 README 生成器 / Bilingual README Generator
增强版：集成 SVG 视觉系统 / Enhanced: Integrated SVG visual system
"""

import csv
import hashlib
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml


def load_categories(categories_file: Path) -> List[Dict]:
    """加载分类定义 / Load category definitions"""
    with open(categories_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["categories"]


def load_resource_overrides(overrides_file: Path) -> Dict:
    """加载资源覆盖配置 / Load resource overrides configuration"""
    if not overrides_file.exists():
        return {}

    with open(overrides_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data.get("overrides", {}) if data else {}


def load_csv_resources(csv_file: Path, overrides: Optional[Dict] = None) -> List[Dict]:
    """加载 CSV 资源 / Load CSV resources"""
    resources = []
    overrides = overrides or {}

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 只包含活跃资源 / Only include active resources
            if row.get("IsActive", "").upper() == "TRUE":
                # 应用资源覆盖 / Apply resource overrides
                resource_id = row["ID"]
                if resource_id in overrides:
                    override_data = overrides[resource_id]
                    # 跳过验证标记，不影响生成 / Skip validation flag doesn't affect generation
                    for key, value in override_data.items():
                        if key != "skip_validation" and key != "reason":
                            row[key] = value

                resources.append(row)
    return resources


def fix_duplicate_ids(resources: List[Dict]) -> List[Dict]:
    """
    修复重复 ID 问题 / Fix duplicate ID issues
    为重复的 ID 添加序号后缀 / Add numeric suffixes to duplicate IDs
    """
    id_counter = Counter(r["ID"] for r in resources)
    id_usage = {}  # 追踪每个 ID 的使用次数

    for resource in resources:
        original_id = resource["ID"]

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
                resource["ID"] = new_id
                print(f"🔧 修复重复 ID: {original_id} → {new_id}")

    return resources


def create_h2_svg_file(text: str, filename: str, assets_dir: str, icon: str = "") -> str:
    """
    创建动画 hero 风格的 H2 标题 SVG 文件（支持中文）。
    Create an animated hero-centered H2 header SVG file (Chinese support).

    Args:
        text: The header text (e.g., "官方资源")
        filename: The output filename
        assets_dir: Directory to save the SVG
        icon: Optional emoji icon to append (e.g., "📘")

    Returns:
        The filename of the created SVG
    """
    # 构建显示文本（可选图标）Build display text with optional icon
    display_text = f"{text} {icon}" if icon else text

    # 转义 XML 特殊字符 Escape XML special characters
    text_escaped = display_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # 根据文本长度计算 viewBox 边界（中文字符约 30px/字，emoji 约 50px）
    # Calculate viewBox bounds based on text length (Chinese chars ~30px each, emoji ~50px)
    text_width = len(text) * 30 + (50 if icon else 0)
    half_text = text_width / 2
    # 确保包含装饰元素（x=187 到 x=613）加上文本边界和充足的填充
    # Ensure we include decorations (x=187 to x=613) plus text bounds with generous padding
    left_bound = int(min(180, 400 - half_text - 30))
    right_bound = int(max(620, 400 + half_text + 30))
    viewbox_width = right_bound - left_bound

    svg_content = """<svg width="100%" height="100" viewBox="{left_bound} 0 {viewbox_width} 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- 微妙的发光效果 - 减少模糊以提高可读性 -->
    <!-- Subtle glow for hero text - reduced blur for better readability -->
    <filter id="heroGlow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="1" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Hero 渐变 - 更亮、更饱和的颜色以提高对比度 -->
    <!-- Hero gradient - brighter, more saturated colors for contrast -->
    <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FF8855" stop-opacity="1">
        <animate attributeName="stop-color" values="#FF8855;#FFAA77;#FF8855" dur="5s" repeatCount="indefinite"/>
      </stop>
      <stop offset="50%" stop-color="#FFAA77" stop-opacity="1"/>
      <stop offset="100%" stop-color="#FF8855" stop-opacity="1">
        <animate attributeName="stop-color" values="#FF8855;#FFCC99;#FF8855" dur="5s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>

    <!-- 强调线渐变 Accent line gradient -->
    <linearGradient id="accentLine" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FFB088" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FF8855" stop-opacity="1">
        <animate attributeName="stop-opacity" values="0.8;1;0.8" dur="3s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="#FFB088" stop-opacity="0"/>
    </linearGradient>

    <!-- 径向发光背景 - 更微妙 Radial glow background - more subtle -->
    <radialGradient id="bgGlow">
      <stop offset="0%" stop-color="#FF8C5A" stop-opacity="0.08">
        <animate attributeName="stop-opacity" values="0.05;0.12;0.05" dur="4s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="#FF8C5A" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- 背景发光 - 更微妙 Background glow - more subtle -->
  <ellipse cx="400" cy="50" rx="300" ry="40" fill="url(#bgGlow)"/>

  <!-- 顶部强调线 Top accent line -->
  <line x1="200" y1="20" x2="600" y2="20" stroke="url(#accentLine)" stroke-width="2" stroke-linecap="round">
    <animate attributeName="stroke-width" values="2;2.5;2" dur="3s" repeatCount="indefinite"/>
  </line>

  <!-- 主 hero 文本 - 更大、更粗，带微妙的深色轮廓以提高对比度 -->
  <!-- Main hero text - larger, bolder, with subtle dark outline for contrast -->
  <text x="400" y="58" font-family="'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, sans-seri" font-size="38" font-weight="900" fill="url(#heroGrad)" text-anchor="middle" filter="url(#heroGlow)" letter-spacing="0.5" stroke="#221111" stroke-width="0.5" paint-order="stroke fill">
    {text_escaped}
  </text>

  <!-- 底部强调线 Bottom accent line -->
  <line x1="200" y1="80" x2="600" y2="80" stroke="url(#accentLine)" stroke-width="2" stroke-linecap="round">
    <animate attributeName="stroke-width" values="2;2.5;2" dur="3s" begin="1.5s" repeatCount="indefinite"/>
  </line>

  <!-- 装饰角元素 Decorative corner elements -->
  <g opacity="0.6">
    <!-- 左上 Top left -->
    <path d="M 195,16 L 195,24 M 195,20 L 187,20" stroke="#FF8855" stroke-width="2" stroke-linecap="round">
      <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" repeatCount="indefinite"/>
    </path>
    <!-- 右上 Top right -->
    <path d="M 605,16 L 605,24 M 605,20 L 613,20" stroke="#FF8855" stroke-width="2" stroke-linecap="round">
      <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" begin="0.5s" repeatCount="indefinite"/>
    </path>
    <!-- 左下 Bottom left -->
    <path d="M 195,76 L 195,84 M 195,80 L 187,80" stroke="#FFAA77" stroke-width="2" stroke-linecap="round">
      <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" begin="1s" repeatCount="indefinite"/>
    </path>
    <!-- 右下 Bottom right -->
    <path d="M 605,76 L 605,84 M 605,80 L 613,80" stroke="#FFAA77" stroke-width="2" stroke-linecap="round">
      <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" begin="1.5s" repeatCount="indefinite"/>
    </path>
  </g>

  <!-- 浮动强调粒子 - 减少不透明度 Floating accent particles - reduced opacity -->
  <g opacity="0.35">
    <circle cx="250" cy="35" r="2" fill="#FFCBA4">
      <animate attributeName="cy" values="35;30;35" dur="4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.5;0" dur="4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="550" cy="45" r="2.5" fill="#FFB088">
      <animate attributeName="cy" values="45;40;45" dur="4.5s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.6;0" dur="4.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="320" cy="68" r="1.5" fill="#FF9B70">
      <animate attributeName="cy" values="68;63;68" dur="3.5s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.4;0" dur="3.5s" repeatCount="indefinite"/>
    </circle>
  </g>
</svg>"""

    # 写入 SVG 文件 Write SVG file
    filepath = os.path.join(assets_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return filename


def create_h3_svg_file(text: str, filename: str, assets_dir: str) -> str:
    """
    创建动画最小内联 H3 标题 SVG 文件（支持中文）。
    Create an animated minimal-inline H3 header SVG file (Chinese support).

    Args:
        text: The header text
        filename: The output filename
        assets_dir: Directory to save the SVG

    Returns:
        The filename of the created SVG
    """
    # 转义 XML 特殊字符 Escape XML special characters
    text_escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # 计算大致文本宽度（中文字符约 14px/字，18px 字体）
    # Calculate approximate text width (Chinese chars ~14px each for 18px font)
    text_width = len(text) * 14
    total_width = text_width + 50  # 为装饰元素添加填充 Add padding for decorative elements

    svg_content = """<svg width="100%" height="36" viewBox="0 0 {total_width} 36" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- 非常微妙的发光 Very subtle glow -->
    <filter id="minimalGlow">
      <feGaussianBlur stdDeviation="1" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- 简单渐变 Simple gradient -->
    <linearGradient id="minimalGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FF6B35" stop-opacity="1"/>
      <stop offset="100%" stop-color="#8B5A3C" stop-opacity="1"/>
    </linearGradient>
  </defs>

  <!-- 左侧装饰元素 Left decorative element -->
  <g>
    <line x1="0" y1="18" x2="12" y2="18" stroke="#FF6B35" stroke-width="3" stroke-linecap="round" opacity="0.8">
      <animate attributeName="x2" values="12;16;12" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.7;1;0.7" dur="3s" repeatCount="indefinite"/>
    </line>
    <circle cx="18" cy="18" r="2" fill="#FF8C5A" opacity="0.7">
      <animate attributeName="r" values="2;2.5;2" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.6;0.9;0.6" dur="3s" repeatCount="indefinite"/>
    </circle>
  </g>

  <!-- 标题文本 Header text -->
  <text x="30" y="24" font-family="'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, sans-seri" font-size="18" font-weight="600" fill="url(#minimalGrad)" filter="url(#minimalGlow)">
    {text_escaped}
    <animate attributeName="opacity" values="0.93;1;0.93" dur="4s" repeatCount="indefinite"/>
  </text>
</svg>"""

    # 写入 SVG 文件 Write SVG file
    filepath = os.path.join(assets_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return filename


def generate_resource_badge_svg(display_name: str, author_name: str = "") -> str:
    """
    为资源名称 badge 生成 SVG 内容，支持主题自适应颜色和中文。
    Generate SVG content for a resource name badge with theme-adaptive colors and Chinese support.

    使用 CSS 媒体查询在浅色和深色方案之间切换。
    Uses CSS media queries to switch between light and dark color schemes.
    - Light: dark text on transparent background
    - Dark: light text on transparent background

    Args:
        display_name: Resource display name (支持中文 supports Chinese)
        author_name: Optional author name (支持中文 supports Chinese)

    Returns:
        SVG content as string
    """
    # 获取首两个字母/首字母用于方框 Get first two letters/initials for the box
    words = display_name.split()
    if len(words) >= 2:
        initials = words[0][0].upper() + words[1][0].upper()
    else:
        # 对于中文，取前两个字符 For Chinese, take first two characters
        initials = display_name[:2].upper()

    # 转义 XML 特殊字符 Escape XML special characters
    name_escaped = display_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    author_escaped = (
        author_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        if author_name
        else ""
    )

    # 根据文本长度计算宽度（中文字符约 14px/字，更大字体需要更多空间）
    # Calculate width based on text length (Chinese chars ~14px each, larger fonts need more space)
    name_width = len(display_name) * 14
    author_width = (len(author_name) * 9 + 35) if author_name else 0  # 35px for "by "
    text_width = name_width + author_width + 70  # 70px for box + padding
    svg_width = max(220, min(700, text_width))

    # 计算作者文本位置 Calculate position for author text
    name_end_x = 48 + name_width

    # 如果提供作者则构建作者文本元素 Build author text element if author provided
    author_element = ""
    if author_name:
        author_element = """
  <text class="author" x="{name_end_x + 10}" y="30" font-family="'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, sans-seri" font-size="14" font-weight="400">by {author_escaped}</text>"""

    svg = """<svg width="{svg_width}" height="44" xmlns="http://www.w3.org/2000/svg">
  <style>
    @media (prefers-color-scheme: light) {{
      .line {{ stroke: #5c5247; }}
      .box {{ stroke: #5c5247; }}
      .initials {{ fill: #c96442; }}
      .name {{ fill: #3d3530; }}
      .author {{ fill: #5c5247; opacity: 0.7; }}
    }}
    @media (prefers-color-scheme: dark) {{
      .line {{ stroke: #888; }}
      .box {{ stroke: #888; }}
      .initials {{ fill: #ff6b4a; }}
      .name {{ fill: #e8e8e8; }}
      .author {{ fill: #aaa; opacity: 0.8; }}
    }}
  </style>

  <!-- 细顶线 Thin top line -->
  <line class="line" x1="4" y1="6" x2="{svg_width - 4}" y2="6" stroke-width="1.25" opacity="0.4"/>

  <!-- 首字母方框 Initials box -->
  <rect class="box" x="4" y="12" width="32" height="26" fill="none" stroke-width="2.25" opacity="0.6"/>
  <text class="initials" x="20" y="30" font-family="'Courier New', Courier, monospace" font-size="14" font-weight="700" text-anchor="middle">{initials}</text>

  <!-- 资源名称 Resource name -->
  <text class="name" x="48" y="30" font-family="'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, sans-seri" font-size="17" font-weight="600">{name_escaped}</text>{author_element}

  <!-- 底部横线 Bottom rule -->
  <line class="line" x1="48" y1="37" x2="{svg_width - 4}" y2="37" stroke-width="1.25" opacity="0.5"/>
</svg>"""
    return svg


def save_resource_badge_svg(display_name: str, author_name: str, assets_dir: str) -> str:
    """
    保存资源名称 SVG badge 到 assets 目录并返回文件名。
    Save a resource name SVG badge to the assets directory and return the filename.

    Args:
        display_name: Resource display name (支持中文 supports Chinese)
        author_name: Author name
        assets_dir: Directory to save SVG

    Returns:
        Filename of the saved SVG
    """
    # 从显示名称创建安全文件名（无 -light 后缀，badge 是主题自适应的）
    # Create a safe filename from the display name (no -light suffix, badge is theme-adaptive)
    safe_name = re.sub(r"[^a-zA-Z0-9]", "-", display_name.lower())
    safe_name = re.sub(r"-+", "-", safe_name).strip("-")
    filename = f"badge-{safe_name}.svg"

    # 生成 SVG 内容（通过 CSS 媒体查询实现主题自适应）
    # Generate the SVG content (theme-adaptive via CSS media queries)
    svg_content = generate_resource_badge_svg(display_name, author_name)

    # 保存到文件 Save to file
    filepath = os.path.join(assets_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return filename


def render_resource(resource: Dict) -> str:
    """
    渲染单个资源 / Render single resource
    优先显示中文 / Prefer Chinese display
    """
    # 优先使用中文名称和描述 / Prefer Chinese name and description
    name = resource.get("DisplayName_ZH") or resource.get("DisplayName")
    desc = resource.get("Description_ZH") or resource.get("Description")
    url = resource.get("PrimaryLink", "")
    author = resource.get("Author", "").strip()
    license_info = resource.get("License", "").strip()

    # 基础渲染 / Basic rendering
    parts = [f"- **[{name}]({url})**"]

    # 添加作者信息 / Add author info
    if author:
        author_profile = resource.get("AuthorProfile", "").strip()
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

    return "".join(parts)


def render_category(category: Dict, resources: List[Dict]) -> str:
    """
    渲染分类区块 / Render category block
    """
    # 分类标题（双语）/ Category title (bilingual)
    title_zh = category.get("name_zh", category["name"])
    title_en = category["name"]
    icon = category.get("icon", "")

    # 创建锚点 / Create anchor
    anchor = category["id"]

    lines = []
    lines.append(f"\n## {icon} {title_zh}")
    lines.append(f"*{title_en}*\n")

    # 描述（双语）/ Description (bilingual)
    desc_zh = category.get("description_zh", "")
    if desc_zh:
        lines.append(f"> {desc_zh}\n")

    # 过滤属于该分类的资源 / Filter resources for this category
    category_resources = [r for r in resources if r["Category"] == category["id"]]

    if not category_resources:
        lines.append("_暂无资源 / No resources yet_\n")
        return "\n".join(lines)

    # 按子分类组织 / Organize by subcategory
    subcategories = category.get("subcategories", [])

    if subcategories:
        for subcat in subcategories:
            subcat_name = subcat["name"]
            subcat_name_zh = subcat.get("name_zh", subcat_name)

            # 过滤该子分类的资源 / Filter resources for this subcategory
            # 修复：只匹配精确的子分类，不再将 general 添加到所有子分类
            # Fix: Only match exact subcategory, don't add general to all subcategories
            subcat_resources = [r for r in category_resources if r.get("SubCategory", "").strip() == subcat["id"]]

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

    return "\n".join(lines)


def generate_toc(categories: List[Dict], resources: List[Dict]) -> str:
    """
    生成目录 / Generate table of contents
    """
    lines = []
    lines.append("## 📚 目录 | Contents\n")

    for category in categories:
        title_zh = category.get("name_zh", category["name"])
        icon = category.get("icon", "")
        anchor = category["id"]

        # 统计该分类的资源数量 / Count resources in this category
        count = len([r for r in resources if r["Category"] == category["id"]])

        lines.append(f"- {icon} [{title_zh}](#{anchor}) ({count})")

    return "\n".join(lines) + "\n"


def generate_stats(resources: List[Dict], categories: List[Dict]) -> str:
    """
    生成统计信息 / Generate statistics
    """
    total = len(resources)
    official = len([r for r in resources if r.get("IsPinned") == "TRUE"])
    community = total - official

    # 按分类统计 / Statistics by category
    category_counts = {}
    for category in categories:
        cat_id = category["id"]
        count = len([r for r in resources if r["Category"] == cat_id])
        if count > 0:
            category_counts[category.get("name_zh", category["name"])] = count

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

    return "\n".join(lines) + "\n"


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

    with open(template_file, "r", encoding="utf-8") as f:
        return f.read()


def generate_readme(
    csv_path: Path, categories_path: Path, template_path: Path, output_path: Path, overrides_path: Optional[Path] = None
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
        cat_resources = [r for r in resources if r["Category"] == category["id"]]
        if cat_resources:
            content_parts.append(render_category(category, resources))

    content = "\n".join(content_parts)

    # 替换模板占位符 / Replace template placeholders
    print("✨ 组装 README...")
    readme = template
    readme = readme.replace("{{STATS}}", stats)
    readme = readme.replace("{{TOC}}", toc)
    readme = readme.replace("{{CONTENT}}", content)

    # 替换日期占位符 / Replace date placeholders
    current_date = datetime.now().strftime("%Y-%m-%d")
    readme = readme.replace("<!--UPDATE_DATE-->", current_date)

    # 写入文件 / Write file
    print(f"\n💾 写入文件: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(readme)

    print("\n✅ README.md 生成成功！")
    print("✅ README.md generated successfully!")
    print(f"\n📊 总计: {len(resources)} 个资源，{len(categories)} 个分类")


def main():
    """主函数 / Main function"""
    project_root = Path(__file__).parent.parent

    csv_path = project_root / "THE_RESOURCES_TABLE.csv"
    categories_path = project_root / "templates" / "categories.yaml"
    template_path = project_root / "templates" / "README.template.md"
    overrides_path = project_root / "templates" / "resource-overrides.yaml"
    output_path = project_root / "README.md"

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


if __name__ == "__main__":
    exit(main())
