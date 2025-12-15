# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AwesomeClaudeCode 是一个采用 **单一数据源（SSOT）** 架构的 Claude Code 资源汇聚项目。所有资源数据存储在 `THE_RESOURCES_TABLE.csv` 中，通过 Python 脚本自动生成 README.md。内容以简体中文为主，英文为辅。

## Architecture

```
数据变更 → CSV 更新 → 脚本处理 → README 生成
```

**核心文件**:
- `THE_RESOURCES_TABLE.csv` - 资源数据的唯一数据源（SSOT）
- `templates/categories.yaml` - 分类定义的唯一数据源
- `templates/resource-overrides.yaml` - 资源手动覆盖配置
- `README.md` - 自动生成，**不要手动编辑**

**关键规则**: README.md 由脚本生成，任何内容变更必须通过修改 CSV 或模板文件实现。

## Common Commands

```bash
# 设置开发环境
make dev-setup

# 生成 README.md（从 CSV 数据）
make generate

# 验证 CSV 数据完整性
make validate

# 运行所有测试
make test

# 自动填充 GitHub 元数据
make auto-fill

# 快速生成并验证
make quick

# 查看所有可用命令
make help
```

## Adding/Updating Resources

1. 编辑 `THE_RESOURCES_TABLE.csv` 添加或修改资源
2. 确保填写所有必填字段（ID, DisplayName, DisplayName_ZH, Category, PrimaryLink, Author, AuthorProfile, Description, Description_ZH）
3. 运行 `make validate` 验证数据
4. 运行 `make generate` 重新生成 README.md
5. 提交 CSV 和 README.md 的变更

## CSV Field Reference

| 字段 | 必填 | 说明 |
|-----|------|-----|
| ID | ✅ | 格式: `{prefix}-{hash}`，前缀见 categories.yaml |
| DisplayName | ✅ | 英文显示名 |
| DisplayName_ZH | ✅ | 中文显示名 |
| Category | ✅ | 主分类，必须匹配 categories.yaml 中的 id |
| SubCategory | ❌ | 子分类 |
| PrimaryLink | ✅ | 主链接 |
| Author | ✅ | 作者名称 |
| AuthorProfile | ✅ | 作者主页 |
| Description | ✅ | 英文描述 |
| Description_ZH | ✅ | 中文描述 |
| License | 推荐 | 许可证（GitHub 仓库可自动获取）|
| IsActive | ✅ | TRUE/FALSE |

## Adding New Categories

编辑 `templates/categories.yaml`，遵循现有格式：

```yaml
- id: new-category
  name: "Category Name"
  name_zh: "分类名称"
  prefix: "new"
  icon: "🆕"
  order: 99
```

## Scripts Directory

- `generate_readme.py` - 核心脚本，生成 README.md
- `validate_csv.py` - CSV 数据验证
- `auto_fill_github_metadata.py` - 自动获取 GitHub 元数据
- `validate_links.py` - 链接有效性验证

## Testing

```bash
# 运行所有测试
make test

# 使用 pytest 详细输出
make test-pytest

# 生成测试覆盖率报告
make test-coverage
```

测试文件位于 `tests/` 目录，使用 pytest 框架。
