from typing import List, Dict, Any
import re


class DocumentChunker:
      """Lightweight, dependency-free document chunker with overlap."""

      def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap

      def chunk_text(self, text: str, metadata: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
            """Split text into overlapping chunks using simple regex + sliding window."""
            if not text or not text.strip():
                  return []

            # Clean and split into sentences/paragraphs
            text = re.sub(r'\s+', ' ', text).strip()
            sentences = re.split(r'(?<=[.!?])\s+', text)

            chunks = []
            current_chunk = ""
            chunk_index = 0

            for sentence in sentences:
                  if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                        chunks.append({
                              "content": current_chunk.strip(),
                              "chunk_index": chunk_index,
                              "chunk_type": "text",
                              "metadata": metadata or {}
                        })
                        chunk_index += 1
                        # Overlap: keep last part of previous chunk
                        current_chunk = current_chunk[-self.chunk_overlap:] + " " + sentence
                  else:
                        current_chunk += " " + sentence

            if current_chunk.strip():
                  chunks.append({
                  "content": current_chunk.strip(),
                  "chunk_index": chunk_index,
                  "chunk_type": "text",
                  "metadata": metadata or {}
                  })

            return chunks

      def chunk_image_description(self, description: str, image_path: str, metadata: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
            """Create single chunk for image with description."""
            if not description or not description.strip():
                  return []
            return [{
                  "content": description.strip(),
                  "chunk_index": 0,
                  "chunk_type": "image",
                  "metadata": {
                  **(metadata or {}),
                  "image_path": image_path
                  }
            }]