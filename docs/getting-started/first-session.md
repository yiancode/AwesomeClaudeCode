# 你的第一个 Claude Code 会话

欢迎使用 Claude Code！本教程将带你完成第一个编程会话，让你快速上手这个强大的 AI 编程助手。

## 开始之前

确保你已经：
- ✅ 安装了 Claude Code（参见[安装指南](../installation/macos.md)）
- ✅ 拥有 Anthropic 账号
- ✅ 准备好一个项目目录

## 启动 Claude Code

### 1. 打开终端并导航到项目

```bash
# 创建一个新项目目录
mkdir my-first-claude-project
cd my-first-claude-project

# 或导航到现有项目
cd /path/to/your/project
```

### 2. 启动 Claude Code

```bash
claude
```

首次运行时，系统会提示你登录。

### 3. 登录认证

```
Welcome to Claude Code!
Please login with your Anthropic account.

Opening browser for authentication...
✓ Successfully authenticated!
```

## 基础交互

### 简单对话

Claude Code 就像一个智能终端，你可以直接输入问题或指令：

```
You: 创建一个简单的 Python 脚本，打印斐波那契数列的前 10 个数字

Claude: 我来帮你创建一个打印斐波那契数列的 Python 脚本。

[创建 fibonacci.py]
```

### 查看 Claude 的操作

Claude 会清晰地显示它执行的每个操作：

```
🔧 Using tool: Write
📝 Creating file: fibonacci.py
✓ File created successfully
```

## 实战示例：创建一个 Todo 应用

让我们通过创建一个简单的 Todo 应用来体验 Claude Code 的强大功能。

### 步骤 1：描述需求

```
You: 帮我创建一个简单的命令行 Todo 应用，使用 Python，支持添加、删除、列出任务，
     数据保存到 JSON 文件中。

Claude: 我来帮你创建一个命令行 Todo 应用。这个应用将支持：
- 添加新任务
- 删除任务
- 列出所有任务
- 标记任务完成
- 数据持久化到 JSON 文件

让我开始创建所需的文件...
```

### 步骤 2：观察 Claude 的工作流程

Claude 会：
1. 创建项目结构
2. 编写主程序文件
3. 添加数据模型
4. 实现功能模块
5. 创建测试文件
6. 生成使用文档

### 步骤 3：测试应用

```
You: 运行这个 Todo 应用并添加一些测试任务

Claude: 我来运行 Todo 应用并添加一些测试任务。

🔧 Using tool: Bash
$ python todo.py add "学习 Claude Code"
✓ 任务添加成功：学习 Claude Code

$ python todo.py add "完成项目文档"
✓ 任务添加成功：完成项目文档

$ python todo.py list
📋 任务列表：
1. [ ] 学习 Claude Code
2. [ ] 完成项目文档
```

## 常用指令模式

### 1. 创建新功能

```
You: 添加一个功能，可以按优先级排序任务
```

### 2. 修复错误

```
You: 运行测试时出现错误，请帮我修复
```

### 3. 代码审查

```
You: 审查 todo.py 的代码，提出改进建议
```

### 4. 重构代码

```
You: 将 Todo 类重构为使用设计模式
```

### 5. 添加测试

```
You: 为所有功能编写单元测试
```

## 高效使用技巧

### 1. 明确具体的需求

❌ 不好的指令：
```
You: 改进这个代码
```

✅ 好的指令：
```
You: 重构 todo.py 中的 add_task 方法，添加输入验证和错误处理
```

### 2. 分步骤处理复杂任务

```
You: 我想创建一个 REST API。先创建基础项目结构，然后我们逐步添加功能。
```

### 3. 利用上下文

Claude Code 会记住整个会话的上下文：

```
You: 使用我们刚创建的 Todo 类
Claude: 好的，我会使用之前创建的 Todo 类...
```

### 4. 请求解释

```
You: 解释一下你刚才使用的装饰器模式
```

## 使用 TODO 管理

Claude Code 内置了任务管理功能：

```
You: 创建一个任务列表来跟踪我们的开发进度

Claude: 我会使用 TodoWrite 工具来创建和管理任务列表：

📝 任务列表：
- [ ] 设置项目结构
- [ ] 实现核心功能
- [ ] 添加错误处理
- [ ] 编写测试
- [ ] 创建文档
```

## 文件操作

### 读取文件

```
You: 查看 package.json 的内容
```

### 编辑文件

```
You: 在 README.md 中添加安装说明
```

### 搜索代码

```
You: 搜索所有包含 "TODO" 的文件
```

### 批量操作

```
You: 将所有 .js 文件中的 var 替换为 const 或 let
```

## 使用 Git

### 查看状态

```
You: 显示 git 状态
```

### 提交更改

```
You: 提交所有更改，写一个合适的提交信息
```

### 创建 PR

```
You: 创建一个 pull request
```

## 集成外部工具

### 运行测试

```
You: 运行测试并修复失败的测试
```

### 使用 Docker

```
You: 创建一个 Dockerfile 来容器化这个应用
```

### 部署

```
You: 创建 GitHub Actions 工作流来自动部署
```

## 会话管理

### 保存会话

Claude Code 会自动保存会话历史。

### 继续之前的工作

```bash
# 在同一项目目录中
claude

You: 继续我们之前的 Todo 应用开发
```

### 清除上下文

```
You: /clear
```

## 获取帮助

### 内置帮助

```
You: /help
```

### 查看可用命令

```
You: 显示所有可用的 Claude Code 命令
```

### 调试信息

```
You: /debug
```

## 最佳实践建议

### 1. 项目开始时

- 清晰描述项目目标
- 指定技术栈和框架
- 提供现有代码结构信息

### 2. 开发过程中

- 经常运行和测试代码
- 及时保存重要更改
- 使用任务列表跟踪进度

### 3. 问题解决

- 提供完整的错误信息
- 描述期望的行为
- 分享相关代码片段

### 4. 代码质量

- 定期请求代码审查
- 运行 linter 和格式化工具
- 编写测试确保功能正确

## 常见问题

### Q: Claude Code 能访问互联网吗？

A: 是的，Claude Code 可以通过 WebFetch 和 WebSearch 工具访问互联网获取信息。

### Q: 如何处理大型项目？

A: Claude Code 智能管理上下文，但建议：
- 分模块处理
- 使用清晰的文件结构
- 定期总结进度

### Q: 能否自定义 Claude 的行为？

A: 可以通过配置文件（`.claude/claude.json`）和全局指令（`~/.claude/CLAUDE.md`）自定义。

### Q: 支持哪些编程语言？

A: Claude Code 支持所有主流编程语言，包括但不限于：
- Python, JavaScript/TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, Swift, Kotlin 等

## 下一步

恭喜完成第一个 Claude Code 会话！接下来你可以：

1. 📖 阅读[基本命令指南](basic-commands.md)
2. 🔧 学习[高级功能](../advanced/agents.md)
3. 💡 探索[最佳实践](../../README.md#-最佳实践)
4. 🚀 查看[真实案例](../case-studies/README.md)

## 反馈和支持

- 报告问题：[GitHub Issues](https://github.com/anthropics/claude-code/issues)
- 加入社区：[Discord](https://discord.gg/anthropic)
- 查看文档：[官方文档](https://docs.anthropic.com/claude-code)

---

💡 **提示**：Claude Code 会不断学习和改进。定期更新以获得最新功能和优化！