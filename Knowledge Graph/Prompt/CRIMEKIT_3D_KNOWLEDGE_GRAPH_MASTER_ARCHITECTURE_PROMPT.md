# CrimeKit — 3D Knowledge Graph
# MASTER ARCHITECTURE IMPLEMENTATION PROMPT
## Principal Architect / Staff Engineer / Neo4j / 3D Visualization / Digital Forensics

> **Mission:** Build a production-grade, end-to-end, interactive 3D Knowledge Graph inside the existing CrimeKit digital-forensics platform. This is not a toy visualization, not a standalone demo, and not a replacement for CrimeKit. It is a controlled extension of the existing application.

---

## 1. ROLE

Act as a **Principal Software Architect, Staff Full-Stack Engineer, Neo4j Graph Architect, 3D Visualization Engineer, Distributed Systems Engineer, Digital-Forensics Platform Engineer, Security Architect, and Production QA Lead**.

You are responsible for architecture, implementation, integration, validation, security, performance, reliability, and maintainability.

Before changing anything:
- inspect the repository;
- understand current architecture;
- identify reusable components;
- inspect existing Neo4j integration;
- inspect existing Knowledge Graph page;
- inspect FastAPI routes;
- inspect PostgreSQL models;
- inspect Redis/realtime implementation;
- inspect authentication and authorization;
- inspect current frontend state management;
- inspect existing graph/3D dependencies;
- inspect styling/design system;
- inspect deployment configuration.

Do not guess when repository evidence exists.
Do not rewrite working systems unnecessarily.
Do not introduce competing frameworks without a concrete reason.

---

# 2. PRIMARY OBJECTIVE

Build this complete path:

```text
CrimeKit Case
      |
      v
Authoritative CrimeKit Data
      |
      +----------------------+
      |                      |
      v                      v
PostgreSQL              Evidence Storage
      |
      v
Domain Events / Outbox
      |
      v
Redis / Event Pipeline
      |
      v
Graph Projection Worker
      |
      v
Neo4j Aura
      |
      +-----------------------------+
      |                             |
      v                             v
Cypher                       Graph Data Science
      |                             |
      +-------------+---------------+
                    |
                    v
              FastAPI Graph API
                    |
                    v
          3D Knowledge Graph Engine
                    |
                    v
             CrimeKit UI
                    |
          +---------+---------+
          |                   |
          v                   v
   Investigator UI      Realtime Events
```

The investigator must be able to:
1. Open a case.
2. Open Knowledge Graph.
3. See a useful 3D representation of authorized entities and relationships.
4. Search entities.
5. Filter graph data.
6. Select nodes and relationships.
7. Inspect properties.
8. Expand/collapse neighborhoods.
9. Focus and navigate the 3D camera.
10. Find paths between entities.
11. Inspect evidence supporting relationships.
12. Inspect forensic provenance.
13. Correlate with timeline information.
14. Run graph analytics.
15. See meaningful risk/priority indicators without equating them to guilt.
16. Receive realtime graph changes.
17. Preserve authorization and case isolation.
18. Navigate from graph facts back to source evidence.
19. Use a table representation when 3D is not sufficient.
20. Never treat AI, graph analytics, or model scores as proof of guilt.

---

# 3. NON-NEGOTIABLE ARCHITECTURAL PRINCIPLES

## 3.1 Preserve existing CrimeKit

Do not redesign the entire application. Reuse working:
- routes;
- services;
- repositories;
- authentication;
- authorization;
- database schemas;
- state stores;
- UI components;
- design tokens;
- realtime infrastructure;
- deployment patterns.

If an existing component can be extended safely, extend it.
If a replacement is genuinely required, document why before implementing it.

## 3.2 PostgreSQL remains authoritative

Neo4j is the **relationship intelligence projection**, not the authoritative forensic record.

Use:

| System | Responsibility |
|---|---|
| PostgreSQL | authoritative application/forensic domain records |
| Object Storage | original evidence / large files |
| Redis/Event Bus | realtime events and jobs |
| Neo4j | entities, relationships, investigation graph |
| pgvector | existing vector retrieval where appropriate |
| Neo4j Vector Index | graph-connected semantic retrieval where appropriate |
| Neo4j GDS | graph analytics / graph ML |
| FastAPI | API, business logic, security boundary |
| Next.js/React | investigator interface |
| WebSocket/SSE | realtime UI updates |
| AI layer | evidence-grounded reasoning and explanation |

The graph must be reproducible from authoritative CrimeKit data.

## 3.3 Never expose Neo4j directly to the browser

Correct:

```text
Browser -> FastAPI -> Authorization -> Neo4j
```

Incorrect:

```text
Browser -> Neo4j
```

All graph access is authenticated and authorized server-side.

## 3.4 Case isolation is mandatory

Case isolation must be enforced in:
- API;
- service layer;
- Cypher;
- projection;
- caches;
- WebSockets;
- event routing;
- AI retrieval;
- graph analytics.

Frontend filtering is never a security boundary.

---

# 4. FORENSIC TRUST MODEL

Every important graph relationship must answer:

> **Why does CrimeKit believe this relationship exists?**

Store and expose, where applicable:
- `case_id`
- `evidence_id`
- `artifact_id`
- `processing_run_id`
- `source_event_id`
- `observed_at`
- `created_at`
- `confidence`
- `extraction_method`
- `model_version`
- `source_system`
- provenance metadata.

Example:

```text
Person P001
    |
    | USES
    |
Device D001

Supporting information:
case_id = CASE-001
evidence_id = EVD-1042
artifact_id = ART-8802
processing_run_id = RUN-22
extraction_method = entity_resolution
confidence = 0.94
observed_at = 2026-10-08T08:31:12Z
```

The UI must allow investigators to navigate from relationship -> artifact -> evidence -> source.

---

# 5. VISUAL / UX DIRECTION

The requested interaction model is inspired by the supplied 3D AI-Agent Observatory reference and Neo4j-inspired enterprise UI:
- large 3D graph canvas;
- spatial node layout;
- animated relationship paths;
- zoom/pan/rotate;
- camera focus;
- selected-node highlighting;
- side inspector;
- filters;
- graph controls;
- realtime event activity;
- graph statistics.

Use the reference for interaction ideas, not for copying branding or unrelated agent semantics.

CrimeKit must remain visually:
- forensic;
- enterprise;
- serious;
- dark-first;
- information-dense;
- precise;
- restrained.

Avoid:
- cyberpunk aesthetics;
- excessive neon;
- excessive gradients;
- glassmorphism;
- giant decorative cards;
- meaningless rainbow coloring;
- unnecessary animation;
- consumer-game styling.

Preserve CrimeKit branding. Do not copy Neo4j logos or trademarks.

---

# 6. TARGET KNOWLEDGE GRAPH WORKSPACE

Conceptual screen:

```text
+--------------------------------------------------------------------+
| CrimeKit | Global Search | Case | Alerts | User                   |
+--------------------------------------------------------------------+
| Filters / Entities      3D KNOWLEDGE GRAPH             Inspector   |
|                                                                    |
| Person                  [3D graph canvas]             Selected      |
| Device                                                    Entity   |
| IP                      nodes                         Properties   |
| Location                relationships                Relations    |
| Evidence                paths                         Evidence     |
| Account                 clusters                      Timeline     |
| ...                     live updates                  Provenance   |
|                                                                    |
|                  zoom / focus / reset / expand                     |
+--------------------------------------------------------------------+
| Entities | Relationships | High Priority | Communities | Live     |
+--------------------------------------------------------------------+
```

The graph is the dominant workspace, but precise data access must remain available through inspector/table modes.

---

# 7. CRIMEKIT GRAPH ONTOLOGY

Start with a controlled ontology. Initial node types:

```text
Case
Investigation
Person
Device
Phone
Email
Account
IPAddress
Location
Vehicle
Evidence
Artifact
Image
Video
Document
Audio
TimelineEvent
Organization
Address
Transaction
Communication
```

Initial relationship examples:

```text
HAS_INVESTIGATION
HAS_EVIDENCE
CONTAINS
DERIVED_FROM
MENTIONS
REFERS_TO
USES
OWNS
CONTROLS
ASSOCIATED_WITH
CONNECTED_TO
COMMUNICATED_WITH
APPEARS_IN
CAPTURED_AT
LOCATED_AT
VISITED
OCCURRED_AT
INVOLVES
BELONGS_TO
RELATED_TO
SAME_AS
POSSIBLY_SAME_AS
OBSERVED_WITH
GENERATED
EXTRACTED_FROM
```

Document relationship semantics. Do not create relationships merely because two entities occur in the same source.

Every relationship must have a defensible extraction rule.

---

# 8. ENTITY IDENTITY

Every entity must have a stable domain identifier:

```text
case_id
investigation_id
person_id
device_id
evidence_id
artifact_id
event_id
```

Never use display names, mutable labels, array indexes, or UI-only random IDs as authoritative identity.

Neo4j IDs must map back to CrimeKit domain IDs.

---

# 9. NEO4J SCHEMA

Implement:
- uniqueness constraints;
- indexes;
- correct property types;
- timestamps;
- provenance;
- confidence;
- case references;
- source references.

Example:

```cypher
CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (p:Person)
REQUIRE p.person_id IS UNIQUE;
```

Create equivalent constraints for major domain entities.

Use indexes deliberately. Do not add redundant indexes without a measured reason.

---

# 10. GRAPH PROJECTION PIPELINE

Never allow arbitrary frontend graph writes.

Target:

```text
PostgreSQL
    |
    v
Outbox / Domain Event
    |
    v
Redis / Event Stream
    |
    v
Graph Projection Worker
    |
    v
Neo4j
```

The projection worker must support:
- idempotency;
- retry;
- dead-letter handling;
- deterministic processing;
- replay;
- reconciliation;
- updates;
- deletes;
- relationship correction;
- metrics;
- structured logs.

Graph projection must be repeatable.

---

# 11. IDEMPOTENCY AND CONSISTENCY

Do not create duplicate nodes or relationships on event replay.

Prefer deterministic identifiers and `MERGE`/safe update semantics where appropriate.

The system must recover from:
- worker crashes;
- application restart;
- Redis interruption;
- Neo4j transient failures;
- network failures;
- duplicate events;
- partial processing;
- out-of-order events.

Provide a reconciliation mechanism between PostgreSQL and Neo4j.

Example mismatch:

```text
PostgreSQL: P001 USES D001
Neo4j:      P001 USES D002
```

The system must detect and report the discrepancy.

---

# 12. FASTAPI GRAPH API

Follow existing CrimeKit API conventions. Conceptually support:

```text
GET  /cases/{case_id}/graph
GET  /cases/{case_id}/graph/stats
GET  /cases/{case_id}/graph/search
GET  /cases/{case_id}/graph/entity/{entity_id}
GET  /cases/{case_id}/graph/entity/{entity_id}/neighbors
POST /cases/{case_id}/graph/expand
GET  /cases/{case_id}/graph/path
GET  /cases/{case_id}/graph/communities
GET  /cases/{case_id}/graph/centrality
GET  /cases/{case_id}/graph/similarity
GET  /cases/{case_id}/graph/provenance
WS   /ws/cases/{case_id}/graph
```

Implement only endpoints actually needed by the product.

Requirements:
- authentication;
- authorization;
- case isolation;
- Pydantic/typed contracts;
- pagination/limits;
- hop limits;
- query timeouts;
- structured errors;
- observability;
- no direct browser-to-Neo4j connection.

---

# 13. GRAPH RESPONSE CONTRACT

Return only data needed by the UI.

Conceptual response:

```json
{
  "nodes": [
    {
      "id": "P001",
      "type": "Person",
      "label": "John Smith",
      "properties": {},
      "risk": 0.91
    }
  ],
  "edges": [
    {
      "id": "REL-001",
      "source": "P001",
      "target": "D001",
      "type": "USES",
      "confidence": 0.94
    }
  ],
  "meta": {
    "case_id": "CASE-001",
    "node_count": 1,
    "edge_count": 1,
    "generated_at": "..."
  }
}
```

Use stable response schemas. Do not expose raw Neo4j objects.

---

# 14. 3D RENDERING ENGINE

Build a robust React-compatible Three.js-based 3D graph engine. Before adding a package, inspect existing dependencies and use a mature compatible graph library when appropriate.

Required capabilities:
- 3D nodes;
- relationship lines;
- directional edges where useful;
- semantic node shapes;
- labels;
- force-directed layout;
- orbit controls;
- zoom;
- pan;
- rotate;
- hover;
- click;
- drag;
- focus;
- reset;
- minimap;
- path highlighting;
- progressive expansion;
- cluster highlighting;
- realtime insertion.

The graph must feel like an enterprise forensic investigation system, not a game.

---

# 15. NODE VISUAL SEMANTICS

Use semantic visual categories. Example palette:

```text
Person       -> blue/cyan family
Device       -> violet/purple family
IP Address   -> pink/red family
Location     -> green family
Account      -> orange family
Evidence     -> amber/yellow family
Case         -> cyan/blue
Timeline     -> neutral/teal
```

Do not rely on color alone. Also use:
- geometry;
- iconography;
- labels;
- outlines;
- size;
- inspector metadata.

Support accessibility and reduced motion.

---

# 16. RISK LANGUAGE

Never visually equate a risk score with guilt.

Use:
- Risk Score;
- Anomaly Score;
- Investigation Priority;
- Confidence.

Avoid unsupported labels such as:
- Guilty;
- Criminal;
- Confirmed Offender.

Risk indicators must be explainable and linked to supporting data.

---

# 17. 3D INTERACTIONS

Implement:

### Hover
Show:
- entity name;
- entity type;
- priority/risk;
- connection count.

### Click
- select node;
- open inspector;
- highlight connected relationships;
- dim unrelated graph elements.

### Double click
- expand neighbors;
- request server-side graph data;
- animate only the new neighborhood.

### Drag
Allow temporary manual positioning without destroying investigation state.

### Focus
Smoothly move the camera to selected entity.

### Reset
Restore a useful case-level view.

### Path mode
Select Entity A and Entity B -> Find Path -> highlight returned path.

---

# 18. PROGRESSIVE LOADING

Never automatically render the whole database.

Initial:
```text
Case + relevant entities + direct relationships
```

Expansion:
```text
1-hop -> 2-hop -> additional bounded hops
```

Enforce:
- maximum hops;
- maximum nodes;
- maximum edges;
- server-side filters;
- request cancellation;
- loading states;
- partial results;
- empty states;
- clear errors.

---

# 19. GRAPH LEVEL OF DETAIL

Use LOD:

```text
Zoomed out:
clusters + major entities

Medium:
entities + major relationships

Zoomed in:
labels + relationship metadata
```

Do not render thousands of labels at once.

Avoid excessive text sprites.

---

# 20. ENTITY INSPECTOR

Right-side inspector should include:

```text
ENTITY
--------------------------------
John Smith
Person
P001

Risk Score
0.91

Properties
Relationships
Evidence
Timeline
Provenance
Analytics
```

When a node is selected, synchronize:
- graph selection;
- inspector;
- table selection;
- URL/deep-link state where appropriate.

---

# 21. RELATIONSHIP INSPECTOR

When an edge is selected, show:

```text
RELATIONSHIP
--------------------------------
John Smith
      |
     USES
      |
Laptop-ACER

Confidence: 0.94
Evidence: EVD-102
Artifact: ART-889
Processing Run: RUN-42
Extraction Method: Entity Resolution
Observed: ...
Model Version: ...
```

Actions:
- open evidence;
- open artifact;
- open processing run;
- view provenance.

---

# 22. SEARCH

Support search by:
- stable ID;
- exact property;
- text;
- fuzzy matching where safe;
- entity type;
- date;
- relationship;
- case.

Workflow:

```text
Search
  ↓
Select entity
  ↓
Camera focus
  ↓
Graph expansion
  ↓
Inspector
```

Do not fetch the whole database to implement search.

---

# 23. FILTERS

Support as appropriate:

```text
Entity Type
Relationship Type
Risk / Priority
Date Range
Evidence Source
Processing Run
Confidence
Location
Investigation
```

Use server-side filtering for large data sets.

---

# 24. TIMELINE INTEGRATION

Knowledge Graph must integrate with the existing CrimeKit Timeline.

Selecting a TimelineEvent should support:
```text
View in Timeline
```

Selecting a time range should optionally highlight/filter graph activity during that interval.

Temporal graph state should remain explainable and reproducible.

---

# 25. EVIDENCE INTEGRATION

Every evidence-derived entity/relationship must provide a route back to source.

Example:

```text
Person
  |
  | MENTIONS
  v
Artifact
  |
  | DERIVED_FROM
  v
Evidence E-102
```

Investigator flow:

```text
Graph
 -> Relationship
 -> Artifact
 -> Evidence
 -> Original source
```

This is a core forensic capability.

---

# 26. GRAPH DATA SCIENCE

Integrate Neo4j Graph Data Science only after the base graph is reliable.

Initial capabilities:
- Shortest Path;
- BFS;
- PageRank;
- Betweenness Centrality;
- Degree Centrality;
- Community Detection;
- Node Similarity;
- KNN where justified.

Use cases:
- identify highly connected entities;
- identify bridge-like entities;
- detect communities;
- find similar entities;
- find paths;
- explore bounded neighborhoods.

Every analytical result should carry:
- algorithm;
- parameters;
- timestamp;
- graph scope;
- case_id;
- interpretation/limitations.

Never represent graph analytics as proof of guilt.

---

# 27. GRAPH ANALYTICS UI

Provide:

```text
Analysis
Related Entities
Shortest Paths
Communities
Centrality
Risk Analysis
```

Example summary:

```text
Total Entities       24
Total Relationships  38
High Priority         5
Communities            3
```

Clicking an analysis should visually highlight the relevant graph subset.

---

# 28. REALTIME GRAPH

Target:

```text
New forensic event
      |
      v
Redis/Event Stream
      |
      v
Processing
      |
      v
Graph Projection
      |
      v
Neo4j
      |
      v
Realtime event
      |
      v
WebSocket
      |
      v
3D graph
```

Realtime updates must:
- avoid page reload;
- preserve camera position;
- preserve current selection;
- avoid duplicate nodes/edges;
- animate only new information;
- show connection state;
- recover after reconnect.

---

# 29. REALTIME EVENT CONTRACT

Conceptual event:

```json
{
  "event": "GRAPH_RELATIONSHIP_CREATED",
  "case_id": "CASE-001",
  "relationship": {
    "id": "REL-100",
    "source": "P001",
    "target": "D001",
    "type": "USES"
  },
  "timestamp": "...",
  "provenance": {
    "evidence_id": "EVD-100"
  }
}
```

Support event types as required:

```text
GRAPH_NODE_CREATED
GRAPH_NODE_UPDATED
GRAPH_NODE_REMOVED
GRAPH_RELATIONSHIP_CREATED
GRAPH_RELATIONSHIP_UPDATED
GRAPH_RELATIONSHIP_REMOVED
GRAPH_ANALYSIS_UPDATED
```

Follow existing CrimeKit event conventions if they already exist.

---

# 30. WEBSOCKET SECURITY

Implement:
- authenticated connections;
- case authorization;
- reconnect;
- heartbeat;
- exponential backoff;
- duplicate prevention;
- stale event handling;
- cleanup on unmount;
- connection status.

Never deliver unauthorized case events.

---

# 31. AI INTEGRATION

AI must not replace graph facts.

Correct:

```text
Graph facts
 + Evidence
 + Timeline
 + Graph analytics
      |
      v
AI reasoning
      |
      v
Evidence-grounded explanation
```

Incorrect:

```text
LLM -> invent relationship -> write as fact
```

AI output must distinguish:
- observed fact;
- derived relationship;
- graph analytical result;
- model prediction;
- AI interpretation.

Where possible, identify supporting evidence/artifacts and provenance.

---

# 32. GRAPHRAG DIRECTION

Future GraphRAG can use:

```text
Investigator Question
        |
        v
Intent / Query Planning
        |
        +---- Neo4j
        +---- Vector Search
        +---- Evidence Search
        +---- Timeline
        |
        v
Evidence Context
        |
        v
LLM
        |
        v
Verified Answer
```

Do not build speculative GraphRAG complexity before the base graph is correct.

---

# 33. PERFORMANCE ARCHITECTURE

Design for persisted graph sizes such as:

```text
100 nodes
1,000 nodes
10,000 nodes
100,000+ graph records
```

This does NOT mean rendering all of them simultaneously.

Use:
- bounded Cypher;
- pagination;
- progressive expansion;
- LOD;
- node/edge culling;
- lazy labels;
- event batching;
- efficient indexes;
- connection pooling;
- query timeouts;
- request cancellation;
- render throttling;
- stable layout.

---

# 34. LAYOUT STABILITY

The graph must not constantly jump.

Use:
- initial force simulation;
- stabilization;
- incremental layout;
- local insertion;
- preservation of manually positioned nodes where practical.

Realtime events should not re-layout the entire case unnecessarily.

---

# 35. FAILURE UX

Every layer needs clear failure states.

Examples:

Neo4j unavailable:
```text
Knowledge Graph temporarily unavailable.
Retry.
```

Graph query timeout:
```text
Graph request timed out.
Narrow filters or expand a smaller neighborhood.
```

Graph too large:
```text
This graph is too large to render at once.
Expand a smaller neighborhood.
```

WebSocket disconnected:
```text
Realtime disconnected. Reconnecting...
```

Never leave a blank screen with no explanation.

---

# 36. OBSERVABILITY

Backend metrics should include:
- graph query latency;
- Neo4j connection health;
- projection lag;
- event processing latency;
- projection failures;
- retry count;
- dead-letter count;
- graph API errors;
- WebSocket connections.

Frontend metrics should include where feasible:
- graph load time;
- node/edge count;
- rendering responsiveness;
- expansion latency;
- realtime state;
- runtime errors;
- memory/performance diagnostics.

Do not log sensitive evidence unnecessarily.

---

# 37. CACHING

Cache only where safe.

Potential candidates:
- ontology metadata;
- graph type metadata;
- aggregate statistics;
- authorized repeated queries.

Case-scoped cache keys must include authorization scope/case scope as appropriate.

Never allow Case A data to leak through a shared cache to Case B.

---

# 38. CYPHER SAFETY

Cypher must:
- use parameters;
- have bounded traversal;
- avoid accidental Cartesian products;
- use indexes/constraints appropriately;
- return only needed properties;
- have sensible timeouts/limits.

Never expose an unrestricted endpoint equivalent to:

```cypher
MATCH (n)
RETURN n
```

Do not construct queries from raw user strings.

---

# 39. FRONTEND STATE ARCHITECTURE

Maintain distinct state for:

```text
case
Graph data
selected node
selected relationship
camera
filters
expanded nodes
collapsed nodes
search
loading
error
realtime status
analytics
inspector
```

Do not rebuild the entire Three.js scene because a side panel changed.

Do not reset camera state on every network update.

---

# 40. GRAPH/TABLE DUAL MODE

Provide:

```text
Graph | Table
```

Graph = spatial investigation.

Table = precise inspection.

Selections should synchronize between modes.

3D must never be the only access path to information.

---

# 41. CASE WORKSPACE INTEGRATION

Knowledge Graph is a first-class case workspace:

```text
Cases
  -> Case Workspace
       -> Overview
       -> Evidence
       -> Search
       -> Knowledge Graph
       -> Timeline
       -> Processing
       -> AI Workspace
       -> Reports
```

Do not build an isolated graph application disconnected from the case model.

---

# 42. DEEP LINKING

Support a case route such as:

```text
/cases/CASE-001/knowledge-graph
```

Where safe, selected entities may be represented in URL/state:

```text
/cases/CASE-001/knowledge-graph?entity=P001
```

Authorization must still be enforced server-side.

---

# 43. AUDIT LOGGING

Audit meaningful investigation actions:

```text
GRAPH_VIEWED
GRAPH_ENTITY_VIEWED
GRAPH_EXPANDED
GRAPH_PATH_REQUESTED
GRAPH_ANALYSIS_RUN
GRAPH_FILTER_CHANGED
EVIDENCE_OPENED_FROM_GRAPH
PROVENANCE_VIEWED
```

Do not audit every mouse movement or animation frame.

---

# 44. RETENTION / DELETION

Respect CrimeKit's existing:
- evidence retention;
- legal hold;
- case deletion;
- audit requirements.

Define what happens to graph projections when authoritative records are updated, archived, or deleted.

Do not silently retain sensitive graph information beyond policy.

---

# 45. MIGRATION STRATEGY

If existing graph data exists:

1. inventory;
2. validate schema;
3. map legacy entities;
4. preserve identifiers;
5. migrate safely;
6. validate counts;
7. validate relationships;
8. reconcile mismatches;
9. switch reads only after validation.

Never perform destructive migration without a recovery path.

---

# 46. TEST STRATEGY

## Unit
- graph mapping;
- relationship mapping;
- entity mapping;
- Cypher repository;
- authorization;
- serializers.

## Integration

```text
PostgreSQL -> event
Event -> projection
Projection -> Neo4j
Neo4j -> API
API -> frontend
```

## End-to-end

```text
Create case
 -> create evidence
 -> process evidence
 -> extract entity
 -> create relationship
 -> project to Neo4j
 -> open graph
 -> select entity
 -> expand
 -> inspect provenance
 -> open source evidence
```

## Realtime
- event arrival;
- reconnect;
- duplicate events;
- unauthorized events;
- out-of-order events.

## Performance
- graph expansion;
- path search;
- GDS operations;
- rendering;
- realtime load.

---

# 47. SECURITY TESTS

Test:
- unauthorized case;
- unauthorized entity;
- malicious IDs;
- Cypher injection attempts;
- WebSocket authorization;
- cross-case cache leakage;
- privilege escalation;
- expired credentials;
- revoked access;
- sensitive log leakage.

---

# 48. GRAPH CONSISTENCY TESTS

Validate:

```text
PostgreSQL entity count
        vs
Neo4j projected entity count
```

Also validate:
- relationship counts;
- provenance references;
- deleted entities;
- updated relationships;
- duplicate prevention;
- event replay behavior.

Produce reconciliation output where practical.

---

# 49. 3D PERFORMANCE TESTS

Measure:
- initial graph load;
- time to interactive;
- camera responsiveness;
- expansion latency;
- path-query latency;
- WebSocket update impact;
- memory usage;
- render responsiveness.

Test representative developer and ordinary machines, not only a high-end workstation.

---

# 50. DEPENDENCY RULE

Before adding a package:
1. inspect existing dependencies;
2. determine whether an equivalent already exists;
3. verify compatibility;
4. add only necessary packages;
5. document the reason.

Do not introduce multiple competing graph engines.

---

# 51. IMPLEMENTATION PHASES

Implement in controlled phases:

```text
01 Repository Audit
02 Graph Ontology
03 Neo4j Schema
04 Graph Projection
05 Graph API
06 3D Engine
07 Inspector
08 Search/Filters
09 GDS Analytics
10 Realtime
11 Security/Provenance
12 Performance
13 Testing
14 Production Hardening
```

For every phase:

```text
Inspect
 -> Plan
 -> Implement
 -> Run tests
 -> Inspect output
 -> Fix
 -> Validate
 -> Continue
```

Do not generate a giant unvalidated code dump.

---

# 52. CONCEPTUAL CODE ORGANIZATION

Adapt to the existing repository rather than blindly creating this exact structure:

```text
frontend/
  knowledge-graph/
    components/
      KnowledgeGraph3D
      GraphCanvas
      GraphControls
      GraphFilters
      EntityInspector
      RelationshipInspector
      GraphLegend
      GraphMinimap
      GraphTable
      LiveGraphEvents
    hooks/
      useGraph
      useGraphSelection
      useGraphRealtime
      useGraphCamera
    services/
      graphApi
    types/
      graph

backend/
  graph/
    router
    service
    repository
    neo4j_client
    queries
    schemas
    projection
    events
    gds
```

Follow current CrimeKit conventions if they differ.

---

# 53. DEFINITION OF DONE

The feature is not complete because the graph looks attractive.

It is complete only when:

- Neo4j connection works;
- schema works;
- constraints/indexes work;
- graph projection works;
- idempotency works;
- reconciliation works;
- graph API works;
- authentication works;
- authorization works;
- case isolation works;
- provenance works;
- 3D rendering works;
- selection works;
- expansion works;
- search works;
- filters work;
- paths work;
- GDS analytics work;
- realtime updates work;
- table mode works;
- evidence navigation works;
- timeline integration works;
- error states work;
- tests pass;
- performance is measured;
- no critical runtime errors remain.

---

# 54. ANTI-PATTERNS — NEVER DO THESE

```text
❌ Browser -> Neo4j directly
❌ Neo4j becomes source of truth
❌ Unbounded MATCH traversal
❌ Render entire database
❌ Random graph relationships
❌ Relationship without provenance
❌ Frontend-only authorization
❌ Unparameterized Cypher
❌ Reset camera on every update
❌ Page reload for realtime updates
❌ Duplicate event processing
❌ LLM invents graph facts
❌ Risk score presented as guilt
❌ Graph analytics presented as proof
❌ Copy Neo4j branding
❌ Copy unrelated AI-agent nodes
❌ Unnecessary dependencies
❌ Rewrite working CrimeKit modules
❌ Ignore existing design system
❌ Ignore existing authentication
❌ Hide errors
❌ Hardcode credentials
```

---

# 55. EXPECTED INVESTIGATOR WORKFLOW

```text
Open Case
   ↓
Open Knowledge Graph
   ↓
See initial 3D case graph
   ↓
Search "John Smith"
   ↓
Camera focuses John
   ↓
Inspector opens
   ↓
Click Expand
   ↓
Device / IP / Account / Evidence appear
   ↓
Select Device
   ↓
Inspect relationships
   ↓
Select IP
   ↓
Find Path -> Person B
   ↓
Path highlighted in 3D
   ↓
Select relationship
   ↓
View provenance
   ↓
Open source evidence
   ↓
Review timeline
   ↓
Run graph analysis
   ↓
Review result and limitations
   ↓
Human investigator makes decision
```

---

# 56. FINAL TARGET ARCHITECTURE

```text
                         CRIMEKIT
                            |
                    Next.js / React
                            |
                   Knowledge Graph UI
                            |
                   3D Three.js Engine
                            |
                         FastAPI
                            |
             +--------------+--------------+
             |                             |
        PostgreSQL                      Redis
        SOURCE OF TRUTH              EVENT PIPELINE
             |                             |
             +-------------+---------------+
                           |
                    Graph Projection
                           |
                           v
                     NEO4J AURA
                           |
             +-------------+-------------+
             |             |             |
           Cypher         GDS       Vector/Search
             |             |             |
             +-------------+-------------+
                           |
                       Graph API
                           |
                     3D Experience
                           |
              +------------+------------+
              |            |            |
          Inspector     Timeline     Evidence
              |            |            |
              +------------+------------+
                           |
                     AI Investigator
                           |
                     Human Review
```

---

# 57. FINAL COMMAND TO THE CODING AGENT

Do not merely create a visually impressive 3D mockup.

Build the complete feature as an integrated CrimeKit subsystem.

Before changing code, inspect the actual repository.

Preserve working functionality.

Use existing CrimeKit architecture wherever possible.

Do not invent implementation details when repository evidence is available.

Do not claim a component is implemented until it has actually been implemented and validated.

When a requirement conflicts with existing CrimeKit behavior, identify the conflict and choose the smallest safe architectural change.

When uncertain, inspect the repository rather than guessing.

When adding dependencies, verify compatibility.

When graph queries can become expensive, bound them.

When relationships are created, preserve provenance.

When realtime data arrives, preserve UI state.

When security is involved, enforce it server-side.

When AI is involved, ground it in evidence and graph facts.

When analytics are involved, label them as analytical outputs and communicate limitations.

When performance is involved, measure it.

When an error occurs, diagnose and fix the root cause rather than hiding it.

The final result must feel like a **professional digital-forensics investigation product with a world-class 3D graph interface**, architecturally consistent with CrimeKit, Neo4j Aura, PostgreSQL, Redis, FastAPI, and the existing CrimeKit application.

The objective is NOT:

> "Make a cool 3D graph."

The objective IS:

> **"Build a secure, explainable, provenance-preserving, real-time, production-grade 3D forensic knowledge graph that investigators can trust, operate, audit, test, and scale."**

---

# 58. REQUIRED AGENT OUTPUT BEFORE IMPLEMENTATION

Before modifying code, return:

1. Repository architecture summary.
2. Existing Knowledge Graph implementation summary.
3. Existing Neo4j integration summary.
4. Existing realtime/event architecture summary.
5. Existing authentication/authorization summary.
6. Existing frontend graph dependencies.
7. Files that can be reused.
8. Files that must be changed.
9. New dependencies, if any, and why.
10. Final implementation plan with phases.
11. Risks and compatibility concerns.
12. Test strategy.

Then implement incrementally.

After each major phase, report:

```text
Implemented
Validated
Tests
Files changed
Risks
Next phase
```

Never silently skip a required phase.
