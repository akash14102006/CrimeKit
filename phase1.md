# ROLE

You are a Principal DevOps Architect, Cloud Infrastructure Engineer, Site Reliability Engineer (SRE), Enterprise Security Engineer, and Backend Platform Architect.

You are working on CrimeKit, an enterprise-grade AI-powered Digital Forensics & Investigation Platform.

Before writing any code:

1. Analyze the ENTIRE repository using Graphify.
2. Read GRAPH_REPORT.md completely.
3. Understand:
   - Architecture
   - Services
   - Dependencies
   - Database
   - AI Pipeline
   - Knowledge Graph
   - Multi-Agent System
   - Investigation Workspace
4. Identify every infrastructure dependency.
5. Do NOT duplicate existing work.
6. Preserve existing architecture.
7. Everything must be production-ready.

This is NOT a simple Docker Compose task.

This is designing the complete enterprise infrastructure layer.

---

# GOAL

Transform CrimeKit into a production-deployable enterprise platform.

Everything must be modular.

Everything must be scalable.

Everything must be secure.

Everything must be cloud-ready.

Everything must follow enterprise DevOps standards.

---

# DO NOT MODIFY

Do not rewrite business logic.

Do not rewrite APIs.

Do not modify existing backend features unless required.

Do not break any existing tests.

Existing backend functionality is considered stable.

---

# PHASE 1 DELIVERABLES

Implement complete infrastructure.

---

# 1. Docker Compose

Design a production-grade Docker Compose architecture.

Include:

Backend

PostgreSQL

Redis

Neo4j

MinIO (S3-compatible object storage)

Nginx Reverse Proxy

Optional pgAdmin

Optional Neo4j Browser

Optional Redis Commander

Optional Prometheus

Optional Grafana

Persistent Volumes

Health Checks

Automatic restart policies

Internal Docker networking

Service dependencies

Graceful startup ordering

Resource limits

Profiles for development and production

---

# 2. Containerization

Create enterprise Dockerfiles.

Backend Dockerfile

Multi-stage build

Non-root user

Minimal image

Security hardened

Optimized layers

Python dependency caching

Health endpoint

Startup script

Production configuration

Development Dockerfile

Hot reload

Debug tools

Separate from production

---

# 3. PostgreSQL

Configure:

Production-ready settings

Indexes

Connection pooling

Automatic migrations

Persistent volume

Backup strategy

Restore strategy

Performance tuning

Extensions required

Health checks

Environment variables

Secrets

---

# 4. Redis

Configure:

Caching

Shared Context

Rate limiting

Session storage

Pub/Sub

Background queue support

Persistence

Health checks

Password protection

Memory policy

Production configuration

---

# 5. Neo4j

Configure:

Persistent graph storage

Authentication

Indexes

Constraints

Performance tuning

Volume mounting

Backup support

Health checks

Enterprise configuration

---

# 6. MinIO Object Storage

Store:

Evidence

Images

Videos

PDFs

Extracted artifacts

AI outputs

Court reports

Backups

Implement:

Buckets

Bucket policies

Versioning

Lifecycle rules

Encryption

Presigned URLs

Retention policies

---

# 7. Nginx Reverse Proxy

Implement:

HTTPS ready

Compression

Security headers

Rate limiting

Static caching

Reverse proxy

WebSocket support

Large file uploads

Request buffering

Timeout configuration

Health endpoints

---

# 8. Configuration Management

Create:

.env.example

.env.production.example

.env.development.example

Configuration validation

Environment loader

Secrets documentation

Configuration hierarchy

---

# 9. Logging

Centralized logging.

Requirements:

JSON logs

Structured logging

Request IDs

Correlation IDs

Agent execution IDs

Audit logs

Container logs

Log rotation

Log levels

---

# 10. Health Checks

Every service must expose:

Health endpoint

Readiness endpoint

Liveness endpoint

Dependency checks

Database check

Redis check

Neo4j check

Storage check

AI Pipeline check

---

# 11. Backup & Recovery

Implement:

PostgreSQL backup

Neo4j backup

MinIO backup

Restore scripts

Backup scheduling

Integrity verification

Disaster recovery documentation

---

# 12. Security

Implement:

Least privilege

Non-root containers

Secrets management

Read-only containers where possible

Network isolation

Private Docker network

TLS ready

Secure headers

Dependency scanning

Container scanning

---

# 13. Monitoring

Prepare for production monitoring.

Integrate:

Prometheus

Grafana

OpenTelemetry

Metrics endpoint

Tracing

Container metrics

Database metrics

Redis metrics

Neo4j metrics

API latency

AI Agent metrics

Queue metrics

---

# 14. Performance

Optimize:

Container startup

Database connections

Connection pooling

Redis caching

Memory usage

Image size

Build speed

Volumes

Networking

---

# 15. Documentation

Generate:

Infrastructure Architecture.md

Deployment Guide.md

Disaster Recovery.md

Operations Manual.md

Environment Variables.md

Backup Guide.md

Troubleshooting Guide.md

Docker Guide.md

Production Checklist.md

---

# 16. Testing

Verify:

docker compose up

docker compose down

Restart

Persistence

Backup restore

Health checks

Database connectivity

Redis connectivity

Neo4j connectivity

MinIO connectivity

Nginx routing

Evidence upload

Workspace API

Knowledge Graph

AI Agents

---

# DIRECTORY STRUCTURE

Create a clean enterprise layout.

Example:

infrastructure/
    docker/
    compose/
    nginx/
    postgres/
    redis/
    neo4j/
    minio/
    monitoring/
    backups/
    scripts/
    configs/
    docs/

---

# CODING STANDARDS

Enterprise-grade.

Modular.

SOLID.

12-Factor App.

Security-first.

Production-first.

Cloud-native.

Docker best practices.

OCI compliant.

No duplicated configuration.

Clear comments.

Maintainable.

---

# ACCEPTANCE CRITERIA

The task is COMPLETE only if:

✅ docker compose up starts the full stack

✅ Backend automatically connects to PostgreSQL

✅ Backend automatically connects to Redis

✅ Backend automatically connects to Neo4j

✅ Backend automatically connects to MinIO

✅ Nginx routes traffic correctly

✅ Persistent volumes survive restarts

✅ Health checks pass

✅ Logging works

✅ Backup scripts work

✅ Documentation is complete

✅ Existing backend tests still pass

✅ No existing functionality is broken

At the end:

1. Explain every file created.
2. Explain every configuration.
3. Explain security decisions.
4. Explain scalability decisions.
5. Explain how this prepares CrimeKit for Kubernetes and cloud deployment.
6. Produce a final infrastructure readiness report with remaining technical debt and recommendations.

Do not stop until all acceptance criteria are satisfied.