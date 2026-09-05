# 📊 Retrieval Evaluation & Benchmarks

Detailed performance breakdown comparing **Baseline** vs. **Fine-Tuned** retrieval models across standard Information Retrieval (IR) metrics.

---

## 1. Evaluation Methodology

The evaluation harness evaluates candidate retrieval strategies using a synthetic test suite generated from ingested document chunks:

* **Test Corpus Size**: 100 domain document chunks.
* **Test Queries**: 50 natural language queries with annotated positive ground-truth chunk IDs and hard negatives mined from BM25 false positives.
* **Evaluated Retreivers**:
  1. Dense-only Search (`all-MiniLM-L6-v2`)
  2. Sparse-only Search (`RankBM25`)
  3. Base Hybrid Search (Dense + BM25 + RRF)
  4. Fine-Tuned Hybrid Search (Fine-Tuned MiniLM + RRF + Cross-Encoder Reranker)

---

## 2. Benchmark Metric Results (Example)

| Retrieval Strategy | MRR@10 | NDCG@10 | Recall@5 | Recall@10 | Precision@5 | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BM25 Sparse Only** | 0.512 | 0.548 | 0.620 | 0.710 | 0.420 | 2.1 ms |
| **FAISS Dense Baseline** | 0.642 | 0.689 | 0.720 | 0.810 | 0.540 | 14.5 ms |
| **Base Hybrid RRF** | 0.710 | 0.745 | 0.810 | 0.880 | 0.610 | 18.2 ms |
| **Fine-Tuned Hybrid + Reranker** | **0.815** | **0.841** | **0.910** | **0.960** | **0.720** | **46.0 ms** |

---
