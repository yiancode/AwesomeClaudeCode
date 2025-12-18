"""
本地化功能测试
Localization Tests

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


def test_csv_chinese_fields():
    """测试 CSV 包含中文字段。Test CSV contains Chinese fields."""
    failures = []

    csv_file = PROJECT_ROOT / "THE_RESOURCES_TABLE.csv"

    if not csv_file.exists():
        failures.append("❌ THE_RESOURCES_TABLE.csv 文件不存在")
        return failures

    try:
        # 读取 CSV 第一行（标题）
        with open(csv_file, "r", encoding="utf-8") as f:
            header = f.readline()

        # 验证包含中文字段
        required_zh_fields = ["DisplayName_ZH", "Description_ZH", "Tags_ZH"]
        for field in required_zh_fields:
            if field not in header:
                failures.append(f"❌ CSV 标题缺少中文字段: {field}")

    except Exception as e:
        failures.append(f"❌ 读取 CSV 标题失败: {e}")

    return failures


def test_readme_bilingual_content():
    """测试 README 双语内容。Test README bilingual content."""
    failures = []

    readme_file = PROJECT_ROOT / "README.md"

    if not readme_file.exists():
        failures.append("❌ README.md 文件不存在")
        return failures

    try:
        content = readme_file.read_text(encoding="utf-8")

        # 验证中文内容存在
        chinese_patterns = [
            "官方",
            "资源",
            "文档",
            "教程",
        ]
        for pattern in chinese_patterns:
            if pattern not in content:
                failures.append(f"❌ README 缺少中文关键词: '{pattern}'")

        # 验证英文内容存在
        english_patterns = [
            "Official",
            "Resources",
            "Documentation",
        ]
        for pattern in english_patterns:
            if pattern not in content:
                failures.append(f"❌ README 缺少英文关键词: '{pattern}'")

    except Exception as e:
        failures.append(f"❌ 读取 README 失败: {e}")

    return failures


def test_categories_bilingual():
    """测试分类定义双语。Test categories bilingual definitions."""
    failures = []

    categories_file = PROJECT_ROOT / "templates" / "categories.yaml"

    if not categories_file.exists():
        failures.append("❌ categories.yaml 文件不存在")
        return failures

    try:
        content = categories_file.read_text(encoding="utf-8")

        # 验证包含 name_zh 字段
        if "name_zh:" not in content:
            failures.append("❌ categories.yaml 缺少 name_zh 字段")

        # 验证包含 description_zh 字段
        if "description_zh:" not in content:
            failures.append("❌ categories.yaml 缺少 description_zh 字段")

        # 验证包含中文分类名称
        chinese_categories = [
            "官方资源",
            "代理技能",
            "工作流",
        ]
        for category in chinese_categories:
            if category not in content:
                failures.append(f"❌ categories.yaml 缺少中文分类: '{category}'")

    except Exception as e:
        failures.append(f"❌ 读取 categories.yaml 失败: {e}")

    return failures


def test_scripts_chinese_output():
    """测试脚本输出中文消息。Test scripts output Chinese messages."""
    failures = []

    # 测试 generate_readme.py 的输出
    script_file = PROJECT_ROOT / "scripts" / "generate_readme.py"

    if not script_file.exists():
        failures.append("❌ generate_readme.py 文件不存在")
        return failures

    try:
        content = script_file.read_text(encoding="utf-8")

        # 验证包含中文输出消息
        chinese_messages = [
            "加载",
            "生成",
            "成功",
            "失败",
        ]
        for message in chinese_messages:
            if message not in content:
                failures.append(f"❌ generate_readme.py 缺少中文消息: '{message}'")

    except Exception as e:
        failures.append(f"❌ 读取 generate_readme.py 失败: {e}")

    return failures


def test_svg_chinese_text():
    """测试 SVG 包含中文文本。Test SVG contains Chinese text."""
    failures = []

    # 测试 logo SVG
    logo_files = [
        PROJECT_ROOT / "assets" / "logo-light.svg",
        PROJECT_ROOT / "assets" / "logo-dark.svg",
    ]

    for logo_file in logo_files:
        if not logo_file.exists():
            continue  # 跳过不存在的文件

        try:
            content = logo_file.read_text(encoding="utf-8")

            # 验证包含中文文本
            if "资源" not in content:
                failures.append(f"❌ {logo_file.name} 缺少中文文本 '资源'")

            if "Claude Code" not in content:
                failures.append(f"❌ {logo_file.name} 缺少 'Claude Code' 文本")

        except Exception as e:
            failures.append(f"❌ 读取 {logo_file.name} 失败: {e}")

    return failures


def test_utf8_encoding_consistency():
    """测试所有文件 UTF-8 编码一致性。Test UTF-8 encoding consistency."""
    failures = []

    # 测试关键文件的 UTF-8 编码
    files_to_test = [
        PROJECT_ROOT / "THE_RESOURCES_TABLE.csv",
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "templates" / "categories.yaml",
        PROJECT_ROOT / "templates" / "README.template.md",
    ]

    for file_path in files_to_test:
        if not file_path.exists():
            continue  # 跳过不存在的文件

        try:
            # 尝试以 UTF-8 读取
            content = file_path.read_text(encoding="utf-8")

            # 验证包含中文字符
            has_chinese = any("\u4e00" <= char <= "\u9fff" for char in content)

            if not has_chinese:
                failures.append(f"⚠️  {file_path.name} 未检测到中文字符（可能正常）")

        except UnicodeDecodeError:
            failures.append(f"❌ {file_path.name} UTF-8 编码错误")
        except Exception as e:
            failures.append(f"❌ 读取 {file_path.name} 失败: {e}")

    return failures


def test_chinese_priority_in_display():
    """测试显示时中文优先。Test Chinese priority in display."""
    failures = []

    # 读取 generate_readme.py 脚本
    script_file = PROJECT_ROOT / "scripts" / "generate_readme.py"

    if not script_file.exists():
        failures.append("❌ generate_readme.py 文件不存在")
        return failures

    try:
        content = script_file.read_text(encoding="utf-8")

        # 验证中文字段优先逻辑存在
        # 查找类似 "DisplayName_ZH" or "DisplayName" 的模式
        if "DisplayName_ZH" not in content:
            failures.append("❌ generate_readme.py 未使用 DisplayName_ZH 字段")

        if "Description_ZH" not in content:
            failures.append("❌ generate_readme.py 未使用 Description_ZH 字段")

        # 验证优先逻辑（应该有 or 逻辑）
        if "or" not in content or ".get(" not in content:
            failures.append("⚠️  generate_readme.py 可能缺少字段优先选择逻辑")

    except Exception as e:
        failures.append(f"❌ 读取 generate_readme.py 失败: {e}")

    return failures


def run_all_tests():
    """运行所有测试并报告结果。Run all tests and report results."""
    print("=" * 80)
    print("本地化测试 | Localization Tests")
    print("=" * 80)
    print()

    all_failures = []
    total_tests = 0

    # 定义所有测试
    tests = [
        ("CSV 中文字段", test_csv_chinese_fields),
        ("README 双语内容", test_readme_bilingual_content),
        ("分类定义双语", test_categories_bilingual),
        ("脚本中文输出", test_scripts_chinese_output),
        ("SVG 中文文本", test_svg_chinese_text),
        ("UTF-8 编码一致性", test_utf8_encoding_consistency),
        ("中文显示优先", test_chinese_priority_in_display),
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
            print("   ✅ 通过")
        print()

    # 最终结果
    print("=" * 80)
    if all_failures:
        print(f"❌ 验证失败 - {len(all_failures)} 个问题，共 {total_tests} 个测试")
        print()
        print("失败详情:")
        for failure in all_failures:
            print(f"  {failure}")
        return 1
    else:
        print(f"✅ 验证通过 - 所有 {total_tests} 个测试成功")
        print("本地化功能正常工作")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
