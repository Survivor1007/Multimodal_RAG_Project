import os
import sys
import pytest

def run_tests():
    """
    Run all unit & integration tests for chunking, embeddings, FAISS, BM25, RRF, reranker, and API endpoints.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_dir = os.path.join(project_root, "backend", "tests")

    print(f"🧪 Running Pytest Test Suite in '{test_dir}'...")

    sys.path.insert(0, os.path.join(project_root, "backend"))

    exit_code = pytest.main([
        test_dir,
        "-v",
        "-ra",
        "--tb=short"
    ])

    if exit_code == 0:
        print("\n✅ All unit & integration tests passed successfully!")
    else:
        print(f"\n❌ Tests completed with exit code: {exit_code}")

    sys.exit(exit_code)

if __name__ == "__main__":
    run_tests()
