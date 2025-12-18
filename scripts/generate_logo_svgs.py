#!/usr/bin/env python3
"""
为 AwesomeClaudeCode 仓库生成响应式 SVG logo。

Generate responsive SVG logos for the AwesomeClaudeCode repository.

这个脚本创建：
This script creates:
- 浅色和深色主题版本的标题 logo
- Light and dark theme versions of the title logo
- 支持中文文本渲染
- Chinese text rendering support
"""

from pathlib import Path


def generate_logo_svg(theme: str = "light") -> str:
    """生成带有中英双语标题的 SVG logo。

    Generate SVG with bilingual Chinese-English title.

    Args:
        theme: "light" or "dark"

    Returns:
        SVG content as string
    """
    # 根据主题选择颜色
    # Choose colors based on theme
    if theme == "light":
        primary_color = "#FF6B35"  # 橙色 Orange
        secondary_color = "#24292e"  # 深灰 Dark gray
        accent_color = "#9C4EFF"  # 紫色 Purple
        glow_opacity = "0.3"
    else:  # dark
        primary_color = "#FF8C5A"  # 浅橙 Light orange
        secondary_color = "#e1e4e8"  # 浅灰 Light gray
        accent_color = "#B47FFF"  # 浅紫 Light purple
        glow_opacity = "0.4"

    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 200" preserveAspectRatio="xMidYMid meet">
  <defs>
    <!-- 渐变定义 Gradient definitions -->
    <linearGradient id="titleGrad-{theme}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{primary_color}"/>
      <stop offset="50%" stop-color="{accent_color}"/>
      <stop offset="100%" stop-color="{primary_color}"/>
      <animate attributeName="x1" values="0%;-100%;0%" dur="8s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="100%;200%;100%" dur="8s" repeatCount="indefinite"/>
    </linearGradient>

    <!-- 发光效果 Glow effect -->
    <filter id="glow-{theme}">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- 强发光效果 Strong glow -->
    <filter id="strongGlow-{theme}">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- 背景装饰圆环 Background decorative circles -->
  <circle cx="100" cy="100" r="60" fill="none" stroke="{accent_color}" stroke-width="1.5" opacity="0.2">
    <animate attributeName="r" values="60;65;60" dur="4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.15;0.25;0.15" dur="4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="900" cy="100" r="60" fill="none" stroke="{primary_color}" stroke-width="1.5" opacity="0.2">
    <animate attributeName="r" values="60;65;60" dur="4s" begin="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.15;0.25;0.15" dur="4s" begin="2s" repeatCount="indefinite"/>
  </circle>

  <!-- 主标题 - 中文 Main title - Chinese -->
  <text x="500" y="85"
        font-family="'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', sans-seri"
        font-size="52"
        font-weight="bold"
        fill="url(#titleGrad-{theme})"
        text-anchor="middle"
        filter="url(#strongGlow-{theme})">
    精选 Claude Code 资源
    <animate attributeName="opacity" values="0.95;1;0.95" dur="3s" repeatCount="indefinite"/>
  </text>

  <!-- 副标题 - 英文 Subtitle - English -->
  <text x="500" y="125"
        font-family="system-ui, -apple-system, 'Helvetica Neue', sans-seri"
        font-size="24"
        font-weight="400"
        fill="{secondary_color}"
        text-anchor="middle"
        opacity="0.85"
        filter="url(#glow-{theme})">
    Awesome Claude Code Resources
  </text>

  <!-- 底部装饰线 Bottom decorative line -->
  <line x1="300" y1="160" x2="700" y2="160"
        stroke="url(#titleGrad-{theme})"
        stroke-width="2"
        stroke-linecap="round"
        opacity="{glow_opacity}">
    <animate attributeName="opacity" values="{glow_opacity};{float(glow_opacity) + 0.2};{glow_opacity}" dur="3s" repeatCount="indefinite"/>
  </line>

  <!-- 左侧装饰点 Left decorative dot -->
  <circle cx="285" cy="160" r="4" fill="{accent_color}" opacity="0.6">
    <animate attributeName="r" values="4;5;4" dur="3s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.5;0.8;0.5" dur="3s" repeatCount="indefinite"/>
  </circle>

  <!-- 右侧装饰点 Right decorative dot -->
  <circle cx="715" cy="160" r="4" fill="{primary_color}" opacity="0.6">
    <animate attributeName="r" values="4;5;4" dur="3s" begin="1.5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.5;0.8;0.5" dur="3s" begin="1.5s" repeatCount="indefinite"/>
  </circle>
</svg>"""

    return svg_content


def main():
    """生成所有 logo SVG 文件。Generate all logo SVG files."""
    # 获取项目根目录 Get the project root directory
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    assets_dir = project_root / "assets"

    # 创建 assets 目录（如果不存在）Create assets directory if it doesn't exist
    assets_dir.mkdir(exist_ok=True)

    # 生成 logo SVG Generate logo SVGs
    logo_light = generate_logo_svg("light")
    logo_dark = generate_logo_svg("dark")

    # 写入文件 Write files
    files_to_write = {
        "logo-light.svg": logo_light,
        "logo-dark.svg": logo_dark,
    }

    for filename, content in files_to_write.items():
        filepath = assets_dir / filename
        filepath.write_text(content, encoding="utf-8")
        print(f"✅ 生成 Generated: {filepath}")

    print("\n🎨 所有 logo SVG 文件已成功生成！")
    print("🎨 All logo SVG files have been generated successfully!")
    print("📝 运行 'make generate' 更新 README 中的 logo。")
    print("📝 Run 'make generate' to update the README with the new logos.")


if __name__ == "__main__":
    main()
