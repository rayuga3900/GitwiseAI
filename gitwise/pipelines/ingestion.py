import os
import pickle
import uuid
import json
import hashlib
import logging
import time

from gitwise.core import DataLoader, Chunker, Embedder, VectorStore
from qdrant_client import QdrantClient
from gitwise.utils.helper import extract_repo_info, normalize_repo_id
from gitwise.config import QDRANT_URL
from gitwise.utils.logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def compute_hash(texts: list[str]) -> str:
    """Compute a single hash for a list of texts."""
    m = hashlib.md5()
    for t in texts:
        m.update(t.encode())
    return m.hexdigest()


def load_old_chunks(chunks_file: str) -> dict:
    """Load previously ingested chunks and return mapping to preserve UUIDs."""
    if not os.path.exists(chunks_file):
        return {}
    with open(chunks_file, "r") as f:
        old_chunks = json.load(f)
    old_map = {
        (c["metadata"].get("file_name", ""),
         c["metadata"].get("start_index", 0),
         c["metadata"].get("end_index", 0)): c["id"]
        for c in old_chunks
    }
    return old_map


def assign_chunk_ids(chunks: list[dict], old_map: dict, repo_id: str) -> None:
    """Assign UUIDs to chunks, reusing existing ones where possible."""
    for chunk in chunks:
        key = (
            chunk["metadata"].get("file_name", ""),
            chunk["metadata"].get("start_index", 0),
            chunk["metadata"].get("end_index", 0)
        )
        if key in old_map:
            chunk["id"] = old_map[key]
        else:
            chunk["id"] = str(uuid.uuid4())
            chunk["metadata"]["repo_name"] = repo_id


def save_chunks(chunks: list[dict], chunks_file: str) -> None:
    """Save chunks to JSON file."""
    os.makedirs(os.path.dirname(chunks_file), exist_ok=True)
    with open(chunks_file, "w") as f:
        json.dump(chunks, f, indent=2)
    logger.info(f"Saved {len(chunks)} chunks to {chunks_file}")


def compute_or_load_embeddings(texts: list[str], embedder: Embedder, cache_file: str) -> list[list[float]]:
    """Compute embeddings or use cached ones if available."""
    current_hash = compute_hash(texts)
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            cache = pickle.load(f)
        if cache.get("hash") == current_hash:
            logger.info("Using cached embeddings")
            return cache["embeddings"]

    logger.info("Computing new embeddings")
    embeddings = embedder.embed_chunks(texts)
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "wb") as f:
        pickle.dump({"hash": current_hash, "embeddings": embeddings}, f)
    return embeddings


def insert_vectors(vector_store: VectorStore, uuids: list[str], embeddings: list[list[float]], payloads: list[dict]):
    """Insert embeddings into the vector store."""
    vector_store.create_collection()
    try:
        vector_store.insert_update_vector(
            uuids, embeddings=embeddings, payloads=payloads, batch_size=200, delay=0.1
        )
    except Exception as e:
        logger.error(f"Vector insertion failed: {e}")
        raise



# Main Ingestion Function
def run_ingestion(repo_url: str, clone_root="data/raw/"):
    start_time = time.time()
    owner, repo_name = extract_repo_info(repo_url)
    repo_id = normalize_repo_id(owner, repo_name)
    logger.info(f"Starting ingestion for repo: {repo_url} (ID: {repo_id})")

    CHUNKS_FILE = f"data/processed/{repo_id}/chunks.json"
    CACHE_FILE = f"data/processed/{repo_id}/embeddings_cache.pkl"
    collection_name = f"{repo_id.replace(' ', '_').lower()}_chunks"


    # 1: Loading & Chunking Data

    data_loader = DataLoader(repo_url=repo_url, clone_root=clone_root)
    files = data_loader.data_loading()
    chunker = Chunker(chunk_size=500, overlap=100)
    chunks = chunker.chunk_content(files)
    logger.info(f"Generated {len(chunks)} chunks from repo files")


    # 2: Assigning UUIDs

    old_map = load_old_chunks(CHUNKS_FILE)
    assign_chunk_ids(chunks, old_map, repo_id)
    save_chunks(chunks, CHUNKS_FILE)

 
    # 3: Computing embeddings
  
    texts = [c["content"] for c in chunks]
    uuids = [c["id"] for c in chunks]
    payloads = [
        {
            "file_name": c["metadata"].get("path"),
            "file_type": c["metadata"].get("file_type"),
            "start_index": c["metadata"].get("start_index"),
            "end_index": c["metadata"].get("end_index"),
            "commit_hash": c["metadata"].get("commit"),
            "content": c["content"],
            "repo_id": repo_id
        }
        for c in chunks
    ]

    embedder = Embedder(model_name="all-MiniLM-L6-v2")
    embeddings = compute_or_load_embeddings(texts, embedder, CACHE_FILE)
 
    #  4: Inserting into Vector Store
 
    client = QdrantClient(url=QDRANT_URL)
    vector_store = VectorStore(client, collection_name=collection_name, vector_dim=384)
    logger.info(f"inserting in vector database")
    insert_vectors(vector_store, uuids, embeddings, payloads)

    logger.info(f"Ingestion completed in {time.time() - start_time:.2f}s")
    return vector_store, embedder, chunks
