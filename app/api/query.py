import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.document import Document, DocumentChunk
from app.services.embedding import embed_texts
from app.services.llm import generate_answer

router = APIRouter()

TOP_K = 5
HISTORY_PAIR_LIMIT = 3
TITLE_MAX_LENGTH = 50


class QueryRequest(BaseModel):
    question: str
    document_ids: list[uuid.UUID] | None = None
    conversation_id: uuid.UUID | None = None


class SourceChunk(BaseModel):
    chunk_id: uuid.UUID
    chunk_text: str
    similarity_score: float
    document_filename: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    conversation_id: uuid.UUID


def _get_or_create_conversation(
    db: Session, request: QueryRequest
) -> Conversation:
    if request.conversation_id:
        conversation = db.get(Conversation, request.conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=404, detail="Conversation not found"
            )
        return conversation

    conversation = Conversation(title=request.question.strip()[:TITLE_MAX_LENGTH])
    db.add(conversation)
    db.flush()
    return conversation


def _load_recent_history(
    db: Session, conversation_id: uuid.UUID
) -> list[dict[str, str]]:
    recent_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(HISTORY_PAIR_LIMIT * 2)
        .all()
    )
    return [
        {"role": message.role, "content": message.content}
        for message in reversed(recent_messages)
    ]


@router.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest, db: Session = Depends(get_db)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty")

    conversation = _get_or_create_conversation(db, request)
    history = _load_recent_history(db, conversation.id)

    question_embedding = embed_texts([request.question])[0]
    distance = DocumentChunk.embedding.cosine_distance(question_embedding)

    query = db.query(DocumentChunk, Document.filename, distance.label("distance")).join(
        Document, DocumentChunk.document_id == Document.id
    )
    if request.document_ids:
        query = query.filter(DocumentChunk.document_id.in_(request.document_ids))

    results = query.order_by(distance).limit(TOP_K).all()

    if not results:
        answer = (
            "Bu soruyla ilgili yüklenmiş bir doküman bulamadım. "
            "Lütfen önce ilgili bir doküman yükleyin."
        )
        sources: list[SourceChunk] = []
    else:
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
                request.question,
                [source.chunk_text for source in sources],
                history=history,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail=f"LLM service error: {exc}"
            ) from exc

    db.add(
        Message(conversation_id=conversation.id, role="user", content=request.question)
    )
    db.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            sources=[source.model_dump(mode="json") for source in sources],
        )
    )
    db.commit()

    return QueryResponse(answer=answer, sources=sources, conversation_id=conversation.id)
