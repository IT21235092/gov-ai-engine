import pytesseract
import pdf2image
import re


HS_CODE_PATTERN = re.compile(r"\b\d{4}\.\d{2}\.\d{2}\b|\b\d{4}\.\d{2}\b")
RATE_PATTERN = re.compile(r"Rs\.?\s?\d+(?:\/-)?")
UNIT_PATTERN = re.compile(r"per\s?kg|per\s?ct|per\s?carat", re.IGNORECASE)


def extract_table_rows_from_scanned_pdf(local_pdf_path: str):
    """
    Extract table rows from scanned gazettes using OCR + HS-code anchoring.
    This works even when no grid lines exist.
    """

    images = pdf2image.convert_from_path(local_pdf_path, dpi=300)
    extracted_rows = []

    for img in images:
        text = pytesseract.image_to_string(img, config="--psm 6")

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        for line in lines:
            if not HS_CODE_PATTERN.search(line):
                continue

            rate = RATE_PATTERN.search(line)
            unit = UNIT_PATTERN.search(line)

            extracted_rows.append({
                "raw_row": line,
                "hs_code": HS_CODE_PATTERN.search(line).group(),
                "rate": rate.group() if rate else None,
                "unit": unit.group() if unit else None
            })

    return extracted_rows
