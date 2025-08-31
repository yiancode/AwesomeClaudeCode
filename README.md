# 🚀 Awesome Claude Code

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Anthropic-blue)](https://claude.ai/code)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 一份精心策划的 Claude Code 资源、最佳实践、工具和项目列表

Claude Code 是 Anthropic 推出的官方 AI 编程助手，可以帮助开发者更高效地编写、调试和优化代码。本项目旨在收集和分享 Claude Code 的最佳实践、教程、工具和生态系统资源。

## 📚 目录

- [🎯 快速开始](#-快速开始)
- [📖 官方资源](#-官方资源)
- [🔧 安装与配置](#-安装与配置)
- [🚦 入门教程](#-入门教程)
- [⚡ 高级功能](#-高级功能)
- [💡 最佳实践](#-最佳实践)
- [📂 案例研究](#-案例研究)
- [🛠️ 第三方工具](#️-第三方工具)
- [🌐 生态系统](#-生态系统)
- [🔌 MCP 服务器](#-mcp-服务器)
- [📦 开源项目](#-开源项目)
- [🤝 贡献指南](#-贡献指南)

## 🎯 快速开始

### 系统要求

- macOS 10.15+ 或 Windows 10+ 或 Linux
- Node.js 18.0+ (用于某些功能)
- Git (用于版本控制)

### 快速安装

```bash
# macOS/Linux
curl -fsSL https://storage.googleapis.com/public-download-production/claude-public/install.sh | sh

# Windows (PowerShell)
iwr https://storage.googleapis.com/public-download-production/claude-public/install.ps1 -useb | iex
```

### 首次使用

1. 安装 Claude Code 后，在终端中输入 `claude` 启动
2. 使用 Anthropic 账号登录
3. 在任意项目目录中运行 `claude` 开始使用

## 📖 官方资源

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code) - 官方文档和 API 参考
- [Anthropic 博客](https://www.anthropic.com/news) - 最新功能和更新
- [Claude Code GitHub Issues](https://github.com/anthropics/claude-code/issues) - 问题反馈和功能请求
- [Discord 社区](https://discord.gg/anthropic) - 官方 Discord 社区

## 🔧 安装与配置

### 详细安装指南

- [macOS 安装指南](docs/installation/macos.md)
- [Windows 安装指南](docs/installation/windows.md)
- [Linux 安装指南](docs/installation/linux.md)
- [配置指南](docs/installation/configuration.md)
- [环境变量设置](docs/installation/environment.md)
- [故障排除](docs/installation/troubleshooting.md)

### 配置文件

Claude Code 支持多种配置文件：

- `.claude/claude.json` - 项目级配置
- `~/.claude/CLAUDE.md` - 全局用户指令
- `.cloderc` - 项目特定设置

## 🚦 入门教程

### 基础教程

- [你的第一个 Claude Code 会话](docs/getting-started/first-session.md)
- [基本命令和操作](docs/getting-started/basic-commands.md)
- [理解工作流程](docs/getting-started/workflow.md)
- [文件操作基础](docs/getting-started/file-operations.md)
- [代码生成与编辑](docs/getting-started/code-generation.md)

### 进阶教程

- [使用 TODO 任务管理](docs/getting-started/todo-management.md)
- [调试和错误处理](docs/getting-started/debugging.md)
- [测试驱动开发](docs/getting-started/tdd.md)
- [版本控制集成](docs/getting-started/git-integration.md)

## ⚡ 高级功能

### 核心功能

- [Agent 任务自动化](docs/advanced/agents.md)
- [多文件编辑](docs/advanced/multi-file-editing.md)
- [代码重构](docs/advanced/refactoring.md)
- [自定义 Hooks](docs/advanced/hooks.md)
- [MCP (Model Context Protocol) 集成](docs/advanced/mcp.md)

### 高级技巧

- [性能优化技巧](docs/advanced/performance.md)
- [上下文管理](docs/advanced/context-management.md)
- [自定义工作流](docs/advanced/custom-workflows.md)
- [批量操作](docs/advanced/batch-operations.md)
- [扩展功能](docs/advanced/extensions.md)

## 💡 最佳实践

### 编码规范

- 遵循项目现有的代码风格
- 使用清晰的提示词
- 充分利用上下文
- 分阶段处理复杂任务

### 提示工程

- [高效提示词模板](docs/case-studies/prompt-templates.md)
- [任务分解策略](docs/case-studies/task-breakdown.md)
- [上下文优化](docs/case-studies/context-optimization.md)

### 工作流优化

- [团队协作最佳实践](docs/case-studies/team-collaboration.md)
- [CI/CD 集成](docs/case-studies/cicd-integration.md)
- [代码审查流程](docs/case-studies/code-review.md)

## 📂 案例研究

### Web 开发

- [构建全栈 Web 应用](examples/web/fullstack-app/)
- [React/Vue/Angular 项目开发](examples/web/frontend/)
- [Node.js API 开发](examples/web/backend/)
- [数据库设计与优化](examples/web/database/)

### 移动开发

- [React Native 应用开发](examples/mobile/react-native/)
- [Flutter 应用开发](examples/mobile/flutter/)
- [原生应用开发](examples/mobile/native/)

### 数据科学

- [数据分析与可视化](examples/data-science/analysis/)
- [机器学习模型开发](examples/data-science/ml/)
- [数据处理管道](examples/data-science/pipeline/)

### DevOps

- [自动化部署脚本](examples/devops/deployment/)
- [容器化应用](examples/devops/docker/)
- [Kubernetes 配置](examples/devops/k8s/)

## 🛠️ 第三方工具

### IDE 集成

- [VS Code 扩展](docs/third-party/vscode.md)
- [IntelliJ IDEA 插件](docs/third-party/intellij.md)
- [Vim/Neovim 集成](docs/third-party/vim.md)
- [Emacs 集成](docs/third-party/emacs.md)

### 终端工具

- [Oh My Zsh 插件](docs/third-party/oh-my-zsh.md)
- [Fish Shell 集成](docs/third-party/fish.md)
- [PowerShell 模块](docs/third-party/powershell.md)

### 自动化工具

- [GitHub Actions 集成](docs/third-party/github-actions.md)
- [GitLab CI 集成](docs/third-party/gitlab-ci.md)
- [Jenkins 插件](docs/third-party/jenkins.md)

## 🌐 生态系统

### 社区资源

- [Claude Code 社区论坛](https://community.claude.ai)
- [Reddit r/ClaudeCode](https://reddit.com/r/claudecode)
- [Stack Overflow 标签](https://stackoverflow.com/questions/tagged/claude-code)
- [YouTube 教程频道](docs/ecosystem/youtube-channels.md)

### 学习资源

- [在线课程](docs/ecosystem/courses.md)
- [书籍推荐](docs/ecosystem/books.md)
- [博客文章](docs/ecosystem/blogs.md)
- [播客节目](docs/ecosystem/podcasts.md)

### 模板和样板

- [项目模板集合](docs/ecosystem/templates.md)
- [代码片段库](docs/ecosystem/snippets.md)
- [配置文件示例](docs/ecosystem/configs.md)

## 🔌 MCP 服务器

MCP (Model Context Protocol) 是 Claude Code 的扩展协议，允许集成外部工具和服务。

### 官方 MCP 服务器

- [Filesystem Server](docs/mcp/filesystem.md) - 文件系统操作
- [GitHub Server](docs/mcp/github.md) - GitHub 集成
- [Google Drive Server](docs/mcp/google-drive.md) - Google Drive 集成
- [Slack Server](docs/mcp/slack.md) - Slack 集成

### 社区 MCP 服务器

- [Database Servers](docs/mcp/database.md) - 各种数据库集成
- [Cloud Services](docs/mcp/cloud.md) - AWS、Azure、GCP 集成
- [API Integrations](docs/mcp/api.md) - 第三方 API 集成
- [Custom Servers](docs/mcp/custom.md) - 创建自定义 MCP 服务器

### MCP 开发

- [MCP 协议规范](https://modelcontextprotocol.io/docs)
- [创建你的第一个 MCP 服务器](docs/mcp/development.md)
- [MCP 服务器最佳实践](docs/mcp/best-practices.md)

## 📦 开源项目

### 使用 Claude Code 构建的项目

- **Web 应用** - 使用 Claude Code 构建的现代 Web 应用集合
- **项目模板** - 各种技术栈的快速启动模板
- **代码片段** - 常用的代码片段和实用工具

### Claude Code 扩展

- **IDE 扩展** - 编辑器和 IDE 的集成插件
- **主题和配置** - 个性化的界面主题和配置文件
- **实用工具** - 提高开发效率的辅助工具

### 贡献项目

欢迎提交你的项目！请查看[贡献指南](CONTRIBUTING.md)了解如何添加你的项目。

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是：

- 🐛 报告错误
- 📝 改进文档
- 🎨 提交案例
- 💡 建议新功能
- 🔧 提交代码

请阅读[贡献指南](CONTRIBUTING.md)了解详细信息。

### 贡献者

感谢所有为这个项目做出贡献的人！

<a href="https://github.com/yiancode/AwesomeClaudeCode/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=yiancode/AwesomeClaudeCode" />
</a>

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yiancode/AwesomeClaudeCode&type=Date)](https://star-history.com/#yiancode/AwesomeClaudeCode&Date)

## 📮 联系我们

- GitHub Issues: [提交问题](https://github.com/yiancode/AwesomeClaudeCode/issues)
- Email: yian20133213@gmail.com
- GitHub: [@yiancode](https://github.com/yiancode)

---

<div align="center">
  <b>⭐ 如果这个项目对你有帮助，请给一个 Star！⭐</b>
  
  <sub>用 ❤️ 构建，由 Claude Code 社区维护</sub>
</div>