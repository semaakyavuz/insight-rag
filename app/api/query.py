import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document, DocumentChunk
from app.services.embedding import embed_texts
from app.services.llm import generate_answer

router = APIRouter()

TOP_K = 5


class QueryRequest(BaseModel):
    question: str
    document_ids: list[uuid.UUID] | None = None


class SourceChunk(BaseModel):
    chunk_id: uuid.UUID
    chunk_text: str
    similarity_score: float
    document_filename: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


@router.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest, db: Session = Depends(get_db)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty")

    question_embedding = embed_texts([request.question])[0]
    distance = DocumentChunk.embedding.cosine_distance(question_embedding)

    query = db.query(DocumentChunk, Document.filename, distance.label("distance")).join(
        Document, DocumentChunk.document_id == Document.id
    )
    if request.document_ids:
        query = query.filter(DocumentChunk.document_id.in_(request.document_ids))

    results = query.order_by(distance).limit(TOP_K).all()

    if not results:
        return QueryResponse(
            answer="Bu soruyla ilgili yüklenmiş bir doküman bulamadım. "
            "Lütfen önce ilgili bir doküman yükleyin.",
            sources=[],
        )

    sources = [
        SourceChunk(
            chunk_id=chunk.id,
            chunk_text=chunk.chunk_text,
            similarity_score=1 - distance_value,
            document_filename=filename,
        )
        for chunk, filename, distance_value in results
    ]

    try:
        answer = generate_answer(
            request.question, [source.chunk_text for source in sources]
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"LLM service error: {exc}"
        ) from exc

    return QueryResponse(answer=answer, sources=sources)
