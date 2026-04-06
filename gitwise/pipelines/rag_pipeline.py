import json
import logging
import time
import os
from gitwise.pipelines.retrieval import run_retrieval
from generation import run_generation
from gitwise.core import VectorStore, Embedder
from qdrant_client import QdrantClient
from gitwise.config import QDRANT_URL
from gitwise.utils.helper import  extract_repo_info, normalize_repo_id
from gitwise.pipelines.ingestion import run_ingestion
from gitwise.utils.logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def load_chunks(repo_id: str) -> list[dict]:
    """Load pre-processed chunks for a repo."""
    chunks_file = f"data/processed/{repo_id}/chunks.json"
    if not os.path.exists(chunks_file):
        raise FileNotFoundError(f"Chunks file not found for repo {repo_id}")
    with open(chunks_file, "r") as f:
        chunks = json.load(f)
    logger.info(f"Loaded {len(chunks)} chunks from {chunks_file}")
    return chunks


def init_vector_store(repo_id: str) -> VectorStore:
    """Initialize the vector store for a repo."""
    collection_name = f"{repo_id.replace(' ', '_').lower()}_chunks"
    client = QdrantClient(url=QDRANT_URL)
    logger.info(f"Initialized vector store: {collection_name}")
    return VectorStore(client, collection_name)


def init_embedder(model_name: str = "all-MiniLM-L6-v2") -> Embedder:
    """Initialize the embedder model."""
    return Embedder(model_name=model_name)


def ensure_ingestion(repo_url: str):
    """Check if repo chunks exist, re-ingest if needed."""
    owner, repo_name = extract_repo_info(repo_url)
    repo_id = normalize_repo_id(owner, repo_name)
    chunks_file = f"data/processed/{repo_id}/chunks.json"
    if not os.path.exists(chunks_file):
        logger.info(f"Chunks missing or repo changed → re-ingesting: {repo_url}")
        run_ingestion(repo_url)
    return repo_id
 
def compress_chunks(context_chunks, max_length=1000):
    compressed = []
    for chunk in context_chunks:
        content = chunk["content"]
        if len(content) > max_length:
            content = content[:max_length] + "..."   
        compressed.append({
            "id": chunk["id"],
            "content": content,
            "file_name": chunk.get("file_name")
        })
    return compressed

def query_pipeline(repo_url: str, query: str, top_k: int = 10) -> str:
    """
    Perform RAG query: retrieve relevant chunks and generate response.
    """
    start_time = time.time()
    logger.info(f"--- Query Pipeline Start ---")
    logger.info(f"Repo URL: {repo_url}, Query: {query}")

    repo_id = ensure_ingestion(repo_url)
    
    chunks = load_chunks(repo_id)
    vector_store = init_vector_store(repo_id)
    embedder = init_embedder()

    # 1. Retrieve relevant context chunks
    context_chunks = run_retrieval(query, chunks, vector_store, embedder, rerank_top_k=top_k)
 
    # context_chunks = compress_chunks(context_chunks)
    # 2. Generate response using context
    response = run_generation(query, context_chunks)

    logger.info(f"Query pipeline completed in {time.time() - start_time:.2f}s")
    return response



if __name__ == "__main__":
    query = "How does the project handle outliers, skewness, and missing values? Which files handle those?"
    repo_url = "https://github.com/rayuga3900/Power-Consumption-Predictor"
    response = query_pipeline(repo_url, query)
    print(response)