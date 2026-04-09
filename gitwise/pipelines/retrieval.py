from gitwise.core import HybridRetriever,Reranker
from rank_bm25 import BM25Okapi
import re
import logging
from gitwise.utils.logger_config import setup_logging
import time 
setup_logging()
logger = logging.getLogger(__name__)

def run_retrieval(query: str, chunks: list, vector_store, embedder, rerank_top_k= 20):
    start_time = time.time()
    logger.info(f"Running retrieval for query: {query}")
    logger.info(f"Using {len(chunks)} chunks as corpus")

    # Preparing documents for BM25
    documents = [c["content"] for c in chunks]
    doc_ids = [c["id"] for c in chunks]
    tokenized_docs = [re.findall(r'\w+', doc.lower()) for doc in documents]
    logger.debug("Initializing BM25...")
    bm25 = BM25Okapi(tokenized_docs)
    bm25_data = {"bm25": bm25, "doc_ids": doc_ids, "documents": documents,  "metadatas": [c["metadata"] for c in chunks]}
    logger.info("BM25 retriever ready")

    # Hybrid retriever
    hr = HybridRetriever(
        dense_store=vector_store,
        dense_embedder=embedder,
        bm25_data=bm25_data,
        top_k_dense = 20,
        top_k_sparse = 20,
        top_k_final = 10
    )
    logger.info("Running hybrid dense + sparse retrieval...")
    hybrid_results = hr.retrieve(query)
    logger.info(f"Retrieved {len(hybrid_results)} initial results")
    context_chunks = [{"id": r['id'], "content": r["content"], "file_name": r.get("file_name") } for r in hybrid_results]

    # --- Rerank ---
    logger.info(f"Reranking top {rerank_top_k} results...")
    rr = Reranker(top_k=rerank_top_k)
    top_docs = rr.rerank(query, context_chunks)
    logger.info(f"Returning {len(top_docs)} top context chunks")
    logger.info(f"Retrieval completed in {time.time() - start_time:.2f}s")
    
   
    return top_docs
