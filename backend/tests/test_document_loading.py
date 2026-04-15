"""Test document loading to diagnose startup issues"""

import os
import sys

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from rag_system import RAGSystem


class TestDocumentLoading:
    """Test document loading functionality"""

    def test_docs_folder_exists(self):
        """Test that docs folder exists"""
        docs_path = "../docs"
        absolute_path = os.path.abspath(docs_path)

        print(f"[INFO] Docs relative path: {docs_path}")
        print(f"[INFO] Docs absolute path: {absolute_path}")
        print(f"[INFO] Docs exists: {os.path.exists(absolute_path)}")

        # Check from backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        docs_from_backend = os.path.join(backend_dir, "..", "docs")
        docs_from_backend_abs = os.path.abspath(docs_from_backend)

        print(f"[INFO] Docs from backend: {docs_from_backend_abs}")
        print(f"[INFO] Docs from backend exists: {os.path.exists(docs_from_backend_abs)}")

        assert os.path.exists(
            docs_from_backend_abs
        ), f"Docs folder not found at {docs_from_backend_abs}"

    def test_load_documents(self):
        """Test actual document loading"""
        rag_system = RAGSystem(config)

        # Try different path resolutions
        possible_paths = [
            "../docs",  # Relative from backend
            "../../docs",  # Relative from tests
            "./docs",  # Current directory
            "/mnt/e/github_project/STARTING_CODEBASE/starting_ragchatbot_codebase/docs",  # Absolute Linux path
        ]

        docs_loaded = False
        for docs_path in possible_paths:
            absolute_path = os.path.abspath(docs_path)
            print(f"[INFO] Trying path: {absolute_path}")
            print(f"[INFO] Exists: {os.path.exists(absolute_path)}")

            if os.path.exists(absolute_path):
                try:
                    print(f"[INFO] Attempting to load from: {absolute_path}")
                    courses, chunks = rag_system.add_course_folder(
                        absolute_path, clear_existing=True
                    )
                    print(f"[INFO] Loaded {courses} courses with {chunks} chunks")
                    docs_loaded = True
                    break
                except Exception as e:
                    print(f"[ERROR] Failed to load from {absolute_path}: {e}")
                    import traceback

                    traceback.print_exc()

        assert docs_loaded, "Failed to load documents from any path"

        # Verify data was loaded
        analytics = rag_system.get_course_analytics()
        print(f"[INFO] Final analytics: {analytics}")

        assert analytics["total_courses"] > 0, "No courses were loaded"
        assert len(analytics["course_titles"]) > 0, "No course titles found"

        print(f"[PASS] Successfully loaded {analytics['total_courses']} courses")

    def test_individual_document_loading(self):
        """Test loading individual documents"""
        rag_system = RAGSystem(config)

        # Try to find and load individual documents
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        docs_path = os.path.join(base_path, "docs")

        print(f"[INFO] Base path: {base_path}")
        print(f"[INFO] Docs path: {docs_path}")
        print(f"[INFO] Docs exists: {os.path.exists(docs_path)}")

        if os.path.exists(docs_path):
            files = [f for f in os.listdir(docs_path) if f.endswith(".txt")]
            print(f"[INFO] Found {len(files)} txt files")

            if files:
                # Try loading first file
                test_file = os.path.join(docs_path, files[0])
                print(f"[INFO] Testing load of: {test_file}")

                try:
                    course, chunks = rag_system.add_course_document(test_file)
                    print(f"[INFO] Loaded course: {course.title if course else 'None'}")
                    print(f"[INFO] Chunks created: {chunks}")

                    if course:
                        print(f"[PASS] Successfully loaded {course.title}")
                    else:
                        print(f"[FAIL] Failed to load course")

                except Exception as e:
                    print(f"[ERROR] Exception loading document: {e}")
                    import traceback

                    traceback.print_exc()


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
