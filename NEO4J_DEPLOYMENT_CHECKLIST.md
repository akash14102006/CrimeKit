# CRIMEKIT NEO4J DEPLOYMENT CHECKLIST
**Document Version:** 1.0.0  
**Target Engine:** Neo4j 5.x (Neo4j AuraDB Professional / Enterprise or Self-Hosted EC2)  
**Client Library:** Official Python `neo4j` Driver 5.28.0  

---

## 1. Engine & Network Specifications

* **Version:** Neo4j 5.x.
* **Port:** 7687 (Bolt protocol) and 7474 (HTTP Browser / Healthcheck).
* **Connection URI:** `NEO4J_URI=bolt://neo4j:7687` or `neo4j+s://<dbid>.databases.neo4j.io` (AuraDB).
* **Authentication:** `NEO4J_USER=neo4j`, `NEO4J_PASSWORD=<STRONG_PASSWORD>`.
* **Database Name:** `neo4j` (default database).

---

## 2. Graph Schema & Constraints

CrimeKit's knowledge graph client is implemented in `backend/app/kg.py`. Run the following Cypher queries upon initial database provisioning to enforce uniqueness and index performance:

```cypher
// 1. Evidence and Case Node Constraints
CREATE CONSTRAINT case_id_unique IF NOT EXISTS
FOR (c:Case) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT evidence_id_unique IF NOT EXISTS
FOR (e:Evidence) REQUIRE e.id IS UNIQUE;

// 2. Entity Node Constraints (Unique by name and type)
CREATE CONSTRAINT entity_identity IF NOT EXISTS
FOR (n:Entity) REQUIRE (n.name, n.type) IS NODE KEY;

// 3. Performance Indexes for Querying & Subgraphs
CREATE INDEX entity_name_idx IF NOT EXISTS
FOR (n:Entity) ON (n.name);

CREATE INDEX entity_type_idx IF NOT EXISTS
FOR (n:Entity) ON (n.type);

CREATE INDEX timeline_event_date_idx IF NOT EXISTS
FOR (t:TimelineEvent) ON (t.date);
```

---

## 3. Node Types & Provenance Structure

* **Nodes Created:**
  - `:Case`: Case container (`id`, `created_at`).
  - `:Evidence`: Source evidence container (`id`, `created_at`).
  - `:Entity`: Entities extracted by GLiNER/Regex (`name`, `type`, `confidence`, `source`, `normalized_value`). Types include: `PERSON`, `PHONE`, `EMAIL`, `DEVICE`, `ACCOUNT`, `IP_ADDRESS`, `DOMAIN`, `URL`, `LOCATION`, `ORGANIZATION`, `VEHICLE`.
  - `:TimelineEvent`: Temporal artifacts (`date`, `summary`, `confidence`).
* **Relationships Created:**
  - `(:Evidence)-[:BELONGS_TO]->(:Case)`
  - `(:Entity)-[:MENTIONED_IN {evidence_id: $ev_id, confidence: $conf}]->(:Evidence)`
  - `(:Entity)-[:CONNECTED_TO {relationship: $rel, evidence_id: $ev_id, confidence: $conf}]->(:Entity)`
  - `(:TimelineEvent)-[:OCCURRED_IN]->(:Case)`

---

## 4. PostgreSQL → Neo4j Synchronization

* Entity and relationship ingestion is automatically triggered during Stage 3 of evidence processing (`backend/app/processing.py:271`).
* `KGClient.ingest()` uses Cypher `MERGE` operations on `(name, type)` pairs, guaranteeing cross-evidence and cross-case entity resolution without duplicate graph nodes.
* **Offline Resilience:** If Neo4j is unreachable, graph data is preserved as structured JSON within PostgreSQL `forensic_results` records (`processor='knowledge_graph'`).
