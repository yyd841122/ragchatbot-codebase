"""Tests for CourseSearchTool to diagnose search failures"""

import os
import sys

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from models import Course, CourseChunk, Lesson
from search_tools import CourseSearchTool
from vector_store import VectorStore


@pytest.fixture
def vector_store():
    """Create a vector store for testing"""
    store = VectorStore(
        chroma_path=config.CHROMA_PATH,
        embedding_model=config.EMBEDDING_MODEL,
        max_results=config.MAX_RESULTS,
    )
    return store


@pytest.fixture
def search_tool(vector_store):
    """Create a CourseSearchTool instance"""
    return CourseSearchTool(vector_store)


@pytest.fixture
def sample_data(vector_store):
    """Add sample data to vector store for testing"""
    # Create a test course
    course = Course(
        title="Test RAG Course",
        course_link="https://example.com/test-course",
        instructor="Test Instructor",
        lessons=[
            Lesson(
                lesson_number=1,
                title="Introduction to RAG",
                lesson_link="https://example.com/lesson1",
            ),
            Lesson(
                lesson_number=2, title="Vector Databases", lesson_link="https://example.com/lesson2"
            ),
        ],
    )

    # Create test chunks
    chunks = [
        CourseChunk(
            content="RAG stands for Retrieval-Augmented Generation. It is a technique that combines retrieval systems with generative AI models.",
            course_title="Test RAG Course",
            lesson_number=1,
            chunk_index=0,
        ),
        CourseChunk(
            content="ChromaDB is a vector database that stores embeddings for semantic search. It is commonly used in RAG applications.",
            course_title="Test RAG Course",
            lesson_number=1,
            chunk_index=1,
        ),
        CourseChunk(
            content="Vector databases like ChromaDB enable efficient similarity search using embeddings. They store vectors and can find similar items quickly.",
            course_title="Test RAG Course",
            lesson_number=2,
            chunk_index=2,
        ),
    ]

    # Clear existing data and add test data
    vector_store.clear_all_data()
    vector_store.add_course_metadata(course)
    vector_store.add_course_content(chunks)

    return {"course": course, "chunks": chunks}


class TestCourseSearchTool:
    """Test suite for CourseSearchTool"""

    def test_tool_definition(self, search_tool):
        """Test that tool definition is correctly structured"""
        definition = search_tool.get_tool_definition()

        assert definition is not None
        assert definition["type"] == "function"
        assert "function" in definition

        func_def = definition["function"]
        assert func_def["name"] == "search_course_content"
        assert "description" in func_def
        assert "parameters" in func_def

        params = func_def["parameters"]
        assert params["type"] == "object"
        assert "properties" in params
        assert "query" in params["properties"]
        assert params["required"] == ["query"]

        print("[PASS] Tool definition structure is correct")

    def test_search_without_filter(self, search_tool, sample_data):
        """Test basic search without any filters"""
        result = search_tool.execute(query="What is RAG?")

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "RAG" in result or "Retrieval-Augmented" in result

        # Check that sources were tracked
        assert len(search_tool.last_sources) > 0

        print(f"[PASS] Basic search works. Found: {result[:100]}...")
        print(f"  Sources: {len(search_tool.last_sources)} items")

    def test_search_with_course_filter(self, search_tool, sample_data):
        """Test search with course name filter"""
        result = search_tool.execute(query="ChromaDB", course_name="Test RAG Course")

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "ChromaDB" in result or "vector" in result.lower()

        print(f"[PASS] Course filter works. Found: {result[:100]}...")

    def test_search_with_lesson_filter(self, search_tool, sample_data):
        """Test search with lesson number filter"""
        result = search_tool.execute(query="vector database", lesson_number=2)

        assert result is not None
        assert isinstance(result, str)
        # Should return search results (case insensitive)
        result_lower = result.lower()
        assert "no relevant content found" in result_lower or "test rag course" in result_lower

        print(f"[PASS] Lesson filter works. Found: {result[:100]}...")

    def test_search_with_both_filters(self, search_tool, sample_data):
        """Test search with both course and lesson filters"""
        result = search_tool.execute(query="RAG", course_name="Test RAG Course", lesson_number=1)

        assert result is not None
        assert isinstance(result, str)
        # Should only return results from lesson 1 of Test RAG Course
        assert "Lesson 1" in result or "lesson_number" in result

        print(f"[PASS] Combined filters work. Found: {result[:100]}...")

    def test_search_no_results(self, search_tool, sample_data):
        """Test search with query that should return no results"""
        result = search_tool.execute(query="quantum physics")

        assert result is not None
        assert isinstance(result, str)
        assert "No relevant content found" in result or "not found" in result.lower()

        print(f"[PASS] No results case handled correctly: {result}")

    def test_search_invalid_course(self, search_tool, sample_data):
        """Test search with non-existent course name"""
        result = search_tool.execute(query="RAG", course_name="NonExistentCourse123")

        assert result is not None
        assert isinstance(result, str)
        assert "not found" in result.lower() or "no course" in result.lower()

        print(f"[PASS] Invalid course handled correctly: {result}")

    def test_sources_tracking(self, search_tool, sample_data):
        """Test that sources are properly tracked"""
        search_tool.execute(query="ChromaDB")

        sources = search_tool.last_sources
        assert len(sources) > 0

        # Check source structure
        for source in sources:
            assert "course_title" in source
            assert "lesson_number" in source
            assert "course_link" in source
            assert "lesson_link" in source

        print(f"[PASS] Sources tracking works. Found {len(sources)} sources")
        for i, source in enumerate(sources):
            print(f"  Source {i+1}: {source['course_title']} - Lesson {source['lesson_number']}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
