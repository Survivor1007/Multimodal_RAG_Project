import pytest
import numpy as np
from app.ml.embeddings.text_embedder import TextEmbedder

@pytest.mark.asyncio
async def test_text_embedder_dimension_and_output():
    embedder = TextEmbedder()
    texts = ["Hybrid search using FAISS and BM25", "Cross-Encoder reranking"]
    
    embeddings = await embedder.embed_text(texts)
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == 2
    assert embeddings.shape[1] == 384  # MiniLM-L6 embedding dimension

@pytest.mark.asyncio
async def test_text_embedder_empty_list():
    embedder = TextEmbedder()
    embeddings = await embedder.embed_text([])
    assert embeddings.shape[0] == 0
