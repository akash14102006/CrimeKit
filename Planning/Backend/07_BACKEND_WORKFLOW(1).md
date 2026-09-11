
# 07_BACKEND_WORKFLOW.md

# CrimeKit Backend – Complete Backend Workflow
**Document:** End-to-End Request Flow Architecture

---

# 1. Purpose

This document explains how every request travels through the CrimeKit backend, from the client to the database and back to the client. It defines the responsibilities of each backend layer and the interaction between modules.

---

# 2. Workflow Goals

- Clean Architecture
- Separation of Concerns
- Secure by Default
- Observable
- Scalable
- Testable
- Enterprise Ready

---

# 3. Backend Layers

```text
Frontend
    │
HTTPS/API
    │
Middleware
    │
Security
    │
API Router
    │
Schemas (Validation)
    │
Dependencies
    │
Services
    │
Repositories
    │
Database / Storage / AI Services
```

---

# 4. Complete Request Lifecycle

```text
Client
 │
 ├── HTTPS Request
 │
 ▼
FastAPI Application
 │
 ▼
Middleware Pipeline
 │
 ├── Request ID
 ├── Security Headers
 ├── CORS
 ├── Logging
 ├── Rate Limiter
 ├── Metrics
 └── Exception Handler
 │
 ▼
Authentication
 │
 ▼
Authorization
 │
 ▼
API Router
 │
 ▼
Pydantic Request Schema
 │
 ▼
Dependency Injection
 │
 ▼
Service Layer
 │
 ▼
Repository Layer
 │
 ▼
PostgreSQL / Neo4j / MinIO / Elasticsearch / Redis / AI
 │
 ▼
Repository
 │
 ▼
Service
 │
 ▼
Response Schema
 │
 ▼
Middleware (Logging & Metrics)
 │
 ▼
JSON Response
```

---

# 5. Step-by-Step Flow

## Step 1 – Client Request

- Web
- Mobile
- Admin Portal
- External APIs

All communication occurs over HTTPS.

---

## Step 2 – Middleware

Executes before business logic.

Responsibilities:

- Generate Request ID
- Security headers
- Logging
- Timing
- CORS
- Rate limiting
- Metrics
- Exception interception

---

## Step 3 – Authentication

Verify:

- JWT
- Session
- API Key (if required)

Reject unauthorized requests immediately.

---

## Step 4 – Authorization

Verify:

- Role
- Permission
- Ownership
- Resource access

---

## Step 5 – API Router

Routes request to the correct feature module:

- Auth
- Cases
- Evidence
- Reports
- Search
- AI
- Audit

---

## Step 6 – Request Schema Validation

Validate:

- Types
- Required fields
- UUIDs
- Enums
- File metadata
- Pagination
- Query parameters

---

## Step 7 – Dependency Injection

Inject:

- Database session
- Current user
- Repository
- Service
- Settings
- Logger

---

## Step 8 – Service Layer

Business logic only.

Examples:

- Create Case
- Upload Evidence
- Generate Report
- Search Evidence
- AI Analysis

---

## Step 9 – Repository Layer

Responsible for:

- CRUD
- Transactions
- Queries
- Pagination
- Bulk operations

No business logic.

---

## Step 10 – Data Sources

- PostgreSQL
- Neo4j
- MinIO
- Elasticsearch
- Redis
- pgvector
- AI Providers

---

## Step 11 – Service Response

Service:

- Combines results
- Applies business rules
- Records audit events
- Triggers background jobs if needed

---

## Step 12 – Response Schema

Convert domain objects into safe API responses.

Never return ORM models directly.

---

## Step 13 – Response Middleware

Execute:

- Logging
- Metrics
- Timing
- Error formatting

---

## Step 14 – Client Response

Return standardized JSON:

```json
{
  "success": true,
  "message": "Operation completed",
  "data": {}
}
```

---

# 6. Background Workflow

Long-running tasks should use background workers.

Examples:

- OCR
- AI Analysis
- Video Processing
- Timeline Generation
- Report Generation
- Notifications

---

# 7. Error Flow

```text
Exception
   │
Exception Middleware
   │
Standard Error Formatter
   │
Audit Log
   │
JSON Error Response
```

---

# 8. Audit Workflow

Important events:

- Login
- Logout
- Case creation
- Evidence upload
- Report generation
- AI execution
- Permission denial

---

# 9. Transaction Workflow

Repository opens transaction.

Service performs operations.

Repository commits.

On failure:

- Rollback
- Log
- Return standardized error

---

# 10. Observability

Collect:

- Request count
- Response time
- Database latency
- AI latency
- Upload duration
- Error rate
- Authentication failures

---

# 11. Design Principles

- Thin Controllers
- Fat Services
- Reusable Repositories
- Independent Middleware
- Strong Validation
- Dependency Injection
- Centralized Error Handling

---

# 12. Acceptance Criteria

- Every request follows one consistent workflow.
- Validation occurs before business logic.
- Authentication precedes authorization.
- Services contain business rules.
- Repositories isolate persistence.
- Responses are schema-driven.
- Errors are standardized.
- All important events are audited.

---

# 13. Developer Checklist

- One responsibility per layer.
- No database access from routers.
- No HTTP logic in services.
- No business logic in repositories.
- Always validate inputs.
- Always log important events.
- Keep workflows predictable.

---

# 14. Guiding Principle

Every request in CrimeKit should pass through a predictable, secure, validated, observable, and maintainable workflow, ensuring enterprise-grade reliability from request intake to final response.
