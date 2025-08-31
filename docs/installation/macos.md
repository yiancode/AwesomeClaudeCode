# macOS 安装指南

## 系统要求

- macOS 10.15 (Catalina) 或更高版本
- 至少 4GB RAM（推荐 8GB+）
- 2GB 可用磁盘空间
- 互联网连接

## 安装方法

### 方法 1：使用安装脚本（推荐）

```bash
curl -fsSL https://storage.googleapis.com/public-download-production/claude-public/install.sh | sh
```

此脚本将：
1. 下载最新版本的 Claude Code
2. 安装到 `/usr/local/bin/claude`
3. 设置必要的权限
4. 配置环境变量

### 方法 2：使用 Homebrew

```bash
# 添加 Claude Code tap
brew tap anthropic/claude-code

# 安装 Claude Code
brew install claude-code
```

### 方法 3：手动安装

1. 从 [GitHub Releases](https://github.com/anthropics/claude-code/releases) 下载最新版本
2. 解压文件：
   ```bash
   tar -xzf claude-code-macos.tar.gz
   ```
3. 移动到系统路径：
   ```bash
   sudo mv claude /usr/local/bin/
   sudo chmod +x /usr/local/bin/claude
   ```

## 配置 Shell

### Zsh（默认 macOS shell）

添加到 `~/.zshrc`：

```bash
# Claude Code 配置
export PATH="/usr/local/bin:$PATH"

# 可选：设置别名
alias cc="claude"
alias ccode="claude"

# 可选：自动补全
source <(claude completion zsh)
```

### Bash

添加到 `~/.bash_profile`：

```bash
# Claude Code 配置
export PATH="/usr/local/bin:$PATH"

# 可选：设置别名
alias cc="claude"
alias ccode="claude"

# 可选：自动补全
source <(claude completion bash)
```

### Fish

添加到 `~/.config/fish/config.fish`：

```fish
# Claude Code 配置
set -gx PATH /usr/local/bin $PATH

# 可选：设置别名
alias cc="claude"
alias ccode="claude"

# 可选：自动补全
claude completion fish | source
```

## 首次运行

1. 打开终端
2. 运行 `claude` 命令
3. 使用 Anthropic 账号登录
4. 验证安装：
   ```bash
   claude --version
   ```

## 权限设置

如果遇到权限问题：

### 允许终端访问

1. 打开 **系统偏好设置** > **安全性与隐私** > **隐私**
2. 选择 **完全磁盘访问权限**
3. 点击锁图标并输入密码
4. 添加你的终端应用（Terminal.app、iTerm2 等）

### Gatekeeper 问题

如果 macOS 阻止运行：

```bash
# 移除隔离属性
xattr -d com.apple.quarantine /usr/local/bin/claude

# 或允许运行
spctl --add /usr/local/bin/claude
```

## 更新 Claude Code

### 使用内置更新命令

```bash
claude update
```

### 使用 Homebrew

```bash
brew upgrade claude-code
```

### 手动更新

重复安装步骤，新版本将覆盖旧版本。

## 卸载

### 使用 Homebrew

```bash
brew uninstall claude-code
```

### 手动卸载

```bash
# 删除二进制文件
sudo rm /usr/local/bin/claude

# 删除配置文件
rm -rf ~/.claude

# 删除缓存
rm -rf ~/Library/Caches/claude-code
```

## 故障排除

### 常见问题

#### 1. "command not found: claude"

确保 `/usr/local/bin` 在你的 PATH 中：

```bash
echo $PATH
```

如果没有，添加到你的 shell 配置文件。

#### 2. "permission denied"

```bash
sudo chmod +x /usr/local/bin/claude
```

#### 3. SSL 证书错误

```bash
# 更新证书
brew install ca-certificates
```

#### 4. 代理设置

如果使用代理：

```bash
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
claude
```

### 获取帮助

- 运行 `claude help` 查看所有命令
- 访问 [官方文档](https://docs.anthropic.com/claude-code)
- 在 [GitHub Issues](https://github.com/anthropics/claude-code/issues) 报告问题

## 下一步

- 查看[配置指南](configuration.md)了解高级配置
- 阅读[入门教程](../getting-started/first-session.md)开始使用
- 探索[最佳实践](../../README.md#-最佳实践)