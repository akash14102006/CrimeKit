# 00_BACKEND_MASTER_PLAN.md

# CrimeKit Backend Master Plan
**Version:** 1.0  
**Project:** CrimeKit (ACPIA - Agentic Child Protection Investigation Assistant)

---

# 1. Purpose

This document is the master blueprint for the entire CrimeKit backend. It defines the architecture, responsibilities, module boundaries, development rules, data flow, security principles, scalability strategy, and implementation roadmap.

It is written for both human developers and AI-assisted ("vibe coding") tools. Every backend implementation should follow this document before any feature is developed.

This document does **not** contain source code. It defines **what must be built**, **why it exists**, **how modules interact**, and **how the backend evolves into a production-grade enterprise system**.

---

# 2. Product Vision

CrimeKit transforms massive volumes of digital evidence into structured, explainable, investigator-ready intelligence.

The backend is responsible for:

- Secure authentication
- Case lifecycle management
- Evidence ingestion
- Chain of custody
- Digital forensic orchestration
- AI workflow orchestration
- Investigation data management
- Court-ready reporting
- Secure APIs
- Auditability
- Scalability

The backend never makes legal decisions. It assists investigators with explainable outputs.

---

# 3. Core Principles

- Human-in-the-loop
- Explainable AI
- Secure by Design
- Privacy First
- Zero Trust
- Modular Architecture
- Event Driven Workflows
- Production Ready
- Horizontally Scalable
- Observable
- API First

---

# 4. Backend Folder Architecture

```text
backend/
│
├── app/
├── api/
├── auth/
├── cases/
├── evidence/
├── reports/
├── uploads/
├── services/
├── middleware/
├── models/
├── schemas/
```

Each module owns a single responsibility.

---

# 5. Request Lifecycle

```text
Client

↓

Authentication

↓

API Gateway

↓

Validation

↓

Authorization

↓

Business Service

↓

Repository

↓

Database / MinIO

↓

Workflow Trigger

↓

Response
```

Every request follows the same lifecycle.

---

# 6. High Level Architecture

```text
Frontend

↓

FastAPI Backend

↓

Authentication

↓

Case Management

↓

Evidence Gateway

↓

MinIO Object Storage

↓

SHA256 Integrity

↓

Temporal Workflow

↓

Forensic Engine

↓

Artifact Extraction

↓

PostgreSQL

Neo4j

Elasticsearch

pgvector

↓

LangGraph Supervisor

↓

AI Agents

↓

Investigation Workspace

↓

Court Report
```

---

# 7. Backend Responsibilities

## Authentication

Identity verification

JWT

Role management

Session management

Permission validation

---

## Case Management

Create cases

Assign investigators

Track lifecycle

Evidence linkage

Audit history

---

## Evidence Management

Upload evidence

Validate

Hash generation

Metadata extraction

Chain of custody

Version tracking

Evidence locking

---

## Upload Pipeline

Large file upload

Chunk uploads

Virus scanning

Storage

Workflow triggering

---

## Report System

Investigation reports

Court reports

Evidence summaries

AI explanation

Export

---

## Service Layer

Business logic only.

Services never contain HTTP logic.

Services never contain SQL.

---

## Middleware

Authentication

Authorization

Logging

Request ID

Error handling

Rate limiting

Tracing

---

## Models

Database entities.

ORM only.

No business logic.

---

## Schemas

Validation

Serialization

API contracts

---

# 8. Design Rules

Every module:

- single responsibility
- dependency injection
- strongly typed
- reusable
- testable
- observable

No duplicated logic.

---

# 9. Security Strategy

Authentication

JWT

Role Based Access

Least Privilege

Encrypted secrets

SHA256 evidence integrity

Audit logs

Input validation

Secure headers

Rate limiting

Malware scanning

---

# 10. Storage Strategy

Large evidence:

MinIO

Metadata:

PostgreSQL

Relationships:

Neo4j

Semantic Search:

pgvector

Search:

Elasticsearch

---

# 11. Workflow Strategy

Temporal controls long-running workflows.

Typical workflow:

Evidence Upload

↓

Hash

↓

Malware Scan

↓

Store

↓

Forensic Extraction

↓

Metadata

↓

Knowledge Graph

↓

AI Correlation

↓

Report

---

# 12. AI Integration

Backend never lets AI directly analyze raw uploads.

Pipeline:

Evidence

↓

Forensic Tools

↓

Structured Artifacts

↓

Knowledge Layer

↓

LangGraph Supervisor

↓

Specialized Agents

↓

Explainable Results

---

# 13. Error Handling Principles

Every error:

- logged
- traced
- categorized
- sanitized before returning to client

No stack traces exposed.

---

# 14. Logging & Monitoring

Every request receives:

- Request ID
- User ID
- Case ID
- Timestamp
- Processing Time

Metrics collected for performance and failures.

---

# 15. Scalability Goals

Support:

- millions of evidence objects
- concurrent investigators
- distributed workers
- multiple forensic nodes
- cloud or on-prem deployment

---

# 16. Coding Standards

Business logic → services/

HTTP → api/

Persistence → repositories (future)

Validation → schemas/

Database → models/

No business logic inside API routers.

---

# 17. Backend Development Order

Phase 1

Authentication

↓

Case Management

↓

Evidence Upload

↓

Storage

Phase 2

Forensic Processing

↓

Workflow

↓

Metadata

Phase 3

AI Integration

↓

Investigation Workspace

↓

Reports

---

# 18. Acceptance Criteria

The backend is complete when it provides:

- Secure authentication
- Complete case management
- Reliable evidence ingestion
- Verified chain of custody
- Automated forensic orchestration
- Explainable AI integration
- Court-ready reporting
- Full audit logging
- Production-grade scalability

---

# 19. Developer Checklist

Before implementing any module:

- Read this document.
- Follow project constitution.
- Keep modules independent.
- Write reusable services.
- Validate every input.
- Protect every endpoint.
- Log every important action.
- Keep AI explainable.
- Never bypass chain of custody.
- Never allow AI to make legal decisions.

---

# 20. Guiding Statement

CrimeKit Backend exists to transform secure digital evidence into trustworthy investigative intelligence through scalable engineering, forensic automation, explainable AI, and human-centered decision support.
