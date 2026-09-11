# 02_AUTH_CASES.md

# CrimeKit Backend – Authentication & Case Management
**Module:** backend/auth + backend/cases

---

# 1. Purpose

This document defines the enterprise architecture for Authentication and Case Management in CrimeKit.

Authentication protects every resource in the platform.

Case Management is the central business domain that connects investigators, evidence, AI analysis, forensic processing, reports, timelines, and audit logs.

Every operation in CrimeKit belongs to a Case.

---

# 2. Objectives

- Secure user authentication
- Role-based authorization
- Investigator identity verification
- Session management
- Case lifecycle management
- Team collaboration
- Evidence ownership
- Complete audit trail
- Human accountability

---

# 3. Folder Structure

```text
backend/
├── auth/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── permissions/
│   ├── tokens/
│   └── utils/
│
├── cases/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── workflow/
│   ├── audit/
│   └── utils/
```

---

# 4. Authentication Responsibilities

Authentication module owns:

- Login
- Logout
- JWT lifecycle
- Refresh tokens
- Password hashing
- Password reset
- Email verification
- MFA (future)
- User profile
- Roles
- Permissions
- Account status
- Session tracking
- Audit logging

Authentication never manages evidence or cases.

---

# 5. Roles

Example roles:

- System Administrator
- Investigation Supervisor
- Child Protection Investigator
- Digital Forensic Analyst
- Legal Reviewer
- Read-only Auditor

Every endpoint checks permissions before execution.

---

# 6. Authorization Principles

- Least privilege
- Role-based access control
- Case-level permissions
- Resource ownership
- Immutable audit history

---

# 7. Case Domain

A Case is the primary business entity.

Everything belongs to a Case:

- Evidence
- Reports
- Timeline
- AI Findings
- Notes
- Tasks
- Investigators
- Audit Logs

---

# 8. Case Lifecycle

```text
Draft

↓

Open

↓

Evidence Collection

↓

Forensic Processing

↓

AI Investigation

↓

Review

↓

Court Report

↓

Closed

↓

Archived
```

Closed cases remain immutable except for authorized administrative actions.

---

# 9. Case Information

Each case maintains:

- Case ID
- Title
- Description
- Priority
- Status
- Assigned team
- Lead investigator
- Evidence count
- Report status
- Created date
- Updated date
- Closure date

---

# 10. Team Collaboration

Each case supports:

- Multiple investigators
- Supervisors
- Reviewers
- Assignment history
- Activity feed

No anonymous actions are allowed.

---

# 11. Authentication Flow

```text
User

↓

Login

↓

Credential Validation

↓

JWT Generation

↓

Permission Resolution

↓

API Access

↓

Audit Log
```

---

# 12. Case Request Flow

```text
Create Case

↓

Generate Case ID

↓

Assign Owner

↓

Store Metadata

↓

Initialize Timeline

↓

Ready for Evidence Upload
```

---

# 13. Security Rules

- Strong password policy
- JWT expiration
- Refresh token rotation
- Account lock after repeated failures
- Audit every login
- Audit permission changes
- Audit case ownership changes

---

# 14. Audit Requirements

Every important action records:

- User ID
- Case ID
- Action
- Timestamp
- IP
- Device
- Request ID

Audit history cannot be edited.

---

# 15. API Overview

Authentication APIs:

- Login
- Logout
- Refresh Token
- Profile
- Change Password

Case APIs:

- Create Case
- Update Case
- Assign Members
- Get Case
- Search Cases
- Close Case
- Archive Case

---

# 16. Integration

Authentication integrates with:

- Middleware
- API Layer
- Services

Cases integrate with:

- Evidence
- Uploads
- Reports
- AI Agents
- Workflow Engine
- Database

---

# 17. Acceptance Criteria

Authentication is complete when:

- Secure login works
- JWT validation works
- Roles are enforced
- Audit logs are generated

Case Management is complete when:

- Cases can be created
- Members assigned
- Evidence linked
- Lifecycle tracked
- History preserved

---

# 18. Developer Checklist

- Never expose passwords
- Never trust client roles
- Validate every request
- Protect every endpoint
- Keep business logic in services
- Maintain complete audit history
- Every evidence item must belong to one Case
- Every report must belong to one Case

---

# 19. Guiding Principle

Authentication establishes trust.

Case Management establishes investigative context.

Together they provide the secure foundation upon which every CrimeKit workflow operates.
