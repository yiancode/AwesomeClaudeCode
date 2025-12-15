# 迁移指南 | Migration Guide

本指南帮助你将现有的 Claude Code 资源列表迁移到 Awesome Claude Code 的自动化系统。

This guide helps you migrate existing Claude Code resource lists to the Awesome Claude Code automated system.

---

## 📋 目录 | Table of Contents

- [为什么需要迁移](#为什么需要迁移--why-migrate)
- [迁移概述](#迁移概述--migration-overview)
- [系统架构变更](#系统架构变更--architecture-changes)
- [迁移前准备](#迁移前准备--preparation)
- [迁移步骤](#迁移步骤--migration-steps)
- [数据映射](#数据映射--data-mapping)
- [常见问题](#常见问题--faq)
- [故障排除](#故障排除--troubleshooting)
- [回滚指南](#回滚指南--rollback)

---

## 为什么需要迁移 | Why Migrate

### 旧系统的问题 | Problems with Old System

❌ **手动维护 README**
- 容易出错，格式不一致
- 难以批量更新
- 协作困难

❌ **缺乏数据验证**
- 链接失效无法自动检测
- 重复资源难以发现
- 数据完整性无保障

❌ **扩展性差**
- 添加新字段困难
- 国际化支持有限
- 统计信息手动计算

### 新系统的优势 | Advantages of New System

✅ **数据驱动架构**
- CSV 作为单一数据源
- 自动生成 README
- 数据与展示分离

✅ **自动化工作流**
- 自动链接验证
- GitHub 元数据自动更新
- CI/CD 集成

✅ **双语支持**
- 中英文内容并重
- 自动双语 README 生成
- 易于扩展其他语言

✅ **质量保证**
- 数据完整性验证
- 自动化测试
- 统一格式标准

---

## 迁移概述 | Migration Overview

### 迁移路径 | Migration Path

```
旧系统 Old System              新系统 New System
┌────────────────────┐         ┌────────────────────┐
│  手动维护的 README  │         │ CSV 数据表         │
│  Manual README      │   ─→    │ CSV Data Table     │
│                     │         │                     │
│  - 混合的格式       │         │  - 结构化数据      │
│  - 英文单语         │         │  - 双语字段        │
│  - 无验证          │         │  - 自动验证        │
└────────────────────┘         └────────────────────┘
                                        │
                                        ↓
                               ┌────────────────────┐
                               │ 自动生成的 README   │
                               │ Auto-generated      │
                               │                     │
                               │  - 统一格式        │
                               │  - 双语支持        │
                               │  - 实时统计        │
                               └────────────────────┘
```

### 迁移阶段 | Migration Stages

本项目已完成 8 个阶段的迁移：

This project has completed 8 stages of migration:

| 阶段 Stage | 任务 Task | 状态 Status |
|-----------|----------|-------------|
| Stage 1 | 环境配置 Environment Setup | ✅ 完成 |
| Stage 2 | 数据结构设计 Data Structure Design | ✅ 完成 |
| Stage 3 | 脚本系统实现 Scripts Implementation | ✅ 完成 |
| Stage 4 | 模板系统创建 Template System | ✅ 完成 |
| Stage 5 | 测试与验证 Testing & Validation | ✅ 完成 |
| Stage 6 | GitHub Actions 集成 CI/CD Integration | ✅ 完成 |
| Stage 7 | 可视化优化 Visual Enhancement | ✅ 完成 |
| Stage 8 | 文档本地化 Documentation i18n | 🔄 进行中 |

---

## 系统架构变更 | Architecture Changes

### 数据存储变更 | Data Storage Changes

#### 旧系统 | Old System

```markdown
# README.md (手动维护)
## 📚 Resources

### Official Documentation
- [Claude Code Docs](https://...)
- [API Reference](https://...)

### Community Resources
- [Tool A](https://...)
- [Tool B](https://...)
```

**问题**:
- 数据和展示混合
- 难以批量处理
- 无结构化元数据

#### 新系统 | New System

**1. 数据层 (CSV)**
```csv
ID,DisplayName,DisplayName_ZH,Category,SubCategory,PrimaryLink,...
off-c260c9d7,Claude Code Docs,Claude Code 官方文档,official-resources,general,https://...
```

**2. 配置层 (YAML)**
```yaml
# templates/categories.yaml
categories:
  - id: official-resources
    name: "Official Resources"
    name_zh: "官方资源"
```

**3. 模板层 (Jinja2)**
```jinja2
# templates/README.template.md
{% for category in categories %}
## {{ category.icon }} {{ category.name_zh }} | {{ category.name }}
{% endfor %}
```

**4. 展示层 (自动生成的 README)**
```markdown
## 🏛️ 官方资源 | Official Resources
- **[Claude Code 官方文档](https://...)**
```

### 目录结构变更 | Directory Structure Changes

#### 旧结构 | Old Structure

```
awesome-claude-code/
├── README.md                 # 手动维护
├── docs/
│   ├── installation.md
│   └── getting-started.md
└── examples/
    └── example.md
```

#### 新结构 | New Structure

```
AwesomeClaudeCode/
├── THE_RESOURCES_TABLE.csv   # 数据源
├── README.md                  # 自动生成
├── templates/                 # 模板系统
│   ├── README.template.md
│   ├── categories.yaml
│   ├── resource-overrides.yaml
│   └── sections/
├── scripts/                   # 自动化脚本
│   ├── generate_readme.py
│   ├── validate_links.py
│   ├── validate_csv.py
│   └── ...
├── .github/workflows/         # CI/CD
│   ├── generate-readme.yml
│   ├── validate-links.yml
│   └── validate-csv.yml
├── docs/                      # 文档
├── examples/                  # 示例
├── tests/                     # 测试
└── assets/                    # 资源文件
```

---

## 迁移前准备 | Preparation

### 1. 环境要求 | Requirements

#### 必需工具 | Required Tools

- **Python 3.11+** (推荐) 或 **Python 3.9+** (最低)
- **Git 2.0+**
- **Make** (可选，用于快捷命令)

#### Python 依赖 | Python Dependencies

```bash
# 必需
pandas>=2.0.0
pyyaml>=6.0
requests>=2.28.0
jinja2>=3.1.0

# 可选（用于测试和开发）
pytest>=7.0.0
black>=23.0.0
ruff>=0.0.280
```

### 2. 备份现有数据 | Backup Existing Data

**⚠️ 重要：在开始迁移前务必备份！**

```bash
# 创建备份目录
mkdir -p .migration_backup

# 备份 README
cp README.md .migration_backup/README_original.md

# 备份文档
cp -r docs .migration_backup/docs_original

# 备份示例
cp -r examples .migration_backup/examples_original

# 创建备份日期标记
date > .migration_backup/backup_date.txt

# 提交备份
git add .migration_backup
git commit -m "backup: 迁移前备份所有内容"
```

### 3. 创建迁移分支 | Create Migration Branch

```bash
# 确保在最新的 main 分支
git checkout main
git pull origin main

# 创建迁移分支
git checkout -b feat/migrate-to-csv-system

# 推送到远程
git push -u origin feat/migrate-to-csv-system
```

### 4. 设置 Python 环境 | Setup Python Environment

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 升级 pip
pip install --upgrade pip

# 安装依赖（如果有 requirements.txt）
pip install -r requirements.txt
```

---

## 迁移步骤 | Migration Steps

### Step 1: 提取现有资源数据

Extract Existing Resource Data

#### 1.1 分析现有 README

```bash
# 查看 README 结构
cat README.md | grep -E "^##|^###|^-"

# 统计资源数量
grep -c "^\-" README.md
```

#### 1.2 创建资源清单

手动或使用脚本提取资源信息：

```python
# extract_resources.py
import re

def extract_resources(readme_path):
    """从 README 提取资源信息"""
    resources = []

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正则表达式提取链接和描述
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, content)

    for name, url in matches:
        resources.append({
            'name': name,
            'url': url
        })

    return resources

# 运行提取
resources = extract_resources('README.md')
print(f"找到 {len(resources)} 个资源")
```

#### 1.3 分类资源

根据新的分类系统对资源进行分类：

```python
# 参考 templates/categories.yaml 中的分类
categories = {
    'official-resources': [],  # 官方资源
    'skills': [],              # 代理技能
    'workflows': [],           # 工作流
    'tooling': [],             # 工具
    # ... 其他分类
}

# 手动或半自动分类
for resource in resources:
    category = determine_category(resource)
    categories[category].append(resource)
```

### Step 2: 创建 CSV 数据文件

Create CSV Data File

#### 2.1 设计 CSV 架构

参考 `THE_RESOURCES_TABLE.csv` 的字段结构：

```csv
ID,DisplayName,DisplayName_ZH,Category,SubCategory,PrimaryLink,SecondaryLink,Author,AuthorProfile,IsActive,DateAdded,LastModified,LastChecked,License,Description,Description_ZH,Tags_ZH,IsPinned,Section
```

**字段说明**：

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| ID | ✅ | 唯一标识符 | `off-c260c9d7` |
| DisplayName | ✅ | 英文显示名 | `Claude Code Docs` |
| DisplayName_ZH | ✅ | 中文显示名 | `Claude Code 官方文档` |
| Category | ✅ | 主分类 ID | `official-resources` |
| SubCategory | ❌ | 子分类 ID | `general` |
| PrimaryLink | ✅ | 主链接 | `https://...` |
| SecondaryLink | ❌ | 次要链接 | `https://...` |
| Author | ⚠️ | 作者名称 | `Anthropic` |
| AuthorProfile | ⚠️ | 作者主页 | `https://anthropic.com` |
| IsActive | ✅ | 是否活跃 | `TRUE` |
| DateAdded | ✅ | 添加日期 | `2025-12-15` |
| LastModified | ❌ | 最后修改 | `2025-12-15` |
| LastChecked | ✅ | 最后检查 | `2025-12-15` |
| License | ⚠️ | 许可证 | `MIT` |
| Description | ✅ | 英文描述 | `Official documentation` |
| Description_ZH | ✅ | 中文描述 | `官方文档` |
| Tags_ZH | ❌ | 中文标签 | `官方资源` |
| IsPinned | ❌ | 是否置顶 | `TRUE` |
| Section | ❌ | 所属区块 | `official` |

#### 2.2 使用迁移脚本

如果你的项目有大量资源，可以使用自动化脚本：

```bash
# 使用项目提供的迁移脚本
python scripts/migrate_existing_resources.py \
    --input README.md \
    --output THE_RESOURCES_TABLE.csv \
    --categories templates/categories.yaml
```

**脚本功能**：
- ✅ 自动提取资源信息
- ✅ 生成唯一 ID
- ✅ 尝试自动分类
- ✅ 设置默认值
- ⚠️ 需要手动补充：作者、许可证、中文翻译

#### 2.3 手动创建 CSV（小型项目）

对于少量资源，可以手动创建：

1. 复制 CSV 模板
2. 逐行填写资源信息
3. 使用工具（Excel、Google Sheets）编辑
4. 导出为 UTF-8 编码的 CSV

**Excel 操作提示**：
```
1. 打开 Excel
2. 导入现有 THE_RESOURCES_TABLE.csv 作为模板
3. 添加新行
4. 填写必填字段
5. 另存为 → CSV UTF-8 (逗号分隔)
```

### Step 3: 数据验证与清理

Data Validation and Cleaning

#### 3.1 运行 CSV 验证

```bash
# 验证 CSV 数据完整性
python scripts/validate_csv.py

# 查看验证结果
# ✅ 通过 - 数据格式正确
# ❌ 失败 - 显示具体错误
```

**常见验证错误**：

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `Missing required field: DisplayName` | 缺少必填字段 | 补充该字段 |
| `Invalid URL format` | URL 格式错误 | 检查 URL 拼写 |
| `Duplicate ID: xxx` | ID 重复 | 重新生成唯一 ID |
| `Invalid category: yyy` | 分类不存在 | 使用正确的分类 ID |
| `Invalid date format` | 日期格式错误 | 使用 YYYY-MM-DD 格式 |

#### 3.2 清理 CSV 格式

```bash
# 自动清理和格式化
python scripts/clean_csv_format.py

# 功能：
# - 移除多余空格
# - 统一日期格式
# - 按分类和名称排序
# - 验证字段格式
```

#### 3.3 验证链接

```bash
# 验证所有资源链接
python scripts/validate_links.py

# 或使用 Make 命令
make validate

# 查看失效链接
grep "FAILED" validation_results.txt
```

### Step 4: 自动填充元数据

Auto-fill Metadata

#### 4.1 GitHub 元数据

对于 GitHub 资源，自动获取元数据：

```bash
# 设置 GitHub Token（可选，用于提高 API 限制）
export GITHUB_TOKEN=your_token_here

# 运行自动填充脚本
python scripts/auto_fill_github_metadata.py

# 功能：
# ✅ 自动获取许可证信息
# ✅ 自动获取最后提交日期
# ✅ 自动获取仓库描述
# ✅ 自动获取作者信息
```

#### 4.2 手动补充非 GitHub 资源

对于非 GitHub 资源，需要手动补充：

1. **Author** - 访问资源网站查找作者信息
2. **AuthorProfile** - 作者的主页或社交媒体链接
3. **License** - 查看资源的许可证信息
4. **Description_ZH** - 翻译或撰写中文描述

### Step 5: 设置模板系统

Setup Template System

#### 5.1 复制模板文件

```bash
# 创建模板目录（如果不存在）
mkdir -p templates

# 从参考项目复制模板（或创建新的）
cp reference/templates/README.template.md templates/
cp reference/templates/categories.yaml templates/
cp reference/templates/resource-overrides.yaml templates/
```

#### 5.2 自定义分类配置

编辑 `templates/categories.yaml`：

```yaml
categories:
  # 添加或修改分类
  - id: your-custom-category
    name: "Your Custom Category"
    name_zh: "你的自定义分类"
    prefix: "cust"
    icon: "🆕"
    order: 99
    description: "Description in English"
    description_zh: "中文描述"

    # 可选：添加子分类
    subcategories:
      - id: sub1
        name: "Subcategory 1"
        name_zh: "子分类 1"
```

#### 5.3 自定义 README 模板

编辑 `templates/README.template.md`：

```jinja2
# 自定义页眉
<div align="center">
  <h1>🚀 {{ project_title }}</h1>
  <p>{{ project_description }}</p>
</div>

# 自定义分类展示
{% for category in categories %}
## {{ category.icon }} {{ category.name_zh }} | {{ category.name }}

{{ category.description_zh }}
*{{ category.description }}*

{% for resource in resources_by_category[category.id] %}
- **[{{ resource.display_name }}]({{ resource.primary_link }})**
  {{ resource.description_zh }}
  *{{ resource.description }}*
{% endfor %}
{% endfor %}
```

### Step 6: 生成新的 README

Generate New README

#### 6.1 首次生成

```bash
# 生成 README
python scripts/generate_readme.py

# 或使用 Make 命令
make generate

# 查看生成的文件
cat README.md
```

#### 6.2 对比新旧 README

```bash
# 对比差异
diff .migration_backup/README_original.md README.md

# 或使用可视化工具
git diff --no-index .migration_backup/README_original.md README.md
```

#### 6.3 调整和迭代

如果生成的 README 不满意：

1. 修改 `templates/README.template.md`
2. 调整 `templates/categories.yaml`
3. 更新 `THE_RESOURCES_TABLE.csv`
4. 重新运行 `make generate`
5. 查看效果，继续调整

### Step 7: 设置自动化工作流

Setup Automation Workflows

#### 7.1 创建 GitHub Actions 配置

```bash
# 创建工作流目录
mkdir -p .github/workflows

# 复制工作流文件
cp reference/.github/workflows/generate-readme.yml .github/workflows/
cp reference/.github/workflows/validate-links.yml .github/workflows/
cp reference/.github/workflows/validate-csv.yml .github/workflows/
```

#### 7.2 配置工作流

**README 自动生成** (`.github/workflows/generate-readme.yml`):

```yaml
name: Generate README
on:
  push:
    paths:
      - 'THE_RESOURCES_TABLE.csv'
      - 'templates/**'
    branches:
      - main

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/generate_readme.py
      - uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "chore: auto-generate README [skip ci]"
```

**链接验证** (`.github/workflows/validate-links.yml`):

```yaml
name: Validate Links
on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日运行
  workflow_dispatch:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/validate_links.py
```

#### 7.3 设置 GitHub Secrets

如果需要 GitHub Token：

```
1. 访问仓库 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. Name: GITHUB_TOKEN
4. Value: your_github_token
5. 点击 "Add secret"
```

### Step 8: 测试和验证

Testing and Verification

#### 8.1 本地测试

```bash
# 运行所有测试
make test

# 或逐个测试
pytest tests/test_csv_validation.py
pytest tests/test_readme_generation.py
pytest tests/test_link_validation.py
```

#### 8.2 验证 README 生成

```bash
# 清理生成的 README
rm README.md

# 重新生成
make generate

# 验证内容
# - 检查统计数字是否正确
# - 检查链接是否正常
# - 检查格式是否一致
# - 检查双语内容是否完整
```

#### 8.3 验证链接

```bash
# 验证所有链接
make validate

# 检查结果
# - 所有链接应返回 200 OK
# - 失效链接应被标记
# - 重定向应被正确处理
```

#### 8.4 验证自动化工作流

```bash
# 提交测试更改
echo "test" >> THE_RESOURCES_TABLE.csv
git add THE_RESOURCES_TABLE.csv
git commit -m "test: 验证自动化工作流"
git push

# 查看 GitHub Actions
# 1. 访问仓库 Actions 标签页
# 2. 查看 "Generate README" 工作流
# 3. 确认工作流成功运行
# 4. 确认 README 已自动更新
```

### Step 9: 最终清理和文档更新

Final Cleanup and Documentation

#### 9.1 清理临时文件

```bash
# 删除临时文件
rm -f validation_results.txt
rm -f *.log
rm -f .DS_Store

# 更新 .gitignore
cat >> .gitignore << EOF
# 迁移相关
.migration_backup/
*.log
validation_results.txt

# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo
EOF
```

#### 9.2 更新文档

**更新 README.md 顶部说明**：

```markdown
<!-- 注意：本文件由脚本自动生成，请勿手动编辑 -->
<!-- Auto-generated. Do not edit manually -->
<!-- 数据源：THE_RESOURCES_TABLE.csv -->
<!-- Data source: THE_RESOURCES_TABLE.csv -->
<!-- 最后生成：{{ generation_date }} -->
<!-- Last generated: {{ generation_date }} -->
```

**更新 CONTRIBUTING.md**：

添加资源提交流程说明：

```markdown
## 如何添加新资源

### 方法一：编辑 CSV（推荐）

1. Fork 本仓库
2. 编辑 `THE_RESOURCES_TABLE.csv`
3. 添加新行，填写所有必填字段
4. 运行 `make validate` 验证数据
5. 运行 `make generate` 生成 README
6. 提交 PR

### 方法二：使用 Issue 模板

1. 访问 Issues 页面
2. 选择 "Add Resource" 模板
3. 填写表单
4. 提交 Issue
5. 维护者审核后会自动创建 PR
```

#### 9.3 创建迁移总结

创建 `MIGRATION_SUMMARY.md`：

```markdown
# 迁移总结

## 迁移信息
- **开始日期**: 2025-12-15
- **完成日期**: 2025-12-16
- **迁移分支**: feat/migrate-to-csv-system

## 迁移统计
- **原始资源数**: 99
- **迁移后资源数**: 124
- **新增资源数**: 25
- **更新资源数**: 15
- **失效资源数**: 5（已移除）

## 主要变更
1. ✅ 从手动维护 README 迁移到 CSV 驱动系统
2. ✅ 实现双语支持（中英文）
3. ✅ 建立自动化工作流（链接验证、README 生成）
4. ✅ 创建完整的测试套件
5. ✅ 添加 GitHub Actions CI/CD

## 遗留问题
- [ ] 补充 15 个资源的作者信息
- [ ] 优化 8 个资源的中文翻译
- [ ] 添加更多子分类

## 下一步计划
- [ ] 继续完善文档
- [ ] 添加更多自动化脚本
- [ ] 实现 Web UI 资源提交界面
```

### Step 10: 合并到主分支

Merge to Main Branch

#### 10.1 最终检查

```bash
# 确保所有测试通过
make test

# 确保 README 正确生成
make generate

# 确保所有链接有效
make validate

# 查看所有更改
git status
git diff main
```

#### 10.2 创建 Pull Request

```bash
# 推送最终更改
git add .
git commit -m "feat: 完成 CSV 驱动系统迁移

- 迁移 124 个资源到 CSV 格式
- 实现双语支持
- 添加自动化工作流
- 更新所有文档

相关 Issue: #XXX"

git push origin feat/migrate-to-csv-system
```

然后在 GitHub 上：
1. 创建 Pull Request
2. 填写 PR 模板
3. 请求审核
4. 等待 CI 检查通过
5. 合并到 main

#### 10.3 合并后清理

```bash
# 切换回 main 分支
git checkout main
git pull origin main

# 删除迁移分支
git branch -d feat/migrate-to-csv-system
git push origin --delete feat/migrate-to-csv-system

# 标记迁移完成
git tag v2.0.0-migrated -m "完成 CSV 驱动系统迁移"
git push --tags
```

---

## 数据映射 | Data Mapping

### 字段映射表 | Field Mapping Table

从旧格式到新格式的字段映射：

| 旧字段 Old Field | 新字段 New Field | 转换规则 Conversion |
|-----------------|-----------------|-------------------|
| Resource Name | DisplayName | 直接复制（英文） |
| - | DisplayName_ZH | 翻译或手动填写 |
| URL | PrimaryLink | 直接复制 |
| Category | Category | 映射到新分类 ID |
| - | SubCategory | 根据内容分配 |
| - | Author | 从资源网站提取 |
| - | AuthorProfile | 查找作者主页 |
| Description | Description | 直接复制（英文） |
| - | Description_ZH | 翻译或手动填写 |
| - | ID | 自动生成 |
| - | DateAdded | 使用迁移日期 |
| - | IsActive | 默认 TRUE |
| - | License | 从 GitHub 获取或手动填写 |

### 分类映射 | Category Mapping

旧分类到新分类的映射：

```yaml
# 旧分类 → 新分类
mapping:
  "Official Documentation": "official-resources/general"
  "API Reference": "official-resources/api-reference"
  "Community Tools": "tooling/general"
  "Workflows": "workflows/general"
  "Examples": "workflows/examples"
  "Tutorials": "workflows/tutorials"
  "MCP Servers": "mcp-servers/general"
  "Open Source": "open-source-projects/general"
```

### 默认值设置 | Default Values

```python
defaults = {
    'IsActive': 'TRUE',
    'DateAdded': '2025-12-15',  # 迁移日期
    'LastChecked': '2025-12-15',
    'Author': 'Unknown',  # 待补充
    'AuthorProfile': '',
    'License': '',  # 待补充
    'SecondaryLink': '',
    'SubCategory': '',
    'Tags_ZH': '',
    'IsPinned': 'FALSE',
    'Section': '',
}
```

---

## 常见问题 | FAQ

### Q1: 迁移需要多长时间？

**A**: 取决于资源数量和数据质量：
- 小型项目（<50 资源）：1-2 天
- 中型项目（50-200 资源）：3-5 天
- 大型项目（>200 资源）：1-2 周

### Q2: 可以保留旧的 README 吗？

**A**: 可以！建议：
1. 备份旧 README 到 `.migration_backup/`
2. 在新 README 顶部添加说明
3. 提供迁移文档链接

### Q3: 如何处理失效的链接？

**A**:
1. 运行 `make validate` 识别失效链接
2. 在 CSV 中设置 `IsActive=FALSE`
3. 或直接删除该资源行
4. 重新生成 README

### Q4: 必须使用双语吗？

**A**: 不是必须的，但强烈推荐：
- 可以只填写一种语言
- 留空另一种语言字段
- 修改模板只显示一种语言

### Q5: 可以自定义 README 样式吗？

**A**: 完全可以！
1. 编辑 `templates/README.template.md`
2. 使用 Jinja2 语法自定义
3. 运行 `make generate` 查看效果

### Q6: GitHub Actions 是必需的吗？

**A**: 不是必需的，但强烈推荐：
- 可以只使用本地脚本
- 手动运行生成和验证
- 但会失去自动化优势

### Q7: 如何添加新的分类？

**A**:
1. 编辑 `templates/categories.yaml`
2. 添加新分类定义
3. 更新 CSV 中的资源分类
4. 重新生成 README

### Q8: 迁移后发现数据错误怎么办？

**A**:
1. 直接编辑 CSV 修正
2. 运行 `make validate` 验证
3. 运行 `make generate` 重新生成
4. 提交更改

---

## 故障排除 | Troubleshooting

### 问题 1: CSV 验证失败

**错误**:
```
Error: Invalid category 'xxx' in row 10
```

**解决方法**:
1. 检查 `templates/categories.yaml` 中的分类 ID
2. 确保 CSV 中的 Category 字段使用正确的 ID
3. 修正后重新验证

### 问题 2: README 生成失败

**错误**:
```
jinja2.exceptions.TemplateNotFound: README.template.md
```

**解决方法**:
1. 确认 `templates/README.template.md` 存在
2. 检查文件路径和文件名
3. 检查文件权限

### 问题 3: 链接验证超时

**错误**:
```
TimeoutError: Request timed out for https://...
```

**解决方法**:
1. 增加超时时间：`TIMEOUT=30 make validate`
2. 或在 `resource-overrides.yaml` 中跳过该链接：
   ```yaml
   resource-id:
     skip_validation: true
   ```

### 问题 4: GitHub API 速率限制

**错误**:
```
RateLimitError: GitHub API rate limit exceeded
```

**解决方法**:
1. 设置 GitHub Token：`export GITHUB_TOKEN=xxx`
2. 等待速率限制重置（通常 1 小时）
3. 使用 `--skip-github` 参数跳过 GitHub API 调用

### 问题 5: 编码问题

**错误**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**解决方法**:
1. 确保 CSV 使用 UTF-8 编码保存
2. 在 Excel 中：另存为 → CSV UTF-8
3. 使用文本编辑器转换编码

### 问题 6: 双语字段缺失

**错误**:
```
KeyError: 'DisplayName_ZH'
```

**解决方法**:
1. 确保 CSV 包含所有必填的双语字段
2. 可以暂时用英文填充中文字段
3. 后续再翻译和更新

---

## 回滚指南 | Rollback

如果迁移过程中遇到问题，可以回滚到迁移前状态：

### 完全回滚 | Complete Rollback

```bash
# 1. 切换到 main 分支
git checkout main

# 2. 删除迁移分支
git branch -D feat/migrate-to-csv-system

# 3. 恢复备份文件
cp .migration_backup/README_original.md README.md
rm -rf docs
cp -r .migration_backup/docs_original docs
rm -rf examples
cp -r .migration_backup/examples_original examples

# 4. 清理迁移文件
rm -rf templates/
rm -rf scripts/
rm -rf tests/
rm THE_RESOURCES_TABLE.csv

# 5. 提交回滚
git add .
git commit -m "revert: 回滚迁移，恢复原始状态"
git push origin main
```

### 部分回滚 | Partial Rollback

只回滚特定文件：

```bash
# 回滚 README
git checkout main -- README.md

# 回滚 CSV
git checkout main -- THE_RESOURCES_TABLE.csv

# 或从备份恢复特定文件
cp .migration_backup/README_original.md README.md
```

---

## 迁移检查清单 | Migration Checklist

使用这个清单确保迁移完整：

### 准备阶段 | Preparation

- [ ] 备份所有现有文件
- [ ] 创建迁移分支
- [ ] 设置 Python 环境
- [ ] 安装所有依赖
- [ ] 阅读完整迁移指南

### 数据迁移 | Data Migration

- [ ] 提取所有现有资源
- [ ] 创建 CSV 文件
- [ ] 填写所有必填字段
- [ ] 添加双语内容
- [ ] 验证 CSV 格式
- [ ] 验证所有链接
- [ ] 自动填充 GitHub 元数据
- [ ] 手动补充缺失信息

### 系统配置 | System Configuration

- [ ] 创建分类配置文件
- [ ] 创建 README 模板
- [ ] 创建资源覆盖配置
- [ ] 设置自动化脚本
- [ ] 配置 GitHub Actions
- [ ] 设置必要的 Secrets

### 测试验证 | Testing and Validation

- [ ] 运行 CSV 验证
- [ ] 生成 README 并检查
- [ ] 验证所有链接
- [ ] 运行自动化测试
- [ ] 检查双语内容
- [ ] 验证统计信息
- [ ] 测试 GitHub Actions

### 文档更新 | Documentation

- [ ] 更新 CONTRIBUTING.md
- [ ] 更新 README 说明
- [ ] 创建 HOW_IT_WORKS.md
- [ ] 创建 MIGRATION_SUMMARY.md
- [ ] 更新项目描述

### 最终检查 | Final Check

- [ ] 对比新旧 README
- [ ] 检查所有自动化工作流
- [ ] 清理临时文件
- [ ] 更新 .gitignore
- [ ] 创建 Pull Request
- [ ] 请求代码审查
- [ ] 合并到主分支
- [ ] 标记版本
- [ ] 清理迁移分支

---

## 获取帮助 | Getting Help

如果在迁移过程中遇到问题：

### 📚 查阅文档

- [系统工作原理](HOW_IT_WORKS.md)
- [贡献指南](CONTRIBUTING.md)
- [项目 README](README.md)

### 💬 寻求支持

1. **搜索现有 Issues**
   - https://github.com/stinglong/AwesomeClaudeCode/issues

2. **创建新 Issue**
   - 选择 "Migration Help" 模板
   - 详细描述问题
   - 附上错误信息和截图

3. **联系维护者**
   - Email: yian20133213@gmail.com
   - 在 Issue 中 @stinglong

### 🤝 社区支持

- 加入 Discord 社区（如有）
- 参与 GitHub Discussions
- 查看其他用户的迁移经验

---

## 迁移最佳实践 | Migration Best Practices

### ✅ 推荐做法

1. **分阶段迁移**
   - 不要一次性迁移所有内容
   - 先迁移一个分类测试
   - 验证通过后继续其他分类

2. **保持备份**
   - 定期备份迁移进度
   - 提交小的、增量的更改
   - 使用有意义的提交信息

3. **充分测试**
   - 每个阶段都运行验证
   - 及时修复发现的问题
   - 不要跳过测试步骤

4. **文档优先**
   - 记录迁移过程
   - 记录遇到的问题和解决方法
   - 为后续维护者留下指导

### ❌ 避免做法

1. **不要跳过备份**
   - 可能导致数据丢失
   - 难以回滚

2. **不要忽略验证错误**
   - 会导致后续问题累积
   - 影响数据质量

3. **不要手动编辑生成的 README**
   - 更改会被覆盖
   - 应编辑 CSV 或模板

4. **不要一次性大规模更改**
   - 难以追踪问题
   - 难以审查和合并

---

**祝你迁移顺利！如有任何问题，请随时寻求帮助。**

**Good luck with your migration! Feel free to reach out if you need any help.**

---

_最后更新：2025-12-15_
_Last updated: 2025-12-15_
