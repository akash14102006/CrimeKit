# CRIMEKIT — 3D FORENSIC KNOWLEDGE GRAPH
# MASTER PROMPT — GRAPH ONTOLOGY + VISUAL ONTOLOGY
## Prompt #3 — Production-Grade Neo4j Graph Model + 3D Semantic Design
### Reference UI: AI Agent Observatory
### Reference implementation: https://ai-agent-observatory.onrender.com/
### Reference repository: https://github.com/sakshigupta372/AI-Agent-observatory
### Product: CrimeKit
### Role: Principal Neo4j Architect + Digital Forensics Architect + 3D Visualization Architect + Enterprise UX Architect + Security Architect + Graph Data Modeler

---

# 0. MISSION

You are now designing the **GRAPH ONTOLOGY** for CrimeKit's production-grade 3D Knowledge Graph.

This is NOT a generic Neo4j tutorial.

This is NOT a normal node-edge diagram.

This is NOT a redesign of the CrimeKit backend from scratch.

This is the next architectural stage after the Repository Audit.

The objective is to define a graph ontology that is:

- forensic
- evidence-grounded
- provenance-preserving
- case-isolated
- explainable
- temporally aware
- realtime-capable
- scalable
- secure
- compatible with Neo4j Aura
- compatible with CrimeKit PostgreSQL as authoritative source
- compatible with a 3D WebGL/Three.js-style visualization
- compatible with future Graph Data Science
- compatible with AI/GraphRAG
- usable by investigators
- suitable for enterprise production

The visual experience must be strongly inspired by the supplied **AI Agent Observatory** reference:

- large immersive 3D graph canvas
- dark near-black environment
- sparse spatial composition
- large semantic nodes
- orbital / wireframe-like node treatments where appropriate
- thin curved relationship paths
- large labels
- floating analytical modules
- right-side execution/trace-style panel adapted into a forensic inspector
- bottom command/search bar
- compact controls
- cinematic but restrained motion
- deep-space spatial feeling
- progressive graph emergence
- zoom/pan/orbit interaction
- graph-centered workspace

However:

> **Do NOT blindly copy another application's source code, branding, proprietary assets, or exact copyrighted artwork.**

Recreate the **interaction language and visual principles** using CrimeKit's own forensic semantics, components, typography, icons, data and branding.

The target is **visual parity in interaction quality and design language**, while remaining an original CrimeKit product.

---

# 1. CRITICAL PRODUCT PRINCIPLE

The 3D graph must never become a decorative visualization.

Every visual element must represent something meaningful.

The system should answer:

```text
WHO?
WHAT?
WHEN?
WHERE?
HOW?
CONNECTED TO WHOM?
SUPPORTED BY WHICH EVIDENCE?
DERIVED FROM WHICH ARTIFACT?
HOW CONFIDENT IS THE RELATIONSHIP?
WHAT CHANGED?
WHY IS THIS NODE IMPORTANT?
WHAT CAN THE INVESTIGATOR VERIFY?
```

The graph is an investigative instrument.

---

# 2. AUTHORITATIVE DATA PRINCIPLE

CrimeKit must maintain a strict separation:

```text
PostgreSQL
    =
authoritative forensic/domain record
```

```text
Neo4j
    =
relationship intelligence projection
```

```text
Object Storage
    =
original evidence / binary artifacts
```

```text
pgvector
    =
vector similarity retrieval where applicable
```

```text
3D UI
    =
investigator visualization and interaction
```

```text
AI
    =
reasoning / explanation / retrieval assistance
```

The 3D graph must never become the sole source of forensic truth.

---

# 3. GRAPH ONTOLOGY OBJECTIVES

The ontology must support:

1. Case investigation.
2. Evidence relationships.
3. Entity relationships.
4. Timeline reconstruction.
5. Device relationships.
6. Communication relationships.
7. Location relationships.
8. Digital artifact relationships.
9. Media relationships.
10. Account relationships.
11. Identity resolution.
12. Face-trace observations where implemented.
13. Network/IP relationships.
14. File relationships.
15. Cross-artifact correlation.
16. Contradiction representation.
17. Confidence.
18. Provenance.
19. Temporal state.
20. Investigator review.
21. Graph analytics.
22. Realtime updates.
23. AI retrieval.
24. 3D semantic visualization.

---

# 4. REFERENCE EXPERIENCE

The supplied AI Agent Observatory reference should influence the visual composition.

Reference characteristics to preserve conceptually:

```text
FULL-SCREEN 3D SPACE
        ↓
SPATIAL NODES
        ↓
CURVED CONNECTIONS
        ↓
LARGE SEMANTIC LABELS
        ↓
FLOATING INFORMATION PANELS
        ↓
BOTTOM COMMAND / QUERY BAR
        ↓
RIGHT-SIDE TRACE / INSPECTOR PANEL
        ↓
MINIMAL CONTROLS
```

CrimeKit adaptation:

```text
FULL-SCREEN FORENSIC GRAPH
        ↓
PERSON / DEVICE / EVIDENCE / LOCATION / ACCOUNT / EVENT
        ↓
PROVENANCE-AWARE RELATIONSHIPS
        ↓
SEMANTIC LABELS
        ↓
FORENSIC INSPECTOR
        ↓
INVESTIGATOR QUERY BAR
        ↓
GRAPH EXPLANATION TRACE
        ↓
TIMELINE / EVIDENCE CONTEXT
```

---

# 5. DO NOT COPY AI AGENT SEMANTICS

The reference may contain concepts such as:

```text
USER
INTENT
PLANNER
MEMORY
LLM
VERIFIER
TOOL HUB
RESPONSE
```

These must NOT simply be transferred into CrimeKit.

CrimeKit should use its own domain:

```text
CASE
PERSON
DEVICE
ACCOUNT
LOCATION
EVIDENCE
ARTIFACT
COMMUNICATION
MEDIA
IP ADDRESS
TIMELINE EVENT
OBSERVATION
PROCESSING RUN
ENTITY
RELATIONSHIP
```

---

# 6. CORE CRIMEKIT GRAPH

At minimum define these conceptual domains:

```text
CASE
INVESTIGATION
PERSON
DEVICE
ACCOUNT
EMAIL
PHONE
IP_ADDRESS
LOCATION
VEHICLE
EVIDENCE
ARTIFACT
FILE
MEDIA
IMAGE
VIDEO
AUDIO
DOCUMENT
MESSAGE
COMMUNICATION
TIMELINE_EVENT
OBSERVATION
FACE_OBSERVATION
PROCESSING_RUN
SEARCH_JOB
MODEL_RUN
GRAPH_ASSERTION
REVIEW
```

Do NOT implement every node automatically.

Use the repository audit to determine which types already exist.

---

# 7. NODE CLASSIFICATION SYSTEM

Every node must have:

```text
stable_id
case_id
type
display_name
created_at
updated_at
source
status
```

Where applicable:

```text
confidence
observed_at
first_seen_at
last_seen_at
provenance_id
evidence_count
relationship_count
```

---

# 8. NODE SEMANTIC GROUPS

Group graph entities into semantic families.

## Identity

```text
PERSON
ORGANIZATION
ACCOUNT
EMAIL
PHONE
```

## Digital

```text
DEVICE
IP_ADDRESS
DOMAIN
URL
FILE
APPLICATION
```

## Physical

```text
LOCATION
VEHICLE
CAMERA
```

## Evidence

```text
EVIDENCE
ARTIFACT
DOCUMENT
IMAGE
VIDEO
AUDIO
MESSAGE
```

## Temporal

```text
TIMELINE_EVENT
OBSERVATION
```

## Processing

```text
PROCESSING_RUN
MODEL_RUN
SEARCH_JOB
```

## Investigation

```text
CASE
INVESTIGATION
REVIEW
GRAPH_ASSERTION
```

---

# 9. STABLE IDENTIFIERS

Do not use:

```text
display_name
email
filename
device name
IP address
```

as the only graph identity.

Every node must have a stable application/domain ID.

Preferred:

```text
person_id
device_id
evidence_id
artifact_id
event_id
case_id
```

Neo4j should maintain uniqueness constraints where appropriate.

---

# 10. CASE ISOLATION

Every graph query must be case-scoped.

Preferred conceptual invariant:

```text
MATCH (n)
WHERE n.case_id = $case_id
```

But do not blindly duplicate the same condition everywhere if the repository's graph access layer can enforce case scope centrally.

The security architecture must prevent:

```text
Case A
   ↓
Case B
```

from appearing in unauthorized graph queries.

Cross-case correlation must be:

- explicitly authorized
- explicitly requested
- auditable
- explainable
- restricted by policy

---

# 11. CASE NODE

Concept:

```text
(:Case)
```

Properties may include:

```text
id
case_id
case_number
title
status
classification
created_at
updated_at
```

The graph should normally begin from:

```text
Case
```

and expand into authorized investigation data.

---

# 12. INVESTIGATION NODE

Concept:

```text
(:Investigation)
```

Relationships:

```text
(Case)-[:HAS_INVESTIGATION]->(Investigation)
```

Purpose:

- investigation workspace
- analytical scope
- search session
- graph context
- investigator activity

---

# 13. PERSON NODE

Concept:

```text
(:Person)
```

Possible properties:

```text
person_id
display_name
aliases
date_of_birth
case_role
status
created_at
updated_at
```

Do not store unnecessary sensitive data in Neo4j if PostgreSQL is authoritative.

Use references where possible.

---

# 14. DEVICE NODE

Concept:

```text
(:Device)
```

Possible properties:

```text
device_id
device_type
manufacturer
model
serial_hash
identifier_hash
first_seen_at
last_seen_at
```

Relationships:

```text
(Person)-[:USES]->(Device)
(Person)-[:OWNS]->(Device)
(Device)-[:CONNECTED_TO]->(IP)
(Device)-[:OBSERVED_AT]->(Location)
(Device)-[:PRODUCED]->(Artifact)
```

Do not assume ownership when evidence only demonstrates usage.

Relationship semantics must remain precise.

---

# 15. ACCOUNT NODE

Concept:

```text
(:Account)
```

Possible relationships:

```text
(Person)-[:CONTROLS]->(Account)
(Device)-[:ACCESSED]->(Account)
(Account)-[:USED_FROM]->(IP_ADDRESS)
(Account)-[:USED_AT]->(Location)
```

Distinguish:

```text
controls
owns
uses
accessed
associated_with
```

Never collapse all of them into:

```text
RELATED_TO
```

---

# 16. EMAIL NODE

Concept:

```text
(:Email)
```

Relationships:

```text
(Person)-[:HAS_EMAIL]->(Email)
(Account)-[:USES_EMAIL]->(Email)
(Email)-[:SENT_MESSAGE]->(Message)
```

Avoid unnecessary duplication of email addresses if privacy/security rules prohibit it.

---

# 17. PHONE NODE

Concept:

```text
(:Phone)
```

Possible relationships:

```text
(Person)-[:USES]->(Phone)
(Phone)-[:COMMUNICATED_WITH]->(Phone)
(Phone)-[:LOCATED_AT]->(Location)
```

Communication relationships must carry temporal context where possible.

---

# 18. IP ADDRESS NODE

Concept:

```text
(:IPAddress)
```

Possible relationships:

```text
(Device)-[:USED_IP]->(IPAddress)
(Account)-[:ACCESSED_FROM]->(IPAddress)
(IPAddress)-[:RESOLVES_TO]->(Location)
```

Do not treat IP location as exact physical identity.

The UI should distinguish:

```text
network attribution
```

from:

```text
physical location certainty
```

---

# 19. LOCATION NODE

Concept:

```text
(:Location)
```

Possible properties:

```text
location_id
name
latitude
longitude
accuracy
location_type
```

Potential relationship:

```text
(Person)-[:OBSERVED_AT]->(Location)
(Device)-[:OBSERVED_AT]->(Location)
(Evidence)-[:CAPTURED_AT]->(Location)
(Event)-[:OCCURRED_AT]->(Location)
```

---

# 20. EVIDENCE NODE

Concept:

```text
(:Evidence)
```

Properties:

```text
evidence_id
case_id
evidence_type
hash
status
collection_time
acquisition_method
custodian
created_at
```

Relationships:

```text
(Case)-[:CONTAINS_EVIDENCE]->(Evidence)
(Evidence)-[:GENERATED]->(Artifact)
(Evidence)-[:SUPPORTS]->(GraphAssertion)
```

The graph should store metadata/references, not replace evidence storage.

---

# 21. ARTIFACT NODE

Concept:

```text
(:Artifact)
```

Examples:

```text
filesystem artifact
browser artifact
message artifact
metadata artifact
EXIF artifact
registry artifact
application artifact
database artifact
```

Relationship:

```text
(Evidence)-[:CONTAINS_ARTIFACT]->(Artifact)
```

---

# 22. FILE NODE

Concept:

```text
(:File)
```

Possible:

```text
filename
mime_type
sha256
size
created_at
modified_at
path
```

Relationship:

```text
(Artifact)-[:REFERENCES]->(File)
(File)-[:MENTIONS]->(Person)
(File)-[:CONTAINS]->(Message)
```

---

# 23. MEDIA NODES

Where supported:

```text
(:Image)
(:Video)
(:Audio)
(:Document)
```

Do not create redundant labels if the existing model already represents media generically.

The ontology must follow actual repository data.

---

# 24. MESSAGE NODE

Concept:

```text
(:Message)
```

Possible:

```text
message_id
channel
timestamp
direction
content_hash
```

Relationships:

```text
(Person)-[:SENT]->(Message)
(Person)-[:RECEIVED]->(Message)
(Message)-[:MENTIONS]->(Person)
(Message)-[:ATTACHES]->(File)
```

Message content should remain in the authoritative/evidence layer unless graph storage is explicitly justified.

---

# 25. COMMUNICATION NODE

If the repository has communication events, consider:

```text
(:Communication)
```

Relationship:

```text
(Person)-[:PARTICIPATED_IN]->(Communication)
```

This allows communication to become a first-class temporal event.

---

# 26. TIMELINE EVENT

Concept:

```text
(:TimelineEvent)
```

Properties:

```text
event_id
timestamp
timestamp_precision
timezone
event_type
confidence
source
```

Relationships:

```text
(Person)-[:INVOLVED_IN]->(TimelineEvent)
(Device)-[:GENERATED]->(TimelineEvent)
(Evidence)-[:SUPPORTS]->(TimelineEvent)
(TimelineEvent)-[:OCCURRED_AT]->(Location)
```

---

# 27. OBSERVATION

Use when the system records an observation without claiming stronger identity.

Example:

```text
(:Observation)
```

This is especially important for:

- CCTV
- face detection
- device sightings
- location sightings
- access events

---

# 28. FACE OBSERVATION

If implemented:

```text
(:FaceObservation)
```

Relationships:

```text
(Video)-[:CONTAINS]->(FaceObservation)
(FaceObservation)-[:OCCURRED_AT]->(Location)
(FaceObservation)-[:CANDIDATE_FOR]->(Person)
```

Never encode a candidate match as:

```text
FaceObservation-[:IS]->Person
```

unless the underlying system has a justified identity confirmation process.

---

# 29. PROCESSING RUN

Concept:

```text
(:ProcessingRun)
```

Properties:

```text
run_id
pipeline
version
started_at
completed_at
status
runtime
```

Relationships:

```text
(Evidence)-[:PROCESSED_BY]->(ProcessingRun)
(ProcessingRun)-[:GENERATED]->(Artifact)
(ProcessingRun)-[:EXTRACTED]->(GraphAssertion)
```

---

# 30. MODEL RUN

Concept:

```text
(:ModelRun)
```

Possible:

```text
model_name
model_version
policy_version
runtime_version
executed_at
```

Use for AI/ML-derived results.

---

# 31. GRAPH ASSERTION

Introduce a forensic-safe abstraction:

```text
(:GraphAssertion)
```

Purpose:

A graph relationship may be an analytical assertion rather than a raw observed fact.

Properties:

```text
assertion_id
status
confidence
assertion_type
created_at
review_status
```

Possible states:

```text
OBSERVED
EXTRACTED
RESOLVED
INFERRED
CORROBORATED
CONTRADICTED
REJECTED
DEPRECATED
```

---

# 32. RELATIONSHIP TAXONOMY

Do not create one generic:

```text
RELATED_TO
```

relationship for everything.

Use semantically meaningful relationship types.

Examples:

```text
USES
OWNS
CONTROLS
ACCESSED
CONNECTED_TO
COMMUNICATED_WITH
SENT
RECEIVED
MENTIONS
CONTAINS
REFERENCES
APPEARS_IN
CAPTURED_AT
OCCURRED_AT
OBSERVED_AT
GENERATED
PRODUCED
SUPPORTS
CONTRADICTS
ASSOCIATED_WITH
CANDIDATE_FOR
INVOLVED_IN
```

---

# 33. RELATIONSHIP PROPERTIES

Important relationships should support:

```text
relationship_id
case_id
confidence
status
source
evidence_id
artifact_id
processing_run_id
model_run_id
observed_at
valid_from
valid_to
created_at
updated_at
```

Not every property belongs on every relationship.

Do not inflate the graph schema unnecessarily.

---

# 34. OBSERVED VS INFERRED

The ontology must explicitly distinguish:

```text
OBSERVED
```

from:

```text
INFERRED
```

Example:

```text
Evidence
   ↓
Device logged in from IP
   ↓
OBSERVED

Person is probably associated with IP
   ↓
INFERRED
```

The 3D UI must never visually imply equal certainty.

---

# 35. CONFIDENCE MODEL

If confidence exists in the repository, preserve its exact semantics.

Do not invent mathematical meaning.

If confidence is introduced, define:

```text
confidence
confidence_source
confidence_method
confidence_version
```

Potential classes:

```text
HIGH
MEDIUM
LOW
UNKNOWN
```

Only use numeric scores when their calculation is defined.

---

# 36. CONTRADICTION MODEL

Support relationships such as:

```text
(EvidenceA)-[:CONTRADICTS]->(GraphAssertion)
```

or equivalent architecture.

The exact model should be determined by the existing repository.

The graph must not hide conflicting evidence.

---

# 37. PROVENANCE MODEL

Every analytical graph assertion must be traceable.

Target conceptual chain:

```text
Evidence
   ↓
Artifact
   ↓
ProcessingRun
   ↓
Extraction
   ↓
GraphAssertion
   ↓
Entity / Relationship
```

The investigator should be able to click a relationship and see:

```text
WHY DOES THIS EDGE EXIST?
```

Then:

```text
SOURCE EVIDENCE
PROCESSING RUN
EXTRACTION METHOD
MODEL
CONFIDENCE
REVIEW STATUS
TIMESTAMP
```

---

# 38. TEMPORAL MODEL

Relationships may be:

```text
time-independent
```

or:

```text
time-bound
```

Where supported:

```text
valid_from
valid_to
observed_at
first_seen_at
last_seen_at
```

The 3D graph must eventually support a temporal lens.

---

# 39. GRAPH LAYERS

The visualization should be able to separate:

```text
LAYER 1 — CASE
LAYER 2 — ENTITIES
LAYER 3 — EVIDENCE
LAYER 4 — RELATIONSHIPS
LAYER 5 — TIMELINE
LAYER 6 — PROVENANCE
LAYER 7 — ANALYTICS
```

Do not render every layer at once by default.

---

# 40. 3D SEMANTIC SPACE

The 3D graph should use space intentionally.

Potential semantic arrangement:

```text
                 EVIDENCE
                    ↑
                    |
LOCATION ← ENTITY CORE → DIGITAL
                    |
                    ↓
                TIMELINE
```

However:

> Do NOT hard-code a static 3D map if a dynamic graph layout is more appropriate.

Use spatial positioning to reduce cognitive load.

---

# 41. 3D NODE DESIGN

Node appearance should encode:

```text
entity type
status
confidence
selection
activity
importance
```

Potential representation:

### Person

```text
central spherical / faceted object
```

### Device

```text
compact geometric object
```

### Evidence

```text
document/file-like or faceted object
```

### Location

```text
orbital/marker-like object
```

### Timeline event

```text
small temporal marker
```

### Processing run

```text
technical/system object
```

Do not make every node identical.

---

# 42. NODE SCALE

Node size must not automatically mean:

```text
guilt
```

Use scale for defensible metrics such as:

```text
degree
evidence count
graph importance
selected state
visual hierarchy
```

Document the metric.

---

# 43. COLOR SYSTEM

Color should primarily encode:

```text
ENTITY TYPE
```

Secondary visual channels should encode:

```text
confidence
status
selection
```

Never make:

```text
red = criminal
```

Instead:

```text
red/orange = alert / analytical state
```

with explicit legend.

---

# 44. RELATIONSHIP VISUALS

Relationships should use:

```text
curve
direction
thickness
opacity
label
animation
```

Only where semantically justified.

Potential:

```text
OBSERVED
→ solid line

INFERRED
→ dashed line

CONTRADICTED
→ broken / warning treatment

SELECTED PATH
→ highlighted line

LIVE EVENT
→ animated pulse
```

These are design proposals and must be validated against accessibility/performance.

---

# 45. REFERENCE-STYLE SPATIAL COMPOSITION

The reference uses a large immersive field.

CrimeKit should emulate:

```text
large empty spatial areas
+
clusters
+
semantic islands
+
focused node
+
relationship paths
```

Avoid:

```text
every node packed into one dense ball
```

---

# 46. FORENSIC GRAPH CLUSTERS

Potential clusters:

```text
PERSON CLUSTER
DEVICE CLUSTER
COMMUNICATION CLUSTER
EVIDENCE CLUSTER
LOCATION CLUSTER
TIMELINE CLUSTER
```

Clusters should emerge from data.

Do not force arbitrary visual clusters that misrepresent relationships.

---

# 47. GRAPH FOCUS

When the investigator selects an entity:

```text
Selected entity
       ↓
Primary neighbors
       ↓
Secondary neighbors
       ↓
Evidence support
       ↓
Timeline
```

Use progressive expansion.

Do not render the entire database.

---

# 48. GRAPH EXPANSION

Potential UI:

```text
[ + Expand ]
```

Options:

```text
1 hop
2 hops
Evidence
Timeline
Devices
Communications
Locations
```

Every expansion must remain case-authorized.

---

# 49. RIGHT-SIDE FORENSIC INSPECTOR

Adapt the reference's right-side panel into:

```text
FORENSIC INSPECTOR
```

When no entity is selected:

```text
Select an entity to inspect
```

When selected:

```text
PERSON
John Smith

STATUS
Under Review

RELATIONSHIPS
12

EVIDENCE
8

OBSERVATIONS
4

CONFIDENCE
...

PROVENANCE
View sources

TIMELINE
View events
```

The exact fields must come from actual data availability.

---

# 50. FORENSIC TRACE PANEL

Adapt the reference's:

```text
AGENT TRACE
```

into:

```text
INVESTIGATION TRACE
```

Example:

```text
INVESTIGATION TRACE

09:31:12
Evidence selected

09:31:13
Artifact resolved

09:31:13
Entity linked

09:31:14
Relationship verified

09:31:14
Graph updated
```

This should show actual system events, not fake animation.

---

# 51. BOTTOM COMMAND BAR

Adapt the reference bottom command interface.

CrimeKit version:

```text
Ask CrimeKit...

[Find connections]
[Trace evidence]
[Show timeline]
[Explain relationship]
[Expand graph]
[Find related devices]
```

AI responses must be evidence-grounded.

Do not allow AI to fabricate graph facts.

---

# 52. SEARCH → GRAPH FOCUS

Target workflow:

```text
Search
  ↓
Entity
  ↓
Graph focus
  ↓
Camera transition
  ↓
Inspector
```

The selected entity should become the visual center.

---

# 53. GRAPH CAMERA

Required interactions:

```text
Orbit
Pan
Zoom
Focus
Reset
Fit graph
Focus selection
```

Camera motion must be:

- smooth
- bounded
- interruptible
- accessible

Never force long cinematic camera animations that slow investigation.

---

# 54. GRAPH NAVIGATION

Controls should be minimal:

```text
+
-
home/reset
fit
fullscreen
```

Additional controls can appear contextually.

---

# 55. MINIMAP

Use a small overview panel if graph size justifies it.

The minimap should show:

```text
current camera region
major clusters
selected entity
```

Do not duplicate the entire graph at high detail.

---

# 56. GRAPH FILTERS

Minimum future filter categories:

```text
Entity type
Relationship type
Evidence type
Time range
Confidence
Status
Source
Processing run
```

Filters must be server-aware when they reduce database load.

---

# 57. TIME FILTER

Potential UI:

```text
[-----------●----------------]
08:00                       18:00
```

When time changes:

```text
graph state updates
```

Only implement deterministic temporal replay when the backend has sufficient event history.

---

# 58. LIVE EVENT MODE

When a new event arrives:

```text
Neo4j update
      ↓
realtime event
      ↓
3D graph
      ↓
new node/edge
      ↓
subtle pulse
```

Do not randomly animate unrelated nodes.

---

# 59. EVENT VISUALIZATION

A new event should show:

```text
LIVE
09:42:13

Device → IP
```

and allow:

```text
Open evidence
Open timeline
Inspect relationship
```

---

# 60. GRAPH STORIES

Potential investigator workflow:

```text
SELECT PERSON
     ↓
SELECT DEVICE
     ↓
TRACE CONNECTION
     ↓
SHOW SUPPORTING EVIDENCE
     ↓
SHOW TIMELINE
     ↓
SAVE INVESTIGATION PATH
```

The ontology must support path identity and provenance.

---

# 61. INVESTIGATION PATH

A path should be represented conceptually as:

```text
Path
 ├── Node 1
 ├── Relationship
 ├── Node 2
 ├── Relationship
 └── Node 3
```

The UI can allow:

```text
Save path
Annotate path
Export path
Open evidence
```

---

# 62. GRAPH ANNOTATIONS

Investigators may need:

```text
bookmark
annotation
review status
investigator note
```

These must be stored outside Neo4j if PostgreSQL is the authoritative application store.

Neo4j can receive projection metadata where appropriate.

---

# 63. GRAPH ANALYTICS

Neo4j Graph Data Science can eventually support:

```text
degree centrality
PageRank
community detection
shortest paths
similarity
connected components
```

Do not expose analytics simply because they exist.

Every metric must have a forensic interpretation.

---

# 64. ANALYTICS SAFETY

Never label:

```text
highest PageRank = offender
```

Instead:

```text
high network centrality
```

and provide:

```text
why this metric is shown
```

---

# 65. GRAPH EXPLAINABILITY

Every analytical highlight must have:

```text
Metric
Value
Calculation / source
Scope
Timestamp
Confidence
```

Example:

```text
WHY HIGHLIGHTED?

High relationship density

18 connected entities
7 evidence items
4 timeline events
```

Only display values that actually exist.

---

# 66. GRAPH AI BOUNDARY

AI can:

```text
query graph
summarize paths
explain relationships
find relevant evidence
suggest investigation paths
```

AI must not silently:

```text
create facts
change evidence
change provenance
declare guilt
```

---

# 67. GRAPH RAG

Future flow:

```text
Investigator question
        ↓
Intent
        ↓
Graph query
        ↓
Neo4j
        ↓
Evidence retrieval
        ↓
PostgreSQL/object storage
        ↓
LLM
        ↓
Verified response
        ↓
Sources
```

---

# 68. GRAPH QUERY API

The frontend must NOT connect directly to Neo4j.

Preferred:

```text
3D UI
  ↓
FastAPI
  ↓
Graph Service
  ↓
Neo4j
```

The API must enforce:

- authentication
- authorization
- case scope
- query limits
- timeouts
- pagination
- logging

---

# 69. GRAPH API CONCEPT

Possible response:

```json
{
  "case_id": "QTC-PROD-001",
  "nodes": [],
  "edges": [],
  "meta": {
    "count": 0,
    "generated_at": "...",
    "scope": "case"
  }
}
```

Do not copy this blindly.

Match the repository's existing API conventions.

---

# 70. GRAPH QUERY TYPES

Potential endpoints/services:

```text
GET graph overview
GET entity
GET neighbors
GET path
GET timeline graph
GET evidence graph
POST graph search
POST graph analytics
```

Only create endpoints actually required.

---

# 71. NEO4J CONSTRAINTS

Define constraints for stable identifiers.

Examples conceptually:

```cypher
CREATE CONSTRAINT person_id_unique
FOR (n:Person)
REQUIRE n.person_id IS UNIQUE;
```

Actual syntax/version must match the Neo4j deployment.

---

# 72. NEO4J INDEXES

Index:

- case_id
- stable IDs
- search keys
- temporal properties where justified

Avoid indiscriminate indexes.

---

# 73. GRAPH PROJECTION

Target:

```text
PostgreSQL
    ↓
Domain Event / Outbox
    ↓
Redis
    ↓
Graph Projection Worker
    ↓
Neo4j
```

The ontology must support idempotent projection.

---

# 74. IDEMPOTENCY

If the same event arrives twice:

```text
event A
event A
```

Neo4j must not create duplicate entities/relationships.

Use stable IDs and deterministic relationship keys.

---

# 75. GRAPH RECONCILIATION

The system should eventually support:

```text
PostgreSQL
     ↕
Neo4j
```

reconciliation.

Detect:

```text
missing node
missing edge
stale edge
wrong property
orphan graph record
```

---

# 76. GRAPH REBUILD

Neo4j should be reconstructible from authoritative data.

Target:

```text
PostgreSQL
   ↓
projection/rebuild
   ↓
Neo4j
```

Do not make Neo4j the only location where critical forensic facts exist.

---

# 77. 3D PERFORMANCE STRATEGY

The ontology must be compatible with progressive rendering.

Do not send:

```text
entire case graph
```

by default.

Prefer:

```text
overview
 ↓
selected entity
 ↓
local neighborhood
 ↓
progressive expansion
```

---

# 78. LEVEL OF DETAIL

Future graph rendering should support:

```text
LOD 0
cluster only

LOD 1
major nodes

LOD 2
nodes + edges

LOD 3
labels + metadata

LOD 4
provenance details
```

The ontology should allow the API to provide different levels of data.

---

# 79. 3D INSTANCING

If many visually similar nodes exist, use rendering techniques such as:

- instancing
- batched geometry
- GPU-friendly buffers

Do not implement during ontology work unless required.

The ontology should avoid unnecessary per-node payload bloat.

---

# 80. LABEL STRATEGY

Labels should be:

- short
- readable
- spatially stable
- collision-aware
- LOD-aware

Examples:

```text
John Smith
iPhone 14
Chennai
IMG_20240115.jpg
```

Do not display entire database records in the graph.

---

# 81. HOVER STATE

Hover should reveal a lightweight tooltip:

```text
PERSON
John Smith

6 relationships
8 evidence items
```

Only display available data.

---

# 82. CLICK STATE

Click should:

```text
focus node
highlight relationships
open inspector
show provenance option
show timeline option
```

---

# 83. DOUBLE-CLICK / EXPAND

Optional:

```text
double click
```

or:

```text
Expand
```

to fetch neighbors.

Avoid accidental huge expansions.

---

# 84. CONTEXT MENU

Possible actions:

```text
Focus
Expand
Trace path
View evidence
View timeline
Open entity
Bookmark
Hide node
```

Authorization must apply.

---

# 85. GRAPH TABLE MODE

3D should not be the only representation.

Provide:

```text
Graph | Table
```

similar to enterprise investigation tools.

Table should expose:

```text
Entity
Type
Relationships
Evidence
Confidence
Last observed
```

---

# 86. 2D FALLBACK

Provide a 2D graph fallback if:

- WebGL unavailable
- low-power device
- accessibility requirement
- performance threshold exceeded

The ontology must be renderer-independent.

---

# 87. ACCESSIBILITY

Do not depend only on:

```text
color
```

Use:

```text
shape
label
pattern
icon
text
```

Provide keyboard-accessible alternatives for graph selection and inspection where feasible.

---

# 88. DARK VISUAL SYSTEM

Target visual direction:

```text
near-black background
very dark blue/black secondary surfaces
thin subtle borders
soft cyan/blue/green/purple semantic accents
low-opacity connection lines
high-contrast white/gray labels
```

Avoid:

```text
large gradients
excessive glow
rainbow graphs
glassmorphism everywhere
oversaturated neon
```

---

# 89. CRIMEKIT BRANDING

Do not replace CrimeKit identity.

Keep:

```text
CrimeKit
```

brand and existing navigation language.

The graph becomes a specialized immersive workspace inside CrimeKit.

---

# 90. REFERENCE-STYLE 3D LAYOUT

Target conceptual layout:

```text
┌──────────────────────────────────────────────────────────────┐
│ CrimeKit        Case: QTC-PROD-001       Status / User       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                         3D GRAPH                             │
│                                                              │
│              ● Person                                        │
│                 \                                             │
│                  ● Device ───── ● IP                         │
│                 / \                                           │
│          ● Evidence   ● Location                             │
│                                                              │
│                                           ┌───────────────┐  │
│                                           │ INVESTIGATOR  │  │
│                                           │ INSPECTOR     │  │
│                                           │               │  │
│                                           │ Selected ...  │  │
│                                           └───────────────┘  │
│                                                              │
│             ┌────────────────────────────────┐               │
│             │ Ask CrimeKit...                │               │
│             └────────────────────────────────┘               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

This is a conceptual composition, not a requirement to use literal coordinates.

---

# 91. REFERENCE-STYLE GRAPH NODES

Create a reusable visual grammar.

Example:

```text
PERSON
      ◉
   orbital ring

DEVICE
      ◈
   compact geometry

LOCATION
      ●
   location marker

EVIDENCE
      ▣
   document geometry

EVENT
      ·
   temporal point
```

Actual geometry should be chosen based on readability and performance.

---

# 92. ORBITAL VISUAL EFFECT

The reference contains orbital/wireframe-like visual forms.

CrimeKit may use a restrained orbital treatment for:

- selected nodes
- active entities
- analytical focus
- live updates

Do NOT put expensive animated wireframes around every node.

Use them selectively.

---

# 93. LIVE PULSE

For a genuinely new realtime event:

```text
node appears
    ↓
subtle pulse
    ↓
relationship draws
    ↓
event badge
    ↓
settles
```

This gives the graph life without becoming distracting.

---

# 94. GRAPH PHYSICS

If force-directed layout is used:

- keep stable positions
- avoid constant movement
- freeze settled nodes
- use deterministic seeds where possible
- animate only when topology changes
- allow manual repositioning
- preserve investigator layout state where useful

A constantly moving graph is unacceptable for serious investigation.

---

# 95. SPATIAL MEMORY

If an investigator positions nodes:

```text
Person
Device
Evidence
```

the system should optionally remember the layout for the investigation workspace.

Do not store transient UI state in Neo4j unless there is a strong reason.

---

# 96. GRAPH SNAPSHOTS

Future capability:

```text
Save graph view
```

with:

```text
case_id
camera
selected entity
visible nodes
filters
time range
layout positions
timestamp
user
```

Store application state in the appropriate authoritative store.

---

# 97. GRAPH EXPORT

Future export options:

```text
PNG
SVG / 2D
CSV
JSON
investigation report
```

Do not expose raw graph data without authorization.

---

# 98. FORENSIC REPORT LINK

A graph path should eventually be exportable to a report:

```text
Selected path
     ↓
Supporting evidence
     ↓
Timeline
     ↓
Provenance
     ↓
Report section
```

---

# 99. GRAPH ANNOTATION SAFETY

Investigator notes must be clearly distinguished from evidence.

Example:

```text
OBSERVED FACT
ANALYTICAL RESULT
INVESTIGATOR NOTE
AI SUGGESTION
```

Never mix them.

---

# 100. GRAPH STATE MODEL

Define application graph state conceptually:

```text
graphData
selectedNode
selectedEdge
expandedNodes
hiddenNodes
filters
timeRange
camera
layout
loading
error
liveMode
analysisMode
```

Use the repository's actual frontend state architecture.

Do not create unnecessary duplicate state stores.

---

# 101. GRAPH LOADING STATES

Required states:

```text
Loading graph
Loading neighbors
Updating graph
No graph data
No case selected
No results
Permission denied
Graph unavailable
Realtime disconnected
```

---

# 102. ERROR STATES

Example:

```text
Knowledge graph unavailable

The investigation data could not be loaded.

Retry
```

Do not expose:

```text
Neo4j credentials
Cypher
stack traces
internal URLs
```

to end users.

---

# 103. EMPTY STATE

When no graph exists:

```text
No knowledge graph yet

Process evidence to generate entities and relationships.
```

Use actual CrimeKit workflow language.

---

# 104. GRAPH STATUS

The graph header may show:

```text
GRAPH
LIVE
SYNCING
STALE
OFFLINE
```

Only display states backed by actual system health.

---

# 105. GRAPH SYNCHRONIZATION STATUS

Potential:

```text
PostgreSQL
   ✓

Graph projection
   ✓

Neo4j
   ✓

Realtime
   ✓
```

This can become a compact diagnostics panel for administrators.

---

# 106. GRAPH DATA FRESHNESS

Expose when useful:

```text
Last graph update
Projection lag
```

Do not imply realtime if updates are delayed.

---

# 107. GRAPH SECURITY INDICATOR

The UI can show:

```text
CASE SCOPED
```

or similar.

Do not expose internal authorization details.

---

# 108. GRAPH ETHICS

The ontology must preserve distinctions between:

```text
fact
observation
correlation
inference
prediction
investigator note
AI suggestion
```

This is a core CrimeKit requirement.

---

# 109. NO GUILT VISUALIZATION

Never encode:

```text
large node = guilty
red node = guilty
central node = guilty
high score = guilty
```

The system visualizes investigative relevance, not guilt.

---

# 110. GRAPH REVIEW STATUS

Possible review states:

```text
UNREVIEWED
UNDER_REVIEW
VERIFIED
DISPUTED
REJECTED
```

These should be stored in the authoritative application layer and projected where useful.

---

# 111. GRAPH VERSIONING

Graph schema changes must be versioned.

Maintain:

```text
ontology_version
projection_version
model_version
```

where required.

---

# 112. ONTOLOGY DOCUMENTATION

Produce an ontology registry:

```text
Node Type
Description
Source
Properties
Relationships
Provenance
UI Representation
Security
```

---

# 113. RELATIONSHIP REGISTRY

Produce:

```text
Relationship
Meaning
Allowed source nodes
Allowed target nodes
Evidence requirement
Temporal support
Confidence support
UI treatment
```

Example:

```text
USES

Allowed:
Person → Device

Meaning:
Evidence indicates use/access.

Must NOT mean:
Legal ownership.
Identity confirmation.
Guilt.
```

---

# 114. GRAPH VALIDATION RULES

Validate:

```text
Person -[:USES]-> Device
```

but reject:

```text
Device -[:USES]-> Person
```

unless explicitly supported.

The ontology should prevent semantically invalid edges.

---

# 115. GRAPH SCHEMA VALIDATION

Implement or plan validation for:

- node labels
- relationship types
- required properties
- case IDs
- provenance
- confidence
- timestamps
- relationship direction

---

# 116. GRAPH DATA QUALITY

Detect:

```text
orphan nodes
duplicate nodes
duplicate edges
missing provenance
invalid relationship direction
missing case_id
stale records
```

---

# 117. GRAPH DATA QUALITY DASHBOARD

Future administrator view:

```text
Nodes
Edges
Orphans
Duplicate candidates
Missing provenance
Projection lag
Failed projections
```

Do not add to investigator UI unless useful.

---

# 118. GRAPH ANALYTICS UI

Possible analytical modes:

```text
Connections
Centrality
Communities
Paths
Temporal
Evidence density
```

Every analytical result must show methodology.

---

# 119. PATH ANALYSIS

Potential:

```text
Person A
  ↓
Device
  ↓
IP
  ↓
Location
  ↓
Person B
```

The UI should let the investigator inspect each hop.

---

# 120. PATH EVIDENCE

For each hop:

```text
Relationship
↓
Supporting evidence
↓
Artifact
↓
Timestamp
```

This is more important than visual styling.

---

# 121. MULTI-PATH COMPARISON

Potential future:

```text
Path A
Path B
```

with:

```text
common entities
different evidence
conflicting relationships
```

Do not implement unless supported by the data model.

---

# 122. TEMPORAL PATH

Potential:

```text
08:31 Person
  ↓
08:35 Device
  ↓
08:41 IP
  ↓
08:47 Location
```

Use the timeline system as the authoritative temporal source.

---

# 123. GRAPH REPLAY

If event history is sufficient:

```text
▶ Replay

08:00
08:05
08:10
08:15
```

Nodes/edges appear based on actual event history.

Never fake historical replay.

---

# 124. GRAPH "TIME MACHINE"

Potential interaction:

```text
Past ←──────────────→ Present
```

The system reconstructs graph state from authoritative events.

This is a future capability, not an assumption that it already exists.

---

# 125. GRAPH LENS ARCHITECTURE

Design the ontology so that future lenses can be implemented without changing the underlying schema:

```text
Relationship Lens
Evidence Lens
Timeline Lens
Location Lens
Risk Lens
Provenance Lens
Communication Lens
```

A lens is a visualization/query mode, not a separate database.

---

# 126. GRAPH CLUSTERING

Potential clustering dimensions:

```text
entity type
time
location
evidence
community
investigation path
```

The UI should support dynamic grouping.

---

# 127. CLUSTER COLLAPSE

If a cluster is large:

```text
[ 42 entities ]
```

Selecting it can expand locally.

Do not force the investigator to render every node.

---

# 128. GRAPH OVERVIEW MODE

Initial view should show:

```text
case context
major entities
major clusters
recent events
high-value evidence
```

Do not immediately load thousands of nodes.

---

# 129. GRAPH LOCAL MODE

When selecting an entity:

```text
center entity
+
1-hop neighbors
+
evidence
```

Then allow expansion.

---

# 130. GRAPH INVESTIGATION MODE

When a path is selected:

```text
hide unrelated graph
focus path
show evidence
show timeline
```

This reduces cognitive load.

---

# 131. GRAPH EVIDENCE MODE

When evidence is selected:

```text
Evidence
 ↓
Artifacts
 ↓
Entities
 ↓
Relationships
```

This is a forensic provenance view.

---

# 132. GRAPH TIMELINE MODE

When timeline is selected:

```text
Events
 ↓
Entities
 ↓
Evidence
```

Use time as the primary axis.

---

# 133. GRAPH CONTRADICTION MODE

Potential future view:

```text
SUPPORTED
   vs
CONTRADICTED
```

Use clear semantics.

Do not visually imply that a contradiction is false evidence; it means sources disagree or analysis conflicts.

---

# 134. GRAPH CONFIDENCE MODE

Potential:

```text
High confidence
Medium confidence
Low confidence
Unknown
```

Use:

- opacity
- edge style
- badges
- labels

not only color.

---

# 135. GRAPH PROVENANCE MODE

When activated:

```text
Entity
 ↓
Relationship
 ↓
Assertion
 ↓
Artifact
 ↓
Evidence
```

This could become one of CrimeKit's strongest differentiators.

---

# 136. PROVENANCE THREAD VISUALIZATION

Candidate interaction:

```text
Click relationship
        ↓
relationship expands into a provenance thread
        ↓
Evidence
   ↓
Artifact
   ↓
Processing
   ↓
Assertion
   ↓
Relationship
```

The UI should show exactly how the relationship was created.

---

# 137. GRAPH STORY MODE

Candidate interaction:

```text
Start
 ↓
Evidence
 ↓
Entity
 ↓
Relationship
 ↓
Entity
 ↓
Timeline
 ↓
Evidence
```

The investigator can save the path as an investigation story.

This is a candidate innovation, not an existing feature unless the repository proves it.

---

# 138. "WHY THIS CONNECTION?"

Every relationship inspector should potentially support:

```text
WHY THIS CONNECTION?

Observed in:
Evidence #123

Artifact:
browser_history

Processed by:
Forensic Pipeline v3

Observed:
2026-10-08 08:42

Confidence:
...

Review:
...
```

Only show actual data.

---

# 139. "WHAT SUPPORTS THIS?"

Provide an evidence-first action:

```text
Show supporting evidence
```

This should navigate to the evidence system.

---

# 140. "WHAT ELSE IS CONNECTED?"

Provide:

```text
Expand neighborhood
```

with bounded expansion.

---

# 141. "HOW DID WE GET HERE?"

Potential path explanation:

```text
Search result
 ↓
Entity match
 ↓
Graph relationship
 ↓
Evidence
```

This improves explainability.

---

# 142. 3D GRAPH MATERIAL SYSTEM

Use restrained materials.

Potential:

```text
matte
soft emissive
wireframe accent
```

Avoid expensive transparency on every node.

---

# 143. LIGHTING

Use subtle ambient/point lighting.

Do not create a cinematic game scene that reduces text readability.

---

# 144. STARFIELD / PARTICLE BACKGROUND

The reference uses a spatial/deep-space feeling.

If used in CrimeKit:

- keep it extremely subtle
- use it as environment only
- never let particles represent fake evidence
- do not consume excessive GPU resources

---

# 145. ANIMATION RULE

Every animation must answer:

> What information does this animation communicate?

Good:

```text
new realtime event
selected path
camera focus
graph expansion
```

Bad:

```text
constant decorative movement
```

---

# 146. MOTION ACCESSIBILITY

Support:

```text
reduced motion
```

Disable or reduce:

- orbital motion
- pulsing
- camera transitions
- animated graph transitions

when appropriate.

---

# 147. GRAPH AUDIO

Do not add sound merely because the reference has interactive controls.

If sound is used:

- optional
- muted by default
- meaningful
- accessible
- never required for understanding

---

# 148. RESPONSIVE BEHAVIOR

Desktop is primary for the 3D graph.

For smaller screens:

```text
graph
+
bottom sheet inspector
```

or a 2D/fallback mode.

Do not force a dense desktop layout onto mobile.

---

# 149. FULLSCREEN MODE

Provide:

```text
Enter fullscreen
Exit fullscreen
```

The graph should use the available viewport.

---

# 150. BROWSER COMPATIBILITY

Audit the repository's supported browsers and ensure the chosen renderer is compatible.

Graceful fallback must exist when WebGL capabilities are insufficient.

---

# 151. SECURITY IN 3D

Never send unauthorized graph data to the browser and rely on UI hiding.

Server-side authorization is mandatory.

---

# 152. PRIVACY IN 3D

Sensitive values may require masking:

```text
phone
email
IP
location
personal identifiers
```

Use role/case policies.

---

# 153. GRAPH EXPORT SECURITY

Exports must obey the same authorization as interactive graph queries.

---

# 154. NEO4J QUERY SECURITY

Never construct unsafe Cypher using raw user strings.

Use parameterized queries and a controlled query layer.

---

# 155. GRAPH INJECTION SAFETY

Do not allow investigators/AI to submit arbitrary Cypher directly to production Neo4j.

Use approved graph operations.

Administrative query tools must be separately protected.

---

# 156. AI GRAPH TOOL SAFETY

If AI can call graph tools:

Allowed:

```text
find_entity
get_neighbors
find_path
get_evidence
get_timeline
```

Avoid unrestricted:

```text
execute_arbitrary_cypher
```

unless explicitly protected for administrators.

---

# 157. AI EXPLANATION FORMAT

Future graph explanations should use:

```text
Finding
Evidence
Graph path
Confidence
Caveat
Sources
```

---

# 158. GRAPH AUDITABILITY

Every graph mutation must eventually be attributable to:

```text
actor
event
source
processing run
timestamp
```

---

# 159. REALTIME GRAPH EVENT SCHEMA

Conceptually:

```json
{
  "event_type": "GRAPH_NODE_ADDED",
  "case_id": "...",
  "entity_id": "...",
  "timestamp": "...",
  "source": "...",
  "version": 1
}
```

Match the existing CrimeKit event conventions.

---

# 160. REALTIME EDGE EVENT

Conceptually:

```json
{
  "event_type": "GRAPH_RELATIONSHIP_ADDED",
  "case_id": "...",
  "relationship_id": "...",
  "source_id": "...",
  "target_id": "...",
  "relationship_type": "...",
  "version": 1
}
```

---

# 161. EVENT ORDERING

The frontend must not assume arrival order equals event time.

Use:

```text
event_id
occurred_at
created_at
sequence/version
```

where available.

---

# 162. REALTIME DUPLICATION

Frontend should tolerate duplicate events.

Projection layer must be idempotent.

---

# 163. REALTIME RECONNECT

When the browser reconnects:

```text
detect gap
 ↓
request current graph state / replay
 ↓
resume realtime
```

Do not assume no events were missed.

---

# 164. GRAPH CACHE

If caching is used:

Cache keys must include:

```text
case_id
query parameters
authorization scope
graph version
```

Never share unauthorized graph results across cases.

---

# 165. GRAPH API PAGINATION

Large graph expansions must support:

```text
limit
cursor / continuation
```

where appropriate.

---

# 166. GRAPH QUERY LIMITS

Every endpoint must have bounded defaults.

Example concepts:

```text
max_nodes
max_edges
max_depth
timeout_ms
```

Actual values must be load-tested.

---

# 167. GRAPH OBSERVABILITY

Track:

```text
neo4j_latency
query_count
query_errors
projection_lag
projection_failures
graph_events
websocket_connections
graph_payload_size
3d_render_fps
3d_memory
```

The frontend should not expose internal metrics to ordinary investigators unless designed as diagnostics.

---

# 168. 3D PERFORMANCE TELEMETRY

Development/admin mode may measure:

```text
FPS
frame time
draw calls
GPU memory where available
node count
edge count
label count
```

Use this for engineering optimization.

---

# 169. GRAPH LOAD TESTING

Test:

```text
100 nodes
500 nodes
1,000 nodes
5,000 nodes
10,000 nodes
```

But do not claim the UI supports a size until it has been measured.

---

# 170. GRAPH QUERY TESTING

Test:

- neighbor query
- path query
- search
- time filtering
- evidence expansion
- case isolation
- permission filtering
- analytics

---

# 171. ONTOLOGY TESTING

Create fixtures that validate:

```text
valid node
valid relationship
invalid relationship
missing provenance
wrong case
duplicate ID
duplicate edge
contradiction
temporal relationship
```

---

# 172. SECURITY TESTING

Must test:

```text
User A cannot access Case B
User A cannot expand Case B
User A cannot retrieve Case B via search
User A cannot retrieve Case B via websocket
User A cannot export Case B
AI cannot retrieve unauthorized graph data
```

---

# 173. GRAPH RECOVERY

Verify that Neo4j can be rebuilt from authoritative application data.

This is a production requirement.

---

# 174. GRAPH MIGRATION

Ontology changes must be:

- versioned
- reversible where practical
- tested
- documented
- compatible with projection

---

# 175. GRAPH SCHEMA EVOLUTION

Avoid breaking all old nodes when adding a new entity type.

Prefer additive evolution.

---

# 176. CROSS-CASE GRAPH

Do not enable global cross-case graphs by default.

If a future authorized cross-case mode exists:

```text
explicit user permission
+
explicit scope
+
audit
+
data policy
```

---

# 177. CASE-LEVEL GRAPH ROOT

The graph workspace should always know:

```text
case_id
```

and the frontend should not infer case identity from graph nodes.

---

# 178. GRAPH ROUTING

Recommended conceptual route:

```text
/cases/{case_id}/knowledge-graph
```

Optional deep links:

```text
/cases/{case_id}/knowledge-graph?entity={entity_id}
```

Only if consistent with existing CrimeKit routing.

---

# 179. UI STATE URL SAFETY

Never encode:

- secrets
- evidence content
- unauthorized identifiers

into shareable URLs.

---

# 180. GRAPH SHARING

If graph views are shareable:

```text
permission check
case membership
snapshot state
expiry / revocation
audit
```

---

# 181. VISUAL HIERARCHY

The screen should visually prioritize:

```text
1. Graph
2. Selected entity
3. Relationship context
4. Inspector
5. Search / commands
6. Secondary controls
```

Do not let panels consume most of the viewport.

---

# 182. REFERENCE-LIKE MINIMALISM

The reference works because the graph has breathing room.

Use:

```text
large negative space
+
few high-value controls
```

Avoid:

```text
dashboard clutter
```

---

# 183. GRAPH TYPOGRAPHY

Labels should be:

- high contrast
- concise
- hierarchy-aware
- LOD-aware

Large selected labels.

Small peripheral labels.

Hide labels at extreme zoom-out.

---

# 184. EDGE LABELS

Show edge labels only when:

```text
selected
hovered
high importance
```

Do not label every relationship at once.

---

# 185. EDGE DIRECTION

Use arrows only where direction matters.

For symmetric relationships, avoid unnecessary arrows.

---

# 186. EDGE BUNDLING

For dense graph regions, consider visual bundling.

Do not implement blindly.

The audit must determine whether edge bundling improves readability.

---

# 187. GRAPH CLUTTER CONTROL

Use:

```text
focus
filter
LOD
collapse
expansion
path mode
```

before relying on rendering tricks.

---

# 188. GRAPH SEARCH RESULT

Search result should show:

```text
Entity
Type
Case
Evidence count
```

Then:

```text
Focus in graph
```

---

# 189. ENTITY INSPECTOR

Inspector should have tabs/sections such as:

```text
Overview
Relationships
Evidence
Timeline
Provenance
Analysis
```

Only show sections supported by actual data.

---

# 190. RELATIONSHIP INSPECTOR

When edge selected:

```text
RELATIONSHIP
Person → Device

Type
USES

Observed
...

Evidence
...

Confidence
...

Provenance
...
```

---

# 191. EVIDENCE INSPECTOR

When evidence selected:

```text
Evidence
Type
Hash
Collection
Processing
Artifacts
Related entities
```

---

# 192. TIMELINE INSPECTOR

When event selected:

```text
Timestamp
Timezone
Event type
Entity
Evidence
Location
Confidence
```

---

# 193. PROVENANCE INSPECTOR

Show:

```text
Source evidence
Artifact
Processing run
Extractor
Model
Timestamp
Review
```

---

# 194. GRAPH LEGEND

Provide a compact legend.

Example:

```text
● Person
◈ Device
● Location
▣ Evidence
· Event

━━ Observed
┄┄ Inferred
⚠ Contradicted
```

Actual visual forms should remain accessible.

---

# 195. VISUAL SEMANTICS TABLE

Produce a final table:

| Entity | Geometry | Primary semantic | Color family | Label | Inspector |
|---|---|---|---|---|---|
| Person | | identity | | | |
| Device | | digital | | | |
| Evidence | | source | | | |
| Location | | physical | | | |
| Event | | temporal | | | |

Fill using actual final design decisions.

---

# 196. RELATIONSHIP SEMANTICS TABLE

Produce:

| Relationship | Meaning | Direction | Visual | Provenance | Confidence |
|---|---|---|---|---|---|
| USES | | | | | |
| OWNS | | | | | |
| OBSERVED_AT | | | | | |
| SUPPORTS | | | | | |
| CONTRADICTS | | | | | |

---

# 197. GRAPH ONTOLOGY DELIVERABLE

The final output of this prompt must include:

```text
Node ontology
Relationship ontology
Property ontology
Provenance ontology
Temporal ontology
Confidence ontology
Review ontology
Case isolation model
Projection model
API model
3D semantic model
UI interaction model
```

---

# 198. NEO4J IMPLEMENTATION DELIVERABLE

Produce conceptual Cypher/schema definitions only after the ontology is validated.

Include:

```text
constraints
indexes
labels
relationship types
sample node creation
sample relationship creation
sample traversal
```

Do not modify the repository unless the next prompt explicitly requests implementation.

---

# 199. GRAPH QUERY EXAMPLES

Provide safe examples for:

### Case graph

```cypher
MATCH (n)
WHERE n.case_id = $case_id
RETURN n
LIMIT $limit
```

### Neighbors

```cypher
MATCH (n {id: $entity_id})-[r]-(m)
WHERE n.case_id = $case_id
  AND m.case_id = $case_id
RETURN n, r, m
LIMIT $limit
```

These are conceptual examples.

Use the actual repository's property names and constraints during implementation.

---

# 200. PATH QUERY

Use bounded path depth.

Concept:

```cypher
MATCH p =
  (a {id: $source_id})-[*1..3]-(b {id: $target_id})
WHERE ...
RETURN p
LIMIT $limit
```

Do not deploy arbitrary unbounded path traversal.

---

# 201. GRAPH QUERY RESULT NORMALIZATION

Backend should normalize Neo4j records into:

```text
nodes[]
edges[]
meta{}
```

rather than exposing raw Neo4j driver objects to the frontend.

---

# 202. NODE DTO

Potential:

```text
id
type
label
properties
position?
status?
confidence?
```

Do not duplicate large evidence payloads.

---

# 203. EDGE DTO

Potential:

```text
id
source
target
type
properties
confidence?
status?
```

---

# 204. GRAPH META

Potential:

```text
case_id
generated_at
graph_version
node_count
edge_count
truncated
```

---

# 205. GRAPH TRUNCATION

If a result is limited:

```text
truncated: true
```

The UI should communicate that more data exists.

Never silently hide the fact.

---

# 206. GRAPH QUERY EXPLANATION

Admin/developer diagnostics may record:

```text
query type
duration
result count
case scope
```

Do not expose raw Cypher to normal investigators.

---

# 207. GRAPH PROJECTION CONTRACT

Define:

```text
source event
graph mutation
idempotency key
case scope
provenance
retry
failure
```

---

# 208. GRAPH EVENT TYPES

Potential:

```text
ENTITY_CREATED
ENTITY_UPDATED
RELATIONSHIP_CREATED
RELATIONSHIP_UPDATED
RELATIONSHIP_REMOVED
EVIDENCE_LINKED
TIMELINE_EVENT_CREATED
GRAPH_RECONCILIATION_REQUIRED
```

Use the existing event taxonomy if one exists.

---

# 209. GRAPH EVENT VERSIONING

Every event should eventually support:

```text
event_type
event_version
event_id
occurred_at
created_at
case_id
payload
```

---

# 210. PROJECTION FAILURE

If projection fails:

```text
authoritative source remains intact
Neo4j may become stale
system marks projection failure
retry occurs
investigator is not shown false realtime status
```

---

# 211. GRAPH STALENESS

The UI should distinguish:

```text
LIVE
SYNCING
STALE
OFFLINE
```

rather than showing a false "LIVE".

---

# 212. NEO4J OUTAGE

If Neo4j is unavailable:

CrimeKit should degrade gracefully.

Possible:

```text
Knowledge graph temporarily unavailable
```

while:

- cases remain available
- evidence remains available
- authoritative data remains available

---

# 213. GRAPH CACHE OUTAGE

The graph system must not corrupt authoritative forensic data because a cache is unavailable.

---

# 214. 3D RENDERER OUTAGE

If WebGL fails:

```text
2D fallback
```

or:

```text
table graph
```

---

# 215. GRAPH UX FAILSAFE

Investigator must still be able to:

```text
search
open evidence
open timeline
inspect entities
```

without 3D.

---

# 216. AI AGENT OBSERVATORY REFERENCE ADAPTATION

Map reference concepts to CrimeKit carefully:

| Reference concept | CrimeKit adaptation |
|---|---|
| USER | Investigator |
| INTENT DETECTION | Investigation Intent |
| PLANNER | Investigation Planner |
| MEMORY | Case Context |
| LLM / REASONING | Evidence-grounded AI |
| VERIFIER | Evidence Verifier |
| TOOL HUB | Forensic Tool Hub |
| RESPONSE | Investigation Result |
| AGENT TRACE | Investigation Trace |

These are future UI concepts only.

Do not create them if CrimeKit does not actually support those services.

---

# 217. REFERENCE REPOSITORY AUDIT REQUIREMENT

Before implementing any copied visual behavior, inspect the referenced public repository and live application where legally/technically accessible.

Determine:

- framework
- renderer
- layout strategy
- animation
- graph engine
- state management
- UI structure
- dependencies
- license
- reusable ideas
- non-reusable implementation details

Do not blindly copy.

If exact source cannot be verified, say so.

---

# 218. VISUAL PARITY TARGET

The implementation should aim for:

```text
same visual quality
same spatial immersion
same interaction density
same dark-space composition
same sense of depth
same graph-centered focus
same inspector pattern
same bottom command pattern
```

while changing:

```text
AI agent semantics
↓
forensic semantics
```

and preserving:

```text
CrimeKit brand
CrimeKit backend
CrimeKit security
CrimeKit evidence model
```

---

# 219. "100% SAME DESIGN" INTERPRETATION

Treat the user's request for "100% same design" as:

> **100% faithful to the requested visual direction and interaction composition, while implementing CrimeKit-specific data and preserving original product identity.**

Do NOT claim literal pixel identity with a third-party application unless the implementation has been visually tested against a fixed reference and licensing allows the reuse.

---

# 220. ORIGINALITY REQUIREMENT

The strongest differentiation should come from combining:

```text
3D graph
+
forensic provenance
+
timeline
+
evidence
+
relationship confidence
+
contradiction
+
realtime events
+
investigator path
+
AI explanation
```

rather than simply adding futuristic graphics.

---

# 221. HIGH-VALUE NOVEL INTERACTION CANDIDATES

Evaluate these against the repository:

## A. Provenance Thread

Click edge → reveal evidence chain.

## B. Temporal Graph Time Machine

Move time → graph reconstructs.

## C. Evidence Emergence

Replay processing → entities appear as evidence is processed.

## D. Contradiction Layer

Show conflicting sources.

## E. Investigation Story

Save graph path + evidence + timeline as a reviewable investigation chain.

## F. Forensic Lens

Change graph semantics without changing data.

## G. Graph-to-Evidence Jump

Any edge → source evidence.

## H. Evidence-to-Graph Jump

Any evidence → all derived graph entities.

## I. Live Forensic Pulse

New evidence/event creates a meaningful graph update.

## J. Explainable Focus

System explains why an entity/path is highlighted.

---

# 222. NOVELTY SCORING

Score each concept:

```text
Forensic value /10
Technical feasibility /10
Differentiation /10
Explainability /10
Scalability /10
Security /10
UX value /10
```

Do not claim global uniqueness.

---

# 223. INVESTIGATOR COGNITIVE LOAD

The design must reduce:

```text
searching
cross-referencing
opening many screens
remembering relationship paths
finding source evidence
```

The graph should increase:

```text
context
traceability
relationship understanding
temporal understanding
evidence verification
```

---

# 224. GRAPH COGNITIVE SAFETY

Do not create visual effects that cause investigators to infer:

```text
correlation = causation
centrality = guilt
prediction = fact
confidence = truth
AI suggestion = evidence
```

The UI should actively preserve these distinctions.

---

# 225. FINAL ONTOLOGY QUALITY GATE

Do not approve the ontology until these are true:

```text
✓ stable IDs
✓ case isolation
✓ semantically valid relationships
✓ provenance
✓ temporal support
✓ confidence support where justified
✓ review state
✓ authoritative source defined
✓ projection path defined
✓ realtime compatibility
✓ 3D compatibility
✓ AI boundary
✓ security boundary
✓ scalable query strategy
```

---

# 226. REQUIRED FINAL OUTPUT — ONTOLOGY

Produce:

```text
1. Node ontology
2. Relationship ontology
3. Property ontology
4. Provenance model
5. Temporal model
6. Confidence model
7. Review model
8. Case isolation
9. Projection architecture
10. Neo4j schema
```

---

# 227. REQUIRED FINAL OUTPUT — VISUAL ONTOLOGY

Produce:

```text
1. Node geometry
2. Node color
3. Node scale
4. Edge style
5. Edge animation
6. Label rules
7. Selection rules
8. Hover rules
9. Inspector
10. Timeline
11. Provenance
12. Realtime
13. Filters
14. Search
15. Camera
16. LOD
17. Performance
18. Accessibility
```

---

# 228. REQUIRED FINAL OUTPUT — SCREEN ARCHITECTURE

Produce a detailed screen map:

```text
Knowledge Graph
├── Top Navigation
├── Case Context
├── 3D Canvas
│   ├── Nodes
│   ├── Edges
│   ├── Labels
│   ├── Clusters
│   └── Timeline effects
├── Right Inspector
├── Bottom Command Bar
├── Search
├── Filters
├── Minimap
├── Camera Controls
└── Status
```

---

# 229. REQUIRED FINAL OUTPUT — COMPONENT MAP

Map each visual component to likely repository files.

Use:

```text
Existing
Modify
New
```

categories.

Do not invent filenames before inspecting the repository.

---

# 230. REQUIRED FINAL OUTPUT — API MAP

Map:

```text
UI action
↓
API
↓
service
↓
Neo4j
↓
PostgreSQL/evidence
```

---

# 231. REQUIRED FINAL OUTPUT — DATA FLOW

Produce:

```text
Evidence
 ↓
Artifact
 ↓
Entity extraction
 ↓
Entity resolution
 ↓
Relationship assertion
 ↓
PostgreSQL
 ↓
Domain event
 ↓
Redis
 ↓
Neo4j projection
 ↓
Graph API
 ↓
3D rendering
```

Clearly mark actual vs planned.

---

# 232. REQUIRED FINAL OUTPUT — IMPLEMENTATION ORDER

Recommend the implementation sequence:

```text
1. Validate ontology
2. Validate Neo4j schema
3. Build projection
4. Build graph API
5. Build graph DTO
6. Build 3D renderer
7. Build node semantics
8. Build edge semantics
9. Build selection/inspector
10. Build search/focus
11. Build filtering
12. Build provenance
13. Build timeline
14. Build realtime
15. Build analytics
16. Build AI graph tools
17. Performance optimization
18. Security testing
19. Production hardening
```

Adjust based on repository findings.

---

# 233. REQUIRED FINAL OUTPUT — IMPLEMENTATION GATES

Define:

```text
Gate 1 — Ontology
Gate 2 — Neo4j
Gate 3 — Projection
Gate 4 — API
Gate 5 — 3D
Gate 6 — Provenance
Gate 7 — Realtime
Gate 8 — Security
Gate 9 — Performance
Gate 10 — Production
```

Each gate must have measurable acceptance criteria.

---

# 234. NO MOCK GRAPH IN PRODUCTION

Development may use fixtures.

Production must use:

```text
real CrimeKit data
```

through:

```text
PostgreSQL → projection → Neo4j
```

Do not hardcode graph nodes into the UI.

---

# 235. NO FAKE REALTIME

Do not animate graph nodes on a timer and call it realtime.

Realtime must originate from actual:

```text
event
```

or:

```text
graph update
```

---

# 236. NO FAKE PROVENANCE

Do not create placeholder:

```text
Evidence #123
```

unless it exists as a real fixture/test record.

---

# 237. NO FAKE CONFIDENCE

Do not display:

```text
Confidence: 97%
```

unless a real algorithm produces that score.

---

# 238. NO FAKE ANALYTICS

Do not display:

```text
Centrality: 0.91
Risk: High
```

unless the metric exists.

---

# 239. NO DECORATIVE DATA

Every number in the graph UI must have a source.

Examples:

```text
24 entities
8 evidence
12 relationships
```

must correspond to actual query results.

---

# 240. GRAPH SOURCE LABELING

Where useful, distinguish:

```text
OBSERVED
EXTRACTED
INFERRED
AI-SUGGESTED
INVESTIGATOR-ANNOTATED
```

---

# 241. AI-SUGGESTED RELATIONSHIPS

If the future system proposes a relationship:

```text
AI SUGGESTION
```

must be visibly distinct from:

```text
OBSERVED FACT
```

and require review before becoming an authoritative graph assertion.

---

# 242. GRAPH REVIEW FLOW

Potential:

```text
AI suggestion
 ↓
Evidence
 ↓
Investigator review
 ↓
Accept / Reject
 ↓
Audit
 ↓
Graph state
```

---

# 243. RELATIONSHIP LIFECYCLE

Define:

```text
PROPOSED
 ↓
REVIEWED
 ↓
ACCEPTED / REJECTED
 ↓
ACTIVE / DEPRECATED
```

Use only if the application actually needs this lifecycle.

---

# 244. GRAPH CHANGE HISTORY

Important graph changes should eventually be traceable.

Do not overwrite forensic history without audit.

---

# 245. GRAPH SNAPSHOT INTEGRITY

Saved graph snapshots must identify:

```text
case
user
time
filters
graph version
```

---

# 246. GRAPH REPORT INTEGRITY

Reports generated from graph paths must reference:

```text
source evidence
relationship IDs
graph version
processing version
```

where appropriate.

---

# 247. GRAPH DATA RETENTION

Follow the platform's evidence retention policies.

Do not invent retention periods.

---

# 248. GRAPH DELETION

Graph deletion must respect:

```text
legal hold
evidence retention
audit
case lifecycle
```

Do not simply delete Neo4j nodes because a UI item was removed.

---

# 249. GRAPH SOFT DELETE

If application semantics require it:

```text
status = DEPRECATED
```

or equivalent.

The actual approach must follow CrimeKit's domain model.

---

# 250. GRAPH IMPORT

If importing external graph data:

- validate schema
- validate case scope
- validate provenance
- validate source
- validate identifiers

---

# 251. GRAPH EXTERNAL DATA

External intelligence must be distinguishable from forensic evidence.

Example:

```text
SOURCE: EXTERNAL
```

Do not blend it silently with collected evidence.

---

# 252. GRAPH SOURCE PRIORITY

Potential source classes:

```text
FORENSIC EVIDENCE
SYSTEM ARTIFACT
EXTERNAL SOURCE
AI INFERENCE
INVESTIGATOR INPUT
```

Use provenance to preserve origin.

---

# 253. GRAPH MERGE SAFETY

Entity resolution must not silently merge:

```text
Person A
Person B
```

just because names match.

The graph should preserve:

```text
candidate
confidence
source
review
```

where identity resolution is uncertain.

---

# 254. ENTITY RESOLUTION VISUALIZATION

Potential future UI:

```text
Candidate match

John Smith
      ↕
Similarity / evidence
      ↕
John Smith
```

Then:

```text
Review
```

Do not imply identity until verified.

---

# 255. GRAPH DUPLICATE HANDLING

Detect:

```text
duplicate entity
duplicate relationship
duplicate artifact
```

and surface administrative quality issues.

---

# 256. GRAPH SEMANTIC VERSION

The ontology should have a version:

```text
ontology_version = ...
```

This enables controlled evolution.

---

# 257. GRAPH DOCUMENTATION

The final implementation should generate machine-readable documentation if practical:

```text
ontology.json
```

or equivalent.

Do not create it during this prompt unless requested.

---

# 258. GRAPH TYPE SAFETY

If using TypeScript:

Define typed graph DTOs.

If using Python:

Define Pydantic models.

Reuse existing repository patterns.

---

# 259. GRAPH TEST FIXTURES

Create representative fixture cases:

```text
Case A
 Person
 Device
 IP
 Location
 Evidence
 Event
```

with provenance.

Use these for integration testing later.

---

# 260. 3D DEMO CASE

The reference screenshot can inspire a demo graph:

```text
Person
 ├── Device
 ├── IP
 ├── Email
 ├── Location
 ├── Evidence
 └── TimelineEvent
```

But production must replace fixture data with real case data.

---

# 261. GRAPH UI DEMO

If building a visual prototype before backend integration:

Clearly label:

```text
DEMO DATA
```

Do not make it appear like real forensic data.

---

# 262. GRAPH UI DESIGN TOKENS

Define:

```text
background
surface
border
text
muted text
accent
node colors
edge colors
status colors
```

Use the existing CrimeKit design system where possible.

---

# 263. COLOR ACCESSIBILITY

Test contrast.

Never use subtle colors that become invisible against the dark background.

---

# 264. GRAPH VISUAL DENSITY

Target:

```text
calm
technical
precise
immersive
```

not:

```text
chaotic
game-like
overloaded
```

---

# 265. VISUAL DEPTH

Use:

- perspective
- depth
- scale
- controlled glow
- subtle lighting

to establish hierarchy.

Do not use depth to hide information.

---

# 266. GRAPH DEPTH CUES

Selected node:

```text
foreground emphasis
```

neighbors:

```text
midground
```

unrelated graph:

```text
background / reduced opacity
```

This is a visual focus mechanism.

---

# 267. FOCUS TRANSITION

When selecting a node:

```text
camera moves
graph dims
node emphasizes
neighbors reveal
inspector opens
```

All transitions should be fast enough for investigation.

---

# 268. SELECTION HISTORY

Potential:

```text
Back
Forward
```

for graph navigation.

This can greatly improve investigative exploration.

Evaluate against the existing frontend router/state model.

---

# 269. GRAPH BREADCRUMB

Potential:

```text
Case
 > Knowledge Graph
 > John Smith
 > iPhone 14
```

This helps investigators understand current context.

---

# 270. GRAPH SEARCH HISTORY

Potential:

```text
recent searches
```

Must respect case privacy.

---

# 271. GRAPH BOOKMARKS

Investigators may bookmark:

```text
entity
relationship
path
view
```

Use PostgreSQL/application state as authoritative.

---

# 272. GRAPH COLLABORATION

If future collaboration exists:

```text
investigator A
investigator B
```

can annotate the same graph.

Do not implement unless required.

---

# 273. GRAPH AUDIT TRAIL

Important user actions:

```text
searched
expanded
viewed evidence
saved path
exported graph
reviewed relationship
```

may be audit events depending on CrimeKit's governance requirements.

---

# 274. GRAPH QUERY AUDIT

For sensitive investigations, log:

```text
who
case
what query operation
when
```

without unnecessarily storing sensitive query contents.

---

# 275. GRAPH API RATE LIMITING

Production graph APIs must have appropriate limits.

Do not allow one browser to overwhelm Neo4j.

---

# 276. GRAPH WEBSOCKET LIMITING

Limit:

```text
subscriptions
connections
case channels
```

per authorization policy.

---

# 277. GRAPH MULTI-TENANCY

If CrimeKit later supports multiple organizations:

```text
tenant_id
+
case_id
```

may be required.

Do not assume tenant model exists unless repository confirms it.

---

# 278. GRAPH DATA CLASSIFICATION

Sensitive fields should carry appropriate classification if CrimeKit has such a model.

---

# 279. GRAPH ENCRYPTION

Neo4j connections should use secure transport in production.

Secrets must never be committed.

---

# 280. GRAPH SECRET MANAGEMENT

Do not store:

```text
NEO4J_PASSWORD
OPENAI_API_KEY
```

in source code.

Use environment/secret management consistent with deployment.

---

# 281. GRAPH CONNECTION POOL

Production Neo4j driver configuration should eventually consider:

```text
pool
timeouts
max connection lifetime
retries
health checks
```

Use driver defaults only when they are appropriate and tested.

---

# 282. GRAPH TRANSACTION BOUNDARIES

Projection workers should use safe transaction boundaries.

Avoid giant transactions for large evidence processing.

---

# 283. GRAPH BATCHING

Batch graph writes where safe.

Do not sacrifice provenance/idempotency for raw throughput.

---

# 284. GRAPH RETRIES

Retry transient Neo4j failures.

Do not blindly retry permanent schema/data errors.

---

# 285. DEAD LETTER

Failed projection events should eventually be recoverable.

---

# 286. GRAPH REPLAY

A projection worker should eventually support replaying events.

---

# 287. GRAPH RECONCILIATION JOB

Periodic reconciliation may compare:

```text
authoritative record count
vs
graph projection
```

and identify drift.

---

# 288. GRAPH HEALTH ENDPOINT

Potential:

```text
/health/graph
```

returning safe status.

Follow existing health endpoint conventions.

---

# 289. GRAPH METRICS

Production monitoring should include:

```text
projection_lag
projection_errors
neo4j_latency
query_errors
graph_nodes
graph_edges
```

---

# 290. GRAPH DEPLOYMENT

The ontology must remain compatible with:

```text
Neo4j Aura
```

and local development.

---

# 291. LOCAL DEVELOPMENT

Developers should be able to run:

```text
CrimeKit
+
PostgreSQL
+
Redis
+
Neo4j
```

without production secrets.

---

# 292. NEO4J AURA

Production should use secure Aura connectivity.

Do not expose Aura credentials to the browser.

---

# 293. GRAPH BACKUP

Neo4j backup strategy must align with deployment.

But the authoritative application data must still allow graph reconstruction.

---

# 294. GRAPH DR

Disaster recovery:

```text
PostgreSQL
+
object storage
+
Neo4j
+
configuration
```

must be recoverable.

---

# 295. GRAPH COST CONTROL

Do not create unlimited Graph Data Science sessions or unnecessary large traversals.

Use resource-aware analytics.

---

# 296. GRAPH ANALYTICS SESSION

If Neo4j GDS is used, document:

```text
graph projection
algorithm
memory
duration
result
```

Do not confuse GDS projection with the permanent application graph.

---

# 297. GDS RESULT PROVENANCE

Any analytical result should identify:

```text
algorithm
version
graph snapshot
parameters
timestamp
```

---

# 298. GRAPH AI + GDS

AI may explain GDS results but must not invent their meaning.

---

# 299. GRAPH EXPLANATION

Example:

```text
This entity is highly connected within the selected case graph.

Metric:
Degree centrality

Observed:
18 direct relationships

Source:
Case graph snapshot #...
```

Only if actually measured.

---

# 300. GRAPH DESIGN PHILOSOPHY

Final visual philosophy:

```text
Dark.
Spatial.
Precise.
Forensic.
Calm.
Explainable.
Interactive.
Evidence-first.
```

Not:

```text
Cyberpunk.
Chaotic.
Decorative.
Game-like.
AI-hype.
```

---

# 301. FINAL GRAPH ONTOLOGY DIAGRAM

Produce a diagram similar to:

```text
                         ┌──────────────┐
                         │     CASE     │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │ INVESTIGATION│
                         └──────┬───────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
   ┌────▼────┐             ┌────▼────┐             ┌───▼────┐
   │ PERSON  │             │ DEVICE  │             │LOCATION│
   └────┬────┘             └────┬────┘             └───┬────┘
        │                       │                       │
        ├──────────────┐        │                       │
        │              │        │                       │
   ┌────▼────┐    ┌────▼────┐   │                  ┌───▼──────┐
   │ ACCOUNT │    │ PHONE   │   │                  │TIMELINE  │
   └─────────┘    └─────────┘   │                  │  EVENT   │
                                │                  └──────────┘
                           ┌────▼────┐
                           │   IP    │
                           └─────────┘

                EVIDENCE / ARTIFACT
                        │
                        ▼
                 PROCESSING RUN
                        │
                        ▼
                 GRAPH ASSERTION
```

Adapt based on actual repository entities.

---

# 302. REQUIRED GRAPH ONTOLOGY TABLE

Final answer must include:

| Node | Purpose | Source | Stable ID | Key relationships | Provenance |
|---|---|---|---|---|---|
| Case | | | | | |
| Person | | | | | |
| Device | | | | | |
| Account | | | | | |
| Evidence | | | | | |
| Artifact | | | | | |
| Location | | | | | |
| TimelineEvent | | | | | |
| Observation | | | | | |
| ProcessingRun | | | | | |

---

# 303. REQUIRED RELATIONSHIP TABLE

| Relationship | Source | Target | Meaning | Evidence | Temporal | Confidence |
|---|---|---|---|---|---|---|
| USES | | | | | | |
| OWNS | | | | | | |
| ACCESSED | | | | | | |
| OBSERVED_AT | | | | | | |
| CONTAINS | | | | | | |
| SUPPORTS | | | | | | |
| CONTRADICTS | | | | | | |
| MENTIONS | | | | | | |
| APPEARS_IN | | | | | | |
| INVOLVED_IN | | | | | | |

---

# 304. REQUIRED VISUAL MAPPING TABLE

| Domain | 3D geometry | Color | Edge treatment | Label | Inspector |
|---|---|---|---|---|---|
| Person | | | | | |
| Device | | | | | |
| Account | | | | | |
| Location | | | | | |
| Evidence | | | | | |
| Artifact | | | | | |
| Event | | | | | |
| Processing | | | | | |

---

# 305. REQUIRED REFERENCE-STYLE SCREEN MAP

Produce:

```text
SCREEN 01 — Graph Overview
SCREEN 02 — Entity Focus
SCREEN 03 — Relationship Inspector
SCREEN 04 — Evidence Provenance
SCREEN 05 — Timeline Lens
SCREEN 06 — Realtime Event
SCREEN 07 — Path Investigation
SCREEN 08 — Graph Analytics
SCREEN 09 — AI Explanation
SCREEN 10 — Table / Fallback
```

For each:

```text
purpose
layout
data
interaction
API
performance
security
```

---

# 306. REQUIRED NEXT-PROMPT HANDOFF

At the end generate a handoff for:

## PROMPT #4 — NEO4J PRODUCTION SCHEMA + CONSTRAINTS

Must include:

- confirmed node labels
- relationship types
- properties
- constraints
- indexes
- case isolation
- provenance
- temporal fields

## PROMPT #5 — GRAPH PROJECTION ENGINE

Must include:

- PostgreSQL source
- events
- Redis
- worker
- idempotency
- retries
- reconciliation

## PROMPT #6 — GRAPH API

Must include:

- endpoints
- DTOs
- query limits
- authorization
- pagination
- graph normalization

## PROMPT #7 — 3D ENGINE

Must include:

- renderer
- scene
- camera
- node system
- edge system
- labels
- LOD
- interaction

## PROMPT #8 — REFERENCE UI IMPLEMENTATION

Must include:

- dark spatial design
- graph canvas
- inspector
- command bar
- controls
- CrimeKit branding
- responsive behavior

---

# 307. FINAL DECISION RULE

Do not proceed to implementation if:

```text
ontology is ambiguous
OR
case isolation is unclear
OR
provenance is missing
OR
relationship semantics are ambiguous
OR
source of truth is unclear
```

Resolve those first.

---

# 308. MASTER PRINCIPLE

The final CrimeKit 3D Knowledge Graph should feel like:

> **An investigative command environment where the investigator is exploring a living evidence-derived universe.**

Not:

> a normal database graph with 3D effects.

The graph should communicate:

```text
RELATIONSHIP
TIME
EVIDENCE
PROVENANCE
UNCERTAINTY
CONTEXT
```

through one coherent spatial interface.

---

# 309. FINAL QUALITY BAR

Before approving the ontology ask:

### Data

```text
Can every important graph fact be traced to data?
```

### Evidence

```text
Can every important relationship be traced to evidence?
```

### Security

```text
Can unauthorized users ever see another case?
```

### Explainability

```text
Can investigators understand why a relationship exists?
```

### 3D

```text
Does spatial visualization improve investigation?
```

### Performance

```text
Can the graph progressively scale?
```

### Realtime

```text
Can new evidence/events appear without fake animation?
```

### AI

```text
Can AI explain without becoming the source of truth?
```

### Ethics

```text
Does the UI avoid turning correlation into guilt?
```

### Production

```text
Can Neo4j be rebuilt from authoritative data?
```

---

# 310. FINAL DIRECTIVE

You are not designing a concept mockup.

You are defining the **production ontology and visual semantics** for CrimeKit.

Use the AI Agent Observatory reference to reproduce the desired:

```text
3D spatial experience
visual density
dark environment
graph immersion
inspector pattern
command interaction
motion discipline
```

but transform its semantics into:

```text
DIGITAL FORENSICS
EVIDENCE
ENTITIES
RELATIONSHIPS
TIMELINE
PROVENANCE
INVESTIGATION
```

The final system must be:

```text
SCALABLE
EXPLAINABLE
ETHICAL
SECURE
CASE-ISOLATED
PROVENANCE-AWARE
REALTIME-CAPABLE
PERFORMANT
MAINTAINABLE
PRODUCTION-READY
```

The final design target is:

```text
                    CRIMEKIT
                       │
                FORENSIC CASE
                       │
                 KNOWLEDGE GRAPH
                       │
          ┌────────────┼────────────┐
          │            │            │
       ENTITIES     EVIDENCE     TIMELINE
          │            │            │
          └────────────┼────────────┘
                       │
                  NEO4J GRAPH
                       │
              GRAPH INTELLIGENCE
                       │
              ┌────────┴────────┐
              │                 │
           3D VIEW          AI EXPLANATION
              │                 │
              └────────┬────────┘
                       │
                 INVESTIGATOR
                       │
                HUMAN REVIEW
```

Do the ontology rigorously.

Do not guess repository capabilities.

Do not fabricate data.

Do not fabricate confidence.

Do not fabricate realtime.

Do not fabricate provenance.

Do not make the graph visually impressive at the cost of forensic correctness.

Build the foundation for a world-class CrimeKit 3D Knowledge Graph.
