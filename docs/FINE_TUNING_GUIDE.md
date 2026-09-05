# 🧠 CPU-Friendly Fine-Tuning & Evaluation Guide

This guide details how to generate synthetic domain datasets, fine-tune dense sentence-transformers and cross-encoders on CPU/laptop hardware, and evaluate retrieval metrics (MRR@K, NDCG@K, Recall@K).

---

## 1. Overview of Lightweight Fine-Tuning

Training large models requires expensive GPUs. However, for retrieval engineering, **fine-tuning small 22M–33M parameter models** (`all-MiniLM-L6-v2`, `ms-marco-MiniLM-L-6-v2`) on domain-specific corpora yields substantial recall gains while running efficiently on CPU within **5–15 minutes**.

---

## 2. Step 1: Synthetic Dataset Generation

To fine-tune a dense embedder using contrastive learning, you need `(query, positive_passage, hard_negative_passage)` triplets.

Run the synthetic data generator:

```bash
python -m backend.scripts.generate_synthetic_dataset
```

### Generated Data Format (`backend/data/synthetic_dataset.json`):
```json
[
  {
    "query": "What is the hybrid retrieval strategy used in the system?",
    "positive_chunk": "The system uses Reciprocal Rank Fusion (RRF) to combine FAISS dense search and BM25 sparse search...",
    "hard_negatives": [
      "FastAPI handles async request routing using Pydantic schemas...",
      "PostgreSQL stores user metadata and query log telemetry..."
    ]
  }
]
```

---

## 3. Step 2: Fine-Tuning the Dense Embedder (`all-MiniLM-L6-v2`)

The fine-tuning script uses `sentence-transformers` with `MultipleNegativesRankingLoss`:

```bash
python -m backend.scripts.fine_tune_embedder
```

### Training Configuration:
* **Base Model**: `sentence-transformers/all-MiniLM-L6-v2`
* **Loss Function**: `MultipleNegativesRankingLoss` (InfoNCE contrastive loss)
* **Epochs**: 3
* **Batch Size**: 16 (CPU optimized)
* **Optimizer**: AdamW with warmup linear schedule (`learning_rate=2e-5`)
* **Output Path**: `backend/models/fine_tuned_minilm`

---

## 4. Step 3: Evaluating Retrieval Performance

Run the evaluation runner to compare **Baseline vs. Fine-Tuned Model**:

```bash
python -m backend.scripts.evaluate_retrieval
```

### Evaluated Metrics:
* **Mean Reciprocal Rank (MRR@10)**: Measures the average inverse rank of the first relevant document.
* **NDCG@10**: Normalized Discounted Cumulative Gain accounting for document relevance position.
* **Recall@5 & Recall@10**: Percentage of ground-truth relevant chunks retrieved in top K.
* **Precision@5**: Percentage of retrieved top 5 chunks that are relevant.

### Benchmark Comparison Output:
```plaintext
=====================================================================
                      RETRIEVAL EVALUATION REPORT
=====================================================================
Metric              Baseline (MiniLM-L6)    Fine-Tuned (MiniLM-L6)   Delta
---------------------------------------------------------------------
MRR@10              0.6420                 0.8150                  +26.9%
NDCG@10             0.6890                 0.8410                  +22.0%
Recall@5            0.7200                 0.9100                  +26.3%
Precision@5         0.5400                 0.7200                  +33.3%
---------------------------------------------------------------------
Evaluation status: Baseline vs Fine-Tuned complete.
```

---

## 5. Step 4: Loading Fine-Tuned Weights into Backend

Set the `.env` configuration file in `backend/.env`:

```env
EMBEDDING_MODEL_PATH=backend/models/fine_tuned_minilm
```

Restart the FastAPI server:

```bash
uvicorn backend.main:app --reload
```

The system will automatically load your custom fine-tuned weights for dense retrieval.
