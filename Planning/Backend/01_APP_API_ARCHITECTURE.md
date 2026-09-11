# 01_APP_API_ARCHITECTURE.md

# CrimeKit Backend – App & API Architecture
**Module:** backend/app + backend/api

---

# 1. Purpose

This document defines the application bootstrap and API architecture for CrimeKit.

The objective is to create a clean, scalable, enterprise-grade FastAPI application that separates infrastructure from business logic and provides a stable foundation for all backend modules.

This document is the implementation specification for the following folders:

```text
backend/
├── app/
└── api/
```

---

# 2. Architectural Goals

- Modular FastAPI application
- API-first design
- Clean Architecture principles
- Dependency Injection
- Versioned REST APIs
- Stateless services
- OpenAPI documentation
- Production-ready startup lifecycle
- Easy integration with AI agents, forensic engine, and workflows

---

# 3. Responsibilities

## app/

Responsible for application initialization.

Owns:

- FastAPI application instance
- Startup lifecycle
- Shutdown lifecycle
- Dependency registration
- Global configuration loading
- Router registration
- Middleware registration
- Exception registration
- Health endpoints
- Application metadata

The app folder **never contains business logic**.

---

## api/

Responsible for HTTP communication.

Owns:

- REST endpoints
- Request validation
- Response formatting
- Authentication checks
- Calling service layer
- HTTP status codes
- API documentation

The API layer **never contains SQL, AI logic, or forensic processing**.

---

# 4. Folder Design

```text
backend/
│
├── app/
│   ├── main.py
│   ├── lifespan.py
│   ├── dependencies.py
│   ├── routers.py
│   ├── settings.py
│   ├── exceptions.py
│   └── health.py
│
├── api/
│   ├── v1/
│   │
│   ├── auth/
│   ├── cases/
│   ├── evidence/
│   ├── uploads/
│   ├── reports/
│   ├── agents/
│   ├── admin/
│   └── system/
```

---

# 5. Startup Lifecycle

```text
Application Start

↓

Load Configuration

↓

Validate Environment

↓

Initialize Logging

↓

Connect PostgreSQL

↓

Connect MinIO

↓

Connect Neo4j

↓

Connect Elasticsearch

↓

Register Routers

↓

Register Middleware

↓

Register Exception Handlers

↓

Application Ready
```

---

# 6. API Design Principles

Every endpoint shall:

- use REST conventions
- return JSON
- be versioned
- validate requests
- validate permissions
- return consistent responses
- include request tracing
- produce OpenAPI documentation

---

# 7. API Versioning

```text
/api/v1/

Authentication

Cases

Evidence

Uploads

Reports

Agents

System
```

Future versions:

```text
/api/v2/
/api/v3/
```

No breaking changes inside a version.

---

# 8. Standard Request Flow

```text
Client

↓

API Router

↓

Dependency Injection

↓

Authentication

↓

Authorization

↓

Schema Validation

↓

Service Layer

↓

Repository/Data Access

↓

Database / MinIO

↓

Response Builder

↓

Client
```

---

# 9. Response Standard

Every response should include:

- success
- message
- data
- request_id
- timestamp

Errors should include:

- error_code
- message
- request_id
- trace_id (internal logging)

---

# 10. Health & System APIs

Provide endpoints for:

- API health
- Database health
- MinIO connectivity
- Neo4j connectivity
- Elasticsearch connectivity
- Workflow engine status
- Application version

---

# 11. Dependency Injection

Dependencies should manage:

- Current user
- Current case
- Database session
- Object storage client
- Search client
- Graph client
- Configuration
- Permissions

Business services receive dependencies through injection rather than creating them.

---

# 12. Router Organization

```text
auth_router

case_router

evidence_router

upload_router

report_router

admin_router

system_router
```

Each router owns only HTTP behavior.

---

# 13. Security at API Layer

- JWT validation
- Role-based authorization
- Request size limits
- Secure headers
- Rate limiting
- Input validation
- Audit logging
- No sensitive data leakage

---

# 14. Documentation

OpenAPI should be generated automatically.

Each endpoint must include:

- Summary
- Description
- Request schema
- Response schema
- Error responses
- Authentication requirements

---

# 15. Integration Boundaries

API communicates with:

- Authentication module
- Case module
- Evidence module
- Upload module
- Report module
- Service layer

API never calls forensic tools directly.

---

# 16. Non-Functional Requirements

- Stateless
- Horizontally scalable
- Container-friendly
- Observable
- Testable
- Async-ready
- High availability

---

# 17. Acceptance Criteria

This module is complete when:

- Application boots successfully
- Configuration loads correctly
- All routers are registered
- Health endpoints function
- API documentation is available
- Global exception handling works
- Middleware pipeline is active
- Versioned API structure is established

---

# 18. Developer Checklist

Before adding a new endpoint:

- Define request schema
- Define response schema
- Validate authentication
- Validate authorization
- Keep business logic in services
- Return standard response format
- Document endpoint
- Add tests
- Log important operations
- Preserve backward compatibility

---

# 19. Guiding Principle

The App layer builds and configures the platform.

The API layer exposes secure, predictable interfaces.

Business intelligence, forensic processing, and AI reasoning always live outside these layers.
