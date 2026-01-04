import re
from typing import List, Dict

# -----------------------------
# CORE REGEX (FROM REAL GAZETTES)
# -----------------------------

ACT_REGEX = r"(.*?Act,?\s+No\.?\s*\d+\s+of\s+\d{4})"
SECTION_REGEX = r"Section[s]?\s+([\d, and]+)"
MINISTER_REGEX = r"(Anura\s+Kumara\s+Dissanayake|Minister\s+of\s+Finance.*)"
DATE_REGEX = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}"

HS_HEADING_REGEX = r"^\d{2}\.\d{2}$"
HS_CODE_REGEX = r"\d{4}\.\d{2}(\.\d{2})?"
RATE_REGEX = r"(Rs\.?\s?\d+(\.\d+)?|USD\s?\d+(\.\d+)?|\d+%|\d+\s*cents)"
UNIT_REGEX = r"(per\s+kg|per\s+ct|Per\s+Kg|Per\s+Ct)"

# -----------------------------
# META EXTRACTION
# -----------------------------

def extract_meta(text: str) -> Dict:
    meta = {
        "act": None,
        "sections": [],
        "minister": None,
        "effective_from": None,
        "valid_until": None
    }

    act = re.search(ACT_REGEX, text)
    if act:
        meta["act"] = act.group(1).strip()

    sections = re.findall(SECTION_REGEX, text)
    meta["sections"] = list(set(sections))

    minister = re.search(MINISTER_REGEX, text)
    if minister:
        meta["minister"] = minister.group(1).strip()

    dates = re.findall(DATE_REGEX, text)
    if dates:
        meta["effective_from"] = dates[0]
        if len(dates) > 1:
            meta["valid_until"] = dates[-1]

    return meta

# -----------------------------
# TABLE RECONSTRUCTION (OCR SAFE)
# -----------------------------

def extract_tables(text: str) -> List[Dict]:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    rows = []

    current_heading = None

    for i, line in enumerate(lines):
        # Detect HS Heading
        if re.match(HS_HEADING_REGEX, line):
            current_heading = line
            continue

        # Detect HS Code row
        hs_code = re.search(HS_CODE_REGEX, line)
        rate = re.search(RATE_REGEX, line)
        unit = re.search(UNIT_REGEX, line)

        if hs_code and rate:
            description = line
            description = re.sub(HS_CODE_REGEX, "", description)
            description = re.sub(RATE_REGEX, "", description)
            description = re.sub(UNIT_REGEX, "", description)

            rows.append({
                "hs_heading": current_heading,
                "hs_code": hs_code.group(),
                "description": description.strip(" -"),
                "rate_value": rate.group(),
                "rate_unit": unit.group() if unit else None
            })

    return rows

# -----------------------------
# MAIN ENTRY
# -----------------------------

def extract_structured_data(text: str) -> Dict:
    return {
        "meta": extract_meta(text),
        "tables": extract_tables(text)
    }
