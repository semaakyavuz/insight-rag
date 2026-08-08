import io
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.document import Document

client = TestClient(app)


def _upload_sample_document():
    content = b"Konusma gecmisi testleri icin ornek bir belge."
    response = client.post(
        "/documents",
        files={
            "file": ("conversation_test.txt", io.BytesIO(content), "text/plain")
        },
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


def _create_conversation(question: str):
    document_id = _upload_sample_document()
    with patch("app.api.query.generate_answer", return_value="test cevabi"):
        response = client.post("/query", json={"question": question})
    assert response.status_code == 200
    return response.json()["conversation_id"], document_id


def test_list_conversations_returns_lightweight_summary():
    conversation_id, document_id = _create_conversation("liste testi sorusu?")
    try:
        response = client.get("/conversations")
        assert response.status_code == 200

        matching = next(
            (c for c in response.json() if c["id"] == conversation_id), None
        )
        assert matching is not None
        assert matching["title"] == "liste testi sorusu?"
        assert "messages" not in matching
    finally:
        client.delete(f"/conversations/{conversation_id}")
        _delete_document(document_id)


def test_list_conversations_orders_newest_first():
    id_a, doc_a = _create_conversation("ilk soru?")
    id_b, doc_b = _create_conversation("ikinci soru?")
    try:
        response = client.get("/conversations")
        ids = [c["id"] for c in response.json()]
        assert ids.index(id_b) < ids.index(id_a)
    finally:
        client.delete(f"/conversations/{id_a}")
        client.delete(f"/conversations/{id_b}")
        _delete_document(doc_a)
        _delete_document(doc_b)


def test_get_conversation_returns_ordered_messages():
    conversation_id, document_id = _create_conversation("detay testi sorusu?")
    try:
        response = client.get(f"/conversations/{conversation_id}")
        assert response.status_code == 200

        body = response.json()
        assert len(body["messages"]) == 2
        assert body["messages"][0]["role"] == "user"
        assert body["messages"][0]["content"] == "detay testi sorusu?"
        assert body["messages"][1]["role"] == "assistant"
        assert body["messages"][1]["content"] == "test cevabi"
    finally:
        client.delete(f"/conversations/{conversation_id}")
        _delete_document(document_id)


def test_get_conversation_not_found():
    response = client.get("/conversations/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_delete_conversation_removes_it():
    conversation_id, document_id = _create_conversation("silme testi sorusu?")
    try:
        delete_response = client.delete(f"/conversations/{conversation_id}")
        assert delete_response.status_code == 204

        get_response = client.get(f"/conversations/{conversation_id}")
        assert get_response.status_code == 404
    finally:
        _delete_document(document_id)


def test_delete_conversation_not_found():
    response = client.delete("/conversations/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
