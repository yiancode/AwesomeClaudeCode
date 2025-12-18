#!/usr/bin/env python3
"""
手动更新 GitHub 项目的元数据 / Manually update GitHub project metadata
"""

import csv
from pathlib import Path

# 收集到的元数据 / Collected metadata
GITHUB_METADATA = {
    "proj-8d219c47": {  # lancekrogers/claude-code-go
        "Author": "lancekrogers",
        "AuthorProfile": "https://github.com/lancekrogers",
        "License": "MIT",
    },
    "proj-67e79a1c": {  # davila7/claude-code-templates
        "Author": "davila7",
        "AuthorProfile": "https://github.com/davila7",
        "License": "MIT",
    },
    "proj-68925cf0": {  # answerdotai/claudette
        "Author": "AnswerDotAI",
        "AuthorProfile": "https://github.com/AnswerDotAI",
        "License": "Apache-2.0",
    },
    "proj-4b657b7d": {  # cgize/claude-mcp-think-tool
        "Author": "cgize",
        "AuthorProfile": "https://github.com/cgize",
        "License": "MIT",
    },
}


def update_csv_metadata(csv_path: Path) -> int:
    """更新 CSV 文件中的元数据 / Update metadata in CSV file"""
    resources = []
    updated_count = 0

    # 读取 CSV / Read CSV
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            resource_id = row["ID"]

            # 如果有元数据更新，则更新 / Update if metadata exists
            if resource_id in GITHUB_METADATA:
                metadata = GITHUB_METADATA[resource_id]
                row["Author"] = metadata["Author"]
                row["AuthorProfile"] = metadata["AuthorProfile"]
                row["License"] = metadata["License"]
                updated_count += 1
                print(f"✅ 更新 {resource_id}: {row['DisplayName']} - {metadata['Author']} ({metadata['License']})")

            resources.append(row)

    # 写回 CSV / Write back to CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resources)

    return updated_count


def main():
    """主函数 / Main function"""
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "THE_RESOURCES_TABLE.csv"

    if not csv_path.exists():
        print(f"❌ 错误：CSV 文件不存在: {csv_path}")
        return 1

    print("🚀 开始更新 GitHub 项目元数据...")
    print("🚀 Starting GitHub metadata update...\n")

    updated = update_csv_metadata(csv_path)

    print(f"\n✅ 完成！共更新了 {updated} 个 GitHub 项目的元数据")
    print(f"✅ Done! Updated metadata for {updated} GitHub projects")

    return 0


if __name__ == "__main__":
    exit(main())
