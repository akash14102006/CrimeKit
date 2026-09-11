# 04_INTEGRATION_TESTING_CONSTITUTION.md

# Enterprise Integration Testing Constitution
Version: 1.0
Authority:
- 00_TESTING_SUPREME_CONSTITUTION
- 01_TEST_ARCHITECTURE_CONSTITUTION
- 02_UNIT_TESTING_CONSTITUTION
- 03_COMPONENT_TESTING_CONSTITUTION

## Mission

Validate that all enterprise systems communicate correctly, securely, reliably, and consistently under real-world production conditions.

Applies To:

- Next.js ↔ NestJS
- NestJS ↔ PostgreSQL
- Prisma ↔ PostgreSQL
- NestJS ↔ Redis
- NestJS ↔ Stripe
- NestJS ↔ Supabase
- External APIs
- Message Queues
- Event Systems
- Microservices

---

# Integration Testing Philosophy

Most production failures occur:

NOT inside units.

BUT between systems.

Integration testing exists to validate:

✓ Communication
✓ Contracts
✓ Transactions
✓ Reliability
✓ Recovery

---

# Constitutional Principles

1. Every integration is a risk boundary.
2. Every dependency can fail.
3. Every timeout must be tested.
4. Every retry must be validated.
5. Every transaction must be verified.
6. Realistic environments are required.
7. Failure paths are first-class citizens.

---

# Mandatory Integration Coverage

Validate:

✓ Success Paths
✓ Failure Paths
✓ Retry Paths
✓ Timeout Paths
✓ Partial Failures
✓ Recovery Paths

Testing only happy paths is forbidden.

---

# API Integration Testing

Required:

✓ Request Validation
✓ Response Validation
✓ Authentication
✓ Authorization
✓ Pagination
✓ Filtering
✓ Sorting
✓ Error Handling

Never trust external responses.

---

# Database Integration Constitution

Validate:

✓ Queries
✓ Transactions
✓ Rollbacks
✓ Constraints
✓ Relationships
✓ Indexes

Database behavior must match production.

---

# Prisma Integration Testing

Validate:

✓ Schema Mapping
✓ Transactions
✓ Relations
✓ Migrations
✓ Query Correctness

Untested migrations are forbidden.

---

# Redis Integration Testing

Validate:

✓ Cache Population
✓ Cache Invalidation
✓ TTL Expiration
✓ Cache Recovery

Cache consistency is mandatory.

---

# Stripe Integration Testing

Required:

✓ Payments
✓ Refunds
✓ Webhooks
✓ Subscription Events
✓ Billing Events

Financial integrations require:

100% critical path validation.

---

# Supabase Integration Testing

Validate:

✓ Authentication
✓ Authorization
✓ Session Management
✓ RLS Policies
✓ User Lifecycle

Tenant isolation must be verified.

---

# Queue & Event Testing

Validate:

✓ Event Publishing
✓ Event Consumption
✓ Retries
✓ Dead Letter Queues
✓ Idempotency

Message loss is unacceptable.

---

# Security Validation

Required:

✓ Auth Validation
✓ Permission Validation
✓ Data Protection
✓ Tenant Isolation
✓ Secret Protection

Security defects block release.

---

# Failure Injection Testing

Simulate:

✓ Network Failure
✓ Database Failure
✓ Cache Failure
✓ Third-Party Failure
✓ Timeout Failure

Recovery behavior must be validated.

---

# Test Environment Governance

Required:

- Production-like environments
- Isolated test environments
- Repeatable test datasets

Environment drift is forbidden.

---

# Enterprise Quality Gates

Required:

✓ Integration Tests Pass
✓ Transaction Validation Pass
✓ Security Validation Pass
✓ Recovery Validation Pass
✓ Dependency Validation Pass

Failure blocks deployment.

---

# Anti-Patterns

Forbidden:

✗ Mocking entire integrations
✗ Happy-path-only testing
✗ Untested retries
✗ Untested transactions
✗ Untested failures

---

# Definition of Done

Integration testing is complete only when:

✓ System boundaries validated
✓ Transactions validated
✓ Failures validated
✓ Recovery validated
✓ Security validated
✓ Third-party integrations validated
✓ Production behavior validated

Anything less is incomplete.

End of Constitution.
