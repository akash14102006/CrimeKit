"""
Entity extraction module for CrimeKit.

Provides ML-based entity extraction using GLiNER (when available)
with automatic fallback to enhanced regex extraction.

Supported entity types:
PERSON, PHONE, EMAIL, DEVICE, ACCOUNT, USERNAME, SOCIAL_HANDLE,
IP_ADDRESS, DOMAIN, URL, LOCATION, ORGANIZATION, VEHICLE, CASE_ID,
DATE, TIME, CRIME_REFERENCE, FINANCIAL_IDENTIFIER, DOCUMENT_ID
"""

import re
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── GLiNER lazy loading ──

_gliner_model = None
_gliner_available = None


def _load_gliner():
    """Lazy-load GLiNER model. Returns model or None."""
    global _gliner_model, _gliner_available
    if _gliner_available is not None:
        return _gliner_model
    try:
        from gliner import GLiNER
        model_name = os.getenv("GLINER_MODEL", "urchade/gliner_mediumv2.1")
        _gliner_model = GLiNER.from_pretrained(model_name)
        _gliner_available = True
        logger.info("GLiNER model loaded: %s", model_name)
    except ImportError:
        _gliner_available = False
        logger.info("GLiNER not installed — using regex fallback")
    except Exception as e:
        _gliner_available = False
        logger.warning("GLiNER load failed: %s — using regex fallback", e)
    return _gliner_model


# ── Entity type labels for GLiNER ──

GLINER_LABELS = [
    "person", "phone", "email", "device", "account", "username",
    "social handle", "ip address", "domain", "url", "location",
    "organization", "vehicle", "case id", "date", "time",
    "crime reference", "financial identifier", "document id",
]

# Map GLiNER labels to our canonical types
LABEL_MAP = {
    "person": "PERSON",
    "phone": "PHONE",
    "email": "EMAIL",
    "device": "DEVICE",
    "account": "ACCOUNT",
    "username": "USERNAME",
    "social handle": "SOCIAL_HANDLE",
    "ip address": "IP_ADDRESS",
    "domain": "DOMAIN",
    "url": "URL",
    "location": "LOCATION",
    "organization": "ORGANIZATION",
    "vehicle": "VEHICLE",
    "case id": "CASE_ID",
    "date": "DATE",
    "time": "TIME",
    "crime reference": "CRIME_REFERENCE",
    "financial identifier": "FINANCIAL_IDENTIFIER",
    "document id": "DOCUMENT_ID",
}


# ── Enhanced regex patterns (fallback + supplementary) ──

REGEX_PATTERNS: Dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "URL": re.compile(r"https?://\S+"),
    "DATE": re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    "TIME": re.compile(r"\b(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?)\b"),
    "PHONE": re.compile(
        r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}"
    ),
    "IP_ADDRESS": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "DOMAIN": re.compile(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b"),
    "USERNAME": re.compile(r"(?:@|(?<!\w))[a-zA-Z][a-zA-Z0-9_]{2,15}\b"),
    "SOCIAL_HANDLE": re.compile(r"@[a-zA-Z][a-zA-Z0-9_]{2,15}"),
    "CASE_ID": re.compile(r"\b(?:CASE|CRIME|INV|REF)[\s-]?\d{3,10}\b", re.IGNORECASE),
    "DOCUMENT_ID": re.compile(
        r"\b(?:DOC|DOCID|FILE|FIL)[\s-]?\d{3,10}\b", re.IGNORECASE
    ),
    "FINANCIAL_IDENTIFIER": re.compile(
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
    ),
    "VEHICLE": re.compile(
        r"\b[A-Z]{1,3}[\s-]?\d{1,4}[\s-]?[A-Z]{1,3}\b"
    ),
    "PROPER_NAME": re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b"),
    "ORGANIZATION": re.compile(
        r"\b(?:Inc\.|Corp\.|LLC|Ltd\.|Co\.|Company|Corporation|Foundation|Institute|Association|University|Bank)\b"
    ),
}

# Words that look like proper names but aren't entities
NAME_STOPWORDS = {
    "The", "This", "That", "These", "Those", "What", "When", "Where",
    "Which", "While", "With", "From", "About", "Been", "Being", "Have",
    "Having", "Could", "Would", "Should", "Might", "Shall", "Will",
    "Just", "Also", "Only", "Then", "Than", "More", "Most", "Such",
    "Each", "Every", "Both", "Few", "Many", "Much", "Several", "Some",
    "After", "Before", "Between", "During", "Into", "Through", "Under",
}


def _regex_extract(text: str) -> List[Dict[str, Any]]:
    """Extract entities using enhanced regex patterns."""
    if not text:
        return []

    entities: Dict[str, Dict[str, Any]] = {}

    for etype, pattern in REGEX_PATTERNS.items():
        for match in pattern.finditer(text):
            raw = match.group(0).strip()
            if not raw or len(raw) < 2:
                continue

            # Skip stop-word "names"
            if etype == "PROPER_NAME" and raw.split()[0] in NAME_STOPWORDS:
                continue

            # Skip short usernames that are likely English words
            if etype == "USERNAME" and raw.lower() in {
                "the", "and", "for", "are", "but", "not", "you", "all",
                "can", "had", "her", "was", "one", "our", "out", "day",
                "get", "has", "him", "his", "how", "its", "may", "new",
                "now", "old", "see", "way", "who", "did", "got", "let",
                "say", "she", "too", "use",
            }:
                continue

            canonical = etype if etype != "PROPER_NAME" else "PERSON"
            dedup_key = f"{canonical}:{raw.lower()}"
            if dedup_key not in entities:
                entities[dedup_key] = {
                    "name": raw,
                    "type": canonical,
                    "confidence": 0.7,
                    "source": "regex",
                }

    return list(entities.values())


def _gliner_extract(text: str, threshold: float = 0.5) -> List[Dict[str, Any]]:
    """Extract entities using GLiNER ML model."""
    model = _load_gliner()
    if model is None:
        return []

    try:
        raw_entities = model.predict_entities(text, GLINER_LABELS, threshold=threshold)
    except Exception as e:
        logger.warning("GLiNER prediction failed: %s", e)
        return []

    entities: List[Dict[str, Any]] = []
    seen = set()

    for ent in raw_entities:
        label = ent.get("label", "").lower()
        canonical = LABEL_MAP.get(label)
        if not canonical:
            continue

        name = text[ent["start"] : ent["end"]].strip()
        if not name or len(name) < 2:
            continue

        confidence = round(ent.get("score", 0.0), 3)
        dedup_key = f"{canonical}:{name.lower()}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        entities.append({
            "name": name,
            "type": canonical,
            "confidence": confidence,
            "source": "gliner",
            "start": ent.get("start"),
            "end": ent.get("end"),
        })

    return entities


def extract_entities(
    text: str,
    use_ml: bool = True,
    min_confidence: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Extract entities from text.

    Strategy:
    1. Try GLiNER ML extraction if use_ml=True and model is available
    2. Fall back to enhanced regex extraction
    3. Merge results, deduplicating by type+name

    Args:
        text: Input text to extract entities from
        use_ml: Whether to attempt ML-based extraction
        min_confidence: Minimum confidence threshold for ML entities

    Returns:
        List of entity dicts with keys: name, type, confidence, source
    """
    if not text or len(text.strip()) < 5:
        return []

    entities: List[Dict[str, Any]] = []
    seen: set = set()

    # Phase 1: ML extraction (if available)
    if use_ml:
        ml_entities = _gliner_extract(text, threshold=min_confidence)
        for ent in ml_entities:
            key = f"{ent['type']}:{ent['name'].lower()}"
            if key not in seen:
                seen.add(key)
                entities.append(ent)

    # Phase 2: Regex extraction (always runs as fallback/supplement)
    regex_entities = _regex_extract(text)
    for ent in regex_entities:
        key = f"{ent['type']}:{ent['name'].lower()}"
        if key not in seen:
            seen.add(key)
            entities.append(ent)

    return entities
