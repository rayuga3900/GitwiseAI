from fastapi import FastAPI
from backend.api import ingestion, query, judge

app = FastAPI(title="Gitwise RAG API")

# Include routers(help us attach router to our fastapi application. so that application can use all the end points defined in that router)
app.include_router(ingestion.router, prefix="/ingest", tags=["Ingestion"])# all ingestion files routes will start with /ingest
# ingestion.router refers to the router defined inside backend/api/ingestion.py
# router group of end points[where we want to go]
# prefix - a common path for all endpoints in the router[help us organize the endpoints]
# tags are used for the dyanmic document generation (Swagger UI / Redoc)
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(judge.router, prefix="/judge", tags=["Judge"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Gitwise RAG API"}

