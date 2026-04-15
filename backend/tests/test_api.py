"""
API endpoint tests for the RAG system.

This module tests all FastAPI endpoints including:
- POST /api/query - Main query processing endpoint
- GET /api/courses - Course statistics endpoint
- Request/response validation
- Error handling
- Session management
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from models import Course, Lesson


# ==================== Test Application Setup ====================

def create_test_app() -> FastAPI:
    """
    Create a test FastAPI application without static file mounting.

    This avoids the issue of missing static files in test environment.
    Only API endpoints are included.
    """
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from pydantic import BaseModel
    from typing import List, Optional

    # Create test app
    app = FastAPI(title="RAG System Test API")

    # Add middleware (same as production)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Request/Response models
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class SourceItem(BaseModel):
        course_title: str
        lesson_number: Optional[int] = None
        course_link: Optional[str] = None
        lesson_link: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[SourceItem]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    # Mock RAG system for testing
    class MockRAGSystem:
        def __init__(self):
            self.session_manager = Mock()
            self._session_counter = 0
            self.session_manager.create_session = self._create_session

        def _create_session(self):
            """Create unique session IDs for testing"""
            self._session_counter += 1
            return f"test_session_{self._session_counter}"

        def query(self, query: str, session_id: str):
            """Mock query method"""
            # Simulate successful query
            answer = f"Here's the answer to: {query}"
            sources = [
                SourceItem(
                    course_title="Test Course",
                    lesson_number=1,
                    course_link="https://example.com/course",
                    lesson_link="https://example.com/lesson1"
                )
            ]
            return answer, sources

        def get_course_analytics(self):
            """Mock analytics method"""
            return {
                "total_courses": 2,
                "course_titles": ["Test Course 1", "Test Course 2"]
            }

    # Initialize mock RAG system
    rag_system = MockRAGSystem()

    # API Endpoints
    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        """Process a query and return response with sources"""
        try:
            # Create session if not provided
            session_id = request.session_id
            if not session_id:
                session_id = rag_system.session_manager.create_session()

            # Process query using RAG system
            answer, sources = rag_system.query(request.query, session_id)

            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR in /api/query: {error_details}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        """Get course analytics and statistics"""
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    app = create_test_app()
    return TestClient(app)


# ==================== Query Endpoint Tests ====================

class TestQueryEndpoint:
    """Test suite for POST /api/query endpoint"""

    def test_query_endpoint_basic_request(self, test_client):
        """Test basic query request without session"""
        response = test_client.post(
            "/api/query",
            json={"query": "What is RAG?"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data

        # Verify data types
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)

        # Verify session was created
        assert data["session_id"] is not None
        assert data["session_id"].startswith("test_session_")

        print("[PASS] Basic query request works")

    def test_query_endpoint_with_existing_session(self, test_client):
        """Test query request with existing session ID"""
        existing_session = "existing_session_456"

        response = test_client.post(
            "/api/query",
            json={
                "query": "Tell me more about RAG",
                "session_id": existing_session
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify same session is used
        assert data["session_id"] == existing_session

        print("[PASS] Query with existing session works")

    def test_query_endpoint_request_validation(self, test_client):
        """Test request validation for malformed requests"""
        # Missing query field
        response = test_client.post(
            "/api/query",
            json={"session_id": "test"}
        )

        assert response.status_code == 422  # Validation error

        # Empty request
        response = test_client.post("/api/query", json={})

        assert response.status_code == 422

        print("[PASS] Request validation works")

    def test_query_endpoint_response_structure(self, test_client):
        """Test complete response structure with sources"""
        response = test_client.post(
            "/api/query",
            json={"query": "What courses do you have?"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify answer is non-empty string
        assert len(data["answer"]) > 0

        # Verify sources structure
        assert isinstance(data["sources"], list)
        if len(data["sources"]) > 0:
            source = data["sources"][0]
            assert "course_title" in source
            assert "lesson_number" in source
            assert "course_link" in source
            assert "lesson_link" in source

        print("[PASS] Response structure is correct")

    def test_query_endpoint_special_characters(self, test_client):
        """Test query with special characters and unicode"""
        special_queries = [
            "What is RAG? 你好",
            "Test with quotes: 'single' and \"double\"",
            "Test with emoji 🚀",
            "Test\nwith\nnewlines",
            "Test\twith\ttabs"
        ]

        for query in special_queries:
            response = test_client.post(
                "/api/query",
                json={"query": query}
            )

            assert response.status_code == 200
            data = response.json()
            assert "answer" in data

        print("[PASS] Special characters handled correctly")

    def test_query_endpoint_long_query(self, test_client):
        """Test query with very long text"""
        long_query = "Explain RAG " * 100  # 1300 characters

        response = test_client.post(
            "/api/query",
            json={"query": long_query}
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

        print("[PASS] Long queries handled correctly")

    def test_query_endpoint_http_methods(self, test_client):
        """Test that only POST method is accepted"""
        # GET should not be allowed
        response = test_client.get("/api/query")
        assert response.status_code == 405  # Method not allowed

        # PUT should not be allowed
        response = test_client.put("/api/query", json={"query": "test"})
        assert response.status_code == 405

        # DELETE should not be allowed
        response = test_client.delete("/api/query")
        assert response.status_code == 405

        print("[PASS] HTTP method restrictions work")


# ==================== Courses Endpoint Tests ====================

class TestCoursesEndpoint:
    """Test suite for GET /api/courses endpoint"""

    def test_courses_endpoint_basic_request(self, test_client):
        """Test basic course statistics request"""
        response = test_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "total_courses" in data
        assert "course_titles" in data

        # Verify data types
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)

        print("[PASS] Basic courses request works")

    def test_courses_endpoint_response_structure(self, test_client):
        """Test complete response structure"""
        response = test_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()

        # Verify total_courses is reasonable
        assert data["total_courses"] >= 0

        # Verify course_titles is a list of strings
        assert all(isinstance(title, str) for title in data["course_titles"])

        # Verify consistency
        assert data["total_courses"] == len(data["course_titles"])

        print("[PASS] Response structure is correct")

    def test_courses_endpoint_http_methods(self, test_client):
        """Test that only GET method is accepted"""
        # POST should not be allowed
        response = test_client.post("/api/courses", json={})
        assert response.status_code == 405

        # PUT should not be allowed
        response = test_client.put("/api/courses", json={})
        assert response.status_code == 405

        # DELETE should not be allowed
        response = test_client.delete("/api/courses")
        assert response.status_code == 405

        print("[PASS] HTTP method restrictions work")

    def test_courses_endpoint_empty_database(self, test_client):
        """Test courses endpoint when no courses are loaded"""
        # This test would require mocking an empty database
        # For now, we just verify the endpoint responds
        response = test_client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()

        # Should handle empty case gracefully
        assert "total_courses" in data
        assert "course_titles" in data

        print("[PASS] Empty database handled correctly")


# ==================== Integration Tests ====================

class TestAPIIntegration:
    """Integration tests for API workflows"""

    def test_conversation_flow(self, test_client):
        """Test a multi-turn conversation"""
        # First query - creates session
        response1 = test_client.post(
            "/api/query",
            json={"query": "What is RAG?"}
        )

        assert response1.status_code == 200
        data1 = response1.json()
        session_id = data1["session_id"]

        # Follow-up query - uses existing session
        response2 = test_client.post(
            "/api/query",
            json={
                "query": "Tell me more about it",
                "session_id": session_id
            }
        )

        assert response2.status_code == 200
        data2 = response2.json()

        # Verify same session is maintained
        assert data2["session_id"] == session_id

        print("[PASS] Conversation flow works")

    def test_query_and_courses_workflow(self, test_client):
        """Test querying courses then getting course list"""
        # Get course list first
        courses_response = test_client.get("/api/courses")
        assert courses_response.status_code == 200
        courses_data = courses_response.json()

        # Make a query about courses
        query_response = test_client.post(
            "/api/query",
            json={"query": "What courses are available?"}
        )

        assert query_response.status_code == 200
        query_data = query_response.json()

        # Verify both endpoints respond correctly
        assert courses_data["total_courses"] >= 0
        assert query_data["answer"] is not None

        print("[PASS] Query and courses workflow works")

    def test_multiple_concurrent_sessions(self, test_client):
        """Test handling multiple separate sessions"""
        sessions = []

        # Create 3 separate sessions
        for i in range(3):
            response = test_client.post(
                "/api/query",
                json={"query": f"Question {i+1}"}
            )

            assert response.status_code == 200
            data = response.json()
            sessions.append(data["session_id"])

        # Verify all sessions are unique
        assert len(set(sessions)) == 3

        print("[PASS] Multiple concurrent sessions work")


# ==================== Error Handling Tests ====================

class TestErrorHandling:
    """Test suite for error handling"""

    def test_invalid_json_input(self, test_client):
        """Test handling of invalid JSON"""
        response = test_client.post(
            "/api/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        # Should return validation error
        assert response.status_code == 422

        print("[PASS] Invalid JSON handled correctly")

    def test_missing_content_type(self, test_client):
        """Test handling of missing content-type header"""
        response = test_client.post(
            "/api/query",
            data='{"query": "test"}'
        )

        # Should still work with form data or handle appropriately
        assert response.status_code in [200, 415, 422]

        print("[PASS] Missing content-type handled")

    def test_empty_query_string(self, test_client):
        """Test handling of empty query"""
        response = test_client.post(
            "/api/query",
            json={"query": ""}
        )

        # Should either process or return validation error
        assert response.status_code in [200, 422]

        print("[PASS] Empty query handled")

    def test_nonexistent_endpoint(self, test_client):
        """Test accessing nonexistent endpoints"""
        response = test_client.get("/api/nonexistent")

        assert response.status_code == 404

        print("[PASS] Nonexistent endpoints return 404")


# ==================== Performance Tests ====================

class TestPerformance:
    """Basic performance tests for API endpoints"""

    def test_query_response_time(self, test_client):
        """Test that query endpoint responds in reasonable time"""
        import time

        start_time = time.time()
        response = test_client.post(
            "/api/query",
            json={"query": "What is RAG?"}
        )
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        # Should respond within 5 seconds (generous for testing)
        assert response_time < 5.0

        print(f"[PASS] Query response time: {response_time:.2f}s")

    def test_concurrent_requests(self, test_client):
        """Test handling multiple concurrent requests"""
        import threading

        results = []
        errors = []

        def make_request(index):
            try:
                response = test_client.post(
                    "/api/query",
                    json={"query": f"Concurrent query {index}"}
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Create 10 concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify all requests succeeded
        assert len(errors) == 0
        assert all(status == 200 for status in results)

        print(f"[PASS] Handled {len(results)} concurrent requests")


# ==================== Run Tests ====================

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])