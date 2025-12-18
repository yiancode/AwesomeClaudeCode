#!/usr/bin/env python3
"""
CSV 数据验证脚本 / CSV Data Validation Script

验证 THE_RESOURCES_TABLE.csv 的数据完整性
Validate data integrity of THE_RESOURCES_TABLE.csv
"""

import csv
from collections import Counter
from pathlib import Path
from typing import List, Dict


def load_csv(csv_file: Path) -> List[Dict]:
    """加载 CSV 文件 / Load CSV file"""
    resources = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        resources = list(reader)
    return resources


def validate_required_fields(resources: List[Dict]) -> List[str]:
    """
    验证必填字段 / Validate required fields
    Returns list of validation errors
    """
    errors = []
    required_fields = [
        'ID', 'DisplayName', 'DisplayName_ZH', 'Category',
        'PrimaryLink', 'IsActive', 'IsPinned'
    ]

    for idx, resource in enumerate(resources, start=2):  # CSV row starts at 2 (1 is header)
        for field in required_fields:
            if not resource.get(field, '').strip():
                errors.append(f"行 {idx}: 缺少必填字段 '{field}' / Row {idx}: Missing required field '{field}'")

    return errors


def validate_id_format(resources: List[Dict]) -> List[str]:
    """
    验证 ID 格式 / Validate ID format
    ID should be: prefix-hash8
    """
    errors = []
    id_pattern = r'^[a-z]+-[a-f0-9]{8}$'

    import re
    for idx, resource in enumerate(resources, start=2):
        resource_id = resource.get('ID', '')
        if not resource_id:
            continue

        # 检查格式 / Check format
        if not re.match(id_pattern, resource_id):
            errors.append(
                f"行 {idx}: ID 格式错误 '{resource_id}' (期望格式: prefix-hash8) / "
                f"Row {idx}: Invalid ID format '{resource_id}' (expected: prefix-hash8)"
            )

    return errors


def check_duplicate_ids(resources: List[Dict]) -> List[str]:
    """
    检查重复 ID / Check duplicate IDs
    """
    errors = []
    id_counter = Counter(r.get('ID', '') for r in resources if r.get('ID'))

    for resource_id, count in id_counter.items():
        if count > 1:
            errors.append(
                f"发现重复 ID '{resource_id}' (出现 {count} 次) / "
                f"Duplicate ID found '{resource_id}' (appears {count} times)"
            )

    return errors


def validate_urls(resources: List[Dict]) -> List[str]:
    """
    验证 URL 格式 / Validate URL format
    """
    errors = []
    import re
    url_pattern = r'^https?://'

    for idx, resource in enumerate(resources, start=2):
        primary_link = resource.get('PrimaryLink', '').strip()
        if primary_link and not re.match(url_pattern, primary_link):
            errors.append(
                f"行 {idx}: 主链接格式错误 '{primary_link}' / "
                f"Row {idx}: Invalid primary link '{primary_link}'"
            )

        secondary_link = resource.get('SecondaryLink', '').strip()
        if secondary_link and not re.match(url_pattern, secondary_link):
            errors.append(
                f"行 {idx}: 次要链接格式错误 '{secondary_link}' / "
                f"Row {idx}: Invalid secondary link '{secondary_link}'"
            )

    return errors


def generate_statistics(resources: List[Dict]) -> Dict:
    """
    生成统计信息 / Generate statistics
    """
    stats = {
        'total': len(resources),
        'official': sum(1 for r in resources if r.get('IsPinned') == 'TRUE'),
        'community': sum(1 for r in resources if r.get('IsPinned') != 'TRUE'),
        'categories': Counter(r.get('Category', '') for r in resources),
        'missing_author': sum(1 for r in resources if not r.get('Author', '').strip()),
        'missing_license': sum(1 for r in resources if not r.get('License', '').strip()),
        'missing_description_zh': sum(1 for r in resources if not r.get('Description_ZH', '').strip()),
    }

    return stats


def print_validation_report(errors: List[str], stats: Dict):
    """
    打印验证报告 / Print validation report
    """
    print("\n" + "="*70)
    print("📋 CSV 数据验证报告 / CSV Data Validation Report")
    print("="*70)

    # 统计信息 / Statistics
    print(f"\n📊 统计信息 / Statistics:")
    print(f"  总资源数 / Total Resources: {stats['total']}")
    print(f"  官方资源 / Official Resources: {stats['official']}")
    print(f"  社区资源 / Community Resources: {stats['community']}")

    print(f"\n📂 分类统计 / Category Statistics:")
    for category, count in sorted(stats['categories'].items()):
        print(f"  - {category}: {count}")

    print(f"\n⚠️  需要补充的字段 / Fields Requiring Completion:")
    print(f"  - 缺少 Author / Missing Author: {stats['missing_author']}")
    print(f"  - 缺少 License / Missing License: {stats['missing_license']}")
    print(f"  - 缺少 Description_ZH / Missing Description_ZH: {stats['missing_description_zh']}")

    # 错误信息 / Errors
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误 / Found {len(errors)} errors:")
        for error in errors[:20]:  # 只显示前20个 / Show first 20 only
            print(f"  • {error}")
        if len(errors) > 20:
            print(f"  ... 还有 {len(errors) - 20} 个错误 / ... and {len(errors) - 20} more errors")
    else:
        print(f"\n✅ 所有验证通过！/ All validations passed!")

    print("\n" + "="*70)


def main():
    """主函数 / Main function"""
    project_root = Path(__file__).parent.parent
    csv_file = project_root / 'THE_RESOURCES_TABLE.csv'

    print(f"🔍 验证 CSV 文件: {csv_file}")
    print(f"🔍 Validating CSV file: {csv_file}\n")

    if not csv_file.exists():
        print("❌ 错误：文件不存在 / Error: File not found")
        return

    # 加载数据 / Load data
    resources = load_csv(csv_file)
    print(f"✅ 加载了 {len(resources)} 条资源")

    # 运行验证 / Run validations
    all_errors = []

    print("\n验证必填字段 / Validating required fields...")
    all_errors.extend(validate_required_fields(resources))

    print("验证 ID 格式 / Validating ID format...")
    all_errors.extend(validate_id_format(resources))

    print("检查重复 ID / Checking duplicate IDs...")
    all_errors.extend(check_duplicate_ids(resources))

    print("验证 URL 格式 / Validating URL format...")
    all_errors.extend(validate_urls(resources))

    # 生成统计 / Generate statistics
    print("生成统计信息 / Generating statistics...")
    stats = generate_statistics(resources)

    # 打印报告 / Print report
    print_validation_report(all_errors, stats)

    # 返回状态码 / Return status code
    return 0 if not all_errors else 1


if __name__ == '__main__':
    exit(main())
