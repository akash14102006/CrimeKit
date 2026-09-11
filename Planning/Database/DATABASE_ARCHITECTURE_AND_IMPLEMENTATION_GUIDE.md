
# DATABASE_ARCHITECTURE_AND_IMPLEMENTATION_GUIDE.md

# CrimeKit Database Architecture & Implementation Guide

**Version:** 1.0  
**Audience:** Backend Engineers, Database Engineers, DevOps, AI Engineers

---

# 1. Purpose

This document defines the complete database architecture for CrimeKit. It explains how PostgreSQL, pgvector, Neo4j, Elasticsearch, migrations, and seed data work together as a unified persistence layer.

---

# 2. Database Philosophy

- PostgreSQL is the system of record.
- pgvector provides semantic similarity search.
- Neo4j models investigative relationships.
- Elasticsearch powers full-text and faceted search.
- Migrations provide version-controlled schema evolution.
- Seeds create reproducible environments.

---

# 3. Folder Structure

```text
database/
├── postgres/
├── neo4j/
├── elasticsearch/
├── pgvector/
├── migrations/
├── seeds/
├── backup/
├── replication/
├── monitoring/
├── indexing/
├── optimization/
├── security/
├── analytics/
└── testing/
```

---

# 4. High-Level Architecture

```text
FastAPI
   │
Repository Layer
   │
──────────────────────────────────────────
│ PostgreSQL │ pgvector │ Neo4j │ Elastic │
──────────────────────────────────────────
   │
Backup • Monitoring • Replication
```

---

# 5. PostgreSQL

Responsibilities

- Primary transactional database
- Case management
- Evidence metadata
- Users & RBAC
- Audit logs
- Reports
- Workflow state

Design Guidelines

- Normalize transactional data
- Use UUID primary keys
- Foreign keys
- CHECK constraints
- JSONB for flexible metadata
- Connection pooling
- Row Level Security
- ACID transactions

Recommended Schemas

- auth
- cases
- evidence
- workflow
- reports
- audit
- ai

---

# 6. pgvector

Purpose

- Embedding storage
- Semantic retrieval
- AI RAG search

Features

- HNSW indexes
- IVFFlat indexes
- Cosine similarity
- Metadata filtering
- Hybrid search

Store vectors only with metadata references.

---

# 7. Neo4j

Purpose

- Knowledge graph
- Relationship discovery
- Timeline analysis

Example Nodes

- Person
- Device
- Evidence
- Case
- Location
- Organization

Example Relationships

- KNOWS
- OWNS
- LOCATED_AT
- RELATED_TO
- APPEARS_IN
- CONTACTED

Use Cypher for graph traversals.

---

# 8. Elasticsearch

Purpose

- Full-text search
- Filters
- Aggregations
- Case discovery

Indexes

- evidence
- reports
- timeline
- chat
- email
- logs

Recommendations

- Custom analyzers
- Synonyms
- Index templates
- Aliases
- Incremental indexing

---

# 9. Synchronization Strategy

PostgreSQL remains the source of truth.

Synchronization

- PostgreSQL → Elasticsearch
- PostgreSQL → Neo4j
- PostgreSQL → pgvector

Patterns

- Event-driven
- Background workers
- Retry queues
- Idempotent updates

---

# 10. Migrations

Use version-controlled migrations.

Guidelines

- One logical change per migration
- Forward-compatible changes
- Rollback scripts
- Tested before production
- Immutable migration history

---

# 11. Seed Data

Use seeds for

- Development
- Testing
- Demo
- Reference values

Never include production secrets.

---

# 12. Indexing Strategy

PostgreSQL

- B-tree
- GIN
- GiST
- Partial indexes

Neo4j

- Node property indexes
- Relationship indexes

Elasticsearch

- Inverted indexes

pgvector

- HNSW
- IVFFlat

---

# 13. Backup & Recovery

PostgreSQL

- Daily backup
- WAL archiving

Neo4j

- Consistent snapshots

Elasticsearch

- Snapshot repository

pgvector

- Included with PostgreSQL backup

Recovery Validation

- Restore
- Integrity checks
- Application smoke tests

---

# 14. Replication

- PostgreSQL streaming replication
- Neo4j cluster
- Elasticsearch cluster
- High availability architecture

Monitor replication lag.

---

# 15. Security

- TLS
- RBAC
- Least privilege
- Secret manager
- Encryption at rest
- Audit logging
- Row Level Security

---

# 16. Monitoring

Metrics

- Query latency
- Slow queries
- Connections
- Replication lag
- Index size
- Disk usage
- Cache hit ratio

Tools

- Prometheus
- Grafana
- OpenTelemetry

---

# 17. Performance Optimization

- Query plans
- Partitioning
- Batch operations
- Prepared statements
- Connection pooling
- Index maintenance
- Vacuum / Analyze
- Search tuning

---

# 18. Testing

Unit

- Repository tests

Integration

- Cross-database synchronization

Load

- High concurrency
- Large evidence imports

Disaster Recovery

- Restore validation
- Failover testing

---

# 19. Coding Standards

Do

- Repository pattern
- Typed models
- Transactions
- Parameterized queries
- Version-controlled schema

Don't

- Business logic in SQL
- Hardcoded credentials
- N+1 queries
- Direct DB access from controllers

---

# 20. Production Checklist

- Database backups verified
- Replication healthy
- Monitoring enabled
- Migrations applied
- Seeds validated
- Security reviewed
- Indexes optimized
- Restore tested
- Audit logging enabled

---

# 21. Guiding Principles

1. PostgreSQL is the single source of truth.
2. Neo4j stores relationships, not transactions.
3. Elasticsearch indexes searchable content.
4. pgvector stores embeddings for semantic search.
5. Every schema change is version controlled.
6. Every environment is reproducible with migrations and seeds.
7. Security, observability, and recoverability are mandatory.
