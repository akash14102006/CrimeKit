
# 06_MIDDLEWARE_SECURITY.md

# CrimeKit Backend – Middleware & Security Architecture
**Modules:** `backend/middleware/` + Cross-Cutting Security

---

# 1. Purpose

This document defines the middleware pipeline and security architecture for CrimeKit.

Middleware processes every incoming request before it reaches the API layer and every outgoing response before it leaves the application.

Its purpose is to enforce security, consistency, observability, auditing, and performance across the platform.

---

# 2. Security Principles

- Zero Trust
- Least Privilege
- Defense in Depth
- Secure by Default
- Immutable Audit Trail
- Privacy by Design
- Explainable Security Decisions

---

# 3. Folder Structure

```text
backend/

middleware/
├── auth_middleware.py
├── request_id.py
├── logging.py
├── audit.py
├── rate_limit.py
├── security_headers.py
├── cors.py
├── exception_handler.py
├── response_wrapper.py
├── metrics.py
└── maintenance.py
```

---

# 4. Middleware Execution Pipeline

```text
HTTP Request
    ↓
Request ID
    ↓
Request Logging
    ↓
Security Headers
    ↓
CORS
    ↓
JWT Authentication
    ↓
Role Authorization
    ↓
Rate Limiting
    ↓
Input Validation
    ↓
API Router
    ↓
Service Layer
    ↓
Response Wrapper
    ↓
Audit Logging
    ↓
Metrics
    ↓
HTTP Response
```

---

# 5. Authentication Middleware

Responsibilities:

- Validate JWT
- Extract user identity
- Load permissions
- Reject expired tokens
- Attach authenticated user to request context

---

# 6. Authorization

Every protected endpoint validates:

- User role
- Case membership
- Resource ownership
- Required permissions

Authorization decisions are logged.

---

# 7. Request Tracking

Each request receives:

- Request ID
- Correlation ID
- Timestamp
- User ID (if authenticated)

These IDs follow the request through all services.

---

# 8. Audit Logging

Record:

- Login attempts
- Case operations
- Evidence access
- Report downloads
- Permission changes
- Administrative actions

Audit records are immutable.

---

# 9. Security Headers

Apply:

- HSTS
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Content-Security-Policy
- Cache-Control (where required)

---

# 10. Input Protection

Validate:

- Payload size
- MIME type
- JSON schema
- File extension
- Path traversal attempts
- Injection patterns

Reject malformed requests before business logic executes.

---

# 11. Rate Limiting

Protect against abuse by limiting:

- Login attempts
- Upload requests
- Search endpoints
- AI endpoints
- Public APIs

---

# 12. Error Handling

Global exception middleware returns:

- Error code
- Message
- Request ID
- Timestamp

Never expose stack traces or internal implementation details.

---

# 13. Observability

Collect:

- Request duration
- API latency
- Error rate
- Upload throughput
- AI processing time
- Database response time

---

# 14. Logging Standards

Every request logs:

- Method
- Path
- User
- Status code
- Execution time
- Request ID

Sensitive information is never logged.

---

# 15. Integration

Middleware interacts with:

- FastAPI
- Authentication
- Authorization
- Audit Service
- Metrics Service
- Logging Infrastructure

Middleware does not contain business logic.

---

# 16. Acceptance Criteria

Complete when:

- Authentication enforced
- Authorization enforced
- Request tracing active
- Security headers applied
- Audit logging operational
- Global exception handling active
- Metrics collected
- Standard responses returned

---

# 17. Developer Checklist

- Keep middleware stateless
- Execute quickly
- Never access repositories directly
- Never implement business rules
- Log security events
- Preserve request IDs
- Sanitize errors
- Test middleware independently

---

# 18. Guiding Principle

Middleware forms the protective boundary around CrimeKit.

Every request must be authenticated, authorized, traceable, observable, and securely processed before it reaches investigative business logic.
