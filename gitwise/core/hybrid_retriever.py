import logging
import re

class HybridRetriever:

    def __init__(self, dense_store, dense_embedder, bm25_data=None ,top_k_dense=20, top_k_sparse=10, top_k_final=20):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.dense_store = dense_store
        self.dense_embedder = dense_embedder
        self.top_k_dense = top_k_dense
        self.top_k_sparse = top_k_sparse
        self.top_k_final = top_k_final
        if bm25_data:
            self.bm25 = bm25_data["bm25"]
            self.doc_ids = bm25_data["doc_ids"]
            self.documents = bm25_data["documents"]
            self.metadatas = bm25_data.get("metadatas", [{} for _ in self.documents])

    # Dense retrieval: vector store returns top-K similar document chunks 
    # along with similarity scores and metadata (stored in payload)
    def _dense_retrieval(self, query):
        query_vec = self.dense_embedder.embed_chunks([query])[0]
        results = self.dense_store.search_vectors(query_vec, limit=self.top_k_dense)
        dense_scores = [r.score for r in results]
        normalized_dense_scores = self._normalize_scores(dense_scores) # Normalize scores to [0, 1] so dense and sparse scores are comparable before combining them
 
        return [
            {"id": r.id, "content": r.payload.get("content", ""), "file_name": r.payload.get("file_name"), "score": normalized_dense_scores[i]}
            for i, r in enumerate(results)
        ]

    # BM25 returns relevance scores for all documents (indexed by position).
    # We maintain document content, IDs, and metadata separately, and use the 
    # ranked indices to retrieve and return the top-K matching documents.
    def _sparse_retrieval(self, query):
        if not self.bm25:
            return []
        # Tokenizing query into words (ignore punctuation and case) to ensure 
        # consistent matching with BM25's tokenized document corpus
        # as punctuation become differnt token example : "handle-skewness" vs "handle skewness"
        tokenized_query = re.findall(r'\w+', query.lower())
        # bm25 scores
        scores = self.bm25.get_scores(tokenized_query)
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.top_k_sparse]#list of indices of the top-scoring documents
        results = []
        for i in ranked_indices:
            results.append({
                "id": self.doc_ids[i],
                "content": self.documents[i],
                "file_name": self.metadatas[i].get("file_name"),
                "score": scores[i]  
            })

        # Normalize scores
        sparse_scores = [r["score"] for r in results]
        normalized_sparse_scores = self._normalize_scores(sparse_scores) # Normalize scores to [0, 1] so dense and sparse scores are comparable before combining them
        for i, r in enumerate(results):
            r["score"] = normalized_sparse_scores[i]
    
        return results
    
    def _normalize_scores(self, scores):
        if not scores:  
            return []
        min_score, max_score = min(scores), max(scores)
        if max_score - min_score == 0:
            return [1.0 for _ in scores]   
        return [(s - min_score) / (max_score - min_score) for s in scores]
    
    def retrieve(self, query):
        self.logger.info(f"Running hybrid retrieval for: {query}")
        dense_results = self._dense_retrieval(query)
        sparse_results = self._sparse_retrieval(query)

        dense_weight = 0.7
        sparse_weight = 0.3
        # Weighting help us control the contribution based on the importance of semantic vs keyword signals.
        # dense contributes 70% and sparse 30% to the final score.
        merged = {}   

        # Adding dense results
        for r in dense_results:
            merged[r["id"]] = {
                "id": r["id"],
                "content": r["content"],
                "score": r["score"] * dense_weight
            }

        # Adding sparse results
        for r in sparse_results:
            if r["id"] in merged:
                merged[r["id"]]["score"] += r["score"] * sparse_weight
            else:
                merged[r["id"]] = {
                    "id": r["id"],
                    "content": r["content"],
                    "score": r["score"] * sparse_weight
                }
        
        ranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
        return ranked[:self.top_k_final]