# CRIMEKIT — FACE TRACE INVESTIGATOR
# PRODUCTION IMPLEMENTATION & DEPLOYMENT SPECIFICATION

**Document:** `PRODUCTION_DEPLOYMENT.md`  
**Subsystem:** Face Trace Investigator  
**Scope:** Production implementation, deployment, CI/CD, model packaging, GPU workers, realtime services, database/vector/graph integration, observability, security, operations, rollout, rollback, incident response, SIH-ready vertical slice  
**Audience:** Backend, frontend, ML, forensic, DevOps, security, QA, project leads  
**Status:** Final implementation/deployment specification

---

# 1. PURPOSE

This document converts the previous Face Trace specifications into a production-oriented implementation and deployment plan.

The complete feature is:

    Investigator
       ↓
    React UI
       ↓
    FastAPI
       ↓
    Durable Job / Workflow
       ↓
    Video Processing
       ↓
    Detection
       ↓
    Quality
       ↓
    Tracking
       ↓
    InsightFace
       ↓
    pgvector Matching
       ↓
    Candidate
       ↓
    Sighting
       ↓
    Provenance
       ↓
    PostgreSQL
       ↓
    Neo4j Projection
       ↓
    Realtime Events
       ↓
    Investigator Review

The production goal is not merely to make the feature run.

The goal is to make it:

    secure
    reproducible
    observable
    scalable
    provenance-complete
    operationally recoverable
    honest about model output

---

# 2. FINAL FEATURE CONTRACT

## Feature

**Face Trace Investigator**

## Purpose

> Trace a reference face across authorized digital evidence and present machine-generated candidate sightings for investigator review.

## Core supported sources

    MP4/video evidence
    authorized RTSP/CCTV streams

## Core result

    Candidate Sighting

## Human control

    Investigator review required

---

# 3. NON-NEGOTIABLE PRODUCTION RULES

1. Never modify source evidence.
2. Never bypass CrimeKit authentication/authorization.
3. Never expose raw biometric vectors to the frontend by default.
4. Never expose RTSP credentials to clients.
5. Never treat similarity as probability.
6. Never treat similarity as guilt.
7. Never call a candidate a confirmed criminal.
8. Never silently cross case boundaries.
9. Never allow unbounded processing queues.
10. Never report processing failure as zero matches.
11. Never hide partial coverage.
12. Never overwrite historical model/policy context.
13. Never destroy provenance during reprocessing.
14. Never invent telemetry.
15. Never use fake demo results as production evidence.

---

# 4. REPOSITORY INTEGRATION

Before implementation:

    inspect existing repository

Identify:

    backend structure
    frontend structure
    forensic processing modules
    evidence module
    authentication
    RBAC
    database migrations
    Temporal/Celery usage
    Redis usage
    Neo4j integration
    pgvector integration
    WebSocket/event architecture
    CI
    deployment configuration

Do not create duplicate infrastructure when equivalent CrimeKit abstractions already exist.

---

# 5. CODE OWNERSHIP BOUNDARY

Recommended feature structure:

    frontend/
        face-trace/

    backend/
        face_trace/

    workers/
        face_trace/

    database/
        migrations/

    docs/
        face-trace/

Use actual repository conventions.

Do not impose this exact folder layout if the existing repository has an established equivalent.

---

# 6. BACKEND MODULE BOUNDARIES

Recommended conceptual modules:

    api/
    domain/
    services/
    workflows/
    repositories/
    providers/
    matching/
    provenance/
    events/
    security/

---

# 7. PROVIDER ABSTRACTIONS

Use interfaces for replaceable technology:

    FaceEmbeddingProvider
    FaceDetector
    FaceTracker
    VectorSearchRepository
    VideoDecoder
    SourceProvider

InsightFace becomes:

    InsightFaceProvider

Do not hard-code provider-specific behavior into unrelated modules.

---

# 8. FRONTEND MODULE BOUNDARIES

Recommended conceptual:

    FaceTracePage
    ReferenceSelector
    EvidenceSelector
    SearchControls
    ProcessingStatus
    CandidateList
    SightingList
    SourceFrameViewer
    ProvenanceDrawer
    ReviewPanel
    RealtimeConnection

Use existing CrimeKit component/state conventions.

---

# 9. WORKFLOW BOUNDARY

Long-running operations must not run inside synchronous HTTP handlers.

Use the existing durable workflow/job architecture.

Conceptual:

    POST search
       ↓
    create job
       ↓
    workflow
       ↓
    workers

---

# 10. FILE PROCESSING WORKFLOW

Recommended:

    ValidateSource
       ↓
    CreateProcessingRun
       ↓
    OpenVideo
       ↓
    Decode
       ↓
    Sample
       ↓
    Detect
       ↓
    Quality
       ↓
    Track
       ↓
    Embed
       ↓
    Match
       ↓
    Aggregate
       ↓
    Persist
       ↓
    Project
       ↓
    Publish
       ↓
    Finalize

---

# 11. LIVE PROCESSING WORKFLOW

Recommended:

    ValidateSource
       ↓
    CreateLiveRun
       ↓
    ConnectRTSP
       ↓
    Decode
       ↓
    BoundedScheduler
       ↓
    Detect
       ↓
    Quality
       ↓
    Track
       ↓
    Embed
       ↓
    Match
       ↓
    Aggregate
       ↓
    Persist
       ↓
    Publish
       ↓
    Health Monitoring
       ↺

---

# 12. CPU/GPU DEPLOYMENT

Separate responsibilities where useful:

    CPU:
        API
        orchestration
        decoding where appropriate
        preprocessing
        persistence

    GPU:
        face detection where supported
        InsightFace recognition
        batch inference

Do not assume every deployment requires GPU.

---

# 13. GPU WORKER SERVICE

Recommended architecture:

    FastAPI
       ↓
    workflow
       ↓
    GPU worker queue
       ↓
    inference worker

Worker receives structured requests and returns structured results.

---

# 14. GPU WORKER ISOLATION

Do not allow one malformed job to take down all inference processing.

Workers should have:

    bounded memory
    health checks
    restart policy
    structured logging

---

# 15. MODEL PACKAGE

Production model package should include:

    model artifact(s)
    model ID
    version
    provider
    expected input contract
    embedding dimension
    preprocessing metadata
    checksum/integrity metadata
    license/approval record where applicable

Do not deploy an unidentified weight file.

---

# 16. MODEL STORAGE

Store production model artifacts in approved protected storage.

Do not commit large/private model binaries into Git unless explicitly approved by repository policy.

---

# 17. MODEL INTEGRITY

At worker startup verify:

    expected model
    expected version
    expected checksum/integrity metadata

where supported.

---

# 18. MODEL LICENSE

The exact model weights used in production must have their applicable license/approval verified.

Do not infer model licensing from the code repository license alone.

---

# 19. INSIGHTFACE RUNTIME

Use the approved InsightFace/runtime configuration documented in `INSIGHTFACE.md`.

Production should use the approved local/private/offline inference architecture rather than depending on an evaluation-only hosted endpoint.

---

# 20. MODEL WARMUP

GPU workers may perform controlled warmup.

Warmup must be excluded from forensic processing statistics.

---

# 21. MODEL LOAD FAILURE

If required model initialization fails:

    worker = NOT_READY

Do not mark service healthy while inference is unavailable.

---

# 22. HEALTH ENDPOINTS

Recommended worker checks:

    /health
    /ready

Health should distinguish:

    process alive

from:

    model ready

---

# 23. GPU HEALTH

Readiness can verify:

    model loaded
    inference provider available
    GPU/runtime operational where required

Do not expose sensitive internal information through public health endpoints.

---

# 24. DATABASE DEPLOYMENT

Use the approved PostgreSQL deployment.

Enable pgvector only through controlled infrastructure/migration.

---

# 25. DATABASE MIGRATIONS

All Face Trace schema changes must use the established migration framework.

Never manually alter production schema as the normal workflow.

---

# 26. MIGRATION PIPELINE

Recommended:

    commit migration
       ↓
    CI migration test
       ↓
    staging migration
       ↓
    validation
       ↓
    production migration

---

# 27. MIGRATION SAFETY

For large datasets evaluate:

    lock duration
    index creation
    backfill time
    replication impact

---

# 28. VECTOR INDEX DEPLOYMENT

Build pgvector indexes according to tested corpus size/workload.

Do not blindly use a specific index type without benchmark evidence.

---

# 29. VECTOR DIMENSION SAFETY

A vector index/table must only contain compatible embedding dimensions.

---

# 30. VECTOR MODEL ISOLATION

When multiple model families are supported:

    separate model/vector contexts

must prevent incompatible comparisons.

---

# 31. GRAPH DEPLOYMENT

Neo4j remains a projection/relationship store according to CrimeKit architecture.

Face Trace domain records remain authoritative in PostgreSQL.

---

# 32. GRAPH PROJECTION

Use:

    domain event
       ↓
    graph projector
       ↓
    Neo4j

Do not make Neo4j the first write path for candidate/sighting persistence.

---

# 33. GRAPH REBUILD

A controlled projection rebuild must be possible from authoritative domain state.

---

# 34. EVENT INFRASTRUCTURE

Use the existing CrimeKit event bus/outbox approach.

Do not create an independent event bus for Face Trace without architectural justification.

---

# 35. OUTBOX PATTERN

Recommended:

    PostgreSQL transaction
       ├── candidate/sighting
       └── event_outbox

then:

    publisher
       ↓
    event bus
       ↓
    graph/realtime consumers

---

# 36. WEBSOCKET SERVICE

Realtime delivery can expose:

    processing progress
    candidate creation
    sighting creation/update
    health state
    job completion

Only authorized data is delivered.

---

# 37. WEBSOCKET AUTHORIZATION

Validate authorization before:

    connection
    subscription
    event delivery

---

# 38. EVENT PAYLOAD

Payload should contain:

    IDs
    state
    timestamps
    concise metadata

Never include:

    raw vector
    RTSP secret
    unnecessary raw media

---

# 39. FRONTEND REALTIME ARCHITECTURE

Recommended:

    initial REST snapshot
       ↓
    WebSocket subscription
       ↓
    event reducer
       ↓
    UI state
       ↓
    reconciliation when gap detected

---

# 40. FRONTEND RECONNECT

On connection loss:

    reconnect
       ↓
    authenticate
       ↓
    resubscribe
       ↓
    refresh authoritative state

---

# 41. NO EVENT-ONLY UI

Critical UI state must be recoverable from APIs.

Do not make WebSocket delivery the only source of truth.

---

# 42. OBJECT STORAGE

Store source/derived media using the existing CrimeKit evidence/object-storage abstraction.

Do not create a hidden local media repository.

---

# 43. SOURCE EVIDENCE ACCESS

Face Trace should reference existing evidence IDs.

---

# 44. DERIVED MEDIA

Possible derived outputs:

    source-frame snapshot
    face crop
    annotated preview
    thumbnail

Each must be traceable.

---

# 45. SECURE MEDIA ACCESS

Use authorized application access or short-lived signed URLs where appropriate.

Do not create public URLs to sensitive evidence.

---

# 46. TEMPORARY MEDIA

Temporary files/buffers require:

    bounded retention
    cleanup
    access control

---

# 47. RTSP SECRET MANAGEMENT

Credentials belong in approved secret management.

Never:

    frontend environment
    React bundle
    logs
    event payloads
    source code

---

# 48. RTSP SOURCE CONFIGURATION

Prefer:

    source_id → secure server-side configuration

rather than:

    browser → raw RTSP URI/password

---

# 49. RTSP NETWORK SECURITY

Restrict outbound worker network access to approved destinations where the deployment architecture supports network controls.

---

# 50. SSRF PROTECTION

Do not allow arbitrary user input to turn the RTSP feature into an uncontrolled internal-network request mechanism.

Validate/allowlist source configuration as appropriate.

---

# 51. JOB RESOURCE LIMITS

Every search job should be bounded by policy:

    maximum sources
    maximum duration where applicable
    top-K
    concurrency
    storage
    compute

Exact values must come from tested deployment configuration.

---

# 52. INPUT SIZE LIMITS

Reject or constrain unsupported oversized inputs.

Do not let one request consume all resources.

---

# 53. LIVE STREAM QUOTAS

Define tested limits for:

    concurrent cameras
    processing FPS
    GPU workers
    CPU workers

Do not claim universal capacity.

---

# 54. FAIR SCHEDULING

Use scheduling/quotas so one case cannot permanently monopolize shared compute.

---

# 55. RATE LIMITING

Protect expensive APIs:

    search creation
    live-stream creation
    reprocessing
    source-frame extraction

---

# 56. AUTHORIZATION MATRIX

Minimum conceptual:

| Operation | Investigator | Reviewer | Admin |
|---|---:|---:|---:|
| Create search | ✓ | ✓ | ✓ |
| View candidates | ✓ | ✓ | ✓ |
| View source frame | ✓ | ✓ | ✓ |
| Review sighting | policy-based | ✓ | ✓ |
| Start live stream | policy-based | policy-based | ✓ |
| Change model | — | — | ✓ |
| Change matching policy | — | — | ✓ |

Actual roles must reuse existing CrimeKit RBAC.

---

# 57. HUMAN REVIEW

Candidate results must remain:

    MACHINE_GENERATED
    REVIEW_PENDING

until the investigator workflow changes the state.

---

# 58. REVIEW AUDIT

Persist:

    reviewer
    decision
    timestamp
    previous state
    new state
    notes where required

---

# 59. NO MACHINE AUTO-CONFIRMATION

Do not build a state transition:

    machine score
       ↓
    confirmed identity

without an explicitly governed human/organizational process.

---

# 60. PROVENANCE GATE

Before candidate exposure:

    validate required provenance

Minimum:

    case
    investigation
    source
    processing run
    detection/frame where applicable
    model
    policy

---

# 61. PROVENANCE FAILURE

If required provenance is missing:

    mark incomplete/degraded

Do not silently substitute unrelated identifiers.

---

# 62. SEARCH COMPLETION LANGUAGE

Successful search:

    "Completed"

No results:

    "No qualifying candidate found under the selected policy."

Partial:

    "Partially processed."

Failure:

    "Processing failed."

Do not claim absence from incomplete analysis.

---

# 63. MODEL SCORE LANGUAGE

Use:

    Similarity

Do not use:

    Accuracy
    Probability
    Certainty

unless a separate calibrated statistic exists.

---

# 64. INVESTIGATOR UI CONTRACT

Candidate card should expose:

    reference
    source
    timestamp
    frame
    similarity
    quality
    sighting
    review state

Advanced:

    model/version
    policy/version
    processing run

---

# 65. SOURCE VERIFICATION

Every meaningful candidate should support:

    View source frame
    View provenance
    View evidence context

subject to permission.

---

# 66. LIVE CAMERA VIEW

Recommended:

    Camera identity
    Stream health
    FPS
    Processing FPS
    Latency
    Candidate/sighting count
    Latest sighting

---

# 67. PERFORMANCE TELEMETRY

Collect:

    source FPS
    processed FPS
    dropped frames
    end-to-end latency
    queue depth
    GPU memory
    CPU
    detection latency
    embedding latency
    vector latency

---

# 68. OBSERVABILITY STACK

Integrate with existing CrimeKit tools for:

    logs
    metrics
    traces
    AI/model observability

Do not create duplicate observability systems.

---

# 69. STRUCTURED LOGGING

Use:

    request_id
    job_id
    processing_run_id
    source_id
    event
    duration
    error_code

Never log raw biometrics.

---

# 70. TRACE PROPAGATION

Trace:

    API
       ↓
    workflow
       ↓
    worker
       ↓
    inference
       ↓
    persistence
       ↓
    event

---

# 71. SENSITIVE TELEMETRY

Do not put high-cardinality sensitive identifiers into unrestricted global metrics.

---

# 72. ALERTS

Recommended operational alerts:

    inference worker down
    GPU unavailable
    queue saturation
    memory growth
    RTSP reconnect storm
    database failure
    vector failure
    event delivery backlog

---

# 73. FORENSIC VS OPERATIONAL ALERT

A service outage is:

    operational incident

A candidate is:

    machine-generated investigative result

Keep these semantics separate.

---

# 74. CI PIPELINE

Recommended pipeline:

    lint
       ↓
    unit tests
       ↓
    type checks
       ↓
    integration tests
       ↓
    security checks
       ↓
    build
       ↓
    migration tests
       ↓
    container scan
       ↓
    artifact publish

---

# 75. MODEL CI

Where feasible test:

    model artifact availability
    compatibility
    embedding shape
    startup
    inference smoke test

Do not run huge model benchmarks on every commit unless infrastructure supports it.

---

# 76. IMAGE/CONTAINER BUILD

Production images should be:

    versioned
    reproducible
    minimal
    scanned

---

# 77. CONTAINER SEPARATION

Potential images:

    crimekit-api
    crimekit-face-worker
    crimekit-gpu-worker
    crimekit-frontend

Reuse existing project images/monorepo patterns where available.

---

# 78. GPU IMAGE

GPU inference image must pin compatible:

    Python
    ONNX Runtime
    CUDA runtime
    driver expectations
    provider dependencies

---

# 79. GPU COMPATIBILITY

Test actual deployment combination.

Do not infer compatibility from package installation success.

---

# 80. CPU IMAGE

A CPU-compatible worker may exist for:

    development
    testing
    controlled fallback

only if supported by performance requirements.

---

# 81. ENVIRONMENT CONFIGURATION

Separate:

    development
    staging
    production

configuration.

---

# 82. ENVIRONMENT SECRETS

Inject at runtime through approved secret/configuration mechanisms.

Do not commit:

    .env
    API keys
    RTSP passwords
    database passwords
    model licenses

---

# 83. CONFIGURATION CLASSES

Recommended:

    infrastructure config
    model config
    matching policy
    runtime limits
    feature flags

---

# 84. FEATURE FLAGS

Face Trace rollout can use feature flags.

Do not let flags silently alter forensic semantics without versioning/logging.

---

# 85. STAGING

Staging should contain:

    approved test media
    synthetic data
    controlled RTSP source
    test model

Never copy production evidence casually.

---

# 86. TEST CAMERA

Use a controlled local/test RTSP source.

Examples:

    prerecorded test stream
    isolated camera lab

Do not make CI depend on a public camera.

---

# 87. PRODUCTION CAMERA ONBOARDING

Each source should have:

    source identity
    authorization
    stream configuration
    expected format
    timezone/context where applicable
    health monitoring

---

# 88. PRODUCTION FILE ONBOARDING

Supported file classes must be explicitly configured.

---

# 89. UNSUPPORTED MEDIA

Return:

    unsupported format

rather than attempting arbitrary decoder behavior.

---

# 90. DEPLOYMENT TOPOLOGY

Reference production topology:

    Browser
       ↓ HTTPS
    Frontend
       ↓
    API Gateway / Load Balancer
       ↓
    FastAPI
       ↓
    Workflow
       ↓
    CPU workers ─────→ PostgreSQL
       ↓                    ↓
    GPU workers         pgvector
       ↓                    ↓
    Matching           Event/Outbox
                            ↓
                         Neo4j
                            ↓
                        WebSocket
                            ↓
                         Browser

Actual infrastructure may consolidate nodes.

---

# 91. NETWORK SEGMENTATION

Sensitive components should reside in appropriate private network segments.

---

# 92. PUBLIC EXPOSURE

Do not expose:

    PostgreSQL
    pgvector
    Neo4j
    Redis
    GPU workers

directly to the public internet.

---

# 93. HTTPS

All investigator-facing transport must use secure transport.

---

# 94. INTERNAL TLS

Use approved internal encryption where infrastructure requires it.

---

# 95. FIREWALLING

Allow only required service-to-service connections.

---

# 96. DEPLOYMENT SCALING

Scale independently where workload allows:

    API replicas
    CPU workers
    GPU workers
    WebSocket gateway

---

# 97. GPU SCALING

GPU capacity depends on:

    model
    detector
    frame size
    source FPS
    face density

Benchmark before scaling.

---

# 98. AUTOSCALING

Autoscale only on metrics that reflect real workload.

Possible:

    queue depth
    GPU utilization
    CPU utilization
    processing latency

---

# 99. GPU AUTOSCALING LIMIT

Do not autoscale beyond available licensed/approved GPU infrastructure.

---

# 100. DATABASE SCALING

Database scaling must be designed from expected:

    writes
    vector queries
    candidate reads
    provenance reads

---

# 101. READ REPLICAS

Read replicas may help where appropriate.

Do not use replicas for workflows requiring immediate read-after-write consistency unless the architecture handles that explicitly.

---

# 102. VECTOR SCALE

Benchmark retrieval as corpus grows.

---

# 103. GRAPH SCALE

Keep Neo4j graph projection bounded to domain needs.

Do not duplicate every low-level frame event into the graph unnecessarily.

---

# 104. EVENT SCALE

High-frequency frame/track events should not flood the event bus unnecessarily.

Aggregate/coalesce where possible.

---

# 105. LIVE EVENT RATE

Prefer:

    sighting created/updated

over:

    every-frame candidate event

for investigator UI.

---

# 106. FILE EVENT RATE

Progress events should be controlled.

Do not publish per-frame progress.

---

# 107. DATA RETENTION

Apply approved retention separately to:

    source evidence
    reference images
    embeddings
    detections
    tracks
    candidates
    sightings
    derived crops
    temporary buffers

---

# 108. DATA DELETION

Derived biometric data must be deleted/expired according to policy.

---

# 109. LEGAL HOLD

Legal hold must override normal expiration where required.

---

# 110. BACKUPS

Production backups containing face data are sensitive.

Use encrypted approved backup storage.

---

# 111. RESTORE TEST

Regularly validate:

    database restore
    vector availability/rebuild
    graph projection rebuild
    event/outbox consistency

---

# 112. DISASTER RECOVERY

Document:

    restore order
    service dependencies
    model artifacts
    secrets
    database
    vector index
    graph projection
    event infrastructure

---

# 113. RECOVERY ORDER

Recommended:

    infrastructure
       ↓
    PostgreSQL
       ↓
    required extensions
       ↓
    API
       ↓
    workers
       ↓
    vector projection
       ↓
    graph projection
       ↓
    realtime

---

# 114. PROJECTION RECOVERY

After restore:

    PostgreSQL authoritative
       ↓
    rebuild/reconcile pgvector
       ↓
    rebuild/reconcile Neo4j
       ↓
    resume events

---

# 115. NO SOURCE LOSS

Recovery must not replace source evidence with derived results.

---

# 116. ROLLOUT STRATEGY

Recommended:

    development
       ↓
    staging
       ↓
    controlled production
       ↓
    broader production

---

# 117. CANARY

Canary rollout may target:

    one investigator team
    one source class
    limited workloads

before broader rollout.

---

# 118. CANARY METRICS

Monitor:

    failure rate
    p95 latency
    queue depth
    GPU memory
    candidate volume
    reconnects

---

# 119. MODEL CANARY

A new model should be tested separately from a production baseline.

Do not silently mix model versions.

---

# 120. POLICY CANARY

A new matching policy must have explicit version identity.

---

# 121. ROLLBACK

Rollback can mean:

    application version rollback
    worker version rollback
    model rollback
    policy rollback

Historical results remain untouched.

---

# 122. MODEL ROLLBACK

Rollback changes future processing.

Do not delete old runs/results.

---

# 123. POLICY ROLLBACK

Future searches may return to previous policy version.

Historical policy context remains unchanged.

---

# 124. INCIDENT SEVERITY

Potential high-severity incidents:

    evidence mutation
    biometric leakage
    cross-case data exposure
    unauthorized source access
    provenance corruption
    model deployment mismatch
    widespread false-result generation

---

# 125. INCIDENT CONTAINMENT

For serious incidents:

    stop affected processing
       ↓
    preserve logs/audit
       ↓
    identify affected runs
       ↓
    restrict access
       ↓
    investigate
       ↓
    remediate
       ↓
    validate
       ↓
    resume

---

# 126. EVIDENCE MUTATION INCIDENT

If source evidence is accidentally modified:

    immediately stop affected workflow
    preserve original available copies
    preserve audit
    identify all affected records
    follow forensic/legal incident process

Do not silently overwrite the evidence again.

---

# 127. BIOMETRIC LEAK INCIDENT

Identify potentially exposed:

    reference images
    embeddings
    candidate images
    source frames

and follow security incident procedures.

---

# 128. CROSS-CASE LEAK INCIDENT

Immediately:

    disable affected endpoint/query path
    revoke active access where appropriate
    identify affected cases
    preserve audit
    remediate authorization

---

# 129. PROVENANCE INCIDENT

If lineage is unreliable:

    affected results must not be treated as fully verified until integrity is restored.

---

# 130. MODEL INCIDENT

If wrong model weights were deployed:

    identify affected processing runs
    preserve results
    stop incorrect worker
    restore approved model
    decide reprocessing scope

---

# 131. FALSE-RESULT INCIDENT

Unexpected candidate behavior should trigger:

    model/policy investigation

not silent candidate deletion.

---

# 132. AUDITABILITY

Every major operation should be attributable:

    who
    what
    when
    which case
    which source
    which run

---

# 133. ACCESS REVIEW

Periodically review:

    investigator permissions
    admin permissions
    service credentials
    source access
    biometric access

---

# 134. SECRET ROTATION

Rotate:

    database secrets
    RTSP credentials
    service secrets

according to security policy.

---

# 135. KEY ROTATION

Encryption/signing key rotation must not make historical records uninterpretable.

---

# 136. SUPPLY CHAIN

Track approved versions for:

    InsightFace dependencies
    ONNX Runtime
    CUDA/runtime
    FFmpeg
    tracker
    detector
    pgvector client
    database driver

---

# 137. DEPENDENCY SCANNING

CI should scan application/container dependencies using existing CrimeKit tooling.

---

# 138. CONTAINER SCANNING

Block deployment on policy-defined critical vulnerabilities.

---

# 139. IMAGE SIGNING

Where supported by deployment infrastructure, sign trusted production images.

---

# 140. MODEL ARTIFACT SECURITY

Treat model weights as controlled deployment artifacts.

---

# 141. SBOM

Include required software dependency metadata in production release processes.

---

# 142. CONFIGURATION DRIFT

Monitor approved:

    model
    runtime
    policy
    container version

against actual deployment.

---

# 143. READINESS CHECK

Before enabling Face Trace:

[ ] Database ready

[ ] pgvector ready

[ ] model available

[ ] inference runtime ready

[ ] worker healthy

[ ] workflow system ready

[ ] event system ready

[ ] WebSocket ready

[ ] object storage ready

[ ] authorization ready

---

# 144. PRODUCTION SMOKE TEST

Run a small approved test case:

    reference
       ↓
    small MP4
       ↓
    one candidate
       ↓
    source frame
       ↓
    provenance
       ↓
    review

Use controlled non-production or approved operational test data.

---

# 145. LIVE SMOKE TEST

Use a controlled RTSP source.

Verify:

    connect
    detect
    track
    candidate
    event
    UI
    stop

---

# 146. RELEASE GATE — SECURITY

Must pass:

[ ] Authentication

[ ] Case isolation

[ ] Investigation isolation

[ ] Source authorization

[ ] Vector authorization

[ ] Secure frame access

[ ] WebSocket authorization

[ ] Secret leak scan

[ ] Raw vector exposure test

[ ] SSRF/source validation

---

# 147. RELEASE GATE — FORENSICS

Must pass:

[ ] Source immutability

[ ] Hash/integrity integration

[ ] Provenance completeness

[ ] Source-frame recovery

[ ] Processing-run traceability

[ ] Model/version traceability

[ ] Policy/version traceability

[ ] Review traceability

---

# 148. RELEASE GATE — MODEL

Must pass:

[ ] Model artifact verified

[ ] Embedding dimension verified

[ ] Model compatibility verified

[ ] Validation dataset documented

[ ] Threshold evaluated

[ ] Known limitations documented

---

# 149. RELEASE GATE — REALTIME

Must pass:

[ ] bounded queues

[ ] frame-drop policy

[ ] reconnect

[ ] cancellation

[ ] GPU health

[ ] latency measurement

[ ] multi-stream capacity test

[ ] long-duration soak

---

# 150. RELEASE GATE — DATABASE

Must pass:

[ ] migration

[ ] indexes

[ ] foreign keys

[ ] vector configuration

[ ] retention handling

[ ] projection consistency

[ ] backup/restore

---

# 151. RELEASE GATE — FRONTEND

Must pass:

[ ] reference workflow

[ ] evidence selection

[ ] processing state

[ ] candidate list

[ ] source frame

[ ] provenance

[ ] realtime updates

[ ] reconnect

[ ] review

[ ] error handling

---

# 152. RELEASE GATE — EVENTS

Must pass:

[ ] event schema

[ ] versioning

[ ] idempotency

[ ] ordering/reconciliation

[ ] authorization

[ ] outbox/retry

---

# 153. RELEASE GATE — OBSERVABILITY

Must pass:

[ ] logs

[ ] metrics

[ ] traces

[ ] alerts

[ ] dashboard

[ ] worker health

[ ] queue monitoring

---

# 154. SIH DEMO VERTICAL SLICE

The ideal demonstration path:

    1. Investigator opens Face Trace Investigator.
    2. Uploads/selects authorized reference image.
    3. Selects face.
    4. Selects MP4 evidence.
    5. Starts Trace Search.
    6. UI displays processing stages.
    7. Faces are detected.
    8. Tracks appear.
    9. InsightFace embeddings are generated.
    10. pgvector returns candidates.
    11. Candidate sighting appears.
    12. Source frame opens.
    13. Provenance drawer opens.
    14. Investigator reviews result.
    15. Timeline/graph can show the sighting.
    16. Optional controlled RTSP demo shows realtime updates.

---

# 155. DEMO UI STORY

Recommended screen story:

    Reference
       ↓
    Evidence
       ↓
    Processing
       ↓
    Live Findings
       ↓
    Source Verification
       ↓
    Provenance
       ↓
    Review

---

# 156. DEMO TELEMETRY

Show actual values:

    frames processed
    effective FPS
    detections
    active tracks
    candidates
    latency

Never fabricate these values.

---

# 157. DEMO FAILURE STORY

The system should be able to demonstrate that:

    unavailable source
       ≠
    no match

and:

    partial processing
       ≠
    full processing

This increases technical credibility.

---

# 158. DEMO LANGUAGE

Use:

    Machine-generated candidate
    Similarity
    Source evidence
    Review pending
    Provenance

Avoid:

    "AI caught the criminal"

---

# 159. INVESTIGATOR TRUST STORY

The strongest product narrative is:

    "The model does not replace the investigator.
     It reduces the time needed to find and verify
     relevant appearances across authorized evidence."

---

# 160. IMPLEMENTATION CHECKLIST

## Backend

[ ] API resources

[ ] auth/RBAC

[ ] search creation

[ ] processing workflow

[ ] provenance

[ ] matching

[ ] candidate/sighting

[ ] review

[ ] events

## ML

[ ] detector

[ ] tracker

[ ] InsightFace provider

[ ] model registry/context

[ ] quality

[ ] evaluation

## Data

[ ] PostgreSQL schema

[ ] pgvector

[ ] indexes

[ ] retention

[ ] provenance

[ ] Neo4j projection

## Realtime

[ ] RTSP

[ ] bounded queues

[ ] health

[ ] reconnect

[ ] WebSocket

## Frontend

[ ] reference

[ ] evidence selector

[ ] live processing

[ ] candidate cards

[ ] source frame

[ ] provenance

[ ] review

## Operations

[ ] CI/CD

[ ] containers

[ ] GPU runtime

[ ] monitoring

[ ] alerts

[ ] backup

[ ] recovery

---

# 161. FINAL ARCHITECTURE

The production Face Trace architecture is:

    ┌──────────────────────────────────────────────┐
    │              React Investigator UI           │
    │ Reference • Evidence • Findings • Review     │
    └───────────────────────┬──────────────────────┘
                            │ HTTPS / WebSocket
                            ▼
    ┌──────────────────────────────────────────────┐
    │                  FastAPI                     │
    │ Auth • RBAC • API • Query • Review           │
    └───────────────────────┬──────────────────────┘
                            │
                            ▼
    ┌──────────────────────────────────────────────┐
    │          Durable Workflow / Jobs             │
    │ Search • Processing • Retry • Cancellation   │
    └───────────────┬──────────────────────────────┘
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
    ┌─────────────┐      ┌─────────────┐
    │ CPU Workers │      │ GPU Workers │
    │ Decode      │      │ Detect      │
    │ Sampling    │      │ InsightFace │
    │ Tracking    │      │ Embedding   │
    └──────┬──────┘      └──────┬──────┘
           └────────────┬───────┘
                        ▼
    ┌──────────────────────────────────────────────┐
    │               Matching Layer                 │
    │ Scope • pgvector • Similarity • Policy      │
    └───────────────────────┬──────────────────────┘
                            ▼
    ┌──────────────────────────────────────────────┐
    │              PostgreSQL                      │
    │ Candidates • Sightings • Provenance • Review│
    └───────────────┬──────────────────────────────┘
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
    ┌─────────────┐      ┌─────────────┐
    │   pgvector  │      │   Neo4j     │
    │ Retrieval   │      │ Projection  │
    └─────────────┘      └──────┬──────┘
                                │
                                ▼
                         Event / Realtime
                                │
                                ▼
                         Investigator UI

---

# 162. FINAL DATA FLOW

## File

    Evidence
       ↓
    Video
       ↓
    Decode
       ↓
    Sample
       ↓
    Detect
       ↓
    Quality
       ↓
    Track
       ↓
    InsightFace
       ↓
    Embedding
       ↓
    pgvector
       ↓
    Candidate
       ↓
    Sighting
       ↓
    Provenance
       ↓
    Review

## Live

    Authorized RTSP
       ↓
    Bounded Buffer
       ↓
    Decode
       ↓
    Detect
       ↓
    Track
       ↓
    InsightFace
       ↓
    Match
       ↓
    Sighting Update
       ↓
    Persist
       ↓
    WebSocket
       ↓
    Investigator

---

# 163. FINAL OPERATIONAL PRINCIPLE

Speed must never override:

    authorization
    evidence integrity
    provenance
    human review
    truthful reporting

The correct degradation is:

    "Processing slower than source; frames are being sampled/dropped
     according to the configured policy."

The incorrect behavior is:

    "Real-time" while hiding backlog or dropped coverage.

---

# 164. FINAL FORENSIC PRINCIPLE

The original evidence remains authoritative.

Everything generated by Face Trace is derived intelligence:

    detection
    track
    embedding
    candidate
    sighting
    graph relationship
    UI annotation

Derived intelligence must always point back to source evidence.

---

# 165. FINAL MODEL PRINCIPLE

InsightFace provides a representation/comparison capability.

It does not establish:

    guilt
    criminality
    legal identity

The matching engine produces candidates.

The investigator evaluates them.

---

# 166. FINAL DATABASE PRINCIPLE

PostgreSQL preserves authoritative domain state.

pgvector performs authorized vector retrieval.

Neo4j projects relationships.

Events communicate change.

The evidence system preserves source material.

No component should silently replace another component's responsibility.

---

# 167. FINAL REALTIME PRINCIPLE

Realtime means:

    bounded latency
    visible health
    controlled resource use
    reliable updates

It does not mean:

    every source frame must be processed regardless of capacity.

---

# 168. FINAL SECURITY PRINCIPLE

Every sensitive operation must answer:

    Who?
    Which case?
    Which investigation?
    Which source?
    Which model?
    Which policy?

No answer:

    no processing.

---

# 169. FINAL PROVENANCE PRINCIPLE

Every investigator-facing candidate should answer:

    Where did this come from?

The expected chain is:

    Candidate
      ↓
    Sighting
      ↓
    Track
      ↓
    Detection
      ↓
    Frame
      ↓
    Artifact
      ↓
    Evidence
      ↓
    Processing Run
      ↓
    Model + Policy

---

# 170. FINAL IMPLEMENTATION RULE

Before writing new code:

    inspect the existing CrimeKit repository.

Before adding a new subsystem:

    check whether an equivalent abstraction already exists.

Before changing evidence:

    verify immutability.

Before adding a model:

    verify compatibility and approval.

Before exposing a result:

    verify provenance and authorization.

Before claiming performance:

    benchmark it.

Before claiming accuracy:

    evaluate it.

Before claiming a match:

    keep it a candidate until human review.

---

# 171. FINAL DEFINITION OF DONE

Face Trace Investigator is production-ready only when all of the following are true:

[ ] Authorized MP4 processing works.

[ ] Authorized RTSP/CCTV processing works.

[ ] Source evidence is immutable.

[ ] Processing runs are durable.

[ ] Video decoding is bounded/recoverable.

[ ] Frame sampling is explicit.

[ ] Face detection is operational.

[ ] Quality filtering is explicit.

[ ] Tracking is operational.

[ ] InsightFace local/approved runtime is operational.

[ ] Model/version provenance is recorded.

[ ] pgvector retrieval is authorized and bounded.

[ ] Matching policy is versioned.

[ ] Candidates are persisted.

[ ] Sightings aggregate observations.

[ ] Provenance is complete.

[ ] PostgreSQL is authoritative.

[ ] Neo4j projection is traceable.

[ ] Realtime events are secure/idempotent.

[ ] WebSocket reconnect works.

[ ] Human review works.

[ ] Cross-case isolation tests pass.

[ ] Raw biometric exposure tests pass.

[ ] RTSP credential leakage tests pass.

[ ] Load tests pass for target deployment.

[ ] Soak tests pass.

[ ] Failure/recovery tests pass.

[ ] Model evaluation is documented.

[ ] Threshold policy is documented.

[ ] CI/CD is established.

[ ] Monitoring and alerts exist.

[ ] Backup/restore is tested.

[ ] Incident procedures exist.

[ ] No fake telemetry is used.

[ ] No unsupported forensic claims are made.

---

# 172. FINAL PRODUCT STATEMENT

**Face Trace Investigator**

> Trace a reference face across authorized evidence, surface machine-generated candidate sightings in real time, preserve complete forensic provenance, and keep the investigator in control of every final decision.

That is the final production contract for CrimeKit Face Trace Investigator.
