import pytest
import numpy as np
from app.ml.retrieval.bm25_manager import BM25Manager
from app.ml.retrieval.faiss_manager import FAISSManager

def test_bm25_manager_indexing_and_search():
    bm25 = BM25Manager()
    chunks = [
        {"chunk_id": 1, "content": "Reciprocal Rank Fusion evaluates positions across FAISS and BM25."},
        {"chunk_id": 2, "content": "FastAPI is a modern web framework for Python."},
        {"chunk_id": 3, "content": "PostgreSQL provides relational storage for vector applications."}
    ]

    bm25.fit(chunks)
    assert bm25.is_indexed is True

    results = bm25.search("Reciprocal Rank Fusion", k=2)
    assert len(results) > 0
    assert results[0][0] == 1  # Top match should be chunk_id 1

@pytest.mark.asyncio
async def test_faiss_manager_add_and_search(tmp_path):
    index_file = str(tmp_path / "test_faiss.index")
    faiss_mgr = FAISSManager(index_path=index_file)

    embeddings = np.random.randn(3, 384).astype(np.float32)
    # L2 normalize
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    chunk_ids = [101, 102, 103]

    await faiss_mgr.add_embeddings(embeddings, chunk_ids, index_type="text")
    assert faiss_mgr.text_index.ntotal == 3

    results = await faiss_mgr.search(embeddings[0], k=2, index_type="text")
    assert len(results) > 0
    assert results[0][0] == 101  # Exact match for first embedding
