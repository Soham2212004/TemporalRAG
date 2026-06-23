from datetime import datetime, timezone
from typing import Optional
import re
from dateutil import parser as dateutil_parser


def parse_date_string(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return dateutil_parser.parse(date_str, fuzzy=True).replace(tzinfo=timezone.utc)
    except Exception:
        return None


def extract_dates_from_text(text: str) -> list[str]:
    patterns = [
        r'\b\d{4}-\d{2}-\d{2}\b',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',
        r'\bQ[1-4]\s+\d{4}\b',
        r'(?:as of|updated|effective|since|from)\s+[A-Z][a-z]+\s+\d{4}',
        r'(?:as of|updated|effective|since|from)\s+\d{4}',
    ]
    found = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.extend(matches)
    return list(set(found))


def days_between(date1: datetime, date2: datetime) -> int:
    if not date1 or not date2:
        return 0
    d1 = date1.replace(tzinfo=timezone.utc) if date1.tzinfo is None else date1
    d2 = date2.replace(tzinfo=timezone.utc) if date2.tzinfo is None else date2
    return abs((d2 - d1).days)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
