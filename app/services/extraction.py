import io

from pypdf import PdfReader


def extract_text(raw_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return _extract_pdf_text(raw_bytes)
    return raw_bytes.decode("utf-8", errors="ignore")


def _extract_pdf_text(raw_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)
