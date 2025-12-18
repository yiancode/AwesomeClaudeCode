"""
CSV 数据完整性验证测试
CSV Data Integrity Validation Tests

根据 CLAUDE.md 要求:
- 使用真实数据，不使用 Mock
- 跟踪所有验证失败
- 有意义的断言验证具体预期值
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict, Set

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# CSV 文件路径
CSV_FILE = PROJECT_ROOT / "THE_RESOURCES_TABLE.csv"

# 必填字段定义
REQUIRED_FIELDS = [
    "ID",
    "DisplayName",
    "DisplayName_ZH",
    "Category",
    "PrimaryLink",
    "IsActive",
    "Description",
    "Description_ZH",
    "IsPinned",
]

# 所有字段定义（19个字段）
ALL_FIELDS = [
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


def load_csv_data() -> tuple[List[str], List[Dict[str, str]]]:
    """加载 CSV 数据。Load CSV data."""
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return fieldnames, rows


def test_csv_file_exists():
    """测试 CSV 文件存在。Test CSV file exists."""
    failures = []

    if not CSV_FILE.exists():
        failures.append(f"❌ CSV 文件不存在: {CSV_FILE}")

    return failures


def test_csv_structure():
    """测试 CSV 文件结构完整性。Test CSV file structure integrity."""
    failures = []

    fieldnames, _ = load_csv_data()

    # 验证所有字段都存在
    for field in ALL_FIELDS:
        if field not in fieldnames:
            failures.append(f"❌ 缺少必需字段: {field}")

    # 验证没有额外字段
    extra_fields = set(fieldnames) - set(ALL_FIELDS)
    if extra_fields:
        failures.append(f"❌ 发现额外字段: {extra_fields}")

    # 验证字段顺序正确（前19个字段）
    expected_order = ALL_FIELDS[: len(fieldnames)]
    if list(fieldnames) != expected_order:
        failures.append("❌ 字段顺序不正确")
        failures.append(f"   期望: {expected_order}")
        failures.append(f"   实际: {list(fieldnames)}")

    return failures


def test_required_fields_present():
    """测试所有资源包含必填字段。Test all resources have required fields."""
    failures = []

    _, rows = load_csv_data()

    for i, row in enumerate(rows, start=2):  # 从第2行开始（第1行是标题）
        for field in REQUIRED_FIELDS:
            if not row.get(field) or row[field].strip() == "":
                resource_id = row.get("ID", "unknown")
                failures.append(f"❌ 第 {i} 行资源 {resource_id}: 缺少必填字段 '{field}'")

    return failures


def test_unique_ids():
    """测试 ID 唯一性。Test ID uniqueness."""
    failures = []

    _, rows = load_csv_data()

    id_counts: Dict[str, int] = {}
    for row in rows:
        resource_id = row.get("ID", "")
        id_counts[resource_id] = id_counts.get(resource_id, 0) + 1

    duplicates = {id_: count for id_, count in id_counts.items() if count > 1}

    if duplicates:
        failures.append(f"❌ 发现 {len(duplicates)} 个重复 ID:")
        for id_, count in duplicates.items():
            failures.append(f"   - {id_}: 出现 {count} 次")

    return failures


def test_id_format():
    """测试 ID 格式正确（prefix-hash8）。Test ID format correctness."""
    failures = []

    _, rows = load_csv_data()

    for i, row in enumerate(rows, start=2):
        resource_id = row.get("ID", "")

        # ID 应该是 prefix-hash8 格式
        parts = resource_id.split("-")

        if len(parts) != 2:
            failures.append(f"❌ 第 {i} 行: ID '{resource_id}' 格式不正确（应为 prefix-hash8）")
            continue

        prefix, hash_part = parts

        # Hash 部分应该是 8 个字符
        if len(hash_part) != 8:
            failures.append(f"❌ 第 {i} 行: ID '{resource_id}' hash 部分长度不是 8 字符")

        # Hash 应该是十六进制
        try:
            int(hash_part, 16)
        except ValueError:
            failures.append(f"❌ 第 {i} 行: ID '{resource_id}' hash 部分不是有效的十六进制")

    return failures


def test_chinese_encoding():
    """测试中文字符编码正确性。Test Chinese character encoding correctness."""
    failures = []

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 验证包含中文字符
    chinese_keywords = ["官方", "资源", "教程", "工具", "集成"]
    found_chinese = any(keyword in content for keyword in chinese_keywords)

    if not found_chinese:
        failures.append(f"❌ CSV 文件中未找到中文内容（期望包含: {chinese_keywords}）")

    # 验证 UTF-8 编码正确（通过成功读取验证）
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            f.read()
    except UnicodeDecodeError as e:
        failures.append(f"❌ UTF-8 编码错误: {e}")

    return failures


def test_boolean_fields():
    """测试布尔字段值正确。Test boolean field values."""
    failures = []

    _, rows = load_csv_data()

    boolean_fields = ["IsActive", "IsPinned"]
    valid_values = {"TRUE", "FALSE", ""}

    for i, row in enumerate(rows, start=2):
        for field in boolean_fields:
            value = row.get(field, "")
            if value not in valid_values:
                resource_id = row.get("ID", "unknown")
                failures.append(
                    f"❌ 第 {i} 行资源 {resource_id}: 字段 '{field}' 值 '{value}' 无效（应为 TRUE/FALSE/空）"
                )

    return failures


def test_url_format():
    """测试 URL 格式基本正确。Test URL format basic correctness."""
    failures = []

    _, rows = load_csv_data()

    for i, row in enumerate(rows, start=2):
        resource_id = row.get("ID", "unknown")
        primary_link = row.get("PrimaryLink", "")

        # PrimaryLink 是必填的
        if not primary_link:
            failures.append(f"❌ 第 {i} 行资源 {resource_id}: PrimaryLink 为空")
            continue

        # 基本 URL 格式检查（应该以 http:// 或 https:// 开头）
        if not (primary_link.startswith("http://") or primary_link.startswith("https://")):
            # 允许本地文档链接（docs/开头）
            if not primary_link.startswith("docs/"):
                failures.append(
                    f"❌ 第 {i} 行资源 {resource_id}: PrimaryLink '{primary_link}' "
                    "格式不正确（应以 http:// 或 https:// 开头）"
                )

    return failures


def test_category_values():
    """测试分类值有效。Test category values are valid."""
    failures = []

    # 从 categories.yaml 加载有效分类（简化版 - 直接硬编码已知分类）
    valid_categories = {
        "official-resources",
        "skills",
        "workflows",
        "tooling",
        "statusline",
        "hooks",
        "slash-commands",
        "claude-md-files",
        "alternative-clients",
        "mcp-servers",
        "open-source-projects",
        "case-studies",
        "ecosystem",
    }

    _, rows = load_csv_data()

    for i, row in enumerate(rows, start=2):
        resource_id = row.get("ID", "unknown")
        category = row.get("Category", "")

        if category and category not in valid_categories:
            failures.append(f"❌ 第 {i} 行资源 {resource_id}: 分类 '{category}' 无效")

    return failures


def run_all_tests():
    """运行所有测试并报告结果。Run all tests and report results."""
    print("=" * 80)
    print("CSV 数据验证测试 | CSV Data Validation Tests")
    print("=" * 80)
    print()

    all_failures = []
    total_tests = 0

    # 定义所有测试
    tests = [
        ("CSV 文件存在性", test_csv_file_exists),
        ("CSV 结构完整性", test_csv_structure),
        ("必填字段完整性", test_required_fields_present),
        ("ID 唯一性", test_unique_ids),
        ("ID 格式正确性", test_id_format),
        ("中文编码正确性", test_chinese_encoding),
        ("布尔字段值正确性", test_boolean_fields),
        ("URL 格式正确性", test_url_format),
        ("分类值有效性", test_category_values),
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
        print(
            f"❌ 验证失败 - {len(all_failures)} 个问题，"
            f"{len([f for f in all_failures if f.startswith('❌')])} 个测试失败，"
            f"共 {total_tests} 个测试"
        )
        print()
        print("失败详情:")
        for failure in all_failures:
            print(f"  {failure}")
        return 1
    else:
        print(f"✅ 验证通过 - 所有 {total_tests} 个测试成功")
        print("CSV 文件数据完整且格式正确")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
