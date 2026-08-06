from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.api.query import router as query_router

app = FastAPI(title="insight-rag")

app.include_router(documents_router)
app.include_router(query_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
