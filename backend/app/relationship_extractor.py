"""
Relationship extraction module for CrimeKit.

Extracts semantic relationships between entities from text.
Each relationship MUST contain evidence provenance.

Relationship types:
USES, OWNS, CONTACTED, CALLED, EMAILED, MESSAGED, LOCATED_AT,
VISITED, ASSOCIATED_WITH, APPEARS_IN, MENTIONED_IN, SENT_TO,
RECEIVED_FROM, CONNECTED_TO, LOGGED_IN_FROM, TRAVELED_TO, BELONGS_TO
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Relationship patterns ──

# Patterns that indicate relationships between entities
RELATIONSHIP_PATTERNS: List[Dict[str, Any]] = [
    # Person -> Device/Account
    {
        "pattern": re.compile(
            r"(?:used|uses|using|logged into|accessed|connected)\s+(?:the\s+)?(\S+)",
            re.IGNORECASE,
        ),
        "type": "USES",
        "source_types": ["PERSON"],
        "target_types": ["DEVICE", "ACCOUNT", "IP_ADDRESS"],
    },
    # Person -> Location
    {
        "pattern": re.compile(
            r"(?:visited|went to|located at|at|in)\s+(?:the\s+)?(\S+(?:\s+\S+)?)",
            re.IGNORECASE,
        ),
        "type": "LOCATED_AT",
        "source_types": ["PERSON"],
        "target_types": ["LOCATION"],
    },
    # Person -> Person (contact)
    {
        "pattern": re.compile(
            r"(?:contacted|called|emailed|messaged|texted|spoke with|talked to)\s+(\S+(?:\s+\S+)?)",
            re.IGNORECASE,
        ),
        "type": "CONTACTED",
        "source_types": ["PERSON"],
        "target_types": ["PERSON", "PHONE", "EMAIL"],
    },
    # Person -> Organization
    {
        "pattern": re.compile(
            r"(?:works? for|employed by|member of|associated with|joined)\s+(?:the\s+)?(\S+(?:\s+\S+)?)",
            re.IGNORECASE,
        ),
        "type": "ASSOCIATED_WITH",
        "source_types": ["PERSON"],
        "target_types": ["ORGANIZATION"],
    },
    # Email/Message sending
    {
        "pattern": re.compile(
            r"(?:sent|sending|forwarded?)\s+(?:an?\s+)?(?:email|message|mail)\s+(?:to\s+)?(\S+)",
            re.IGNORECASE,
        ),
        "type": "SENT_TO",
        "source_types": ["PERSON", "EMAIL"],
        "target_types": ["PERSON", "EMAIL"],
    },
    # Email/Message receiving
    {
        "pattern": re.compile(
            r"(?:received|getting)\s+(?:an?\s+)?(?:email|message|mail)\s+(?:from\s+)?(\S+)",
            re.IGNORECASE,
        ),
        "type": "RECEIVED_FROM",
        "source_types": ["PERSON", "EMAIL"],
        "target_types": ["PERSON", "EMAIL"],
    },
    # Ownership
    {
        "pattern": re.compile(
            r"(?:owns?|owned|has possession of)\s+(?:the\s+)?(\S+(?:\s+\S+)?)",
            re.IGNORECASE,
        ),
        "type": "OWNS",
        "source_types": ["PERSON"],
        "target_types": ["DEVICE", "VEHICLE", "ACCOUNT"],
    },
    # Travel
    {
        "pattern": re.compile(
            r"(?:traveled?|flew|drove|drove to|went to)\s+(?:to\s+)?(\S+(?:\s+\S+)?)",
            re.IGNORECASE,
        ),
        "type": "TRAVELED_TO",
        "source_types": ["PERSON"],
        "target_types": ["LOCATION"],
    },
]


def _find_entity_in_text(
    entity_name: str,
    text: str,
    context_window: int = 50,
) -> Optional[Dict[str, Any]]:
    """Find an entity mention in text with surrounding context."""
    idx = text.lower().find(entity_name.lower())
    if idx == -1:
        return None

    start = max(0, idx - context_window)
    end = min(len(text), idx + len(entity_name) + context_window)

    return {
        "text_span": entity_name,
        "start": idx,
        "end": idx + len(entity_name),
        "context": text[start:end].strip(),
        "page": None,  # Will be filled by caller if page info available
    }


def extract_relationships(
    text: str,
    entities: List[Dict[str, Any]],
    evidence_id: Optional[str] = None,
    artifact_id: Optional[str] = None,
    page: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Extract relationships between entities from text.

    Every relationship includes:
    - source_entity: source entity name
    - relationship: relationship type
    - target_entity: target entity name
    - confidence: extraction confidence
    - evidence_id: source evidence
    - artifact_id: source artifact
    - source_reference: text span with context

    Args:
        text: Input text
        entities: List of extracted entities
        evidence_id: Source evidence ID for provenance
        artifact_id: Source artifact ID for provenance
        page: Page number if applicable

    Returns:
        List of relationship dicts with full provenance
    """
    if not text or not entities:
        return []

    # Build entity lookup by name (case-insensitive)
    entity_map: Dict[str, Dict[str, Any]] = {}
    for ent in entities:
        name = ent.get("name", "")
        if name:
            entity_map[name.lower()] = ent

    relationships: List[Dict[str, Any]] = []
    seen: set = set()

    # ── Pattern-based extraction ──
    for rel_def in RELATIONSHIP_PATTERNS:
        pattern = rel_def["pattern"]
        for match in pattern.finditer(text):
            target_text = match.group(1).strip()

            # Find source entity in the match context
            match_start = match.start()
            match_end = match.end()
            context = text[max(0, match_start - 100) : match_end + 100]

            # Find which source entity this match relates to
            source_entity = None
            for ent in entities:
                ent_name = ent.get("name", "")
                if ent_name and ent_name.lower() in context.lower():
                    source_entity = ent
                    break

            if not source_entity:
                continue

            # Find target entity
            target_entity = None
            for ent in entities:
                ent_name = ent.get("name", "")
                if (
                    ent_name
                    and ent_name.lower() != source_entity.get("name", "").lower()
                    and ent_name.lower() in target_text.lower()
                ):
                    target_entity = ent
                    break

            if not target_entity:
                continue

            # Check type compatibility
            source_type = source_entity.get("type", "")
            target_type = target_entity.get("type", "")

            if (
                source_type not in rel_def["source_types"]
                and rel_def["source_types"]
            ):
                continue
            if (
                target_type not in rel_def["target_types"]
                and rel_def["target_types"]
            ):
                continue

            # Deduplicate
            pair_key = tuple(
                sorted(
                    [source_entity.get("name", ""), target_entity.get("name", "")]
                )
            )
            rel_key = (pair_key, rel_def["type"])
            if rel_key in seen:
                continue
            seen.add(rel_key)

            # Build source reference
            source_ref = _find_entity_in_text(
                source_entity.get("name", ""), text
            )

            relationships.append({
                "source_entity": source_entity.get("name", ""),
                "relationship": rel_def["type"],
                "target_entity": target_entity.get("name", ""),
                "confidence": round(
                    min(
                        source_entity.get("confidence", 0.7),
                        target_entity.get("confidence", 0.7),
                    ),
                    3,
                ),
                "evidence_id": evidence_id,
                "artifact_id": artifact_id,
                "source_reference": {
                    "page": page,
                    "text_span": source_ref.get("text_span") if source_ref else None,
                    "context": source_ref.get("context") if source_ref else None,
                },
                "processor": "relationship_extractor",
            })

    # ── Co-occurrence fallback (for entity pairs without pattern matches) ──
    # Only add co-occurrence if no pattern-based relationships were found for that pair
    sentences = re.split(r"[\.\n?!]+", text)
    for sentence in sentences:
        present = [
            e
            for e in entities
            if e.get("name", "") and e["name"] in sentence
        ]
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                a_name = present[i].get("name", "")
                b_name = present[j].get("name", "")
                pair_key = tuple(sorted([a_name, b_name]))
                rel_key = (pair_key, "CO_OCCURS")

                if rel_key in seen:
                    continue

                # Only add if no other relationship exists between these entities
                has_explicit = any(
                    r.get("source_entity") in (a_name, b_name)
                    and r.get("target_entity") in (a_name, b_name)
                    for r in relationships
                )
                if has_explicit:
                    continue

                seen.add(rel_key)

                source_ref = _find_entity_in_text(a_name, sentence)

                relationships.append({
                    "source_entity": a_name,
                    "relationship": "CO_OCCURS",
                    "target_entity": b_name,
                    "confidence": 0.5,
                    "evidence_id": evidence_id,
                    "artifact_id": artifact_id,
                    "source_reference": {
                        "page": page,
                        "text_span": source_ref.get("text_span") if source_ref else None,
                        "context": source_ref.get("context") if source_ref else None,
                    },
                    "processor": "co_occurrence",
                })

    return relationships
