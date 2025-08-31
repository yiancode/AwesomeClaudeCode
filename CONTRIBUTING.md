# 贡献指南

感谢你对 Awesome Claude Code 项目的关注！我们欢迎所有形式的贡献，无论是修复错误、改进文档、添加新功能还是分享使用案例。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [报告问题](#报告问题)
- [提交更改](#提交更改)
- [贡献类型](#贡献类型)
- [开发指南](#开发指南)
- [审查流程](#审查流程)

## 行为准则

本项目遵循[贡献者公约](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)。参与本项目即表示你同意遵守其条款。

### 我们的承诺

我们致力于为每个人提供一个友好、安全和欢迎的环境，无论其年龄、体型、残疾、种族、性别特征、性别认同和表达、经验水平、教育、社会经济地位、国籍、个人外表、种族、宗教或性身份和取向。

## 如何贡献

### 第一次贡献？

如果这是你第一次为开源项目贡献，欢迎！这里有一些资源可以帮助你：

- [如何为开源做贡献](https://opensource.guide/how-to-contribute/)
- [第一次贡献](https://github.com/firstcontributions/first-contributions)
- [GitHub 流程指南](https://guides.github.com/introduction/flow/)

寻找标记为 `good first issue` 或 `help wanted` 的问题开始。

## 报告问题

### Bug 报告

发现 bug？请通过 [GitHub Issues](https://github.com/yiancode/AwesomeClaudeCode/issues) 报告。

创建 bug 报告时，请包含：

1. **问题描述**：清晰简洁地描述问题
2. **复现步骤**：
   - 步骤 1
   - 步骤 2
   - 步骤 3
   - ...
3. **预期行为**：描述你期望发生的事情
4. **实际行为**：描述实际发生的事情
5. **截图**：如果适用，添加截图帮助解释问题
6. **环境信息**：
   - Claude Code 版本
   - 操作系统和版本
   - Node.js 版本（如果相关）
   - 其他相关环境信息

**模板示例**：

```markdown
## Bug 描述
[清晰简洁地描述 bug]

## 复现步骤
1. 进入 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## 预期行为
[描述你期望发生的事情]

## 截图
[如果适用，添加截图]

## 环境
- Claude Code 版本：[例如 1.0.0]
- OS：[例如 macOS 12.0]
- Node.js：[例如 18.0.0]
```

### 功能请求

有新功能的想法？我们很乐意听到！

创建功能请求时，请包含：

1. **功能描述**：清晰描述你想要的功能
2. **使用场景**：解释为什么需要这个功能
3. **建议实现**：如果有想法，描述如何实现
4. **替代方案**：你考虑过的任何替代方案

## 提交更改

### 1. Fork 仓库

点击仓库页面右上角的 "Fork" 按钮。

### 2. 克隆你的 Fork

```bash
git clone https://github.com/your-username/AwesomeClaudeCode.git
cd AwesomeClaudeCode
```

### 3. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-description
```

分支命名约定：
- `feature/` - 新功能
- `fix/` - Bug 修复
- `docs/` - 文档改进
- `refactor/` - 代码重构
- `test/` - 测试相关

### 4. 进行更改

确保你的更改：
- ✅ 遵循项目的编码风格
- ✅ 包含适当的文档
- ✅ 有意义的提交信息
- ✅ 不破坏现有功能

### 5. 提交更改

```bash
git add .
git commit -m "feat: 添加新的 MCP 服务器示例"
```

提交信息格式：
- `feat:` - 新功能
- `fix:` - Bug 修复
- `docs:` - 文档更改
- `style:` - 格式更改（不影响代码运行）
- `refactor:` - 代码重构
- `test:` - 测试相关
- `chore:` - 构建过程或辅助工具的变动

### 6. 推送到你的 Fork

```bash
git push origin feature/your-feature-name
```

### 7. 创建 Pull Request

1. 访问原始仓库
2. 点击 "New Pull Request"
3. 选择你的分支
4. 填写 PR 模板
5. 提交 PR

## 贡献类型

### 📝 文档

我们特别欢迎文档贡献：

- 修复拼写错误或语法错误
- 改进现有文档的清晰度
- 添加缺失的文档
- 翻译文档到其他语言
- 添加或改进代码示例

### 💻 代码

代码贡献包括：

- 修复 bug
- 添加新功能
- 改进性能
- 重构代码
- 添加测试

### 🎨 设计

设计贡献包括：

- 改进 UI/UX
- 创建图标或图形
- 改进可访问性

### 📚 案例和示例

分享你的使用案例：

- 真实项目示例
- 教程和指南
- 最佳实践
- 技巧和窍门

### 🌍 翻译

帮助我们国际化：

- 翻译文档
- 本地化示例
- 审查现有翻译

## 开发指南

### 项目结构

```
AwesomeClaudeCode/
├── docs/              # 文档文件
│   ├── installation/  # 安装指南
│   ├── getting-started/ # 入门教程
│   ├── advanced/      # 高级功能
│   └── ...
├── examples/          # 示例代码
├── images/           # 图片资源
├── CONTRIBUTING.md   # 贡献指南
├── LICENSE          # 许可证
└── README.md        # 项目说明
```

### 文档规范

- 使用 Markdown 格式
- 保持一致的标题层级
- 添加目录（TOC）用于长文档
- 使用清晰的代码示例
- 包含截图或 GIF（当有帮助时）

### 代码规范

- 遵循项目的 `.editorconfig` 设置
- 使用有意义的变量名和函数名
- 添加必要的注释
- 保持代码简洁清晰

### 测试

- 为新功能添加测试
- 确保所有测试通过
- 保持测试覆盖率

## 审查流程

### Pull Request 审查

所有提交都需要审查才能合并。审查过程包括：

1. **自动检查**：
   - CI/CD 测试通过
   - 代码质量检查
   - 文档构建成功

2. **人工审查**：
   - 代码质量和风格
   - 功能正确性
   - 文档完整性
   - 向后兼容性

3. **反馈和迭代**：
   - 审查者可能会请求更改
   - 讨论和改进
   - 最终批准

### 审查时间

我们努力在以下时间内审查 PR：
- 小型更改（文档、拼写错误）：1-2 天
- 中型更改（bug 修复、小功能）：3-5 天
- 大型更改（新功能、重构）：1 周

### 合并要求

PR 必须满足以下条件才能合并：
- ✅ 所有 CI 检查通过
- ✅ 至少一位维护者批准
- ✅ 没有未解决的对话
- ✅ 分支是最新的

## 获得帮助

需要帮助？你可以：

- 📧 发送邮件到：yian20133213@gmail.com
- 💬 在 [GitHub Issues](https://github.com/yiancode/AwesomeClaudeCode/issues) 中讨论
- 📖 查看项目文档和示例

## 认可贡献者

我们使用 [All Contributors](https://github.com/all-contributors/all-contributors) 来认可所有贡献者。

贡献类型：
- 💻 代码
- 📖 文档
- 🎨 设计
- 💡 示例
- 🤔 想法和反馈
- 🌍 翻译
- 📋 组织
- 👀 审查

## 许可证

通过贡献，你同意你的贡献将在 [MIT 许可证](LICENSE) 下发布。

## 感谢

感谢所有已经贡献的人！

特别感谢：
- Anthropic 团队创建了 Claude Code
- 所有贡献者和用户
- 开源社区

---

**记住**：最好的贡献方式是开始使用 Claude Code 并分享你的经验！

如有任何问题，请随时联系维护者。我们期待你的贡献！ 🎉