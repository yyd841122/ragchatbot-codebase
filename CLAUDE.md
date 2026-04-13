# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **RAG (Retrieval-Augmented Generation) chatbot system** for answering questions about course materials. Users can query course content, and the system uses semantic search over processed documents combined with AI-generated responses.

**Tech Stack:**
- Backend: FastAPI + Python 3.13+
- Vector Database: ChromaDB with SentenceTransformer embeddings
- AI Provider: Zhipu AI (GLM-4-Flash model)
- Frontend: Static HTML/CSS/JS served by FastAPI
- Package Manager: `uv`

## Essential Commands

### Running the Application

```bash
# Install dependencies
uv sync

# Start development server (auto-reload enabled)
cd backend
uv run uvicorn app:app --reload --port 8000

# Or use the startup script (requires Git Bash on Windows)
bash run.sh
```

**Startup verification:** Look for log lines like `Loaded X courses with Y chunks` indicating successful document ingestion.

### Development Workflow

```bash
# Add/modify course documents (placed in docs/ folder)
# Restart server - documents auto-load on startup via app.py startup_event

# Access API documentation
open http://localhost:8000/docs

# Test query endpoint directly
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "session_id": null}'
```

## Architecture

### Core Request Flow

```
User Query → Frontend (fetch) → FastAPI Route → RAGSystem → AIGenerator
                                                              ↓
                                            Zhipu AI API (decision)
                                                              ↓
                                          ToolManager → CourseSearchTool
                                                              ↓
                                            VectorStore → ChromaDB
                                                              ↓
                                          AIGenerator → Zhipu AI (generation)
                                                              ↓
                                              Response + Sources → Frontend
```

### Key Components

**`backend/app.py`** - FastAPI entry point
- Route: `POST /api/query` (main query endpoint)
- Route: `GET /api/courses` (course statistics)
- Startup event: Auto-loads documents from `../docs/` folder
- Serves static frontend from root `/`

**`backend/rag_system.py`** - Central orchestrator
- `RAGSystem.query(query, session_id)` - Main query processing
- Coordinates: document processing, vector search, AI generation, session history
- Two-stage AI flow: decision → search (if needed) → generation

**`backend/ai_generator.py`** - Zhipu AI wrapper
- Implements Function Calling (tool use)
- First API call: AI decides whether `search_course_content` tool is needed
- If tool called: executes search, formats results, makes second API call
- System prompt enforces: search only for course-specific questions

**`backend/vector_store.py`** - ChromaDB wrapper
- Two collections: `course_catalog` (metadata), `course_content` (chunks)
- `search(query, course_name, lesson_number)` - Semantic search with filters
- Uses SentenceTransformer `all-MiniLM-L6-v2` for embeddings

**`backend/document_processor.py`** - Document parsing and chunking
- Expected format:
  ```
  Course Title: [name]
  Course Link: [url]
  Course Instructor: [name]
  Lesson 0: [title]
  Lesson Link: [url] (optional)
  [content...]
  ```
- Smart sentence-based chunking (800 chars, 100 char overlap)
- Extracts Course/Lesson/Chunk models for structured storage

**`backend/search_tools.py`** - Function Calling tools
- `CourseSearchTool` - Searches course content via VectorStore
- Implements Tool interface with `get_tool_definition()` and `execute()`
- Tracks `last_sources` for UI display

**`backend/session_manager.py`** - Conversation history
- In-memory session storage (no persistence)
- `MAX_HISTORY=2` exchanges per session (configurable)

### Data Models

**`backend/models.py`** - Pydantic models
- `Course` - Course metadata with lessons list
- `Lesson` - Lesson within a course
- `CourseChunk` - Text chunk with course/lesson context

### Configuration

**`backend/config.py`** - Centralized configuration
- `ZHIPU_API_KEY` - Loaded from `.env` file
- `ZHIPU_MODEL` - Model name (default: `glm-4-flash`)
- `CHUNK_SIZE`, `CHUNK_OVERLAP` - Document processing parameters
- `MAX_RESULTS` - Search result limit (default: 5)
- `CHROMA_PATH` - Vector database location

## Important Implementation Details

### Tool Calling Flow

The system uses Zhipu AI's Function Calling capability:

1. **First AI Call**: User query → AI decides if search needed
2. **Tool Execution**: If needed, `search_course_content` tool calls `VectorStore.search()`
3. **Second AI Call**: Search results → AI generates contextualized answer

**Key file:** `ai_generator.py` - `_handle_tool_execution()` method

### Document Format Requirements

Course documents in `docs/` must follow strict format:
- First 3 lines: `Course Title:`, `Course Link:`, `Course Instructor:`
- Lesson markers: `Lesson N: Title`
- Optional: `Lesson Link:` on next line

**Parser:** `document_processor.py` - `process_course_document()`

### Vector Search Strategy

- **Course name resolution**: Fuzzy semantic match via `course_catalog` collection
- **Content filtering**: By `course_title` and/or `lesson_number` metadata
- **Result formatting**: Adds `[Course - Lesson N]` context headers

**Method:** `VectorStore.search()` in `vector_store.py`

### Session Management

- Sessions created on first query (no session_id provided)
- History tracked in-memory (lost on restart)
- History format: `"User: ...\nAssistant: ..."`
- Passed to AI as part of system prompt

### Frontend-Backend Contract

**Request (`POST /api/query`):**
```json
{
  "query": "string",
  "session_id": "string | null"
}
```

**Response:**
```json
{
  "answer": "string (markdown)",
  "sources": ["string"],
  "session_id": "string"
}
```

**Frontend rendering:** `frontend/script.js` - `addMessage()` uses `marked.parse()` for Markdown

## Environment Setup

Required `.env` file:
```
ZHIPU_API_KEY=your_key_here
```

The application requires:
- Python 3.13+
- uv package manager
- Zhipu AI API key

**Important Rules:**
- **Always use `uv` to run the server and manage dependencies. Never use `pip` directly.**
- Use `uv` for all dependency management operations (install, add, remove, sync)
- **Use `uv run` to execute all Python files** (e.g., `uv run script.py` instead of `python script.py`)

### Git Configuration

Before making commits, ensure Git user identity is configured:
```bash
git config --global user.name "yyd841122"
git config --global user.email "115401344@qq.com"
```


## Common Modification Points

**Adjust search relevance:**
- Modify `MAX_RESULTS` in `config.py`
- Change chunk size/overlap in `config.py`
- Adjust embedding model in `config.py`

**Change AI behavior:**
- Edit `SYSTEM_PROMPT` in `ai_generator.py`
- Switch model in `config.py` (`ZHIPU_MODEL`)

**Add new tools:**
- Implement Tool interface in `search_tools.py`
- Register in `RAGSystem.__init__`

**Modify document parsing:**
- Edit regex patterns in `document_processor.py`
- Adjust chunking algorithm in `chunk_text()`
