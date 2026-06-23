import re
from typing import Optional
from pydantic import BaseModel
from loguru import logger
from utils.date_utils import extract_dates_from_text, parse_date_string


class TemporalMetadata(BaseModel):
    created_at: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    temporal_confidence: float = 0.5
    temporal_signals: list[str] = []


# Patterns that indicate a document creation/effective date
EFFECTIVE_DATE_PATTERNS = [
    r'effective\s+([A-Z][a-z]+\s+\d{4})',
    r'effective\s+(\d{4}-\d{2}-\d{2})',
    r'revised\s+([A-Z][a-z]+\s+\d{4})',
    r'updated\s+([A-Z][a-z]+\s+\d{4})',
    r'as\s+of\s+([A-Z][a-z]+\s+\d{4})',
    r'date[d]?\s*:\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
    r'(\d{4}-\d{2}-\d{2})',
    r'([A-Z][a-z]+\s+\d{4})',   # "March 2021"
]

VALID_UNTIL_PATTERNS = [
    r'expires?\s+([A-Z][a-z]+\s+\d{4})',
    r'until\s+([A-Z][a-z]+\s+\d{4})',
    r'through\s+([A-Z][a-z]+\s+\d{4})',
]


def extract_temporal_metadata(
    text: str,
    fallback_date: Optional[str] = None
) -> TemporalMetadata:
    """
    Extract temporal metadata using regex only — no LLM calls.
    Fast, free, no rate limits. Good enough for most documents.
    """
    signals = extract_dates_from_text(text)
    created_at = None
    valid_until = None
    confidence = 0.3

    # Try effective/revised/updated date patterns first
    for pattern in EFFECTIVE_DATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            parsed = parse_date_string(date_str)
            if parsed:
                created_at = parsed.strftime("%Y-%m-%d")
                confidence = 0.85
                break

    # Try valid_until patterns
    for pattern in VALID_UNTIL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            parsed = parse_date_string(date_str)
            if parsed:
                valid_until = parsed.strftime("%Y-%m-%d")
                break

    # Fall back to any year found in text
    if not created_at:
        year_match = re.search(r'\b(20\d{2})\b', text)
        if year_match:
            created_at = f"{year_match.group(1)}-01-01"
            confidence = 0.5

    # Fall back to provided date
    if not created_at and fallback_date:
        created_at = fallback_date
        confidence = 0.2

    logger.debug(f"Date extracted: {created_at} (confidence={confidence})")

    return TemporalMetadata(
        created_at=created_at,
        valid_until=valid_until,
        temporal_confidence=confidence,
        temporal_signals=signals[:5],
    )