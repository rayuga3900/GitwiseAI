from sentence_transformers import SentenceTransformer
import logging
import torch

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"  # allowing to use gpu if available
        self.logger.info(f"Loading embedding model: {self.model_name} on {self.device}...")
        self.model = SentenceTransformer(self.model_name, device=self.device)  # Load only once

    def embed_chunks(self, chunks, batch_size=16):
        self.logger.info(f"Generating embeddings for {len(chunks)} chunks...")
    
        all_embeddings = []
    
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
    
            self.logger.debug(f"Processing batch {i}-{i+len(batch)}")
    
            emb = self.model.encode(
                batch,
                show_progress_bar=False,
                normalize_embeddings=True
            )
    
            all_embeddings.extend(emb.tolist())
    
        self.logger.info(f"Generated {len(all_embeddings)} embeddings")
        return all_embeddings
