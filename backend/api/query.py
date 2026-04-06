from fastapi import APIRouter, HTTPException
from gitwise.pipelines.retrieval import run_retrieval
from gitwise.pipelines.generation import run_generation
from backend.schemas import QueryRequest 
from backend.services.repo_service import get_or_load_repo, reload_repo, needs_reload
from fastapi.concurrency import run_in_threadpool
router = APIRouter()
 
@router.post("/")


 
async def query_endpoint(request: QueryRequest, reload: bool = False):
    if reload or needs_reload(request.repo_url):
        repo_data = await run_in_threadpool(reload_repo, request.repo_url)
    else:
        repo_data = get_or_load_repo(request.repo_url)
        if not repo_data:
            raise HTTPException(status_code=400, detail="Repo not ingested yet. Use reload=True to ingest.")

    chunks = repo_data["chunks"]
    vector_store = repo_data["vector_store"]
    embedder = repo_data["embedder"]

    context_chunks = await run_in_threadpool(
        run_retrieval,
        request.query, chunks, vector_store, embedder, request.top_k
    )

    response = await run_in_threadpool(
        run_generation, request.query, context_chunks
    )

    return {
        "response": response,
        "retrieved_chunks": [chunk["content"] for chunk in context_chunks]
    }