import sys
import pytest
import asyncio
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_text():
    return """
    Multimodal Hybrid RAG System is a platform for semantic search.
    It uses Reciprocal Rank Fusion (RRF) to combine FAISS dense vector search and BM25 sparse keyword search.
    Cross-encoder reranking is applied to refine the top candidate chunks.
    """

@pytest.fixture
def sample_query():
    return "What algorithm is used for rank fusion?"
