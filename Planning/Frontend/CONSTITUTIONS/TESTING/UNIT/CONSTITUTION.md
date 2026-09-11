# 02_UNIT_TESTING_CONSTITUTION.md

# Enterprise Unit Testing Constitution
Version: 1.0
Authority: Subordinate to
- 00_TESTING_SUPREME_CONSTITUTION
- 01_TEST_ARCHITECTURE_CONSTITUTION

## Mission

Validate every unit of business logic with deterministic, repeatable, maintainable, and production-grade automated tests.

Applies To:

- Next.js
- React
- NestJS
- TypeScript
- Node.js
- Prisma
- Domain Services
- Utilities
- Validation Logic
- Business Rules

---

# Unit Testing Philosophy

Unit tests exist to validate behavior.

Unit tests do NOT exist to:

- increase coverage numbers
- satisfy metrics
- test implementation details

Unit tests MUST validate:

- business outcomes
- business rules
- domain correctness

---

# Constitutional Principles

1. Business logic must be testable.
2. Untested business logic is a defect.
3. Every critical rule requires tests.
4. Deterministic tests only.
5. Fast feedback is mandatory.
6. Tests are production assets.
7. Quality over quantity.
8. Coverage alone is insufficient.

---

# Mandatory Coverage Areas

Required:

✓ Domain Services
✓ Utility Functions
✓ Validation Rules
✓ Mappers
✓ Transformers
✓ Calculators
✓ Authorization Rules
✓ Feature Flags
✓ Data Sanitization

Forbidden:

✗ Untested critical logic
✗ Hidden business rules
✗ Unverified calculations

---

# Enterprise Coverage Governance

Minimum Targets

Critical Business Logic:
100%

Security Logic:
100%

Financial Logic:
100%

Core Domain Services:
95%+

Overall Coverage:
85%+

Coverage is a floor.

Not a quality indicator.

---

# Test Classification

Tier 1:
Critical Business Tests

Tier 2:
Security Tests

Tier 3:
Financial Tests

Tier 4:
Domain Logic Tests

Tier 5:
Utility Tests

Higher tiers receive priority.

---

# Required Test Structure

Arrange

Act

Assert

AAA pattern is mandatory.

Avoid mixed structures.

---

# Naming Convention

Format:

should_<expected_behavior>_when_<condition>

Examples:

should_create_invoice_when_payment_succeeds

should_reject_request_when_user_is_unauthorized

should_expire_session_when_timeout_reached

---

# Mocking Constitution

Mock only:

- external services
- databases
- queues
- APIs
- cloud providers

Do NOT mock:

- domain logic
- business rules
- validation rules

Over-mocking is forbidden.

---

# Anti-Patterns

Forbidden:

- testing private methods
- testing implementation details
- random test data
- flaky tests
- timing dependent tests
- hidden assertions
- duplicate tests

---

# Deterministic Testing Rules

Required:

- repeatable execution
- predictable outcomes
- isolated execution

Tests must pass consistently on:

- local
- CI
- staging

---

# Mutation Testing Governance

Required for:

- financial systems
- authentication systems
- authorization systems
- critical business domains

Target:

Mutation Score > 80%

Low mutation scores indicate weak tests.

---

# Security Logic Testing

Required:

- authorization rules
- role validation
- permissions
- access control
- token validation

Security logic requires 100% coverage.

---

# Financial Logic Testing

Required:

- billing
- subscriptions
- pricing
- invoices
- taxation

Financial logic requires:

100% branch coverage.

---

# AI Generated Test Governance

AI-generated tests must:

- be reviewed
- be deterministic
- validate behavior
- avoid hallucinated assertions

AI tests are never trusted automatically.

---

# Test Data Governance

Required:

- explicit fixtures
- controlled factories
- deterministic datasets

Forbidden:

- production data
- hidden dependencies
- mutable shared state

---

# Enterprise Quality Scoring

Evaluate:

- correctness
- maintainability
- readability
- isolation
- determinism
- business value

A passing test suite may still fail quality review.

---

# CI/CD Quality Gates

Required:

✓ Type Check Pass
✓ Lint Pass
✓ Unit Test Pass
✓ Coverage Gate Pass
✓ Security Gate Pass

Pipeline failure blocks deployment.

---

# Definition of Done

Unit testing is complete only when:

✓ Business logic validated
✓ Security logic validated
✓ Financial logic validated
✓ Edge cases validated
✓ Error paths validated
✓ Coverage targets achieved
✓ Quality gates passed

Anything less is incomplete.

End of Constitution.
