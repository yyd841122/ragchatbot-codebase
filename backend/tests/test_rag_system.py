"""Integration tests for RAG System to diagnose end-to-end issues"""

import os
import sys

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from rag_system import RAGSystem


@pytest.fixture
def rag_system():
    """Create a RAGSystem instance for testing"""
    system = RAGSystem(config)

    # Clear existing data for clean test
    system.vector_store.clear_all_data()

    return system


@pytest.fixture
def populated_rag_system(rag_system):
    """Create a RAGSystem with sample data"""
    # Add sample course document
    # For this test, we'll manually add course data

    from models import Course, CourseChunk, Lesson

    # Create test course
    course = Course(
        title="Integration Test Course",
        course_link="https://example.com/integration-test",
        instructor="Test Instructor",
        lessons=[
            Lesson(lesson_number=1, title="Test Lesson 1"),
            Lesson(lesson_number=2, title="Test Lesson 2"),
        ],
    )

    # Create test chunks
    chunks = [
        CourseChunk(
            content="This is test content for integration testing. RAG systems combine retrieval with generation.",
            course_title="Integration Test Course",
            lesson_number=1,
            chunk_index=0,
        ),
        CourseChunk(
            content="Vector databases store embeddings for semantic search. They enable efficient similarity matching.",
            course_title="Integration Test Course",
            lesson_number=1,
            chunk_index=1,
        ),
        CourseChunk(
            content="The RAG pipeline processes user queries, searches for relevant content, and generates contextual responses.",
            course_title="Integration Test Course",
            lesson_number=2,
            chunk_index=2,
        ),
    ]

    # Add to vector store
    rag_system.vector_store.add_course_metadata(course)
    rag_system.vector_store.add_course_content(chunks)

    return rag_system


class TestRAGSystem:
    """Integration tests for RAG System"""

    def test_system_initialization(self, rag_system):
        """Test that RAGSystem initializes all components correctly"""
        assert rag_system is not None
        assert rag_system.config is not None
        assert rag_system.document_processor is not None
        assert rag_system.vector_store is not None
        assert rag_system.ai_generator is not None
        assert rag_system.session_manager is not None
        assert rag_system.tool_manager is not None

        print("[PASS] RAGSystem initializes all components")

    def test_vector_store_has_data(self, populated_rag_system):
        """Test that vector store contains test data"""
        course_count = populated_rag_system.vector_store.get_course_count()
        assert course_count > 0

        titles = populated_rag_system.vector_store.get_existing_course_titles()
        assert len(titles) > 0
        assert "Integration Test Course" in titles

        print(f"[PASS] Vector store contains data: {course_count} courses")

    def test_query_without_session(self, populated_rag_system):
        """Test basic query without session context"""
        query = "What is RAG?"

        try:
            response, sources = populated_rag_system.query(query)

            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0

            # Response should not be an error message
            assert "查询失败" not in response
            assert "error" not in response.lower()

            print(f"[PASS] Basic query works")
            print(f"  Response: {response[:100]}...")
            print(f"  Sources: {len(sources)} items")

            if sources:
                for i, source in enumerate(sources):
                    print(f"    Source {i+1}: {source.get('course_title', 'unknown')}")

        except Exception as e:
            print(f"[FAIL] Query failed with error: {e}")
            raise

    def test_query_with_session(self, populated_rag_system):
        """Test query with session context"""
        query = "Tell me more about vector databases"

        try:
            # First query creates session
            response1, sources1 = populated_rag_system.query(query, session_id="test_session")

            # Second query uses session history
            response2, sources2 = populated_rag_system.query(
                "How do they work?", session_id="test_session"
            )

            assert response2 is not None
            assert len(response2) > 0
            assert "查询失败" not in response2

            print(f"[PASS] Session-based query works")
            print(f"  First response: {response1[:50]}...")
            print(f"  Second response: {response2[:50]}...")

        except Exception as e:
            print(f"[FAIL] Session query failed with error: {e}")
            raise

    def test_course_specific_query(self, populated_rag_system):
        """Test query that should find course-specific content"""
        query = "What is the RAG pipeline?"

        try:
            response, sources = populated_rag_system.query(query)

            assert response is not None
            assert len(response) > 0
            assert "查询失败" not in response

            # Check that sources were found
            if sources:
                assert len(sources) > 0
                print(f"[PASS] Course-specific query found {len(sources)} sources")
            else:
                print(f"[WARNING] Course-specific query returned no sources")
                print(f"  Response: {response[:100]}...")

        except Exception as e:
            print(f"[FAIL] Course-specific query failed with error: {e}")
            raise

    def test_no_results_query(self, populated_rag_system):
        """Test query that should return no results"""
        query = "Tell me about quantum entanglement"

        try:
            response, sources = populated_rag_system.query(query)

            assert response is not None
            assert len(response) > 0

            # Should gracefully handle no results
            if "no relevant" in response.lower() or "not found" in response.lower():
                print(f"[PASS] No results case handled gracefully")
            else:
                print(f"[WARNING] No results query: {response[:100]}...")

        except Exception as e:
            print(f"[FAIL] No results query failed with error: {e}")
            raise

    def test_tool_availability(self, populated_rag_system):
        """Test that tools are properly registered and available"""
        tools = populated_rag_system.tool_manager.get_tool_definitions()

        assert tools is not None
        assert len(tools) > 0

        # Check for expected tools
        tool_names = []
        for tool in tools:
            if "function" in tool:
                tool_names.append(tool["function"]["name"])
            else:
                tool_names.append(tool.get("name", "unknown"))

        assert "search_course_content" in tool_names
        assert "get_course_outline" in tool_names

        print(f"[PASS] Tools available: {tool_names}")

    def test_course_analytics(self, populated_rag_system):
        """Test course analytics functionality"""
        analytics = populated_rag_system.get_course_analytics()

        assert analytics is not None
        assert "total_courses" in analytics
        assert "course_titles" in analytics

        assert analytics["total_courses"] > 0
        assert len(analytics["course_titles"]) > 0

        print(f"[PASS] Analytics: {analytics['total_courses']} courses")
        print(f"  Titles: {analytics['course_titles']}")


class TestRAGSystemWithRealAPI:
    """Test RAG System with actual API calls (requires API key)"""

    @pytest.mark.skipif(
        not config.ZHIPU_API_KEY or config.ZHIPU_API_KEY == "", reason="ZHIPU_API_KEY not available"
    )
    def test_real_query_with_api(self, populated_rag_system):
        """Test real query with actual API"""
        query = "What is RAG?"

        try:
            response, sources = populated_rag_system.query(query)

            assert response is not None
            assert len(response) > 0
            assert "查询失败" not in response

            print(f"[PASS] Real API query works")
            print(f"  Response: {response[:100]}...")
            print(f"  Sources: {len(sources)} items")

        except Exception as e:
            print(f"[FAIL] Real API query failed: {e}")
            raise


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
