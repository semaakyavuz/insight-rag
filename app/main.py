from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.api.query import router as query_router

app = FastAPI(title="insight-rag")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(documents_router)
app.include_router(query_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
