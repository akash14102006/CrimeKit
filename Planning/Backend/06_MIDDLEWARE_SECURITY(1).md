
# 06_MIDDLEWARE_SECURITY.md

# CrimeKit Backend – Middleware & Security Architecture
**Modules:** `backend/middleware/` + `backend/security/`

---

# 1. Purpose

This document defines the middleware pipeline and security architecture for CrimeKit. Middleware protects every incoming request before it reaches business logic, while the security layer handles authentication, authorization, encryption, secrets, and defensive controls.

---

# 2. Goals

- Zero Trust architecture
- Secure by default
- Defense in depth
- Least privilege
- Complete auditability
- Enterprise-ready deployment

---

# 3. Folder Structure

```text
backend/
├── middleware/
│   ├── request_id.py
│   ├── logging.py
│   ├── cors.py
│   ├── security_headers.py
│   ├── rate_limit.py
│   ├── exception_handler.py
│   ├── audit.py
│   ├── metrics.py
│   └── timing.py
│
└── security/
    ├── jwt.py
    ├── auth.py
    ├── permissions.py
    ├── roles.py
    ├── hashing.py
    ├── encryption.py
    ├── secrets.py
    ├── csrf.py
    ├── validators.py
    └── dependencies.py
```

---

# 4. Request Pipeline

```text
Client
 ↓
HTTPS
 ↓
Security Headers
 ↓
CORS
 ↓
Request ID
 ↓
Rate Limiter
 ↓
Authentication
 ↓
Authorization
 ↓
Validation
 ↓
Logging & Metrics
 ↓
API Router
 ↓
Service Layer
 ↓
Repository
 ↓
Database
```

---

# 5. Middleware Responsibilities

- Attach request ID
- Configure CORS
- Add security headers
- Log requests/responses
- Measure latency
- Handle exceptions
- Enforce rate limits
- Publish metrics
- Record audit events

---

# 6. Security Responsibilities

- JWT access/refresh tokens
- Password hashing (Argon2 or bcrypt)
- Role-Based Access Control (RBAC)
- Permission checks
- Secret management
- Encryption at rest and in transit
- Input validation
- Token verification

---

# 7. Authentication Flow

1. User logs in.
2. Credentials verified.
3. Password hash checked.
4. JWT generated.
5. Refresh token issued.
6. Protected endpoints require valid access token.
7. Expired tokens refreshed securely.

---

# 8. Authorization (RBAC)

Suggested roles:

- Admin
- Investigator
- Forensic Analyst
- Reviewer
- Read-Only Auditor

Permissions should be fine-grained (view_case, upload_evidence, generate_report, delete_case, etc.).

---

# 9. Security Headers

Include:

- Strict-Transport-Security
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

---

# 10. Rate Limiting

Protect against abuse by limiting:

- Login attempts
- Search endpoints
- Upload endpoints
- AI inference endpoints
- Public APIs

Return HTTP 429 when limits are exceeded.

---

# 11. Password Policy

- Minimum 12 characters
- Upper/lowercase
- Number
- Special character
- Never store plaintext passwords
- Rotate compromised credentials

---

# 12. Encryption

Encrypt:

- Tokens
- Secrets
- Sensitive metadata
- Personally identifiable information (PII)

Always use HTTPS/TLS for transport.

---

# 13. Secret Management

Never hardcode:

- JWT secret
- Database passwords
- API keys
- Cloud credentials

Load from environment variables or a secret manager.

---

# 14. Audit Logging

Record:

- Login/logout
- Permission failures
- Case access
- Evidence upload
- Report generation
- Administrative actions

Logs should be immutable and timestamped.

---

# 15. Exception Handling

Return standardized errors:

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

Never expose stack traces in production.

---

# 16. Monitoring

Collect:

- Request count
- Error rate
- Response time
- Authentication failures
- Rate-limit events
- Upload failures

---

# 17. Integrations

Middleware integrates with:

- FastAPI
- Prometheus
- OpenTelemetry

Security integrates with:

- JWT
- OAuth2
- SQLAlchemy
- Pydantic
- Argon2/bcrypt

---

# 18. Best Practices

- Validate every request
- Deny by default
- Least privilege
- Rotate secrets regularly
- Sanitize inputs
- Escape outputs where needed
- Log security events
- Keep dependencies updated

---

# 19. Acceptance Criteria

- Every request passes through middleware.
- Protected endpoints require authentication.
- Authorization is role and permission based.
- Security headers are enabled.
- Rate limiting works.
- Secrets are externalized.
- Audit logs are generated.
- Errors are standardized.

---

# 20. Developer Checklist

- Create reusable middleware.
- Keep authentication separate from authorization.
- Never trust client input.
- Use dependency injection for security.
- Avoid business logic inside middleware.
- Test every security control.

---

# 21. Guiding Principle

Middleware protects the request lifecycle.

Security protects the CrimeKit platform, its investigators, and digital evidence through layered, verifiable, and enterprise-grade defenses.
