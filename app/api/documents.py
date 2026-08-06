from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document, DocumentChunk
from app.services.chunking import chunk_text
from app.services.embedding import embed_texts
from app.services.extraction import extract_text

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/documents", status_code=201)
async def upload_document(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail="Only .pdf and .txt files are supported"
        )

    raw_bytes = await file.read()
    text = extract_text(raw_bytes, file.filename)

    if not text.strip():
        raise HTTPException(
            status_code=422, detail="No extractable text found in file"
        )

    document = Document(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
    )
    db.add(document)
    db.flush()

    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_text=chunk,
                chunk_index=index,
                embedding=embedding,
            )
        )

    db.commit()
    db.refresh(document)

    return {
        "id": str(document.id),
        "filename": document.filename,
        "content_type": document.content_type,
        "chunk_count": len(chunks),
    }
