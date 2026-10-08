# CRIMEKIT — NEO4J PRODUCTION SETUP
# MASTER IMPLEMENTATION PROMPT
## Prompt #4 — Production Neo4j + Official Neo4j MCP + Google Antigravity + CrimeKit 3D Knowledge Graph
### Role: Principal Neo4j Architect • Staff Backend Engineer • MCP Architect • Security Architect • Graph Data Engineer • Digital Forensics Architect • 3D Platform Architect • Enterprise DevOps Engineer • Production Reliability Engineer

---

# 0. MISSION

You are now responsible for implementing and hardening the **production Neo4j foundation** for CrimeKit.

CrimeKit is an enterprise-oriented digital-forensics and investigation platform.

The immediate objective is to establish a **secure, production-grade Neo4j data layer** that can power:

```text
CrimeKit
   ↓
Forensic Knowledge Graph
   ↓
3D Knowledge Graph UI
   ↓
Graph Analytics
   ↓
Evidence / Timeline / Provenance
   ↓
AI-assisted investigation
```

A second objective is to connect the development environment to the **official Neo4j MCP server** so that the engineering agent working inside **Google Antigravity** can inspect the schema, query the graph, validate graph data, and safely assist with graph development.

The MCP integration is for **developer/agent access and controlled tooling**.

It must NOT replace the normal CrimeKit application architecture.

The production application should still use:

```text
CrimeKit FastAPI
      ↓
Neo4j official driver / graph service
      ↓
Neo4j
```

while developer/AI tooling can use:

```text
Antigravity
      ↓
Official Neo4j MCP
      ↓
Neo4j
```

This separation is mandatory.

---

# 1. PRIMARY OBJECTIVE

Implement the following target architecture:

```text
                         CRIMEKIT
                            |
                     Next.js / React
                            |
                     Knowledge Graph UI
                            |
                         FastAPI
                            |
          +-----------------+------------------+
          |                                    |
      PostgreSQL                            Redis
   AUTHORITATIVE DATA                   EVENT PIPELINE
          |                                    |
          +----------------+-------------------+
                           |
                    Graph Projection
                           |
                           v
                     NEO4J AURA
                           |
          +----------------+----------------+
          |                |                |
        Cypher            GDS        Vector/Search
          |                |                |
          +----------------+----------------+
                           |
                      Graph Service
                           |
                     3D Graph API
                           |
                      Three.js UI
                           |
             +-------------+-------------+
             |             |             |
          Inspector     Timeline      Evidence
                           |
                     Human Review
```

Developer/AI tooling:

```text
Google Antigravity
       |
       v
Official Neo4j MCP
       |
       v
Neo4j Aura
```

---

# 2. NON-NEGOTIABLE ARCHITECTURAL RULE

## Neo4j is NOT the forensic source of truth.

The responsibilities must remain:

| System | Responsibility |
|---|---|
| PostgreSQL | authoritative CrimeKit domain / forensic records |
| Object storage | original evidence / binary data |
| Redis | realtime events / jobs / transport |
| Neo4j | graph relationships, connected entities, graph context |
| Neo4j GDS | graph analytics / graph algorithms |
| pgvector | existing vector retrieval where appropriate |
| Neo4j vector index | graph-connected vector retrieval where justified |
| FastAPI | application business logic + security boundary |
| Three.js/WebGL layer | 3D graph visualization |
| AI agent | retrieval, reasoning, explanation |
| Neo4j MCP | developer / agent access to Neo4j |

Do not copy the same responsibility into multiple systems unless there is a clear reason.

---

# 3. CRITICAL MCP BOUNDARY

The official Neo4j MCP server is a **developer/tooling interface**.

It must NOT be treated as:

```text
Browser
   ↓
MCP
   ↓
Neo4j
```

and it must NOT be treated as a substitute for:

```text
CrimeKit Backend
   ↓
Neo4j Driver
   ↓
Neo4j
```

The intended separation is:

```text
             DEVELOPMENT / AGENT ACCESS

Antigravity
    ↓
Neo4j MCP
    ↓
Neo4j


             PRODUCTION APPLICATION ACCESS

CrimeKit Frontend
    ↓
CrimeKit FastAPI
    ↓
Neo4j Graph Service
    ↓
Neo4j
```

The application must remain controlled, typed, authorized and auditable.

---

# 4. OFFICIAL NEO4J MCP REQUIREMENT

Use the **official Neo4j MCP server**, not an unofficial replacement, unless there is a repository-specific reason documented and approved.

Current official Neo4j MCP documentation describes the MCP server as a bridge between MCP-compatible clients and Neo4j and supports schema inspection and Cypher-based graph access.

The official server currently provides tools including:

```text
get-schema
read-cypher
write-cypher
list-gds-procedures
```

The official documentation also supports:

```text
STDIO transport
HTTP transport
```

and provides specific configuration for Aura and self-managed Neo4j.

Reference:
https://neo4j.com/docs/mcp/current/

Reference:
https://neo4j.com/docs/mcp/current/installation/

Reference:
https://neo4j.com/docs/mcp/current/quickstart/

Reference:
https://neo4j.com/docs/mcp/current/tools/

Reference:
https://github.com/neo4j/mcp

Use the current official documentation when a configuration detail is version-sensitive.

---

# 5. GOOGLE ANTIGRAVITY MCP REQUIREMENT

The developer environment is expected to use **Google Antigravity** as the coding-agent environment.

Antigravity supports MCP servers.

The repository/project configuration should use the Antigravity-supported MCP configuration mechanism appropriate to the installed version.

Possible project-scoped configuration:

```text
.agents/mcp_config.json
```

Possible global configuration:

```text
~/.gemini/config/mcp_config.json
```

Do not assume both should be modified.

Inspect the actual Antigravity environment first.

Use the project-scoped configuration when it is appropriate and supported.

---

# 6. MCP CONNECTION STRATEGY

Prefer the simplest secure configuration that works with the actual Neo4j deployment.

For Neo4j Aura, the official Neo4j MCP quickstart documents an instance MCP URL pattern similar to:

```text
https://<INSTANCE_ID>.mcp-instances.neo4j.io
```

The actual URI must come from the user's Neo4j Aura instance.

Do NOT invent the instance ID.

Do NOT hardcode credentials.

Do NOT commit secrets.

---

# 7. AURA TOOL AUTHENTICATION

For Aura MCP connections, inspect whether **Tool authentication** is enabled for the organization/instance as required by the current Neo4j documentation.

Follow the current official documentation rather than relying on an old MCP configuration copied from an earlier project.

---

# 8. MCP READ-ONLY DEFAULT

For normal development graph inspection, prefer read-only MCP access.

Conceptual policy:

```text
Development inspection
        ↓
Neo4j MCP
        ↓
READ ONLY
```

Writes must be separately controlled.

The official Neo4j MCP documentation notes that `NEO4J_READ_ONLY=true` disables write tools for configurations using that mode.

Do not enable arbitrary AI-generated production writes merely because the MCP server supports a write tool.

---

# 9. PRODUCTION WRITE SAFETY

Do NOT let an LLM freely mutate production forensic graph data.

Never allow a general AI assistant to execute arbitrary:

```cypher
CREATE
MERGE
DELETE
DETACH DELETE
SET
DROP
CREATE INDEX
DROP INDEX
CREATE CONSTRAINT
DROP CONSTRAINT
```

against production merely because the MCP server exposes write capabilities.

Preferred:

```text
AI / MCP
   ↓
READ / INSPECT
   ↓
Human review
   ↓
Controlled application mutation
   ↓
Graph projection
```

Forensic graph writes should generally originate from the CrimeKit application/projection system.

---

# 10. MCP USE CASES

The MCP connection should enable Antigravity to perform safe development tasks such as:

```text
Inspect graph schema
Inspect labels
Inspect relationship types
Inspect property keys
Read graph samples
Validate constraints
Validate indexes
Run bounded read queries
Inspect GDS availability
Debug projection results
Validate graph consistency
Investigate graph query performance
```

It should NOT become a shortcut for bypassing CrimeKit's architecture.

---

# 11. REPOSITORY-FIRST RULE

Before changing any code:

1. Inspect repository structure.
2. Inspect existing Neo4j integration.
3. Inspect environment files.
4. Inspect Docker configuration.
5. Inspect FastAPI graph code.
6. Inspect graph models.
7. Inspect existing Knowledge Graph UI.
8. Inspect existing database migration strategy.
9. Inspect existing authentication.
10. Inspect existing deployment.
11. Inspect existing MCP configuration if any.
12. Inspect existing Antigravity configuration if present.

Do not create duplicate clients or duplicate graph layers.

---

# 12. AUDIT EXISTING NEO4J DEPENDENCIES

Find:

```text
neo4j
neo4j-driver
neo4j-mcp
neo4j-mcp-server
mcp
graphdatascience
GDS
```

Classify:

```text
used
unused
partial
mock
development-only
production
obsolete
```

---

# 13. AUDIT CURRENT GRAPH CLIENT

Find where the backend currently connects to Neo4j.

Determine:

```text
URI
username
database
driver
connection pool
timeouts
retries
TLS
health checks
```

Report current implementation before modifying it.

---

# 14. DO NOT CREATE TWO NEO4J CLIENTS

If CrimeKit already has a working Neo4j driver:

```text
reuse / harden
```

Do not create:

```text
neo4j_client.py
graph_client.py
database_client.py
neo4j_service.py
```

all independently connecting to the same database.

Create one clear abstraction.

---

# 15. NEO4J CONFIGURATION

Use environment-driven configuration.

Conceptual variables:

```text
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
NEO4J_DATABASE
```

Optional:

```text
NEO4J_MAX_CONNECTION_POOL_SIZE
NEO4J_CONNECTION_TIMEOUT
NEO4J_CONNECTION_ACQUISITION_TIMEOUT
NEO4J_MAX_CONNECTION_LIFETIME
NEO4J_QUERY_TIMEOUT
```

Use only the variables that the actual Neo4j driver/version supports.

Do not invent unsupported names.

---

# 16. SECRET MANAGEMENT

Never put real credentials into:

```text
source code
git
README
frontend
logs
screenshots
client-side environment
```

Use:

```text
.env.local
development secret store
deployment secret configuration
```

consistent with the existing CrimeKit environment.

---

# 17. FRONTEND SECURITY

The frontend must NEVER receive:

```text
NEO4J_PASSWORD
NEO4J_USERNAME
private Bolt URI
MCP credentials
```

The frontend receives only authorized application-level API results.

---

# 18. NEO4J AURA PRODUCTION CONNECTION

For Aura:

```text
CrimeKit Backend
      ↓
secure Neo4j connection
      ↓
Aura
```

Use the connection URI generated by the Aura instance.

Do not hardcode:

```text
bolt://localhost:7687
```

for production.

Local development may use local Neo4j where appropriate.

---

# 19. DATABASE NAME

Determine the actual Aura database name.

Do not assume:

```text
neo4j
```

is always the application database.

Make it configurable.

---

# 20. CONNECTION POOL

Production backend should use driver pooling appropriately.

Audit:

- pool size
- acquisition timeout
- connection lifetime
- idle management
- retry behavior
- shutdown

Do not oversize the pool relative to:

- API concurrency
- Neo4j capacity
- VM/container resources

---

# 21. TRANSACTION MANAGEMENT

Graph mutations should occur in controlled transactions.

Use:

```text
read transaction
write transaction
```

appropriately.

Do not open unmanaged long-lived sessions for ordinary requests.

---

# 22. QUERY TIMEOUTS

Every expensive graph operation should have a bounded timeout.

Especially:

```text
path finding
community detection
large expansion
similarity
cross-entity exploration
```

A graph query that never returns is a production incident.

---

# 23. RETRY POLICY

Retry transient failures.

Do NOT automatically retry:

```text
syntax error
schema error
authorization failure
invalid data
```

Retry only appropriate transient failures.

Use exponential backoff where appropriate.

---

# 24. HEALTH CHECK

Implement/reuse a backend health check.

It should distinguish:

```text
backend healthy
Neo4j reachable
Neo4j unavailable
```

Do not expose raw database errors to investigators.

---

# 25. GRAPH READINESS CHECK

A stronger readiness check should eventually verify:

```text
Neo4j connectivity
database availability
schema readiness
required constraints
required indexes
```

Do not run expensive analytics during ordinary health checks.

---

# 26. SCHEMA MANAGEMENT

Implement controlled schema management.

Schema responsibilities:

```text
constraints
indexes
ontology version
```

Do not run destructive schema commands automatically when the application boots.

---

# 27. MIGRATION STRATEGY

Prefer versioned migrations or a safe initialization process.

Avoid:

```text
DROP ALL
CREATE ALL
```

as an application startup behavior.

---

# 28. CORE NODE CONSTRAINTS

Based on the repository-confirmed ontology, define uniqueness for stable IDs.

Examples:

```cypher
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person)
REQUIRE p.person_id IS UNIQUE;
```

and equivalent constraints for:

```text
Case
Investigation
Person
Device
Phone
Account
Email
IPAddress
Location
Evidence
Artifact
TimelineEvent
Observation
ProcessingRun
GraphAssertion
```

Only create constraints for labels that actually exist.

---

# 29. CASE ISOLATION

Case boundaries must be explicit.

Where appropriate, graph nodes should have:

```text
case_id
```

or a structurally enforced relationship to an authorized case.

The final design must avoid ambiguous case ownership.

---

# 30. CASE-SAFE GRAPH QUERIES

Every application graph query must be scoped.

Bad:

```cypher
MATCH (p:Person {person_id: $person_id})
RETURN p
```

when a globally unique entity ID is not guaranteed and authorization is not independently enforced.

Better conceptual architecture:

```text
API verifies case access
     ↓
query constrained to case
     ↓
return authorized graph data
```

Use the actual repository's domain key strategy.

---

# 31. CROSS-CASE ACCESS

Do not expose cross-case traversal in ordinary endpoints.

Cross-case queries require:

```text
explicit scope
explicit authorization
explicit audit
explicit purpose
```

---

# 32. NEO4J ROLE / DATABASE PRIVILEGE

Use the least privilege available.

Separate:

```text
application runtime user
developer MCP user
administrator
analytics user
```

where deployment/security requirements justify it.

The MCP developer identity should not automatically have unrestricted production privileges.

---

# 33. MCP CREDENTIAL SEPARATION

Do not assume the same credential should be used for:

```text
CrimeKit backend
```

and:

```text
Antigravity MCP
```

Use separated identities where practical.

---

# 34. OFFICIAL MCP INSTALLATION

If Antigravity needs a local official Neo4j MCP server and the environment supports local MCP:

Use the official package/binary instructions.

The official Neo4j documentation currently documents installation options including:

```text
pip install neo4j-mcp-server
```

and a standalone `neo4j-mcp` binary.

Use the current official instructions and compatible version.

Do not install a similarly named unofficial package.

---

# 35. MCP CONFIGURATION — DO NOT INVENT

Inspect Antigravity's actual MCP configuration schema.

If using a remote Aura MCP endpoint, use the correct Antigravity/official Neo4j MCP format supported by the current versions.

If using stdio, use the correct executable/package invocation.

Do not mix configuration formats from:

```text
VS Code
Cursor
Claude Desktop
Antigravity
```

without verifying compatibility.

---

# 36. ANTIGRAVITY PROJECT MCP CONFIG

Where project-scoped configuration is supported, prefer:

```text
.agents/mcp_config.json
```

for repository-specific development configuration.

Do not commit secrets.

Use placeholders only if the configuration requires a secret.

---

# 37. ANTIGRAVITY GLOBAL MCP CONFIG

If the user's installed Antigravity version requires global configuration, use:

```text
~/.gemini/config/mcp_config.json
```

Do not modify global configuration blindly.

First inspect what already exists.

Merge safely.

Do not overwrite unrelated MCP servers.

---

# 38. MCP SERVER NAMING

Use a clear server name such as:

```text
neo4j-crimekit
```

or an existing project convention.

Avoid ambiguous:

```text
neo4j
```

if multiple Neo4j servers are configured.

---

# 39. MCP SERVER DESCRIPTION

Where configuration supports metadata, identify:

```text
CrimeKit production/development graph
```

and clearly distinguish:

```text
DEV
STAGING
PROD
```

Never accidentally connect the agent to production while intending development.

---

# 40. ENVIRONMENT SAFETY

Use explicit environment names:

```text
CRIMEKIT_NEO4J_ENV=development
```

only if the application already uses such a convention or one is intentionally introduced.

Avoid ambiguous aliases.

---

# 41. PRODUCTION MCP POLICY

For production:

```text
MCP = controlled administrative/developer tool
```

not:

```text
MCP = public application API
```

Do not expose the MCP endpoint to public unauthenticated users.

---

# 42. MCP HTTP SECURITY

If using HTTP transport:

- TLS required in production
- authenticated access required
- access restrictions required
- no anonymous mutation
- network exposure minimized
- logs monitored

Follow current Neo4j official MCP deployment/security guidance.

---

# 43. MCP STDIO SECURITY

If using local stdio:

- use a trusted local executable
- secure environment variables
- avoid secrets in shell history
- restrict local users/processes
- verify executable path

---

# 44. MCP READONLY POLICY

For repository development and investigation graph inspection:

Prefer:

```text
NEO4J_READ_ONLY=true
```

when using a local/self-hosted official MCP configuration.

Where Aura tool-authenticated MCP behavior differs, follow the official Aura MCP flow while still applying the same least-privilege principle.

---

# 45. MCP WRITE POLICY

If a development workflow genuinely needs writes:

1. confirm target environment
2. confirm user authorization
3. back up/recover if necessary
4. use test data first
5. use controlled mutation
6. validate result
7. audit the change

Never make arbitrary production mutations simply because an agent can.

---

# 46. MCP SCHEMA INSPECTION

First MCP test:

```text
get-schema
```

The returned schema must be compared to the CrimeKit ontology.

Identify:

```text
labels
relationships
property keys
```

---

# 47. MCP DATA INSPECTION

Next perform safe bounded reads.

Example conceptual query:

```cypher
MATCH (n)
RETURN labels(n) AS labels, count(*) AS count
ORDER BY count DESC
LIMIT 50
```

Use safe read-only queries and appropriate limits.

---

# 48. MCP CASE INSPECTION

Inspect one development/test case.

Do not dump all case data.

---

# 49. MCP GRAPH VALIDATION

Validate:

```text
Case
Person
Device
IP
Location
Evidence
Artifact
TimelineEvent
```

and relationship presence according to the actual ontology.

---

# 50. MCP PROVENANCE VALIDATION

Inspect representative edges and verify fields such as:

```text
evidence_id
artifact_id
processing_run_id
confidence
observed_at
```

only if the repository schema contains them.

---

# 51. GDS DISCOVERY

Use the official MCP GDS procedure discovery tool where available:

```text
list-gds-procedures
```

This is useful for determining what GDS functionality is available on the connected instance.

Do not assume every GDS algorithm is enabled.

---

# 52. GDS SEPARATION

Remember:

```text
Neo4j persistent application graph
```

is not automatically the same thing as:

```text
GDS in-memory projection
```

Design analytics workflows explicitly.

---

# 53. SCHEMA VALIDATION

Validate required:

```text
constraints
indexes
relationship types
```

before integrating 3D rendering.

---

# 54. INDEX POLICY

Create only justified indexes.

Potential categories:

```text
stable IDs
case lookup
search properties
temporal fields
```

Use full-text and vector indexes only where their retrieval role is clear.

---

# 55. VECTOR INDEX POLICY

If Neo4j vector indexes are used:

- define embedding model/version
- define vector dimensions
- define similarity function
- define source
- define update lifecycle
- preserve provenance

Do not duplicate pgvector data without an explicit reason.

---

# 56. FULL-TEXT SEARCH

Use Neo4j full-text capabilities where graph-connected text retrieval materially improves investigation.

Do not replace CrimeKit's entire search stack automatically.

---

# 57. HYBRID SEARCH

Potential target:

```text
Full text
   +
Vector
   +
Graph neighborhood
   ↓
Investigation context
```

This should remain a later controlled layer.

---

# 58. GRAPH QUERY SAFETY

No production query should use uncontrolled:

```cypher
MATCH (n)-[*]-(m)
```

without a depth limit and appropriate scoping.

---

# 59. PATH QUERIES

Use bounded paths:

```cypher
[*1..3]
```

or an appropriate repository-defined maximum.

Use query limits.

---

# 60. GRAPH EXPANSION

3D expansion must be lazy.

Target:

```text
case overview
   ↓
selected entity
   ↓
1-hop
   ↓
2-hop
```

Do not return the entire graph by default.

---

# 61. API PAYLOAD LIMIT

Do not send:

```text
entire evidence objects
large documents
binary data
```

through graph APIs.

Return:

```text
metadata
IDs
relationships
provenance references
```

and navigate to the relevant evidence subsystem.

---

# 62. GRAPH NODE PAYLOAD

A node returned to the frontend should be compact.

Example conceptual:

```json
{
  "id": "P001",
  "type": "Person",
  "label": "John Smith",
  "status": "UNDER_REVIEW",
  "relationship_count": 12
}
```

Do not include unnecessary sensitive fields.

---

# 63. GRAPH EDGE PAYLOAD

Example conceptual:

```json
{
  "id": "REL001",
  "source": "P001",
  "target": "D001",
  "type": "USES",
  "confidence": 0.94
}
```

Only include available, meaningful fields.

---

# 64. GRAPH PROVENANCE REFERENCE

Do not embed an entire forensic evidence object into an edge.

Use references:

```text
evidence_id
artifact_id
processing_run_id
```

and allow the investigator UI to fetch details.

---

# 65. GRAPH DRIVER ABSTRACTION

Recommended conceptual separation:

```text
router
   ↓
graph service
   ↓
graph repository
   ↓
neo4j driver
```

Do not put Cypher in every FastAPI route.

---

# 66. CYPHER ORGANIZATION

Centralize important queries.

Potential categories:

```text
overview
neighbors
search
path
analytics
provenance
```

Use repository conventions.

---

# 67. QUERY PARAMETERIZATION

Never concatenate user strings into Cypher.

Bad:

```python
query = f"MATCH (n {{name: '{name}'}}) RETURN n"
```

Use parameters.

---

# 68. CYPHER INJECTION

Test:

```text
quotes
braces
special characters
Cypher fragments
malicious input
```

The graph layer must remain safe.

---

# 69. GRAPH API AUTHORIZATION

Before every case-scoped graph operation:

```text
authenticate
↓
authorize case
↓
authorize operation
↓
execute bounded query
```

---

# 70. GRAPH API ERROR MODEL

Use safe application errors:

```text
NOT_FOUND
FORBIDDEN
GRAPH_UNAVAILABLE
GRAPH_QUERY_TIMEOUT
INVALID_REQUEST
```

Do not expose:

```text
Cypher
stack trace
database credentials
internal topology
```

---

# 71. GRAPH STATUS

Expose only safe status:

```text
healthy
degraded
unavailable
syncing
stale
```

where backed by actual system state.

---

# 72. GRAPH PROJECTION

The graph should be populated using the application projection strategy:

```text
PostgreSQL
    ↓
Outbox / event
    ↓
Redis
    ↓
Graph Projection Worker
    ↓
Neo4j
```

If the repository has a different established event mechanism, adapt to it instead of introducing a duplicate bus.

---

# 73. PROJECTION IDEMPOTENCY

Use stable event/relationship IDs.

Repeated event:

```text
E1
E1
```

must not generate duplicate graph records.

---

# 74. GRAPH RECONCILIATION

Implement or prepare reconciliation:

```text
Authoritative data
      ↕
Neo4j projection
```

Detect:

```text
missing node
missing edge
stale edge
wrong property
orphan node
```

---

# 75. GRAPH REBUILD

A graph rebuild must be possible.

Target:

```text
authoritative source
   ↓
projection/rebuild
   ↓
Neo4j
```

This is a key production resilience requirement.

---

# 76. GRAPH VERSION

Support where useful:

```text
ontology_version
projection_version
```

and analytics/model versions separately.

---

# 77. FORENSIC ASSERTION

If a relationship is inferred:

```text
GraphAssertion
```

or an equivalent domain model should distinguish it from an observed fact.

Do not overstate certainty.

---

# 78. RELATIONSHIP LIFECYCLE

Potential states:

```text
PROPOSED
OBSERVED
VERIFIED
DISPUTED
REJECTED
DEPRECATED
```

Only implement statuses actually required by the repository.

---

# 79. CONFIDENCE

If confidence exists:

```text
confidence
confidence_source
confidence_method
```

Do not display fake values.

---

# 80. TEMPORAL DATA

Where supported:

```text
observed_at
first_seen_at
last_seen_at
valid_from
valid_to
```

Use authoritative CrimeKit timestamps.

---

# 81. GRAPH CASE SAMPLE

Create or use a test case containing:

```text
Case
 ├── Person
 ├── Device
 ├── IP Address
 ├── Location
 ├── Evidence
 ├── Artifact
 └── Timeline Event
```

The sample must be explicitly labeled as test/demo data.

---

# 82. MCP VALIDATION SCENARIO

After configuration:

```text
Antigravity
    ↓
Neo4j MCP
    ↓
get-schema
    ↓
read-cypher
    ↓
list-gds-procedures
```

Verify every step.

---

# 83. MCP FAILURE TEST

Intentionally test safe failure cases:

```text
wrong instance
invalid credentials
Neo4j unavailable
MCP process unavailable
network blocked
invalid query
```

The failure must be clear.

---

# 84. ENVIRONMENT MISMATCH TEST

Ensure:

```text
development MCP
```

cannot accidentally point to:

```text
production Neo4j
```

without deliberate configuration.

---

# 85. MCP SERVER HEALTH

Document:

```text
MCP connected
MCP unavailable
Neo4j unavailable
authentication failed
```

inside developer documentation.

Do not expose internal MCP status in the investigator UI unless intentionally designed.

---

# 86. ANTIGRAVITY WORKFLOW

The coding agent should be able to ask:

```text
Inspect CrimeKit Neo4j schema.
```

and use MCP to inspect:

```text
labels
relationship types
properties
```

Then:

```text
Validate the Person → Device relationships.
```

Then:

```text
Find orphan graph records in this development case.
```

All such operations should remain bounded and authorized.

---

# 87. MCP DEVELOPMENT POLICY

The agent should:

```text
inspect
reason
validate
query
report
```

before:

```text
mutate
```

---

# 88. AGENT QUERY POLICY

Prefer high-level instructions:

```text
Inspect the graph schema.
Find all relationship types used by Person nodes.
```

rather than forcing the coding agent to blindly write arbitrary Cypher.

---

# 89. HUMAN-IN-THE-LOOP

For sensitive graph mutations:

```text
agent proposes
↓
human reviews
↓
application executes
```

---

# 90. GRAPH WRITE AUDIT

If a developer-authorized MCP write is performed:

capture:

```text
actor
environment
operation
timestamp
reason
affected entities
```

where the tooling and application governance support such audit.

---

# 91. PRODUCTION APPLICATION WRITE PATH

Preferred:

```text
Forensic pipeline
   ↓
PostgreSQL/domain event
   ↓
Graph projection
   ↓
Neo4j
```

Do not have the 3D UI directly issue graph writes.

---

# 92. 3D GRAPH READ PATH

Preferred:

```text
3D UI
   ↓
FastAPI
   ↓
Graph Service
   ↓
Neo4j
   ↓
normalized graph DTO
   ↓
3D renderer
```

---

# 93. 3D GRAPH PERFORMANCE

The Neo4j layer must support:

```text
small neighborhood queries
progressive expansion
path queries
filters
search
```

without returning unnecessary data.

---

# 94. GRAPH OVERVIEW QUERY

Build a bounded case overview query.

It should return enough context for initial 3D rendering but not the complete database.

---

# 95. GRAPH NEIGHBOR QUERY

Build:

```text
entity
   ↓
neighbors
```

with:

```text
case scope
depth
limit
relationship filter
```

---

# 96. GRAPH SEARCH QUERY

Search must be application-scoped.

Potential:

```text
entity ID
display name
device name
email
IP
evidence reference
```

Use the correct indexes.

---

# 97. GRAPH PATH QUERY

Path query requirements:

```text
source
target
case
max_hops
limit
timeout
```

---

# 98. GDS INTEGRATION

Do not implement every GDS algorithm immediately.

Start with repository-justified analytics.

Likely:

```text
degree centrality
PageRank
betweenness
community detection
shortest path
node similarity
```

Validate actual GDS availability first.

---

# 99. GDS PROVENANCE

Every meaningful graph analytics result should retain:

```text
algorithm
parameters
graph scope
timestamp
version
```

---

# 100. GDS SAFETY

Do not label:

```text
high centrality = criminal
```

Use:

```text
high graph centrality
```

and provide methodology.

---

# 101. NEO4J MCP + GDS

Use MCP's GDS procedure discovery for development visibility.

Do not assume the AI may run unlimited GDS computations.

Analytics must remain bounded.

---

# 102. GRAPH SEARCH + VECTOR

Do not automatically migrate existing pgvector functionality to Neo4j.

Evaluate:

```text
existing pgvector
```

versus:

```text
Neo4j vector index
```

based on actual use case.

Graph-connected vector retrieval may be valuable when semantic matches need immediate graph expansion.

---

# 103. FULL-TEXT + VECTOR + GRAPH

Potential future retrieval architecture:

```text
Question
  ↓
Full-text / vector
  ↓
candidate entities
  ↓
Neo4j neighborhood
  ↓
evidence
  ↓
AI
```

This should be implemented after basic graph correctness is established.

---

# 104. NEO4J MCP AS KNOWLEDGE-GRAPH ENGINEERING ASSISTANT

Antigravity should be able to use MCP for:

```text
schema discovery
query validation
sample data inspection
projection debugging
relationship verification
data quality inspection
GDS discovery
```

This creates a fast development feedback loop.

---

# 105. MCP DOES NOT BUILD THE 3D UI

Important:

```text
Neo4j MCP
```

does NOT replace:

```text
Three.js
FastAPI
React
Graph API
```

It only assists the development/agent layer in accessing Neo4j.

---

# 106. NEO4J DRIVER + MCP COEXISTENCE

Correct architecture:

```text
                 Neo4j
                /     \
               /       \
      FastAPI Driver    MCP
          |              |
      CrimeKit App    Antigravity
```

This is intentional.

---

# 107. GRAPH SCHEMA SOURCE

The ontology from the previous prompt remains the source design.

If the actual repository differs:

```text
repository truth
```

wins over assumptions.

Report schema conflicts.

---

# 108. SCHEMA DRIFT DETECTION

MCP schema inspection should make it possible to compare:

```text
expected ontology
      vs
actual Neo4j schema
```

and detect drift.

---

# 109. GRAPH DRIFT

Detect:

```text
unexpected label
unexpected relationship
missing property
missing constraint
```

---

# 110. GRAPH DATA QUALITY SCRIPT

Where useful, create a safe developer diagnostic that reports:

```text
nodes by label
relationships by type
orphans
missing provenance
missing case IDs
duplicates
```

Do not delete anything.

---

# 111. NO DESTRUCTIVE AUTO-REPAIR

Never automatically:

```text
DELETE duplicates
```

from an AI agent's diagnostic task.

Produce a report first.

---

# 112. GRAPH ADMIN COMMANDS

Administrative mutations should be separate from ordinary graph APIs.

Examples:

```text
schema migration
rebuild projection
reconcile
repair
```

These require explicit authorization.

---

# 113. DEPLOYMENT ENVIRONMENTS

Define:

```text
LOCAL
DEVELOPMENT
STAGING
PRODUCTION
```

where the existing deployment supports them.

Each environment must have separate Neo4j configuration.

---

# 114. PRODUCTION INSTANCE IDENTIFICATION

Make it impossible or difficult to accidentally use production from local development.

Use clear names and environment-specific secrets/configuration.

---

# 115. MCP PROD GUARDRAIL

If connecting Antigravity to production:

require an explicit developer decision and display/log the environment context before any write-capable action.

Default to read-only inspection.

---

# 116. BACKUP / RECOVERY

The Neo4j deployment must have a recovery strategy appropriate to the chosen Aura tier/deployment.

More importantly:

```text
authoritative CrimeKit data
```

must allow graph reconstruction.

---

# 117. DISASTER RECOVERY

Target:

```text
PostgreSQL + object storage
      ↓
graph rebuild
      ↓
Neo4j
```

---

# 118. DATABASE CONSISTENCY

Neo4j is a projection.

If a graph write fails:

```text
authoritative source remains valid
projection retry occurs
```

Do not silently lose the source event.

---

# 119. EVENT IDENTITY

Projection events should have stable:

```text
event_id
case_id
entity_id / relationship_id
event_type
version
```

---

# 120. RELATIONSHIP IDENTITY

A relationship should have a deterministic identity strategy.

Avoid duplicate edges due to repeated projection.

---

# 121. GRAPH TRANSACTION BOUNDARY

If one event creates:

```text
Person
Device
USES
```

prefer atomic graph mutation where appropriate.

Do not leave half-created relationship structures after an ordinary successful projection.

---

# 122. PARTIAL FAILURE

If a batch has 100 relationships and item 67 fails:

- preserve failure information
- retry appropriately
- avoid duplicate successful records
- keep authoritative source intact

---

# 123. PROJECTION OBSERVABILITY

Track:

```text
projection_count
projection_success
projection_failure
projection_retry
projection_lag
```

---

# 124. MCP OBSERVABILITY

Developer tooling should make it possible to identify:

```text
connected server
target environment
database
schema
```

without exposing credentials.

---

# 125. LOGGING

Backend logs should include safe identifiers:

```text
case_id
request_id
operation
duration
```

Do not log:

```text
password
tokens
full evidence
sensitive document contents
```

unless specifically required and protected.

---

# 126. CYPHER LOGGING

Do not log arbitrary Cypher containing sensitive values.

Log:

```text
operation name
query template identifier
duration
result count
```

when practical.

---

# 127. MCP LOGGING

Do not paste secrets into chat/tool requests.

Use environment configuration or secure credentials.

---

# 128. CONNECTION TEST SCRIPT

Create a non-destructive connection diagnostic only if the repository lacks one.

It should verify:

```text
environment loaded
Neo4j reachable
database selected
schema accessible
```

and return a safe result.

---

# 129. SCHEMA BOOTSTRAP

Schema bootstrap should be:

```text
explicit
versioned
repeatable
safe
```

---

# 130. CONSTRAINT VERIFICATION

A deployment check should verify critical constraints exist.

Do not silently create destructive replacements.

---

# 131. INDEX VERIFICATION

Verify required indexes.

---

# 132. SCHEMA MIGRATION FAILURE

If schema migration fails:

```text
stop
report
do not continue with an inconsistent graph schema
```

unless the migration is explicitly designed for partial compatibility.

---

# 133. GRAPH VERSION COMPATIBILITY

Ensure the application expects the graph schema it connects to.

If incompatible:

```text
graph schema incompatible
```

rather than producing corrupt results.

---

# 134. GRAPH API CONTRACT

Define a normalized contract:

```text
nodes[]
edges[]
meta{}
```

with:

```text
case_id
graph_version
generated_at
truncated
```

where appropriate.

---

# 135. GRAPH TRUNCATION

When server limits are reached:

```text
truncated = true
```

must be communicated.

---

# 136. QUERY LIMITS

Use safe defaults for:

```text
max nodes
max edges
max hops
query timeout
```

Actual production values must be benchmarked.

---

# 137. GRAPH QUERY CACHING

If caching is used:

cache keys must include authorization/case context.

Do not leak case data through shared cache.

---

# 138. REALTIME

The graph layer should eventually support:

```text
Redis
 ↓
Graph Projection
 ↓
Neo4j
 ↓
WebSocket
 ↓
3D graph
```

Do not make Neo4j polling the default realtime mechanism unless required.

---

# 139. REALTIME GRAPH UPDATE

A new graph event should:

```text
arrive
 ↓
validate
 ↓
update graph
 ↓
broadcast authorized event
 ↓
3D graph updates
```

---

# 140. REALTIME CASE ISOLATION

WebSocket subscribers must be authorized for the case before events are delivered.

---

# 141. 3D GRAPH SNAPSHOT

The graph API should allow the frontend to build an initial snapshot.

Realtime then updates it incrementally.

---

# 142. GRAPH API + MCP SEPARATION

Never call MCP from the browser.

Never make the frontend depend on Antigravity.

---

# 143. PRODUCTION BUILD SEPARATION

The production application must work when:

```text
Antigravity
```

is closed.

This is a critical acceptance criterion.

---

# 144. DEVELOPER TOOLING SEPARATION

The production application must not depend on:

```text
MCP process running on developer laptop
```

---

# 145. 3D GRAPH DEPENDENCY SEPARATION

The graph UI must work in a deployed CrimeKit environment without Antigravity.

---

# 146. NEO4J MCP TEST MATRIX

Test:

| Test | Expected |
|---|---|
| MCP starts | success |
| Schema request | success |
| Read query | success |
| Unauthorized target | denied |
| Write while read-only | unavailable/blocked |
| Invalid query | safe error |
| Neo4j down | clear unavailable state |
| Antigravity restart | reconnect |
| Wrong environment | detected |

---

# 147. PRODUCTION NEO4J TEST MATRIX

Test:

| Test | Expected |
|---|---|
| Backend connection | success |
| Health check | success |
| Case query | scoped |
| Neighbor query | bounded |
| Path query | bounded |
| Projection | idempotent |
| Failure | retry |
| Rebuild | reproducible |
| Unauthorized case | denied |

---

# 148. SECURITY ACCEPTANCE TEST

Must prove:

```text
User A cannot retrieve Case B
User A cannot expand Case B
User A cannot receive Case B WebSocket events
User A cannot export Case B graph
Developer MCP cannot accidentally mutate production without explicit privilege
Frontend cannot access Neo4j credentials
```

---

# 149. DATA INTEGRITY ACCEPTANCE TEST

Must prove:

```text
PostgreSQL authoritative record
        ↕
Neo4j projection
```

is consistent for representative test cases.

---

# 150. FORENSIC PROVENANCE ACCEPTANCE TEST

Select a graph relationship and prove:

```text
relationship
 ↓
evidence
 ↓
artifact
 ↓
processing run
```

where applicable.

---

# 151. GRAPH AUDIT ACCEPTANCE TEST

The investigator must be able to understand:

```text
what
where
when
why
source
confidence
```

for important relationships.

---

# 152. 3D READINESS ACCEPTANCE TEST

Graph API should provide data suitable for:

```text
3D node rendering
3D edge rendering
selection
expansion
focus
path highlighting
```

---

# 153. GRAPH PAYLOAD PERFORMANCE

Measure payload size.

Do not send:

```text
large unnecessary properties
```

to the browser.

---

# 154. NEO4J QUERY PERFORMANCE

Benchmark:

```text
case overview
entity lookup
neighbor expansion
path search
search
analytics
```

---

# 155. QUERY PROFILE

Do not use expensive `PROFILE` queries in normal production execution.

Performance analysis should occur in controlled developer/staging environments.

---

# 156. INDEX VALIDATION

Use actual query plans to determine whether indexes are effective.

Do not assume an index is useful merely because it exists.

---

# 157. GRAPH ANALYTICS RESOURCE CONTROL

Heavy analytics can consume resources.

Use:

```text
bounded scope
appropriate graph projection
controlled execution
```

---

# 158. GDS PRODUCTION POLICY

Do not run expensive global analytics on every page load.

Prefer:

```text
explicit analysis
background job
cached result
scheduled analysis
```

when appropriate.

---

# 159. 3D GRAPH INITIALIZATION

Initial graph load should favor:

```text
high-value
small
scoped
```

data.

---

# 160. GRAPH VIEW MODES

The production graph foundation should support future:

```text
Overview
Local neighborhood
Path
Timeline
Evidence
Provenance
Community
Analytics
```

---

# 161. MCP GRAPH EXPLORATION FOR ANTIGRAVITY

The coding agent should be able to perform:

```text
"Inspect the schema."
"Count nodes by label."
"Show relationship types."
"Check whether provenance exists."
"Find orphaned entities in test case."
"Check whether indexes exist."
```

without requiring manual database-console work every time.

---

# 162. AGENT GUARDRAILS

When an AI agent uses MCP:

1. identify target environment
2. identify database
3. inspect schema
4. use read-only operations by default
5. bound queries
6. avoid sensitive dumps
7. summarize findings
8. request explicit approval before mutation

---

# 163. AGENT RESPONSE STYLE

For graph diagnostics, the agent should report:

```text
Finding
Evidence
Impact
Recommended action
```

not:

```text
I think this might be...
```

when the graph provides definitive evidence.

---

# 164. NO UNBOUNDED DATA DUMPS

Never ask MCP to return:

```text
all nodes
all evidence
all properties
```

for a production-scale case.

Use counts, samples and bounded queries.

---

# 165. GRAPH SAMPLE STRATEGY

For inspection:

```text
counts first
 ↓
schema
 ↓
sample
 ↓
targeted query
```

rather than:

```text
dump everything
```

---

# 166. DEVELOPMENT GRAPH DATA

If using synthetic demo data:

label it clearly:

```text
DEMO / TEST
```

and never confuse it with real evidence.

---

# 167. PRODUCTION GRAPH DATA

The production graph must be populated from the authorized CrimeKit pipeline.

---

# 168. NEO4J DATABASE OBJECTS TO AUDIT

Inspect:

```text
nodes
relationships
constraints
indexes
procedures
GDS availability
database status
```

---

# 169. NEO4J AURA INSTANCE AUDIT

Confirm:

```text
instance identity
region
tier
database
availability
authentication
```

but do not change infrastructure during this prompt unless explicitly required.

---

# 170. AURA UI / MCP

Where supported, use Aura's documented MCP/tool authentication flow for the connected instance.

Do not copy credentials from screenshots or commit them.

---

# 171. NEO4J MCP TOOL AUDIT

Verify available tools:

```text
get-schema
read-cypher
write-cypher
list-gds-procedures
```

Actual available tools may vary by version/configuration.

Record the actual output.

---

# 172. READ-ONLY MCP VALIDATION

The default developer validation should be:

```text
get-schema
read-cypher
list-gds-procedures
```

No writes.

---

# 173. WRITE MCP VALIDATION

Do not test writes against production.

If write behavior must be tested:

```text
local/dev database only
```

with disposable test data.

---

# 174. MCP VERSION PINNING

Record the installed MCP version.

Avoid uncontrolled latest-version drift in production engineering environments when reproducibility matters.

---

# 175. MCP UPGRADE POLICY

Before upgrading:

```text
read release notes
test config
test tool availability
test query behavior
```

---

# 176. NEO4J DRIVER VERSION

Record the backend driver version.

Check compatibility with:

```text
Neo4j server
Aura
Python version
FastAPI runtime
```

---

# 177. APOC / GDS

Do not assume APOC or GDS availability.

Check the actual instance.

---

# 178. SCHEMA SAMPLE SIZE

If MCP configuration exposes schema sampling:

use a bounded sample appropriate to the environment.

Do not use giant schema sampling unnecessarily.

---

# 179. MCP TELEMETRY

Follow the organization/project privacy and security policy.

If telemetry can be disabled and policy requires it, configure appropriately.

Do not disable required enterprise observability without authorization.

---

# 180. NETWORK SECURITY

For production:

```text
Internet
   |
   v
FastAPI
   |
   v
Neo4j Aura secure endpoint
```

Do not expose Neo4j directly to browsers.

---

# 181. MCP NETWORK SECURITY

If a remote MCP endpoint is used:

- secure transport
- authentication
- network restriction where possible
- no public write access

---

# 182. ENVIRONMENT DOCUMENTATION

Document:

```text
how to connect local
how to connect development
how to connect staging
how to connect production
how to use MCP
```

Do not include secrets.

---

# 183. DEVELOPER README

Include safe instructions such as:

```text
Prerequisites
Neo4j connection
MCP setup
Antigravity setup
verification
troubleshooting
```

---

# 184. TROUBLESHOOTING GUIDE

Document failures such as:

```text
MCP not visible
MCP failed to start
authentication failed
Neo4j unavailable
wrong database
schema missing
GDS unavailable
```

---

# 185. MCP CONFIG RECOVERY

If `.agents/mcp_config.json` already exists:

- read it
- preserve unrelated servers
- merge carefully
- do not overwrite user configuration

---

# 186. GLOBAL CONFIG RECOVERY

If modifying `~/.gemini/config/mcp_config.json`:

- back up logically if needed
- parse JSON
- merge
- validate JSON
- preserve unrelated servers

Do not replace the entire file.

---

# 187. CONFIG VALIDATION

After editing MCP configuration:

```text
parse JSON
 ↓
verify schema
 ↓
restart/reload Antigravity MCP
 ↓
verify connected server
```

---

# 188. NO SECRETS IN GIT

Ensure:

```text
.agents/mcp_config.json
```

does not accidentally contain secrets if the repository convention is to commit project config.

Use secure placeholders or supported environment substitution.

---

# 189. GITIGNORE

Inspect `.gitignore`.

Ensure local secret/config files are not accidentally committed.

Do not blindly ignore configuration that the team needs.

---

# 190. PRODUCTION CONFIG CHECK

Confirm production environment variables are injected at deploy time.

---

# 191. DATABASE LAYER TEST

Build an integration test that:

```text
connects
queries
closes
```

without leaking secrets.

---

# 192. DRIVER SHUTDOWN

Ensure the Neo4j driver closes cleanly during application shutdown.

---

# 193. ASYNC / SYNC COMPATIBILITY

Use the correct Neo4j driver mode for the existing FastAPI architecture.

Do not mix blocking database calls into async request paths without a reason.

---

# 194. CONNECTION LEAK TEST

Run repeated graph requests and ensure:

```text
connections stable
no unbounded growth
no session leak
```

---

# 195. CONCURRENCY TEST

Test concurrent:

```text
graph reads
expansions
searches
```

and confirm stable behavior.

---

# 196. GRAPH PROJECTION CONCURRENCY

Test concurrent projection events for the same entity/relationship.

The final state must be deterministic.

---

# 197. ORDERING

Where multiple events affect the same relationship:

use domain/event versioning as appropriate.

Do not rely blindly on arrival order.

---

# 198. GRAPH CONSISTENCY

After projections:

```text
counts
relationships
provenance
```

should match authoritative expectations.

---

# 199. DATA CLEANUP

Do not delete development graph data automatically unless the command is explicitly a development cleanup task.

---

# 200. SCHEMA RESET

If needed for local development, provide a clearly separated development-only reset process.

Never reuse it in production.

---

# 201. PRODUCTION READINESS SCORE

At the end score:

```text
Neo4j connectivity /10
Schema /10
Case isolation /10
Provenance /10
Projection /10
Query safety /10
Security /10
MCP integration /10
GDS readiness /10
Realtime readiness /10
3D API readiness /10
Observability /10
Recovery /10
Testing /10
Documentation /10
```

Support every score with evidence.

---

# 202. FINAL IMPLEMENTATION CHECKLIST

Before declaring Prompt #4 complete:

```text
[ ] Existing Neo4j integration audited
[ ] Single backend Neo4j abstraction identified
[ ] Aura configuration verified
[ ] Secure credentials configured
[ ] Frontend has no Neo4j credentials
[ ] Case isolation enforced
[ ] Stable ID constraints implemented/verified
[ ] Required indexes implemented/verified
[ ] Bounded graph queries established
[ ] Projection path verified
[ ] Idempotency verified
[ ] Provenance verified
[ ] Health check verified
[ ] Failure handling verified
[ ] MCP official server verified
[ ] Antigravity MCP configuration verified
[ ] MCP schema query verified
[ ] MCP read query verified
[ ] GDS discovery verified
[ ] MCP write disabled or tightly controlled
[ ] Production MCP guardrails documented
[ ] Config secrets protected
[ ] Tests passing
[ ] Developer documentation updated
```

---

# 203. REQUIRED DELIVERABLES

Produce/update only what the actual repository requires.

Expected categories:

## Backend

```text
Neo4j client
Graph repository
Graph service
configuration
health check
schema/migrations
tests
```

## MCP

```text
Antigravity project MCP configuration
developer setup documentation
MCP verification procedure
security policy
```

## Database

```text
constraints
indexes
schema version
```

## Documentation

```text
Neo4j setup
MCP setup
troubleshooting
production notes
```

Do not create duplicate documentation systems.

---

# 204. REQUIRED MCP CONFIGURATION EXAMPLE

Include a clearly labeled example in developer documentation, but replace placeholders with actual values only in the user's local secure environment.

Conceptual Aura configuration based on the current official Neo4j MCP documentation:

```json
{
  "servers": {
    "neo4j-mcp": {
      "type": "http",
      "url": "https://<INSTANCE_ID>.mcp-instances.neo4j.io"
    }
  }
}
```

The exact configuration key names may differ by MCP client/version.

**For Antigravity, inspect its current configuration schema first.**

Do not blindly paste a VS Code configuration into Antigravity.

---

# 205. LOCAL / SELF-HOSTED MCP EXAMPLE

Where local stdio MCP is appropriate, the official Neo4j MCP documentation currently documents a Python entry point similar to:

```json
{
  "servers": {
    "neo4j": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "neo4j_mcp_server"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "<LOCAL_SECRET>",
        "NEO4J_DATABASE": "neo4j",
        "NEO4J_READ_ONLY": "true"
      }
    }
  }
}
```

Treat this as a **reference shape**, not a guaranteed Antigravity-ready configuration.

Verify the current Antigravity and Neo4j MCP schemas before use.

---

# 206. OFFICIAL TOOL SAFETY

Current official Neo4j MCP documentation distinguishes:

```text
get-schema
read-cypher
write-cypher
list-gds-procedures
```

and supports a read-only mode that hides write tools.

Use the read-only mode as the default for development graph inspection.

---

# 207. MCP QUERY SAFETY

The official read-Cypher tool is designed to reject write/admin/schema operations in read mode, but this does not remove the need for application-level safety and least privilege.

Treat MCP as a privileged engineering tool.

---

# 208. ANTIGRAVITY CONNECTION SUCCESS CRITERIA

Inside Antigravity:

```text
MCP server visible
        ↓
connected
        ↓
Neo4j schema readable
        ↓
bounded query succeeds
```

The exact UI labels may vary by Antigravity version.

---

# 209. SUCCESSFUL MCP DEMO

Demonstrate:

```text
Antigravity:
"Inspect the CrimeKit graph schema."

MCP:
get-schema

Result:
labels
relationships
property keys
```

Then:

```text
Antigravity:
"Count entities in development case CASE-TEST-001."

MCP:
read-cypher

Result:
bounded count
```

Then:

```text
Antigravity:
"List available GDS procedures."

MCP:
list-gds-procedures

Result:
available procedures
```

Do not dump the entire graph.

---

# 210. MCP + 3D DEVELOPMENT LOOP

The resulting developer workflow should be:

```text
Antigravity
    |
    v
Ask about graph schema
    |
    v
Neo4j MCP
    |
    v
Inspect actual graph
    |
    v
Implement FastAPI query
    |
    v
Run API test
    |
    v
3D UI
    |
    v
Validate visualization
```

This creates a rapid evidence-backed development loop.

---

# 211. MCP + ONTOLOGY LOOP

Use:

```text
Ontology design
   ↓
Neo4j schema
   ↓
MCP get-schema
   ↓
compare
   ↓
fix drift
```

---

# 212. MCP + PROJECTION LOOP

Use:

```text
PostgreSQL test event
   ↓
projection
   ↓
Neo4j
   ↓
MCP read
   ↓
verify node/edge
```

---

# 213. MCP + PROVENANCE LOOP

Use:

```text
relationship
   ↓
MCP read
   ↓
provenance
   ↓
evidence ID
   ↓
artifact ID
```

---

# 214. MCP + GDS LOOP

Use:

```text
MCP
 ↓
list GDS procedures
 ↓
select justified algorithm
 ↓
run bounded development analysis
 ↓
verify result
 ↓
integrate API
 ↓
3D visualization
```

---

# 215. NO MCP DEPENDENCY IN DEPLOYMENT

The production CrimeKit web application must continue to work when:

```text
Antigravity is closed
MCP is offline
developer laptop is offline
```

---

# 216. NO MCP IN FRONTEND

Never bundle:

```text
MCP client credentials
Neo4j credentials
MCP endpoint
```

into browser JavaScript.

---

# 217. NO MCP IN PUBLIC API

Do not expose:

```text
/api/mcp
```

or equivalent merely so the frontend can query the graph.

---

# 218. AI AGENT FUTURE INTEGRATION

A future CrimeKit AI agent may use controlled graph tools.

Preferred:

```text
find_entity
get_neighbors
find_path
get_evidence
get_timeline
get_provenance
```

instead of:

```text
arbitrary_cypher
```

for normal investigators.

---

# 219. AI GRAPH TOOL AUTHORIZATION

Graph tools must inherit case authorization.

AI must not have a broader graph scope than the authenticated investigator.

---

# 220. GRAPH AI EXPLANATION

The AI should return:

```text
Finding
Graph path
Evidence
Provenance
Confidence
Caveat
```

---

# 221. GRAPH ETHICS

Do not convert:

```text
centrality
risk
similarity
anomaly
association
```

into:

```text
guilt
criminality
certainty
```

---

# 222. GRAPH TRUST

A graph relationship should be explainable to:

```text
investigator
reviewer
auditor
engineer
```

---

# 223. GRAPH DATA MODEL CONFIDENCE

If entity resolution is uncertain:

```text
candidate relationship
```

not:

```text
confirmed identity
```

---

# 224. INVESTIGATION SAFETY

The system is an assistive investigation platform.

Human investigators remain responsible for decisions.

---

# 225. OBSERVABILITY

Monitor:

```text
Neo4j availability
query latency
query failures
projection lag
projection failures
MCP developer access status
GDS execution where monitored
```

Do not expose internal security information publicly.

---

# 226. PRODUCTION ALERTS

Potential alerts:

```text
Neo4j unavailable
high graph query latency
projection lag
projection failures
schema mismatch
unexpected relationship growth
```

Use the existing monitoring stack if one exists.

---

# 227. GRAPH CAPACITY

Do not claim a specific graph size is supported without measuring the actual deployment tier and query/render architecture.

Separate:

```text
persisted graph size
```

from:

```text
simultaneously rendered graph size
```

---

# 228. 3D RENDERING LIMIT

The 3D client should render only a bounded subset.

Neo4j may contain:

```text
100k+
```

records while the UI may show only:

```text
100–500
```

at a time depending on measured performance.

Do not treat these as fixed production limits until benchmarked.

---

# 229. GRAPH QUERY LAYER FOR 3D

Design API operations to return:

```text
overview graph
local graph
path graph
evidence graph
timeline graph
```

rather than a single unlimited endpoint.

---

# 230. GRAPH UI SOURCE

The 3D UI gets normalized API data.

It never parses raw Neo4j driver output.

---

# 231. GRAPH ERROR UX

When Neo4j is unavailable:

```text
Knowledge graph temporarily unavailable.
Retry.
```

Do not break the case workspace.

---

# 232. GRAPH STALE UX

If the graph projection is stale:

```text
Graph last updated:
...
```

where the data supports it.

---

# 233. MCP ERROR UX

For developers:

```text
Neo4j MCP unavailable
Check:
- MCP server
- target instance
- authentication
- network
```

---

# 234. DOCUMENTATION SOURCE OF TRUTH

For MCP-specific configuration, current official Neo4j documentation is authoritative over stale copied examples.

For Antigravity MCP configuration, current Google/Antigravity documentation is authoritative over older examples.

---

# 235. REFERENCES

Official Neo4j MCP:

https://neo4j.com/docs/mcp/current/

Official Neo4j MCP installation:

https://neo4j.com/docs/mcp/current/installation/

Official Neo4j MCP quickstart:

https://neo4j.com/docs/mcp/current/quickstart/

Official Neo4j MCP tools:

https://neo4j.com/docs/mcp/current/tools/

Official Neo4j MCP configuration:

https://neo4j.com/docs/mcp/current/configuration/

Official Neo4j MCP GitHub:

https://github.com/neo4j/mcp

Google Antigravity MCP guidance:

https://developers.google.com/knowledge/mcp

Use these references for current implementation verification.

---

# 236. REQUIRED FINAL REPORT

At the end, produce:

## 1. Current Neo4j Status

```text
Connection:
Schema:
Data:
Projection:
Security:
```

## 2. Implementation Completed

```text
file
change
purpose
```

## 3. MCP Status

```text
Official server:
Antigravity:
Configuration:
Authentication:
Read-only:
Validation:
```

## 4. Schema Status

```text
constraints
indexes
labels
relationships
```

## 5. Security Status

```text
credentials
case isolation
privileges
MCP
frontend exposure
```

## 6. Projection Status

```text
source
event
worker
Neo4j
reconciliation
```

## 7. Testing

```text
connection
query
security
projection
MCP
GDS
```

## 8. Remaining Risks

Only real repository-supported risks.

## 9. Production Readiness

```text
READY
READY AFTER FIXES
NOT READY
```

with evidence.

---

# 237. REQUIRED OUTPUT — MCP VERIFICATION TABLE

Produce:

| Check | Expected | Actual | Status |
|---|---|---|---|
| MCP server installed | | | |
| Antigravity sees server | | | |
| Authentication | | | |
| get-schema | | | |
| read-cypher | | | |
| list-gds-procedures | | | |
| read-only protection | | | |
| correct environment | | | |
| production guardrail | | | |

---

# 238. REQUIRED OUTPUT — NEO4J CHECKLIST

Produce:

| Area | Result |
|---|---|
| Aura connectivity | |
| TLS/security | |
| Credentials | |
| Driver | |
| Pooling | |
| Timeouts | |
| Constraints | |
| Indexes | |
| Case isolation | |
| Provenance | |
| Projection | |
| Reconciliation | |
| Health checks | |
| Metrics | |
| Recovery | |
| Tests | |

---

# 239. REQUIRED OUTPUT — FILE CHANGE MAP

Produce:

```text
EXISTING — KEEP
EXISTING — MODIFY
NEW — REQUIRED
NEW — OPTIONAL
DO NOT TOUCH
```

Every item must include an actual repository path.

---

# 240. REQUIRED OUTPUT — ANTIGRAVITY HANDOFF

Generate a concise developer procedure:

```text
1. Open CrimeKit in Antigravity
2. Open MCP configuration
3. Verify neo4j-crimekit server
4. Verify target environment
5. Run get-schema
6. Run bounded read query
7. Inspect GDS procedures
8. Continue graph implementation
```

Use the current Antigravity UI/configuration discovered during implementation.

---

# 241. FINAL PRODUCTION ARCHITECTURE

The final target is:

```text
                     CRIMEKIT

             Next.js / React UI
                     |
                     v
               FastAPI API
                     |
          +----------+----------+
          |                     |
     PostgreSQL              Redis
     authoritative           events
          |                     |
          +----------+----------+
                     |
               Graph Projection
                     |
                     v
                 Neo4j Aura
                     |
       +-------------+-------------+
       |             |             |
     Cypher          GDS        Vector/Search
       |             |             |
       +-------------+-------------+
                     |
                Graph Service
                     |
                     v
             Normalized Graph API
                     |
                     v
              Three.js / 3D Graph
                     |
       +-------------+-------------+
       |             |             |
   Inspector      Timeline      Evidence
                     |
                     v
                 AI Layer
                     |
                     v
               Human Review


DEVELOPER / AGENT PLANE

               Google Antigravity
                       |
                       v
               Official Neo4j MCP
                       |
                       v
                   Neo4j Aura
```

---

# 242. FINAL PRINCIPLE

The correct architecture is:

```text
Neo4j
    =
forensic relationship intelligence

Neo4j MCP
    =
developer/agent graph access

FastAPI
    =
production application access

PostgreSQL
    =
authoritative CrimeKit record

3D Graph
    =
investigator visualization

AI
    =
assistance + reasoning

Human
    =
final investigative judgement
```

Do not collapse these responsibilities.

---

# 243. FINAL DIRECTIVE

Do the implementation as an enterprise production engineer.

Before changing anything:

```text
inspect
verify
plan
```

Then:

```text
implement
test
measure
harden
```

Do not:

```text
guess
copy blindly
hardcode
expose secrets
bypass authorization
allow unbounded Cypher
allow arbitrary production writes
make frontend-to-Neo4j connections
treat MCP as the application API
treat graph analytics as proof
treat AI output as evidence
```

The Neo4j integration is successful only when all of the following coexist cleanly:

```text
                AUTHORITATIVE CRIMEKIT DATA
                           |
                           v
                    GRAPH PROJECTION
                           |
                           v
                      NEO4J AURA
                       /       \
                      /         \
             CrimeKit API       MCP
                 |                |
                 v                v
             Production       Antigravity
                 |                |
                 v                v
              3D UI          Developer Agent
                 |
                 v
       Evidence / Timeline / Provenance
                 |
                 v
             Human Review
```

The result must be a **secure, explainable, scalable, forensic-grade Neo4j foundation** that is ready to power the next stages:

```text
Prompt #5 — Graph Projection Engine
Prompt #6 — Graph API
Prompt #7 — 3D Graph Engine
Prompt #8 — Reference UI
Prompt #9 — 3D Interaction System
Prompt #10 — Entity/Relationship Inspector
Prompt #11 — Search/Filter/Progressive Loading
Prompt #12 — GDS Intelligence
Prompt #13 — Realtime Graph
Prompt #14 — Forensic Provenance + Security
Prompt #15 — Performance
Prompt #16 — Final Production QA
```

Do not proceed by making the graph merely "look connected."

Build the graph so that:

> **every important relationship has a legitimate source, every query has a controlled scope, every developer connection has the correct environment, every MCP operation is governed, every visual result can be traced to structured graph data, and the entire graph can be reconstructed from authoritative CrimeKit data.**
