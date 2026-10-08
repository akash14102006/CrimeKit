# CRIMEKIT — NEO4J-STYLE VISUAL UI

MASTER IMPLEMENTATION PROMPT
Prompt #7 — Enterprise Graph Visual System + 3D Forensic Knowledge Workspace

ROLE:
Act as a world-class Principal Product Designer, Design Systems Architect, Neo4j Graph UX Architect, 3D Visualization Architect, Digital Forensics UX Architect, Frontend Platform Architect, WebGL/Three.js Engineer, Accessibility Engineer, Security UX Architect, AI/GraphRAG UX Architect, and Enterprise QA Lead.

MISSION:
Transform the existing CrimeKit Graph experience into a premium, production-grade, Neo4j-inspired forensic graph workspace with a genuinely interactive 3D knowledge graph.

The goal is NOT to make a decorative 3D graph.

The goal is to create a forensic knowledge operating system in which:
Evidence → Processing → Artifacts → Entities → Relationships → Timeline → Provenance → Contradictions → Investigation reasoning

can be explored visually, spatially, temporally and explainably.

The visual direction must strongly follow the user's supplied Neo4j-style reference screens and the interaction language of Neo4j Aura/Bloom, while remaining an original CrimeKit product and never copying Neo4j trademarks, logos, proprietary source code or protected assets.

The implementation must be:
scalable • explainable • ethical • secure • accessible • performant • responsive • realtime-capable • production-ready.

# 1. DESIGN REFERENCE PRINCIPLE

Use the user's reference screens as the primary visual reference for:
- layout density
- graph workspace composition
- dark enterprise visual language
- sidebar/header relationships
- search placement
- graph canvas behavior
- inspector/panel behavior
- legend behavior
- controls
- information hierarchy
- interaction patterns

Also use official Neo4j Bloom/Aura documentation as a product-behavior reference.

Neo4j describes Bloom as a visual graph exploration environment with a main Scene, search, toolbars, map, legend and inspection interactions. Aura/Bloom also supports perspectives, graph scene interaction, card lists and contextual inspection. citeturn0search1turn0search0turn0search6

Do NOT blindly reproduce the Neo4j interface.

Create:
"Neo4j-style graph ergonomics + CrimeKit forensic intelligence + original 3D interaction model."

# 2. CORE VISUAL PHILOSOPHY

The UI must feel like:

```text
Neo4j Aura
     +
Neo4j Bloom
     +
Mission-control workstation
     +
Digital-forensics evidence laboratory
     +
3D scientific visualization
```

NOT:

```text
gaming UI
crypto dashboard
cyberpunk dashboard
generic SaaS dashboard
ChatGPT clone
glassmorphism landing page
```

Visual personality:
- dark
- precise
- dense
- calm
- technical
- premium
- analytical
- evidence-first
- graph-first
- minimal decoration

# 3. ABSOLUTE PRODUCT PRINCIPLE

The 3D visualization must communicate meaning.

Every visible:
- node
- edge
- label
- glow
- size
- opacity
- animation
- cluster
- highlight
- trajectory
- pulse

must have a documented semantic reason.

Never use animation merely because it looks impressive.

Never use:
- random node movement
- fake realtime pulses
- fake evidence links
- fake confidence
- decorative relationships
- random colors
- arbitrary centrality sizing
- misleading visual emphasis

# 4. SCREEN ARCHITECTURE

Build the main CrimeKit Graph screen as a full-screen investigative workstation.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ CrimeKit | Case / Investigation | Search | Graph State | User | Status      │
├──────────┬─────────────────────────────────────────────────────────┬─────────┤
│          │                                                         │         │
│ LEFT     │                 3D GRAPH SCENE                          │ RIGHT   │
│ NAV      │                                                         │ INSPECT │
│          │             ●────────────●                              │ OR      │
│ Cases    │          ╱       ╲         ╲                            │         │
│ Evidence │       ●──────●──────●──────●                           │ Entity  │
│ Timeline │          ╲       ╱                                      │ Details │
│ Graph    │             ●                                           │         │
│ AI       │                                                         │ Evidence│
│ Reports  │       floating graph controls                           │ Proven. │
│          │                                                         │ Timeline│
│          │                                                         │         │
├──────────┴─────────────────────────────────────────────────────────┴─────────┤
│ Timeline / Replay / Graph Events / Query / AI Command Bar                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

The exact existing CrimeKit shell must be inspected before changing it.
Reuse the current design system and navigation where practical.

# 5. GLOBAL VISUAL LANGUAGE

Use a restrained dark enterprise palette inspired by graph/database tooling.

Do not hard-code arbitrary colors everywhere.

Create semantic tokens:

```text
--ck-bg
--ck-bg-elevated
--ck-bg-panel
--ck-bg-canvas
--ck-border
--ck-border-strong
--ck-text
--ck-text-muted
--ck-text-disabled
--ck-accent
--ck-accent-hover
--ck-success
--ck-warning
--ck-danger
--ck-info
--ck-selection
--ck-focus
```

The exact token values must be derived from:
1. the existing CrimeKit theme
2. the supplied reference screens
3. accessibility contrast requirements

Use cyan/aqua as a restrained graph-system accent where appropriate.

Do NOT create:
- neon rainbow graphs
- purple AI gradients
- excessive glow
- giant shadows
- glassmorphism
- excessive rounded cards

# 6. TYPOGRAPHY

Typography must feel like a serious developer/forensics product.

Use the actual existing CrimeKit typography if already established.

If replacing typography is necessary:
- use a highly legible UI sans-serif
- use a monospaced family only for IDs, hashes, timestamps, technical metadata and code
- use clear weight hierarchy
- avoid oversized marketing typography

Hierarchy:
```text
Case title
Section title
Entity title
Metadata
Technical ID
Timestamp
Status
```

Graph labels must remain readable at useful zoom levels.

# 7. NEO4J-STYLE ERGONOMICS

Recreate the following interaction principles rather than copying implementation:

- persistent graph scene
- search-first exploration
- perspective/lens concept
- compact toolbars
- legend
- minimap
- card/inspector navigation
- select/expand/dismiss interactions
- contextual actions
- graph filtering
- timeline slicing
- graph export
- saved views

Neo4j Bloom documentation explicitly describes a Scene, Settings header, search bar, toolbars, map and legend panel; it also describes card lists and inspectors for navigating graph details. citeturn0search1turn0search14

# 8. CRIMEKIT DIFFERENTIATION

CrimeKit must go beyond a normal graph viewer.

Add forensic-first concepts:

1. Provenance Thread
2. Evidence Impact
3. Processing Impact
4. Temporal Graph Time Machine
5. Investigation Replay
6. Contradiction Layer
7. Knowledge Gap Layer
8. Hypothesis Sandbox
9. Evidence Support Stack
10. Uncertainty Stack
11. Graph-to-Evidence navigation
12. Evidence-to-Graph navigation
13. Live Forensic Pulse
14. Investigation Story
15. Review Boundary
16. Source Diversity View
17. Relationship Lifecycle
18. Graph Evolution View

These concepts must be implemented through real data contracts, not decorative UI.

# 9. 3D GRAPH CORE

Use a production-grade WebGL-capable renderer such as the existing CrimeKit renderer or Three.js if that is the actual repository choice.

Do not introduce another rendering framework without repository justification.

The 3D graph must support:
- orbit
- pan
- zoom
- node selection
- multi-selection
- edge selection
- focus
- isolate
- expand
- collapse
- search highlight
- semantic filtering
- temporal filtering
- provenance mode
- replay mode
- 2D fallback
- reduced-motion mode
- high-density LOD

# 10. 3D SCENE COORDINATE MODEL

The graph scene is a spatial representation of relationships, not a physical simulation of reality.

Position must be treated as visualization state.

Never imply:
- geographic distance
- social distance
- legal importance

unless the selected lens explicitly defines such semantics.

Persist user layout only as visualization state.

# 11. NODE VISUAL ONTOLOGY

Every node needs:

```text
id
type
label
status
semantic category
icon/shape
visual priority
evidence count
relationship count
provenance availability
review state
temporal availability
```

Suggested semantic families:

```text
CASE
INVESTIGATION
PERSON
DEVICE
ACCOUNT
PHONE
EMAIL
IP_ADDRESS
LOCATION
VEHICLE
FILE
MEDIA
DOCUMENT
IMAGE
VIDEO
AUDIO
ARTIFACT
OBSERVATION
TIMELINE_EVENT
PROCESSING_RUN
EVIDENCE
HYPOTHESIS
CONTRADICTION
REVIEW
```

Use the actual CrimeKit ontology rather than inventing duplicate entities.

# 12. NODE SHAPES

Node geometry must encode semantic category consistently.

Example direction:

```text
Person        → sphere
Device        → rounded cube
Account       → compact cylinder
Location      → ring/sphere hybrid
Evidence      → document/card-like geometry
Media         → frame/slab geometry
Timeline      → temporal marker
Processing    → pipeline capsule
Contradiction → split/dual-state marker
Hypothesis    → dashed/ghost geometry
Review        → verification ring
```

These are proposed visual mappings only.
Verify against the existing ontology before implementation.

# 13. NODE SIZE

Node size must NEVER represent guilt.

Possible legitimate size semantics:
- selected/focused state
- bounded degree
- evidence count
- UI priority

If degree/evidence count changes size:
- disclose the rule
- cap the range
- avoid huge visual distortion

# 14. EDGE VISUAL ONTOLOGY

Edges must have:
- stable ID
- relationship type
- direction
- state
- provenance availability
- confidence semantics where applicable
- temporal availability

Visual dimensions:
- line style
- thickness
- opacity
- direction marker
- animation
- color

must map to documented semantics.

# 15. EDGE STATES

Support explicit states:

```text
OBSERVED
DERIVED
CANDIDATE
REVIEWED
CONFIRMED_BY_POLICY
DISPUTED
REJECTED
HYPOTHESIS
RETIRED
```

Do not visually collapse these into one generic relationship.

# 16. ETHICAL VISUAL SEMANTICS

Absolute rule:

```text
Graph centrality ≠ guilt
Graph proximity ≠ causation
Similarity ≠ identity
Anomaly ≠ criminality
Connection ≠ intent
Location association ≠ person presence
```

The UI must avoid visually implying conclusions that the evidence does not establish.

Never use a "danger red" visual merely because a person has many connections.

# 17. PROVENANCE THREAD

When an investigator selects an important relationship:

```text
Relationship
     ↓
Observation / Assertion
     ↓
Artifact
     ↓
Processing Run
     ↓
Evidence
     ↓
Original Source
```

The UI should animate/highlight the actual chain only.

Do not fabricate a lineage path.

This is one of the core CrimeKit differentiators.

# 18. EVIDENCE IMPACT MODE

Selecting Evidence should produce a visually bounded impact mode:

```text
Evidence
 ├── Artifacts
 ├── Observations
 ├── Entities affected
 ├── Relationships affected
 ├── Timeline events affected
 ├── Contradictions
 └── Processing runs
```

Show:
- direct impact
- derived impact
- unresolved impact

with explicit labels.

# 19. PROCESSING IMPACT MODE

Selecting a forensic processing run:

```text
Processing Run
      ↓
Artifacts
      ↓
Extracted Entities
      ↓
Relationships
      ↓
Timeline Events
      ↓
Graph Changes
```

This implements CrimeKit's "SHOW THE WORK" principle visually.

# 20. TEMPORAL GRAPH TIME MACHINE

Create a bottom timeline control.

Modes:

```text
LIVE
CASE START
CUSTOM RANGE
CHECKPOINT
REPLAY
```

When the investigator changes time:
- request an actual temporal graph state
- update only permitted graph elements
- show current time range
- distinguish event time from ingestion/projection time
- never fake historical state

# 21. INVESTIGATION REPLAY

Replay actual knowledge emergence:

```text
00:00 Evidence uploaded
00:04 OCR completed
00:09 Entity extracted
00:12 Entity resolved
00:15 Relationship proposed
00:18 Contradiction detected
00:21 Investigator reviewed
```

Every step must correspond to real system events or stored workflow records.

# 22. GRAPH EVOLUTION VISUALIZATION

Show actual graph changes:

```text
NEW
CHANGED
DISPUTED
RETIRED
REVIEWED
```

Use restrained motion:
- fade in
- edge draw
- focus transition
- timeline marker

No explosive or game-like animation.

# 23. CONTRADICTION LAYER

A contradiction should be visually distinct without automatically making one side "wrong".

Inspector:

```text
CONTRADICTION
────────────────
Observation A
Source A
Timestamp A

vs

Observation B
Source B
Timestamp B

Status:
UNRESOLVED / REVIEWED / RESOLVED
```

The graph must preserve both observations.

# 24. KNOWLEDGE GAP LAYER

Show what the investigation does NOT know.

Examples:
- unresolved identity
- missing timestamp
- unsupported ownership
- conflicting location
- insufficient source support

Visual:
- muted dashed node
- question marker
- "UNKNOWN" label
- explicit explanation

Never fill a gap with an invented relationship.

# 25. HYPOTHESIS SANDBOX

Provide a clearly separated hypothetical layer:

```text
CANONICAL GRAPH
      |
      +------ HYPOTHESIS SANDBOX
```

Hypothesis nodes/edges:
- dashed
- translucent
- explicit HYPOTHESIS badge
- excluded from canonical reports by default
- excluded from AI factual context unless explicitly requested

# 26. INVESTIGATION STORY MODE

A high-level mode can construct a visual sequence:

```text
Evidence
 ↓
Discovery
 ↓
Relationship
 ↓
Timeline
 ↓
Contradiction
 ↓
Review
```

This is a visual narrative of actual system records.

It is not an AI-generated fictional story.

# 27. SOURCE DIVERSITY VIEW

When inspecting a relationship, show supporting source categories:

```text
CCTV
DOCUMENT
DEVICE LOG
COMMUNICATION
METADATA
FORENSIC ARTIFACT
HUMAN REVIEW
```

Source diversity is contextual information, not automatic proof.

# 28. UNCERTAINTY STACK

Do not reduce uncertainty to one number.

Where available, expose:

```text
Identity
Source quality
Model confidence
Temporal confidence
Review status
Contradiction state
```

Example:

```text
IDENTITY       Candidate
SOURCE         Strong
TEMPORAL       Approximate
MODEL          0.91
REVIEW         Pending
CONTRADICTION  Present
```

Only show fields actually supported by the backend.

# 29. RELATIONSHIP INSPECTOR

Right-side inspector should answer:

1. What is this relationship?
2. Why does it exist?
3. When was it observed?
4. What evidence supports it?
5. Which processing run created it?
6. Which model/rule contributed?
7. Is it reviewed?
8. Is it disputed?
9. What contradicts it?
10. What can I inspect next?

# 30. ENTITY INSPECTOR

Inspector structure:

```text
ENTITY HEADER
Type / ID / Status

SUMMARY
Key authorized metadata

RELATIONSHIPS
Bounded list

EVIDENCE
Supporting evidence

TIMELINE
Relevant events

PROVENANCE
Origin and processing

UNCERTAINTY
Known uncertainty

CONTRADICTIONS
Conflicting observations

ACTIONS
Expand / Focus / Compare / Timeline / Evidence
```

# 31. CARD LIST

Implement a compact card list inspired by graph exploration tools.

Card:
- icon
- type
- title
- ID
- small status
- relationship count
- evidence count

Cards must stay synchronized with graph selection.

Neo4j Bloom documentation describes card-list synchronization with graph selection and inspector navigation. citeturn0search14

# 32. LEGEND

Right/secondary legend should explain:
- node categories
- edge categories
- status states
- lens
- visual rules

Neo4j's Aura/Bloom documentation describes legend styling for categories and relationship types, including captions and icons. citeturn0search16

CrimeKit extension:
The legend must also explain forensic semantics:
- observed
- derived
- candidate
- disputed
- hypothesis
- reviewed

# 33. PERSPECTIVE / LENS SYSTEM

Create a CrimeKit equivalent of a graph Perspective.

Potential lenses:

```text
FORENSIC OVERVIEW
EVIDENCE
IDENTITY
DEVICE
COMMUNICATION
LOCATION
TIMELINE
PROVENANCE
CONTRADICTION
PROCESSING
INVESTIGATION
```

A lens controls:
- visible node types
- visible relationships
- labels
- inspector fields
- emphasis rules
- layout strategy

It must NOT change canonical graph truth.

# 34. SEARCH BAR

Search must be the primary entry point.

Support:
- entity search
- case-scoped search
- evidence search
- graph pattern search where supported
- natural-language query only if backed by safe structured translation

Example:

```text
Find devices connected to Person P001
```

The UI should translate this into a controlled Graph API operation.

Never send unrestricted user text directly to Neo4j as Cypher.

# 35. COMMAND BAR

Optional bottom command bar:

```text
Search graph…
Ask about this case…
Find path…
Show evidence…
Show contradictions…
Replay changes…
```

AI must remain grounded in authorized Graph API responses.

# 36. AI GRAPH ASSISTANT

The AI layer can answer:

- What connects these entities?
- What evidence supports this edge?
- What changed after this evidence?
- Which relationships are disputed?
- What information is missing?
- Which entities are connected through a bounded path?

AI must cite internal CrimeKit identifiers and evidence references where applicable.

Never let AI invent graph edges.

# 37. GRAPH-TO-EVIDENCE NAVIGATION

Interaction:

```text
Select edge
 ↓
Open provenance
 ↓
Click evidence
 ↓
Open evidence viewer
 ↓
Highlight originating artifact
```

This should feel like drilling through a graph into the underlying forensic source.

# 38. EVIDENCE-TO-GRAPH NAVIGATION

Interaction:

```text
Open Evidence
 ↓
Graph Impact
 ↓
3D graph centers on affected entities
 ↓
Affected edges highlighted
 ↓
Timeline changes shown
```

# 39. 3D CAMERA MODEL

Camera behavior:
- smooth orbit
- constrained zoom
- inertial pan
- focus selected
- fit selection
- fit neighborhood
- reset view
- saved camera state

Avoid uncontrolled camera flips.

Provide keyboard equivalents.

# 40. GRAPH LAYOUTS

Support multiple layout strategies:

```text
FORCE
RADIAL
HIERARCHICAL
TIMELINE
CLUSTER
PROVENANCE
EVIDENCE-CENTERED
```

The backend determines semantic grouping.
The frontend determines visual placement.

Layout selection is a visualization preference unless explicitly defined as an analytical view.

# 41. EVIDENCE-CENTERED LAYOUT

Selected evidence at center:

```text
             Entity
               |
Artifact — Evidence — Observation
               |
           Timeline
               |
         Processing Run
```

Useful for forensic review.

# 42. PROVENANCE LAYOUT

Selected relationship at center:

```text
Source Evidence
      ↓
Artifact
      ↓
Processing
      ↓
Observation
      ↓
Relationship
```

Use directional visual flow.

# 43. TIMELINE LAYOUT

Use time as an explicit visual axis only in Timeline lens.

Do not imply spatial geography when the axis is temporal.

# 44. 3D LOD

At distance:
- hide labels
- reduce geometry
- reduce edge detail
- cluster dense regions

Near selection:
- restore labels
- restore metadata
- restore provenance indicators

LOD must be deterministic and performant.

# 45. HIGH-DEGREE NODE STRATEGY

For high-degree nodes:

```text
Node
 ↓
Relationship groups
 ↓
Aggregate counts
 ↓
Expand selected group
 ↓
Progressive graph
```

Never render thousands of relationships immediately if the viewport cannot meaningfully display them.

# 46. CLUSTER REPRESENTATION

A cluster can be shown as:

```text
Cluster
47 entities
12 relationships
Expandable
```

But the cluster must correspond to a real grouping:
- graph analytics
- explicit category
- temporal group
- semantic lens

Never create arbitrary visual clusters.

# 47. MINIMAP

Provide a small graph minimap for large scenes.

It should show:
- graph bounds
- current camera
- selected region
- major clusters

Use it as navigation, not another data visualization.

# 48. TOOLBAR

Compact graph toolbar:

```text
Search
Select
Box Select
Lasso
Expand
Collapse
Focus
Fit
Filter
Lens
Layout
Timeline
Replay
Legend
Minimap
2D/3D
Fullscreen
```

Only show actions relevant to current permissions/state.

# 49. CONTEXT MENU

Node context:
- Inspect
- Expand
- Focus
- Isolate
- Evidence
- Timeline
- Provenance
- Compare
- Copy ID

Edge context:
- Inspect
- Provenance
- Evidence
- Timeline
- Compare
- Copy ID

Do not provide unauthorized write operations.

# 50. SELECTION MODEL

States:

```text
hover
selected
multi-selected
focused
dimmed
hidden
filtered
locked
```

Selection must be synchronized across:
- graph
- cards
- inspector
- timeline
- evidence panel

# 51. FOCUS MODE

When one entity is selected:
- brighten selected entity
- softly dim unrelated graph
- preserve context
- show direct neighbors
- show path if requested

Never hide all context automatically.

# 52. ISOLATE MODE

Explicitly isolate:
- selected entity
- selected relationship
- selected path
- selected evidence impact

Clearly label:
```text
ISOLATED VIEW
```

# 53. FILTER SYSTEM

Filters:
- node type
- relationship type
- evidence source
- status
- time range
- review state
- confidence availability
- provenance availability
- contradiction state

Filter state must be visible and reversible.

# 54. GRAPH QUERY CHIPS

Display active filters as compact chips:

```text
Case: CASE-001
Lens: Provenance
Time: Oct 1–Oct 8
Nodes: Person, Device
Edges: USES
Status: Reviewed
```

Provide:
- remove
- clear all
- save view

# 55. SAVE VIEW

A saved view stores visualization/query state:

```text
case
graph checkpoint
lens
filters
selected IDs
layout
camera
timeline range
```

It does not create new forensic facts.

# 56. GRAPH STATE INDICATOR

Top-right status:

```text
● LIVE
● SYNCING
● STALE
● REPLAY
● OFFLINE
```

Only use LIVE when backend freshness policy confirms it.

# 57. REALTIME GRAPH PULSE

When a real graph event arrives:

```text
Graph event
 ↓
validate sequence
 ↓
authorize case
 ↓
merge state
 ↓
subtle visual transition
 ↓
event indicator
```

Do not animate fake activity.

# 58. REALTIME EVENT TYPES

Potential:

```text
EVIDENCE_CREATED
ARTIFACT_CREATED
ENTITY_CREATED
ENTITY_UPDATED
EDGE_CREATED
EDGE_UPDATED
EDGE_REVIEWED
CONTRADICTION_CREATED
TIMELINE_EVENT_CREATED
PROCESSING_COMPLETED
GRAPH_PROJECTION_UPDATED
```

Use only events actually implemented by CrimeKit.

# 59. RECONNECT MODEL

If realtime disconnects:

```text
LIVE
 ↓
RECONNECTING
 ↓
SYNCING
 ↓
LIVE
```

If event sequence gap:
- request bounded replay
- or refresh current graph snapshot

# 60. OFFLINE / DEGRADED UI

If Neo4j is unavailable:
- keep case shell alive
- show graph unavailable
- preserve non-graph modules
- do not display stale data as current

# 61. LOADING STATES

Avoid blank screen.

Use:
- graph skeleton
- subtle node placeholders only where appropriate
- progress status
- current operation
- cancel option for async operations

# 62. ERROR STATES

Graph errors should explain:
- what failed
- whether the case data is safe
- whether retry is possible
- whether the graph is stale
- what action is available

Never show raw stack traces.

# 63. EMPTY STATE

Example:

```text
NO GRAPH RELATIONSHIPS YET

Evidence has been uploaded, but no graph relationships
have been projected for this case.

[View Evidence]   [Check Processing]
```

Never generate fake nodes to make the screen look populated.

# 64. GRAPH PROJECTION STATE

If projection is running:

```text
GRAPH SYNC
Processing forensic relationships…

Source events: 1,248
Projected: 1,194
Pending: 54

Last update: 10:42:31
```

Only show real counters.

# 65. GRAPH FRESHNESS

Show:

```text
Last synchronized
Projection version
Graph state
```

Do not claim realtime based only on a WebSocket connection.

# 66. 2D FALLBACK

Provide a 2D mode for:
- low-end devices
- accessibility
- reduced motion
- WebGL failure
- dense graph analysis
- debugging

The semantic graph must remain identical.

# 67. ACCESSIBILITY

Must support:
- keyboard navigation
- focus visibility
- screen-reader-accessible metadata outside canvas
- alternative node/edge list
- high contrast
- reduced motion
- non-color status encoding
- zoom controls
- accessible inspector

Never make 3D the only way to access graph information.

# 68. COLOR ACCESSIBILITY

Do not rely only on color.

Use:
- icons
- patterns
- labels
- line styles
- shapes
- status badges

for semantic differentiation.

# 69. REDUCED MOTION

When reduced motion is enabled:
- remove orbit animations
- remove pulsing
- replace animated edge drawing with instant transitions
- disable decorative camera movement

# 70. RESPONSIVE DESIGN

Desktop-first because the graph is information-dense.

Still support:
- laptop
- tablet
- narrow screens

On narrow screens:
- collapse sidebars
- use bottom sheets
- preserve graph interaction
- keep inspector accessible

# 71. DENSITY PRINCIPLE

Prefer:
- compact controls
- small labels
- strong hierarchy
- meaningful whitespace

Avoid:
- oversized cards
- excessive padding
- marketing-style empty space

# 72. PANEL SYSTEM

Panels should have:
- consistent border
- compact header
- title
- status
- collapse control
- optional resize handle

Panels must not obscure critical graph context without user intent.

# 73. RIGHT INSPECTOR

Width should be responsive and resizable.

Sections:
```text
Overview
Properties
Relationships
Evidence
Timeline
Provenance
Contradictions
Review
```

Only render sections with available data.

# 74. BOTTOM TIMELINE

Bottom workspace can switch between:
- timeline
- replay
- graph events
- query results
- AI explanation

Do not permanently consume excessive viewport height.

# 75. TOP GLOBAL HEADER

Header:
- CrimeKit identity
- case breadcrumb
- investigation
- global search
- graph state
- notification/event state
- user/access state

Keep it compact.

# 76. LEFT NAVIGATION

Reuse current CrimeKit navigation where practical:

```text
Dashboard
Cases
Evidence
Processing
Timeline
Knowledge Graph
AI Investigation
Reports
Audit
Settings
```

Graph screen should feel integrated, not like a separate application.

# 77. GRAPH-SPECIFIC LEFT TOOLS

Optional contextual drawer:

```text
LENS
FILTERS
LAYOUT
SAVED VIEWS
GRAPH STATS
```

Use progressive disclosure.

# 78. GRAPH STATS

Useful, non-misleading statistics:

```text
Visible Nodes
Visible Relationships
Entities
Evidence-linked Entities
Provenance-linked Relationships
Contradictions
Unresolved Candidates
Graph Projection Lag
```

Do not show "risk" unless it has a precise documented meaning.

# 79. GRAPH ANALYTICS VISUALS

If GDS analytics are available:
- clearly label algorithm
- show algorithm parameters
- show graph scope
- show graph version
- explain what the metric means
- provide methodology

Never label PageRank/centrality as guilt or threat.

# 80. SEARCH RESULTS

Search result card:
- entity type
- title
- ID
- match reason
- evidence count
- relationship count
- status

Click:
→ graph focus
→ inspector

# 81. PATH VISUALIZATION

For selected source and target:

```text
SOURCE
  ↓
A
  ↓
B
  ↓
TARGET
```

Show:
- hop count
- relationship types
- evidence availability
- temporal compatibility where supported
- provenance availability

Do not imply causal certainty.

# 82. PATH COMPARISON

Allow two paths to be compared:

```text
Path A
Path B

Common nodes
Common edges
Different nodes
Different evidence
Different time ranges
```

# 83. GRAPH DIFF VIEW

Two-state mode:

```text
BEFORE                  AFTER
  ●──●                    ●──●
     \                             ●                       ●──●
```

Use:
- added
- removed
- changed
- reviewed

and show checkpoint IDs.

# 84. REPLAY CONTROLS

```text
|<  Previous
<    Step back
▶    Play/Pause
>    Step forward
>|   Next
```

Additional:
- speed
- event type filter
- time range
- jump to checkpoint

# 85. GRAPH STORY MARKERS

Timeline markers can represent:
- evidence arrival
- processing completion
- entity discovery
- relationship proposal
- contradiction
- review

Markers link directly to source records.

# 86. GRAPH EVENT FEED

Optional compact feed:

```text
10:42:31  EDGE_CREATED
10:42:28  ENTITY_RESOLVED
10:41:59  OCR_COMPLETED
```

Click event:
→ focus graph change
→ inspect source

# 87. FORENSIC PULSE

The graph can have a subtle activity indicator:

```text
LIVE FORENSIC PULSE
3 new graph changes
```

Do not pulse the whole graph continuously.
Only react to real events.

# 88. EVIDENCE HEATMAP

Potential lens:
show graph regions by evidence density.

But explicitly label:
```text
Evidence density
```

Never:
```text
crime density
suspect density
guilt density
```

# 89. PROVENANCE HEATMAP

Show relationships with complete vs incomplete provenance.

Example:
- complete provenance
- partial provenance
- unavailable provenance

This helps investigators prioritize verification.

# 90. REVIEW HEATMAP

Show:
- reviewed
- pending
- disputed
- rejected

Do not infer correctness from review status.

# 91. GRAPH LENS — FORENSIC OVERVIEW

Default lens:
- core entities
- high-value evidence relationships
- current timeline context
- provenance indicators

Keep initial render bounded.

# 92. GRAPH LENS — EVIDENCE

Center evidence nodes.
Show:
- artifacts
- observations
- affected entities
- processing runs

# 93. GRAPH LENS — IDENTITY

Show:
- person
- aliases
- devices
- accounts
- candidate relationships

Make candidate vs reviewed status explicit.

# 94. GRAPH LENS — DEVICE

Show:
- devices
- accounts
- IPs
- files
- observations
- people associations

Do not equate device ownership with human identity without evidence.

# 95. GRAPH LENS — COMMUNICATION

Show:
- phone
- email
- account
- message
- communication event

Preserve temporal direction where available.

# 96. GRAPH LENS — LOCATION

Show:
- locations
- events
- devices
- vehicles
- observations

Do not imply precise human location from indirect device signals.

# 97. GRAPH LENS — TIMELINE

Time-centric graph:
- event markers
- actors
- devices
- evidence
- locations

Allow time-window filtering.

# 98. GRAPH LENS — PROVENANCE

Source-centric:
```text
Evidence → Artifact → Processing → Observation → Relationship
```

# 99. GRAPH LENS — CONTRADICTION

Highlight only actual contradictions/conflicts.

Show:
- conflict type
- sources
- timestamps
- review status

# 100. GRAPH LENS — PROCESSING

Show:
```text
Processing Run
 → Artifacts
 → Extraction
 → Entities
 → Relations
```

Useful for forensic auditability.

# 101. GRAPH LENS — INVESTIGATION

High-level:
- selected investigation entities
- key evidence
- timeline
- reviewed relationships
- unresolved areas

Never automatically rank people as guilty.

# 102. VISUAL STATUS SYSTEM

Use semantic status tokens.

Example:

```text
OBSERVED      neutral
DERIVED       informational
CANDIDATE     warning
REVIEWED      positive
DISPUTED      warning/danger
REJECTED      muted
HYPOTHESIS    dashed
```

Exact colors must pass accessibility checks.

# 103. GLOW POLICY

Glow only for:
- active selection
- realtime event
- focused path
- current replay step

Never glow everything.

# 104. LABEL POLICY

Labels:
- visible on selection
- visible at close LOD
- hidden/abbreviated at distance
- always available in accessible list/inspector

Use collision avoidance.

# 105. EDGE LABEL POLICY

Edge labels should appear:
- on selection
- on hover
- in provenance/path mode
- when density permits

Never label every edge in a dense scene.

# 106. GRAPH BACKGROUND

Use a restrained technical canvas.

Possible:
- subtle grid
- very subtle spatial reference
- dark neutral background

Do not create:
- starfield
- galaxy
- cyberpunk particles
- decorative circuitry

# 107. 3D DEPTH

Use depth for navigation, not semantic importance.

Do not make deeper nodes look less important.
Do not imply distance = relationship strength.

# 108. SHADOWS

Use lightweight shadows only if they improve node readability.

Disable or reduce expensive effects for performance mode.

# 109. PARTICLES

Particles are prohibited unless they represent a real semantic stream.

Example legitimate use:
- actual realtime event flow

Even then:
- low density
- accessible alternative
- disabled in reduced-motion mode

# 110. ANIMATION SYSTEM

Define animation tokens:

```text
instant
fast
normal
slow
replay
```

All animation must have:
- semantic purpose
- cancellation
- reduced-motion behavior

# 111. GRAPH TRANSITIONS

When expanding:
- new nodes enter smoothly
- existing nodes remain stable
- camera moves only when requested
- selected node remains anchored

# 112. CAMERA STABILITY

Never unexpectedly teleport the investigator.

Automatic camera movement must be:
- triggered by explicit action
- short
- reversible

# 113. PERFORMANCE BUDGET

Define measurable budgets rather than arbitrary claims.

Measure:
- first graph render
- first interactive frame
- FPS during interaction
- node count
- edge count
- GPU memory where measurable
- JS memory
- network payload
- API latency

# 114. PROGRESSIVE GRAPH LOADING

```text
1. shell
2. overview
3. selected neighborhood
4. requested expansion
5. provenance
6. evidence
```

Do not wait for every related store before showing the initial safe graph.

# 115. NETWORK OPTIMIZATION

Use:
- compact DTOs
- pagination
- compression
- delta events
- lazy inspector data
- batched expansion

Do not send full evidence metadata with every node.

# 116. FRONTEND STATE MODEL

Separate:

```text
canonical graph data
visualization state
selection state
query state
timeline state
realtime state
inspector state
AI state
```

Do not mix UI camera state with forensic graph state.

# 117. GRAPH STORE

Use the existing CrimeKit state management approach.

If creating a graph store, separate:

```text
graph.nodes
graph.edges
graph.meta

selection.nodeIds
selection.edgeIds

view.lens
view.layout
view.filters
view.camera

realtime.connection
realtime.sequence
```

# 118. API CONTRACT

The frontend must consume the Graph API defined in Prompt #6.

Do not:
- query Neo4j directly
- query MCP
- embed Cypher
- expose Neo4j credentials

# 119. MCP / ANTIGRAVITY

Developer workflow:

```text
Google Antigravity
        ↓
Official Neo4j MCP
        ↓
get-schema
        ↓
read-cypher
        ↓
list-gds-procedures
        ↓
Neo4j DEV/STAGING
```

MCP is a developer/agent tooling plane.

Production UI:

```text
CrimeKit Frontend
        ↓
FastAPI Graph API
        ↓
Neo4j
```

Never:
```text
Browser → MCP → Neo4j
```

# 120. MCP SAFETY

Use readonly MCP by default for production-adjacent environments.

The official Neo4j MCP documentation describes tools including get-schema, read-cypher, write-cypher and list-gds-procedures, and documents a read-only environment option that disables write tools. citeturn0search1

If write access is required:
- development only
- synthetic data
- explicit approval
- audited
- no destructive production operations

# 121. ANTIGRAVITY IMPLEMENTATION LOOP

```text
Inspect repository
 ↓
Inspect existing graph UI
 ↓
Inspect Graph API
 ↓
Inspect Neo4j schema through MCP
 ↓
Implement UI component
 ↓
Run frontend tests
 ↓
Run API tests
 ↓
Inspect real graph
 ↓
Validate 3D rendering
 ↓
Validate provenance
 ↓
Validate security
```

# 122. REFERENCE SCREEN AUDIT

Before implementation, inspect every supplied reference screen in the user's reference folder.

For each screenshot record:

```text
SCREEN
├── global layout
├── sidebar
├── topbar
├── canvas
├── search
├── toolbar
├── legend
├── inspector
├── cards
├── graph controls
├── typography
├── spacing
├── border treatment
├── iconography
├── color tokens
├── hover states
├── selected states
└── responsive behavior
```

Do not guess if the reference screen visibly answers the question.

# 123. REFERENCE SCREEN → DESIGN TOKEN MATRIX

Create a matrix:

| Element | Reference | CrimeKit Current | Final |
|---|---|---|---|
| Canvas | | | |
| Sidebar | | | |
| Header | | | |
| Search | | | |
| Panels | | | |
| Borders | | | |
| Text | | | |
| Accent | | | |
| Graph Nodes | | | |
| Graph Edges | | | |
| Inspector | | | |
| Legend | | | |
| Timeline | | | |

# 124. DO NOT BREAK CURRENT CRIMEKIT

Before visual changes identify and preserve:
- routing
- authentication
- RBAC
- case management
- evidence
- processing
- timeline
- graph API
- realtime
- audit
- reports
- existing design system
- existing API hooks
- existing stores

Visual modernization must not become an architecture rewrite.

# 125. COMPONENT ARCHITECTURE

Preferred conceptual structure:

```text
KnowledgeGraphPage
├── GraphShell
│   ├── GraphHeader
│   ├── GraphSidebar
│   ├── GraphCanvas3D
│   ├── GraphToolbar
│   ├── GraphLegend
│   ├── GraphMinimap
│   ├── GraphInspector
│   ├── GraphTimeline
│   └── GraphCommandBar
├── GraphStateProvider
├── GraphAPIClient
├── GraphRealtimeClient
└── GraphAccessibilityView
```

Use actual repository conventions.

# 126. COMPONENT CONTRACTS

Each component must define:
- inputs
- outputs
- state
- loading
- empty
- error
- accessibility
- performance
- telemetry where appropriate

# 127. GRAPH CANVAS CONTRACT

Inputs:
- nodes
- edges
- visual semantics
- selection
- layout
- filters
- realtime changes

Outputs:
- selected node
- selected edge
- camera state
- interaction events

# 128. INSPECTOR CONTRACT

Input:
- selected graph object

Output:
- actions

Data:
- fetched lazily from Graph API

The inspector must not require the entire graph payload.

# 129. LEGEND CONTRACT

Legend must be generated from the actual graph perspective/ontology where possible.

Avoid a hardcoded legend that drifts from the backend schema.

# 130. SEARCH CONTRACT

Search must:
- debounce
- cancel stale requests
- show loading
- show result count
- support keyboard navigation
- preserve case scope
- preserve authorization

# 131. GRAPH QUERY CANCELLATION

If a user rapidly changes filters:
- cancel obsolete frontend requests
- ignore stale responses
- maintain request IDs

Never allow an old query to overwrite a newer graph state.

# 132. REALTIME MERGE RULES

Use stable IDs.

For incoming event:
```text
if new → insert
if update → patch
if retired → mark/remove according to policy
```

Never duplicate nodes/edges because the same event arrived twice.

# 133. REALTIME ORDERING

Use:
- event sequence
- timestamps
- graph version

If ordering cannot be trusted:
- show syncing state
- recover snapshot

# 134. GRAPH EXPORT UI

Allow:
- image
- structured graph export
- saved view

Only if backend permissions allow it.

Export must show scope:
```text
Current visible graph
Selected subgraph
Full authorized case graph
```

# 135. EXPORT WATERMARK / CONTEXT

For forensic-facing visual exports, include:
- case ID
- view name
- timestamp
- graph/projection version
- generated-by
- disclaimer that visualization is a representation of graph data

Use actual policy requirements.

# 136. FORENSIC REPORT LINK

From graph:
```text
Select entity/relationship
 ↓
Create report context
 ↓
Open report builder
```

Do not create report facts that cannot be traced to source records.

# 137. GRAPH BOOKMARKS

Allow investigator to bookmark:
- entity
- edge
- path
- evidence
- graph state

Bookmarks are workflow metadata.

# 138. INVESTIGATION WORKSPACE

Allow a saved workspace to contain:

```text
selected entities
selected relationships
saved paths
evidence references
timeline range
lens
annotations
```

Clearly distinguish annotations from evidence.

# 139. INVESTIGATOR ANNOTATIONS

Annotations:
- author
- timestamp
- text
- related object
- review status

Do not overwrite source evidence.

# 140. GRAPH COMPARE MODE

Compare:
- two entities
- two paths
- two checkpoints
- two evidence impacts

Keep the graph readable by splitting or focusing the scene.

# 141. GRAPH SEARCH HISTORY

Optional:
- recent searches
- saved searches

Do not expose sensitive search history across users.

# 142. SEARCH SUGGESTIONS

Suggestions can come from:
- ontology
- indexed entities
- known graph patterns

Do not leak entities from unauthorized cases.

# 143. GRAPH PATTERN TEMPLATES

Safe templates:

```text
Person → Device
Person → Account
Device → IP
Evidence → Artifact
Artifact → Entity
Entity → Timeline
Evidence → Relationship
```

Templates generate structured API requests.

# 144. GRAPH PATTERN BUILDER

Optional visual builder:

```text
[Person]
   ↓ USES
[Device]
   ↓ CONNECTED_TO
[IP]
```

Then:
```text
Run Search
```

The builder creates a safe typed request.

# 145. NATURAL LANGUAGE GRAPH SEARCH

If implemented:
```text
User language
 ↓
intent parser
 ↓
typed graph query
 ↓
authorization
 ↓
Graph API
```

Never:
```text
LLM → raw Cypher → production Neo4j
```

# 146. GRAPH EXPLANATION PANEL

When an AI explanation is shown:

```text
ANSWER
Evidence-backed reasoning

SOURCES
E001
ART001
REL001

LIMITATIONS
...

UNCERTAINTY
...

NEXT REVIEW
...
```

This makes AI explainable.

# 147. AI VISUAL HIGHLIGHT

If AI refers to an entity:
- highlight actual node
- show ID
- provide evidence link

If AI mentions an entity not found in graph:
- mark as unverified
- do not create node automatically

# 148. AI HYPOTHESIS VISUAL

AI-generated hypothesis must appear only in sandbox:

```text
AI HYPOTHESIS
NOT CANONICAL
```

Require explicit human action before any promotion workflow.

# 149. GRAPH PRIVACY

Privacy controls must include:
- case isolation
- field masking
- access logs
- export control
- secure URLs
- no sensitive graph data in client-side logs

# 150. CLIENT SECURITY

Never ship:
- Neo4j password
- Neo4j private credentials
- MCP credentials
- object-store secrets
- internal service tokens

to browser bundles.

# 151. URL SECURITY

Do not put sensitive evidence content or credentials into query strings.

Use opaque authorized resource IDs where necessary.

# 152. CONTENT SECURITY

Respect application CSP.

Avoid unsafe dynamic script injection.

Third-party 3D libraries must be pinned/reviewed according to repository security policy.

# 153. DEPENDENCY RULE

Do not add:
- multiple graph rendering libraries
- multiple icon libraries
- duplicate state managers
- duplicate animation engines

unless a measured requirement justifies it.

# 154. RENDERER SELECTION

Inspect current repository.

If already using:
- Three.js
- React Three Fiber
- Sigma
- Cytoscape
- another renderer

evaluate it first.

Do not rewrite the graph engine only because another library is fashionable.

# 155. THREE.JS / WEBGL RULE

If Three.js is selected:
- isolate rendering layer
- keep domain DTOs renderer-agnostic
- dispose geometries/materials/textures
- handle WebGL context loss
- avoid memory leaks
- use instancing where appropriate
- use LOD

# 156. WEBGL FAILURE

Fallback:

```text
WebGL unavailable
 ↓
2D graph mode
 ↓
accessible graph list
```

Do not show a blank page.

# 157. GPU PERFORMANCE

Avoid:
- thousands of unique materials
- unnecessary post-processing
- expensive shadows
- huge textures
- unbounded text sprites
- per-frame object creation

# 158. TEXT RENDERING

3D text is expensive.

Prefer:
- labels only near selection
- billboards
- HTML overlays where appropriate
- canvas/text atlas where appropriate
- 2D accessible metadata

# 159. NODE INSTANCING

For repeated node geometry:
- use instancing when compatible
- maintain ID mapping
- preserve selection
- preserve accessibility through external UI

# 160. EDGE RENDERING

For dense graphs:
- batched lines
- simplified geometry
- opacity reduction
- LOD
- path-specific highlighting

Avoid one heavyweight mesh object per relationship where scale makes this impractical.

# 161. GRAPH MEMORY MANAGEMENT

On case switch:
- dispose previous scene
- clear subscriptions
- clear graph store
- cancel requests
- remove event listeners

No cross-case graph leakage.

# 162. CASE SWITCH SECURITY

When switching case:

```text
unsubscribe old case
 ↓
clear graph state
 ↓
authorize new case
 ↓
fetch new overview
 ↓
subscribe new case
```

Never show old case graph during new case loading.

# 163. MULTI-TAB SAFETY

If multiple tabs:
- case scope must remain explicit
- realtime subscriptions must be isolated
- saved view state must not corrupt another case

# 164. SESSION EXPIRATION

On authentication expiry:
- stop graph requests
- stop realtime
- clear sensitive graph state as policy requires
- redirect/re-authenticate

# 165. AUDIT UX

Meaningful graph actions should be auditable:
- search
- expansion
- path analysis
- evidence open
- provenance open
- export
- review action

Do not audit every mouse movement.

# 166. PERFORMANCE OBSERVABILITY

Measure:

```text
Graph API latency
Graph payload size
Initial render time
Time to interaction
FPS
Node count
Edge count
WebGL memory if available
Realtime lag
Projection lag
```

# 167. USER EXPERIENCE TELEMETRY

If telemetry is enabled:
- follow privacy policy
- avoid sensitive evidence content
- collect performance metrics rather than raw forensic content

# 168. GRAPH QUALITY INDICATORS

Optional system-level indicator:

```text
GRAPH HEALTH
Projection: Healthy
Provenance: 98%
Realtime: Connected
Schema: Compatible
```

Only display metrics backed by real measurements.

# 169. SCHEMA COMPATIBILITY

If API ontology and Neo4j schema mismatch:
- do not silently render wrong semantics
- show degraded state
- report schema compatibility error

# 170. VISUAL SCHEMA DRIFT

If a new node type appears:
- use fallback neutral style
- label as unknown/unmapped
- log telemetry
- do not crash the graph

# 171. UNKNOWN RELATIONSHIP

Unknown edge type:
- render neutral fallback
- show exact type in inspector
- mark mapping unavailable
- never assign a misleading semantic color

# 172. GRAPH DESIGN TOKENS

Create centralized tokens for:

```text
spacing
radius
border
shadow
font
icon
node
edge
animation
z-index
panel
canvas
status
```

Do not scatter constants across components.

# 173. ICON SYSTEM

Use one consistent icon family.

Node icons must be:
- recognizable
- small
- accessible
- semantically stable

Avoid using icons purely for decoration.

# 174. MICROINTERACTIONS

Useful:
- hover highlight
- selection ring
- panel open
- search result focus
- timeline marker focus
- provenance path highlight

Avoid:
- bouncing
- spinning
- flashy transitions

# 175. TOOLTIP SYSTEM

Tooltip should explain:
- node type
- relationship type
- status
- key metadata

Avoid tooltips containing sensitive data the user cannot otherwise access.

# 176. COMMAND DISCOVERY

Use:
- tooltips
- keyboard shortcut hints
- context menu
- command bar

but keep the screen visually quiet.

# 177. KEYBOARD SHORTCUTS

Potential:
```text
F       Focus
E       Expand
I       Inspector
L       Lens
T       Timeline
R       Replay
F2      Search
Esc     Clear selection
Space   Pause replay
```

Use only if consistent with the existing application.

# 178. TOUCH SUPPORT

For supported touch devices:
- pinch zoom
- pan
- tap selection
- long press/context
- bottom-sheet inspector

# 179. GRAPH 3D TO 2D TRANSITION

Transition must preserve:
- selected IDs
- filters
- lens
- visible graph
- inspector state

Only geometry/layout changes.

# 180. GRAPH FULLSCREEN

Fullscreen should:
- hide global navigation if permitted
- preserve case identity
- preserve user controls
- offer exit

# 181. MULTI-MONITOR / LARGE SCREEN

On large screens:
- graph canvas grows
- inspector remains bounded
- side controls remain compact
- labels do not become huge

# 182. LOW-END MODE

Offer:
```text
Performance Mode
```

Reduce:
- shadows
- post-processing
- labels
- animations
- geometry complexity

# 183. INVESTIGATOR MODE

Potential preference:

```text
ANALYSIS
PRESENTATION
PERFORMANCE
ACCESSIBILITY
```

Each changes UI behavior without changing graph truth.

# 184. PRESENTATION MODE

For authorized presentations:
- cleaner canvas
- controlled labels
- hide technical controls
- preserve case identity
- export-ready layout

Do not hide important uncertainty/dispute information if the view is used for evidentiary explanation.

# 185. FORENSIC REVIEW MODE

Prioritize:
- provenance
- evidence
- timeline
- contradictions
- review state

# 186. GRAPH DEBUG MODE

Developer-only:
- node IDs
- edge IDs
- renderer stats
- API requests
- event sequence
- projection version
- graph schema

Never expose this to ordinary investigators by default.

# 187. DESIGN SYSTEM GOVERNANCE

Every graph UI change must answer:

1. Which semantic meaning changed?
2. Which token changed?
3. Which components are affected?
4. Which API contract is affected?
5. Which accessibility behavior is affected?
6. Which tests must change?

# 188. VISUAL REGRESSION

Create screenshots for:
- empty graph
- small graph
- dense graph
- selected node
- selected edge
- provenance
- contradiction
- replay
- realtime
- error
- stale
- 2D fallback
- accessibility

# 189. END-TO-END TEST

Test:

```text
Login
 ↓
Case
 ↓
Knowledge Graph
 ↓
3D load
 ↓
Search
 ↓
Select
 ↓
Expand
 ↓
Inspector
 ↓
Evidence
 ↓
Provenance
 ↓
Timeline
 ↓
Realtime
 ↓
Replay
 ↓
Report
```

# 190. SECURITY TEST

Test:
- cross-case graph leakage
- cross-tenant leakage
- unauthorized evidence
- unauthorized export
- websocket subscription abuse
- stale cache leakage
- malformed filters
- oversized limits
- injection attempts
- session expiry

# 191. PERFORMANCE TEST

Benchmark:
- 100 nodes
- 1,000 nodes
- 10,000 persisted graph nodes
- high-degree entity
- dense subgraph
- realtime event burst
- repeated expansions

Actual supported viewport/render limits must come from measured results.

# 192. 3D LOAD TEST

Test:
- initial render
- repeated expansion
- collapse/re-expand
- case switching
- long sessions
- replay
- realtime updates

Look for:
- memory leaks
- FPS degradation
- duplicate objects
- stale subscriptions

# 193. SOAK TEST

Run the graph for extended sessions.

Check:
- memory
- event listeners
- WebSocket reconnects
- renderer resources
- API connections

# 194. CHAOS TEST

Inject:
- Neo4j outage
- API outage
- realtime disconnect
- projection delay
- malformed event
- WebGL failure
- expired auth

# 195. NO-FAKE-DATA GATE

Production graph must contain no:
- demo nodes
- random edges
- placeholder evidence
- fake confidence
- fake timestamps
- fake realtime
- fake analytics

Demo mode must be explicit and isolated.

# 196. DEMO MODE

If demo data is required:
- explicit DEMO banner
- synthetic dataset
- no resemblance to real case evidence
- no mixing with production data

# 197. DATA LINEAGE UI

Every major graph object should be able to answer:

```text
WHERE DID THIS COME FROM?
```

Possible:
- source evidence
- artifact
- processing
- model
- human review

# 198. SHOW THE WORK

CrimeKit's graph should visually expose:

```text
INPUT
 ↓
PROCESSING
 ↓
EXTRACTION
 ↓
RESOLUTION
 ↓
RELATIONSHIP
 ↓
REVIEW
```

This is a stronger differentiator than simply having 3D graphics.

# 199. GRAPH AS INVESTIGATION INSTRUMENT

The final screen must answer five questions immediately:

1. What am I looking at?
2. What is connected?
3. Why is it connected?
4. What evidence supports it?
5. What remains uncertain?

# 200. FINAL VISUAL TARGET

The target experience:

```text
                     CRIMEKIT
        FORENSIC KNOWLEDGE GRAPH WORKSPACE

 ┌─────────────────────────────────────────────────────────────┐
 │ Case ▾  Search graph…                 ● LIVE     User       │
 ├───────┬───────────────────────────────────────────┬─────────┤
 │       │                                           │         │
 │ LENS  │                                           │ ENTITY  │
 │       │               3D GRAPH                    │         │
 │ ●     │                                           │ Person  │
 │ EVID. │          ●────────●                       │ P001    │
 │       │        ╱          ╲                       │         │
 │ ID    │      ●              ●                     │ Evidence│
 │       │       ╲            ╱                      │ Timeline│
 │ TIME  │          ●──────●                         │ Proven. │
 │       │                                           │ Review  │
 │ PROV. │                                           │         │
 │       │       [graph controls]                   │         │
 ├───────┴───────────────────────────────────────────┴─────────┤
 │ ◀  Timeline  ─────────●──────────────  Replay  ▶  Events    │
 └─────────────────────────────────────────────────────────────┘
```

It must feel:
- premium
- intelligent
- forensic
- technical
- calm
- trustworthy
- graph-native
- production-grade

# 201. WHAT MAKES IT DIFFERENT

The novelty is not simply "3D".

The differentiated product stack is:

```text
Neo4j-style graph exploration
          +
3D spatial interaction
          +
Forensic provenance
          +
Temporal replay
          +
Evidence impact
          +
Contradiction awareness
          +
Knowledge gaps
          +
Hypothesis isolation
          +
Human review
          +
AI grounding
          +
Realtime graph evolution
```

That combination is the intended CrimeKit product identity.

Do not claim that any individual feature is globally unprecedented.
The engineering goal is to create a genuinely differentiated integrated experience.

# 202. IMPLEMENTATION ORDER

PHASE 1 — REPOSITORY AUDIT
- inspect existing Graph UI
- inspect current Graph API
- inspect renderer
- inspect theme
- inspect screenshots
- inspect Neo4j schema through MCP

PHASE 2 — DESIGN SYSTEM
- tokens
- layout
- typography
- panels
- graph styles
- status system

PHASE 3 — 3D FOUNDATION
- renderer
- node geometry
- edge geometry
- camera
- LOD
- selection

PHASE 4 — GRAPH API INTEGRATION
- overview
- neighbors
- search
- path
- inspector
- provenance

PHASE 5 — FORENSIC MODES
- evidence impact
- timeline
- contradiction
- knowledge gaps
- hypothesis sandbox

PHASE 6 — REALTIME
- events
- sequence
- reconnect
- graph pulse

PHASE 7 — ADVANCED
- replay
- graph diff
- saved views
- graph lenses
- analytics

PHASE 8 — AI
- grounded graph tools
- explanation
- evidence citations
- uncertainty

PHASE 9 — HARDENING
- security
- accessibility
- performance
- visual regression
- production readiness

# 203. DO NOT REDESIGN BACKEND UNNECESSARILY

Prompt #6 defines the Graph API boundary.

This prompt defines the visual/interaction consumer.

Do not:
- replace PostgreSQL
- replace Neo4j
- replace Graph API
- replace Redis
- replace authentication
- replace existing forensic pipelines

unless repository evidence proves the current implementation is unusable.

# 204. REQUIRED REPOSITORY OUTPUT

Before implementation return:

### EXISTING
- graph page
- graph components
- graph API client
- state store
- renderer
- theme
- icons
- tests

### REUSE
What can remain unchanged?

### MODIFY
What needs visual modernization?

### NEW
What must be created?

### DELETE
What is genuinely dead/duplicate?

Never invent filenames.

# 205. REQUIRED DESIGN AUDIT

Return:

| Area | Current | Reference | Gap | Final |
|---|---|---|---|---|
| Layout | | | | |
| Sidebar | | | | |
| Header | | | | |
| Search | | | | |
| Graph | | | | |
| Inspector | | | | |
| Legend | | | | |
| Timeline | | | | |
| 3D | | | | |
| Typography | | | | |
| Colors | | | | |
| Motion | | | | |

# 206. REQUIRED 3D CONTRACT

Return:

| Element | Geometry | Semantic meaning | Interaction | API source |
|---|---|---|---|---|
| Person | | | | |
| Device | | | | |
| Account | | | | |
| Evidence | | | | |
| Artifact | | | | |
| Timeline | | | | |
| Processing | | | | |
| Contradiction | | | | |
| Hypothesis | | | | |

# 207. REQUIRED VISUAL TOKEN CONTRACT

Return:

| Token | Purpose | Value source | Accessibility check |
|---|---|---|---|
| Background | | | |
| Panel | | | |
| Border | | | |
| Text | | | |
| Muted text | | | |
| Accent | | | |
| Selection | | | |
| Warning | | | |
| Danger | | | |
| Success | | | |

# 208. REQUIRED INTERACTION MATRIX

| Action | Graph | Inspector | Timeline | Evidence | API |
|---|---|---|---|---|---|
| Click node | | | | | |
| Click edge | | | | | |
| Expand | | | | | |
| Focus | | | | | |
| Search | | | | | |
| Replay | | | | | |
| Evidence | | | | | |
| Provenance | | | | | |

# 209. REQUIRED STATE MATRIX

| State | Graph | Inspector | Header | Timeline |
|---|---|---|---|---|
| Loading | | | | |
| Empty | | | | |
| Live | | | | |
| Stale | | | | |
| Syncing | | | | |
| Error | | | | |
| Offline | | | | |
| Replay | | | | |

# 210. REQUIRED TEST MATRIX

| Test | Expected |
|---|---|
| Case isolation | no leakage |
| Search | scoped |
| Expansion | bounded |
| Provenance | real |
| Evidence impact | real |
| Timeline | temporal correctness |
| Replay | actual events |
| Realtime | ordered |
| WebGL failure | 2D fallback |
| Reduced motion | respected |
| Accessibility | usable |
| Performance | measured |

# 211. FINAL PRODUCTION GATES

Do not declare complete until:

```text
[ ] Reference screens audited
[ ] Current CrimeKit graph UI audited
[ ] Neo4j schema verified
[ ] Graph API contract verified
[ ] No frontend → Neo4j connection
[ ] MCP isolated to developer/agent plane
[ ] Case authorization verified
[ ] 3D renderer stable
[ ] 2D fallback works
[ ] Accessibility works
[ ] Realtime is real
[ ] Provenance is real
[ ] Evidence links are real
[ ] Timeline is real
[ ] Contradictions are real
[ ] No fake graph data
[ ] No fake confidence
[ ] No fake freshness
[ ] No graph hallucinations
[ ] Performance benchmarked
[ ] Security tested
[ ] Visual regression tested
[ ] Case switching safe
[ ] Long-session memory stable
[ ] Production build passes
```

# 212. FINAL GOLDEN USER JOURNEY

```text
LOGIN
 ↓
OPEN CASE
 ↓
KNOWLEDGE GRAPH
 ↓
3D OVERVIEW
 ↓
SEARCH "PERSON P001"
 ↓
FOCUS
 ↓
EXPAND DEVICE
 ↓
SELECT RELATIONSHIP
 ↓
OPEN INSPECTOR
 ↓
PROVENANCE THREAD
 ↓
OPEN EVIDENCE
 ↓
SHOW TIMELINE
 ↓
SHOW CONTRADICTION
 ↓
REPLAY GRAPH EVOLUTION
 ↓
ASK GROUNDED AI QUESTION
 ↓
VIEW SOURCES
 ↓
HUMAN REVIEW
 ↓
SAVE INVESTIGATION VIEW
 ↓
REPORT
```

# 213. FINAL MASTER DIRECTIVE

Act as the senior engineering/design owner of an international enterprise digital-forensics platform.

Do not merely make CrimeKit "look like Neo4j".

Make it operate with the same level of graph-native clarity while adding a CrimeKit-specific forensic intelligence layer.

The visual target is:

**Neo4j-style graph ergonomics**
+
**CrimeKit forensic semantics**
+
**3D spatial exploration**
+
**provenance-first interaction**
+
**temporal graph intelligence**
+
**human-review boundaries**
+
**secure Graph API**
+
**grounded AI**
+
**production engineering**

Every screen must be beautiful because it is useful.
Every animation must be meaningful.
Every graph object must be explainable.
Every important relationship must be traceable.
Every AI statement must be grounded.
Every sensitive operation must be authorized.
Every performance claim must be measured.

Never sacrifice forensic correctness for visual novelty.
Never sacrifice usability for 3D effects.
Never sacrifice security for convenience.
Never sacrifice explainability for AI magic.

Build a product that an investigator can trust, a security team can approve, an enterprise architect can scale, and a senior engineer can maintain.

# 214. OFFICIAL REFERENCE NOTES

Neo4j's official documentation describes:
- Bloom as a graph exploration UI
- a graph Scene as the main visualization workspace
- search, toolbars, map and legend
- perspectives as business-context views
- card lists and inspectors
- graph visualization and interaction
- Aura's integrated graph tools and management UI

Sources:
https://neo4j.com/docs/bloom-user-guide/current/bloom-visual-tour/
https://neo4j.com/docs/bloom-user-guide/current/about-bloom/
https://neo4j.com/docs/aura/visual-tour/
https://neo4j.com/docs/aura/explore/explore-visual-tour/explore-overview/
https://neo4j.com/docs/aura/explore/explore-visual-tour/legend-panel/

Use the current official documentation when implementing version-sensitive Neo4j behavior.

### APPENDIX CHECK 001 — REFERENCE SCREENSHOT INVENTORY

For **Reference screenshot inventory**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 002 — CURRENT CRIMEKIT UI INVENTORY

For **Current CrimeKit UI inventory**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 003 — EXISTING GRAPH RENDERER

For **Existing graph renderer**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 004 — EXISTING GRAPH STORE

For **Existing graph store**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 005 — EXISTING GRAPH API CLIENT

For **Existing Graph API client**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 006 — EXISTING THEME TOKENS

For **Existing theme tokens**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 007 — EXISTING ICON SYSTEM

For **Existing icon system**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 008 — EXISTING TYPOGRAPHY

For **Existing typography**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 009 — SIDEBAR AUDIT

For **Sidebar audit**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 010 — HEADER AUDIT

For **Header audit**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 011 — SEARCH AUDIT

For **Search audit**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 012 — TOOLBAR AUDIT

For **Toolbar audit**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 013 — LEGEND AUDIT

For **Legend audit**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 014 — INSPECTOR AUDIT

For **Inspector audit**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 015 — TIMELINE AUDIT

For **Timeline audit**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 016 — REALTIME AUDIT

For **Realtime audit**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 017 — GRAPH API CONTRACT

For **Graph API contract**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 018 — NEO4J SCHEMA CONTRACT

For **Neo4j schema contract**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 019 — MCP CONFIGURATION

For **MCP configuration**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 020 — ANTIGRAVITY MCP ENVIRONMENT

For **Antigravity MCP environment**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 021 — MCP READONLY POLICY

For **MCP readonly policy**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 022 — NODE ONTOLOGY

For **Node ontology**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 023 — RELATIONSHIP ONTOLOGY

For **Relationship ontology**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 024 — NODE SHAPES

For **Node shapes**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 025 — EDGE STYLES

For **Edge styles**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 026 — NODE SIZE SEMANTICS

For **Node size semantics**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 027 — EDGE THICKNESS SEMANTICS

For **Edge thickness semantics**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 028 — SELECTION STATE

For **Selection state**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 029 — HOVER STATE

For **Hover state**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 030 — FOCUS STATE

For **Focus state**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 031 — LOD STRATEGY

For **LOD strategy**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 032 — CAMERA STRATEGY

For **Camera strategy**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 033 — LAYOUT STRATEGY

For **Layout strategy**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 034 — FORCE LAYOUT

For **Force layout**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 035 — RADIAL LAYOUT

For **Radial layout**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 036 — TIMELINE LAYOUT

For **Timeline layout**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 037 — EVIDENCE LAYOUT

For **Evidence layout**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 038 — PROVENANCE LAYOUT

For **Provenance layout**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 039 — CLUSTER LAYOUT

For **Cluster layout**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 040 — HIGH-DEGREE HANDLING

For **High-degree handling**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 041 — MINIMAP

For **Minimap**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 042 — GRAPH CONTROLS

For **Graph controls**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 043 — 2D FALLBACK

For **2D fallback**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 044 — WEBGL FALLBACK

For **WebGL fallback**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 045 — REDUCED MOTION

For **Reduced motion**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 046 — KEYBOARD NAVIGATION

For **Keyboard navigation**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 047 — SCREEN READER REPRESENTATION

For **Screen reader representation**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 048 — COLOR CONTRAST

For **Color contrast**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 049 — STATUS ENCODING

For **Status encoding**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 050 — PANEL SYSTEM

For **Panel system**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 051 — RIGHT INSPECTOR

For **Right inspector**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 052 — BOTTOM TIMELINE

For **Bottom timeline**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 053 — COMMAND BAR

For **Command bar**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 054 — GRAPH LENS SYSTEM

For **Graph lens system**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 055 — FILTER SYSTEM

For **Filter system**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 056 — SAVED VIEWS

For **Saved views**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 057 — GRAPH SEARCH

For **Graph search**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 058 — PATH VISUALIZATION

For **Path visualization**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 059 — GRAPH DIFF

For **Graph diff**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 060 — REPLAY

For **Replay**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 061 — REALTIME PULSE

For **Realtime pulse**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 062 — EVENT FEED

For **Event feed**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 063 — PROJECTION STATUS

For **Projection status**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 064 — FRESHNESS STATE

For **Freshness state**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 065 — ERROR STATE

For **Error state**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 066 — EMPTY STATE

For **Empty state**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 067 — LOADING STATE

For **Loading state**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 068 — OFFLINE STATE

For **Offline state**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 069 — CASE SWITCHING

For **Case switching**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 070 — MULTI-TAB ISOLATION

For **Multi-tab isolation**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 071 — SESSION EXPIRY

For **Session expiry**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 072 — EXPORT

For **Export**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 073 — BOOKMARKS

For **Bookmarks**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 074 — ANNOTATIONS

For **Annotations**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 075 — COMPARE MODE

For **Compare mode**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 076 — EVIDENCE IMPACT

For **Evidence impact**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 077 — PROCESSING IMPACT

For **Processing impact**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 078 — CONTRADICTIONS

For **Contradictions**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 079 — KNOWLEDGE GAPS

For **Knowledge gaps**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 080 — HYPOTHESIS SANDBOX

For **Hypothesis sandbox**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 081 — UNCERTAINTY STACK

For **Uncertainty stack**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 082 — SOURCE DIVERSITY

For **Source diversity**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 083 — PROVENANCE THREAD

For **Provenance thread**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 084 — INVESTIGATION STORY

For **Investigation story**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 085 — AI GRAPH TOOLS

For **AI graph tools**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 086 — AI GROUNDING

For **AI grounding**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 087 — AI VISUAL HIGHLIGHTS

For **AI visual highlights**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 088 — AI HYPOTHESIS ISOLATION

For **AI hypothesis isolation**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 089 — GRAPH ANALYTICS

For **Graph analytics**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 090 — GDS VISUALIZATION

For **GDS visualization**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 091 — SECURITY

For **Security**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 092 — PII

For **PII**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 093 — SECRETS

For **Secrets**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 094 — CSP

For **CSP**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 095 — DEPENDENCIES

For **Dependencies**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 096 — PERFORMANCE

For **Performance**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 097 — FPS MEASUREMENT

For **FPS measurement**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 098 — PAYLOAD MEASUREMENT

For **Payload measurement**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 099 — API LATENCY

For **API latency**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 100 — MEMORY LEAK TESTING

For **Memory leak testing**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 101 — LONG-SESSION TESTING

For **Long-session testing**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 102 — VISUAL REGRESSION

For **Visual regression**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 103 — ACCESSIBILITY TESTING

For **Accessibility testing**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 104 — SECURITY TESTING

For **Security testing**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 105 — CASE ISOLATION TESTING

For **Case isolation testing**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 106 — REALTIME TESTING

For **Realtime testing**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 107 — PRODUCTION BUILD

For **Production build**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 108 — ROLLBACK PLAN

For **Rollback plan**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 109 — RELEASE GATE

For **Release gate**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 110 — DOCUMENTATION

For **Documentation**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 111 — DEVELOPER HANDOFF

For **Developer handoff**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

### APPENDIX CHECK 112 — DESIGN GOVERNANCE

For **Design governance**, inspect the real repository and produce evidence.

Answer:
- What exists?
- Exact file/component path?
- IMPLEMENTED / PARTIAL / MOCKED / DEAD / DUPLICATED / DEPRECATED / PLANNED / UNKNOWN?
- Current behavior?
- Reference-screen behavior?
- Gap?
- Proposed final behavior?
- API dependency?
- Neo4j dependency?
- 3D dependency?
- Security implications?
- Performance implications?
- Accessibility implications?
- Tests required?
- Acceptance criteria?

Do not invent implementation details that are not supported by the repository.

## FINAL HANDOFF — PROMPT #8

After this visual UI work is complete, hand off stable contracts to:

**Prompt #8 — 3D GRAPH ENGINE + PRODUCTION RENDERING**

Handoff:
- node geometry map
- edge rendering map
- graph DTOs
- lens definitions
- layout contracts
- camera behavior
- LOD thresholds
- selection state
- realtime events
- provenance visualization
- timeline/replay contracts
- accessibility fallback
- performance budgets
- visual regression cases
- Neo4j MCP development workflow

# PROMPT #8 — DEEP 3D INTERACTION COMMAND LAYER
## ADDENDUM: 100 FORENSIC-NATIVE INTERACTION PRIMITIVES

Use this addendum as the implementation authority for the **interaction behavior** of the 3D workspace. The visual system may be Neo4j-inspired in ergonomics, but the interaction semantics must remain original to CrimeKit and forensic workflows.

### NON-NEGOTIABLE

The experience must feel like a professional investigation instrument rather than a game, crypto network, generic AI observatory, or decorative WebGL demo.

A “wow” moment is successful only when the investigator discovers a useful fact, source, contradiction, timeline relationship, lineage, uncertainty boundary, or graph change faster than with a conventional 2D interface.

---

## A. CAMERA + SPATIAL CONTROL

### 1. Focus Snap
Select an object → camera moves to a stable framing target → stops. Never overshoot. Never rotate unnecessarily.

### 2. Focus + Context
Focus on an entity while automatically revealing only the bounded local neighborhood required to understand it.

### 3. Focus Lock
Keep the selected entity centered while realtime data updates around it.

### 4. Camera Return Stack
Back/forward navigation restores prior camera + selection + inspector state.

### 5. Camera Bookmark
Save an approved investigation viewpoint as a named scene state.

### 6. Investigation Corridor
When comparing A and B, camera creates a neutral spatial corridor between their relevant evidence-backed paths.

### 7. Path Fly-Through
Navigate a selected path hop-by-hop. Each hop pauses long enough for the relationship inspector to be readable.

### 8. Local Explosion
Temporarily spread a dense neighborhood outward without changing actual graph topology.

### 9. Depth Slice
Drag a bounded depth plane to isolate a dense region. State exactly why the slice is active.

### 10. Orientation Restore
Return to a canonical case orientation without resetting filters or selection.

---

## B. NODE INTERACTIONS

### 11. Node Hover Preview
Show lightweight local information only. Never trigger an expensive network request on hover.

### 12. Node Select
Select + outline + local-neighbor emphasis + inspector synchronization.

### 13. Node Multi-Select
Shift/Ctrl click or accessible equivalent. Immediately expose group operations.

### 14. Node Double-Click Expand
Fetch a server-bounded neighborhood using explicit depth/node/edge budgets.

### 15. Node Context Menu
Context actions are generated from object type, object state, current mode, and authorization.

### 16. Node Isolate
Show a clearly labeled isolated view. Provide an immediate exit action.

### 17. Node Compare
Pin an entity in the inspector and select another entity without losing the first context.

### 18. Node Evidence Focus
Jump from a node to its supporting evidence without leaving the graph workspace.

### 19. Node Timeline Focus
Jump to the first or selected timeline event associated with the node.

### 20. Node Provenance X-Ray
Reveal how the canonical entity was constructed from source mentions or artifacts.

---

## C. EDGE / RELATIONSHIP INTERACTIONS

### 21. Edge Hover
Show relationship type + status only.

### 22. Edge Select
Highlight both endpoints and open the relationship inspector.

### 23. Relationship Microscope
Expand one edge into a temporary micro-scene showing source, derivation, time, review status and destination.

### 24. Why-This-Edge
One-click explanation built only from structured provenance / relationship metadata.

### 25. Edge Evidence Beam
Visually bridge the selected edge to supporting evidence.

### 26. Edge Timeline Beam
Show event timestamps supporting the relationship where available.

### 27. Edge Lifecycle View
Reveal OBSERVED → DERIVED → CANDIDATE → REVIEWED → DISPUTED/CONFIRMED/REJECTED → RETIRED where real state transitions exist.

### 28. Edge Contradiction Split
If sources disagree, show parallel source branches rather than silently merging them.

### 29. Edge Source Diversity
Show independent source groups, not raw duplicate count.

### 30. Edge Review Preview
Before a consequential review action, show current state vs proposed state.

---

## D. EVIDENCE-NATIVE INTERACTIONS

### 31. Evidence → Graph Impact
Select an evidence item → reveal directly and indirectly derived graph objects.

### 32. Graph → Evidence Trace
Select a graph object → surface all authorized supporting source records.

### 33. Evidence Gravity
Represent source-support density using a restrained halo/field. Never map it to guilt.

### 34. Evidence Support Stack
Expose source count, artifact count, review status, conflicts, and lineage completeness.

### 35. Evidence Dependency Warning
Show when many claims originate from the same upstream source.

### 36. Duplicate Evidence Cluster
Collapse duplicate copies while preserving every original record and custody path.

### 37. Evidence Hash Inspector
Expose forensic hash metadata in the evidence panel, not as decorative graph text.

### 38. Chain-of-Custody Link
Separate evidence custody state from analytical provenance state.

### 39. Evidence Frame Focus
For video-derived objects, jump to the exact frame/time where evidence was observed.

### 40. Evidence-Centered Scene
Temporarily make evidence the root of the scene and place derived objects around it.

---

## E. PROVENANCE + LINEAGE INTERACTIONS

### 41. Provenance Thread
Animate a controlled, user-triggered path from relationship → artifact → evidence → original source.

### 42. Provenance Reverse Trace
Start from evidence and travel forward to derived graph state.

### 43. Processing Impact Map
Select a processing run and reveal all downstream graph changes attributed to it.

### 44. Artifact X-Ray
Reveal the artifact(s) that produced a graph object.

### 45. Extraction Method Lens
Show whether data came from OCR, metadata parsing, entity extraction, media analysis, or another actual pipeline stage.

### 46. Model Version Lens
For model-derived relationships, compare model versions where provenance supports it.

### 47. Provenance Completeness Badge
Show COMPLETE / PARTIAL / UNKNOWN based on real lineage fields.

### 48. Orphan Lineage Detector
Highlight objects whose source lineage is incomplete or missing.

### 49. Provenance Repair Route
Open the exact workflow that can repair or reconcile an incomplete lineage when policy allows.

### 50. Source-to-Claim Matrix
Show which independent evidence groups support each important graph claim.

---

## F. TIME + TEMPORAL INTERACTIONS

### 51. Timeline Scrub
Move the time cursor → graph state updates to the selected window.

### 52. Temporal Lock
Lock the graph to a specific investigation time window.

### 53. Temporal Preview
Hover a moment on the timeline → preview the graph state without committing the change.

### 54. Temporal Replay
Play the graph evolution from one known state to another.

### 55. Temporal Compare
Compare T1 and T2 side by side or through graph diff.

### 56. Temporal Fog
Subdue older or outside-window objects without implying suspicion.

### 57. Temporal Uncertainty Band
Represent uncertain time ranges as bands, never fake exact timestamps.

### 58. Temporal Position Unknown
Objects without trustworthy time remain in an explicit UNKNOWN temporal state.

### 59. Event Constellation
Select one timeline event → reveal its people/devices/locations/evidence in a temporary 3D constellation.

### 60. Temporal Causality Guardrail
Never convert chronological sequence alone into a visual claim of causation.

---

## G. CONTRADICTION + UNCERTAINTY INTERACTIONS

### 61. Contradiction Fracture
Conflicting sources branch visibly from a shared subject.

### 62. Claim Comparison
Compare two competing claims with source/timestamp/extraction metadata.

### 63. Uncertainty Envelope
Show uncertainty around an object or relationship only when backed by measured fields.

### 64. Confidence Decomposition
If supported by the data model, expose components such as extraction and resolution confidence separately.

### 65. Review Pending Halo
Indicate candidate review status without implying wrongdoing.

### 66. Disputed Relationship State
Make disputed edges visually explicit and searchable.

### 67. Unknown State
Use UNKNOWN rather than inventing a score when data is missing.

### 68. Evidence Conflict Counter
Show the number of real conflicting source groups.

### 69. Resolution Disagreement
When identity resolution candidates compete, show the competing records rather than forcing a merge.

### 70. Methodology Popover
Any complex analytical visualization can expose the method and limitation in one click.

---

## H. SEARCH + DISCOVERY INTERACTIONS

### 71. Search-to-Focus
Search result → camera focus → inspector.

### 72. Search-to-Expand
Search result → focus → optional bounded neighborhood expansion.

### 73. Structured Query Chips
Represent active type/case/time/status filters as visible chips.

### 74. Semantic Search Suggestions
Suggestions may include ENTITY, RELATIONSHIP, EVIDENCE, EVENT, CASE.

### 75. Search History
Keep a bounded private session history; never expose it to other users by default.

### 76. Related Search
After selecting an entity, suggest authorized related search operations.

### 77. Query Explain
Show what the selected graph query is actually doing: scope, hops, budgets, filters.

### 78. Query Cancel
Cancel long-running searches without freezing the UI.

### 79. Query Replay
Reuse a previous structured scene query after authorization is rechecked.

### 80. Search Result Confidence Guard
Never rank results by hidden risk or suspicion unless the user explicitly enables a documented analytical mode.

---

## I. GRAPH OPERATIONS + ANALYTICS

### 81. Path Mode
Select A → select B → choose path metric → run bounded analysis.

### 82. Path Metric Switch
Compare hop count vs other declared metrics without silently mixing them.

### 83. Community Focus
Select a real community-analysis result → isolate and inspect topology.

### 84. Bridge Entity Explanation
Show the actual graph paths that make an entity a bridge-like node.

### 85. Centrality Lens
Show graph connectivity while explicitly avoiding guilt terminology.

### 86. Similarity Lens
Show similar-node candidates and the actual similarity basis where supported.

### 87. Anomaly Window
Open a bounded anomaly result with algorithm/scope/time/limitations.

### 88. Anomaly Explanation Path
Trace anomaly output back to observations and source evidence.

### 89. Graph Data Quality Lens
Reveal missing timestamps, orphan artifacts, stale projection, duplicate entities, unresolved links.

### 90. Knowledge Gap Explorer
Select a real graph gap → show what is missing, why it matters, and what evidence would reduce uncertainty.

---

## J. REVIEW + HUMAN CONTROL

### 91. Hypothesis Sandbox
Allow an investigator to create a non-authoritative hypothetical relationship.

### 92. Review Boundary
Separate observed/reviewed graph facts from candidate/hypothesis space.

### 93. Review Queue → Graph
Click a candidate in the queue → focus the graph → provenance → evidence → review action.

### 94. Review Impact Preview
Show exactly which graph objects will change before committing the review action.

### 95. Safe Review Transaction
Re-check authorization and version before the decision is committed.

### 96. Human Annotation Anchor
Attach a private or permissioned note to a node/edge/evidence/event.

### 97. Investigation Story Recording
Record deliberate investigator navigation as a reproducible story.

### 98. Story Playback
Replay the saved investigative sequence without changing authoritative data.

### 99. Presentation / Analyst Toggle
Switch between clean briefing mode and high-density analytical mode while preserving semantic state.

### 100. Two-Mode Truth
Every meaningful 3D interaction must have an equivalent 2D/table/inspector representation so the investigator is never forced to trust 3D alone.

---

# PROMPT #8 — INTERACTION STATE MACHINE

Implement interaction state using an explicit finite/state-machine approach rather than scattered booleans.

Suggested high-level state:

```text
IDLE
SELECTING
MULTI_SELECT
FOCUSING
FOCUSED
EXPANDING
FILTERING
PATH_SELECT_A
PATH_SELECT_B
PATH_LOADING
PATH_READY
PROVENANCE_LOADING
PROVENANCE_VISIBLE
TIMELINE_REPLAY
TIME_LOCKED
GRAPH_DIFF
CONTRADICTION_VIEW
REVIEW_PREVIEW
HYPOTHESIS_MODE
REALTIME_LIVE
REALTIME_DEGRADED
RENDERER_DEGRADED
```

Every transition must declare:

```text
current state
trigger
authorization requirement
data requirement
visual transition
new state
cancellable?
```

---

# PROMPT #8 — INTERACTION EVENT CONTRACT

Every important interaction should have a typed event concept.

Example:

```typescript
interface GraphInteractionEvent {
  interactionId: string;
  type: string;
  caseId: string;
  investigationId?: string;
  objectId?: string;
  objectType?: string;
  occurredAt: string;
  source: "user" | "realtime" | "replay" | "system";
}
```

Do not record sensitive payloads unnecessarily.

---

# PROMPT #8 — SEMANTIC SCENE RUNTIME

The renderer must receive semantic data rather than database details.

Conceptually:

```text
Backend Graph DTO
      ↓
Semantic Normalizer
      ↓
Scene Object Model
      ↓
Interaction State
      ↓
3D Renderer
```

Scene objects should be able to answer:

```text
Who am I?
What type am I?
What scope am I in?
What is my state?
What supports me?
When was I observed?
What is my current review state?
What actions are allowed?
```

---

# PROMPT #8 — 3D SEMANTIC MAP

Maintain a documented mapping table:

| Visual dimension | Allowed meaning | Forbidden meaning |
|---|---|---|
| node size | declared metric such as source count / degree when explicitly labeled | guilt / innocence |
| edge width | declared relationship metric | “importance” without definition |
| halo | support / uncertainty / selection | guilt |
| depth | layout unless explicitly documented | hidden suspicion score |
| color | categorical/status meaning | emotional judgment |
| glow | selected/realtime transition | danger / guilt by default |
| motion | event/replay/navigation | hidden intelligence |
| fog | explicit time/lens context | suspicion |
| transparency | visibility/LOD/state | certainty unless defined |

---

# PROMPT #8 — 3D EFFECT BUDGET

Every effect has a cost budget.

Track:

```text
active node effects
active edge effects
active particles
active labels
active tweens
active post-processing
```

If the budget is exceeded:

```text
aggregate
simplify
batch
or disable
```

Never preserve visual effects at the cost of investigative responsiveness.

---

# PROMPT #8 — ATTENTION ENGINE

Create a centralized attention engine.

Inputs:

```text
user action
realtime event
review task
contradiction
system warning
```

Outputs:

```text
highlight
badge
panel notification
camera suggestion
```

Default policy:

```text
user action > review-critical > data-integrity > high-value realtime > routine realtime > decoration
```

---

# PROMPT #8 — “WOW” SCENARIO A
## Relationship → Evidence → Timeline

```text
Select relationship
       ↓
Graph quiets
       ↓
Relationship Microscope opens
       ↓
Provenance Thread unfolds
       ↓
Evidence source appears
       ↓
Timeline marker lights
       ↓
Evidence Inspector synchronizes
```

User understands in seconds:

```text
WHAT
WHY
WHEN
SOURCE
STATUS
```

---

# PROMPT #8 — “WOW” SCENARIO B
## New Evidence → Graph Impact

```text
New evidence arrives
       ↓
Realtime event
       ↓
Affected subgraph is identified
       ↓
Small localized event wake
       ↓
Evidence Impact corridor appears
       ↓
Investigator chooses Review Changes
```

No random pulsing.

---

# PROMPT #8 — “WOW” SCENARIO C
## Contradiction Discovery

```text
Select relationship
       ↓
WHY?
       ↓
Two source branches appear
       ↓
Timeline mismatch visible
       ↓
Contradiction panel opens
       ↓
Investigator compares claims
```

The graph communicates disagreement rather than pretending certainty.

---

# PROMPT #8 — “WOW” SCENARIO D
## Investigation Evolution

```text
Scene at T1
      ↓
Scrub timeline
      ↓
Graph diff
      ↓
New relationship appears
      ↓
Evidence source is revealed
      ↓
Processing run is shown
      ↓
Review status is shown
```

This demonstrates why the graph matters.

---

# PROMPT #8 — “WOW” SCENARIO E
## Face Trace / Media Provenance

```text
Select candidate
       ↓
Source frame
       ↓
Detection
       ↓
Track
       ↓
Embedding
       ↓
Vector candidate
       ↓
Temporal/media context
       ↓
Human review
```

Never collapse the workflow into:

```text
FACE → PERSON
```

---

# PROMPT #8 — UX FAILURE CONDITIONS

Reject the implementation if:

```text
3D looks impressive but graph is fake
camera moves unexpectedly
user cannot tell why something is highlighted
provenance is decorative
realtime is simulated
missing data is rendered as certainty
hypothesis looks like fact
candidate looks confirmed
stale graph looks current
restricted data leaks through graph topology
```

---

# PROMPT #8 — FINAL INTERACTION LAW

**3D is the navigation medium. Evidence is the authority. Neo4j is the graph engine. FastAPI is the security boundary. PostgreSQL remains the authoritative forensic domain store. Human review controls consequential interpretations.**

The visual system must make investigation faster without making conclusions stronger than the evidence.

