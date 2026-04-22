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

## Testing Stage 6

### Overview

This section outlines the testing plan for Stage 6, which includes generating a structured plan and modifying the README.md file. The goal is to ensure that the system can automatically create a Draft Pull Request (PR) with the structured plan.

### Prerequisites

- Ensure that Stage 6 is properly configured with all necessary environment variables and configuration items.
- Have a `.env` file with the Anthropic API key set.

### Testing Steps

1. **Generate Structured Plan**
   - Run the test script to generate a structured plan.
   - Verify that the plan is correctly formatted and contains all required information.

2. **Modify README.md**
   - The test script should use the README.md file to record the plan modifications.
   - Check that the README.md file has been updated with the new plan.

3. **Automated Draft PR Creation**
   - Verify that the system can automatically create a Draft PR with the structured plan.
   - Ensure that the PR contains the correct content and is linked to the appropriate repository.

### Results

- [ ] Structured plan generated successfully.
- [ ] README.md updated with plan modifications.
- [ ] Draft PR created automatically with the structured plan.

### Known Issues

- [ ] Potential issue with reading/writing to README.md.
- [ ] Possible configuration or permission issues with Draft PR creation.

### Next Steps

- Continue testing and refining the Stage 6 functionality.
- Address any known issues and ensure the system meets all requirements.

For more information, refer to the [Stage 6 documentation](docs/STAGE_6.md).