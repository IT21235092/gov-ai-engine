from pdfminer.high_level import extract_text

MIN_VALID_TEXT_LENGTH = 500

def extract_text_from_pdf(filepath: str) -> str:
    try:
        text = extract_text(filepath)
        if not text:
            return ""

        text = text.strip()

        # Too short → probably scanned
        if len(text) < MIN_VALID_TEXT_LENGTH:
            return ""

        return text

    except Exception:
        return ""
