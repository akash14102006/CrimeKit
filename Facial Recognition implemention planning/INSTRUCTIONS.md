# CrimeKit Face Trace Investigator — IMPLEMENTATION INSTRUCTIONS

**Document:** `INSTRUCTIONS.md`  
**Subsystem:** Face Trace Investigator  
**Purpose:** Operational instructions for the engineering agent implementing the feature  
**Audience:** Senior engineers, coding agents, reviewers, QA, infrastructure engineers  
**Mode:** Inspect → Plan → Integrate → Implement → Validate → Review  
**Priority:** Existing CrimeKit architecture, correctness, security, forensic traceability, and maintainability

---

# 1. ROLE

Act as the principal engineer responsible for implementing the CrimeKit Face Trace Investigator subsystem.

Operate as an experienced engineer across:

- InsightFace
- SCRFD
- ArcFace-style face embeddings
- ONNX Runtime
- real-time video processing
- tracking
- vector similarity search
- PostgreSQL
- pgvector
- Neo4j
- Redis/event systems
- WebSockets
- FastAPI
- React/TypeScript
- distributed worker systems
- forensic evidence architecture
- security and privacy
- production observability
- testing and performance engineering

The objective is not to create a facial-recognition demo.

The objective is to implement a maintainable, production-oriented investigative subsystem that integrates into the existing CrimeKit platform without damaging existing functionality.

---

# 2. MANDATORY DOCUMENT ORDER

Before changing code, read the following in order:

1. `MASTER_SPEC.md`
2. `RULES.md`
3. `INSTRUCTIONS.md`
4. `ARCHITECTURE.md`
5. `INSIGHTFACE.md`
6. `BACKEND.md`
7. `FRONTEND.md`
8. `UI.md`
9. `DATA_SECURITY.md`
10. `FORENSIC_PROVENANCE.md`
11. `REALTIME_VIDEO.md`
12. `TESTING_PERFORMANCE.md`
13. `DEPLOYMENT_OPERATIONS.md`

If any file does not exist yet, do not invent its contents.

Use the documents that actually exist.

---

# 3. PHASE 0 — STOP AND INSPECT

Do not immediately begin coding.

First inspect the complete CrimeKit repository.

Determine:

- root structure
- backend entry point
- frontend entry point
- package managers
- Python environment
- TypeScript configuration
- API routing structure
- authentication implementation
- authorization/RBAC implementation
- evidence module
- evidence storage
- forensic workers
- workflow/orchestration
- queue system
- Redis integration
- PostgreSQL integration
- pgvector integration
- Neo4j integration
- WebSocket/event infrastructure
- logging
- telemetry
- testing framework
- Docker setup
- environment configuration
- CI/CD
- current deployment model

Do not assume that the architecture described in documents is already implemented.

The repository is the source of truth for existing implementation.

---

# 4. PHASE 1 — REPOSITORY DISCOVERY

Create an internal mental map before editing.

Map:

    user request
       ↓
    frontend
       ↓
    API
       ↓
    service layer
       ↓
    workflow/queue
       ↓
    worker
       ↓
    database/storage
       ↓
    realtime events
       ↓
    frontend

Then identify where the new face feature should connect.

Record:

- existing reusable service
- existing reusable worker
- existing reusable evidence record
- existing storage abstraction
- existing event publisher
- existing authorization dependency
- existing database conventions
- existing API naming conventions
- existing frontend feature conventions

Do not create replacement versions of these components.

---

# 5. PHASE 2 — DEPENDENCY ANALYSIS

Before adding any dependency, inspect:

- `requirements.txt`
- `pyproject.toml`
- `uv.lock`
- `poetry.lock`
- `package.json`
- lockfiles
- Dockerfiles
- deployment manifests
- CI configuration

Identify whether the repository already contains:

- OpenCV
- InsightFace
- ONNX Runtime
- NumPy
- pgvector
- Redis client
- FFmpeg integration
- video processing tools
- tracking libraries
- WebSocket support

If a dependency already exists, reuse the existing version unless there is a demonstrated compatibility problem.

Do not introduce duplicate libraries for the same responsibility.

---

# 6. PHASE 3 — ARCHITECTURE CONFLICT CHECK

Before implementation, look for conflicts between:

- existing CrimeKit architecture
- feature documentation
- actual code

Classify each conflict:

    IMPLEMENTED
    PLANNED
    OUTDATED
    UNKNOWN
    BLOCKING

Never silently replace an existing implementation because the documentation suggests a different architecture.

Prefer adaptation where possible.

If there is a blocking architectural conflict, stop and document it before making destructive changes.

---

# 7. PHASE 4 — DEFINE THE VERTICAL SLICE

Do not implement every feature simultaneously.

The first working vertical slice must be:

    Authorized Investigator
          ↓
    Reference Image Upload
          ↓
    Reference Face Validation
          ↓
    Local Face Embedding
          ↓
    Select One Video Evidence
          ↓
    Create Async Job
          ↓
    Decode Video
          ↓
    Sample Frames
          ↓
    Face Detection
          ↓
    Face Quality
          ↓
    Tracking
          ↓
    Candidate Similarity
          ↓
    Sighting
          ↓
    Provenance
          ↓
    Persistent Result
          ↓
    WebSocket Event
          ↓
    React Finding
          ↓
    Source Frame
          ↓
    Investigator Review

Do not add multi-camera scale before the single-video path is stable.

---

# 8. PHASE 5 — CREATE THE FEATURE BOUNDARY

Use the existing CrimeKit module structure.

Conceptual boundary:

    forensic/
        face-intelligence/

Possible internal responsibility boundaries:

    detection
    recognition
    quality
    tracking
    matching
    aggregation
    provenance
    workers

Do not create a new directory if the repository already has an established equivalent.

The exact path must follow existing CrimeKit architecture.

---

# 9. PHASE 6 — ESTABLISH DOMAIN CONTRACTS FIRST

Before implementation, define the internal contracts.

At minimum, understand these conceptual objects:

    FaceInvestigation
    FaceReference
    FaceEmbedding
    FaceSearchJob
    FaceDetection
    FaceTrack
    FaceCandidate
    FaceSighting
    FaceReview
    FaceProcessingRun
    FaceModel
    FaceMatchingPolicy

Do not create duplicate versions of an existing entity.

If CrimeKit already has:

    ProcessingJob

then determine whether FaceSearchJob should specialize/reuse it rather than creating an unrelated job system.

---

# 10. PHASE 7 — IMPLEMENT REFERENCE PIPELINE

Implement the reference image workflow first.

Required sequence:

    upload
      ↓
    validate file
      ↓
    decode
      ↓
    detect faces
      ↓
    handle face count
      ↓
    quality evaluation
      ↓
    alignment/preprocessing
      ↓
    embedding
      ↓
    validate embedding
      ↓
    persist metadata
      ↓
    protected embedding persistence

Requirements:

- exactly one intended reference face
- no silent selection among multiple faces
- no source-image overwrite
- no raw vector logging
- model/version metadata recorded
- authorization checked

---

# 11. PHASE 8 — INSIGHTFACE ADAPTER

Keep all provider-specific inference behind the model abstraction.

The rest of CrimeKit should depend on a stable internal contract, not raw InsightFace classes.

Conceptual:

    CrimeKit
       ↓
    FaceModelProvider
       ↓
    InsightFaceAdapter
       ↓
    ONNX Runtime

The adapter must expose enough metadata to identify:

- provider
- model
- model version
- runtime
- embedding dimension

Do not expose raw implementation details across the application.

---

# 12. PHASE 9 — MODEL STARTUP

Model loading must happen during worker initialization.

Startup sequence:

    process starts
       ↓
    configuration loaded
       ↓
    model artifact verified
       ↓
    runtime initialized
       ↓
    model loaded
       ↓
    smoke inference
       ↓
    worker READY

If the model cannot be loaded:

    worker NOT_READY

Do not allow the worker to accept production inference jobs.

---

# 13. PHASE 10 — MODEL COMPATIBILITY

Before writing an embedding:

Validate:

- model identity
- model version
- embedding dimension
- normalization expectation
- preprocessing version

Before vector search:

Validate:

- reference model compatibility
- candidate model compatibility
- vector dimensionality
- configured metric

Never compare incompatible embeddings simply because the database can mathematically calculate a distance.

---

# 14. PHASE 11 — VIDEO PIPELINE

After the reference pipeline works, implement one local/test video.

Required order:

    video evidence
       ↓
    authorization
       ↓
    decoder
       ↓
    source timestamps
       ↓
    frame sampling
       ↓
    face detection
       ↓
    quality filter
       ↓
    tracking
       ↓
    embedding
       ↓
    matching

Do not initially optimize for multiple cameras.

Do not start with RTSP complexity unless the existing project already requires it.

---

# 15. PHASE 12 — VIDEO DECODING

Use the project's existing media/decode infrastructure where available.

If adding a decoder:

- verify codec support
- verify timestamp handling
- handle corrupt frames
- handle end-of-stream
- record source metadata
- bound resource consumption

Do not load an entire large video into memory.

Use streaming/chunked processing.

---

# 16. PHASE 13 — FRAME SAMPLING

Start with a documented, configurable sampling policy.

Example:

    source FPS = 25
    recognition sample rate = configurable

Do not assume the sample rate should be a fixed number for all cameras.

Record the sampling configuration in the processing run.

Later, after measurement, consider adaptive sampling.

Do not add adaptive behavior before the baseline is understood.

---

# 17. PHASE 14 — DETECTION

For each selected frame:

    frame
      ↓
    face detector
      ↓
    zero or more detections

Each detection must include:

- detection ID
- source evidence
- frame number if available
- timestamp
- bounding box
- detector score
- processing run ID

Do not discard source frame identity.

---

# 18. PHASE 15 — FACE QUALITY

Before recognition:

    detection
       ↓
    quality assessment
       ↓
    eligible / ineligible

Quality can consider:

- face size
- blur
- pose
- occlusion
- illumination
- alignment
- detection score

Keep quality separate from similarity.

A similarity score must not be allowed to hide poor source quality.

---

# 19. PHASE 16 — TRACKING

Add tracking after reliable detection.

Conceptually:

    detection frames
          ↓
    tracker
          ↓
    track

Every track must retain:

- track ID
- evidence ID
- first timestamp
- last timestamp
- source detections
- tracker version/configuration

Do not equate:

    track_id

with:

    confirmed_person_id

Tracking and identity are separate concepts.

---

# 20. PHASE 17 — RECOGNITION

Generate embeddings only for eligible observations.

Use the approved local InsightFace model adapter.

Do not call external hosted inference services in the normal production pipeline.

Do not initialize the model inside the frame loop.

Bad:

    for frame:
        model = load_model()
        model.predict(frame)

Correct conceptual model:

    worker startup:
        model = load_model()

    processing:
        model.predict(face)

---

# 21. PHASE 18 — MATCHING

Start with deterministic similarity matching.

Inputs:

    reference_embedding
    candidate_embedding
    matching_policy

Outputs:

    similarity
    candidate decision
    policy metadata

The matching implementation must not hard-code unexplained threshold values.

Use configuration/policy.

Every result must identify the policy version.

---

# 22. PHASE 19 — VECTOR SEARCH

For a single reference against the faces of one video, direct similarity calculations may be sufficient for the initial vertical slice.

Use pgvector when the system requires large-scale candidate retrieval.

Do not introduce a vector database query for every frame unnecessarily.

Preferred progression:

    Phase 1:
    reference vector
       ↓
    candidate embedding
       ↓
    direct similarity

    Phase 2:
    many known references
       ↓
    pgvector retrieval
       ↓
    candidate ranking

Measure before optimizing.

---

# 23. PHASE 20 — TRACK-LEVEL MATCHING

Do not generate an investigator alert for every matching frame.

Instead:

    frame observations
          ↓
    track aggregation
          ↓
    candidate track
          ↓
    sighting

Keep underlying observations for forensic traceability.

---

# 24. PHASE 21 — SIGHTING AGGREGATION

Implement an explicit aggregation service.

Input:

    candidate observations

Output:

    face sighting

A sighting should contain:

- source evidence
- track
- first observed time
- last observed time
- best observation
- best similarity
- observation count
- processing run
- matching policy

Do not delete observations after aggregation.

---

# 25. PHASE 22 — PROVENANCE

Before exposing any candidate result to the frontend, ensure the provenance chain exists.

Required conceptual path:

    case
      ↓
    investigation
      ↓
    search job
      ↓
    processing run
      ↓
    evidence
      ↓
    artifact
      ↓
    frame
      ↓
    detection
      ↓
    track
      ↓
    candidate
      ↓
    sighting

If a new result cannot follow this path, stop and fix provenance before continuing.

---

# 26. PHASE 23 — DATABASE PERSISTENCE

Persist data using the existing CrimeKit database conventions.

Avoid creating:

    face_db.py
    face_database.py
    face_repository.py
    face_store.py

all doing overlapping jobs.

Choose the appropriate existing pattern.

Database writes should use:

- transactions where required
- constraints
- foreign keys
- proper indexes
- idempotency safeguards

---

# 27. PHASE 24 — NEO4J INTEGRATION

Do not start with Neo4j.

First make the relational forensic model correct.

Then add graph projection.

The graph should reference domain entities such as:

    FaceSighting
    Evidence
    FaceTrack
    Time
    Location

Do not create a graph node called:

    Criminal

from a machine-generated face candidate.

Graph edges must remain explainable and provenance-linked.

---

# 28. PHASE 25 — REAL-TIME EVENTS

After persistence works, add event publication.

Sequence:

    domain event
       ↓
    event publisher
       ↓
    Redis/event infrastructure
       ↓
    WebSocket gateway
       ↓
    React

Do not make the WebSocket the persistence mechanism.

Persist first where event semantics require authoritative state.

---

# 29. PHASE 26 — EVENT DESIGN

Use stable event names and versions.

Conceptual:

    face_job.started
    face_job.progress
    face_track.created
    face_candidate.detected
    face_sighting.created
    face_job.completed
    face_job.failed
    face_job.cancelled

Each event should include appropriate identifiers.

Never include raw embedding vectors.

---

# 30. PHASE 27 — WEB SOCKET RECONNECTION

Implement this sequence:

    Browser connects
       ↓
    receives live events

Network failure:

    WebSocket disconnects

Browser:

    reconnect
       ↓
    fetch authoritative investigation state
       ↓
    resume event stream

Do not attempt to reconstruct the entire investigation solely from missed WebSocket messages.

---

# 31. PHASE 28 — FRONTEND INTEGRATION

Add the frontend using existing CrimeKit conventions.

First implement:

    Reference Image
    Evidence Selector
    Start Search
    Processing Status
    Findings

Then:

    Candidate Detail
    Source Frame
    Timeline
    Review

Do not redesign the entire CrimeKit investigation workspace for this feature.

---

# 32. PHASE 29 — UI STATES

Explicitly implement:

    EMPTY
    UPLOADING
    VALIDATING
    READY
    QUEUED
    PROCESSING
    MATCHING
    FINDING
    COMPLETED
    NO_MATCHES
    PARTIAL_RESULTS
    FAILED
    CANCELLED

The interface must remain understandable during all processing states.

---

# 33. PHASE 30 — INVESTIGATOR REVIEW

Implement review after candidate generation.

Candidate:

    PENDING

Then investigator may choose an approved review state.

Every review operation must:

- verify authorization
- update state
- record reviewer
- record time
- preserve audit history

The machine must not perform the final investigator decision.

---

# 34. PHASE 31 — SECURITY INTEGRATION

Before declaring the feature complete, verify all existing security controls.

Check:

- authentication
- case authorization
- evidence authorization
- role permissions
- cross-case restrictions
- source-frame access
- export permissions
- audit logging

Do not trust frontend authorization state.

The backend must enforce the final decision.

---

# 35. PHASE 32 — DATA PROTECTION

Review all code paths for:

- face images
- face crops
- embeddings
- metadata
- source frames
- logs
- analytics
- WebSocket payloads
- error responses

Remove unnecessary exposure.

Never print embeddings or secrets.

---

# 36. PHASE 33 — ERROR HANDLING

Every critical stage must have controlled failure handling.

Examples:

    reference decode failure
    no face
    multiple faces
    low quality
    model unavailable
    GPU unavailable
    corrupt video
    decode failure
    database timeout
    vector search failure
    event failure

Each failure should:

1. Produce a known error state.
2. Preserve useful diagnostics.
3. Avoid exposing sensitive internal details.
4. Avoid fabricating results.
5. Be observable.

---

# 37. PHASE 34 — RETRY DESIGN

Identify which operations are safe to retry.

Safe candidates may include:

- transient database operations
- event publication
- worker pickup

But retrying inference must not accidentally duplicate:

- detections
- candidates
- sightings
- reviews

Use processing-run IDs and deterministic/unique identifiers as appropriate.

---

# 38. PHASE 35 — CANCELLATION

Cancellation must be explicit.

Sequence:

    user requests cancel
       ↓
    authorization
       ↓
    job transitions
       ↓
    worker stops new processing
       ↓
    persisted observations remain valid
       ↓
    job marked CANCELLED

Do not delete valid forensic output merely because remaining processing was cancelled.

---

# 39. PHASE 36 — TESTING

Write tests at each layer before declaring the feature stable.

## Unit

Test:

- file validation
- face count validation
- quality policy
- embedding validation
- similarity
- threshold policy
- track aggregation
- sighting aggregation
- event serialization
- state transitions

## Integration

Test:

    API
      ↓
    job
      ↓
    worker
      ↓
    database
      ↓
    event

## Security

Test:

- unauthorized case
- unauthorized evidence
- cross-case access
- restricted source-frame access
- restricted review

## Realtime

Test:

- event delivery
- duplicate events
- reconnect
- state recovery

---

# 40. PHASE 37 — MODEL EVALUATION

Do not call the matching behavior production-grade without evaluation.

Create an authorized evaluation dataset representing intended CrimeKit conditions.

Measure:

- false accepts
- false rejects
- precision
- recall
- ROC/DET where appropriate

Evaluate difficult conditions where relevant:

- low light
- blur
- profile
- occlusion
- small faces
- video compression
- distance
- crowded scenes

Thresholds must be derived from evaluation, not copied from a random example.

---

# 41. PHASE 38 — PERFORMANCE BASELINE

Establish baseline metrics before optimization.

Measure:

    video decode FPS
    frames sampled/sec
    faces detected/sec
    embeddings/sec
    matching latency
    vector search latency
    end-to-end latency
    queue latency
    GPU utilization
    GPU memory
    CPU utilization
    memory usage

Record hardware and software environment.

---

# 42. PHASE 39 — LOAD TESTING

After a working baseline, test increasing load.

Example:

    1 video
    5 videos
    10 videos

For live stream architecture where applicable:

    1 camera
    multiple concurrent cameras

Do not invent scale claims from theoretical capacity.

Report measured results.

---

# 43. PHASE 40 — FAILURE TESTING

Test:

- worker crash
- model initialization failure
- GPU failure
- corrupt video
- empty video
- no face
- many faces
- database interruption
- event system interruption
- browser refresh
- WebSocket disconnect
- job cancellation
- duplicate job execution

Every failure must have a deterministic expected behavior.

---

# 44. PHASE 41 — OBSERVABILITY

Before deployment, verify:

- structured logs
- metrics
- health endpoint
- readiness endpoint
- worker status
- job status
- processing latency
- queue depth
- failure counts

Sensitive biometric information must not appear in telemetry.

---

# 45. PHASE 42 — DEPLOYMENT VALIDATION

Validate:

    local development
    test environment
    container build
    runtime startup
    model startup
    database migration
    vector index
    event infrastructure
    frontend build
    backend startup

Do not claim production readiness solely because local development works.

---

# 46. PHASE 43 — MODEL DEPLOYMENT VALIDATION

Before deployment:

[ ] exact model artifact is identified

[ ] licensing status is recorded

[ ] model checksum/integrity check works where applicable

[ ] runtime version is recorded

[ ] embedding dimension is verified

[ ] test inference succeeds

[ ] matching policy is versioned

[ ] historical results remain attributable to their original model

---

# 47. PHASE 44 — SECURITY REVIEW

Perform a focused review for:

- IDOR
- missing case authorization
- unrestricted media access
- cross-case search
- embedding leakage
- log leakage
- WebSocket authorization
- insecure object-storage URLs
- secret exposure
- insufficient audit logging
- overly broad service permissions

Do not merge until critical findings are resolved.

---

# 48. PHASE 45 — DOCUMENTATION

Update implementation documentation only after verifying the real code.

Document:

- what is actually implemented
- what is experimental
- what is planned
- what model is used
- what matching policy is used
- what limitations remain
- what performance was measured
- what deployment configuration is required

Never document unimplemented capabilities as production features.

---

# 49. PHASE 46 — DEMO VALIDATION

For the SIH/demo flow, verify this exact experience:

    1. Investigator opens a case.
    2. Investigator opens Face Trace Investigator.
    3. Investigator uploads a reference image.
    4. System validates the reference.
    5. Investigator selects video evidence.
    6. Investigator starts the search.
    7. UI immediately shows QUEUED/PROCESSING.
    8. Video processing begins asynchronously.
    9. Live progress appears.
    10. Candidate sighting appears.
    11. Investigator opens candidate.
    12. Exact source frame is displayed.
    13. Timestamp and evidence are displayed.
    14. Provenance is visible.
    15. Investigator reviews the candidate.
    16. Review action is audited.
    17. Timeline/graph integration is visible where implemented.

No step should be mocked in the final demo if it is presented as a working feature.

---

# 50. PHASE 47 — FINAL VALIDATION COMMANDS

Use the repository's actual package/build/test tools.

Run, as applicable:

    backend tests
    frontend tests
    type checks
    lint
    import validation
    database migration validation
    Docker build
    container startup
    API smoke tests
    WebSocket smoke tests
    security checks
    dependency audit
    performance tests

Then inspect:

    git status
    git diff
    git diff --stat

Confirm there are no unrelated modifications.

---

# 51. PHASE 48 — SAFE CHANGE REVIEW

Before completion, compare:

    requested feature
          vs
    implemented feature

Confirm:

- no unrelated refactor
- no unnecessary dependency
- no duplicate architecture
- no duplicate model service
- no new security bypass
- no evidence mutation
- no missing provenance
- no undocumented threshold
- no fake confidence
- no fake agent
- no placeholder implementation presented as complete

---

# 52. PHASE 49 — PERFORMANCE OPTIMIZATION ORDER

Only optimize after functional correctness.

Recommended order:

    1. Correctness
    2. Provenance
    3. Authorization
    4. Reliability
    5. Baseline measurement
    6. Decoder efficiency
    7. Frame sampling
    8. Tracking
    9. Batch inference
    10. GPU utilization
    11. Vector search
    12. Worker scaling
    13. Multi-camera optimization

Do not prematurely optimize the vector database when the dominant bottleneck is video decoding.

---

# 53. PHASE 50 — SCALE ARCHITECTURE

Once the single-video path works, evolve toward:

    Camera / Evidence
          ↓
    Stream / Job Queue
          ↓
    Video Workers
          ↓
    GPU Face Workers
          ↓
    Matching Service
          ↓
    Sighting Aggregator
          ↓
    Persistence
          ↓
    Event Bus
          ↓
    WebSocket
          ↓
    UI

Use worker pools rather than increasing API process count as the primary face-inference scaling mechanism.

---

# 54. PHASE 51 — LIVE RTSP

Implement RTSP only after file-based video search works.

Live pipeline:

    RTSP
      ↓
    reconnecting decoder
      ↓
    bounded frame buffer
      ↓
    detection/tracking
      ↓
    recognition
      ↓
    match
      ↓
    sighting/event

Requirements:

- reconnect
- stream health
- bounded memory
- source timestamp handling
- no duplicate alerts
- auditability

---

# 55. PHASE 52 — MULTI-CAMERA SEARCH

When adding multiple cameras:

Process each source independently.

    CCTV-01
       ↓
    source-specific track IDs

    CCTV-02
       ↓
    source-specific track IDs

Then:

    sightings
       ↓
    case-level temporal correlation

Never reuse a tracker ID across sources.

---

# 56. PHASE 53 — CROSS-CASE SEARCH

Treat cross-case search as a separate privileged capability.

It must require:

- explicit role permission
- scope selection
- audit
- result filtering
- protected data handling

Do not add it merely because the vector index technically supports it.

---

# 57. PHASE 54 — AI AGENT INTEGRATION

Only after deterministic face processing is stable may CrimeKit AI agents consume the results.

Example:

    Face Sighting
      ↓
    Timeline
      ↓
    Evidence Graph
      ↓
    AI Investigator

The AI can explain/correlate evidence.

It must not replace the face-processing pipeline.

---

# 58. PHASE 55 — AI RESPONSE RULE

When an AI agent discusses a face-related finding, it must be grounded in structured evidence.

The agent should be able to reference:

- sighting ID
- evidence ID
- timestamp
- source artifact
- review state

Do not let an LLM invent a face match that is not present in the forensic records.

---

# 59. PHASE 56 — CODE QUALITY

Implementation must follow existing CrimeKit conventions for:

- naming
- typing
- dependency injection
- error handling
- API schemas
- repository structure
- logging
- tests
- migrations

Prefer simple, readable code over excessive abstraction.

Add an abstraction only when it reduces coupling or represents a genuine domain boundary.

---

# 60. PHASE 57 — NO MAGIC

Avoid hard-coded:

- thresholds
- model paths
- GPU IDs
- queue limits
- sample rates
- timeouts
- storage locations
- secrets

Use the project's existing configuration system.

---

# 61. PHASE 58 — NO DUPLICATE SOURCE OF TRUTH

There must be one authoritative source for each concept.

Examples:

    job state
    authorization
    matching policy
    model metadata
    evidence identity

Do not create a second implementation merely because it is easier locally.

---

# 62. PHASE 59 — NO FAKE PRODUCTION CLAIMS

Do not write:

    "real-time"
    "enterprise-grade"
    "99% accurate"
    "production-ready"

unless the implementation and measurement support the claim.

Use precise statements such as:

    "GPU benchmarked at X FPS on Y hardware"

when such a measurement exists.

---

# 63. PHASE 60 — IMPLEMENTATION PRIORITY

When trade-offs are necessary, prioritize:

    1. Evidence integrity
    2. Security
    3. Correctness
    4. Provenance
    5. Human review
    6. Reliability
    7. Maintainability
    8. Performance
    9. UX polish
    10. Optional optimization

Never trade evidence integrity or security merely for demo speed.

---

# 64. PHASE 61 — WHEN TO STOP

Stop coding and report the blocker when:

- existing architecture is incompatible
- required authentication is missing
- evidence provenance cannot be preserved
- model license status is unresolved for the intended deployment
- model artifacts cannot be verified
- existing database schema conflicts with the required semantics
- critical security controls cannot be enforced
- a requested feature requires destructive modification of unrelated code

Do not hide architectural blockers with temporary hacks.

---

# 65. PHASE 62 — FINAL REVIEW QUESTIONS

Before declaring complete, answer:

## Architecture

Can another engineer explain the entire data path?

## Model

Can we identify exactly which model created each embedding?

## Evidence

Can we open the exact source frame?

## Security

Can an unauthorized investigator access the result?

## Matching

Can we explain how the candidate was generated?

## Real time

Can the UI recover after reconnect?

## Reliability

What happens if the worker dies?

## Performance

What was actually measured?

## Operations

Can an operator determine why a job failed?

## Investigation

Can the human investigator review the candidate?

## History

Can historical results still be interpreted after a model upgrade?

If any answer is NO, the feature is not finished.

---

# 66. REQUIRED FINAL REPORT FROM THE IMPLEMENTATION AGENT

At the end of implementation, provide a concise engineering report containing:

    IMPLEMENTED
    PARTIALLY IMPLEMENTED
    NOT IMPLEMENTED
    BLOCKED

Then include:

### Architecture changes

What was integrated and where.

### Model

Exact model/provider/runtime.

### APIs

New or modified endpoints.

### Database

Migrations/tables/indexes.

### Worker

Worker behavior and concurrency.

### Realtime

Events and WebSocket changes.

### Security

Authorization and data protection.

### Tests

Tests executed and results.

### Performance

Measured results and hardware/environment.

### Known limitations

Explicit unresolved areas.

### Files changed

Actual paths only.

Do not invent files in the report.

---

# 67. FINAL AGENT PRINCIPLE

Do not code from imagination.

Do not code from architecture diagrams alone.

Do not code from documentation alone.

The correct workflow is:

    READ
      ↓
    INSPECT
      ↓
    MAP
      ↓
    VERIFY
      ↓
    PLAN
      ↓
    IMPLEMENT
      ↓
    TEST
      ↓
    MEASURE
      ↓
    REVIEW
      ↓
    DOCUMENT

The existing CrimeKit repository is the source of truth for what already exists.

The Face Trace Investigator documentation is the source of truth for what the new feature is supposed to accomplish.

When the two conflict, identify the conflict explicitly and resolve it deliberately.

Never silently break CrimeKit to force the repository into an imagined architecture.

---

# 68. FINAL QUALITY BAR

The implementation is successful when:

    an authorized investigator
          ↓
    uploads a reference face
          ↓
    selects authorized evidence
          ↓
    starts a search
          ↓
    processing runs asynchronously
          ↓
    InsightFace performs local inference
          ↓
    video faces are detected and tracked
          ↓
    candidate observations are generated
          ↓
    sightings are aggregated
          ↓
    provenance is preserved
          ↓
    results are persisted
          ↓
    live events reach the UI
          ↓
    source frames can be verified
          ↓
    investigator review is recorded

and every step remains:

    secure
    traceable
    versioned
    testable
    observable
    maintainable

That is the implementation standard for CrimeKit Face Trace Investigator.
