from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from app.db.database import SessionLocal, GovernmentNotice
from app.utils.hash_utils import generate_hash, generate_uid
from app.utils.pdf.pdf_downloader import download_pdf
from app.utils.pdf.pdf_text_extractor import extract_text_from_pdf
from app.utils.pdf.ocr_fallback import ocr_pdf
import time

GAZETTE_URL = "https://www.treasury.gov.lk/acts-gazettes-circulars"

def scrape_gazette():
    print("[INFO] Launching browser...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(GAZETTE_URL, timeout=60000)
        page.wait_for_selector("table", timeout=60000)
        time.sleep(3)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tbody tr")

    print(f"[INFO] Found {len(rows)} gazette rows")

    db = SessionLocal()

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        date = cols[0].get_text(strip=True)
        title = cols[3].get_text(strip=True)
        link_tag = cols[4].find("a")

        if not link_tag:
            continue

        pdf_url = link_tag.get("href")
        if not pdf_url.startswith("http"):
            pdf_url = "https://www.treasury.gov.lk" + pdf_url

        print(f"[INFO] Processing: {title}")

        pdf_path = download_pdf(pdf_url)
        if not pdf_path:
            continue

        text = extract_text_from_pdf(pdf_path)
        if not text:
            print("[INFO] Scanned PDF detected → OCR")
            text = ocr_pdf(pdf_path)

        if not text or len(text) < 500:
            print("[WARN] Unusable text, skipping")
            continue

        content_hash = generate_hash(text)
        notice_uid = generate_uid(title, "treasury_gazette")

        # 1️⃣ Exact duplicate check
        if db.query(GovernmentNotice)\
            .filter(GovernmentNotice.content_hash == content_hash)\
            .first():
            print("[SKIP] Exact duplicate")
            continue

        # 2️⃣ Check for previous versions
        latest = db.query(GovernmentNotice)\
            .filter(GovernmentNotice.notice_uid == notice_uid)\
            .order_by(GovernmentNotice.version.desc())\
            .first()

        if latest:
            version = latest.version + 1
            is_update = True
            previous_id = latest.id
            print(f"[UPDATE] New version detected (v{version})")
        else:
            version = 1
            is_update = False
            previous_id = None

        notice = GovernmentNotice(
            notice_uid=notice_uid,
            title=title,
            source="Ministry of Finance - Treasury",
            source_url=pdf_url,
            content=text,
            content_hash=content_hash,
            published_date=date,
            version=version,
            is_update=is_update,
            previous_notice_id=previous_id
        )

        db.add(notice)
        db.commit()

        print(f"[SAVED] Gazette v{version}")

    db.close()
