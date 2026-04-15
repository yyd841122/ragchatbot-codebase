import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration settings for the RAG system"""

    # Zhipu AI API settings
    ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")
    ZHIPU_MODEL: str = "glm-4-flash"

    # Embedding model settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Document processing settings
    CHUNK_SIZE: int = 800  # Size of text chunks for vector storage
    CHUNK_OVERLAP: int = 100  # Characters to overlap between chunks
    MAX_RESULTS: int = 5  # Maximum search results to return
    MAX_HISTORY: int = 2  # Number of conversation messages to remember

    # Sequential tool calling settings
    MAX_TOOL_ROUNDS: int = 2  # Maximum consecutive tool calls per query
    TOOL_TIMEOUT: int = 30  # Timeout for tool execution (seconds)
    ENABLE_SEQUENTIAL_TOOLS: bool = True  # Enable sequential tool calling

    # Database paths - use absolute path to avoid issues with different working directories
    _backend_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_backend_dir)
    CHROMA_PATH: str = os.path.join(_project_root, "chroma_db")  # ChromaDB storage location


config = Config()
