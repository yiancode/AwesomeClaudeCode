#!/usr/bin/env python3
"""
清理 CSV 中的格式标记 / Clean format markers in CSV
"""

import csv
import re
from pathlib import Path


def clean_description(text: str) -> str:
    """清理描述中的格式标记 / Clean format markers in description"""
    if not text:
        return text

    # 移除开头的 "** - " / Remove leading "** - "
    text = re.sub(r"^\*\* - ", "", text.strip())

    # 移除其他常见格式标记 / Remove other common format markers
    text = re.sub(r"^\*\*([^*]+)\*\*", r"\1", text)  # **text** -> text

    return text.strip()


def clean_csv(csv_path: Path) -> tuple[int, int]:
    """清理 CSV 文件中的格式标记 / Clean format markers in CSV file"""
    resources = []
    cleaned_count = 0
    total_changes = 0

    # 读取 CSV / Read CSV
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            changed = False

            # 清理 Description 字段 / Clean Description field
            if row.get("Description"):
                original = row["Description"]
                cleaned = clean_description(original)
                if cleaned != original:
                    row["Description"] = cleaned
                    changed = True
                    total_changes += 1
                    print(f"  清理 Description: {row['ID']}")
                    print(f"    原始: {original[:60]}...")
                    print(f"    清理: {cleaned[:60]}...")

            # 清理 Description_ZH 字段 / Clean Description_ZH field
            if row.get("Description_ZH"):
                original = row["Description_ZH"]
                cleaned = clean_description(original)
                if cleaned != original:
                    row["Description_ZH"] = cleaned
                    changed = True
                    total_changes += 1
                    print(f"  清理 Description_ZH: {row['ID']}")
                    print(f"    原始: {original[:60]}...")
                    print(f"    清理: {cleaned[:60]}...")

            if changed:
                cleaned_count += 1

            resources.append(row)

    # 写回 CSV / Write back to CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resources)

    return cleaned_count, total_changes


def main():
    """主函数 / Main function"""
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "THE_RESOURCES_TABLE.csv"

    if not csv_path.exists():
        print(f"❌ 错误：CSV 文件不存在: {csv_path}")
        return 1

    print("🚀 开始清理 CSV 格式标记...")
    print("🚀 Starting CSV format marker cleanup...\n")

    cleaned_resources, total_changes = clean_csv(csv_path)

    print(f"\n✅ 完成！共清理了 {cleaned_resources} 个资源的 {total_changes} 个字段")
    print(f"✅ Done! Cleaned {total_changes} fields in {cleaned_resources} resources")

    return 0


if __name__ == "__main__":
    exit(main())
