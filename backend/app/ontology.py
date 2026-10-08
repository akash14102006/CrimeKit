"""
CrimeKit Graph Ontology Definition.

Defines standard entity types, relationship types, fact classifications,
and evidence provenance metadata for the CrimeKit Knowledge Graph.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# --- Entity Types ---
class EntityType(str, Enum):
    CASE = "case"
    PERSON = "person"
    LOCATION = "location"
    ORGANIZATION = "organization"
    DIGITAL_IDENTITY = "digital_identity"  # email, phone, ip, username, account
    DEVICE = "device"                      # computer, mobile, server, USB
    FILE = "file"                          # document, image, audio, video, archive
    ARTIFACT = "artifact"                  # browser history, registry, log entry
    EVENT = "event"                        # incident, meeting, transaction, login
    CONCEPT = "concept"                    # keyword, topic, malware family


# --- Relationship Types ---
class RelationshipType(str, Enum):
    MENTIONED_IN = "MENTIONED_IN"
    COMMUNICATED_WITH = "COMMUNICATED_WITH"
    TRANSFERRED_TO = "TRANSFERRED_TO"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    LOCATED_AT = "LOCATED_AT"
    OWNED_BY = "OWNED_BY"
    CREATED_BY = "CREATED_BY"
    AFFILIATED_WITH = "AFFILIATED_WITH"
    OCCURRED_AT = "OCCURRED_AT"
    EXECUTES = "EXECUTES"
    CONNECTED_TO = "CONNECTED_TO"
    PART_OF = "PART_OF"


# --- Fact Classification ---
class FactClassification(str, Enum):
    OBSERVED = "OBSERVED"        # Directly extracted from hard evidence (e.g. EXIF, header, log)
    DERIVED = "DERIVED"          # Computed via automated forensic rules/processors
    CANDIDATE = "CANDIDATE"      # Entity resolution candidate match
    HYPOTHESIS = "HYPOTHESIS"    # AI model inference / correlation hypothesis
    REVIEWED = "REVIEWED"        # Manually confirmed by investigator


# --- Color Map for 3D Visual Rendering ---
ENTITY_COLOR_MAP: Dict[str, str] = {
    EntityType.CASE.value: "#f59e0b",              # Amber / Gold
    EntityType.PERSON.value: "#3b82f6",            # Cyan Blue
    EntityType.LOCATION.value: "#22c55e",          # Emerald Green
    EntityType.ORGANIZATION.value: "#f97316",      # Vibrant Orange
    EntityType.DIGITAL_IDENTITY.value: "#06b6d4",  # Cyan
    EntityType.DEVICE.value: "#a855f7",            # Purple
    EntityType.FILE.value: "#10b981",              # Teal
    EntityType.ARTIFACT.value: "#8b5cf6",          # Violet
    EntityType.EVENT.value: "#ec4899",             # Pink
    EntityType.CONCEPT.value: "#64748b",           # Slate Gray
}


# --- Node Schema ---
class GraphNodeSchema(BaseModel):
    id: str
    label: str
    type: str = Field(default=EntityType.CONCEPT.value)
    case_id: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    fact_classification: str = Field(default=FactClassification.OBSERVED.value)
    properties: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    # 3D spatial properties (computed or updated)
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


# --- Edge Schema ---
class GraphEdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    type: str = Field(default=RelationshipType.CONNECTED_TO.value)
    label: Optional[str] = None
    case_id: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    fact_classification: str = Field(default=FactClassification.OBSERVED.value)
    evidence_id: Optional[str] = None
    artifact_id: Optional[str] = None
    source_text: Optional[str] = None
    source_page: Optional[int] = None
    processor: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


def get_entity_color(entity_type: str) -> str:
    """Return HEX color for given entity type."""
    t = str(entity_type).lower()
    return ENTITY_COLOR_MAP.get(t, "#94a3b8")
