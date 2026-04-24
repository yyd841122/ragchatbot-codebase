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

## Test Section

[TEST] Stage 8.1 - Phase 2A 测试 README.md

## 测试目标

验证 Stage 8.1 是否能正确识别和处理根目录的 README.md 文件。

## 预期结果

- Stage 1 AI 应该能识别出 README.md
- AI 生成的计划中第一个文件应该是 README.md
- 不应该有任何文件类型错误

## 执行计划

## 🤖 Zhipu Fix Plan

### 问题理解
验证 Stage 8.1 是否能正确识别和处理根目录的 README.md 文件，并确保没有文件类型错误。

### 计划修改文件
- README.md - [添加测试章节]

### Todo List
- [ ] [第一步] - 在 README.md 文件中添加一个测试章节，例如 "Test Section"
- [ ] [第二步] - 运行 Stage 8.1，确保 AI 识别出添加的测试章节
- [ ] [第三步] - 检查 AI 生成的计划中第一个文件是否为 README.md
- [ ] [第四步] - 验证生成的计划中不包含任何非 .md 文件类型
- [ ] [第五步] - 确认所有步骤完成后，没有文件类型错误

### 风险提示
- [可能的风险点1] - Stage 8.1 无法识别 README.md 文件
- [可能的风险点2] - 生成的计划中包含非 .md 文件类型

### 下一步
💡 评论 `/zhipu-apply` 可进入执行阶段（第二阶段功能，敬请期待）

---