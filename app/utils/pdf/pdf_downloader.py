import requests
import os

PDF_DIR = "data/pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

def download_pdf(url: str) -> str | None:
    try:
        filename = url.split("/")[-1].split("?")[0]
        filepath = os.path.join(PDF_DIR, filename)

        if os.path.exists(filepath):
            return filepath

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

        return filepath

    except Exception as e:
        print(f"[ERROR] PDF download failed: {e}")
        return None
