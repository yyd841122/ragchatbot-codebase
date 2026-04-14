"""Tests for sequential tool calling functionality"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_generator import AIGenerator
from search_tools import ToolManager, CourseSearchTool, CourseOutlineTool
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
    """Create a ToolManager with mock search tools"""
    manager = ToolManager()
    search_tool = CourseSearchTool(mock_vector_store)
    manager.register_tool(search_tool)
    outline_tool = CourseOutlineTool(mock_vector_store)
    manager.register_tool(outline_tool)
    return manager


class TestSequentialToolCalling:
    """Test suite for sequential tool calling functionality"""

    @patch('zhipuai.ZhipuAI')
    def test_sequential_tool_calling_two_rounds(self, mock_client_class, mock_vector_store):
        """Test that two consecutive tool calls work correctly"""
        # Setup mock vector store responses
        mock_search_result = Mock()
        mock_search_result.error = None
        mock_search_result.is_empty.return_value = False
        mock_search_result.documents = ["Test content about RAG"]
        mock_search_result.metadata = [{
            "course_title": "Test Course",
            "lesson_number": 1,
            "chunk_index": 0
        }]

        mock_outline_result = Mock()
        mock_outline_result.title = "Introduction to RAG"
        mock_outline_result.course_link = "https://example.com/rag"
        mock_outline_result.instructor = "Test Instructor"
        mock_outline_result.lessons = []

        mock_vector_store.search.return_value = mock_search_result
        mock_vector_store.get_course_metadata.return_value = mock_outline_result

        # Setup three API calls:
        # 1st: User query → first tool call
        mock_first_response = Mock()
        mock_tool_call_1 = Mock()
        mock_tool_call_1.id = "call_1"
        mock_tool_call_1.type = "function"
        mock_tool_call_1.function.name = "search_course_content"
        mock_tool_call_1.function.arguments = '{"query": "RAG"}'

        mock_first_response.choices = [Mock()]
        mock_first_response.choices[0].message.content = None
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call_1]

        # 2nd: First tool result → second tool call
        mock_second_response = Mock()
        mock_tool_call_2 = Mock()
        mock_tool_call_2.id = "call_2"
        mock_tool_call_2.type = "function"
        mock_tool_call_2.function.name = "get_course_outline"
        mock_tool_call_2.function.arguments = '{"course_title": "Introduction to RAG"}'

        mock_second_response.choices = [Mock()]
        mock_second_response.choices[0].message.content = None
        mock_second_response.choices[0].message.tool_calls = [mock_tool_call_2]

        # 3rd: Second tool result → final response
        mock_third_response = Mock()
        mock_third_response.choices = [Mock()]
        mock_third_response.choices[0].message.content = "Based on the search and course outline, RAG is..."
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
        outline_tool = CourseOutlineTool(mock_vector_store)
        manager.register_tool(outline_tool)

        # Test execution
        response = generator.generate_response(
            query="What is RAG and show me the course outline",
            tools=manager.get_tool_definitions(),
            tool_manager=manager,
            max_rounds=2
        )

        # Verify results
        assert response is not None
        assert isinstance(response, str)
        assert "Based on the search and course outline" in response

        # Verify API was called 3 times (initial + 2 tool rounds)
        assert mock_client_instance.chat.completions.create.call_count == 3

        # Verify both tools were executed
        assert mock_vector_store.search.called
        assert mock_vector_store.get_course_metadata.called

        print("[PASS] Sequential tool calling with two rounds works correctly")

    @patch('zhipuai.ZhipuAI')
    def test_early_termination_no_tool_calls(self, mock_client_class, mock_vector_store):
        """Test that loop terminates when AI decides not to use tools"""
        # Setup three API calls:
        # 1st: User query → tool call
        mock_first_response = Mock()
        mock_tool_call = Mock()
        mock_tool_call.id = "call_1"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "search_course_content"
        mock_tool_call.function.arguments = '{"query": "test"}'

        mock_first_response.choices = [Mock()]
        mock_first_response.choices[0].message.content = None
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]

        # 2nd: Tool result → no tool call (direct response)
        mock_second_response = Mock()
        mock_second_response.choices = [Mock()]
        mock_second_response.choices[0].message.content = "Here's the information you requested"
        mock_second_response.choices[0].message.tool_calls = None

        # 3rd: Final response (same as 2nd, since loop terminates)
        mock_third_response = Mock()
        mock_third_response.choices = [Mock()]
        mock_third_response.choices[0].message.content = "Here's the information you requested"
        mock_third_response.choices[0].message.tool_calls = None

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = [
            mock_first_response,
            mock_second_response,
            mock_third_response
        ]
        mock_client_class.return_value = mock_client_instance

        # Setup mock vector store
        mock_search_result = Mock()
        mock_search_result.error = None
        mock_search_result.is_empty.return_value = False
        mock_search_result.documents = ["Test content"]
        mock_search_result.metadata = [{"course_title": "Test", "lesson_number": 1}]
        mock_vector_store.search.return_value = mock_search_result

        # Create generator and tool manager
        generator = AIGenerator("test_key", "glm-4-flash")
        manager = ToolManager()
        search_tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(search_tool)

        # Test execution
        response = generator.generate_response(
            query="Tell me about test topic",
            tools=manager.get_tool_definitions(),
            tool_manager=manager,
            max_rounds=2
        )

        # Verify results
        assert response is not None
        assert "Here's the information you requested" in response

        # Verify API was called 3 times:
        # 1. Initial call with user query
        # 2. Call after first tool execution (AI decides no more tools needed)
        # 3. Final call without tools
        assert mock_client_instance.chat.completions.create.call_count == 3

        print("[PASS] Early termination when no tool calls works correctly")

    @patch('zhipuai.ZhipuAI')
    def test_early_termination_on_error(self, mock_client_class, mock_vector_store):
        """Test that loop terminates when tool execution fails"""
        # Setup two API calls:
        # 1st: User query → tool call
        mock_first_response = Mock()
        mock_tool_call = Mock()
        mock_tool_call.id = "call_1"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "search_course_content"
        mock_tool_call.function.arguments = '{"query": "test"}'

        mock_first_response.choices = [Mock()]
        mock_first_response.choices[0].message.content = None
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]

        # 2nd: Tool error → final response
        mock_second_response = Mock()
        mock_second_response.choices = [Mock()]
        mock_second_response.choices[0].message.content = "I encountered an error searching for information"
        mock_second_response.choices[0].message.tool_calls = None

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = [
            mock_first_response,
            mock_second_response
        ]
        mock_client_class.return_value = mock_client_instance

        # Setup mock vector store to return error
        mock_vector_store.search.return_value = Mock(
            error="Database connection failed",
            is_empty=lambda: True
        )

        # Create generator and tool manager
        generator = AIGenerator("test_key", "glm-4-flash")
        manager = ToolManager()
        search_tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(search_tool)

        # Test execution
        response = generator.generate_response(
            query="Tell me about test topic",
            tools=manager.get_tool_definitions(),
            tool_manager=manager,
            max_rounds=2
        )

        # Verify results
        assert response is not None
        assert "I encountered an error" in response

        # Verify API was called 2 times (terminated after error)
        assert mock_client_instance.chat.completions.create.call_count == 2

        print("[PASS] Early termination on error works correctly")

    @patch('zhipuai.ZhipuAI')
    def test_source_accumulation_across_rounds(self, mock_client_class, mock_vector_store):
        """Test that sources are accumulated from multiple tool executions"""
        # Setup mock vector store responses
        mock_search_result = Mock()
        mock_search_result.error = None
        mock_search_result.is_empty.return_value = False
        mock_search_result.documents = ["RAG content"]
        mock_search_result.metadata = [{
            "course_title": "RAG Course",
            "lesson_number": 1,
            "chunk_index": 0
        }]

        mock_outline_result = Mock()
        mock_outline_result.title = "RAG Course"
        mock_outline_result.course_link = "https://example.com/rag"
        mock_outline_result.instructor = "Instructor"
        mock_outline_result.lessons = []

        mock_vector_store.search.return_value = mock_search_result
        mock_vector_store.get_course_metadata.return_value = mock_outline_result
        mock_vector_store.get_course_link.return_value = "https://example.com/rag"
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson1"

        # Setup three API calls
        mock_first_response = Mock()
        mock_tool_call_1 = Mock()
        mock_tool_call_1.id = "call_1"
        mock_tool_call_1.type = "function"
        mock_tool_call_1.function.name = "search_course_content"
        mock_tool_call_1.function.arguments = '{"query": "RAG"}'
        mock_first_response.choices = [Mock()]
        mock_first_response.choices[0].message.content = None
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call_1]

        mock_second_response = Mock()
        mock_tool_call_2 = Mock()
        mock_tool_call_2.id = "call_2"
        mock_tool_call_2.type = "function"
        mock_tool_call_2.function.name = "get_course_outline"
        mock_tool_call_2.function.arguments = '{"course_title": "RAG Course"}'
        mock_second_response.choices = [Mock()]
        mock_second_response.choices[0].message.content = None
        mock_second_response.choices[0].message.tool_calls = [mock_tool_call_2]

        mock_third_response = Mock()
        mock_third_response.choices = [Mock()]
        mock_third_response.choices[0].message.content = "Combined response"
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
        outline_tool = CourseOutlineTool(mock_vector_store)
        manager.register_tool(outline_tool)

        # Test execution
        response = generator.generate_response(
            query="What is RAG and show me the outline",
            tools=manager.get_tool_definitions(),
            tool_manager=manager,
            max_rounds=2
        )

        # Verify sources were accumulated
        sources = manager.get_last_sources()
        assert len(sources) > 0
        print(f"[PASS] Source accumulation works: {len(sources)} sources collected")

    @patch('zhipuai.ZhipuAI')
    def test_max_rounds_enforcement(self, mock_client_class, mock_vector_store):
        """Test that MAX_ROUNDS limit is enforced"""
        # Setup mock to always return tool calls (trying to exceed limit)
        def create_response_with_tool(call_id, tool_name):
            response = Mock()
            tool_call = Mock()
            tool_call.id = call_id
            tool_call.type = "function"
            tool_call.function.name = tool_name
            tool_call.function.arguments = '{"query": "test"}'
            response.choices = [Mock()]
            response.choices[0].message.content = None
            response.choices[0].message.tool_calls = [tool_call]
            return response

        # Create responses for 3 rounds (should stop at 2)
        responses = [
            create_response_with_tool("call_1", "search_course_content"),
            create_response_with_tool("call_2", "search_course_content"),
            Mock(choices=[Mock(content="Final response", tool_calls=None)])
        ]

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = responses
        mock_client_class.return_value = mock_client_instance

        # Setup mock vector store
        mock_search_result = Mock()
        mock_search_result.error = None
        mock_search_result.is_empty.return_value = False
        mock_search_result.documents = ["Test"]
        mock_search_result.metadata = [{"course_title": "Test", "lesson_number": 1}]
        mock_vector_store.search.return_value = mock_search_result

        # Create generator and tool manager
        generator = AIGenerator("test_key", "glm-4-flash")
        manager = ToolManager()
        search_tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(search_tool)

        # Test execution with max_rounds=2
        response = generator.generate_response(
            query="Test query",
            tools=manager.get_tool_definitions(),
            tool_manager=manager,
            max_rounds=2
        )

        # Verify API was called 3 times max (initial + 2 rounds + final)
        # Should NOT continue to 4th call even though AI wanted to
        assert mock_client_instance.chat.completions.create.call_count == 3

        print("[PASS] MAX_ROUNDS limit is enforced correctly")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])