# GitHub Actions 工作流详解

## 工作流概览

项目包含 3 个主要工作流 + 1 个依赖更新工作流：

1. **Validate Links** - 定期链接验证（每周一次）
2. **Generate README** - 自动生成 README（PR 触发）
3. **Format Check** - 代码格式检查（PR/Push 触发）
4. **Dependabot Updates** - 依赖自动更新（GitHub 自动配置）

---

## 1️⃣ Validate Links 工作流

### 触发条件
```yaml
触发器：
├─ 定期触发：每周一 UTC 0:00 (北京时间周一 8:00)
├─ 手动触发：workflow_dispatch
└─ PR 触发：修改 THE_RESOURCES_TABLE.csv
```

### 流程图

```mermaid
graph TD
    A[开始] --> B[检出代码<br/>Checkout repository]
    B --> C[设置 Python 3.11<br/>Setup Python]
    C --> D[安装依赖<br/>pip install -r requirements.txt]
    D --> E[运行链接验证<br/>validate_links.py]

    E --> F{验证结果?}
    F -->|成功| G[没有失败链接]
    F -->|失败| H[发现失败链接]

    E --> I[上传验证报告<br/>Artifact: validation-report.txt]

    H --> J{是否已有<br/>broken-links Issue?}
    J -->|否| K[创建新 Issue<br/>标签: broken-links, automated]
    J -->|是| L[更新现有 Issue<br/>添加最新报告]

    K --> M{触发方式?}
    L --> M
    G --> M

    M -->|PR 触发| N[在 PR 添加评论<br/>显示验证结果]
    M -->|定期/手动| O[结束]
    N --> O

    style H fill:#ffcccc
    style G fill:#ccffcc
    style K fill:#ffeecc
    style L fill:#ffeecc
```

### 关键步骤说明

**步骤 1-4：环境准备**
- 检出代码到 GitHub Actions runner
- 配置 Python 3.11 环境
- 安装项目依赖（PyYAML, requests 等）

**步骤 5：链接验证**
```bash
python3 scripts/validate_links.py > validation_report.txt 2>&1
```
- 读取 THE_RESOURCES_TABLE.csv
- 逐个验证所有资源的 PrimaryLink 和 SecondaryLink
- 检测 HTTP 状态码（200-399 为成功）
- 生成验证报告

**步骤 6：结果处理**
- 检查报告中是否包含 "❌" 或 "broken" 关键词
- 设置 `has_failures` 输出变量

**步骤 7-9：Issue 管理**（仅在有失败链接时）
- 查询是否已存在 `broken-links` 标签的 Issue
- 如果不存在，创建新 Issue
- 如果存在，在现有 Issue 添加评论

**步骤 10：Artifacts**
- 无论成功或失败，都上传验证报告
- 保留期：30 天
- 可在 Actions 页面下载查看

---

## 2️⃣ Generate README 工作流

### 触发条件
```yaml
触发器：
├─ PR 触发：修改以下文件时
│   ├─ THE_RESOURCES_TABLE.csv
│   ├─ templates/**
│   └─ scripts/generate_readme.py
└─ 手动触发：workflow_dispatch
```

### 流程图

```mermaid
graph TD
    A[开始] --> B[检出 PR 分支<br/>Checkout with token]
    B --> C[设置 Python 3.11<br/>Setup Python + Cache]
    C --> D[安装依赖<br/>pip install -r requirements.txt]
    D --> E[生成 README<br/>generate_readme.py]

    E --> F[设置中文环境变量<br/>LANG=zh_CN.UTF-8]
    F --> G{检查文件变更<br/>git diff README.md}

    G -->|无变更| H[README 已是最新]
    G -->|有变更| I[配置 Git 身份<br/>github-actions bot]

    I --> J[提交变更<br/>git add README.md<br/>git commit]
    J --> K[推送到 PR 分支<br/>git push]
    K --> L[在 PR 添加评论<br/>说明 README 已更新]

    H --> M[结束]
    L --> M

    style H fill:#ccffcc
    style I fill:#cce5ff
    style L fill:#ccffcc
```

### 关键步骤说明

**步骤 1：特殊检出配置**
```yaml
ref: ${{ github.head_ref }}  # 检出 PR 分支
token: ${{ secrets.GITHUB_TOKEN }}  # 使用 Token 以便推送
```

**步骤 2-5：生成 README**
```bash
LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 python3 scripts/generate_readme.py
```
- 设置中文环境变量确保正确处理中文字符
- 从 CSV 和模板生成完整的 README.md
- 包含统计信息、目录、分类内容等

**步骤 6：变更检测**
```bash
git diff --quiet README.md || echo "changed=true"
```
- 使用 git diff 检测 README.md 是否有变化
- 只有在有变化时才提交

**步骤 7-9：自动提交**（仅在有变更时）
- 配置 Git 用户为 `github-actions[bot]`
- 提交信息：`docs: 自动生成 README [skip ci]`
- `[skip ci]` 避免触发新的 CI 循环

**步骤 10：PR 反馈**
- 在 PR 添加友好的评论
- 提示用户 README 已更新
- 包含 emoji 和统计信息

---

## 3️⃣ Format Check 工作流

### 触发条件
```yaml
触发器：
├─ PR 触发：修改 .py 或 pyproject.toml 文件
├─ Push 到 main：修改 .py 文件
└─ 手动触发：workflow_dispatch
```

### 流程图

```mermaid
graph TD
    A[开始] --> B[检出代码<br/>Checkout repository]
    B --> C[设置 Python 3.11<br/>Setup Python]
    C --> D[安装 ruff<br/>pip install ruff]

    D --> E[运行格式检查<br/>ruff format --check .]
    D --> F[运行 Lint 检查<br/>ruff check .]

    E --> G{格式检查}
    F --> H{Lint 检查}

    G -->|通过| I[格式 ✓]
    G -->|失败| J[格式 ✗]
    H -->|通过| K[Lint ✓]
    H -->|失败| L[Lint ✗]

    I --> M{汇总结果}
    J --> M
    K --> M
    L --> M

    M -->|全部通过| N[✅ 所有检查通过]
    M -->|有失败| O{触发方式?}

    O -->|PR 触发| P[在 PR 添加评论<br/>说明失败原因和修复方法]
    O -->|Push 触发| Q[设置失败状态]

    P --> R[工作流失败 exit 1]
    Q --> R
    N --> S[工作流成功]

    style I fill:#ccffcc
    style K fill:#ccffcc
    style J fill:#ffcccc
    style L fill:#ffcccc
    style N fill:#ccffcc
    style R fill:#ffcccc
```

### 关键步骤说明

**步骤 1-4：环境准备**
- 使用 ruff 进行 Python 代码格式化和 Lint 检查
- ruff 是新一代 Python linter，速度极快

**步骤 5：格式检查**
```bash
ruff format --check .
```
- 检查代码格式是否符合标准（PEP 8）
- 只检查，不修改文件
- `continue-on-error: true` 允许继续执行

**步骤 6：Lint 检查**
```bash
ruff check .
```
- 检查代码质量问题
- 未使用的导入、变量
- 潜在的 bug 和反模式

**步骤 7-8：结果汇总**
- 收集两个检查的结果
- 只要有一个失败，整体就失败

**步骤 9：PR 反馈**（仅 PR 触发且失败时）
- 添加详细的评论说明问题
- 提供修复命令：
  ```bash
  make format  # 自动修复格式问题
  ```
- 包含 pre-commit hook 配置建议

**步骤 10：失败处理**
- 如果检查失败，工作流返回失败状态
- 阻止 PR 合并（如果设置了分支保护规则）

---

## 工作流交互关系图

```mermaid
graph LR
    A[开发者] -->|1. 修改 CSV| B[提交到 PR 分支]
    B -->|触发| C[Generate README]
    B -->|触发| D[Validate Links]
    B -->|触发| E[Format Check]

    C -->|2. 生成| F[README.md]
    F -->|3. 自动提交| B

    D -->|4. 验证| G[链接状态]
    G -->|失败| H[创建/更新 Issue]
    G -->|成功| I[PR 评论]

    E -->|5. 检查| J[代码格式]
    J -->|失败| K[PR 评论 + 阻止合并]
    J -->|通过| L[允许合并]

    B -->|6. 合并到 main| M[主分支]

    N[定期调度<br/>每周一] -->|触发| D

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style F fill:#ccffcc
    style H fill:#ffcccc
    style M fill:#e8f5e9
```

---

## 数据流向图

```mermaid
graph TD
    A[THE_RESOURCES_TABLE.csv] -->|读取| B[generate_readme.py]
    C[templates/categories.yaml] -->|读取| B
    D[templates/resource-overrides.yaml] -->|读取| B

    B -->|生成| E[README.md]

    A -->|读取| F[validate_csv.py]
    A -->|读取| G[validate_links.py]

    F -->|验证| H[数据完整性报告]
    G -->|验证| I[链接状态报告]

    I -->|失败时| J[GitHub Issue]

    K[scripts/*.py] -->|检查| L[ruff format/check]
    L -->|报告| M[PR 评论]

    E -->|触发| N[Dependabot]
    N -->|更新| O[依赖 PR]

    style A fill:#fff3cd
    style E fill:#d1ecf1
    style J fill:#f8d7da
    style H fill:#d4edda
    style I fill:#d4edda
```

---

## 完整执行时间线示例

### 场景：开发者添加新资源

```
时间线：
┌─────────────────────────────────────────────────────────────────┐
│ T+0s    开发者修改 THE_RESOURCES_TABLE.csv，添加新资源          │
│ T+1s    git push 到 feature/add-new-resource 分支              │
│ T+2s    GitHub 接收到 push 事件                                │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ T+3s    创建 Pull Request                                       │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ T+4s    ⚡ 并行触发 3 个工作流：                                │
│         ├─ Generate README (工作流 1)                          │
│         ├─ Validate Links (工作流 2)                           │
│         └─ Format Check (工作流 3)                             │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ T+10s   工作流 3 完成 (最快，仅检查 Python 文件)                │
│         └─ ✅ Format Check 通过                                │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ T+15s   工作流 1 完成                                           │
│         ├─ 生成新的 README.md                                  │
│         ├─ 自动提交到 PR 分支                                   │
│         └─ 💬 在 PR 添加评论：README 已更新                     │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ T+45s   工作流 2 完成 (最慢，需要验证所有链接)                   │
│         ├─ 验证 124 个资源的链接                                │
│         ├─ 发现 2 个失败链接                                    │
│         ├─ 上传验证报告到 Artifacts                             │
│         ├─ 🐛 创建 Issue: "链接验证失败"                        │
│         └─ 💬 在 PR 添加评论：发现失败链接                      │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ T+60s   开发者查看 PR                                           │
│         ├─ ✅ 看到 README 已自动更新                            │
│         ├─ ⚠️  看到链接验证警告                                 │
│         └─ 点击查看详细报告                                     │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ T+120s  开发者修复失败的链接                                     │
│         └─ git push 更新 (触发新一轮工作流)                     │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ T+180s  所有检查通过                                            │
│         ├─ ✅ Format Check                                      │
│         ├─ ✅ Generate README                                   │
│         └─ ✅ Validate Links                                    │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ T+200s  维护者审查并合并 PR                                      │
│         └─ 合并到 main 分支                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 定期任务时间线

```
周一 (Monday)
00:00 UTC (08:00 CST)
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 🕐 Validate Links 定期触发                                      │
│    ├─ 验证所有 124 个资源                                       │
│    ├─ 检测死链、重定向、超时                                    │
│    └─ 生成周度报告                                             │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 如果发现问题：                                                   │
│ ├─ 创建/更新 Issue with broken-links 标签                      │
│ ├─ 上传详细报告到 Artifacts                                     │
│ └─ 等待维护者处理                                               │
└─────────────────────────────────────────────────────────────────┘

周二 - 周日
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Dependabot 每日检查依赖更新                                      │
│ ├─ 检测 requirements.txt 更新                                   │
│ ├─ 检测 GitHub Actions 版本更新                                │
│ └─ 自动创建 PR                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 工作流配置对比表

| 特性 | Validate Links | Generate README | Format Check |
|------|---------------|----------------|--------------|
| **触发频率** | 每周 + PR + 手动 | PR + 手动 | PR + Push + 手动 |
| **执行时间** | ~30-60秒 | ~10-20秒 | ~5-10秒 |
| **主要工具** | requests, urllib | PyYAML | ruff |
| **Python 版本** | 3.11 | 3.11 | 3.11 |
| **失败后果** | 创建 Issue | PR 评论 | 阻止合并 |
| **自动修复** | ❌ | ✅ (生成 README) | ❌ |
| **Artifacts** | ✅ (报告) | ❌ | ❌ |
| **成本影响** | 中 (HTTP 请求) | 低 | 低 |

---

## 总结

### 工作流设计原则

1. **自动化优先** - 减少人工干预，提高效率
2. **快速反馈** - PR 触发，立即得到结果
3. **友好提示** - 清晰的评论和 Issue 说明
4. **防御性设计** - continue-on-error 避免单点失败
5. **可追溯性** - Artifacts 保存详细报告

### 优势

- ✅ 自动生成 README，保持数据同步
- ✅ 定期检测死链，维护资源质量
- ✅ 代码格式检查，保持代码一致性
- ✅ 并行执行，节省时间
- ✅ 智能 Issue 管理，避免重复

### 可改进空间

- 🔧 添加测试覆盖率报告
- 🔧 集成代码质量分析工具
- 🔧 添加自动发布工作流
- 🔧 实现自动修复死链（查找替代资源）
