import hashlib

def generate_hash(text: str) -> str:
    normalized = " ".join(text.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def generate_uid(*parts: str) -> str:
    combined = "|".join(p.strip().lower() for p in parts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()
