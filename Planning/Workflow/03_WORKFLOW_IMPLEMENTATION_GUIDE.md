# 03_WORKFLOW_IMPLEMENTATION_GUIDE.md

# CrimeKit Workflow Implementation Guide

> Version: 1.0 Audience: Backend Developers, AI Engineers, DevOps, QA,
> AI Coding Agents

------------------------------------------------------------------------

# 1. Purpose

This guide explains how to implement the CrimeKit Workflow Engine in
production using Temporal, FastAPI, PostgreSQL, MinIO, Neo4j,
Elasticsearch, pgvector, Docker, and Kubernetes.

------------------------------------------------------------------------

# 2. Recommended Folder Structure

``` text
workflows/
├── temporal/
├── upload/
├── processing/
├── ai/
├── report/
├── notifications/
├── shared/
├── activities/
├── workers/
├── interceptors/
├── schemas/
└── tests/
```

## Responsibilities

-   **temporal/**: Parent workflows, child workflows, schedules,
    versioning.
-   **activities/**: Small idempotent business operations.
-   **workers/**: Register activities and poll task queues.
-   **shared/**: Retry policies, constants, utilities.
-   **schemas/**: Typed payloads and workflow contracts.
-   **tests/**: Workflow and activity tests.

------------------------------------------------------------------------

# 3. Workflow Rules

-   Workflows orchestrate only.
-   No database queries inside workflows.
-   No HTTP requests inside workflows.
-   Activities perform external work.
-   Every workflow must be deterministic.
-   Use typed request/response payloads.

------------------------------------------------------------------------

# 4. Activity Standards

Every activity should include:

-   Single responsibility
-   Idempotency
-   Timeouts
-   Retries
-   Structured logging
-   Metrics
-   Exception mapping
-   Cancellation support

------------------------------------------------------------------------

# 5. Worker Architecture

Worker Types

-   Upload Worker
-   OCR Worker
-   Image Worker
-   Video Worker
-   Audio Worker
-   AI Worker
-   Report Worker
-   Notification Worker

Recommendations

-   Dedicated task queues
-   Horizontal scaling
-   Health probes
-   Graceful shutdown

------------------------------------------------------------------------

# 6. Queue Topology

Critical: - evidence-critical

High: - upload-high - processing-high

Normal: - ai-normal - reports-normal

Low: - notifications-low - archive-low

Dead Letter Queue for permanent failures.

------------------------------------------------------------------------

# 7. Retry Strategy

Retry

-   Network timeout
-   Storage timeout
-   Temporary AI outage

Do Not Retry

-   Invalid payload
-   Authorization failure
-   Hash mismatch

Use exponential backoff with maximum retry limits.

------------------------------------------------------------------------

# 8. Signals, Queries & Updates

Signals

-   Pause Investigation
-   Resume Investigation
-   Cancel Investigation

Queries

-   Current Status
-   Progress
-   Active Stage

Updates

-   Assign Investigator
-   Change Priority
-   Add Metadata

------------------------------------------------------------------------

# 9. Versioning

-   Version every workflow.
-   Never break running executions.
-   Introduce new activities instead of modifying old contracts.
-   Maintain backward compatibility.

------------------------------------------------------------------------

# 10. Security

-   JWT propagation
-   RBAC
-   Secret management
-   TLS
-   Encrypted storage
-   Audit trail
-   Immutable evidence

------------------------------------------------------------------------

# 11. Observability

Log Fields

-   Workflow ID
-   Activity ID
-   Case ID
-   Evidence ID
-   Request ID
-   Duration
-   Retry Count

Metrics

-   Workflow latency
-   Activity latency
-   Queue depth
-   Success rate
-   Failure rate

Tracing

-   OpenTelemetry
-   Temporal UI
-   Grafana
-   Prometheus

------------------------------------------------------------------------

# 12. Docker Deployment

Containers

-   API
-   Temporal
-   PostgreSQL
-   Redis
-   MinIO
-   Neo4j
-   Elasticsearch
-   Worker Services

Recommendations

-   Environment variables
-   Health checks
-   Persistent volumes
-   Resource limits

------------------------------------------------------------------------

# 13. Kubernetes

Deploy

-   API Deployment
-   Worker Deployments
-   Horizontal Pod Autoscaler
-   Ingress
-   ConfigMaps
-   Secrets
-   Persistent Volumes

------------------------------------------------------------------------

# 14. CI/CD

Pipeline

1.  Lint
2.  Unit Tests
3.  Workflow Tests
4.  Integration Tests
5.  Build Image
6.  Security Scan
7.  Deploy Staging
8.  Smoke Test
9.  Production Deployment

------------------------------------------------------------------------

# 15. Testing Strategy

Unit Tests

-   Activities

Integration Tests

-   Workflow orchestration

Load Tests

-   Concurrent uploads
-   Large evidence

Chaos Tests

-   Worker crashes
-   Database outages

Recovery Tests

-   Retry validation
-   Compensation validation

------------------------------------------------------------------------

# 16. Coding Standards

Do

-   Keep workflows thin
-   Write reusable activities
-   Use typed payloads
-   Emit metrics
-   Document contracts

Don't

-   Put business logic in workflows
-   Access databases from workflows
-   Ignore retries
-   Share mutable state

------------------------------------------------------------------------

# 17. Production Checklist

-   Deterministic workflows
-   Idempotent activities
-   Monitoring enabled
-   Alerting configured
-   Audit logging enabled
-   Backups verified
-   Security review complete
-   Disaster recovery tested

------------------------------------------------------------------------

# 18. Developer Checklist

-   Follow folder structure
-   Write tests first
-   Version changes
-   Document APIs
-   Review telemetry
-   Validate retries
-   Verify chain of custody

------------------------------------------------------------------------

# 19. Final Principles

1.  Reliability over speed.
2.  Security over convenience.
3.  Explainability over automation.
4.  Deterministic orchestration.
5.  Human oversight for legal outcomes.
6.  Observable systems by default.
7.  Production-ready from day one.
