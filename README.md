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
   curl -LsSf https://astral.sh/uv/install.sh | sh

2. **Install Python dependencies**
   uv sync

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ZHIPU_API_KEY=your_zhipu_api_key_here

## Running the Application

### Quick Start

Use the provided shell script:
chmod +x run.sh
./run.sh

### Manual Start

cd backend
uv run uvicorn app:app --reload --port 8000

The application will be available at:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Tools

### Code Quality

This project includes automated code quality tools:

- Format code
  python scripts/format.py

- Run quality checks
  python scripts/check_quality.py

- Or use the convenience scripts (Windows)
  scripts\dev.bat format
  scripts\dev.bat check

- Or use the convenience scripts (Linux/Mac)
  bash scripts/dev.sh format
  bash scripts/dev.sh check

**Tools included:**
- Black: Code formatter (line length: 100 chars)
- isort: Import statement organizer
- Flake8: Code style checker

For detailed usage, see docs/CODE_QUALITY.md.

### Testing

Run the test suite:
cd backend
uv run pytest -v

### Pre-commit Hooks (Optional)

Install pre-commit hooks for automatic quality checks:
pip install pre-commit
pre-commit install
Now hooks will run automatically on each commit

## Issue 标题
Stage 7 验证：测试计划生成质量

## Issue 正文
请测试改进后的 @zhipu 功能，验证生成的计划第一个文件是否为 README.md

## 执行计划
## 🤖 Zhipu Fix Plan

### 问题理解
验证改进后的 @zhipu 功能，确保生成的计划中第一个文件是仓库根目录下的 README.md 文件。

### 计划修改文件
- README.md - 确保为第一个文件

### Todo List
- [ ] [第一步] - 检查 @zhipu 功能是否已正确配置
  - 预期结果：功能配置正确，可以生成计划文件
- [ ] [第二步] - 运行 @zhipu 功能生成计划文件
  - 预期结果：生成计划文件，文件列表中包含 README.md
- [ ] [第三步] - 验证生成的计划文件列表
  - 预期结果：文件列表的第一个文件是 README.md
- [ ] [第四步] - 检查 README.md 文件是否位于仓库根目录
  - 预期结果：README.md 文件确实位于仓库根目录
- [ ] [第五步] - 确认 README.md 文件内容
  - 预期结果：README.md 文件内容符合预期

### 风险提示
- [可能的风险点1] - @zhipu 功能配置错误，导致无法生成计划文件
- [可能的风险点2] - 生成的计划文件列表中 README.md 文件位置错误

### 下一步
💡 评论 `/zhipu-apply` 可进入执行阶段（第二阶段功能，敬请期待）

---