# Course Materials RAG System

A Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.

## Overview

This application is a full-stack web application that enables users to query course materials and receive intelligent, context-aware responses. It uses ChromaDB for vector storage, Anthropic's Claude for AI generation, and provides a web interface for interaction.

## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- An Anthropic API key (for Claude AI)
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
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
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
测试 Stage 6 的功能，确保 Step 1 正常，Step 5 成功修改 README.md 并创建 commit，Step 6 成功创建 Draft PR，并在 Issue 和 Pull Requests 页面显示成功信息。

### 计划修改文件
- README.md - [修改 README.md 文件内容，以便验证 Step 5 和 Step 6]

### Todo List
- [ ] [第一步] - 运行测试 Stage 6，确保 Step 1 正常
- [ ] [第二步] - 检查 README.md 文件内容，确认 Step 5 修改成功
- [ ] [第三步] - 检查 Git 提交历史，确认 Step 5 创建了 commit
- [ ] [第四步] - 检查 GitHub 上的 Draft PR 页面，确认 Step 6 创建了 Draft PR
- [ ] [第五步] - 在 Issue 中回复 Stage 6 成功信息

### 风险提示
- [可能的风险点1] - Stage 6 功能存在bug，导致测试失败
- [可能的风险点2] - README.md 文件修改未正确反映在 commit 和 Draft PR 中

### 下一步
💡 评论 `/zhipu-apply` 可进入执行阶段（第二阶段功能，敬请期待）

---
🤖 本回复由 Zhipu AI 生成 - yyd841122/ragchatbot-codebase