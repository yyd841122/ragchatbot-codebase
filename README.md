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

## Issue Tracking

- [test: stage5 modify README.md](#test-stage5-modify-readme-md)

## 🤖 Zhipu Fix Plan

### Stage 5 Update

- **Completed Tasks**:
  - Updated the README.md with the initial setup instructions.
  - Implemented the basic structure of the RAG system.
  - Integrated ChromaDB for vector storage.
  - Integrated Anthropic's Claude for AI generation.

- **To-Do Tasks**:
  - Refine the user interface for better interaction.
  - Optimize the AI responses for better context awareness.
  - Conduct thorough testing of the system.
  - Document the system architecture and usage.

### Running the Application

To run the application, follow the instructions in the "Running the Application" section.

### Development Tools

The project includes tools for code quality and testing, as described in the "Development Tools" section.

### Testing

To run the test suite, navigate to the backend directory and execute the following command:

```bash
uv run pytest -v
```

### Pre-commit Hooks

To install pre-commit hooks for automatic quality checks, follow the instructions in the "Pre-commit Hooks (Optional)" section.

For detailed information on each section, refer to the respective sections in the README.md file.