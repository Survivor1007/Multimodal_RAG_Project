import os
import json
import torch
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

def run_fine_tuning(
    dataset_file: str = "data/synthetic_dataset.json",
    output_dir: str = "models/fine_tuned_minilm",
    base_model_name: str = "all-MiniLM-L6-v2",
    epochs: int = 2,
    batch_size: int = 4
):
    """
    Lightweight CPU-friendly fine-tuning of sentence-transformer model using MultipleNegativesRankingLoss.
    Runs fast on laptop hardware without overloading CPU/RAM.
    """
    print(f"🚀 Starting lightweight fine-tuning of '{base_model_name}'...")
    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

    if not os.path.exists(dataset_file):
        from .generate_synthetic_dataset import generate_synthetic_dataset
        generate_synthetic_dataset(dataset_file)

    with open(dataset_file, "r", encoding="utf-8") as f:
        samples = json.load(f)

    train_examples = []
    for sample in samples:
        query = sample["query"]
        pos = sample["positive_chunk"]
        # Add (query, positive) pairs for MultipleNegativesRankingLoss
        train_examples.append(InputExample(texts=[query, pos]))

    model = SentenceTransformer(base_model_name)
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
    train_loss = losses.MultipleNegativesRankingLoss(model)

    os.makedirs(output_dir, exist_ok=True)

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=epochs,
        warmup_steps=1,
        output_path=output_dir,
        show_progress_bar=True
    )

    print(f"🎉 Fine-tuning complete! Model saved to '{output_dir}'")

if __name__ == "__main__":
    run_fine_tuning()
