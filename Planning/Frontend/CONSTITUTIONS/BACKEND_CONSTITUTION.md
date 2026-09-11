# 01_BACKEND_ENGINEERING_CONSTITUTION_MASTER_PROMPT.md

# ENTERPRISE BACKEND CONSTITUTION
# VIBE CODING UNIVERSAL BACKEND RULES

## PURPOSE

This document is the supreme constitution for backend engineering.

Designed for:

- Cursor
- Claude Code
- Windsurf
- Roo Code
- Cline
- Aider
- GitHub Copilot
- OpenAI Agents
- Gemini CLI
- Any AI Coding Agent

Target Architecture:

- NestJS
- TypeScript
- PostgreSQL
- Supabase
- Prisma
- Redis
- Stripe
- Docker
- Railway
- Fly.io
- AWS
- GCP

This is NOT:

- tutorial code
- hackathon code
- demo code
- portfolio code
- proof of concept code

This is:

Enterprise Production Software.

---

# CONSTITUTION RATING

Based on your frontend constitution chain:

Engineering Quality: 9.5/10

Architecture Quality: 9.5/10

Security Quality: 9.8/10

Accessibility Quality: 9.8/10

Performance Quality: 9.4/10

Testing Quality: 9.5/10

AI Governance Quality: 10/10

Production Readiness: 9.7/10

Missing Area:

Backend Systems Constitution

This file closes that gap.

---

# CORE PHILOSOPHY

Backend exists to protect business rules.

Frontend can be replaced.

Backend is the source of truth.

Always prioritize:

1. Security
2. Correctness
3. Reliability
4. Data Integrity
5. Scalability
6. Maintainability
7. Observability
8. Performance

Never prioritize:

- shorter code
- clever code
- faster generation
- fewer files

---

# REQUIRED ANALYSIS BEFORE CODING

Before generating ANY code:

Analyze:

Business Context

Example:

SaaS CRM

Questions:

- Who owns data?
- Who can access data?
- What is sensitive?
- What is auditable?
- What can fail?

---

Analyze:

Security Context

Example:

Authentication
Payments
Admin Actions

Questions:

- Attack surface?
- Privilege escalation?
- Data leakage?
- Abuse vectors?

---

Analyze:

Scalability Context

Questions:

- Expected users?
- Concurrent traffic?
- Heavy queries?
- Background jobs?

---

Analyze:

Failure Context

Questions:

- What breaks?
- How does recovery happen?
- What happens if Redis fails?
- What happens if Stripe fails?

---

# BACKEND THINKING MODEL

Always think:

Business
↓
Domain
↓
Workflow
↓
API
↓
Database
↓
Infrastructure

Never:

Controller
↓
Database

---

# ENTERPRISE LAYER ARCHITECTURE

Mandatory:

API Layer
↓
Application Layer
↓
Domain Layer
↓
Infrastructure Layer

Forbidden:

Controller
↓
Prisma
↓
Database

---

# DOMAIN FIRST DESIGN

Every system must have:

Authentication

Billing

Organizations

Projects

Notifications

Audit

Permissions

as independent domains.

Domains own:

- workflows
- validation
- permissions
- business rules

---

# NESTJS GOLDEN RULES

Use:

- Modules
- Providers
- Guards
- Interceptors
- Filters

Avoid:

- fat controllers
- business logic in controllers
- direct Prisma usage in controllers

Controllers are transport layer only.

---

# ANTI-HALLUCINATION RULES

AI MUST NEVER:

Invent:

- modules
- decorators
- providers
- repositories
- framework APIs

If unsure:

State uncertainty.

Do not hallucinate.

---

# CONTROLLER RULES

Controllers:

Maximum 10 executable lines.

Responsibilities:

- receive request
- validate request
- call service
- return response

Nothing else.

---

# SERVICE RULES

Services own:

- business logic
- orchestration
- workflows

Services NEVER own:

- SQL
- HTTP response objects
- infrastructure implementation

---

# REPOSITORY RULES

Repositories own:

- persistence
- query optimization
- database access

Repositories NEVER own:

- business logic
- permissions
- workflows

---

# DATABASE RULES

Database is:

Source of Truth.

Never trust:

- frontend payloads
- cached data
- client state

---

# SUPABASE RULES

Mandatory:

- RLS
- Policies
- Auditability
- Secure Storage

Never disable RLS.

---

# PRISMA RULES

Use:

- typed queries
- transactions
- migrations

Avoid:

- raw SQL unless justified

---

# TRANSACTION RULES

Use transactions when:

Multiple writes must succeed together.

Examples:

Create User
Create Organization
Assign Role

Atomicity required.

---

# REDIS RULES

Use for:

- caching
- rate limiting
- queues
- distributed locks

Never store source-of-truth business data.

---

# STRIPE RULES

Treat Stripe as eventually consistent.

Use:

- webhooks
- idempotency keys
- audit logs

Never trust client payment success.

---

# AUTHENTICATION RULES

Authentication answers:

Who are you?

Authorization answers:

What can you do?

Never mix them.

---

# AUTHORIZATION RULES

Use:

RBAC

AND

Resource Ownership

AND

Tenant Validation

Every request.

---

# MULTI-TENANCY RULES

Always verify:

- organization
- workspace
- tenant

on every query.

Cross-tenant access is critical severity.

---

# API DESIGN RULES

APIs are contracts.

Every endpoint requires:

- request schema
- response schema
- error schema

Use Zod.

---

# VALIDATION RULES

Validate:

- params
- queries
- headers
- body
- webhooks

Trust nothing.

---

# ERROR HANDLING RULES

Create:

Domain Exceptions

Examples:

PaymentFailed

SubscriptionExpired

InvalidTenant

InsufficientCredits

Avoid generic errors.

---

# OBSERVABILITY RULES

Every feature requires:

Logs

Metrics

Tracing

Auditability

Invisible systems are broken systems.

---

# SECURITY RULES

Protect against:

- XSS
- CSRF
- SSRF
- SQL Injection
- Privilege Escalation
- Broken Access Control

Follow OWASP.

---

# PERFORMANCE RULES

Optimize:

- query count
- index usage
- caching
- network round trips

Measure first.

---

# TESTING RULES

Required:

Unit Tests

Integration Tests

Contract Tests

Critical Paths:

E2E Tests

---

# AI SELF REVIEW

Before generating code:

Ask:

1. Is architecture correct?
2. Is security enforced?
3. Is tenant isolation enforced?
4. Is validation complete?
5. Is observability included?
6. Is testing included?
7. Is rollback strategy defined?
8. Is production readiness achieved?

If NO:

Generation is incomplete.

---

# DEFINITION OF DONE

A backend feature is complete only when:

✓ Business rules enforced

✓ Security enforced

✓ Validation complete

✓ Multi-tenancy protected

✓ Observability included

✓ Tests pass

✓ Performance reviewed

✓ Production ready

Anything less is incomplete.
