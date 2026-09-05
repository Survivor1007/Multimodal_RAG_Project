import pytest
from app.ml.chunking.document_chunker import DocumentChunker

def test_document_chunker_text_splitting(sample_text):
    chunker = DocumentChunker(chunk_size=100, overlap=20)
    chunks = chunker.chunk_text(sample_text)

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all("content" in c and "chunk_index" in c for c in chunks)

def test_document_chunker_empty_input():
    chunker = DocumentChunker()
    chunks = chunker.chunk_text("")
    assert chunks == []
