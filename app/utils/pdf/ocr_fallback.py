import pytesseract
from pdf2image import convert_from_path
import re

def ocr_pdf(filepath: str) -> str:
    try:
        images = convert_from_path(filepath, dpi=300)
        full_text = []

        for img in images:
            text = pytesseract.image_to_string(
                img,
                lang="eng",
                config="--oem 3 --psm 6"
            )
            full_text.append(text)

        combined = "\n".join(full_text)

        # Basic cleanup
        combined = re.sub(r"\s+", " ", combined)
        combined = combined.strip()

        return combined

    except Exception as e:
        print(f"[OCR ERROR] {e}")
        return ""
