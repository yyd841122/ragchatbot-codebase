# Course Materials RAG System

A Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.

## Overview

This application is a full-stack web application that enables users to query course materials and receive intelligent, context-aware responses. It uses ChromaDB for vector storage, Zhipu AI (GLM-4-Flash) for AI generation, and provides a web interface for interaction.

## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- A Zhipu AI API key (for GLM-4-Flash model)
- **For Windows**: Use Git Bash to run the application commands - [Download Git for Windows](https://git-scm.com/downloads/win)

## Installation

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

## Running the Application

### Quick Start

Use the provided shell script:
```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

The application will be available at:
- Web Interface: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## Development Tools

### Code Quality

This project includes automated code quality tools:

```bash
# Format code
python scripts/format.py

# Run quality checks
python scripts/check_quality.py

# Or use the convenience scripts (Windows)
scripts\dev.bat format
scripts\dev.bat check

# Or use the convenience scripts (Linux/Mac)
bash scripts/dev.sh format
bash scripts/dev.sh check
```

**Tools included:**
- **Black**: Code formatter (line length: 100 chars)
- **isort**: Import statement organizer
- **Flake8**: Code style checker

For detailed usage, see [docs/CODE_QUALITY.md](docs/CODE_QUALITY.md).

### Testing

Run the test suite:
```bash
cd backend
uv run pytest -v
```

### Pre-commit Hooks (Optional)

Install pre-commit hooks for automatic quality checks:
```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks
pre-commit install

# Now hooks will run automatically on each commit
```

## 🤖 Zhipu Fix Plan

### 问题理解
验证 Stage 8.1 修复后，对 README.md 文件进行最小必要修改，确保不破坏原有结构。

### 计划修改文件
- `README.md` - 在文件中添加一个简单的测试章节

### Todo List
- [ ] [第一步] - 在 README.md 文件中找到合适的位置添加测试章节标题，例如 "测试章节"
- [ ] [第二步] - 在测试章节下添加至少一个测试用例，例如 "测试用例1: 检查文件是否存在"
- [ ] [第三步] - 确保测试用例的描述简洁明了，不包含测试说明、执行计划、Zhipu Fix Plan 等内容
- [ ] [第四步] - 检查添加的测试章节是否破坏了 README.md 的原有标题结构和格式
- [ ] [第五步] - 保存修改并提交更改，确保提交信息描述了本次修改的目的

### 风险提示
- [可能的风险点1] - 添加测试章节时可能破坏 README.md 的原有格式
- [可能的风险点2] - 测试用例描述可能过于详细，违反了预期结果

### 下一步
💡 评论 `/zhipu-apply` 可进入执行阶段（第二阶段功能，敬请期待）