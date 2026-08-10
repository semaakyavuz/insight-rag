"""Remove duplicate Document rows (same filename), keeping the newest upload.

Usage:
    python scripts/cleanup_duplicates.py            # dry run, shows what would be deleted
    python scripts/cleanup_duplicates.py --confirm  # actually deletes
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func

from app.database import SessionLocal
from app.models.document import Document


def find_duplicate_filenames(db) -> list[str]:
    rows = (
        db.query(Document.filename)
        .group_by(Document.filename)
        .having(func.count(Document.id) > 1)
        .all()
    )
    return [filename for (filename,) in rows]


def cleanup(dry_run: bool = True) -> None:
    db = SessionLocal()
    try:
        filenames = find_duplicate_filenames(db)
        if not filenames:
            print("Duplicate doküman bulunamadı.")
            return

        total_deleted = 0
        for filename in filenames:
            documents = (
                db.query(Document)
                .filter(Document.filename == filename)
                .order_by(Document.uploaded_at.desc())
                .all()
            )
            keep, remove = documents[0], documents[1:]
            print(
                f"'{filename}': {len(documents)} kayıt bulundu — "
                f"{keep.id} tutulacak (en yeni, {keep.uploaded_at})"
            )
            for doc in remove:
                print(
                    f"  siliniyor: {doc.id} "
                    f"({len(doc.chunks)} chunk, {doc.uploaded_at})"
                )
                if not dry_run:
                    db.delete(doc)
                total_deleted += 1

        if dry_run:
            print(
                f"\n[DRY RUN] {total_deleted} duplicate kayıt silinecekti. "
                "Gerçekten silmek için --confirm kullan."
            )
        else:
            db.commit()
            print(f"\n{total_deleted} duplicate kayıt silindi.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Aynı filename'e sahip duplicate Document kayıtlarını temizler."
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Belirtilmezse yalnızca ne silineceğini gösterir (dry run).",
    )
    args = parser.parse_args()
    cleanup(dry_run=not args.confirm)
