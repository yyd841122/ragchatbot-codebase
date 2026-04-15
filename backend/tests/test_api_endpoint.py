"""Test the actual API endpoint to diagnose frontend issues"""

import os
import sys
import time

import pytest
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAPIEndpoint:
    """Test the actual FastAPI endpoints"""

    @pytest.fixture
    def api_base_url(self):
        """Base URL for API testing"""
        return "http://127.0.0.1:8000"

    def test_api_health(self, api_base_url):
        """Test that API is running"""
        try:
            response = requests.get(f"{api_base_url}/", timeout=5)
            print(f"[INFO] API Status: {response.status_code}")
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip(
                "API server not running - start with: cd backend && uv run uvicorn app:app --reload --port 8000"
            )

    def test_query_endpoint_simple(self, api_base_url):
        """Test simple query via API"""
        try:
            response = requests.post(
                f"{api_base_url}/api/query",
                json={"query": "What is RAG?", "session_id": None},
                timeout=30,
            )

            print(f"[INFO] API Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"[INFO] Response keys: {data.keys()}")
                print(f"[INFO] Answer preview: {data.get('answer', 'No answer')[:100]}...")
                print(f"[INFO] Sources count: {len(data.get('sources', []))}")

                # Check for error indicators
                answer = data.get("answer", "")
                if "查询失败" in answer or "error" in answer.lower():
                    print(f"[ERROR] API returned error: {answer}")
                    pytest.fail(f"API returned error: {answer}")

                assert "answer" in data
                assert "sources" in data
                assert "session_id" in data

                print("[PASS] Query endpoint works")
            else:
                print(f"[ERROR] API returned status {response.status_code}: {response.text}")
                pytest.fail(f"API returned status {response.status_code}")

        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")

    def test_query_endpoint_course_specific(self, api_base_url):
        """Test course-specific query via API"""
        try:
            response = requests.post(
                f"{api_base_url}/api/query",
                json={"query": "How does ChromaDB work?", "session_id": None},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")

                print(f"[INFO] Course-specific query response: {answer[:100]}...")

                # Check for error indicators
                if "查询失败" in answer or "error" in answer.lower():
                    print(f"[ERROR] API returned error: {answer}")
                    pytest.fail(f"API returned error: {answer}")

                print("[PASS] Course-specific query works")
            else:
                pytest.fail(f"API returned status {response.status_code}")

        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")

    def test_query_endpoint_irrelevant(self, api_base_url):
        """Test irrelevant query via API"""
        try:
            response = requests.post(
                f"{api_base_url}/api/query",
                json={"query": "What is the weather in Tokyo?", "session_id": None},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")

                print(f"[INFO] Irrelevant query response: {answer[:100]}...")

                # Should gracefully handle irrelevant queries
                if "查询失败" in answer:
                    print(f"[ERROR] API returned '查询失败' for irrelevant query")
                    pytest.fail("API should handle irrelevant queries gracefully")

                print("[PASS] Irrelevant query handled gracefully")
            else:
                pytest.fail(f"API returned status {response.status_code}")

        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")

    def test_courses_endpoint(self, api_base_url):
        """Test courses statistics endpoint"""
        try:
            response = requests.get(f"{api_base_url}/api/courses", timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"[INFO] Courses data: {data}")
                print("[PASS] Courses endpoint works")
            else:
                pytest.fail(f"API returned status {response.status_code}")

        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
