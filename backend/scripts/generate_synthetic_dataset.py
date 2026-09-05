import os
import json
import random

def generate_synthetic_dataset(output_file: str = "data/synthetic_dataset.json"):
    """
    Generate a lightweight synthetic dataset of (query, positive_chunk, hard_negatives)
    for contrastive fine-tuning and evaluation.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    synthetic_samples = [
        {
            "query": "How does Reciprocal Rank Fusion combine vector and keyword search?",
            "positive_chunk": "Reciprocal Rank Fusion (RRF) evaluates position ranks across FAISS dense semantic search and BM25 sparse keyword search using weighted reciprocal formulas.",
            "hard_negatives": [
                "PostgreSQL async SQLAlchemy ORM provides relational document storage and query logging.",
                "FastAPI uses Pydantic schemas for strict payload validation and automatic OpenAPI generation."
            ]
        },
        {
            "query": "What model is used for cross-modal vision text search?",
            "positive_chunk": "The system utilizes OpenAI CLIP (clip-vit-base-patch32) to project both text queries and visual media into a shared 512-dimensional vector space for multimodal retrieval.",
            "hard_negatives": [
                "RankBM25 is a term frequency-idf keyword algorithm optimized for exact phrase matching.",
                "Cross-Encoder reranking scores candidate pairs using multi-head self-attention mechanisms."
            ]
        },
        {
            "query": "What happens when internal retrieval confidence drops below threshold?",
            "positive_chunk": "When internal search confidence score falls below 0.65, adaptive Tavily web search is triggered to augment context with real-time web results.",
            "hard_negatives": [
                "Recursive character splitting breaks raw text into 500-token chunks with 50-token overlap.",
                "The React frontend relies on Tailwind CSS v3 and Framer Motion for glassmorphism UI components."
            ]
        },
        {
            "query": "How are document uploads processed during ingestion?",
            "positive_chunk": "Ingested documents are extracted into text, chunked using token splitters, embedded via SentenceTransformers into FAISS, and indexed in BM25.",
            "hard_negatives": [
                "Groq LLM generates answers based on retrieved context prompts with temperature controls.",
                "Structlog produces structured JSON logs for backend monitoring and per-step latency profiling."
            ]
        },
        {
            "query": "What per-step latency metrics are measured during RAG execution?",
            "positive_chunk": "Microsecond profiling tracks query expansion, text embedding, FAISS search, BM25 search, CLIP search, RRF fusion, Tavily web search, reranking, and LLM generation.",
            "hard_negatives": [
                "Dark mode state is synchronized with localStorage and root HTML dark classes in Zustand.",
                "The Cross-Encoder model outputs logit relevance scores normalized via sigmoid functions."
            ]
        }
    ]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(synthetic_samples, f, indent=2)

    print(f"✅ Generated {len(synthetic_samples)} synthetic fine-tuning samples at '{output_file}'")

if __name__ == "__main__":
    generate_synthetic_dataset()
