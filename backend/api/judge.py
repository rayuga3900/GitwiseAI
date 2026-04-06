from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from gitwise.dynamic_eval import judge_answer, scoring_generator  
import re 
from backend.schemas import JudgeRequest
from gitwise.pipelines.retrieval import run_retrieval
from backend.services.repo_service import get_or_load_repo

router = APIRouter()
 


def clean_response(response: str, max_length=1000) -> str:
    if not response:
        return ""
    # Remove markdown bold/italic
    response = re.sub(r"[*_]", "", response)
    # Normalize unicode hyphens
    response = response.replace("‑", "-")
    # Remove extra whitespace / line breaks
    response = " ".join(response.split())
    # Truncate to max_length
    return response[:max_length]
 
@router.post("/")
async def judge_endpoint(request: JudgeRequest):
    repo_data = get_or_load_repo(request.repo_url)

    if not repo_data:
        raise HTTPException(status_code=400, detail="Repo not ingested yet.")

    if request.context_chunks:
        context_chunks = request.context_chunks
    else:
        context_chunks = await run_in_threadpool(
            run_retrieval,
            request.query,
            repo_data["chunks"],
            repo_data["vector_store"],
            repo_data["embedder"],
            20
        )

    clean_resp = clean_response(request.response)

    # run_in_threadpool to run synchronous CPU-bound code without blocking the async event loop
    score = await run_in_threadpool(
        judge_answer,
        request.query,
        clean_resp,
        context_chunks,
        scoring_generator
    )

    return {"score": score}