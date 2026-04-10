from sentence_transformers import SentenceTransformer
import logging
import torch

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Loading embedding model: {self.model_name} on {self.device}...")

        self.model = SentenceTransformer(self.model_name, device=self.device)

    def embed_chunks(self, chunks):
        self.logger.info(f"Generating embeddings for {len(chunks)} chunks...")

      
        for i, chunk in enumerate(chunks[:5]):
             # Only show first 100 characters to avoid flooding logs
            self.logger.debug(
                f"Chunk {i}: {chunk[:20]}{'...' if len(chunk) > 20 else ''}"
            )

        embeddings = self.model.encode(
              chunks,
                batch_size=16,             # processes 16 chunks at a time
                show_progress_bar=True,
                normalize_embeddings=True  # Ensures all vectors have unit length[which makes cosine similarity easier]
        )

        self.logger.info(f"Generated embeddings with shape: {embeddings.shape}")

        return embeddings.tolist()
