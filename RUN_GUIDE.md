# 🚀 运行指南 - Course Materials RAG System

## 📋 运行前检查清单

### ✅ 1. 确认 Python 版本
```bash
python --version
```
**要求**: Python 3.13 或更高版本

如果版本不符合，请安装 [Python 3.13+](https://www.python.org/downloads/)

### ✅ 2. 安装 uv 包管理器
```bash
# 使用 PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# 或使用 curl（Windows 10+）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

验证安装：
```bash
uv --version
```

### ✅ 3. 检查 API Key 配置
`.env` 文件已配置：
```
ZHIPU_API_KEY=bcafaf9d4d5f43cea4f9e3fd98b4a81c.57JT9ghmIrNf19aQ
```

---

## 🎯 运行步骤

### 方法1: 使用启动脚本（推荐）

#### Windows PowerShell:
```powershell
# 进入项目目录
cd e:\github_project\STARTING_CODEBASE\starting_ragchatbot_codebase

# 方式1: 使用 Git Bash（如果已安装）
bash run.sh

# 方式2: 直接运行（见方法2）
```

#### Windows CMD:
```cmd
cd e:\github_project\STARTING_CODEBASE\starting_ragchatbot_codebase
bash run.sh
```

---

### 方法2: 手动启动（Windows 原生）

#### 步骤1: 安装依赖
```bash
# 在项目根目录执行
uv sync
```

**预期输出**:
```
Resolved packages in X秒
Installed packages in X秒
```

#### 步骤2: 启动后端服务
```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

**预期输出**:
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
Loading initial documents...
Added new course: Building Towards Computer Use with Anthropic (X chunks)
Added new course: MCP: Build Rich-Context AI Apps (X chunks)
...
Loaded X courses with X chunks
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🌐 访问应用

启动成功后，在浏览器中访问：

### 主界面
```
http://localhost:8000
```

### API 文档（Swagger UI）
```
http://localhost:8000/docs
```

### 课程统计 API
```
http://localhost:8000/api/courses
```

---

## 🧪 测试查询

### 方式1: 通过 Web 界面
1. 打开 http://localhost:8000
2. 在输入框输入问题，例如：
   - "什么是 RAG?"
   - "MCP 课程讲了什么？"
   - "有哪些课程？"
3. 点击发送按钮或按 Enter

### 方式2: 通过 API（使用 curl）
```bash
curl -X POST http://localhost:8000/api/query ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"什么是 RAG?\", \"session_id\": null}"
```

### 方式3: 通过 API（使用 PowerShell）
```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8000/api/query" `
  -ContentType "application/json" `
  -Body '{"query": "什么是 RAG?", "session_id": null}'
```

---

## 🔍 常见问题排查

### 问题1: 端口被占用
**错误信息**:
```
ERROR: [Errno 48] Address already in use
```

**解决方案**:
```bash
# 方法1: 更换端口
uv run uvicorn app:app --reload --port 8001

# 方法2: 杀死占用进程
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

---

### 问题2: Python 版本不兼容
**错误信息**:
```
TypeError: argument of type 'NoneType' is not iterable
```

**解决方案**:
```bash
# 安装 Python 3.13+
# 下载地址: https://www.python.org/downloads/

# 验证版本
python --version
```

---

### 问题3: uv 命令未找到
**错误信息**:
```
'uv' is not recognized as an internal or external command
```

**解决方案**:
```bash
# 重新安装 uv
irm https://astral.sh/uv/install.ps1 | iex

# 或使用 pip（不推荐，但可以工作）
pip install chromadb anthropic sentence-transformers fastapi uvicorn python-multipart python-dotenv zhipuai
```

---

### 问题4: 依赖安装失败
**错误信息**:
```
Failed to download packages
```

**解决方案**:
```bash
# 清除缓存重试
uv cache clean
uv sync

# 或配置国内镜像（如果网络慢）
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
uv sync
```

---

### 问题5: 智谱 API 调用失败
**错误信息**:
```
Error: Query failed
```

**排查步骤**:
```bash
# 1. 检查 .env 文件
cat .env

# 2. 检查 API Key 格式
ZHIPU_API_KEY=id.secret
# 例如: bcafaf9d4d5f43cea4f9e3fd98b4a81c.57JT9ghmIrNf19aQ

# 3. 测试 API 连接
curl https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-4-flash","messages":[{"role":"user","content":"hi"}]}'
```

---

### 问题6: ChromaDB 初始化失败
**错误信息**:
```
Search error: No courses found
```

**解决方案**:
```bash
# 检查文档是否存在
ls -la docs/

# 检查 ChromaDB 目录
ls -la chroma_db/

# 重新启动服务（会自动加载文档）
# 查看日志: "Loaded X courses with X chunks"
```

---

### 问题7: 前端无法连接后端
**症状**: 页面显示但发送消息无响应

**排查步骤**:
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/api/courses

# 2. 检查浏览器控制台（F12）
# 查看 Network 面板是否有请求发出

# 3. 检查 CORS 配置
# backend/app.py 中已配置:
# allow_origins=["*"]
```

---

## 📊 启动成功标志

当你看到以下输出时，说明启动成功：

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
Loading initial documents...
Added new course: Building Towards Computer Use with Anthropic (23 chunks)
Added new course: MCP: Build Rich-Context AI Apps (31 chunks)
Added new course: LangChain for LLM Application Development (18 chunks)
Added new course: Prompt Engineering for LLMs (27 chunks)
Loaded 4 courses with 99 chunks
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**关键点**:
- ✅ "Loaded X courses with X chunks" - 文档已加载
- ✅ "Uvicorn running on http://0.0.0.0:8000" - 服务已启动
- ✅ 无 ERROR 级别的日志

---

## 🛑 停止服务

在运行服务的终端窗口中：
```
按 Ctrl + C
```

---

## 🔄 重新启动

```bash
# 停止服务（Ctrl+C）
# 重新执行启动命令
cd backend
uv run uvicorn app:app --reload --port 8000
```

**注**: `--reload` 参数会自动检测代码变化并重新加载，修改代码后无需手动重启。

---

## 📁 项目目录结构

```
starting_ragchatbot_codebase/
├── backend/              # 后端代码
│   ├── app.py           # FastAPI 应用入口
│   ├── rag_system.py    # RAG 核心逻辑
│   └── ...
├── frontend/            # 前端代码
│   ├── index.html       # 主页面
│   ├── script.js        # 前端逻辑
│   └── style.css        # 样式
├── docs/                # 课程文档
│   ├── course1_script.txt
│   ├── course2_script.txt
│   ├── course3_script.txt
│   └── course4_script.txt
├── .env                 # 环境变量（API Key）
├── run.sh              # 启动脚本（Linux/Mac）
└── pyproject.toml      # Python 依赖配置
```

---

## 🎯 下一步

1. **测试基本功能**: 访问 http://localhost:8000
2. **查看 API 文档**: 访问 http://localhost:8000/docs
3. **测试查询**: 输入"有哪些课程？"
4. **查看日志**: 观察终端输出的调试信息

---

## 💡 开发模式

如果你想修改代码并实时看到效果：

```bash
# 使用 --reload 参数（已包含在启动命令中）
uv run uvicorn app:app --reload --port 8000
```

修改以下文件会自动重新加载：
- `backend/*.py` - 后端代码
- `frontend/*` - 前端代码（静态文件）

---

## 📞 获取帮助

如果遇到其他问题：

1. **查看日志**: 终端输出的错误信息
2. **浏览器控制台**: 按 F12 查看 Console 和 Network 面板
3. **API 文档**: http://localhost:8000/docs
4. **依赖版本**: `uv pip list` 查看已安装的包

---

## ✅ 快速启动命令（复制粘贴）

```bash
# PowerShell 一键启动
cd e:\github_project\STARTING_CODEBASE\starting_ragchatbot_codebase; uv sync; cd backend; uv run uvicorn app:app --reload --port 8000

# CMD 分步启动
cd e:\github_project\STARTING_CODEBASE\starting_ragchatbot_codebase
uv sync
cd backend
uv run uvicorn app:app --reload --port 8000
```

启动成功后，打开浏览器访问: **http://localhost:8000** 🎉
