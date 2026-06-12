from __future__ import annotations

import re
from .models import LeaseRequest


def parse_lease_request(text: str) -> LeaseRequest:
    operator = _extract_operator(text)
    weight = _extract_weight(text)
    height = _extract_height(text)
    tower_id = _extract_tower_id(text)
    return LeaseRequest(
        operator=operator,
        equipment_weight_kg=weight,
        equipment_height_m=height,
        tower_id=tower_id,
        raw_text=text,
    )


def _extract_operator(text: str) -> str:
    m = re.search(r"[Oo]perator\s+([A-Za-z\s]+?)(?:\s+(?:wants|requests|wishes|plans))", text)
    if m:
        return m.group(1).strip()
    m = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s+(?:wants|requests|wishes|plans)", text)
    if m:
        return m.group(1).strip()
    return "Unknown"


def _extract_weight(text: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)\s*[-]?\s*kg", text, re.IGNORECASE)
    return float(m.group(1)) if m else 0.0


def _extract_height(text: str) -> float | None:
    patterns = [
        r"height\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*m",
        r"at\s+(?:a\s+)?(?:height\s+(?:of\s+)?)?(\d+(?:\.\d+)?)\s*m(?:eters?)?",
        r"(\d+(?:\.\d+)?)\s*m(?:eters?)?\s+height",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return float(m.group(1))
    return None


def _extract_tower_id(text: str) -> str:
    m = re.search(r"(TWR-\d+)", text, re.IGNORECASE)
    return m.group(1).upper() if m else "UNKNOWN"
