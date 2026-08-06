import io
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.document import Document

client = TestClient(app)


def _upload_sample_document():
    content = (
        b"insight-rag, dokumanlari parcalayip pgvector ile saklayan bir "
        b"RAG servisidir. Sorular bu parcalar uzerinden cevaplanir."
    )
    response = client.post(
        "/documents",
        files={"file": ("query_test.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _delete_document(document_id):
    db = SessionLocal()
    try:
        db.query(Document).filter(Document.id == document_id).delete()
        db.commit()
    finally:
        db.close()


def test_query_returns_answer_and_sources_with_mocked_llm():
    document_id = _upload_sample_document()
    try:
        with patch(
            "app.api.query.generate_answer", return_value="mocked cevap"
        ) as mock_generate_answer:
            response = client.post(
                "/query", json={"question": "insight-rag ne yapar?"}
            )

        assert response.status_code == 200
        body = response.json()
        assert body["answer"] == "mocked cevap"
        assert len(body["sources"]) > 0
        source = body["sources"][0]
        assert source["document_filename"] == "query_test.txt"
        assert isinstance(source["similarity_score"], float)
        mock_generate_answer.assert_called_once()
    finally:
        _delete_document(document_id)


def test_query_filters_by_document_ids():
    document_id = _upload_sample_document()
    try:
        with patch("app.api.query.generate_answer", return_value="mocked cevap"):
            response = client.post(
                "/query",
                json={
                    "question": "insight-rag ne yapar?",
                    "document_ids": ["00000000-0000-0000-0000-000000000000"],
                },
            )

        assert response.status_code == 200
        assert response.json()["sources"] == []
    finally:
        _delete_document(document_id)


def test_query_rejects_empty_question():
    response = client.post("/query", json={"question": "   "})
    assert response.status_code == 400
