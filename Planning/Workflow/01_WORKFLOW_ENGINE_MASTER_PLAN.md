# 01_WORKFLOW_ENGINE_MASTER_PLAN.md

# CrimeKit Workflow Engine -- Enterprise Master Plan

> Version: 1.0 Status: Architecture Constitution

------------------------------------------------------------------------

# 1. Purpose

This document is the single architectural blueprint for the CrimeKit
Workflow Engine.

It defines how long-running business processes are orchestrated using
Temporal, how forensic services collaborate, how AI pipelines execute
safely, and how every workflow remains deterministic, auditable,
scalable, and production-ready.

------------------------------------------------------------------------

# 2. Vision

Build an enterprise-grade workflow platform that:

-   Orchestrates every investigation from evidence upload to archival.
-   Preserves chain of custody.
-   Coordinates forensic engines and AI agents.
-   Survives failures automatically.
-   Produces explainable, court-ready outputs.
-   Scales horizontally across distributed workers.

------------------------------------------------------------------------

# 3. Guiding Principles

1.  Workflow orchestration, not business logic.
2.  Activities are idempotent.
3.  Evidence is immutable.
4.  Human approval before legal conclusions.
5.  Every state transition is auditable.
6.  Retries are automatic for transient failures.
7.  Observability is mandatory.
8.  Security by default.
9.  Deterministic workflow execution.
10. Version every workflow.

------------------------------------------------------------------------

# 4. High-Level Architecture

``` text
Investigator
      │
      ▼
Evidence Upload
      │
FastAPI
      │
SHA256 + Malware Scan
      │
MinIO + PostgreSQL
      │
Temporal Parent Workflow
      │
├── Upload Workflow
├── Processing Workflow
├── AI Workflow
├── Report Workflow
├── Notification Workflow
└── Archive Workflow
      │
Forensic Engines
      │
Artifact Normalization
      │
Knowledge Graph + Search + Vectors
      │
LangGraph Supervisor
      │
Human Review
      │
Court-ready Report
```

------------------------------------------------------------------------

# 5. Workflow Layers

-   API Layer
-   Workflow Layer (Temporal)
-   Activity Layer
-   Domain Services
-   Forensic Engines
-   AI Orchestration
-   Storage Layer
-   Notification Layer
-   Monitoring Layer

------------------------------------------------------------------------

# 6. Folder Structure

``` text
workflows/
│
├── temporal/
├── upload/
├── processing/
├── ai/
├── report/
├── notifications/
├── shared/
├── activities/
├── workers/
├── schemas/
└── tests/
```

Responsibilities:

-   temporal/: parent workflows, child workflows, schedules.
-   upload/: evidence intake lifecycle.
-   processing/: forensic orchestration.
-   ai/: LangGraph orchestration.
-   report/: report generation.
-   notifications/: email, SMS, push.
-   shared/: constants, helpers, retry policies.
-   activities/: Temporal activities only.
-   workers/: worker registration.
-   schemas/: workflow payload contracts.
-   tests/: workflow/activity tests.

------------------------------------------------------------------------

# 7. Parent Workflow

The Parent Workflow coordinates the entire investigation lifecycle.

Stages:

1.  Intake
2.  Validation
3.  Storage
4.  Processing
5.  AI
6.  Human Review
7.  Reporting
8.  Notification
9.  Archive

------------------------------------------------------------------------

# 8. Child Workflows

-   Upload Workflow
-   Evidence Processing Workflow
-   AI Investigation Workflow
-   Report Workflow
-   Notification Workflow
-   Archive Workflow
-   Reprocessing Workflow

Each child workflow owns one business capability.

------------------------------------------------------------------------

# 9. Activity Design Rules

Every activity must:

-   Be idempotent
-   Be retry-safe
-   Avoid shared mutable state
-   Return structured outputs
-   Emit telemetry
-   Support cancellation
-   Use timeouts
-   Never perform orchestration

------------------------------------------------------------------------

# 10. Queue Strategy

Priority Queues:

-   critical
-   high
-   normal
-   low

Dedicated queues:

-   OCR
-   Video
-   Audio
-   AI
-   Reports
-   Notifications

------------------------------------------------------------------------

# 11. Retry Policy

Retry automatically for:

-   Network failures
-   Temporary database outages
-   Object storage timeouts
-   AI provider timeout

Do not retry:

-   Invalid evidence
-   Authorization failures
-   Corrupted files

------------------------------------------------------------------------

# 12. Workflow States

PENDING ↓ RUNNING ↓ WAITING ↓ COMPLETED

Failure path:

RUNNING ↓ FAILED ↓ RETRYING ↓ FAILED_PERMANENTLY

------------------------------------------------------------------------

# 13. Security

-   JWT context propagation
-   RBAC
-   Encrypted secrets
-   Immutable evidence
-   SHA-256 integrity
-   Audit logging
-   Least privilege

------------------------------------------------------------------------

# 14. Observability

Every workflow records:

-   Workflow ID
-   Parent ID
-   Request ID
-   Case ID
-   Evidence ID
-   User ID
-   Start Time
-   End Time
-   Duration
-   Retry Count
-   Failure Reason

Metrics:

-   Success rate
-   Queue latency
-   Activity latency
-   Worker utilization
-   AI latency

------------------------------------------------------------------------

# 15. Error Recovery

Recoverable: - Worker crash - Storage timeout - API timeout

Non-recoverable: - Invalid evidence - Integrity mismatch - Permission
denied

Compensation actions roll back metadata while preserving original
evidence.

------------------------------------------------------------------------

# 16. Performance Strategy

-   Parallel child workflows
-   Horizontal worker scaling
-   Streaming uploads
-   Batched activities
-   Async execution
-   Continue-As-New for long cases

------------------------------------------------------------------------

# 17. Deployment

-   Docker
-   Kubernetes
-   Temporal Cluster
-   Redis
-   PostgreSQL
-   MinIO
-   Neo4j
-   Elasticsearch
-   pgvector

------------------------------------------------------------------------

# 18. Coding Standards

-   Thin workflows
-   Small activities
-   Domain logic inside services
-   No database access inside workflows
-   Strong typing
-   Versioned payloads

------------------------------------------------------------------------

# 19. Acceptance Criteria

-   Deterministic execution
-   Automatic recovery
-   Full audit trail
-   Explainable AI orchestration
-   Production-grade scalability
-   Complete chain of custody

------------------------------------------------------------------------

# 20. Guiding Statement

The CrimeKit Workflow Engine exists to orchestrate secure, explainable,
fault-tolerant investigations by coordinating forensic processing, AI
reasoning, human validation, and reporting through deterministic
enterprise workflows.
