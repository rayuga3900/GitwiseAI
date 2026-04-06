import logging

class Retriever:
    def __init__(self, vector_store, embedder, top_k=5):
        """
        Args:
            vector_store: your VectorStore instance
            embedder: your Embedder instance
            top_k: number of chunks to retrieve
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.vector_store = vector_store
        self.embedder = embedder
        self.top_k = top_k

    def retrieve(self, query):
        """
        Returns the top-k relevant chunks for the query.
        """
        #  Embedding the query
        query_vec = self.embedder.embed_chunks([query])[0]
        self.logger.info(f"Query vector : {query_vec[:10]}")

        #  Search the vector store, qdrant returns score for each retrieved vector
        results = self.vector_store.search_vectors(query_vec, limit=self.top_k)
        self.logger.info(f"retrieved results: {[r.payload.get('content', '')[:10] for r in results]}")
  
        return results