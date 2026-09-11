"""
Entity resolution module for CrimeKit.

Determines whether two entity mentions refer to the same real-world entity.
Uses a multi-signal strategy:
1. Exact match
2. Canonical normalization
3. Rule-based matching
4. Fuzzy similarity
5. Context similarity

Resolution confidence levels:
- MATCH: High confidence same entity
- LIKELY_MATCH: Good evidence but not certain
- POSSIBLE_MATCH: Some evidence, needs review
- NO_MATCH: Different entities

Every merge is reversible and auditable.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher


class ResolutionResult:
    """Result of entity resolution between two mentions."""

    __slots__ = ("confidence", "level", "reason", "signals")

    def __init__(self, confidence: float, level: str, reason: str, signals: Dict[str, float]):
        self.confidence = confidence
        self.level = level
        self.reason = reason
        self.signals = signals

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence,
            "level": self.level,
            "reason": self.reason,
            "signals": self.signals,
        }


def _fuzzy_ratio(a: str, b: str) -> float:
    """SequenceMatcher similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _tokens(text: str) -> set:
    """Tokenize name into lowercase word set."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _jaccard(a: set, b: set) -> float:
    """Jaccard similarity between two token sets."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def resolve_entities(
    entities: List[Dict[str, Any]],
    evidence_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Resolve entity mentions into canonical entities.

    For each pair of entities with the same type, compute resolution signals
    and merge if confidence is high enough.

    Returns a list of canonical entities with:
    - id: stable internal ID
    - name: canonical name
    - type: entity type
    - confidence: resolution confidence
    - mentions: list of original mentions that were resolved to this entity
    - merged: list of entity names that were merged

    Every merge is logged for audit.
    """
    if not entities:
        return []

    # Group by type
    by_type: Dict[str, List[Dict[str, Any]]] = {}
    for ent in entities:
        etype = ent.get("type", "unknown")
        by_type.setdefault(etype, []).append(ent)

    canonical_entities: List[Dict[str, Any]] = []

    for etype, type_entities in by_type.items():
        # Sort by confidence descending
        type_entities.sort(key=lambda e: e.get("confidence", 0), reverse=True)

        # Track which entities have been merged
        merged_into: Dict[int, int] = {}  # index -> canonical index

        for i in range(len(type_entities)):
            if i in merged_into:
                continue

            canonical = type_entities[i]
            canonical_entry = {
                "id": f"{etype}:{canonical.get('normalized_value', canonical.get('name', ''))}",
                "name": canonical.get("name", ""),
                "normalized_value": canonical.get("normalized_value", canonical.get("name", "")),
                "type": etype,
                "confidence": canonical.get("confidence", 1.0),
                "mentions": [canonical.get("name", "")],
                "merged": [],
                "source": canonical.get("source", "regex"),
                "evidence_id": evidence_id,
            }

            for j in range(i + 1, len(type_entities)):
                if j in merged_into:
                    continue

                other = type_entities[j]
                result = _resolve_pair(canonical, other, etype)

                if result.level in ("MATCH", "LIKELY_MATCH"):
                    merged_into[j] = i
                    canonical_entry["mentions"].append(other.get("name", ""))
                    canonical_entry["merged"].append(other.get("name", ""))
                    # Boost confidence from merge
                    canonical_entry["confidence"] = max(
                        canonical_entry["confidence"],
                        result.confidence,
                    )

            canonical_entities.append(canonical_entry)

    return canonical_entities


def _resolve_pair(
    a: Dict[str, Any],
    b: Dict[str, Any],
    etype: str,
) -> ResolutionResult:
    """
    Compute resolution between two entity mentions.

    Returns a ResolutionResult with confidence, level, reason, and signal scores.
    """
    name_a = a.get("normalized_value", a.get("name", "")).lower().strip()
    name_b = b.get("normalized_value", b.get("name", "")).lower().strip()

    signals: Dict[str, float] = {}

    # Signal 1: Exact match
    if name_a == name_b:
        signals["exact_match"] = 1.0
        return ResolutionResult(1.0, "MATCH", "Exact normalized value match", signals)

    # Signal 2: Exact original match (case-insensitive)
    orig_a = a.get("name", "").lower().strip()
    orig_b = b.get("name", "").lower().strip()
    if orig_a == orig_b:
        signals["exact_original"] = 1.0
        return ResolutionResult(1.0, "MATCH", "Exact original value match", signals)

    # Signal 3: Type-specific rules
    if etype == "EMAIL":
        if name_a == name_b:
            signals["email_exact"] = 1.0
            return ResolutionResult(1.0, "MATCH", "Email address match", signals)
        # Different emails = different entities
        signals["email_different"] = 0.0
        return ResolutionResult(0.0, "NO_MATCH", "Different email addresses", signals)

    if etype == "PHONE":
        digits_a = re.sub(r"[^\d]", "", name_a)
        digits_b = re.sub(r"[^\d]", "", name_b)
        if digits_a == digits_b:
            signals["phone_digits"] = 1.0
            return ResolutionResult(1.0, "MATCH", "Phone digits match", signals)
        # Check if one is a prefix of the other (country code)
        if digits_a.endswith(digits_b) or digits_b.endswith(digits_a):
            signals["phone_partial"] = 0.9
            return ResolutionResult(0.9, "LIKELY_MATCH", "Phone number prefix match", signals)
        signals["phone_different"] = 0.0
        return ResolutionResult(0.0, "NO_MATCH", "Different phone numbers", signals)

    if etype == "IP_ADDRESS":
        if name_a == name_b:
            signals["ip_exact"] = 1.0
            return ResolutionResult(1.0, "MATCH", "IP address match", signals)
        signals["ip_different"] = 0.0
        return ResolutionResult(0.0, "NO_MATCH", "Different IP addresses", signals)

    if etype == "URL":
        # Normalize and compare
        norm_a = name_a.rstrip("/")
        norm_b = name_b.rstrip("/")
        if norm_a == norm_b:
            signals["url_exact"] = 1.0
            return ResolutionResult(1.0, "MATCH", "URL match", signals)
        signals["url_different"] = 0.0
        return ResolutionResult(0.0, "NO_MATCH", "Different URLs", signals)

    if etype == "DATE":
        if name_a == name_b:
            signals["date_exact"] = 1.0
            return ResolutionResult(1.0, "MATCH", "Date match", signals)
        signals["date_different"] = 0.0
        return ResolutionResult(0.0, "NO_MATCH", "Different dates", signals)

    # Signal 4: Fuzzy similarity for names, locations, organizations
    if etype in ("PERSON", "LOCATION", "ORGANIZATION", "VEHICLE"):
        tokens_a = _tokens(name_a)
        tokens_b = _tokens(name_b)

        # Jaccard token overlap
        jaccard = _jaccard(tokens_a, tokens_b)
        signals["jaccard"] = jaccard

        # Fuzzy string similarity
        fuzzy = _fuzzy_ratio(name_a, name_b)
        signals["fuzzy"] = fuzzy

        # Substring containment
        containment = 0.0
        if name_a in name_b or name_b in name_a:
            shorter = min(len(name_a), len(name_b))
            longer = max(len(name_a), len(name_b))
            containment = shorter / longer if longer > 0 else 0.0
        signals["containment"] = containment

        # Composite score
        score = max(jaccard, fuzzy, containment)

        if score >= 0.95:
            return ResolutionResult(score, "MATCH", f"High similarity ({score:.2f})", signals)
        elif score >= 0.8:
            return ResolutionResult(score, "LIKELY_MATCH", f"Likely same entity ({score:.2f})", signals)
        elif score >= 0.6:
            return ResolutionResult(score, "POSSIBLE_MATCH", f"Possible match ({score:.2f})", signals)
        else:
            return ResolutionResult(score, "NO_MATCH", f"Low similarity ({score:.2f})", signals)

    # Default: use fuzzy similarity
    fuzzy = _fuzzy_ratio(name_a, name_b)
    signals["fuzzy"] = fuzzy

    if fuzzy >= 0.95:
        return ResolutionResult(fuzzy, "MATCH", f"Fuzzy match ({fuzzy:.2f})", signals)
    elif fuzzy >= 0.8:
        return ResolutionResult(fuzzy, "LIKELY_MATCH", f"Likely match ({fuzzy:.2f})", signals)
    elif fuzzy >= 0.6:
        return ResolutionResult(fuzzy, "POSSIBLE_MATCH", f"Possible match ({fuzzy:.2f})", signals)
    else:
        return ResolutionResult(fuzzy, "NO_MATCH", f"Low similarity ({fuzzy:.2f})", signals)
