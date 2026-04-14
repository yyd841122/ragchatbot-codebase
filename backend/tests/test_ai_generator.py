"""Tests for AIGenerator to diagnose tool calling issues"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_generator import AIGenerator
from search_tools import ToolManager, CourseSearchTool
from vector_store import VectorStore
from config import config


@pytest.fixture
def mock_zhipu_client():
    """Create a mock Zhipu AI client"""
    with patch('zhipuai.ZhipuAI') as mock:
        yield mock


@pytest.fixture
def ai_generator():
    """Create an AIGenerator instance"""
    return AIGenerator(
        api_key=config.ZHIPU_API_KEY,
        model=config.ZHIPU_MODEL
    )


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store"""
    store = Mock(spec=VectorStore)
    return store


@pytest.fixture
def tool_manager(mock_vector_store):
    """Create a ToolManager with mock search tool"""
    manager = ToolManager()
    search_tool = CourseSearchTool(mock_vector_store)
    manager.register_tool(search_tool)
    return manager


class TestAIGenerator:
    """Test suite for AIGenerator"""

    def test_initialization(self, ai_generator):
        """Test that AIGenerator initializes correctly"""
        assert ai_generator is not None
        assert ai_generator.model == config.ZHIPU_MODEL
        assert hasattr(ai_generator, 'client')

        print("[PASS] AIGenerator initializes correctly")

    def test_system_prompt_structure(self, ai_generator):
        """Test that system prompt is properly defined"""
        assert ai_generator.SYSTEM_PROMPT is not None
        assert len(ai_generator.SYSTEM_PROMPT) > 0
        assert "search_course_content" in ai_generator.SYSTEM_PROMPT
        assert "get_course_outline" in ai_generator.SYSTEM_PROMPT

        print("[PASS] System prompt is properly defined")
        print(f"  Prompt length: {len(ai_generator.SYSTEM_PROMPT)} characters")

    @patch('zhipuai.ZhipuAI')
    def test_generate_response_without_tools(self, mock_client_class, ai_generator):
        """Test basic response generation without tools"""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! I'm your course assistant."
        mock_response.choices[0].message.tool_calls = None

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_client_class.return_value = mock_client_instance

        # Create generator with mocked client
        generator = AIGenerator("test_key", "glm-4-flash")

        # Test
        response = generator.generate_response("Hello")

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0

        print(f"[PASS] Basic response generation works: {response[:50]}...")

    @patch('zhipuai.ZhipuAI')
    def test_generate_response_with_tool_call(self, mock_client_class, mock_vector_store):
        """Test response generation with tool calling"""
        # Setup mock vector store response
        mock_search_result = Mock()
        mock_search_result.error = None
        mock_search_result.is_empty.return_value = False
        mock_search_result.documents = ["Test content about RAG"]
        mock_search_result.metadata = [{
            "course_title": "Test Course",
            "lesson_number": 1,
            "chunk_index": 0
        }]

        mock_vector_store.search.return_value = mock_search_result
        mock_vector_store.get_course_link.return_value = "https://example.com/course"
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson1"

        # Setup first API call (with tool call)
        mock_first_response = Mock()
        mock_first_response.choices = [Mock()]

        # Create mock tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "search_course_content"
        mock_tool_call.function.arguments = '{"query": "What is RAG?"}'

        mock_first_response.choices[0].message.content = None
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]

        # Setup second API call (AI response after tool execution)
        mock_second_response = Mock()
        mock_second_response.choices = [Mock()]
        mock_second_response.choices[0].message.content = None
        mock_second_response.choices[0].message.tool_calls = None

        # Setup third API call (final response)
        mock_third_response = Mock()
        mock_third_response.choices = [Mock()]
        mock_third_response.choices[0].message.content = "RAG stands for Retrieval-Augmented Generation..."
        mock_third_response.choices[0].message.tool_calls = None

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = [
            mock_first_response,
            mock_second_response,
            mock_third_response
        ]
        mock_client_class.return_value = mock_client_instance

        # Create generator and tool manager
        generator = AIGenerator("test_key", "glm-4-flash")
        manager = ToolManager()
        search_tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(search_tool)

        # Test
        response = generator.generate_response(
            query="What is RAG?",
            tools=manager.get_tool_definitions(),
            tool_manager=manager
        )

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0

        # Verify tool was called
        mock_vector_store.search.assert_called_once()

        print(f"[PASS] Tool calling works: {response[:50]}...")

    def test_conversation_history_integration(self, ai_generator):
        """Test that conversation history is properly integrated"""
        history = "User: What is RAG?\nAssistant: RAG stands for..."

        with patch('zhipuai.ZhipuAI') as mock_client_class:
            # Setup mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Based on our previous discussion..."
            mock_response.choices[0].message.tool_calls = None

            mock_client_instance = Mock()
            mock_client_instance.chat.completions.create.return_value = mock_response
            mock_client_class.return_value = mock_client_instance

            # Create generator with mocked client
            generator = AIGenerator("test_key", "glm-4-flash")

            # Test
            response = generator.generate_response(
                "Tell me more",
                conversation_history=history
            )

            # Verify that the API was called with history
            call_args = mock_client_instance.chat.completions.create.call_args
            messages = call_args[1]['messages']

            # Check that history was included in system message
            system_msg = [m for m in messages if m['role'] == 'system'][0]
            assert history in system_msg['content']

            print(f"[PASS] Conversation history integration works")

    def test_tool_execution_error_handling(self, ai_generator, mock_vector_store):
        """Test error handling when tool execution fails"""
        # Setup vector store to return error
        mock_vector_store.search.side_effect = Exception("Database connection failed")

        with patch('zhipuai.ZhipuAI') as mock_client_class:
            # Setup mock response with tool call
            mock_response = Mock()
            mock_response.choices = [Mock()]

            mock_tool_call = Mock()
            mock_tool_call.id = "call_123"
            mock_tool_call.type = "function"
            mock_tool_call.function.name = "search_course_content"
            mock_tool_call.function.arguments = '{"query": "test"}'

            mock_response.choices[0].message.content = None
            mock_response.choices[0].message.tool_calls = [mock_tool_call]

            mock_client_instance = Mock()
            mock_client_instance.chat.completions.create.return_value = mock_response
            mock_client_class.return_value = mock_client_instance

            # Create generator and tool manager
            generator = AIGenerator("test_key", "glm-4-flash")
            manager = ToolManager()
            search_tool = CourseSearchTool(mock_vector_store)
            manager.register_tool(search_tool)

            # Test - should handle error gracefully
            try:
                response = generator.generate_response(
                    query="test query",
                    tools=manager.get_tool_definitions(),
                    tool_manager=manager
                )
                print(f"[PASS] Error handling works: {response[:50]}...")
            except Exception as e:
                print(f"⚠ Error propagated: {e}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])