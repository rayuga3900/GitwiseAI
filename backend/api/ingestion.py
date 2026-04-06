from fastapi import APIRouter
from gitwise.pipelines.ingestion_pipeline import ingest_repo  
from backend.session import current_repo_data
from backend.schemas import RepoRequest 
from gitwise.utils.helper import extract_repo_info, normalize_repo_id
router = APIRouter()

@router.post("/")
def ingest_repo_endpoint(request: RepoRequest):
    vector_store, embedder, chunks = ingest_repo(request.repo_url)

    owner, repo_name = extract_repo_info(request.repo_url)
    repo_id = normalize_repo_id(owner, repo_name)

    repos = current_repo_data.setdefault("repos", {})

    repos[repo_id] = {
        "vector_store": vector_store,
        "embedder": embedder,
        "chunks": chunks,
         
    }

    return {
        "message": f"Ingested repo {request.repo_url}",
        "num_chunks": len(chunks)
    }