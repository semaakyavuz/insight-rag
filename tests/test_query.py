import io
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.document import Document

client = TestClient(app)


def _upload_sample_document():
    content = (
        "insight-rag, dokumanlari parcalayip pgvector ile saklayan bir "
        "RAG servisidir. Sorular bu parcalar uzerinden cevaplanir. "
        f"test-id:{uuid.uuid4().hex}"
    ).encode()
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


def _delete_conversation(conversation_id):
    if conversation_id:
        client.delete(f"/conversations/{conversation_id}")


def test_query_returns_answer_and_sources_with_mocked_llm():
    document_id = _upload_sample_document()
    conversation_id = None
    try:
        with patch(
            "app.api.query.generate_answer", return_value="mocked cevap"
        ) as mock_generate_answer:
            response = client.post(
                "/query", json={"question": "insight-rag ne yapar?"}
            )

        assert response.status_code == 200
        body = response.json()
        conversation_id = body["conversation_id"]
        assert body["answer"] == "mocked cevap"
        assert len(body["sources"]) > 0
        source = body["sources"][0]
        assert source["document_filename"] == "query_test.txt"
        assert isinstance(source["similarity_score"], float)
        mock_generate_answer.assert_called_once()
    finally:
        _delete_conversation(conversation_id)
        _delete_document(document_id)


def test_query_filters_by_document_ids():
    document_id = _upload_sample_document()
    conversation_id = None
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
        conversation_id = response.json()["conversation_id"]
        assert response.json()["sources"] == []
    finally:
        _delete_conversation(conversation_id)
        _delete_document(document_id)


def test_query_rejects_empty_question():
    response = client.post("/query", json={"question": "   "})
    assert response.status_code == 400


def test_query_creates_conversation_with_title_from_question():
    document_id = _upload_sample_document()
    conversation_id = None
    try:
        long_question = "Bu " * 30 + "soru?"
        with patch("app.api.query.generate_answer", return_value="cevap"):
            response = client.post("/query", json={"question": long_question})

        assert response.status_code == 200
        conversation_id = response.json()["conversation_id"]

        detail = client.get(f"/conversations/{conversation_id}")
        assert detail.status_code == 200
        body = detail.json()
        assert body["title"] == long_question.strip()[:50]
        assert len(body["messages"]) == 2
        assert body["messages"][0]["role"] == "user"
        assert body["messages"][0]["content"] == long_question
        assert body["messages"][1]["role"] == "assistant"
        assert body["messages"][1]["content"] == "cevap"
    finally:
        _delete_conversation(conversation_id)
        _delete_document(document_id)


def test_query_injects_recent_history_into_llm_call():
    document_id = _upload_sample_document()
    conversation_id = None
    try:
        with patch("app.api.query.generate_answer", return_value="ilk cevap"):
            first_response = client.post(
                "/query", json={"question": "insight-rag nedir?"}
            )
        assert first_response.status_code == 200
        conversation_id = first_response.json()["conversation_id"]

        with patch(
            "app.api.query.generate_answer", return_value="ikinci cevap"
        ) as mock_generate_answer:
            second_response = client.post(
                "/query",
                json={
                    "question": "peki nasil calisiyor?",
                    "conversation_id": conversation_id,
                },
            )

        assert second_response.status_code == 200
        assert second_response.json()["conversation_id"] == conversation_id

        _, kwargs = mock_generate_answer.call_args
        history = kwargs["history"]
        assert {"role": "user", "content": "insight-rag nedir?"} in history
        assert {"role": "assistant", "content": "ilk cevap"} in history
    finally:
        _delete_conversation(conversation_id)
        _delete_document(document_id)


def test_query_with_unknown_conversation_id_returns_404():
    response = client.post(
        "/query",
        json={
            "question": "soru?",
            "conversation_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert response.status_code == 404
