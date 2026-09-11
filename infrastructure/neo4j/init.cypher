// ============================================
// CrimeKit Neo4j Initialization Script
// ============================================

// Constraints
// Enforce uniqueness for Entity name+type combinations
CREATE CONSTRAINT entity_name_type IF NOT EXISTS
FOR (e:Entity) REQUIRE (e.name, e.type) IS UNIQUE;

// Enforce unique Case identifiers
CREATE CONSTRAINT case_id IF NOT EXISTS
FOR (c:Case) REQUIRE c.id IS UNIQUE;

// Enforce unique Evidence identifiers
CREATE CONSTRAINT evidence_id IF NOT EXISTS
FOR (ev:Evidence) REQUIRE ev.id IS UNIQUE;

// Indexes
// Fast lookup by Entity name
CREATE INDEX entity_name IF NOT EXISTS
FOR (e:Entity) ON (e.name);

// Fast lookup by Entity type
CREATE INDEX entity_type IF NOT EXISTS
FOR (e:Entity) ON (e.type);

// Fast lookup by Case id
CREATE INDEX case_id_index IF NOT EXISTS
FOR (c:Case) ON (c.id);

// Fast lookup by Evidence id
CREATE INDEX evidence_id_index IF NOT EXISTS
FOR (ev:Evidence) ON (ev.id);

// Fast lookup by Event date
CREATE INDEX event_date IF NOT EXISTS
FOR (ev:Event) ON (ev.date);

// Full-text search index for Entity names
CREATE FULLTEXT INDEX entity_name_fulltext IF NOT EXISTS
FOR (e:Entity) ON EACH [e.name];
