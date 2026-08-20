import re

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
ACCOUNT_RE = re.compile(r"\b(?:ACC|ACCOUNT)[-_ ]?\d{4,}\b", re.I)
CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")

def mask_pii(text: str) -> str:
    """Mask common PII before text is sent to an external model."""
    if not text:
        return text
    text = EMAIL_RE.sub("[EMAIL_REDACTED]", text)
    text = PHONE_RE.sub("[PHONE_REDACTED]", text)
    text = ACCOUNT_RE.sub("[ACCOUNT_REDACTED]", text)
    text = CARD_RE.sub("[CARD_REDACTED]", text)
    return text

def mask_payload(payload):
    """Recursively mask strings in dicts/lists/tuples."""
    if isinstance(payload, str):
        return mask_pii(payload)
    if isinstance(payload, dict):
        return {k: mask_payload(v) for k, v in payload.items()}
    if isinstance(payload, list):
        return [mask_payload(v) for v in payload]
    if isinstance(payload, tuple):
        return tuple(mask_payload(v) for v in payload)
    return payload
