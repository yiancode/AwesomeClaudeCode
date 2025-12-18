"""
README 生成功能测试
README Generation Tests

根据 CLAUDE.md 要求:
- 使用真实数据，不使用 Mock
- 跟踪所有验证失败
- 有意义的断言验证具体预期值
"""

import sys
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入生成脚本
from scripts.generate_readme import (
    load_categories,
    load_csv_resources,
    generate_readme,
)


def test_load_categories():
    """测试加载分类配置。Test loading categories."""
    failures = []

    try:
        categories = load_categories(PROJECT_ROOT / "templates" / "categories.yaml")

        # 验证返回的是列表
        if not isinstance(categories, list):
            failures.append(f"❌ 分类数据类型错误: {type(categories)}，应为 list")
            return failures

        # 验证至少有13个分类
        if len(categories) < 13:
            failures.append(f"❌ 分类数量不足: {len(categories)}，应至少 13 个")

        # 验证每个分类都有必需的字段
        required_category_fields = ["id", "name", "name_zh", "prefix"]
        for i, category in enumerate(categories):
            for field in required_category_fields:
                if field not in category:
                    failures.append(f"❌ 分类 {i}: 缺少必需字段 '{field}'")

        # 验证 official-resources 分类存在且置顶
        official_cat = next((c for c in categories if c.get("id") == "official-resources"), None)
        if not official_cat:
            failures.append("❌ 未找到 'official-resources' 分类")
        elif not official_cat.get("is_pinned"):
            failures.append("❌ 'official-resources' 分类未设置 is_pinned")

    except FileNotFoundError:
        failures.append("❌ categories.yaml 文件不存在")
    except Exception as e:
        failures.append(f"❌ 加载分类失败: {e}")

    return failures


def test_load_csv_resources():
    """测试加载 CSV 资源。Test loading CSV resources."""
    failures = []

    try:
        resources = load_csv_resources(PROJECT_ROOT / "THE_RESOURCES_TABLE.csv", None)

        # 验证返回的是列表
        if not isinstance(resources, list):
            failures.append(f"❌ 资源数据类型错误: {type(resources)}，应为 list")
            return failures

        # 验证资源数量（应该有100+个）
        if len(resources) < 100:
            failures.append(f"❌ 资源数量过少: {len(resources)}，应至少 100 个")

        # 验证第一个资源的基本字段
        if resources:
            first_resource = resources[0]
            required_fields = ["ID", "DisplayName", "PrimaryLink"]
            for field in required_fields:
                if field not in first_resource:
                    failures.append(f"❌ 第一个资源缺少字段 '{field}'")

    except FileNotFoundError:
        failures.append("❌ THE_RESOURCES_TABLE.csv 文件不存在")
    except Exception as e:
        failures.append(f"❌ 加载资源失败: {e}")

    return failures


def test_generate_readme():
    """测试 README 生成功能。Test README generation."""
    failures = []

    try:
        # 使用临时文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp_file:
            temp_readme = Path(tmp_file.name)

        # 生成 README
        generate_readme(
            csv_path=PROJECT_ROOT / "THE_RESOURCES_TABLE.csv",
            template_path=PROJECT_ROOT / "templates" / "README.template.md",
            categories_path=PROJECT_ROOT / "templates" / "categories.yaml",
            output_path=temp_readme,
            overrides_path=None,
        )

        # 读取生成的内容
        content = temp_readme.read_text(encoding="utf-8")

        # 验证基本结构
        if "# " not in content and "Awesome" not in content:
            failures.append("❌ README 缺少主标题")

        # 验证中文内容存在
        chinese_keywords = [
            "Claude Code",
            "资源",
            "官方",
        ]
        for keyword in chinese_keywords:
            if keyword not in content:
                failures.append(f"❌ README 缺少中文关键词: '{keyword}'")

        # 验证英文内容存在
        english_keywords = [
            "Awesome",
            "Resources",
            "Official",
        ]
        for keyword in english_keywords:
            if keyword not in content:
                failures.append(f"❌ README 缺少英文关键词: '{keyword}'")

        # 验证分类标题存在
        if "## " not in content:
            failures.append("❌ README 缺少二级标题（分类）")

        # 验证资源链接存在
        if "](http" not in content:
            failures.append("❌ README 缺少资源链接")

        # 验证文件长度合理（应该有足够的内容）
        if len(content) < 10000:  # 至少10KB内容
            failures.append(f"❌ README 内容过短: {len(content)} 字符，应至少 10000 字符")

        # 清理临时文件
        temp_readme.unlink()

    except FileNotFoundError as e:
        failures.append(f"❌ 文件不存在: {e}")
    except Exception as e:
        failures.append(f"❌ 生成 README 失败: {e}")

    return failures


def test_readme_chinese_encoding():
    """测试 README 中文编码正确。Test README Chinese encoding."""
    failures = []

    # 读取实际的 README.md
    readme_path = PROJECT_ROOT / "README.md"

    if not readme_path.exists():
        failures.append("❌ README.md 文件不存在")
        return failures

    try:
        content = readme_path.read_text(encoding="utf-8")

        # 验证中文字符数量合理（应该有大量中文）
        chinese_char_count = sum(1 for char in content if "\u4e00" <= char <= "\u9fff")

        if chinese_char_count < 1000:  # 至少1000个中文字符
            failures.append(f"❌ README 中文字符过少: {chinese_char_count}，应至少 1000 个")

    except UnicodeDecodeError:
        failures.append("❌ README.md UTF-8 编码错误")
    except Exception as e:
        failures.append(f"❌ 读取 README.md 失败: {e}")

    return failures


def test_readme_structure():
    """测试 README 结构完整。Test README structure completeness."""
    failures = []

    readme_path = PROJECT_ROOT / "README.md"

    if not readme_path.exists():
        failures.append("❌ README.md 文件不存在")
        return failures

    try:
        content = readme_path.read_text(encoding="utf-8")

        # 验证必需的章节存在
        required_sections = [
            "## ",  # 至少有二级标题
            "###",  # 至少有三级标题
            "- [",  # 至少有列表项
        ]

        for section in required_sections:
            if section not in content:
                failures.append(f"❌ README 缺少必需结构: '{section}'")

        # 验证官方资源区块存在
        if "官方" not in content and "Official" not in content:
            failures.append("❌ README 缺少官方资源区块")

    except Exception as e:
        failures.append(f"❌ 验证 README 结构失败: {e}")

    return failures


def run_all_tests():
    """运行所有测试并报告结果。Run all tests and report results."""
    print("=" * 80)
    print("README 生成测试 | README Generation Tests")
    print("=" * 80)
    print()

    all_failures = []
    total_tests = 0

    # 定义所有测试
    tests = [
        ("加载分类配置", test_load_categories),
        ("加载 CSV 资源", test_load_csv_resources),
        ("生成 README", test_generate_readme),
        ("README 中文编码", test_readme_chinese_encoding),
        ("README 结构完整性", test_readme_structure),
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
        print("README 生成功能正常工作")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
