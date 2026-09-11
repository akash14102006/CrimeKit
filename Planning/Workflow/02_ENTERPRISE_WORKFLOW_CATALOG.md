# 02_ENTERPRISE_WORKFLOW_CATALOG.md

# CrimeKit Enterprise Workflow Catalog

> Version: 1.0 Purpose: Defines every business workflow executed by the
> CrimeKit Workflow Engine.

------------------------------------------------------------------------

# 1. Workflow Catalog Overview

The Workflow Engine orchestrates every investigation using independent,
reusable workflows.

``` text
Upload
   ↓
Validation
   ↓
Storage
   ↓
Processing
   ↓
AI Investigation
   ↓
Human Review
   ↓
Reporting
   ↓
Notification
   ↓
Archive
```

------------------------------------------------------------------------

# 2. Upload Workflow

## Goal

Securely ingest evidence while preserving integrity.

### Trigger

-   Investigator uploads evidence.

### Activities

-   Validate request
-   Chunk upload
-   Resume upload
-   SHA-256 generation
-   Duplicate detection
-   Malware scan
-   Store in MinIO
-   Register metadata
-   Create chain of custody
-   Start processing workflow

### Outputs

-   Evidence ID
-   Case linkage
-   Audit record

### Failure Recovery

-   Resume interrupted uploads
-   Retry storage failures
-   Preserve original evidence

------------------------------------------------------------------------

# 3. Evidence Processing Workflow

## Goal

Convert raw evidence into structured forensic artifacts.

### Supported Types

-   Disk Images
-   Mobile
-   Documents
-   Images
-   Videos
-   Audio
-   Email
-   Chats

### Activities

-   Classify evidence
-   Dispatch to forensic engine
-   Run extraction
-   Normalize artifacts
-   Store outputs

Outputs: - Structured artifacts - Metadata - Timeline events

------------------------------------------------------------------------

# 4. AI Investigation Workflow

## Goal

Generate explainable investigative intelligence.

### Child Workflows

-   Detective Agent
-   Timeline Agent
-   Correlation Agent
-   GeoScope Agent
-   Testimony Agent
-   Evidence QA
-   Report Agent

Activities - Entity extraction - Relationship discovery - Timeline
correlation - Risk scoring - Evidence summarization

Output - Explainable AI findings - Confidence scores - Evidence
references

Human validation is mandatory before legal conclusions.

------------------------------------------------------------------------

# 5. Knowledge Workflow

Activities

-   Artifact normalization
-   Entity linking
-   Neo4j graph updates
-   Vector embedding generation
-   Elasticsearch indexing
-   Timeline indexing

Outputs

-   Knowledge Graph
-   Semantic Search
-   Timeline
-   Similarity Search

------------------------------------------------------------------------

# 6. Report Workflow

Activities

-   Collect artifacts
-   Merge AI findings
-   Generate timeline
-   Generate court package
-   Export PDF
-   Export DOCX
-   Export JSON
-   Export ZIP evidence package

Outputs

-   Court-ready report
-   Investigation summary
-   Evidence package

------------------------------------------------------------------------

# 7. Notification Workflow

Triggers

-   Upload complete
-   Analysis complete
-   Report generated
-   Assignment
-   Failure
-   Archive complete

Channels

-   Email
-   SMS
-   Push
-   Webhooks

Retry

-   Exponential backoff
-   Dead-letter queue

------------------------------------------------------------------------

# 8. Archive Workflow

Activities

-   Verify completion
-   Lock evidence
-   Archive metadata
-   Backup objects
-   Retention policy
-   Immutable audit log

Outputs

-   Archived case
-   Backup confirmation

------------------------------------------------------------------------

# 9. Common Workflow Contract

Every workflow defines:

-   Business Goal
-   Trigger
-   Preconditions
-   Inputs
-   Activities
-   Child Workflows
-   Outputs
-   Retry Policy
-   Timeout Policy
-   Compensation
-   Security
-   Metrics
-   Audit Events
-   Acceptance Criteria

------------------------------------------------------------------------

# 10. Enterprise Standards

-   Stateless workflows
-   Idempotent activities
-   Immutable evidence
-   Complete audit trail
-   Human approval before court reporting
-   Observability for every execution
-   Versioned workflow definitions

------------------------------------------------------------------------

# 11. Acceptance Criteria

-   Every workflow independently testable
-   Automatic retry for transient failures
-   Explainable AI
-   Chain of custody preserved
-   End-to-end traceability
-   Production-ready orchestration

------------------------------------------------------------------------

# 12. Guiding Statement

Every CrimeKit investigation follows a predictable, secure, observable
workflow that transforms uploaded evidence into verified forensic
intelligence while preserving integrity, explainability, and legal
traceability.
