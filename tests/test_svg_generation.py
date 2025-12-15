"""
SVG 生成功能测试
SVG Generation Tests

根据 CLAUDE.md 要求:
- 使用真实数据，不使用 Mock
- 跟踪所有验证失败
- 有意义的断言验证具体预期值
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入生成脚本
from scripts.generate_logo_svgs import generate_logo_svg
from scripts.generate_ticker_svg import generate_ticker_svg, load_repos


def test_generate_logo_svgs():
    """测试 Logo SVG 生成。Test logo SVG generation."""
    failures = []

    try:
        # 生成 logo SVG
        assets_dir = PROJECT_ROOT / "assets"
        assets_dir.mkdir(exist_ok=True)

        # 生成两个主题的 logo
        logo_light = generate_logo_svg("light")
        logo_dark = generate_logo_svg("dark")

        # 写入文件
        (assets_dir / "logo-light.svg").write_text(logo_light, encoding="utf-8")
        (assets_dir / "logo-dark.svg").write_text(logo_dark, encoding="utf-8")

        # 验证文件存在
        light_logo = PROJECT_ROOT / "assets" / "logo-light.svg"
        dark_logo = PROJECT_ROOT / "assets" / "logo-dark.svg"

        if not light_logo.exists():
            failures.append("❌ logo-light.svg 文件未生成")

        if not dark_logo.exists():
            failures.append("❌ logo-dark.svg 文件未生成")

        # 如果文件存在，验证内容
        if light_logo.exists():
            content = light_logo.read_text(encoding="utf-8")

            # 验证是有效的 SVG
            if "<svg" not in content:
                failures.append("❌ logo-light.svg 不是有效的 SVG 文件")

            # 验证包含中文文本
            if "Claude Code" not in content:
                failures.append("❌ logo-light.svg 缺少 'Claude Code' 文本")

            if "资源" not in content:
                failures.append("❌ logo-light.svg 缺少中文文本 '资源'")

            # 验证包含动画
            if "<animate" not in content:
                failures.append("❌ logo-light.svg 缺少动画元素")

        if dark_logo.exists():
            content = dark_logo.read_text(encoding="utf-8")

            # 验证是有效的 SVG
            if "<svg" not in content:
                failures.append("❌ logo-dark.svg 不是有效的 SVG 文件")

            # 验证包含中文文本
            if "资源" not in content:
                failures.append("❌ logo-dark.svg 缺少中文文本")

    except Exception as e:
        failures.append(f"❌ 生成 logo SVG 失败: {e}")

    return failures


def test_load_ticker_data():
    """测试加载 ticker 数据。Test loading ticker data."""
    failures = []

    try:
        data_file = PROJECT_ROOT / "data" / "repo-ticker.csv"

        if not data_file.exists():
            failures.append("❌ repo-ticker.csv 文件不存在")
            return failures

        repos = load_repos(data_file)

        # 验证返回的是列表
        if not isinstance(repos, list):
            failures.append(f"❌ ticker 数据类型错误: {type(repos)}，应为 list")
            return failures

        # 验证至少有一些数据
        if len(repos) == 0:
            failures.append("❌ ticker 数据为空")
            return failures

        # 验证第一个仓库的数据结构
        if repos:
            first_repo = repos[0]
            required_fields = ["full_name", "stars", "watchers", "forks"]
            for field in required_fields:
                if field not in first_repo:
                    failures.append(f"❌ ticker 数据缺少字段 '{field}'")

    except Exception as e:
        failures.append(f"❌ 加载 ticker 数据失败: {e}")

    return failures


def test_generate_ticker_svg():
    """测试 Ticker SVG 生成。Test ticker SVG generation."""
    failures = []

    try:
        # 加载数据
        data_file = PROJECT_ROOT / "data" / "repo-ticker.csv"
        if not data_file.exists():
            failures.append("❌ repo-ticker.csv 文件不存在，跳过测试")
            return failures

        # 加载仓库数据
        repos = load_repos(data_file)

        # 生成 ticker SVG
        assets_dir = PROJECT_ROOT / "assets"
        assets_dir.mkdir(exist_ok=True)

        # 生成两个主题的 ticker
        ticker_dark = generate_ticker_svg(repos, theme="dark")
        ticker_light = generate_ticker_svg(repos, theme="light")

        # 写入文件
        (assets_dir / "repo-ticker.svg").write_text(ticker_dark, encoding="utf-8")
        (assets_dir / "repo-ticker-light.svg").write_text(ticker_light, encoding="utf-8")

        # 验证文件存在
        dark_ticker = PROJECT_ROOT / "assets" / "repo-ticker.svg"
        light_ticker = PROJECT_ROOT / "assets" / "repo-ticker-light.svg"

        if not dark_ticker.exists():
            failures.append("❌ repo-ticker.svg 文件未生成")

        if not light_ticker.exists():
            failures.append("❌ repo-ticker-light.svg 文件未生成")

        # 如果文件存在，验证内容
        if dark_ticker.exists():
            content = dark_ticker.read_text(encoding="utf-8")

            # 验证是有效的 SVG
            if "<svg" not in content:
                failures.append("❌ repo-ticker.svg 不是有效的 SVG 文件")

            # 验证包含 ticker 文本
            if "CLAUDE CODE" not in content:
                failures.append("❌ repo-ticker.svg 缺少 'CLAUDE CODE' 文本")

            # 验证包含滚动动画
            if "<animateTransform" not in content:
                failures.append("❌ repo-ticker.svg 缺少滚动动画")

            # 验证包含仓库名称（至少一个）
            if "anthropics" not in content and "AwesomeClaudeCode" not in content:
                failures.append("❌ repo-ticker.svg 缺少仓库名称")

    except Exception as e:
        failures.append(f"❌ 生成 ticker SVG 失败: {e}")

    return failures


def test_svg_chinese_encoding():
    """测试 SVG 中文编码正确。Test SVG Chinese encoding correctness."""
    failures = []

    # 测试所有 SVG 文件
    svg_files = [
        PROJECT_ROOT / "assets" / "logo-light.svg",
        PROJECT_ROOT / "assets" / "logo-dark.svg",
        PROJECT_ROOT / "assets" / "repo-ticker.svg",
        PROJECT_ROOT / "assets" / "repo-ticker-light.svg",
    ]

    for svg_file in svg_files:
        if not svg_file.exists():
            continue  # 跳过不存在的文件

        try:
            content = svg_file.read_text(encoding="utf-8")

            # 验证 UTF-8 编码正确（通过成功读取验证）
            # 验证包含中文字符
            has_chinese = any("\u4e00" <= char <= "\u9fff" for char in content)

            # logo SVG 应该包含中文
            if "logo" in svg_file.name and not has_chinese:
                failures.append(f"❌ {svg_file.name} 缺少中文字符")

        except UnicodeDecodeError:
            failures.append(f"❌ {svg_file.name} UTF-8 编码错误")
        except Exception as e:
            failures.append(f"❌ 读取 {svg_file.name} 失败: {e}")

    return failures


def test_svg_file_sizes():
    """测试 SVG 文件大小合理。Test SVG file sizes are reasonable."""
    failures = []

    svg_files = {
        PROJECT_ROOT / "assets" / "logo-light.svg": (1000, 10000),  # 1-10KB
        PROJECT_ROOT / "assets" / "logo-dark.svg": (1000, 10000),
        PROJECT_ROOT / "assets" / "repo-ticker.svg": (5000, 50000),  # 5-50KB
        PROJECT_ROOT / "assets" / "repo-ticker-light.svg": (5000, 50000),
    }

    for svg_file, (min_size, max_size) in svg_files.items():
        if not svg_file.exists():
            continue  # 跳过不存在的文件

        file_size = svg_file.stat().st_size

        if file_size < min_size:
            failures.append(
                f"❌ {svg_file.name} 文件过小: {file_size} bytes "
                f"（应 >= {min_size} bytes）"
            )

        if file_size > max_size:
            failures.append(
                f"❌ {svg_file.name} 文件过大: {file_size} bytes "
                f"（应 <= {max_size} bytes）"
            )

    return failures


def run_all_tests():
    """运行所有测试并报告结果。Run all tests and report results."""
    print("=" * 80)
    print("SVG 生成测试 | SVG Generation Tests")
    print("=" * 80)
    print()

    all_failures = []
    total_tests = 0

    # 定义所有测试
    tests = [
        ("生成 Logo SVG", test_generate_logo_svgs),
        ("加载 Ticker 数据", test_load_ticker_data),
        ("生成 Ticker SVG", test_generate_ticker_svg),
        ("SVG 中文编码", test_svg_chinese_encoding),
        ("SVG 文件大小", test_svg_file_sizes),
    ]

    # 运行所有测试
    for test_name, test_func in tests:
        total_tests += 1
        print(f"🧪 测试: {test_name}")
        failures = test_func()

        if failures:
            all_failures.extend(failures)
            print(f"   ❌ 失败 ({len(failures)} 个问题)")
            for failure in failures:
                print(f"      {failure}")
        else:
            print(f"   ✅ 通过")
        print()

    # 最终结果
    print("=" * 80)
    if all_failures:
        print(
            f"❌ 验证失败 - {len(all_failures)} 个问题，"
            f"共 {total_tests} 个测试"
        )
        print()
        print("失败详情:")
        for failure in all_failures:
            print(f"  {failure}")
        return 1
    else:
        print(f"✅ 验证通过 - 所有 {total_tests} 个测试成功")
        print(f"SVG 生成功能正常工作")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
