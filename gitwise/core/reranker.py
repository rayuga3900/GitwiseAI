import logging
import torch
from sentence_transformers import CrossEncoder


class Reranker:
    """
    BGE Cross-Encoder Reranker.

    Scores (query, document) pairs and returns the best ranked documents.
    """
    #    BAAI/bge-reranker-base -> old reranker replaced cause of memory issue 
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", top_k: int = 10):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.model_name = model_name
        
        self.top_k = top_k

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.logger.info(f"Loading reranker model: {self.model_name} on {self.device}")

        self.model = CrossEncoder(self.model_name, device=self.device)

    def rerank(self, query: str, documents: list):

        if not documents:
            self.logger.warning("No documents provided for reranking.")
            return []
     
        pairs = [(query, doc["content"]) for doc in documents]

        self.logger.info(f"Reranking {len(documents)} documents")

        scores = self.model.predict(pairs, batch_size=16)

        # Combining docs + scores
        scored_docs = [{"id": d["id"], "content": d["content"], "score": float(s), **d}
                    for d, s in zip(documents, scores)]

       # Deduplicating  by content
        seen_contents = set()
        unique_scored_docs = []
        for doc in scored_docs:
            content = doc["content"].strip()
            if content not in seen_contents:
                unique_scored_docs.append(doc)
                seen_contents.add(content)

        # Sort by score descending
        unique_scored_docs.sort(key=lambda x: x["score"], reverse=True)

        # Take top_k
        # threshold = 0.05
        # filtered = [d for d in unique_scored_docs if d["score"] > threshold]

        # if len(filtered) >= self.top_k:
        #     top_docs = filtered[:self.top_k]
        # else:
        #     top_docs = unique_scored_docs[:self.top_k]
        top_docs = unique_scored_docs[:self.top_k]
    

        # Logging 
        log_entries = []
        for idx, doc in enumerate(top_docs, start=1):
            content_preview = doc["content"].strip().replace("\n", " ")  # remove line breaks
            log_entries.append(
               f"{idx}. id={doc['id']}, score={doc['score']:.4f}, content={content_preview[:50]}..."
            )

        self.logger.info("Best chunks after reranking:\n" + "\n".join(log_entries))
        self.logger.info(f"Returning top {len(top_docs)} reranked documents")

        return top_docs
