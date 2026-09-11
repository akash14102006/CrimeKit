# CrimeKit Face Trace Investigator — BACKEND SPECIFICATION

**Document:** `BACKEND.md`  
**Subsystem:** Face Trace Investigator  
**Primary backend:** Existing CrimeKit backend architecture (FastAPI where applicable)  
**Audience:** Backend, forensic, ML, database, security, workflow, infrastructure, QA engineers  
**Status:** Authoritative backend implementation specification

---

# 1. PURPOSE

This document defines the backend implementation contract for CrimeKit Face Trace Investigator.

The backend must provide a secure, asynchronous, evidence-first execution environment for:

- reference-face processing
- face-search job creation
- video processing
- face detection
- tracking
- embedding generation
- similarity matching
- sighting aggregation
- provenance
- persistence
- real-time event publication
- investigator review

The backend must integrate into existing CrimeKit architecture.

It must not create a second application architecture inside the application.

---

# 2. BACKEND RESPONSIBILITY

The backend owns:

1. Authentication integration
2. Authorization
3. Case scoping
4. Evidence authorization
5. Input validation
6. Investigation lifecycle
7. Job lifecycle
8. Workflow invocation
9. Domain rules
10. Face-service orchestration
11. Persistence
12. Provenance
13. Candidate semantics
14. Review operations
15. Event publication
16. Audit
17. Error handling
18. Observability

The backend does not own:

- frontend rendering
- investigator visual layout
- browser state
- model training
- legal conclusions

---

# 3. EXISTING CRIMEKIT INTEGRATION FIRST

Before implementation, identify the current:

- FastAPI application entry point
- router structure
- dependency injection
- authentication middleware
- RBAC implementation
- case service
- evidence service
- evidence storage
- workflow system
- worker architecture
- PostgreSQL session/repository pattern
- vector storage implementation
- Neo4j integration
- Redis/event infrastructure
- WebSocket gateway
- audit system
- error-handling conventions
- configuration system
- testing conventions

Do not assume the paths shown in this document exist.

Adapt to the real repository.

---

# 4. BACKEND LAYERING

Preferred logical layers:

    HTTP/API
       ↓
    Application Service
       ↓
    Domain Logic
       ↓
    Repository / Infrastructure
       ↓
    External Systems

For face intelligence:

    Face Router
       ↓
    Face Investigation Service
       ↓
    Face Domain
       ↓
    Workflow/Worker
       ↓
    InsightFace Adapter / Processing
       ↓
    Persistence/Event Infrastructure

Do not put the entire feature inside the router.

---

# 5. API DESIGN PRINCIPLE

HTTP endpoints should:

- authenticate
- authorize
- validate
- create commands
- retrieve state
- return results

Long-running computation must not run inside the ordinary request lifecycle.

---

# 6. RESOURCE MODEL

Conceptual resources:

    FaceInvestigation
    FaceReference
    FaceSearchJob
    FaceProcessingRun
    FaceDetection
    FaceTrack
    FaceCandidate
    FaceSighting
    FaceReview

The actual persistence model must follow existing CrimeKit naming conventions.

---

# 7. RECOMMENDED API SURFACE

Use existing CrimeKit API versioning and route conventions.

Conceptual endpoints:

    POST /api/v1/cases/{case_id}/face-investigations

    GET /api/v1/cases/{case_id}/face-investigations

    GET /api/v1/face-investigations/{investigation_id}

    POST /api/v1/face-investigations/{investigation_id}/reference

    GET /api/v1/face-investigations/{investigation_id}/reference

    POST /api/v1/face-investigations/{investigation_id}/search

    POST /api/v1/face-investigations/{investigation_id}/cancel

    GET /api/v1/face-investigations/{investigation_id}/sightings

    GET /api/v1/face-sightings/{sighting_id}

    POST /api/v1/face-sightings/{sighting_id}/review

The exact endpoint names must be reconciled with the existing CrimeKit API.

Do not introduce duplicate naming styles.

---

# 8. API 1 — CREATE INVESTIGATION

Conceptual:

    POST /cases/{case_id}/face-investigations

Purpose:

Create an authorized Face Trace investigation.

Input may contain:

    title
    description
    search_scope
    selected_evidence_ids

Validation:

1. Authenticate user.
2. Verify case access.
3. Verify feature permission.
4. Validate selected evidence belongs to accessible case/scope.
5. Create investigation.
6. Create audit record.

Response:

    investigation_id
    case_id
    status
    created_at

Do not start heavy processing from this endpoint.

---

# 9. API 2 — UPLOAD REFERENCE

Conceptual:

    POST /face-investigations/{id}/reference

Sequence:

    authenticate
       ↓
    authorize case
       ↓
    authorize investigation
       ↓
    validate upload
       ↓
    store source artifact
       ↓
    enqueue reference processing
       ↓
    return processing state

Do not directly perform expensive model inference inside the HTTP request.

---

# 10. REFERENCE UPLOAD VALIDATION

Validate:

- authenticated user
- case ownership/access
- investigation access
- file size
- supported MIME
- extension
- file content
- image decoding
- maximum dimensions

Uploaded content is untrusted.

Use existing CrimeKit secure-upload mechanisms.

---

# 11. REFERENCE PROCESSING JOB

Create a dedicated processing operation conceptually:

    REFERENCE_VALIDATION_JOB

Stages:

    CREATED
       ↓
    QUEUED
       ↓
    DECODING
       ↓
    DETECTING
       ↓
    QUALITY_CHECK
       ↓
    EMBEDDING
       ↓
    VALIDATING
       ↓
    COMPLETED

Failure:

    FAILED

---

# 12. REFERENCE FACE COUNT

The backend must interpret detector output.

Cases:

## Zero faces

Return:

    NO_FACE

and a clear investigator-facing status.

## One usable face

Continue.

## Multiple faces

Return an explicit ambiguity state.

Do not silently use the first detected face.

---

# 13. REFERENCE QUALITY

The backend receives a structured quality result.

Example:

    quality_state
    face_size
    blur
    pose
    occlusion
    detection_score

The exact fields depend on the implemented quality service.

Persist the policy/version used.

---

# 14. REFERENCE EMBEDDING

After successful validation:

    reference face
       ↓
    InsightFace adapter
       ↓
    embedding
       ↓
    validate dimension
       ↓
    validate numerical values
       ↓
    persist

Store the embedding according to protected biometric-data policy.

Do not return the raw vector to the frontend by default.

---

# 15. REFERENCE READY STATE

Only set:

    REFERENCE_READY

after:

- reference artifact is valid
- intended face is resolved
- quality policy passes
- embedding is valid
- model metadata is recorded
- persistence succeeds

Do not mark the reference ready simply because the image uploaded.

---

# 16. API 3 — START SEARCH

Conceptual:

    POST /face-investigations/{id}/search

Input:

    selected_evidence_ids
    matching_policy_id
    optional_processing_profile

Validation:

1. Authenticate.
2. Authorize investigation.
3. Verify reference is READY.
4. Verify evidence access.
5. Validate search scope.
6. Create job.
7. Persist processing context.
8. Start workflow.
9. Publish job-created event.

Response:

    job_id
    status = QUEUED

---

# 17. SEARCH IDEMPOTENCY

A retrying client must not accidentally create duplicate searches.

Use an appropriate idempotency mechanism according to existing CrimeKit conventions.

Possible conceptual key:

    idempotency_key
       +
    investigation_id

Repeated request with same valid idempotency key should return the original operation where appropriate.

---

# 18. EVIDENCE AUTHORIZATION

Before processing each source:

    user
       ↓
    case access
       ↓
    evidence access
       ↓
    evidence eligibility

Do not trust that an evidence ID supplied by the frontend belongs to the case.

---

# 19. SEARCH JOB STATE MACHINE

Recommended:

    CREATED
       ↓
    QUEUED
       ↓
    PROCESSING
       ↓
    MATCHING
       ↓
    FINALIZING
       ↓
    COMPLETED

Error:

    FAILED

Cancellation:

    CANCELLING
       ↓
    CANCELLED

The actual workflow engine should enforce legal state transitions.

---

# 20. JOB STATE AUTHORITY

Only the domain/workflow layer should make authoritative state transitions.

Frontend does not set:

    COMPLETED

Worker does not arbitrarily set:

    CANCELLED

unless the workflow/domain command authorizes that transition.

---

# 21. WORKFLOW DESIGN

Use the existing CrimeKit workflow architecture.

If Temporal is the existing durable workflow system:

    FaceSearchWorkflow

may conceptually orchestrate:

    validate reference
    ↓
    process evidence
    ↓
    aggregate
    ↓
    finalize

If another workflow/queue engine already exists, integrate with it.

Do not add Temporal merely because this document mentions it.

---

# 22. WORKFLOW ACTIVITIES

Potential activities:

    validate_reference
    process_video
    process_image
    persist_detection
    persist_track
    generate_embeddings
    match_candidates
    aggregate_sightings
    project_graph
    publish_events

The actual workflow decomposition must match the existing platform.

Do not create hundreds of tiny activities without operational value.

---

# 23. WORKER RESPONSIBILITY

Workers execute processing.

They should not decide:

- case authorization
- investigator permission
- legal conclusions

Authorization should already be established by the command/workflow path.

Workers should still validate critical resource references before dangerous operations where needed.

---

# 24. FACE INFERENCE SERVICE

Provide an internal abstraction such as:

    FaceModelProvider

Conceptual methods:

    detect()
    embed()
    metadata()
    health()

The exact interfaces must follow the existing code style.

---

# 25. INSIGHTFACE ADAPTER

The backend must not scatter:

    insightface.app.FaceAnalysis

through unrelated modules.

Use one controlled adapter/service boundary.

Conceptually:

    FaceModelProvider
           ↓
    InsightFaceAdapter
           ↓
    InsightFace
           ↓
    ONNX Runtime

---

# 26. MODEL INITIALIZATION

Model loading belongs to worker/service lifecycle.

Do not load the model per request/frame.

Startup:

    configuration
       ↓
    artifact validation
       ↓
    runtime
       ↓
    model
       ↓
    smoke test
       ↓
    READY

---

# 27. MODEL METADATA

The processing context must record:

    provider
    model_id
    model_version
    detector_model
    recognition_model
    embedding_dimension
    preprocessing_version
    runtime_version
    execution_provider

Do not rely on current configuration months later to explain old results.

---

# 28. PROCESSING RUN

Create an explicit processing-run concept.

Example:

    processing_run_id

It identifies the execution context of a search.

Store:

    job
    evidence
    model
    preprocessing
    matching policy
    execution provider
    worker
    start/end
    outcome

---

# 29. VIDEO PROCESSING CONTRACT

Input:

    evidence artifact

Output stream:

    frame observations

    frame
      ↓
    detection
      ↓
    quality
      ↓
    track
      ↓
    embedding
      ↓
    match
      ↓
    candidate observation

The source evidence must remain immutable.

---

# 30. VIDEO STREAMING

Do not load an entire large video into memory.

Process incrementally.

Conceptually:

    decoder
      ↓
    bounded buffer
      ↓
    frame processor

Respect resource limits.

---

# 31. FRAME IDENTIFICATION

For every processed frame retain:

    evidence_id
    artifact_id
    frame_number where available
    source_timestamp
    processing_timestamp where useful
    processing_run_id

Source timestamp and processing timestamp are distinct.

---

# 32. FRAME SAMPLING

Use a configured processing profile.

Possible settings:

    recognition_sample_rate
    detector_rate
    tracking_rate

Record the profile used.

Do not hide the sampling strategy.

---

# 33. FACE DETECTION RECORD

Each detection should persist:

    detection_id
    evidence_id
    artifact_id
    frame_number
    timestamp
    bbox
    detector_score
    processing_run_id

Keypoints may be stored where useful and permitted.

---

# 34. BOUNDING BOX VALIDATION

Validate:

- coordinates finite
- x1 < x2
- y1 < y2
- bounds within frame
- non-zero dimensions

Invalid model output must not be persisted as a valid detection.

---

# 35. FACE QUALITY PROCESSING

Each eligible detection goes through:

    quality evaluator

Output:

    eligible
    or
    rejected

with machine-readable reason.

Do not silently discard all rejected observations without statistics.

---

# 36. TRACKING CONTRACT

Tracking input:

    frame detections

Tracking output:

    track observations

Each track:

    track_id
    source_evidence
    first_timestamp
    last_timestamp
    detection_ids
    tracker_version

Do not assign person identity to a track simply because it exists.

---

# 37. EMBEDDING GENERATION

Eligible track observations may generate embeddings.

The worker should avoid unnecessary repeated recognition.

Potential strategy:

    tracker runs frequently
       ↓
    recognition runs on selected observations
       ↓
    aggregate candidate observations

The policy must remain configurable.

---

# 38. MATCHING CONTRACT

Input:

    reference embedding
    candidate embedding
    matching policy
    quality context

Output:

    candidate observation

Persist:

    similarity
    quality context
    model metadata
    policy metadata
    source metadata

---

# 39. MATCHING THRESHOLD

Do not write:

    if similarity > 0.55

as a permanent business rule in the worker.

Instead:

    matching_policy
       ↓
    evaluate(candidate)

Threshold values must be configuration/policy data.

---

# 40. MATCHING POLICY MODEL

Conceptual:

    MatchingPolicy
      ├── id
      ├── version
      ├── metric
      ├── candidate_threshold
      ├── high_candidate_threshold
      ├── quality_rules
      └── aggregation_rules

The exact schema follows existing CrimeKit patterns.

---

# 41. CANDIDATE RECORD

Candidate should contain:

    candidate_id
    investigation_id
    evidence_id
    processing_run_id
    detection_id
    track_id
    similarity
    quality
    model_version
    matching_policy_version
    status
    created_at

Candidate is not a legal identity conclusion.

---

# 42. SIGHTING RECORD

Sighting aggregates candidate observations.

Conceptual:

    sighting_id
    candidate_id/group
    evidence_id
    track_id
    start_time
    end_time
    best_observation
    best_similarity
    observation_count
    processing_run_id

Underlying observations remain queryable.

---

# 43. SIGHTING AGGREGATOR

Aggregation inputs:

    candidate observations
    track
    timestamps

Output:

    sighting

The aggregator must be deterministic according to the configured policy.

---

# 44. MULTI-EVIDENCE PROCESSING

For multiple evidence sources:

    Job
      ├── Source A
      ├── Source B
      └── Source C

Each source gets independent processing.

Then:

    source sightings
       ↓
    investigation-level result

Do not accidentally share mutable tracker state between sources.

---

# 45. PROCESSING ISOLATION BETWEEN SOURCES

A failure in:

    CCTV-02

must not automatically destroy:

    CCTV-01

unless the workflow contract explicitly requires all-or-nothing processing.

Expose partial state.

---

# 46. PARTIAL SEARCH

Example:

    CCTV-01 = COMPLETED
    CCTV-02 = FAILED
    CCTV-03 = PROCESSING

Overall status should make this clear.

Do not claim:

    COMPLETED

if meaningful source scope remains unprocessed.

---

# 47. CANCELLATION

API:

    POST /face-investigations/{id}/cancel

Sequence:

    authorize
       ↓
    request cancellation
       ↓
    workflow transitions
       ↓
    workers stop new work
       ↓
    persisted outputs remain valid
       ↓
    CANCELLED

---

# 48. RETRIES

Retry transient failures.

Do not retry permanently invalid input indefinitely.

Classify failures:

    input
    transient infrastructure
    resource
    model
    configuration
    permanent

Use existing retry mechanisms.

---

# 49. IDEMPOTENT PERSISTENCE

Retries must not create duplicates.

Use stable identities such as:

    processing_run_id
    evidence_id
    frame_number
    detection sequence
    track namespace

where appropriate.

The exact key must be designed against the real data model.

---

# 50. TRANSACTION BOUNDARIES

Use transactions for logically coupled relational writes.

Example:

    Candidate
       +
    Provenance
       +
    initial review state

must not accidentally create an orphan candidate.

---

# 51. DISTRIBUTED WRITE MODEL

Do not assume:

    PostgreSQL
    +
    pgvector
    +
    Neo4j
    +
    Redis

share one ACID transaction.

Use an authoritative relational write followed by controlled projections/events where appropriate.

---

# 52. VECTOR PERSISTENCE

Store embeddings using the existing vector abstraction.

The backend must enforce:

    model compatibility
    dimension
    authorization
    correct metric

Do not expose vector database details directly to API consumers.

---

# 53. VECTOR SEARCH AUTHORIZATION

Authorization must be applied at the data-access/backend layer.

Incorrect:

    query all vectors
       ↓
    filter in React

Correct:

    authorized scope
       ↓
    vector query
       ↓
    authorized candidates

---

# 54. VECTOR INDEXING

Use an exact search strategy for initial small-scale implementation where appropriate.

Introduce approximate indexing only when measured scale requires it.

Benchmark:

    latency
    recall
    memory
    build/update cost

---

# 55. NEO4J PROJECTION

Neo4j projection should consume persisted face domain records.

Preferred:

    FaceSighting
       ↓
    graph projection
       ↓
    Neo4j

Do not let a raw inference callback arbitrarily create graph claims.

---

# 56. GRAPH EDGE PROVENANCE

Every face-derived graph relationship must be traceable back to:

    sighting
    evidence
    processing run

where the relationship represents an inference-derived association.

---

# 57. AUDIT EVENTS

Audit:

    investigation.created
    reference.uploaded
    reference.processed
    search.started
    search.cancelled
    source.viewed
    candidate.reviewed
    export.created
    cross_case.search

Use CrimeKit's existing audit service.

Do not build a second audit system.

---

# 58. SOURCE FRAME ACCESS

Endpoint:

    GET /face-sightings/{id}/source

or existing artifact-access equivalent.

Before returning source media:

    authenticate
       ↓
    case authorization
       ↓
    evidence authorization
       ↓
    artifact authorization
       ↓
    source access

Do not use a candidate ID as the only authorization check.

---

# 59. FRAME RESPONSE

Where possible, provide:

    source artifact
    timestamp
    frame reference
    bbox metadata
    controlled image/frame

The overlay should be derived and non-destructive.

---

# 60. SECURITY OF SOURCE MEDIA

Never expose sensitive source media through uncontrolled public object-storage URLs.

Use the project's secure artifact access mechanism.

---

# 61. REVIEW API

Conceptual:

    POST /face-sightings/{id}/review

Input:

    decision
    reason
    notes

Validate:

    investigator permission
    case access
    sighting exists
    valid state transition

Record:

    reviewer
    timestamp
    previous state
    new state
    reason

---

# 62. REVIEW HISTORY

Do not simply overwrite the old decision if audit requirements require history.

Preserve review transitions.

Example:

    PENDING
      ↓
    NEEDS_FURTHER_REVIEW
      ↓
    REJECTED

History remains available.

---

# 63. AI AGENT INTEGRATION

AI agents may consume structured records:

    sightings
    candidates
    timestamps
    evidence
    review state

They must not invent candidates.

Do not place low-level InsightFace inference inside an LLM call unless an explicitly approved workflow requires it.

---

# 64. RESPONSE SCHEMAS

Frontend-facing response schemas should not expose:

- raw embeddings
- internal service credentials
- model tensors
- unnecessary infrastructure details

Expose only useful investigator data.

---

# 65. ERROR RESPONSE CONTRACT

Use existing CrimeKit error format.

Conceptual:

    code
    message
    details
    request_id

Potential codes:

    FACE_REFERENCE_INVALID
    FACE_NO_FACE
    FACE_MULTIPLE_FACES
    FACE_LOW_QUALITY
    FACE_MODEL_UNAVAILABLE
    FACE_SEARCH_NOT_READY
    FACE_EVIDENCE_ACCESS_DENIED
    FACE_UNSUPPORTED_MEDIA
    FACE_JOB_NOT_CANCELLABLE

Do not expose stack traces.

---

# 66. ERROR MAPPING

Internal:

    CUDA initialization exception

External:

    FACE_MODEL_UNAVAILABLE

Internal diagnostic details remain in controlled logs.

---

# 67. TIMEOUTS

Apply timeouts at:

- image validation
- inference
- database
- vector search
- event publication
- workflow activity

Use existing platform defaults where available.

---

# 68. LOGGING

Every important backend operation should include correlation identifiers:

    request_id
    case_id
    investigation_id
    job_id
    processing_run_id
    evidence_id

Never log raw embeddings.

---

# 69. LOG LEVELS

INFO:

    job started
    job completed
    source completed

WARNING:

    low-quality observation
    recoverable frame failure
    degraded dependency

ERROR:

    worker failure
    model unavailable
    database failure

Never include secrets or raw biometric vectors.

---

# 70. METRICS

Recommended:

    face_investigations_created
    face_searches_started
    face_searches_completed
    face_searches_failed
    frames_processed
    faces_detected
    faces_quality_rejected
    embeddings_generated
    candidates_generated
    sightings_created
    reviews_completed

Performance:

    detection_latency
    embedding_latency
    match_latency
    processing_latency
    queue_latency
    end_to_end_latency

---

# 71. JOB PROGRESS

Progress should be based on meaningful work units.

Possible:

    source count
    frame count
    estimated frame completion

Do not fake:

    50%

because time has passed.

If exact progress is unavailable, communicate indeterminate processing state.

---

# 72. PROGRESS PERSISTENCE

Persist progress only at a reasonable rate.

Do not write a database row for every frame merely to update:

    progress = X

Use throttled progress updates.

---

# 73. EVENT PUBLICATION

Recommended event sequence:

    job.created
       ↓
    job.started
       ↓
    job.progress
       ↓
    sighting.created
       ↓
    job.completed

Use existing CrimeKit event infrastructure.

---

# 74. EVENT DELIVERY

Events should be published after or around authoritative persistence according to domain consistency requirements.

Do not publish:

    sighting.created

before a sighting record can be resolved by the authorized API unless the event contract explicitly handles eventual consistency.

---

# 75. EVENT IDEMPOTENCY

Each event must have:

    event_id
    event_type
    version
    occurred_at
    aggregate_id

Consumers must tolerate duplicate delivery.

---

# 76. WEBSOCKET BACKEND

WebSocket subscription must be authorization-aware.

A user should only receive:

    events for authorized investigations/cases

Never broadcast all face events to all connected clients.

---

# 77. WEBSOCKET RECONNECT

When a client reconnects:

    authenticate
       ↓
    authorize
       ↓
    retrieve authoritative state
       ↓
    resume live events

Do not assume the browser received every previous event.

---

# 78. WEBSOCKET EVENT PAYLOAD

Provide:

    investigation_id
    job_id
    source/evidence IDs where appropriate
    candidate/sighting ID
    timestamp
    similarity
    quality
    status

Do not include raw embeddings.

---

# 79. DATABASE SCHEMA PRINCIPLES

Use the existing CrimeKit migration system.

Potential relational entities:

    face_investigations
    face_references
    face_embeddings
    face_search_jobs
    face_processing_runs
    face_detections
    face_tracks
    face_candidates
    face_sightings
    face_reviews
    face_models
    face_matching_policies

Do not create unnecessary duplicates of existing general tables.

---

# 80. FOREIGN KEYS

Maintain relationships:

    case
       ↓
    investigation

    investigation
       ↓
    job

    job
       ↓
    processing run

    processing run
       ↓
    detections/tracks/candidates/sightings

Actual schema depends on existing CrimeKit conventions.

---

# 81. INDEXES

Likely useful indexes:

    case_id
    investigation_id
    job_id
    evidence_id
    processing_run_id
    timestamp
    track_id
    status
    review_status

Create indexes based on actual query patterns.

---

# 82. QUERY PERFORMANCE

The common read path:

    investigation
       ↓
    sightings
       ↓
    source evidence
       ↓
    frame

must be efficient.

Do not create highly complex unindexed queries for each UI request.

---

# 83. DATABASE RETENTION

Retention must account for:

    references
    embeddings
    detections
    tracks
    candidates
    sightings
    intermediate artifacts

Follow CrimeKit retention policy.

---

# 84. EMBEDDING DELETION

When required by retention policy, remove searchable vectors as well as relational metadata.

Do not leave embeddings behind in vector indexes.

---

# 85. MODEL MIGRATION

If model version changes:

    new model
       ↓
    new processing run
       ↓
    new embedding representation

Do not silently convert old historical output into the new model version.

---

# 86. PREPROCESSING VERSION

If preprocessing changes materially, record:

    preprocessing_version

with the processing run.

---

# 87. MATCHING POLICY VERSION

If matching logic changes:

    matching_policy_version

must change.

Historical results retain old policy metadata.

---

# 88. TRACKER VERSION

If tracker algorithm/configuration changes materially:

    tracker_version

should be recorded for relevant runs.

---

# 89. CONFIGURATION SNAPSHOT

Where practical, persist an immutable configuration/profile ID rather than relying on current environment configuration.

Do not make historical output dependent on mutable "current" settings.

---

# 90. SERVICE CONFIGURATION

Use the existing CrimeKit configuration system for:

    model
    runtime
    sampling
    worker limits
    matching policy
    storage
    queue

Do not hard-code deployment-specific paths.

---

# 91. ENVIRONMENT VARIABLES

Potential variables may include:

    FACE_MODEL_ID
    FACE_MODEL_VERSION
    FACE_EXECUTION_PROVIDER
    FACE_SAMPLE_RATE
    FACE_MAX_CONCURRENT_JOBS
    FACE_WORKER_TIMEOUT

Only add variables required by actual implementation.

Do not create configuration clutter.

---

# 92. SECRET HANDLING

Secrets must use the existing secret mechanism.

Never commit:

- model-provider credentials
- database credentials
- cloud credentials
- tokens
- private keys

---

# 93. API SECURITY

Protect against:

- IDOR
- path traversal
- unrestricted media access
- unauthorized cross-case search
- request replay
- oversized uploads
- denial of service

Use existing CrimeKit security patterns.

---

# 94. UPLOAD SECURITY

Treat reference and video uploads as untrusted.

Validate:

- file type
- size
- content
- decode behavior

Do not trust only filename extension.

---

# 95. REQUEST LIMITS

Limit:

- upload size
- number of selected evidence sources
- concurrent jobs
- processing duration

according to product requirements.

---

# 96. CROSS-CASE SEARCH

If enabled:

    explicit permission
       ↓
    scope validation
       ↓
    authorized vector search
       ↓
    audit

Do not implement global search simply by dropping case filtering.

---

# 97. MULTI-TENANT FUTURE

If CrimeKit becomes multi-tenant:

    tenant
       ↓
    case
       ↓
    investigation
       ↓
    biometric data

The backend must prevent tenant leakage.

Do not rely solely on frontend routing.

---

# 98. TESTING ARCHITECTURE

Test independently:

    API
    application service
    model adapter
    worker
    database
    vector search
    graph projection
    event publication
    WebSocket authorization

Then test the complete workflow.

---

# 99. UNIT TESTS

Minimum:

    reference validation
    face count handling
    quality policy
    embedding validation
    similarity calculation
    matching policy
    state transitions
    sighting aggregation
    authorization
    event schema

---

# 100. API TESTS

Test:

    create investigation
    upload reference
    start search
    get status
    list sightings
    get source frame
    submit review
    cancel job

---

# 101. AUTHORIZATION TESTS

Test:

    authorized investigator → allowed

    wrong case → denied

    wrong tenant → denied

    unauthorized role → denied

    unauthorized source frame → denied

    unauthorized cross-case search → denied

---

# 102. INTEGRATION TEST

Build at least one real integration path:

    API
      ↓
    workflow
      ↓
    worker
      ↓
    InsightFace adapter
      ↓
    database
      ↓
    event

Do not test only isolated mocks.

---

# 103. RETRY TEST

Verify:

    worker fails
       ↓
    retry
       ↓
    result

does not create:

    duplicate candidate
    duplicate sighting
    duplicate audit record

where idempotency guarantees are expected.

---

# 104. CANCELLATION TEST

Verify:

    running job
       ↓
    cancel
       ↓
    worker stops
       ↓
    valid prior output remains

---

# 105. REALTIME TEST

Verify:

    job progress
       ↓
    event
       ↓
    WebSocket

and:

    disconnect
       ↓
    reconnect
       ↓
    authoritative state recovery

---

# 106. SOURCE VERIFICATION TEST

A test must prove:

    candidate
       ↓
    sighting
       ↓
    detection/track
       ↓
    frame
       ↓
    evidence

is resolvable through authorized APIs.

---

# 107. MODEL TEST

Verify:

- model loads
- detector produces expected schema
- embedding dimension is correct
- output values are finite
- adapter metadata is correct

---

# 108. PERFORMANCE TEST

Measure:

    image embedding latency
    frame detection throughput
    embedding throughput
    matching latency
    sighting aggregation latency
    end-to-end processing

Record environment.

---

# 109. LOAD TEST

Gradually test:

    1 job
    multiple jobs
    multiple videos

Do not claim large-scale capacity without measurement.

---

# 110. DATABASE FAILURE TEST

Simulate database unavailability.

Expected behavior must be documented.

Do not continue in a way that silently loses authoritative forensic state.

---

# 111. VECTOR FAILURE TEST

If pgvector/search fails:

    candidate search unavailable

The job should enter a controlled failure/degraded state.

Do not fabricate candidates.

---

# 112. GRAPH FAILURE TEST

If Neo4j is unavailable after relational persistence:

    preserve relational forensic result
    mark graph projection pending/failure
    retry through controlled mechanism

Do not discard the authoritative sighting.

---

# 113. EVENT FAILURE TEST

If event publication fails after authoritative persistence:

    retain persisted state
    retry/event recovery

Do not roll back valid forensic data unnecessarily.

---

# 114. API RESPONSE CONSISTENCY

The API should return consistent representations of:

    investigation
    job
    candidate
    sighting
    review

Use existing CrimeKit schemas.

---

# 115. PAGINATION

For large result sets:

    sightings
    candidates
    detections

use pagination according to existing CrimeKit API conventions.

Do not return thousands of rows by default.

---

# 116. FILTERING

Support controlled filters where useful:

    source
    timestamp range
    candidate tier
    review status

Do not expose arbitrary database query functionality.

---

# 117. SORTING

Common investigator sort:

    time ascending/descending
    best similarity
    source

All sorting must be server-side.

---

# 118. TIME RANGE QUERIES

Validate:

    start_time
    end_time

Do not allow expensive unconstrained queries against huge datasets without appropriate limits.

---

# 119. SOURCE FILTERING

Source filtering must remain within authorized case/evidence scope.

---

# 120. CANDIDATE PAGING

Candidate data may be high-volume.

Default to investigator-useful results.

Do not load all frame-level observations into the initial UI.

---

# 121. FRAME-LEVEL ACCESS

Frame-level data should be retrieved only when needed.

Avoid:

    investigation page
       ↓
    load every frame crop

Instead:

    candidate selected
       ↓
    retrieve relevant source frame

---

# 122. DATABASE CONNECTION MANAGEMENT

Use existing connection pooling.

Do not create a new database connection for every frame.

---

# 123. VECTOR CONNECTION MANAGEMENT

Use appropriate pooled/reused connections.

Do not create a new vector connection for every embedding.

---

# 124. NEO4J SESSION MANAGEMENT

Use existing driver/session patterns.

Do not create one driver per request/job/frame.

---

# 125. REDIS MANAGEMENT

Reuse existing Redis client/connection infrastructure.

Do not create Redis clients repeatedly inside frame loops.

---

# 126. WORKER PROCESS LIFECYCLE

Worker:

    start
       ↓
    initialize dependencies
       ↓
    load model
       ↓
    readiness
       ↓
    process jobs
       ↓
    graceful shutdown

---

# 127. WORKER MEMORY

Monitor:

    process memory
    GPU memory
    queue depth

Do not allow long-running jobs to cause unbounded memory growth.

---

# 128. WORKER TIMEOUT

A stuck video/inference operation must eventually produce a controlled timeout/failure state.

---

# 129. JOB LEASING

If the existing queue/workflow system uses leases/heartbeats:

    use existing mechanism

Do not implement a second heartbeat system.

---

# 130. HEARTBEATS

For long-running processing, publish heartbeat/progress according to existing workflow semantics.

This allows operators to distinguish:

    active

from:

    stuck

---

# 131. OBSERVABILITY CORRELATION

Use:

    request_id
    investigation_id
    job_id
    processing_run_id

throughout logs/events.

---

# 132. SECURITY TELEMETRY

Track security events such as:

    access denied
    cross-case request
    repeated unauthorized attempts

according to existing CrimeKit security monitoring.

---

# 133. RATE LIMITING

Protect:

    investigation creation
    reference upload
    search creation
    source retrieval

according to existing API rate-limit infrastructure.

---

# 134. DOS PROTECTION

Protect against:

    huge video
    huge image
    repeated job creation
    many simultaneous searches
    malicious media

Use admission and processing limits.

---

# 135. NO SYNCHRONOUS VIDEO SEARCH API

Never implement:

    POST /search
       ↓
    process 2-hour video
       ↓
    hold HTTP connection
       ↓
    return results

Correct:

    POST /search
       ↓
    return job_id
       ↓
    async processing

---

# 136. SEARCH RESULT CACHING

Caching may be introduced for repeated authorized reads where useful.

Never use an unscoped cache key such as:

    sightings:investigation

if authorization context can differ.

---

# 137. CACHE INVALIDATION

When review state or relevant candidate data changes:

    invalidate/update cache

according to the existing cache strategy.

---

# 138. API OBSERVABILITY

Record:

    endpoint
    status
    latency
    request_id

Do not record sensitive request bodies containing biometric data.

---

# 139. ERROR OBSERVABILITY

For failures, capture:

    error category
    component
    job
    processing run

Do not log sensitive payloads.

---

# 140. SENSITIVE RESPONSE SCRUBBING

Before returning an error:

    remove secrets
    remove embedding vectors
    remove internal paths
    remove stack traces

---

# 141. SECURITY OF JOB IDS

Job IDs should not themselves bypass authorization.

Always re-check authorization when retrieving a job.

Do not rely on opaque IDs as access control.

---

# 142. SECURITY OF CANDIDATE IDS

Candidate/sighting IDs must not be direct authorization tokens.

Always enforce case/evidence access.

---

# 143. REVIEW AUTHORIZATION

Only authorized roles may change review state.

Reading a candidate and adjudicating a candidate are different permissions if the role model requires that distinction.

---

# 144. EXPORT AUTHORIZATION

Face investigation exports must respect:

    case
    role
    tenant
    data-retention policy

---

# 145. API DOCUMENTATION

Document:

- endpoint
- authentication
- authorization
- request
- response
- errors
- status transitions
- side effects

Do not document unimplemented endpoints as operational.

---

# 146. OPENAPI

Use the existing FastAPI/OpenAPI generation.

Schemas must accurately describe the implementation.

Do not expose internal vectors simply because FastAPI can serialize them.

---

# 147. BACKWARD COMPATIBILITY

Existing CrimeKit APIs must not break because Face Trace Investigator was added.

Any shared schema change requires impact analysis.

---

# 148. DATABASE MIGRATION SAFETY

Before migration:

    inspect current schema

Then:

    create migration
       ↓
    test migration
       ↓
    run application tests
       ↓
    validate rollback strategy where required

Do not manually modify production tables.

---

# 149. DEPLOYMENT MIGRATION ORDER

Where necessary:

    backward-compatible schema
       ↓
    deploy backend
       ↓
    deploy workers
       ↓
    activate feature

Avoid deployments that require all services to switch simultaneously without compatibility planning.

---

# 150. FEATURE FLAGS

If CrimeKit already uses feature flags, consider controlled activation:

    FACE_TRACE_ENABLED

Do not add a feature-flag system if one already exists.

---

# 151. MODEL ACTIVATION

Model activation should be separate from code deployment where practical.

Possible:

    model version approved
       ↓
    configuration activation
       ↓
    worker rollout

---

# 152. WORKER ROLLOUT

For major model/runtime changes:

    old workers
       ↓
    controlled transition
       ↓
    new workers

Do not mix incompatible workers accidentally.

---

# 153. ROLLING DEPLOYMENT

Ensure that temporary coexistence of worker versions does not corrupt:

    job state
    embeddings
    policy metadata

---

# 154. DATABASE COMPATIBILITY

New worker versions must remain compatible with database schema during rolling deployment.

---

# 155. API/WORKER COMPATIBILITY

Job payloads should remain compatible during rolling deployment.

Use versioned task/event contracts when necessary.

---

# 156. CONFIGURATION VALIDATION

At startup verify:

    required model config
    required database config
    required event config
    compatible vector dimension

Fail early.

---

# 157. STARTUP FAILURE

If critical face configuration is invalid:

    face worker = NOT_READY

Do not partially activate the subsystem.

---

# 158. HEALTH ENDPOINT

Expose an appropriate health/readiness integration.

Example conceptual:

    /health
    /ready

Use existing CrimeKit operational conventions.

---

# 159. READINESS CHECK

Readiness may verify:

    model loaded
    inference smoke test
    required storage connectivity

Do not make liveness depend on every downstream dependency if the platform semantics separate these checks.

---

# 160. DEPENDENCY FAILURE

If pgvector is temporarily unavailable:

    face inference may remain healthy

but:

    search subsystem = DEGRADED

Represent dependency-level state appropriately.

---

# 161. SECURITY OF BACKEND SERVICE

Backend processes must run with minimum required permissions.

Do not give face workers broad administrative database permissions if scoped access is possible.

---

# 162. SERVICE ACCOUNT

Where service accounts exist:

    API account
    worker account
    graph projection account

may have different privileges.

Use existing security architecture.

---

# 163. DATABASE PERMISSIONS

Inference workers should not automatically have access to unrelated CrimeKit tables.

Follow least privilege.

---

# 164. OBJECT STORAGE PERMISSIONS

Workers should access only the evidence required for the current authorized job.

---

# 165. MODEL STORAGE PERMISSIONS

Only inference workers/services that need model artifacts should read them.

---

# 166. REQUEST CONTEXT

Job metadata must carry enough context for safe execution:

    case_id
    investigation_id
    job_id
    processing_run_id
    authorized scope

Workers should not invent this context.

---

# 167. WORKER INPUT VALIDATION

Workers must validate that referenced:

    case
    investigation
    evidence

still exist and are in expected state where applicable.

---

# 168. TOCTOU CONSIDERATIONS

An evidence authorization/state may change after job creation.

Before accessing highly sensitive evidence, revalidate required authorization/state according to the domain policy.

---

# 169. DELETED/REVOKED EVIDENCE

If evidence is revoked/deleted while a search is running:

    stop/skip according to evidence governance

Do not continue accessing revoked media blindly.

---

# 170. CASE CLOSURE

If a case is closed:

    follow project policy

Potentially:

    allow existing processing to finish
    or
    cancel new work

Do not invent lifecycle behavior without checking CrimeKit case policy.

---

# 171. USER DEACTIVATION

If an initiating investigator is deactivated while a job is running, the job should follow case-level ownership/workflow rules rather than relying on the user's continued session.

---

# 172. AUDIT ACTOR

Audit records must identify the actual actor/service that initiated the operation.

Worker execution should be distinguishable from human initiation.

---

# 173. SERVICE ACTOR VS USER ACTOR

Example:

    initiated_by = user-123
    executed_by = face-worker-07

This may be useful in operational/audit systems.

---

# 174. REVIEW ACTOR

Review must identify the human/authorized actor responsible for the decision.

Do not let the worker perform a human review action.

---

# 175. PROVENANCE ACTOR

Machine-generated outputs should identify the service/process responsible without implying human authorship.

---

# 176. DATA MODEL OWNERSHIP

One domain component should own each entity lifecycle.

Example:

    FaceInvestigationService → investigation lifecycle

    FaceProcessingService → processing run

    ReviewService → review lifecycle

Actual ownership must align with existing application architecture.

---

# 177. DOMAIN EVENTS

Use domain events where appropriate.

Examples:

    FaceInvestigationCreated
    FaceReferenceReady
    FaceSearchStarted
    FaceSightingCreated
    FaceReviewUpdated
    FaceSearchCompleted

Transport them through existing event infrastructure.

---

# 178. DOMAIN EVENT CONTENT

Events should describe domain state changes.

Do not pack arbitrary implementation state into public events.

---

# 179. EVENT VERSIONING

Version event payloads if consumers may evolve independently.

---

# 180. EVENT ORDERING

Do not assume globally ordered events unless the transport guarantees the needed ordering scope.

Consumers should use:

    event_id
    occurred_at
    aggregate_id

and authoritative state as required.

---

# 181. EVENT DUPLICATION

Design consumers for at-least-once delivery where applicable.

Duplicate event reception must not create duplicate forensic records.

---

# 182. VECTOR SEARCH RESULT STABILITY

If the same query can produce different ordering because of approximate search or concurrent index updates, document this.

Do not claim deterministic rank without validating it.

---

# 183. SEARCH REPRODUCIBILITY

Record enough context to reproduce interpretation:

    model
    policy
    query scope
    processing run
    index/model compatibility

---

# 184. REPORTING

Backend should expose authoritative stored results to the report system.

Do not rerun face recognition simply to generate a report.

---

# 185. REPORT CONTEXT

Include:

    source evidence
    timestamps
    candidate/sighting
    model metadata
    matching policy
    review status

according to reporting requirements.

---

# 186. REPORT LANGUAGE

Backend/report data should distinguish:

    machine-generated candidate

from:

    investigator-reviewed outcome

Do not encode legal conclusions automatically.

---

# 187. FILE EXPORT

If an annotated frame is exported:

    preserve source reference
    preserve non-destructive annotation
    preserve metadata
    follow security/retention policy

---

# 188. TEST FIXTURES

Use synthetic/public/approved media only.

Do not commit real case images/videos to tests.

---

# 189. TEST DATABASE

Use isolated test databases/vector indexes/graph namespaces as required.

Do not run destructive tests against development/prod data.

---

# 190. TEST MODEL

Use a deterministic mock provider for most domain tests.

Use real InsightFace integration tests separately.

---

# 191. TEST MODEL VERSION

The integration test should assert:

    expected model metadata
    expected embedding dimension
    valid numerical result

Avoid brittle exact-vector assertions unless intentionally required.

---

# 192. PERFORMANCE BASELINE

At minimum record:

    source video resolution
    FPS
    sample rate
    average faces/frame
    model
    execution provider
    hardware
    processing duration

---

# 193. PERFORMANCE REGRESSION

Any changes to:

    model
    runtime
    preprocessing
    sample rate
    batch size

must be benchmarked if they can affect throughput/latency.

---

# 194. SECURITY REGRESSION

Any changes to:

    routes
    artifact access
    vector queries
    cross-case scope
    review permissions

must include security tests.

---

# 195. BACKEND ACCEPTANCE CRITERIA

The backend is acceptable when:

[ ] Reference upload is authenticated.

[ ] Reference processing is asynchronous.

[ ] Reference face count is handled correctly.

[ ] Reference embedding is versioned.

[ ] Search is asynchronous.

[ ] Evidence access is case-scoped.

[ ] Video processing is incremental.

[ ] Face detection records are persisted.

[ ] Tracks are persisted.

[ ] Candidate matches are persisted.

[ ] Sightings are aggregated.

[ ] Provenance is preserved.

[ ] Model/policy metadata is persisted.

[ ] WebSocket events are authorization-aware.

[ ] Review is explicitly human-driven.

[ ] Retry is idempotent.

[ ] Cancellation is controlled.

[ ] Source-frame access is secured.

[ ] Tests exist.

[ ] Performance is measured.

[ ] No sensitive biometric vector is exposed unnecessarily.

---

# 196. BACKEND IMPLEMENTATION ORDER

Implement in this order:

    1. Existing architecture inspection
    2. Domain contract
    3. Database model/migration
    4. Reference API
    5. Reference processor
    6. InsightFace adapter
    7. Search job
    8. Video worker
    9. Detection/quality/tracking
    10. Matching
    11. Sighting aggregation
    12. Provenance
    13. Persisted result APIs
    14. Realtime events
    15. WebSocket authorization
    16. Review
    17. Neo4j projection
    18. Performance optimization
    19. Security hardening
    20. Full integration testing

Do not start with Neo4j or polished UI.

---

# 197. BACKEND REVIEW QUESTIONS

Before merge:

## Architecture

Does this reuse existing CrimeKit infrastructure?

## Security

Can a user access another case's biometric data?

## Model

Can we identify the model that produced every result?

## Evidence

Can we reach the exact source frame?

## Matching

Is the threshold/policy versioned?

## Reliability

What happens after worker failure?

## Realtime

What happens after WebSocket disconnect?

## Scale

What is the measured bottleneck?

## Review

Can a human investigator explicitly review the candidate?

---

# 198. ANTI-PATTERNS

Never implement:

    route → model → result

for the entire feature.

Never implement:

    upload → process 2-hour video synchronously

Never implement:

    candidate_id → unrestricted source access

Never implement:

    similarity > unexplained magic number

Never implement:

    all vectors → browser filtering

Never implement:

    worker → arbitrary graph writes

Never implement:

    WebSocket → source of truth

Never implement:

    hosted evaluation API → production frame processing

Never implement:

    face match → criminal identity

---

# 199. FINAL BACKEND CONTRACT

The backend must provide this controlled pipeline:

    AUTHENTICATED USER
         ↓
    CASE AUTHORIZATION
         ↓
    FACE INVESTIGATION
         ↓
    REFERENCE PROCESSING
         ↓
    VERSIONED EMBEDDING
         ↓
    AUTHORIZED EVIDENCE
         ↓
    ASYNC SEARCH
         ↓
    VIDEO/IMAGE PROCESSING
         ↓
    FACE DETECTION
         ↓
    QUALITY
         ↓
    TRACKING
         ↓
    EMBEDDING
         ↓
    MATCHING
         ↓
    SIGHTING
         ↓
    PROVENANCE
         ↓
    PERSISTENCE
         ↓
    REALTIME EVENT
         ↓
    INVESTIGATOR REVIEW

The backend is complete only when this path is:

    secure
    asynchronous
    versioned
    observable
    idempotent
    provenance-preserving
    testable
    scalable

and remains compatible with the rest of CrimeKit.
