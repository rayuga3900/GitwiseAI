import os
import json
import logging
from gitwise.pipelines.ingestion import run_ingestion   
from gitwise.utils import *
from gitwise.utils.helper import *
setup_logging()



logger = logging.getLogger(__name__)



def ingest_repo(repo_url: str):
    """
    Run ingestion for a repo and save chunks + vector store.
    """
    logging.info(f"--- Inside the Ingestion Pipeline ---")
    logger.info(f"Starting ingestion for {repo_url}")

     
    # REPO_NAME = get_repo_name_from_url(repo_url)
    owner, repo_name = extract_repo_info(repo_url)
    repo_id = normalize_repo_id(owner, repo_name)
    CHUNKS_FILE = f"data/processed/{repo_id}/chunks.json"
    os.makedirs(os.path.dirname(CHUNKS_FILE), exist_ok=True)
    vector_store, embedder, chunks = run_ingestion(repo_url)

    with open(CHUNKS_FILE, "w") as f:
        json.dump(chunks, f, indent=2)
    logger.info(f"Saved chunks to {CHUNKS_FILE}")


    return vector_store, embedder, chunks

if __name__ == "__main__": # ensures script runs only when file is ran directly rather than running the script on imports
    # as that will cause issue for the backend
    repo_url = "https://github.com/rayuga3900/Power-Consumption-Predictor"
    ingest_repo(repo_url)