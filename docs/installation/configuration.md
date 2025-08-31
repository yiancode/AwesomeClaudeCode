# Claude Code 配置指南

## 配置文件层级

Claude Code 支持多层配置，优先级从高到低：

1. **命令行参数** - 直接在命令中指定
2. **项目配置** - `.claude/claude.json` 或 `.cloderc`
3. **用户配置** - `~/.claude/config.json`
4. **全局指令** - `~/.claude/CLAUDE.md`
5. **系统默认** - 内置默认值

## 项目级配置

### `.claude/claude.json`

项目根目录下的配置文件：

```json
{
  "version": "1.0",
  "language": "zh-CN",
  "editor": {
    "defaultEditor": "vscode",
    "autoSave": true,
    "formatOnSave": true
  },
  "context": {
    "maxTokens": 100000,
    "includePatterns": ["**/*.js", "**/*.ts"],
    "excludePatterns": ["node_modules/**", "dist/**"]
  },
  "tools": {
    "bash": {
      "enabled": true,
      "allowedCommands": ["npm", "yarn", "git", "docker"]
    },
    "web": {
      "enabled": true,
      "timeout": 30000
    }
  },
  "hooks": {
    "preCommit": "npm test",
    "postEdit": "npm run lint"
  },
  "mcp": {
    "servers": [
      {
        "name": "filesystem",
        "enabled": true,
        "config": {
          "allowedPaths": ["./src", "./tests"]
        }
      }
    ]
  }
}
```

### `.cloderc`

简化的 YAML 配置格式：

```yaml
# Claude Code 项目配置
version: 1.0
language: zh-CN

# 编辑器设置
editor:
  defaultEditor: vscode
  autoSave: true
  formatOnSave: true
  tabSize: 2
  useTabs: false

# 上下文管理
context:
  maxTokens: 100000
  includePatterns:
    - "**/*.js"
    - "**/*.ts"
    - "**/*.jsx"
    - "**/*.tsx"
  excludePatterns:
    - "node_modules/**"
    - "dist/**"
    - "coverage/**"
    - ".git/**"

# 工具配置
tools:
  bash:
    enabled: true
    defaultShell: /bin/zsh
    timeout: 120000
  
  web:
    enabled: true
    userAgent: "Claude-Code/1.0"
    
  task:
    autoTrack: true
    showProgress: true

# Git 集成
git:
  autoStage: false
  commitTemplate: |
    feat: [description]
    
    [detailed explanation]
    
    Co-authored-by: Claude <claude@anthropic.com>
  
# 测试配置
testing:
  framework: jest
  autoRun: true
  coverage: true
  watchMode: false
```

## 用户级配置

### `~/.claude/config.json`

全局用户配置：

```json
{
  "user": {
    "name": "Your Name",
    "email": "you@example.com",
    "preferredLanguage": "zh-CN"
  },
  "appearance": {
    "theme": "dark",
    "fontSize": 14,
    "fontFamily": "JetBrains Mono"
  },
  "behavior": {
    "autoUpdate": true,
    "telemetry": true,
    "confirmBeforeRun": false,
    "verboseOutput": false
  },
  "shortcuts": {
    "runTests": "cmd+shift+t",
    "format": "cmd+shift+f",
    "commit": "cmd+k"
  },
  "integrations": {
    "vscode": {
      "enabled": true,
      "extensionPath": "/path/to/extension"
    },
    "github": {
      "token": "${GITHUB_TOKEN}",
      "defaultBranch": "main"
    }
  }
}
```

## 全局指令文件

### `~/.claude/CLAUDE.md`

Markdown 格式的全局指令，用于定义 Claude 的行为准则：

```markdown
# Claude Code 全局指令

## 语言偏好
- 始终使用简体中文回复
- 代码注释使用英文
- 错误信息保持原文

## 编码规范
- 使用 2 空格缩进
- 使用 ESLint 和 Prettier
- 遵循 Airbnb JavaScript 风格指南
- 函数不超过 50 行
- 类不超过 200 行

## 开发流程
1. 理解需求
2. 编写测试
3. 实现功能
4. 重构优化
5. 文档更新

## 安全准则
- 不在代码中硬编码密钥
- 使用环境变量管理敏感信息
- 定期更新依赖
- 进行安全审计

## 性能要求
- 响应时间 < 200ms
- 内存使用 < 512MB
- 代码覆盖率 > 80%
```

## 环境变量

支持的环境变量：

```bash
# API 配置
export ANTHROPIC_API_KEY="your-api-key"
export CLAUDE_API_URL="https://api.anthropic.com"

# 代理设置
export HTTP_PROXY="http://proxy:8080"
export HTTPS_PROXY="http://proxy:8080"
export NO_PROXY="localhost,127.0.0.1"

# 路径配置
export CLAUDE_HOME="$HOME/.claude"
export CLAUDE_CONFIG_PATH="$HOME/.claude/config.json"
export CLAUDE_WORKSPACE="/path/to/workspace"

# 功能开关
export CLAUDE_TELEMETRY="false"
export CLAUDE_AUTO_UPDATE="true"
export CLAUDE_DEBUG="true"

# MCP 配置
export MCP_SERVER_PATH="/path/to/mcp/servers"
export MCP_TIMEOUT="30000"

# 编辑器集成
export EDITOR="code"
export VISUAL="code"
```

## MCP 服务器配置

### 基本配置

```json
{
  "mcp": {
    "servers": [
      {
        "name": "filesystem",
        "command": "npx",
        "args": ["@modelcontextprotocol/server-filesystem"],
        "config": {
          "allowedPaths": ["/path/to/project"]
        }
      },
      {
        "name": "github",
        "command": "npx",
        "args": ["@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_TOKEN": "${GITHUB_TOKEN}"
        }
      }
    ]
  }
}
```

### 高级 MCP 配置

```json
{
  "mcp": {
    "defaultTimeout": 30000,
    "maxConnections": 5,
    "autoReconnect": true,
    "servers": [
      {
        "name": "custom-db",
        "command": "python",
        "args": ["./mcp-servers/db-server.py"],
        "config": {
          "database": "postgresql://localhost/mydb",
          "poolSize": 10
        },
        "env": {
          "DB_PASSWORD": "${DB_PASSWORD}"
        },
        "capabilities": {
          "tools": true,
          "resources": true,
          "prompts": false
        }
      }
    ]
  }
}
```

## Hooks 配置

### 可用的 Hooks

```json
{
  "hooks": {
    "preStart": "echo 'Starting Claude Code session'",
    "postStart": "git pull",
    "preEdit": "npm run lint",
    "postEdit": "npm run format",
    "preCommit": "npm test",
    "postCommit": "git push",
    "preTest": "npm run build",
    "postTest": "npm run coverage",
    "onError": "npm run debug",
    "onExit": "echo 'Session ended'"
  }
}
```

### Hook 脚本示例

创建 `.claude/hooks/pre-commit.sh`：

```bash
#!/bin/bash
# 运行测试
npm test
if [ $? -ne 0 ]; then
  echo "Tests failed, aborting commit"
  exit 1
fi

# 运行 linter
npm run lint
if [ $? -ne 0 ]; then
  echo "Linting failed, aborting commit"
  exit 1
fi

# 检查代码覆盖率
coverage=$(npm run coverage --silent | grep "All files" | awk '{print $10}' | sed 's/%//')
if [ "$coverage" -lt 80 ]; then
  echo "Code coverage is below 80%, aborting commit"
  exit 1
fi

echo "Pre-commit checks passed!"
```

## 性能优化配置

```json
{
  "performance": {
    "cache": {
      "enabled": true,
      "maxSize": "500MB",
      "ttl": 3600
    },
    "context": {
      "maxTokens": 100000,
      "compressionLevel": 5,
      "lazyLoading": true
    },
    "parallel": {
      "maxWorkers": 4,
      "taskQueue": 10
    },
    "memory": {
      "maxHeapSize": "2GB",
      "gcInterval": 300
    }
  }
}
```

## 安全配置

```json
{
  "security": {
    "sandbox": {
      "enabled": true,
      "allowedDomains": ["github.com", "npmjs.com"],
      "blockedCommands": ["rm -rf", "sudo", "chmod 777"]
    },
    "secrets": {
      "scanEnabled": true,
      "patterns": [
        "api[_-]?key",
        "secret",
        "password",
        "token"
      ],
      "vaultPath": "~/.claude/vault"
    },
    "audit": {
      "enabled": true,
      "logPath": "~/.claude/audit.log",
      "retention": 30
    }
  }
}
```

## 配置验证

验证配置文件：

```bash
# 验证配置语法
claude config validate

# 查看当前配置
claude config show

# 查看特定配置项
claude config get editor.defaultEditor

# 设置配置项
claude config set editor.tabSize 4

# 重置为默认配置
claude config reset
```

## 配置最佳实践

### 1. 使用环境变量管理敏感信息

```json
{
  "github": {
    "token": "${GITHUB_TOKEN}"
  }
}
```

### 2. 项目特定配置

每个项目应有自己的 `.claude/claude.json`：

```json
{
  "project": {
    "type": "node",
    "framework": "express",
    "testCommand": "npm test",
    "buildCommand": "npm run build"
  }
}
```

### 3. 团队共享配置

创建 `.claude/team-config.json`：

```json
{
  "team": {
    "codeStyle": "airbnb",
    "commitConvention": "conventional",
    "reviewRequired": true
  }
}
```

### 4. 配置继承

```json
{
  "extends": "./base-config.json",
  "overrides": {
    "editor": {
      "tabSize": 4
    }
  }
}
```

## 故障排除

### 配置不生效

1. 检查配置文件语法
2. 确认文件路径正确
3. 检查优先级顺序
4. 运行 `claude config validate`

### 性能问题

调整性能相关配置：

```json
{
  "performance": {
    "context": {
      "maxTokens": 50000
    },
    "cache": {
      "enabled": false
    }
  }
}
```

### 获取帮助

- 运行 `claude config help`
- 查看[官方配置文档](https://docs.anthropic.com/claude-code/configuration)
- 在 [Discord](https://discord.gg/anthropic) 寻求帮助