# MCP (Model Context Protocol) 完全指南

## 什么是 MCP？

MCP（Model Context Protocol）是 Anthropic 开发的开放协议，允许 Claude Code 与外部工具和服务进行标准化通信。通过 MCP，你可以扩展 Claude Code 的能力，集成数据库、API、云服务等。

## 核心概念

### 1. MCP 服务器

MCP 服务器是提供特定功能的独立进程：

- **工具（Tools）**：可执行的操作，如数据库查询、API 调用
- **资源（Resources）**：可访问的数据，如文件、配置
- **提示（Prompts）**：预定义的交互模板

### 2. 通信协议

MCP 使用 JSON-RPC 2.0 通过 stdio 进行通信：

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "query_database",
    "arguments": {
      "query": "SELECT * FROM users"
    }
  },
  "id": 1
}
```

## 配置 MCP 服务器

### 基本配置

在 `~/.claude/claude.json` 中添加：

```json
{
  "mcp": {
    "servers": [
      {
        "name": "filesystem",
        "command": "npx",
        "args": ["@modelcontextprotocol/server-filesystem"],
        "config": {
          "allowedPaths": [
            "/Users/username/projects",
            "/Users/username/documents"
          ]
        }
      }
    ]
  }
}
```

### 高级配置示例

```json
{
  "mcp": {
    "defaultTimeout": 30000,
    "maxConnections": 10,
    "servers": [
      {
        "name": "postgres-db",
        "command": "python",
        "args": ["./mcp-servers/postgres-server.py"],
        "env": {
          "DATABASE_URL": "postgresql://user:pass@localhost/db",
          "LOG_LEVEL": "DEBUG"
        },
        "config": {
          "maxPoolSize": 20,
          "queryTimeout": 5000,
          "allowedTables": ["users", "products", "orders"]
        },
        "capabilities": {
          "tools": true,
          "resources": true,
          "prompts": false
        }
      },
      {
        "name": "github",
        "command": "node",
        "args": ["./mcp-servers/github-server.js"],
        "env": {
          "GITHUB_TOKEN": "${GITHUB_TOKEN}"
        },
        "config": {
          "defaultBranch": "main",
          "autoMerge": false
        }
      },
      {
        "name": "slack",
        "command": "npx",
        "args": ["@modelcontextprotocol/server-slack"],
        "env": {
          "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
          "SLACK_APP_TOKEN": "${SLACK_APP_TOKEN}"
        }
      }
    ]
  }
}
```

## 官方 MCP 服务器

### 1. Filesystem Server

文件系统操作服务器：

```bash
# 安装
npm install -g @modelcontextprotocol/server-filesystem

# 配置
{
  "name": "filesystem",
  "command": "mcp-server-filesystem",
  "config": {
    "allowedPaths": ["/path/to/project"],
    "watchFiles": true,
    "maxFileSize": "10MB"
  }
}
```

功能：
- 读写文件
- 目录操作
- 文件监视
- 搜索功能

### 2. GitHub Server

GitHub 集成服务器：

```bash
# 安装
npm install -g @modelcontextprotocol/server-github

# 配置
{
  "name": "github",
  "command": "mcp-server-github",
  "env": {
    "GITHUB_TOKEN": "${GITHUB_TOKEN}"
  },
  "config": {
    "repos": ["owner/repo1", "owner/repo2"],
    "scopes": ["repo", "read:org"]
  }
}
```

功能：
- 仓库管理
- Issue 和 PR 操作
- Actions 触发
- 代码搜索

### 3. PostgreSQL Server

数据库操作服务器：

```bash
# 安装
npm install -g @modelcontextprotocol/server-postgres

# 配置
{
  "name": "postgres",
  "command": "mcp-server-postgres",
  "env": {
    "DATABASE_URL": "postgresql://localhost/mydb"
  },
  "config": {
    "readOnly": false,
    "schemas": ["public", "app"]
  }
}
```

### 4. Slack Server

Slack 集成服务器：

```bash
# 安装
npm install -g @modelcontextprotocol/server-slack

# 配置
{
  "name": "slack",
  "command": "mcp-server-slack",
  "env": {
    "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
    "SLACK_APP_TOKEN": "${SLACK_APP_TOKEN}"
  }
}
```

## 创建自定义 MCP 服务器

### Python 示例

```python
#!/usr/bin/env python3
"""
自定义 MCP 服务器示例
"""
import json
import sys
import asyncio
from typing import Any, Dict, List

class CustomMCPServer:
    def __init__(self):
        self.tools = {
            "get_weather": self.get_weather,
            "calculate": self.calculate,
            "search_data": self.search_data
        }
        
    async def get_weather(self, location: str) -> Dict[str, Any]:
        """获取天气信息"""
        # 实现天气 API 调用
        return {
            "location": location,
            "temperature": 22,
            "condition": "晴朗",
            "humidity": 65
        }
    
    async def calculate(self, expression: str) -> float:
        """计算数学表达式"""
        try:
            # 安全地计算表达式
            result = eval(expression, {"__builtins__": {}}, {})
            return result
        except Exception as e:
            raise ValueError(f"计算错误: {e}")
    
    async def search_data(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索数据"""
        # 实现数据搜索逻辑
        results = []
        # ... 搜索实现
        return results
    
    async def handle_request(self, request: Dict) -> Dict:
        """处理 JSON-RPC 请求"""
        method = request.get("method")
        params = request.get("params", {})
        id = request.get("id")
        
        try:
            if method == "initialize":
                return self.initialize_response(id)
            elif method == "tools/list":
                return self.list_tools_response(id)
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                if tool_name in self.tools:
                    result = await self.tools[tool_name](**arguments)
                    return self.success_response(id, result)
                else:
                    return self.error_response(id, f"Unknown tool: {tool_name}")
            else:
                return self.error_response(id, f"Unknown method: {method}")
        except Exception as e:
            return self.error_response(id, str(e))
    
    def initialize_response(self, id: Any) -> Dict:
        """初始化响应"""
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": {
                "protocolVersion": "1.0",
                "capabilities": {
                    "tools": True,
                    "resources": False,
                    "prompts": False
                },
                "serverInfo": {
                    "name": "custom-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    def list_tools_response(self, id: Any) -> Dict:
        """列出可用工具"""
        tools = [
            {
                "name": "get_weather",
                "description": "获取指定地点的天气信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "地点名称"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "calculate",
                "description": "计算数学表达式",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "数学表达式"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "search_data",
                "description": "搜索数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "结果数量限制",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": {"tools": tools}
        }
    
    def success_response(self, id: Any, result: Any) -> Dict:
        """成功响应"""
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }
    
    def error_response(self, id: Any, message: str) -> Dict:
        """错误响应"""
        return {
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": -32603,
                "message": message
            }
        }
    
    async def run(self):
        """运行服务器"""
        while True:
            try:
                # 从 stdin 读取请求
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = await self.handle_request(request)
                
                # 写入响应到 stdout
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                error_response = self.error_response(None, str(e))
                print(json.dumps(error_response))
                sys.stdout.flush()

if __name__ == "__main__":
    server = CustomMCPServer()
    asyncio.run(server.run())
```

### Node.js 示例

```javascript
#!/usr/bin/env node
/**
 * 自定义 MCP 服务器 (Node.js)
 */

const readline = require('readline');

class CustomMCPServer {
  constructor() {
    this.tools = new Map([
      ['fetch_data', this.fetchData.bind(this)],
      ['process_text', this.processText.bind(this)],
      ['generate_report', this.generateReport.bind(this)]
    ]);
    
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: false
    });
  }
  
  async fetchData(params) {
    const { url, headers = {} } = params;
    // 实现数据获取逻辑
    const response = await fetch(url, { headers });
    const data = await response.json();
    return data;
  }
  
  async processText(params) {
    const { text, operation } = params;
    // 实现文本处理逻辑
    switch (operation) {
      case 'uppercase':
        return text.toUpperCase();
      case 'lowercase':
        return text.toLowerCase();
      case 'reverse':
        return text.split('').reverse().join('');
      default:
        throw new Error(`Unknown operation: ${operation}`);
    }
  }
  
  async generateReport(params) {
    const { data, format = 'json' } = params;
    // 实现报告生成逻辑
    if (format === 'json') {
      return JSON.stringify(data, null, 2);
    } else if (format === 'csv') {
      // CSV 转换逻辑
      return this.convertToCSV(data);
    }
    throw new Error(`Unsupported format: ${format}`);
  }
  
  convertToCSV(data) {
    // CSV 转换实现
    if (!Array.isArray(data) || data.length === 0) {
      return '';
    }
    const headers = Object.keys(data[0]);
    const rows = data.map(obj => 
      headers.map(header => obj[header]).join(',')
    );
    return [headers.join(','), ...rows].join('\n');
  }
  
  async handleRequest(request) {
    const { method, params = {}, id } = request;
    
    try {
      switch (method) {
        case 'initialize':
          return this.initializeResponse(id);
          
        case 'tools/list':
          return this.listToolsResponse(id);
          
        case 'tools/call': {
          const { name, arguments: args = {} } = params;
          if (this.tools.has(name)) {
            const result = await this.tools.get(name)(args);
            return this.successResponse(id, result);
          }
          return this.errorResponse(id, `Unknown tool: ${name}`);
        }
        
        default:
          return this.errorResponse(id, `Unknown method: ${method}`);
      }
    } catch (error) {
      return this.errorResponse(id, error.message);
    }
  }
  
  initializeResponse(id) {
    return {
      jsonrpc: '2.0',
      id,
      result: {
        protocolVersion: '1.0',
        capabilities: {
          tools: true,
          resources: false,
          prompts: false
        },
        serverInfo: {
          name: 'custom-node-mcp-server',
          version: '1.0.0'
        }
      }
    };
  }
  
  listToolsResponse(id) {
    const tools = [
      {
        name: 'fetch_data',
        description: '从 URL 获取数据',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: '要获取的 URL'
            },
            headers: {
              type: 'object',
              description: '请求头'
            }
          },
          required: ['url']
        }
      },
      {
        name: 'process_text',
        description: '处理文本',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: '要处理的文本'
            },
            operation: {
              type: 'string',
              enum: ['uppercase', 'lowercase', 'reverse'],
              description: '操作类型'
            }
          },
          required: ['text', 'operation']
        }
      },
      {
        name: 'generate_report',
        description: '生成报告',
        inputSchema: {
          type: 'object',
          properties: {
            data: {
              type: 'array',
              description: '报告数据'
            },
            format: {
              type: 'string',
              enum: ['json', 'csv'],
              default: 'json',
              description: '报告格式'
            }
          },
          required: ['data']
        }
      }
    ];
    
    return {
      jsonrpc: '2.0',
      id,
      result: { tools }
    };
  }
  
  successResponse(id, result) {
    return {
      jsonrpc: '2.0',
      id,
      result
    };
  }
  
  errorResponse(id, message) {
    return {
      jsonrpc: '2.0',
      id,
      error: {
        code: -32603,
        message
      }
    };
  }
  
  start() {
    this.rl.on('line', async (line) => {
      try {
        const request = JSON.parse(line);
        const response = await this.handleRequest(request);
        console.log(JSON.stringify(response));
      } catch (error) {
        const errorResponse = this.errorResponse(null, error.message);
        console.log(JSON.stringify(errorResponse));
      }
    });
  }
}

// 启动服务器
const server = new CustomMCPServer();
server.start();
```

## 社区 MCP 服务器

### 数据库服务器

- **MongoDB MCP Server** - MongoDB 数据库集成
- **MySQL MCP Server** - MySQL 数据库操作
- **Redis MCP Server** - Redis 缓存操作
- **Elasticsearch MCP Server** - 全文搜索功能

### 云服务集成

- **AWS MCP Server** - AWS 服务集成（S3、Lambda、DynamoDB）
- **Azure MCP Server** - Azure 服务集成
- **GCP MCP Server** - Google Cloud Platform 集成

### API 集成

- **OpenAPI MCP Server** - 通用 OpenAPI 集成
- **GraphQL MCP Server** - GraphQL API 集成
- **REST MCP Server** - RESTful API 通用集成

### 开发工具

- **Docker MCP Server** - Docker 容器管理
- **Kubernetes MCP Server** - K8s 集群操作
- **Terraform MCP Server** - 基础设施即代码

## MCP 最佳实践

### 1. 安全性

```json
{
  "mcp": {
    "servers": [
      {
        "name": "database",
        "config": {
          "allowedOperations": ["SELECT", "INSERT", "UPDATE"],
          "deniedTables": ["users_passwords", "api_keys"],
          "maxQueryTime": 5000,
          "readOnly": false
        }
      }
    ]
  }
}
```

### 2. 性能优化

```json
{
  "mcp": {
    "connectionPool": {
      "minSize": 2,
      "maxSize": 10,
      "idleTimeout": 60000
    },
    "cache": {
      "enabled": true,
      "ttl": 300,
      "maxSize": "100MB"
    }
  }
}
```

### 3. 错误处理

```python
async def robust_tool_handler(self, **kwargs):
    """带有完整错误处理的工具处理器"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            # 验证参数
            self.validate_params(kwargs)
            
            # 执行操作
            result = await self.execute_operation(**kwargs)
            
            # 验证结果
            self.validate_result(result)
            
            return result
            
        except ValidationError as e:
            # 参数验证失败，不重试
            raise
            
        except TemporaryError as e:
            # 临时错误，重试
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
                continue
            raise
            
        except Exception as e:
            # 记录错误
            self.log_error(e, kwargs)
            raise
```

### 4. 监控和日志

```javascript
class MonitoredMCPServer {
  constructor() {
    this.metrics = {
      requests: 0,
      errors: 0,
      latency: []
    };
  }
  
  async handleRequest(request) {
    const startTime = Date.now();
    this.metrics.requests++;
    
    try {
      const response = await super.handleRequest(request);
      
      // 记录延迟
      const latency = Date.now() - startTime;
      this.metrics.latency.push(latency);
      
      // 记录请求
      this.logRequest(request, response, latency);
      
      return response;
    } catch (error) {
      this.metrics.errors++;
      this.logError(request, error);
      throw error;
    }
  }
  
  logRequest(request, response, latency) {
    console.error(JSON.stringify({
      timestamp: new Date().toISOString(),
      type: 'request',
      method: request.method,
      latency,
      success: !response.error
    }));
  }
  
  logError(request, error) {
    console.error(JSON.stringify({
      timestamp: new Date().toISOString(),
      type: 'error',
      method: request.method,
      error: error.message,
      stack: error.stack
    }));
  }
}
```

## 调试 MCP 服务器

### 启用调试日志

```bash
# 设置环境变量
export MCP_DEBUG=true
export MCP_LOG_LEVEL=debug

# 启动 Claude Code
claude
```

### 测试 MCP 服务器

```bash
# 手动测试 MCP 服务器
echo '{"jsonrpc":"2.0","method":"initialize","id":1}' | python mcp-server.py

# 使用测试工具
mcp-test --server ./mcp-server.py --test-file ./tests.json
```

### 常见问题排查

1. **服务器无法启动**
   - 检查命令路径是否正确
   - 验证依赖是否安装
   - 查看错误日志

2. **工具调用失败**
   - 验证参数格式
   - 检查权限设置
   - 确认服务可用性

3. **性能问题**
   - 优化查询和操作
   - 使用连接池
   - 实现缓存机制

## 资源和文档

- [MCP 协议规范](https://modelcontextprotocol.io/docs)
- [MCP SDK 文档](https://github.com/anthropics/mcp-sdk)
- [服务器示例](https://github.com/anthropics/mcp-servers)
- [社区论坛](https://community.modelcontextprotocol.io)

## 下一步

- 探索[官方 MCP 服务器](../mcp/filesystem.md)
- 学习[创建自定义服务器](../mcp/development.md)
- 查看[真实案例](../case-studies/mcp-integration.md)