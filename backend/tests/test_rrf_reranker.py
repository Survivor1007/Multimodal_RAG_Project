import pytest
from app.ml.ranking.rrf_ranker import RRF_Ranker
from app.ml.ranking.reranker import CrossEncoderReranker

def test_rrf_ranker_fusion():
    rrf = RRF_Ranker(k=60)
    # Simulated top-k lists from FAISS and BM25
    faiss_list = [(1, 0.9), (2, 0.8), (3, 0.7)]
    bm25_list = [(2, 12.0), (1, 10.0), (4, 8.0)]

    fused = rrf.fuse([faiss_list, bm25_list], weights=[1.0, 1.0])
    assert isinstance(fused, list)
    assert len(fused) > 0
    # Chunk 1 and 2 present in both lists should have highest fusion scores
    top_ids = [item[0] for item in fused[:2]]
    assert 1 in top_ids and 2 in top_ids

@pytest.mark.asyncio
async def test_cross_encoder_reranker():
    reranker = CrossEncoderReranker()
    query = "What is Reciprocal Rank Fusion?"
    candidates = [
        (1, 0.03, "Reciprocal Rank Fusion (RRF) evaluates position ranks across multiple retrievers."),
        (2, 0.02, "PostgreSQL stores relational schemas and JSON query telemetry."),
    ]

    reranked = await reranker.rerank(query, candidates)
    assert isinstance(reranked, list)
    assert len(reranked) == 2
    assert reranked[0][0] == 1  # Chunk 1 should rank higher for the query
