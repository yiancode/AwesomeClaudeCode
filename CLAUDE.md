# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AwesomeClaudeCode 是一个采用 **单一数据源（SSOT）** 架构的 Claude Code 资源汇聚项目。所有资源数据存储在 `THE_RESOURCES_TABLE.csv` 中，通过 Python 脚本自动生成 README.md。内容以简体中文为主，英文为辅。

## Architecture

### Data Flow

```
数据变更 → CSV 更新 → 脚本处理 → README 生成
```

### Core Components

**数据层 (Data Layer)**:
- `THE_RESOURCES_TABLE.csv` - 资源数据的唯一数据源（SSOT）。包含所有资源的元数据
- `templates/categories.yaml` - 分类定义的唯一数据源。定义13个主分类及其子分类
- `templates/resource-overrides.yaml` - 资源手动覆盖配置。用于特殊情况的数据覆盖

**生成层 (Generation Layer)**:
- `scripts/generate_readme.py` - 核心生成脚本，从 CSV 生成 README.md
- `scripts/generate_logo_svgs.py` - 生成 SVG 图标和动画
- `scripts/generate_ticker_svg.py` - 生成滚动条 SVG

**验证层 (Validation Layer)**:
- `scripts/validate_csv.py` - CSV 数据完整性验证
- `scripts/validate_links.py` - 链接有效性检查
- `tests/` - 单元测试和集成测试

**输出层 (Output Layer)**:
- `README.md` - 自动生成的项目主页，**不要手动编辑**
- `assets/` - 生成的 SVG 图标和动画文件

### Critical Rules

1. **README.md 是只读的**: 所有内容变更必须通过修改 CSV 或模板文件实现
2. **CSV 是数据源**: 直接修改 CSV 文件添加、更新或删除资源
3. **categories.yaml 定义结构**: 添加新分类时必须更新此文件
4. **先验证后生成**: 修改后先运行 `make validate` 再运行 `make generate`

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

## Working with Resources

### Adding a New Resource

1. **打开 CSV 文件**: 编辑 `THE_RESOURCES_TABLE.csv`
2. **生成唯一 ID**: 使用格式 `{category_prefix}-{hash8}`
   - 从 `templates/categories.yaml` 找到分类的 prefix
   - 生成 8 位哈希值（基于资源 URL 或名称）
3. **填写所有必填字段**（见下方 CSV 字段参考）
4. **设置状态**: `IsActive=TRUE`, `IsPinned=FALSE` (除非是特别重要的资源)
5. **运行验证**: `make validate`
6. **生成 README**: `make generate`
7. **提交变更**: 提交 CSV 和生成的 README.md

### Updating an Existing Resource

1. 在 `THE_RESOURCES_TABLE.csv` 中找到对应的行
2. 修改需要更新的字段
3. 如果需要覆盖某些验证规则，编辑 `templates/resource-overrides.yaml`
4. 运行 `make validate && make generate`
5. 提交变更

### Deactivating a Resource

不要删除资源行，而是设置 `IsActive=FALSE`。这样保留历史记录。

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
- id: new-category          # 唯一标识符，kebab-case
  name: "Category Name"     # 英文名称
  name_zh: "分类名称"        # 中文名称
  prefix: "new"             # ID 前缀（2-5个字母）
  icon: "🆕"                # emoji 图标
  description: |            # 英文描述
    Description in English
  description_zh: |         # 中文描述
    中文描述
  order: 99                 # 排序顺序（数字越小越靠前）
  subcategories:            # 子分类（可选）
    - id: general
      name: "General"
      name_zh: "通用"
```

**重要提示**:
- `order: 0` 保留给官方资源（置顶分类）
- 确保 `prefix` 在所有分类中唯一
- 添加分类后需要运行 `make generate` 更新 README

## Scripts Overview

### Generation Scripts
- `generate_readme.py` - 核心脚本，从 CSV 和模板生成 README.md
  - 读取 CSV 数据和分类定义
  - 应用资源覆盖配置
  - 生成双语 README（中英文）
  - 创建统计信息和导航目录
- `generate_logo_svgs.py` - 生成 SVG 图标和动画
- `generate_ticker_svg.py` - 生成滚动条效果的 SVG

### Validation Scripts
- `validate_csv.py` - CSV 数据验证
  - 检查必填字段
  - 验证 ID 格式（`{prefix}-{hash8}`）
  - 检测重复 ID
  - 验证 URL 格式
  - 检查 Category 是否在 categories.yaml 中定义
- `validate_links.py` - 链接有效性验证（HTTP 请求测试）

### Utility Scripts
- `auto_fill_github_metadata.py` - 自动从 GitHub API 获取仓库元数据（stars, license, description）
- `migrate_existing_resources.py` - 从旧格式迁移资源到 CSV（历史用途）
- `fix_data_integrity.py` - 修复数据完整性问题
- `clean_csv_format.py` - 清理和格式化 CSV 文件

### Development Workflow

**日常开发流程**:
```bash
# 1. 修改 CSV 或 categories.yaml
vim THE_RESOURCES_TABLE.csv

# 2. 验证数据
make validate

# 3. 生成 README
make generate

# 4. 运行测试（可选但推荐）
make test

# 5. 提交变更
git add THE_RESOURCES_TABLE.csv README.md
git commit -m "feat: add new resource XXX"
```

**快速开发**:
```bash
make quick  # 等同于 make generate && make validate
```

## Testing

本项目使用 Python unittest 和 pytest 进行测试。

### Test Structure

```
tests/
├── test_csv_validation.py    # CSV 数据验证测试
├── test_generate_readme.py   # README 生成测试
├── test_localization.py       # 双语功能测试
└── test_svg_generation.py     # SVG 生成测试
```

### Running Tests

```bash
# 运行所有测试（使用 unittest）
make test

# 使用 pytest 运行（详细输出）
make test-pytest

# 生成测试覆盖率报告
make test-coverage

# 运行所有测试和验证
make test-all
```

### Test Requirements

测试覆盖以下方面：
- CSV 数据格式和完整性
- ID 唯一性和格式正确性
- 必填字段验证
- README 生成的正确性
- 双语内容的完整性
- SVG 文件生成

**重要**: 在提交 PR 前，确保所有测试通过。

## Important Design Decisions

### Single Source of Truth (SSOT)

项目采用 SSOT 架构的原因：
1. **避免数据不一致**: CSV 是唯一的数据源，README 是自动生成的输出
2. **易于维护**: 只需维护一个 CSV 文件，不需要在多处同步更新
3. **可验证性**: 数据验证脚本确保数据质量
4. **可追溯性**: Git 历史记录所有数据变更

### ID Generation Strategy

资源 ID 格式为 `{prefix}-{hash8}`：
- `prefix`: 来自分类定义的前缀（如 `off`, `wf`, `tool`）
- `hash8`: 8位十六进制哈希值
- 这种格式既可读又唯一，便于识别资源所属分类

### Bilingual Support

所有用户可见的内容都提供中英文版本：
- 字段命名: `DisplayName` (英文), `DisplayName_ZH` (中文)
- README 生成时同时包含两种语言
- categories.yaml 定义中包含 `name` 和 `name_zh`

## Troubleshooting

### 常见问题

**问题**: `make generate` 报错 "ModuleNotFoundError: No module named 'yaml'"
**解决**: 运行 `make install` 或 `make dev-setup` 安装依赖

**问题**: CSV 验证失败，提示重复 ID
**解决**: 检查 `THE_RESOURCES_TABLE.csv` 中是否有重复的 ID，修改为唯一值

**问题**: 生成的 README 中某个资源没有显示
**解决**: 检查该资源的 `IsActive` 字段是否为 `TRUE`

**问题**: 新增的分类在 README 中没有出现
**解决**: 确保在 `templates/categories.yaml` 中正确定义了分类，然后运行 `make generate`

### Debug Mode

在脚本中添加 debug 输出：
```python
# 在 generate_readme.py 或其他脚本中
print(f"Debug: 处理资源 {resource['ID']}")
```

然后运行脚本查看详细输出。

## Python Environment

**要求**: Python 3.9+

**依赖管理**: 使用 venv 虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

**核心依赖**:
- `pyyaml` - YAML 文件解析
- `pytest` (可选) - 测试框架
- `pytest-cov` (可选) - 测试覆盖率

## GitHub Actions

项目使用 GitHub Actions 进行自动化：
- 自动验证 PR 中的 CSV 数据
- 自动运行测试
- 自动生成并更新 README（在 main 分支）

查看 `.github/workflows/` 目录了解工作流配置。
