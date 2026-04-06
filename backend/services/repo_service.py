from gitwise.utils.helper import extract_repo_info, normalize_repo_id
from gitwise.core import VectorStore, Embedder
from qdrant_client import QdrantClient
from gitwise.config import QDRANT_URL
import os, json
from backend.session import current_repo_data
from gitwise.pipelines.ingestion_pipeline import ingest_repo, run_ingestion
from git import Repo

def reload_repo(repo_url: str):
    """
    Clears cached repo data and re-ingests the repo.
    Returns updated repo_data
    """
    owner, repo_name = extract_repo_info(repo_url)
    repo_id = normalize_repo_id(owner, repo_name)

    # Remove from cache if exists
    if repo_id in current_repo_data.get("repos", {}):
        del current_repo_data["repos"][repo_id]

    # Re-ingest repo
    vector_store, embedder, chunks = run_ingestion(repo_url,clone_root="data/raw/")

    # Store in cache
    current_repo_data.setdefault("repos", {})[repo_id] = {
        "vector_store": vector_store,
        "embedder": embedder,
        "chunks": chunks
    }

    return current_repo_data["repos"][repo_id]

def needs_reload(repo_url, clone_root="data/raw"):
    """
    Returns True if the local repo doesn't exist or if the remote has new commits.
    """
    owner, repo_name = extract_repo_info(repo_url)
    repo_id = normalize_repo_id(owner, repo_name)
    local_path = os.path.join(clone_root, repo_id)

    if not os.path.exists(local_path):
        # Repo not cloned yet
        return True

    try:
        repo = Repo(local_path)
        # Fetch latest commits from origin
        repo.remotes.origin.fetch()
        remote_commit = repo.remotes.origin.refs[repo.active_branch.name].commit.hexsha
        local_commit = repo.head.commit.hexsha
        return remote_commit != local_commit
    except Exception as e:
        # If anything fails, re-ingest
        return True
def get_or_load_repo(repo_url: str):
    """
    if session cache has the repo data use that 
    else try to load from the disk if available
    """
    owner, repo_name = extract_repo_info(repo_url)
    repo_id = normalize_repo_id(owner, repo_name)

    repos = current_repo_data.setdefault("repos", {})

    # Check session cache first
    if repo_id in repos:
        return repos[repo_id]
    
    # Load chunks from disk if available
    chunks_file = f"data/processed/{repo_id}/chunks.json"
    if not os.path.exists(chunks_file):
        return None

    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    client = QdrantClient(url=QDRANT_URL)
    collection_name = f"{repo_id}_chunks"

    if not client.collection_exists(collection_name):
        return None
    
    # Create repo_data and store in session cache
    repo_data = {
        "vector_store": VectorStore(client, collection_name=collection_name),
        "embedder": Embedder(model_name="all-MiniLM-L6-v2"),
        "chunks": chunks
    }

    repos[repo_id] = repo_data
    return repo_data