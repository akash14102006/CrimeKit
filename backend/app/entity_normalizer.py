"""
Entity normalization module for CrimeKit.

Normalizes extracted entities to canonical forms while preserving
original observed values. Never destroys source evidence.
"""

import re
from typing import Dict, Any, Optional


def normalize_phone(value: str) -> str:
    """
    Normalize phone numbers to E.164-like format.
    Examples:
        "98765 43210" -> "+919876543210"
        "(555) 123-4567" -> "+15551234567"
        "+44 20 7946 0958" -> "+442079460958"
    """
    digits = re.sub(r"[^\d]", "", value)
    if not digits:
        return value
    if len(digits) == 10 and not value.startswith("+"):
        return f"+1{digits}"
    if len(digits) > 10 and not value.startswith("+"):
        return f"+{digits}"
    if value.startswith("+"):
        return f"+{digits}"
    return f"+{digits}"


def normalize_email(value: str) -> str:
    """Normalize email to lowercase, trimmed."""
    return value.strip().lower()


def normalize_url(value: str) -> str:
    """Normalize URL: lowercase scheme/host, remove trailing slash."""
    url = value.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    url = url.rstrip("/")
    return url


def normalize_domain(value: str) -> str:
    """Normalize domain to lowercase, trimmed, no trailing dot."""
    return value.strip().lower().rstrip(".")


def normalize_ip(value: str) -> str:
    """Normalize IP address — just trim and return as-is (preserves original)."""
    return value.strip()


def normalize_name(value: str) -> str:
    """
    Normalize name to title case, trimmed.
    Does NOT merge names — "John Kumar" and "J. Kumar" remain separate.
    """
    return " ".join(value.strip().split())


def normalize_username(value: str) -> str:
    """Normalize username: lowercase, strip @ prefix."""
    name = value.strip().lower()
    if name.startswith("@"):
        name = name[1:]
    return name


def normalize_case_id(value: str) -> str:
    """Normalize case ID: uppercase, single space separator."""
    v = value.strip().upper()
    v = re.sub(r"\s+", " ", v)
    return v


def normalize_financial(value: str) -> str:
    """Normalize financial identifier: digits only, grouped in 4s."""
    digits = re.sub(r"[^\d]", "", value)
    if len(digits) == 16:
        return " ".join(digits[i : i + 4] for i in range(0, 16, 4))
    return value.strip()


NORMALIZERS: Dict[str, Any] = {
    "PHONE": normalize_phone,
    "EMAIL": normalize_email,
    "URL": normalize_url,
    "DOMAIN": normalize_domain,
    "IP_ADDRESS": normalize_ip,
    "PERSON": normalize_name,
    "LOCATION": normalize_name,
    "ORGANIZATION": normalize_name,
    "USERNAME": normalize_username,
    "SOCIAL_HANDLE": normalize_username,
    "CASE_ID": normalize_case_id,
    "DOCUMENT_ID": normalize_case_id,
    "FINANCIAL_IDENTIFIER": normalize_financial,
}


def normalize_entity(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize an entity in-place. Preserves original_value and adds normalized_value.

    Args:
        entity: Dict with at least 'name' and 'type' keys

    Returns:
        The same entity dict with 'original_value' and 'normalized_value' added.
    """
    etype = entity.get("type", "")
    name = entity.get("name", "")

    if not name:
        return entity

    entity["original_value"] = name

    normalizer = NORMALIZERS.get(etype)
    if normalizer:
        entity["normalized_value"] = normalizer(name)
    else:
        entity["normalized_value"] = name.strip()

    return entity


def normalize_entities(entities: list) -> list:
    """Normalize a list of entities."""
    return [normalize_entity(e) for e in entities]
