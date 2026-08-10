import io
import uuid

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.document import Document

client = TestClient(app)


def _delete_document(document_id):
    db = SessionLocal()
    try:
        db.query(Document).filter(Document.id == document_id).delete()
        db.commit()
    finally:
        db.close()


def test_duplicate_upload_returns_409():
    content = f"duplicate detection testi {uuid.uuid4().hex}".encode()
    document_id = None
    try:
        first = client.post(
            "/documents",
            files={"file": ("dup_test.txt", io.BytesIO(content), "text/plain")},
        )
        assert first.status_code == 201
        document_id = first.json()["id"]

        second = client.post(
            "/documents",
            files={"file": ("dup_test.txt", io.BytesIO(content), "text/plain")},
        )
        assert second.status_code == 409
        assert "zaten yüklü" in second.json()["detail"]
    finally:
        if document_id:
            _delete_document(document_id)


def test_same_content_different_filename_is_still_a_duplicate():
    content = f"ayni icerik farkli isim {uuid.uuid4().hex}".encode()
    document_id = None
    try:
        first = client.post(
            "/documents",
            files={"file": ("a.txt", io.BytesIO(content), "text/plain")},
        )
        assert first.status_code == 201
        document_id = first.json()["id"]

        second = client.post(
            "/documents",
            files={"file": ("b.txt", io.BytesIO(content), "text/plain")},
        )
        assert second.status_code == 409
    finally:
        if document_id:
            _delete_document(document_id)
