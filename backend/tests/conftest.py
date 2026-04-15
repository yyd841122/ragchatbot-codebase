"""
Shared pytest fixtures and test utilities for RAG system testing.

This module provides common fixtures used across all test files to ensure
consistent mocking and test data setup.
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from rag_system import RAGSystem
from ai_generator import AIGenerator
from search_tools import ToolManager, CourseSearchTool, CourseOutlineTool
from vector_store import VectorStore
from session_manager import SessionManager
from models import Course, Lesson, CourseChunk


# ==================== Mock Fixtures ====================

@pytest.fixture
def mock_zhipu_client():
    """Create a mock Zhipu AI client that can be configured for different test scenarios."""
    with patch('zhipuai.ZhipuAI') as mock:
        yield mock


@pytest.fixture
def mock_vector_store():
    """Create a mock VectorStore with configurable search results."""
    store = Mock(spec=VectorStore)

    # Setup default behavior
    store.search.return_value = Mock(
        error=None,
        is_empty=lambda: False,
        documents=["Test course content"],
        metadata=[{
            "course_title": "Test Course",
            "lesson_number": 1,
            "chunk_index": 0
        }]
    )

    store.get_course_link.return_value = "https://example.com/course"
    store.get_lesson_link.return_value = "https://example.com/lesson1"
    store.get_course_metadata.return_value = Mock(
        title="Test Course",
        course_link="https://example.com/course",
        instructor="Test Instructor",
        lessons=[]
    )

    return store


@pytest.fixture
def mock_session_manager():
    """Create a mock SessionManager with default session."""
    manager = Mock(spec=SessionManager)
    manager.create_session.return_value = "test_session_123"
    manager.get_history.return_value = ""
    manager.add_exchange.return_value = None
    return manager


# ==================== Real Component Fixtures ====================

@pytest.fixture
def ai_generator():
    """Create a real AIGenerator instance with test configuration."""
    return AIGenerator(
        api_key="test_api_key",  # Use test key, doesn't need to be valid for mocked tests
        model=config.ZHIPU_MODEL
    )


@pytest.fixture
def tool_manager(mock_vector_store):
    """Create a ToolManager with registered search tools."""
    manager = ToolManager()
    search_tool = CourseSearchTool(mock_vector_store)
    manager.register_tool(search_tool)

    outline_tool = CourseOutlineTool(mock_vector_store)
    manager.register_tool(outline_tool)

    return manager


@pytest.fixture
def rag_system(mock_vector_store, mock_session_manager):
    """Create a RAGSystem instance with mocked dependencies."""
    with patch('rag_system.VectorStore', return_value=mock_vector_store), \
         patch('rag_session_manager.SessionManager', return_value=mock_session_manager):

        system = RAGSystem(config)
        system.vector_store = mock_vector_store
        system.session_manager = mock_session_manager

        # Mock the add_course_folder to avoid file system operations
        system.add_course_folder = Mock(return_value=(1, 10))

        yield system


# ==================== Test Data Fixtures ====================

@pytest.fixture
def sample_courses() -> List[Course]:
    """Sample course data for testing."""
    return [
        Course(
            title="Introduction to RAG",
            link="https://example.com/rag",
            instructor="Dr. Smith",
            lessons=[
                Lesson(number=0, title="Overview", link=None),
                Lesson(number=1, title="Vector Databases", link="https://example.com/rag/lesson1"),
                Lesson(number=2, title="Embeddings", link="https://example.com/rag/lesson2"),
            ]
        ),
        Course(
            title="FastAPI Basics",
            link="https://example.com/fastapi",
            instructor="Jane Doe",
            lessons=[
                Lesson(number=0, title="Getting Started", link=None),
                Lesson(number=1, title="Routing", link="https://example.com/fastapi/routing"),
            ]
        )
    ]


@pytest.fixture
def sample_chunks() -> List[CourseChunk]:
    """Sample text chunks for testing."""
    return [
        CourseChunk(
            course_title="Introduction to RAG",
            lesson_number=1,
            chunk_index=0,
            text="RAG stands for Retrieval-Augmented Generation. It combines..."
        ),
        CourseChunk(
            course_title="Introduction to RAG",
            lesson_number=1,
            chunk_index=1,
            text="Vector databases are essential for RAG systems. They store..."
        ),
        CourseChunk(
            course_title="FastAPI Basics",
            lesson_number=0,
            chunk_index=0,
            text="FastAPI is a modern, fast web framework for building APIs..."
        )
    ]


@pytest.fixture
def sample_query_requests() -> Dict[str, Dict[str, Any]]:
    """Sample query request data for API testing."""
    return {
        "basic_query": {
            "query": "What is RAG?",
            "session_id": None
        },
        "course_specific_query": {
            "query": "Tell me about vector databases in the RAG course",
            "session_id": "session_123"
        },
        "followup_query": {
            "query": "Can you explain more about embeddings?",
            "session_id": "session_123"
        },
        "general_query": {
            "query": "What courses are available?",
            "session_id": None
        }
    }


@pytest.fixture
def sample_ai_responses():
    """Sample AI responses for mocking API calls."""
    return {
        "direct_answer": {
            "message": Mock(
                content="I can help you with questions about course materials.",
                tool_calls=None
            )
        },
        "tool_call_search": {
            "message": Mock(
                content=None,
                tool_calls=[Mock(
                    id="call_123",
                    type="function",
                    function=Mock(
                        name="search_course_content",
                        arguments='{"query": "What is RAG?"}'
                    )
                )]
            )
        },
        "final_response": {
            "message": Mock(
                content="Based on the course materials, RAG is...",
                tool_calls=None
            )
        }
    }


# ==================== API Test Fixtures ====================

@pytest.fixture
def test_app_data():
    """Sample data for API endpoint testing."""
    return {
        "course_stats": {
            "total_courses": 2,
            "course_titles": ["Introduction to RAG", "FastAPI Basics"]
        },
        "query_result": {
            "answer": "RAG stands for Retrieval-Augmented Generation...",
            "sources": [
                {
                    "course_title": "Introduction to RAG",
                    "lesson_number": 1,
                    "course_link": "https://example.com/rag",
                    "lesson_link": "https://example.com/rag/lesson1"
                }
            ]
        }
    }


@pytest.fixture
def mock_ai_response_direct():
    """Mock AI response without tool calls."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "I can help you with course questions."
    mock_response.choices[0].message.tool_calls = None
    return mock_response


@pytest.fixture
def mock_ai_response_with_tool():
    """Mock AI response with tool call."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = None

    mock_tool_call = Mock()
    mock_tool_call.id = "call_test_123"
    mock_tool_call.type = "function"
    mock_tool_call.function.name = "search_course_content"
    mock_tool_call.function.arguments = '{"query": "What is RAG?"}'

    mock_response.choices[0].message.tool_calls = [mock_tool_call]
    return mock_response


# ==================== Test Helper Functions ====================

def create_mock_search_result(documents: List[str], metadata: List[Dict]) -> Mock:
    """Helper to create mock search results."""
    result = Mock()
    result.error = None
    result.is_empty.return_value = len(documents) == 0
    result.documents = documents
    result.metadata = metadata
    return result


def create_mock_zhipu_response(content: str = None, tool_calls: List = None) -> Mock:
    """Helper to create mock Zhipu AI responses."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = content
    mock_response.choices[0].message.tool_calls = tool_calls
    return mock_response


def setup_mock_client_with_responses(responses: List[Mock]) -> Mock:
    """Helper to setup mock client with multiple responses."""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = responses
    return mock_client


# ==================== Environment Setup ====================

@pytest.fixture(autouse=True)
def suppress_warnings():
    """Suppress resource tracking warnings during tests."""
    import warnings
    warnings.filterwarnings("ignore", message="resource_tracker: There appear to be.*")


@pytest.fixture(scope="session")
def test_config():
    """Test configuration that can be used across tests."""
    return {
        "test_api_key": "test_key_for_testing",
        "test_model": "glm-4-flash",
        "test_session_id": "test_session_456",
        "max_test_results": 5
    }