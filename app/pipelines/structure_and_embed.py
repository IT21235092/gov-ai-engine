from app.db.database import SessionLocal, GovernmentNotice
from app.utils.text_structuring import extract_structured_data
from app.utils.vector_store import VectorStore

def process_notices():
    print("[PIPELINE] Starting structure + embed pipeline")

    db = SessionLocal()
    vector = VectorStore()

    notices = db.query(GovernmentNotice)\
        .filter(GovernmentNotice.structured_data == None)\
        .all()

    if not notices:
        print("[PIPELINE] No unprocessed notices found")
        return

    for notice in notices:
        print(f"[PIPELINE] Processing notice {notice.id}")

        structured = extract_structured_data(notice.content)
        notice.structured_data = structured
        db.commit()

        # Embed meta
        vector.add(
            text=str(structured["meta"]),
            metadata={
                "notice_id": notice.id,
                "type": "meta",
                "title": notice.title
            }
        )

        # Embed each table row
        for row in structured["tables"]:
            vector.add(
                text=f'{row["hs_code"]} {row["description"]} {row["rate_value"]}',
                metadata={
                    "notice_id": notice.id,
                    "type": "table",
                    "hs_code": row["hs_code"]
                }
            )

        print(f"[PIPELINE] Done notice {notice.id}")

    db.close()
