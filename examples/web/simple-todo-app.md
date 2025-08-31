# 简单的 Todo 应用案例

这个案例展示如何使用 Claude Code 从零开始创建一个简单的 Web Todo 应用。

## 项目概述

我们将创建一个包含以下功能的 Todo 应用：

- ✅ 添加新任务
- ✅ 删除任务
- ✅ 标记任务完成
- ✅ 任务过滤（全部、已完成、未完成）
- ✅ 数据持久化（localStorage）

## 技术栈

- **前端**：HTML5 + CSS3 + JavaScript (Vanilla)
- **样式**：CSS Grid + Flexbox
- **存储**：localStorage
- **构建工具**：无需构建工具，纯静态文件

## 与 Claude Code 的对话示例

### 步骤 1：初始化项目

```
You: 帮我创建一个简单的 Todo Web 应用项目结构，使用原生 HTML、CSS、JavaScript

Claude: 我来帮你创建一个简单的 Todo 应用项目。让我先创建基本的项目结构。

📁 创建项目结构...
📝 创建 index.html - 主页面
🎨 创建 style.css - 样式文件  
💻 创建 script.js - JavaScript 逻辑
📖 创建 README.md - 项目说明
```

### 步骤 2：实现基本 HTML 结构

```
You: 创建一个现代化的 HTML 结构，包含输入框、任务列表和过滤按钮

Claude: 我来创建一个现代化的 HTML 结构，包含所有必要的元素。

🔧 Using tool: Write
📝 Creating: index.html
```

### 步骤 3：添加样式

```
You: 为这个 Todo 应用添加美观的 CSS 样式，使用现代的设计

Claude: 我来为 Todo 应用创建现代化的 CSS 样式。

🔧 Using tool: Write  
🎨 Creating: style.css
```

### 步骤 4：实现 JavaScript 功能

```
You: 实现所有的 JavaScript 功能，包括添加、删除、完成任务和数据持久化

Claude: 我来实现完整的 JavaScript 功能，包括所有交互和数据持久化。

🔧 Using tool: Write
💻 Creating: script.js
```

### 步骤 5：测试应用

```
You: 帮我测试这个应用是否工作正常

Claude: 我来帮你测试这个 Todo 应用。让我创建一个简单的测试页面来验证所有功能。

🔧 Using tool: Bash
🧪 打开本地服务器测试...
```

## 完整代码示例

### index.html

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Todo App</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1 class="title">📝 我的待办事项</h1>
        </header>
        
        <main class="main">
            <form class="todo-form" id="todoForm">
                <input 
                    type="text" 
                    id="todoInput" 
                    class="todo-input" 
                    placeholder="输入新的待办事项..."
                    required
                >
                <button type="submit" class="add-btn">
                    ➕ 添加
                </button>
            </form>
            
            <div class="filters">
                <button class="filter-btn active" data-filter="all">
                    全部 (<span id="allCount">0</span>)
                </button>
                <button class="filter-btn" data-filter="active">
                    未完成 (<span id="activeCount">0</span>)
                </button>
                <button class="filter-btn" data-filter="completed">
                    已完成 (<span id="completedCount">0</span>)
                </button>
            </div>
            
            <ul class="todo-list" id="todoList">
                <!-- 动态生成的待办事项 -->
            </ul>
            
            <div class="empty-state" id="emptyState">
                <p>🎉 暂无待办事项</p>
                <p>添加一些任务来开始使用吧！</p>
            </div>
        </main>
    </div>
    
    <script src="script.js"></script>
</body>
</html>
```

### style.css

```css
/* 现代化的 Todo 应用样式 */
:root {
    --primary-color: #667eea;
    --primary-dark: #5a6fd8;
    --success-color: #48bb78;
    --danger-color: #f56565;
    --warning-color: #ed8936;
    --gray-100: #f7fafc;
    --gray-200: #edf2f7;
    --gray-300: #e2e8f0;
    --gray-500: #a0aec0;
    --gray-700: #4a5568;
    --gray-800: #2d3748;
    --white: #ffffff;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --radius: 8px;
    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: var(--font-family);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: var(--gray-800);
    line-height: 1.6;
}

.container {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.header {
    text-align: center;
    margin-bottom: 2rem;
}

.title {
    color: var(--white);
    font-size: 2.5rem;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 0.5rem;
}

.main {
    background: var(--white);
    border-radius: var(--radius);
    box-shadow: var(--shadow-lg);
    padding: 2rem;
}

.todo-form {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 2rem;
}

.todo-input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 2px solid var(--gray-200);
    border-radius: var(--radius);
    font-size: 1rem;
    transition: border-color 0.2s ease;
}

.todo-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.add-btn {
    padding: 0.75rem 1.5rem;
    background: var(--primary-color);
    color: var(--white);
    border: none;
    border-radius: var(--radius);
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.add-btn:hover {
    background: var(--primary-dark);
}

.filters {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
}

.filter-btn {
    padding: 0.5rem 1rem;
    background: var(--gray-100);
    border: 2px solid transparent;
    border-radius: var(--radius);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.filter-btn:hover {
    background: var(--gray-200);
}

.filter-btn.active {
    background: var(--primary-color);
    color: var(--white);
    border-color: var(--primary-color);
}

.todo-list {
    list-style: none;
    space-y: 0.5rem;
}

.todo-item {
    display: flex;
    align-items: center;
    padding: 1rem;
    background: var(--gray-50);
    border-radius: var(--radius);
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
    border-left: 4px solid transparent;
}

.todo-item:hover {
    box-shadow: var(--shadow);
    transform: translateY(-1px);
}

.todo-item.completed {
    border-left-color: var(--success-color);
    opacity: 0.7;
}

.todo-checkbox {
    margin-right: 0.75rem;
    width: 1.25rem;
    height: 1.25rem;
    accent-color: var(--success-color);
}

.todo-text {
    flex: 1;
    font-size: 1rem;
    transition: all 0.2s ease;
}

.todo-item.completed .todo-text {
    text-decoration: line-through;
    color: var(--gray-500);
}

.delete-btn {
    padding: 0.5rem;
    background: var(--danger-color);
    color: var(--white);
    border: none;
    border-radius: var(--radius);
    cursor: pointer;
    font-size: 0.875rem;
    transition: all 0.2s ease;
}

.delete-btn:hover {
    background: #e53e3e;
    transform: scale(1.05);
}

.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--gray-500);
    display: none;
}

.empty-state p {
    margin-bottom: 0.5rem;
}

.empty-state p:first-child {
    font-size: 2rem;
    margin-bottom: 1rem;
}

/* 响应式设计 */
@media (max-width: 640px) {
    .container {
        padding: 1rem 0.5rem;
    }
    
    .title {
        font-size: 2rem;
    }
    
    .main {
        padding: 1.5rem;
    }
    
    .todo-form {
        flex-direction: column;
    }
    
    .filters {
        justify-content: stretch;
    }
    
    .filter-btn {
        flex: 1;
        text-align: center;
    }
}

/* 动画效果 */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.todo-item {
    animation: slideIn 0.3s ease;
}
```

### script.js

```javascript
/**
 * Simple Todo App
 * 使用原生 JavaScript 实现的待办事项应用
 */

class TodoApp {
    constructor() {
        this.todos = this.loadTodos();
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.render();
        this.updateCounts();
    }

    setupEventListeners() {
        // 表单提交事件
        const form = document.getElementById('todoForm');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTodo();
        });

        // 过滤按钮事件
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setFilter(e.target.dataset.filter);
            });
        });
    }

    addTodo() {
        const input = document.getElementById('todoInput');
        const text = input.value.trim();
        
        if (!text) return;

        const todo = {
            id: Date.now().toString(),
            text: text,
            completed: false,
            createdAt: new Date().toISOString()
        };

        this.todos.unshift(todo);
        this.saveTodos();
        this.render();
        this.updateCounts();
        
        input.value = '';
        input.focus();
    }

    deleteTodo(id) {
        this.todos = this.todos.filter(todo => todo.id !== id);
        this.saveTodos();
        this.render();
        this.updateCounts();
    }

    toggleTodo(id) {
        const todo = this.todos.find(todo => todo.id === id);
        if (todo) {
            todo.completed = !todo.completed;
            this.saveTodos();
            this.render();
            this.updateCounts();
        }
    }

    setFilter(filter) {
        this.currentFilter = filter;
        
        // 更新过滤按钮状态
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        
        this.render();
    }

    getFilteredTodos() {
        switch (this.currentFilter) {
            case 'active':
                return this.todos.filter(todo => !todo.completed);
            case 'completed':
                return this.todos.filter(todo => todo.completed);
            default:
                return this.todos;
        }
    }

    render() {
        const todoList = document.getElementById('todoList');
        const emptyState = document.getElementById('emptyState');
        const filteredTodos = this.getFilteredTodos();

        if (filteredTodos.length === 0) {
            todoList.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }

        todoList.style.display = 'block';
        emptyState.style.display = 'none';

        todoList.innerHTML = filteredTodos.map(todo => `
            <li class="todo-item ${todo.completed ? 'completed' : ''}">
                <input 
                    type="checkbox" 
                    class="todo-checkbox"
                    ${todo.completed ? 'checked' : ''}
                    onchange="todoApp.toggleTodo('${todo.id}')"
                >
                <span class="todo-text">${this.escapeHtml(todo.text)}</span>
                <button 
                    class="delete-btn"
                    onclick="todoApp.deleteTodo('${todo.id}')"
                    title="删除任务"
                >
                    🗑️ 删除
                </button>
            </li>
        `).join('');
    }

    updateCounts() {
        const allCount = this.todos.length;
        const activeCount = this.todos.filter(todo => !todo.completed).length;
        const completedCount = this.todos.filter(todo => todo.completed).length;

        document.getElementById('allCount').textContent = allCount;
        document.getElementById('activeCount').textContent = activeCount;
        document.getElementById('completedCount').textContent = completedCount;
    }

    loadTodos() {
        try {
            const stored = localStorage.getItem('simple-todos');
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            console.error('Failed to load todos:', e);
            return [];
        }
    }

    saveTodos() {
        try {
            localStorage.setItem('simple-todos', JSON.stringify(this.todos));
        } catch (e) {
            console.error('Failed to save todos:', e);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 导出数据
    exportData() {
        const data = {
            todos: this.todos,
            exportDate: new Date().toISOString(),
            version: '1.0'
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `todos-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // 导入数据
    importData(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (data.todos && Array.isArray(data.todos)) {
                    this.todos = data.todos;
                    this.saveTodos();
                    this.render();
                    this.updateCounts();
                    alert('数据导入成功！');
                } else {
                    throw new Error('Invalid data format');
                }
            } catch (error) {
                alert('导入失败：文件格式不正确');
                console.error('Import error:', error);
            }
        };
        reader.readAsText(file);
    }
}

// 初始化应用
const todoApp = new TodoApp();

// 全局方法，供 HTML 调用
window.todoApp = todoApp;

// 键盘快捷键支持
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter 快速添加任务
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const input = document.getElementById('todoInput');
        if (document.activeElement === input) {
            todoApp.addTodo();
        }
    }
});

// 页面可见性变化时保存数据
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
        todoApp.saveTodos();
    }
});
```

## 运行和测试

### 本地运行

```bash
# 创建本地服务器（可选，直接打开 index.html 也可以）
python -m http.server 8000
# 或
npx serve .
```

访问 `http://localhost:8000`

### 功能测试

1. ✅ **添加任务**：在输入框中输入任务，点击添加按钮
2. ✅ **完成任务**：点击复选框标记任务完成
3. ✅ **删除任务**：点击删除按钮移除任务
4. ✅ **过滤显示**：点击过滤按钮查看不同状态的任务
5. ✅ **数据持久化**：刷新页面数据仍然存在

## 扩展功能建议

### 与 Claude Code 继续开发

```
You: 为这个 Todo 应用添加以下功能：
1. 任务编辑功能
2. 截止日期设置
3. 优先级标记
4. 任务分类

Claude: 我来为你的 Todo 应用添加这些高级功能...
```

### 可能的改进

- 📱 响应式设计优化
- 🎨 主题切换（深色/浅色模式）
- 📂 任务分组和标签
- 🔔 提醒和通知
- ☁️ 云同步功能
- 📊 统计和报表
- 🔍 搜索和排序
- 📱 PWA 支持

## 学习收获

通过这个案例，你可以学到：

1. **与 Claude Code 协作**：如何有效地与 AI 助手交互
2. **项目组织**：良好的文件结构和代码组织
3. **现代 Web 开发**：HTML5 语义化、CSS3 特性、ES6+ JavaScript
4. **用户体验**：响应式设计、动画效果、键盘支持
5. **数据管理**：本地存储、状态管理、数据导入导出

## 相关资源

- [MDN Web 文档](https://developer.mozilla.org/)
- [Can I Use](https://caniuse.com/)
- [CSS Grid 指南](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [JavaScript 最佳实践](https://github.com/airbnb/javascript)

---

💡 **提示**：这个案例演示了如何与 Claude Code 协作开发一个完整的 Web 应用。你可以基于这个基础继续添加更多功能！