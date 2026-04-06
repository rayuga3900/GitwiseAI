from pydantic import BaseModel

class RepoRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    query: str
    repo_url: str
    top_k: int = 20

class JudgeRequest(BaseModel):
    query: str
    repo_url: str
    response: str
    context_chunks: list | None = None