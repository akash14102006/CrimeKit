# CrimeKit Face Trace Investigator — ARCHITECTURE

**Document:** `ARCHITECTURE.md`  
**Subsystem:** Face Trace Investigator  
**Status:** Authoritative target architecture  
**Audience:** Principal engineers, backend, forensic, ML, frontend, database, infrastructure, security, and QA teams

---

# 1. ARCHITECTURE OBJECTIVE

The CrimeKit Face Trace Investigator must integrate facial analysis into the existing digital-forensics platform without turning CrimeKit into a generic facial-recognition application.

The architecture must preserve five properties simultaneously:

1. **Forensic integrity**
2. **Biometric security**
3. **Real-time user experience**
4. **Scalable inference**
5. **Clear separation of responsibilities**

The subsystem must support this primary workflow:

    Authorized Investigator
            ↓
    Reference Face
            ↓
    Face Validation
            ↓
    Reference Embedding
            ↓
    Authorized Evidence
            ↓
    Asynchronous Search
            ↓
    Video Decode / Frame Processing
            ↓
    Face Detection
            ↓
    Face Quality
            ↓
    Tracking
            ↓
    Embedding
            ↓
    Candidate Matching
            ↓
    Sighting Aggregation
            ↓
    Provenance
            ↓
    PostgreSQL / pgvector / Neo4j
            ↓
    Real-Time Events
            ↓
    Investigator UI
            ↓
    Source Verification
            ↓
    Human Review

---

# 2. ARCHITECTURAL POSITIONING INSIDE CRIMEKIT

The Face Trace Investigator is a forensic processing capability.

It belongs conceptually here:

    CrimeKit
       │
       ├── Evidence
       │
       ├── Forensic Processing
       │      ├── Disk
       │      ├── Mobile
       │      ├── Documents
       │      ├── Images
       │      ├── Video
       │      ├── Audio
       │      └── Face Intelligence
       │
       ├── Investigation Intelligence
       │
       ├── Timeline
       │
       ├── Graph
       │
       ├── AI Agents
       │
       └── Reporting

Face intelligence produces structured forensic observations.

AI agents may later reason over those observations.

Do not reverse these responsibilities.

---

# 3. ARCHITECTURAL BOUNDARIES

The subsystem is divided into the following logical boundaries:

    1. Presentation
    2. API
    3. Authorization
    4. Application/Domain
    5. Workflow
    6. Video Processing
    7. Face Inference
    8. Tracking
    9. Matching
    10. Sighting Aggregation
    11. Persistence
    12. Event Delivery
    13. Observability
    14. Security

Each boundary must have a clear responsibility.

---

# 4. CONTEXT DIAGRAM

                         ┌────────────────────┐
                         │    Investigator    │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ CrimeKit Web App   │
                         │ React / TypeScript │
                         └─────────┬──────────┘
                                   │
                           HTTPS / WebSocket
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   CrimeKit API     │
                         │      FastAPI       │
                         └─────────┬──────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               │                   │                   │
               ▼                   ▼                   ▼
        Authentication       Case Authorization    Job Creation
               │                   │                   │
               └───────────────────┼───────────────────┘
                                   │
                                   ▼
                          Workflow / Queue
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       Reference Worker       Video Workers       Match Workers
              │                    │                    │
              ▼                    ▼                    ▼
       Face Inference        Decode + Detect       Vector Search
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
                                   ▼
                         Sighting Aggregation
                                   │
                  ┌────────────────┼────────────────┐
                  │                │                │
                  ▼                ▼                ▼
             PostgreSQL        pgvector          Neo4j
                  │                │                │
                  └────────────────┼────────────────┘
                                   │
                                   ▼
                              Event Bus
                                   │
                                   ▼
                              WebSocket
                                   │
                                   ▼
                            React UI Update

Evidence media remains in the approved CrimeKit evidence/object-storage layer.

---

# 5. DEPLOYMENT VIEW

A production-oriented deployment should conceptually separate workloads:

                     ┌─────────────────┐
                     │  Load Balancer  │
                     └────────┬────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
        ┌──────────────┐             ┌──────────────┐
        │ API Workers  │             │ WS Gateway   │
        │   FastAPI    │             │ / Realtime   │
        └──────┬───────┘             └──────┬───────┘
               │                            │
               └──────────────┬─────────────┘
                              ▼
                      Workflow / Queue
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          Video Workers  GPU Workers   Match Workers
                │             │             │
                │             │             │
                └─────────────┼─────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
       PostgreSQL          pgvector            Neo4j
           │                                     │
           └──────────────────┬──────────────────┘
                              ▼
                         Object Storage

The exact infrastructure must follow the existing CrimeKit deployment architecture.

---

# 6. COMPONENT MODEL

## 6.1 Frontend

Responsibilities:

- authentication-aware UI
- case selection
- reference upload
- evidence selection
- investigation creation
- processing display
- live findings
- timeline
- source-frame viewing
- provenance
- review controls

Does not perform authoritative inference.

---

## 6.2 API Layer

Responsibilities:

- authentication
- authorization
- request validation
- investigation lifecycle
- evidence scope validation
- job creation
- status retrieval
- candidate retrieval
- review commands
- cancellation

The API is not an inference worker.

---

## 6.3 Application/Domain Layer

Responsibilities:

- FaceInvestigation lifecycle
- validation policy
- domain rules
- candidate semantics
- sighting semantics
- review semantics
- orchestration decisions

This layer should not know low-level OpenCV or CUDA implementation details.

---

## 6.4 Workflow Layer

Responsibilities:

- durable orchestration
- retries
- state transitions
- cancellation
- timeout handling
- worker coordination
- progress

Use the existing CrimeKit workflow infrastructure where present.

If Temporal is already the project's durable workflow engine, use Temporal.

If an existing queue/worker system already owns this responsibility, integrate with it rather than adding a parallel system.

---

## 6.5 Video Worker

Responsibilities:

- open media
- decode frames
- preserve source timing
- sample frames
- handle media errors
- create detection work units

The worker should not own case authorization.

---

## 6.6 Face Inference Worker

Responsibilities:

- load model
- detect faces
- quality assessment
- alignment/preprocessing
- generate embeddings

The worker should expose a stable service interface to the rest of CrimeKit.

---

## 6.7 Tracking Layer

Responsibilities:

- associate detections across adjacent frames
- maintain track lifecycle
- produce track identifiers
- preserve source-detection relationships

Tracking does not decide identity.

---

## 6.8 Matching Layer

Responsibilities:

- compare embeddings
- vector retrieval
- candidate scoring
- matching policy evaluation

It must be independent from UI rendering.

---

## 6.9 Sighting Aggregator

Responsibilities:

- combine frame-level candidate observations
- use track/time continuity
- create investigator-friendly sightings
- preserve underlying observations

---

## 6.10 Persistence Layer

Responsibilities:

- transactional records
- vector persistence/retrieval
- graph projection
- provenance relationships
- review records

---

## 6.11 Event Layer

Responsibilities:

- publish processing events
- publish candidate/sighting events
- maintain event versioning
- deliver through existing event infrastructure

---

# 7. DATA FLOW — REFERENCE IMAGE

The reference image path is:

    Investigator
         │
         ▼
    Upload API
         │
         ▼
    Authorization
         │
         ▼
    Evidence / Artifact
         │
         ▼
    Reference Validation Job
         │
         ▼
    Face Detector
         │
         ▼
    Face Count
       /   \
      /     \
   0       >1
   │        │
 Reject   Resolve ambiguity
      \     /
       \   /
       1
       │
       ▼
    Quality Evaluation
       │
   ┌───┴────┐
   ▼        ▼
 PASS     REVIEW/REJECT
   │
   ▼
 Alignment / Preprocessing
   │
   ▼
 Embedding Model
   │
   ▼
 Embedding Validation
   │
   ▼
 Persist Reference + Metadata
   │
   ▼
 REFERENCE_READY

---

# 8. DATA FLOW — VIDEO

Video search:

    Investigator
         │
         ▼
    Search Request
         │
         ▼
    Authorization
         │
         ▼
    Create Job
         │
         ▼
    Queue / Workflow
         │
         ▼
    Video Worker
         │
         ▼
    Decode
         │
         ▼
    Frame Sampling
         │
         ▼
    Face Detection
         │
         ▼
    Quality Filter
         │
         ▼
    Tracking
         │
         ▼
    Eligible Face Crops
         │
         ▼
    Embedding
         │
         ▼
    Similarity
         │
         ▼
    Candidate Observation
         │
         ▼
    Track Aggregation
         │
         ▼
    Sighting
         │
         ▼
    Provenance Persistence
         │
         ▼
    Event Publication
         │
         ▼
    UI

---

# 9. REFERENCE EMBEDDING LIFECYCLE

A reference embedding has the following lifecycle:

    Uploaded Image
         ↓
    Validated Image
         ↓
    Detected Face
         ↓
    Quality Approved
         ↓
    Preprocessed Face
         ↓
    Model Inference
         ↓
    Embedding
         ↓
    Compatibility Validation
         ↓
    Protected Persistence
         ↓
    Search Input

Reference embeddings are derived data.

They are not a replacement for the original image.

---

# 10. VIDEO OBSERVATION LIFECYCLE

Each observation progresses through:

    Frame
      ↓
    Detection
      ↓
    Quality
      ↓
    Track Association
      ↓
    Embedding
      ↓
    Similarity
      ↓
    Candidate Observation
      ↓
    Aggregation
      ↓
    Sighting

At every stage, source identifiers must remain available.

---

# 11. TRACK VS IDENTITY ARCHITECTURE

The system must maintain three distinct concepts:

    Detection
       = one visual face occurrence in one frame

    Track
       = temporal association of detections

    Candidate Identity
       = matching hypothesis generated by the recognition system

These are NOT interchangeable.

Correct:

    detection → track → candidate → sighting

Incorrect:

    track → confirmed person

unless an authorized downstream workflow explicitly creates that relationship.

---

# 12. SIGHTING ARCHITECTURE

A sighting is an investigator-oriented aggregation.

Example:

    Detection 101  similarity .88
    Detection 102  similarity .91
    Detection 103  similarity .93
    Detection 104  similarity .90

becomes:

    SIGHTING-001

      source = CCTV-01
      track = TRACK-017
      start = 14:21:01
      end = 14:21:04
      best_similarity = .93
      observations = 4

The underlying observations remain queryable.

---

# 13. REAL-TIME ARCHITECTURE

The live system should use:

    Worker
      ↓
    Domain Event
      ↓
    Event Infrastructure
      ↓
    WebSocket Gateway
      ↓
    Browser

Do not stream every frame event to the UI.

Instead publish meaningful state changes.

Example:

    face_job.progress

rather than:

    face.frame_processed

for every frame.

This prevents unnecessary frontend traffic.

---

# 14. EVENT SEPARATION

Classify events as:

## Job events

    job.created
    job.queued
    job.started
    job.progress
    job.completed
    job.failed
    job.cancelled

## Face events

    face.detected
    face.track_created
    face.candidate_created

## Sighting events

    sighting.created
    sighting.updated

## Review events

    review.created
    review.updated

Use the project's existing event naming convention when available.

---

# 15. EVENT DATA FLOW

Example:

    Video Worker
        │
        ▼
    Candidate Sighting
        │
        ├── persist
        │
        └── publish event
                 │
                 ▼
             Event Bus
                 │
                 ▼
          WebSocket Gateway
                 │
                 ▼
              Browser
                 │
                 ▼
            Live Finding

The event does not replace persistence.

---

# 16. FAILURE ISOLATION

A failure in one layer must not unnecessarily destroy unrelated layers.

Example:

    WebSocket unavailable

must NOT imply:

    forensic processing failed

Likewise:

    Neo4j unavailable

should not automatically imply:

    original evidence unavailable

The domain must record degraded behavior appropriately.

---

# 17. STORAGE ARCHITECTURE

Separate:

    ORIGINAL EVIDENCE
          │
          ├── source video
          ├── source image
          └── source media

from:

    DERIVED DATA
          │
          ├── face detections
          ├── crops
          ├── embeddings
          ├── tracks
          ├── candidates
          └── sightings

Original evidence remains authoritative.

Derived data can be regenerated if policy permits.

---

# 18. POSTGRESQL RESPONSIBILITY

PostgreSQL should own relational forensic metadata.

Examples:

    investigation
    reference
    processing_run
    detection
    track
    candidate
    sighting
    review
    model metadata
    policy metadata
    audit records

Use PostgreSQL for authoritative state.

---

# 19. PGVECTOR RESPONSIBILITY

pgvector should support efficient embedding retrieval when the workload requires vector search.

Conceptual:

    reference embedding
          ↓
    authorized vector query
          ↓
    candidate embeddings
          ↓
    similarity ranking

Vector search must respect:

- model compatibility
- dimension
- authorization
- index
- policy

Do not use pgvector as a substitute for relational provenance.

---

# 20. NEO4J RESPONSIBILITY

Neo4j should represent investigative relationships.

Example:

    (:FaceSighting)
         |
         | FROM_EVIDENCE
         ▼
    (:Evidence)

    (:FaceSighting)
         |
         | OBSERVED_AT
         ▼
    (:Location)

    (:FaceSighting)
         |
         | OCCURRED_AT
         ▼
    (:EventTime)

The relational store remains authoritative for detailed forensic records.

---

# 21. GRAPH PROJECTION

Do not make the face worker write arbitrary graph structures directly.

Preferred flow:

    forensic domain record
            ↓
      graph projection
            ↓
          Neo4j

This keeps graph representation aligned with domain semantics.

---

# 22. AUTHORIZATION ARCHITECTURE

Authorization path:

    user
      ↓
    authenticated identity
      ↓
    role
      ↓
    case access
      ↓
    evidence access
      ↓
    face investigation access
      ↓
    operation

Every sensitive operation must pass through this model.

---

# 23. CROSS-CASE SEARCH ARCHITECTURE

Default:

    Case A
      ↓
    Face Search
      ↓
    Case A embeddings only

Privileged:

    Explicit cross-case permission
      ↓
    Authorized scope
      ↓
    Search index
      ↓
    Filtered result
      ↓
    Audit

Do not implement global search as the default.

---

# 24. SECURITY BOUNDARY

Sensitive areas:

    reference images
    source frames
    face crops
    embeddings
    candidate results
    investigation metadata
    review records

These should remain inside trusted application boundaries.

The browser should receive only the data required for the current UI.

---

# 25. NETWORK BOUNDARY

Preferred production topology:

    Internet
       ↓
    Load Balancer
       ↓
    API / WebSocket
       ↓
    Private service network
       ├── workflow
       ├── workers
       ├── inference
       ├── PostgreSQL
       ├── Redis
       ├── pgvector
       ├── Neo4j
       └── object storage

Databases and GPU workers should not be directly public.

---

# 26. INFERENCE ARCHITECTURE

Face inference should be isolated from general application compute.

Conceptual:

    FastAPI
       │
       │ job
       ▼
    Face Worker
       │
       ├── InsightFace
       ├── ONNX Runtime
       └── GPU/CPU

A worker should load its model once and process multiple jobs.

---

# 27. GPU ARCHITECTURE

Where NVIDIA GPU acceleration is available:

    ONNX Runtime
         ↓
    CUDA EP

or, after validated optimization:

    ONNX Runtime
         ↓
    TensorRT EP
         ↓
    CUDA

ONNX Runtime supports multiple execution providers and uses provider priority/fallback semantics. citeturn981516search0

The TensorRT execution provider can improve inference performance on supported NVIDIA hardware, while retaining CUDA as a fallback for unsupported subgraphs. citeturn981516search1

Do not introduce TensorRT before measuring whether it improves CrimeKit's actual workload.

---

# 28. CPU FALLBACK

The model service may support:

    GPU
     ↓
    CPU fallback

only when explicitly configured.

The processing run must record which provider actually executed.

Example:

    execution_provider = CUDAExecutionProvider

or:

    execution_provider = CPUExecutionProvider

Do not hide fallback behavior.

---

# 29. MODEL PACKAGE ARCHITECTURE

The exact approved model artifact should be treated as a deployable dependency.

Store metadata such as:

    provider
    model_id
    model_version
    artifact_version
    embedding_dimension
    detector_version
    runtime_version

Current InsightFace server documentation describes local model package installation and verification and lists `buffalo_l` as a package containing detector and recognition ONNX artifacts. citeturn981516search8

InsightFace's current repository also states that the repository code is MIT-licensed while pretrained model licensing has separate conditions and directs users to contact InsightFace regarding licensing for open-source recognition models such as `buffalo_l`. citeturn981516search4

Therefore model approval is an architectural/deployment concern, not merely a Python dependency decision.

---

# 30. MODEL VERSION ARCHITECTURE

A processing result should conceptually reference:

    Model Identity
        ↓
    Model Version
        ↓
    Preprocessing Version
        ↓
    Matching Policy Version
        ↓
    Processing Run

This makes historical output interpretable.

---

# 31. PREPROCESSING ARCHITECTURE

Keep preprocessing explicit:

    source image/frame
          ↓
    decode
          ↓
    face crop
          ↓
    alignment
          ↓
    normalization
          ↓
    embedding

The preprocessing pipeline is part of model compatibility.

Changing preprocessing can alter matching behavior.

Therefore it requires versioning where material.

---

# 32. VIDEO PROCESSING ARCHITECTURE

Video worker should operate as a streaming pipeline:

    decoder
       ↓
    bounded frame buffer
       ↓
    sampler
       ↓
    detector
       ↓
    tracker
       ↓
    quality
       ↓
    recognizer
       ↓
    matching

Do not load long videos completely into memory.

---

# 33. BACKPRESSURE

When the downstream inference stage cannot keep up:

    decoder
       ↓
    bounded queue
       ↓
    controlled processing

Do not permit unlimited frame accumulation.

The system must expose queue pressure to operators.

---

# 34. CONCURRENCY

Concurrency should be controlled independently for:

    video decoding
    GPU inference
    vector search
    persistence
    event publication

Do not assume:

    more threads = more throughput

Measure the workload.

---

# 35. BATCHING

Where model/runtime behavior supports batching, evaluate:

    multiple eligible face crops
        ↓
    one inference batch

Potential benefit:

- improved GPU utilization
- reduced invocation overhead

But batching must not break:

- source mapping
- frame IDs
- timestamps
- provenance
- ordering semantics

---

# 36. FRAME SAMPLING

Sampling is a performance policy.

Architecture should allow:

    configured sampling
    adaptive sampling
    source-specific sampling

but all behavior must remain observable and reproducible enough for the forensic workflow.

---

# 37. TRACKING ARCHITECTURE

Tracking should operate on:

    frame detections

and output:

    track state

A tracker must not directly change the candidate identity record.

Architecture:

    Detector
       ↓
    Tracker
       ↓
    Track
       ↓
    Recognition

---

# 38. QUALITY GATE

Recognition pipeline:

    Detection
       ↓
    Quality Gate
       ↓
      / \
   poor good
    │    │
 reject  embedding
```

Quality rules must be configurable and versioned.

---

# 39. MATCHING ARCHITECTURE

Candidate matching:

    reference embedding
            │
            ▼
      candidate retrieval
            │
            ▼
       similarity
            │
            ▼
       quality context
            │
            ▼
       track context
            │
            ▼
     matching policy
            │
            ▼
       candidate result

Do not collapse all signals into an unexplained scalar.

---

# 40. CANDIDATE MODEL

A candidate should conceptually contain:

    candidate_id
    investigation_id
    source
    detection/track
    similarity
    quality
    policy_version
    model_version
    status
    created_at

The candidate is a hypothesis generated by computation.

---

# 41. REVIEW ARCHITECTURE

    Candidate
       ↓
    Investigator
       ↓
    Review
      / | \
     /  |  \
  accept reject further-review

The review record must be auditable.

Do not overwrite historical review decisions without preserving the audit trail.

---

# 42. TIMELINE INTEGRATION

After a valid sighting exists:

    FaceSighting
         ↓
    Timeline Event
         ↓
    Investigator Timeline

Timeline should expose:

- source
- timestamp
- location if known
- evidence
- sighting
- review state

The timeline should not invent times from processing timestamps.

---

# 43. GRAPH INTEGRATION

After persistence:

    FaceSighting
         ↓
    Graph Projection
         ↓
    Neo4j

Graph nodes/edges should not contain unsupported assertions.

A face candidate should not automatically become a criminal/person-of-interest node without a separate authorized domain relationship.

---

# 44. REPORTING INTEGRATION

Reports may include:

    reference investigation
    candidate sightings
    evidence sources
    timestamps
    model metadata
    policy metadata
    investigator review

Reports should preserve the distinction between machine-generated observation and human-reviewed conclusion.

---

# 45. CACHING

Cache only non-sensitive or appropriately protected data where justified.

Never use an unprotected shared cache for biometric vectors.

Any cache must define:

- scope
- TTL
- invalidation
- authorization

Do not cache sensitive results globally.

---

# 46. OBJECT STORAGE

Original media should remain in the existing evidence storage system.

Derived artifacts may include:

    source-frame snapshot
    annotated frame
    face crop

Only create derived files when they provide operational/forensic value.

Do not generate millions of unnecessary image files.

---

# 47. DERIVED ARTIFACT POLICY

Every derived artifact should have:

    source_artifact_id
    processing_run_id
    artifact_type
    created_at

This enables provenance.

---

# 48. AUDIT ARCHITECTURE

Audit path:

    Sensitive command
         ↓
    Authorization
         ↓
    Domain action
         ↓
    Audit record

Examples:

    reference uploaded
    investigation started
    cross-case search
    candidate viewed
    source frame opened
    review changed
    export created

---

# 49. OBSERVABILITY ARCHITECTURE

Three layers:

## Application metrics

    jobs
    candidates
    sightings
    failures

## Infrastructure metrics

    CPU
    GPU
    memory
    queues
    database

## Forensic processing metrics

    frames
    detections
    embeddings
    processing time

Do not expose sensitive biometric values in metrics.

---

# 50. LOGGING ARCHITECTURE

Use structured logging.

Correlation identifiers:

    request_id
    case_id
    investigation_id
    job_id
    processing_run_id
    evidence_id

Never log:

    raw embedding vectors
    credentials
    private keys
    unrestricted source imagery

---

# 51. JOB CORRELATION

A processing operation should be traceable through:

    request_id
       ↓
    investigation_id
       ↓
    job_id
       ↓
    processing_run_id
       ↓
    evidence_id
       ↓
    detections
       ↓
    sightings

This makes production troubleshooting and forensic auditing possible.

---

# 52. HEALTH MODEL

Face inference workers should expose:

    STARTING
    READY
    DEGRADED
    NOT_READY

Readiness requires:

- runtime initialized
- model loaded
- smoke inference successful
- required dependencies available

---

# 53. DISASTER RECOVERY ARCHITECTURE

The failure of face intelligence must not destroy original evidence.

Therefore:

    Original evidence
          ↓
    independent storage protection

while:

    Face intelligence
          ↓
    derived processing layer

Derived results should be reconstructible where policy permits.

---

# 54. REPROCESSING ARCHITECTURE

Reprocessing must create a new processing run.

Do not overwrite the historical run.

Example:

    RUN-001
      model v1
      policy v1

    RUN-002
      model v2
      policy v2

Both remain attributable.

---

# 55. MODEL MIGRATION ARCHITECTURE

When changing model:

    Candidate Model
          ↓
    Offline Evaluation
          ↓
    Regression
          ↓
    Performance
          ↓
    Licensing
          ↓
    Approval
          ↓
    New Model Version
          ↓
    New Processing Runs

Do not silently regenerate old results.

---

# 56. SECURITY ZONES

Recommended conceptual zones:

    PUBLIC
      ↓
    API
      ↓
    PRIVATE APPLICATION NETWORK
      ↓
    WORKFLOW / WORKERS
      ↓
    DATA NETWORK
      ├── PostgreSQL
      ├── pgvector
      ├── Neo4j
      └── Object Storage

Inference nodes should not be unnecessarily exposed.

---

# 57. FRONTEND DATA BOUNDARY

The browser should receive only data required for:

    visualization
    investigator action
    verification

Example response:

    candidate_id
    source
    timestamp
    similarity
    quality
    status
    artifact reference

Avoid sending:

    raw embedding
    internal credentials
    unrestricted object-storage credentials

---

# 58. RECONNECT ARCHITECTURE

If WebSocket disconnects:

    Browser
       ↓
    reconnect
       ↓
    GET investigation state
       ↓
    obtain missed authoritative status
       ↓
    resume live stream

The database/domain state is authoritative.

---

# 59. MULTI-CAMERA ARCHITECTURE

Each source has its own:

    decoder
    track namespace
    processing run

Example:

    CCTV-01
      TRACK-001

    CCTV-02
      TRACK-001

These are different track namespaces.

Higher-level candidate correlation occurs through sightings.

---

# 60. MULTI-VIDEO PARALLELISM

For multiple videos:

    Job
      ├── Source Worker 1
      ├── Source Worker 2
      └── Source Worker 3

then:

    all source sightings
          ↓
    investigation aggregation

Each source remains independently traceable.

---

# 61. REAL-TIME CCTV ARCHITECTURE

For live streams:

    RTSP
      ↓
    Reconnecting Decoder
      ↓
    Bounded Buffer
      ↓
    Sampling
      ↓
    Detection
      ↓
    Tracking
      ↓
    Quality
      ↓
    Recognition
      ↓
    Matching
      ↓
    Sighting
      ↓
    Event

A stream disconnect should produce a source health event rather than silently terminating the investigation.

---

# 62. LIVE EVENT THROTTLING

Do not publish unlimited events.

Prefer:

    candidate created
    sighting updated
    progress changed materially

rather than:

    one event per processed frame

This keeps the realtime channel useful.

---

# 63. LATENCY BUDGET

Track separate stages:

    decode latency
    queue latency
    detection latency
    tracking latency
    embedding latency
    vector search latency
    persistence latency
    event latency

Then:

    total observed latency

This prevents false claims about "real time."

---

# 64. SCALING MODEL

Scale based on bottleneck.

If API is bottleneck:

    scale API workers

If decoding is bottleneck:

    scale video workers

If GPU inference is bottleneck:

    scale GPU workers

If vector search is bottleneck:

    optimize/index/search infrastructure

Do not simply scale the entire platform horizontally.

---

# 65. RESOURCE ISOLATION

Do not allow one huge video job to starve all other investigations.

Consider:

    per-job limits
    per-case limits
    worker concurrency limits
    queue priorities

The exact policy must be based on CrimeKit's operational needs.

---

# 66. FAIRNESS / SCHEDULING

If multiple investigations are running:

    Job A
    Job B
    Job C

the scheduler should prevent one investigation from consuming all inference capacity unless the project explicitly prioritizes it.

Do not implement unfair global FIFO blindly if operational requirements differ.

---

# 67. SECURITY OF MODEL SERVICE

The face inference service should not be publicly exposed.

Preferred:

    FastAPI
       ↓
    internal inference RPC/service boundary

Access should require internal service authorization where the infrastructure supports it.

---

# 68. DATA MODEL RELATIONSHIP VIEW

Conceptual domain model:

    Case
      │
      └── FaceInvestigation
             │
             ├── FaceReference
             │       └── FaceEmbedding
             │
             ├── FaceSearchJob
             │       └── ProcessingRun
             │
             ├── FaceDetection
             │
             ├── FaceTrack
             │
             ├── FaceCandidate
             │
             ├── FaceSighting
             │
             └── FaceReview

---

# 69. PROCESSING RUN MODEL

A ProcessingRun groups the actual execution context.

It should identify:

    job
    evidence
    model
    policy
    preprocessing
    runtime
    start
    end
    execution provider
    worker
    outcome

This is the main reproducibility boundary.

---

# 70. CONFIGURATION ARCHITECTURE

Configuration should be layered:

    code defaults
       ↓
    environment configuration
       ↓
    deployment configuration
       ↓
    approved matching/model policy

Secrets must be provided through the project's secret-management approach.

---

# 71. API / DOMAIN SEPARATION

Routes should delegate:

    Router
      ↓
    Application Service
      ↓
    Domain
      ↓
    Repository / Infrastructure

Do not put all face logic inside route functions.

---

# 72. REPOSITORY / INFRASTRUCTURE SEPARATION

Database-specific logic should stay behind the existing CrimeKit persistence conventions.

The domain should not contain raw:

    SQL
    Cypher
    Redis commands

unless the current project architecture intentionally allows it.

---

# 73. GRAPH / VECTOR DUAL-WRITE RULE

Do not assume PostgreSQL + pgvector + Neo4j can be atomically committed in one ordinary database transaction.

Treat graph/vector projection as a controlled distributed process.

Preferred pattern:

    authoritative relational record
             ↓
    projection event
             ↓
    vector/graph projection
             ↓
    projection status

This allows recovery from partial downstream failure.

---

# 74. EVENTUAL CONSISTENCY

The UI must tolerate a short period where:

    PostgreSQL = updated
    Neo4j = still processing

or:

    relational record = complete
    graph projection = pending

The UI should represent projection status where material.

Do not claim graph consistency before it exists.

---

# 75. IDEMPOTENT PROJECTIONS

Graph/vector projection operations should be safe to retry.

Use stable domain identifiers.

Do not create duplicated graph nodes every time a worker retries.

---

# 76. VERSIONED EVENT SCHEMA

Every event should have:

    event_type
    event_version
    event_id
    occurred_at
    aggregate_id

Consumers should be able to evolve without silently breaking older producers.

---

# 77. API VERSIONING

Use the existing CrimeKit API versioning convention.

Do not introduce a second API versioning style specifically for face intelligence.

---

# 78. SECURITY OF SOURCE-FRAME VIEWER

When viewing a source frame:

    authorized request
       ↓
    evidence access validation
       ↓
    controlled artifact access
       ↓
    frame response

Do not trust a candidate ID alone to grant source evidence access.

---

# 79. REPORT GENERATION ARCHITECTURE

Reports should consume stored domain records.

Do not regenerate the face analysis simply to create a report.

Report path:

    persisted investigation
          ↓
    persisted sightings
          ↓
    provenance
          ↓
    report generator

This maintains reproducibility.

---

# 80. AUDITABLE EXPORT

Export operations must record:

    exporter
    case
    investigation
    timestamp
    export type
    scope

The export should not silently include unauthorized cases or biometric data.

---

# 81. BACKUP

Back up according to the platform's existing strategy:

    PostgreSQL
    evidence/object storage
    critical configuration
    review/audit information

Embeddings should be backed up or reproducible according to retention/security policy.

Do not create an independent ungoverned backup path for face data.

---

# 82. DELETION

Deletion must respect dependencies.

Conceptual:

    Delete/expire investigation
       ↓
    derived face records
       ↓
    embeddings
       ↓
    derived crops
       ↓
    index cleanup
       ↓
    graph projection cleanup
       ↓
    audit/retention policy

Never delete original evidence solely because a derived face record was deleted unless the primary evidence policy says so.

---

# 83. RETENTION

Retention decisions should be explicit for:

    source reference
    derived crops
    embeddings
    detection records
    tracks
    sightings
    audit records

Do not assume all derived data has the same retention period.

---

# 84. PERFORMANCE TEST ENVIRONMENT

Performance numbers must identify:

    CPU
    GPU
    RAM
    OS
    Python/runtime
    ONNX Runtime version
    model version
    video properties

Without this context, FPS numbers are incomplete.

---

# 85. BASELINE SCENARIO

Create at least one repeatable benchmark:

    video duration
    resolution
    FPS
    average faces/frame
    sample rate
    hardware
    model

Measure:

    processing duration
    throughput
    latency
    peak memory

---

# 86. CAPACITY PLANNING

Do not make unsupported claims such as:

    "supports 100 cameras"

unless measured.

Instead document:

    tested:
    X cameras / streams

    observed:
    Y FPS

    bottleneck:
    Z

---

# 87. FAILURE MODEL

Possible failure domains:

    API
    workflow
    decoder
    inference
    GPU
    database
    vector
    graph
    events
    UI

Each domain needs explicit recovery behavior.

---

# 88. DEGRADED MODES

Examples:

    Neo4j unavailable
      ↓
    preserve relational forensic result
      ↓
    mark graph projection pending

    WebSocket unavailable
      ↓
    continue processing
      ↓
    UI recovers through API

    GPU unavailable
      ↓
    approved CPU fallback
      OR
    pause/fail according to policy

---

# 89. NO SILENT DATA LOSS

If any component drops observations intentionally:

    record policy
    expose processing statistics
    make scope understandable

Never silently discard evidence-derived observations to improve performance numbers.

---

# 90. CONFIGURATION CHANGE CONTROL

Changes to:

    model
    preprocessing
    sample rate
    quality policy
    matching policy
    worker concurrency

must be traceable.

Where the change materially affects forensic output, create a new processing/model/policy version.

---

# 91. SECURITY REVIEW ARCHITECTURE

Security review should cover:

    authentication
    authorization
    object access
    biometric protection
    API abuse
    WebSocket authorization
    cross-case search
    data export
    storage access
    logging
    secrets

Do not treat InsightFace itself as a security boundary.

---

# 92. DEPENDENCY SECURITY

All dependencies must be:

- pinned according to project policy
- scanned
- compatible with deployment
- documented where security-critical

Do not install arbitrary model/runtime packages directly on production hosts.

---

# 93. SUPPLY-CHAIN RULE

Verify:

    Python package
    model artifact
    container image
    runtime

before deployment.

Model artifacts are part of the software supply chain.

---

# 94. OBSERVABILITY CORRELATION

A single investigation should be traceable through logs/metrics using:

    investigation_id

Then:

    investigation_id
       ↓
    job_id
       ↓
    worker logs
       ↓
    processing_run
       ↓
    candidate
       ↓
    sighting

This should be possible without logging biometric vectors.

---

# 95. OPERATIONAL DASHBOARD

Operations should be able to observe:

    active jobs
    queued jobs
    failed jobs
    worker health
    GPU utilization
    processing throughput
    error rates
    event lag
    database health

Do not expose investigator-sensitive content in the operations dashboard unless explicitly needed.

---

# 96. UI ARCHITECTURE INTEGRATION

The frontend feature should consume domain endpoints and event streams.

Conceptually:

    FaceTracePage
       │
       ├── ReferenceState
       ├── EvidenceState
       ├── JobState
       ├── FindingsState
       ├── TimelineState
       └── ReviewState

The exact state management approach must follow the existing frontend architecture.

---

# 97. COMPONENT RESPONSIBILITY

Avoid one giant React component.

Prefer separation:

    ReferenceUpload
    EvidenceSelector
    InvestigationHeader
    ProcessingStatus
    LiveFindings
    VideoViewer
    CandidateDetail
    ProvenancePanel
    Timeline
    ReviewPanel

Only create components that correspond to real responsibilities.

---

# 98. UI DATA FLOW

    API initial state
          ↓
    React state/store
          ↓
    WebSocket updates
          ↓
    reducer/state transition
          ↓
    UI

Do not mutate business objects directly in arbitrary components.

---

# 99. ACCESSIBLE STATE MODEL

The UI state should map cleanly to backend state.

Backend:

    PROCESSING

Frontend:

    Processing

Backend:

    COMPLETED

Frontend:

    Completed

No ad-hoc frontend-only states that hide backend failures.

---

# 100. EMPTY / NO MATCH ARCHITECTURE

No matches is a valid result.

It is not the same as:

    failure

Therefore:

    COMPLETED + NO_MATCHES

must be distinguishable from:

    FAILED

---

# 101. PARTIAL RESULT ARCHITECTURE

If a multi-source search finishes only partially:

    CCTV-01 = complete
    CCTV-02 = failed
    CCTV-03 = processing

the investigation must reflect partial state.

Do not display:

    "Search complete"

without qualification.

---

# 102. CANCELLED SEARCH ARCHITECTURE

A cancelled job should expose:

    cancellation status
    completed sources
    unprocessed sources
    persisted observations

Do not erase valid previous processing.

---

# 103. CONCURRENCY SAFETY

The system must safely handle:

    investigator clicks Start twice

or:

    browser retries request

without creating duplicate investigations/jobs unintentionally.

Use API idempotency where appropriate.

---

# 104. API IDEMPOTENCY

Operations such as job creation should support a safe idempotency mechanism when duplicate client requests are possible.

Do not create two identical jobs because the browser retried after a timeout.

---

# 105. STATE MACHINE AUTHORITY

Only the application/workflow layer should be allowed to transition job state.

Workers report outcomes.

Random frontend requests must not arbitrarily set:

    COMPLETED
    FAILED

without domain validation.

---

# 106. DATA CONTRACT STABILITY

Internal domain models and API response schemas must remain stable enough that frontend and worker components can evolve independently.

Use explicit DTO/schema boundaries.

---

# 107. SECURITY OF INTERNAL EVENTS

Internal event payloads may contain sensitive IDs.

Treat event infrastructure as a trusted but secured internal system.

Do not assume that "internal" means "publicly readable."

---

# 108. MODEL SERVICE API

If inference is exposed as a service boundary, define explicit operations conceptually:

    health
    readiness
    detect
    embed
    batch_embed

Do not expose arbitrary model execution.

---

# 109. INFERENCE BOUNDARY SECURITY

Model service should validate:

- request schema
- image limits
- batch limits
- caller authorization
- resource limits

Do not permit unbounded arbitrary tensors or files.

---

# 110. RESOURCE LIMITS

Protect against:

- enormous images
- huge batches
- extremely long videos
- excessive simultaneous jobs
- maliciously crafted media

Use configurable limits.

---

# 111. MEDIA SECURITY

Uploaded images/videos should be treated as untrusted input.

Validate and safely decode media.

Avoid executing or interpreting uploaded files as code.

Use appropriate sandbox/container isolation where required by the existing forensic architecture.

---

# 112. FILE PATH SAFETY

Never construct local filesystem paths directly from investigator-supplied names without safe normalization/validation.

Avoid path traversal.

---

# 113. VIDEO PROCESSING ISOLATION

Where appropriate, run media decoding/inference in an isolated worker/container so malformed media cannot compromise the API service.

Follow the existing CrimeKit security architecture.

---

# 114. MODEL RESOURCE ISOLATION

A model worker should have controlled:

    CPU
    GPU memory
    host memory
    process count
    batch size

Do not allow one request to consume all resources.

---

# 115. DATABASE QUERY ARCHITECTURE

Candidate retrieval must use indexed, parameterized queries.

Do not build SQL/Cypher from string concatenation.

Do not allow investigator input to become executable database syntax.

---

# 116. GRAPH QUERY ARCHITECTURE

Use parameterized Cypher through the approved Neo4j driver/integration.

Neo4j provides an official Python driver for Python applications. citeturn981516search6

Do not expose direct arbitrary Cypher execution to the frontend.

---

# 117. MIGRATION ARCHITECTURE

Schema additions should be introduced through the existing migration framework.

Do not modify production tables manually.

Migrations must be:

- repeatable
- reviewable
- tested
- reversible where the project policy requires

---

# 118. INDEX ARCHITECTURE

Likely index domains:

    case_id
    investigation_id
    evidence_id
    job_id
    processing_run_id
    timestamp
    track_id
    review_status

Vector indexes should be added only after workload analysis.

---

# 119. TEMPORAL INDEXING

Because investigation results are time-oriented, optimize for queries such as:

    sightings by case
    sightings by evidence
    sightings by time window
    tracks by video
    candidates by investigation

---

# 120. PROVENANCE QUERY PATH

The most important read path is:

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
    Evidence

Design persistence so this path is efficient.

---

# 121. PROVENANCE PERFORMANCE

Do not solve provenance by joining dozens of tables blindly for every UI request.

Use appropriate relational modeling, indexes, and controlled read models where needed.

Do not denormalize until profiling justifies it.

---

# 122. SECURITY AND PERFORMANCE TRADE-OFF

Never remove authorization filtering merely to improve vector-search latency.

Never remove provenance merely to improve write throughput.

Security and forensic integrity are higher priority than raw performance.

---

# 123. REAL-TIME PERFORMANCE TRADE-OFF

The UI does not need every computational detail.

Publish meaningful events.

Store detailed processing metrics separately.

This keeps realtime communication efficient without sacrificing forensic records.

---

# 124. REFERENCE IMAGE MULTIPLE-FACE HANDLING

If a reference contains multiple faces:

    API
      ↓
    detection result
      ↓
    explicit selection or rejection
      ↓
    continue

Do not silently use the first detected face.

---

# 125. MULTIPLE-REFERENCE EXTENSION

The architecture may later support multiple reference images:

    Reference A
    Reference B
    Reference C
          ↓
    reference gallery
          ↓
    search video

The initial implementation should not require this complexity unless explicitly needed.

The data model should not prevent future extension.

---

# 126. MULTIPLE-VIDEO EXTENSION

Similarly:

    one reference
       ↓
    multiple videos

should reuse the same investigation.

Each source gets independent processing state.

---

# 127. SEARCH SCOPE MODEL

Possible scope:

    selected evidence
    selected videos
    entire case

Scope must be explicit in the investigation record.

---

# 128. CASE ISOLATION

Vector and graph queries must not accidentally cross cases.

Case ID should be a first-class domain constraint.

---

# 129. AUDIT OF SEARCH SCOPE

Every search should record:

    scope type
    evidence IDs
    case ID
    requester
    timestamp
    cross-case flag if applicable

---

# 130. SYSTEM OF RECORDS

Recommended responsibility:

    PostgreSQL
      = authoritative relational state

    pgvector
      = vector retrieval representation

    Neo4j
      = graph projection/relationship view

    Object Storage
      = evidence/media

    Event Bus
      = event delivery

No secondary store should silently become the authoritative source for the same domain state.

---

# 131. EVENTUAL GRAPH CONSISTENCY

If graph projection is delayed:

    PostgreSQL = authoritative
    Neo4j = pending projection

This state must be recoverable.

---

# 132. REPLAY ARCHITECTURE

If the event system supports replay, domain events may be replayed to rebuild projections.

Events must therefore contain sufficient stable identifiers.

Do not put ephemeral UI-only state in domain events.

---

# 133. FORENSIC REPRODUCIBILITY

A historical processing run should be explainable from:

    source evidence
    model version
    preprocessing version
    policy version
    configuration
    processing run
    output

This is one of the defining quality requirements of the subsystem.

---

# 134. REPRODUCIBILITY VS EXACT BYTE REPEATABILITY

The system should target reproducible processing context.

Do not claim bit-for-bit deterministic results unless the complete runtime and model behavior have been verified as deterministic.

---

# 135. QUALITY OF SOURCE EVIDENCE

The system should retain source quality metadata where it already exists in CrimeKit.

Do not assume every frame can provide high-quality identification.

---

# 136. INVESTIGATIVE CONTEXT

Face sightings should remain contextualized by:

    camera
    time
    location
    evidence
    other forensic artifacts

The face subsystem generates one evidence signal among many.

---

# 137. MULTI-MODAL INTEGRATION

Later integration can connect:

    Face Sighting
       +
    Device Artifact
       +
    Location
       +
    Communication
       +
    Timeline

through the existing investigation graph.

Face recognition should not become the sole source of investigative truth.

---

# 138. AI AGENT CONSUMPTION

AI investigator agents may query:

    FaceSightings
    Candidates
    Reviews
    Evidence
    Timeline

They must use stored structured results.

Do not allow AI agents to call low-level face inference as a replacement for the forensic workflow unless a separately approved use case exists.

---

# 139. EXPLANATION CONTRACT

If the system displays why a candidate was surfaced, it should be based on real stored values:

    similarity
    quality
    track duration
    observation count
    source evidence
    timestamp

Do not generate an LLM explanation that invents evidence.

---

# 140. INVESTIGATOR TRUST MODEL

The architecture should make it easy for an investigator to ask:

    "Show me the evidence."

The system should respond with:

    exact source
    exact time
    exact frame
    machine-generated candidate metadata
    review state

This is a primary design objective.

---

# 141. DEMO ARCHITECTURE

The SIH demo should use a controlled flow:

    Reference Image
          ↓
    One Video
          ↓
    Real Processing
          ↓
    Detection
          ↓
    Tracking
          ↓
    Matching
          ↓
    Candidate
          ↓
    Live UI
          ↓
    Source Frame
          ↓
    Provenance
          ↓
    Review

Only after this works reliably should the demo add multiple cameras.

---

# 142. PRODUCTION EVOLUTION PATH

Version 1:

    Image reference
    +
    MP4 search

Version 2:

    Multi-video
    +
    vector indexing
    +
    graph integration

Version 3:

    RTSP live streams
    +
    adaptive sampling
    +
    distributed GPU workers

Version 4:

    large-scale deployment
    +
    model optimization
    +
    advanced scheduling
    +
    multi-site operation

Do not build all versions simultaneously.

---

# 143. ARCHITECTURAL DECISION RECORDS

Any major architectural decision should be documented.

Examples:

    why a specific tracker was selected
    why pgvector is used
    why a specific sampling policy is used
    why a model runtime was selected
    why TensorRT was or was not adopted

Do not rely on tribal knowledge.

---

# 144. TECHNOLOGY SUBSTITUTION

The system should allow replacing:

    InsightFace

with another approved recognition provider without rewriting:

    case management
    provenance
    UI
    review
    reporting

This is achieved through the model adapter boundary.

---

# 145. TRACKER SUBSTITUTION

Likewise, replacing one tracker should affect:

    tracking implementation

not:

    database semantics
    review system
    evidence model

---

# 146. EVENT INFRASTRUCTURE SUBSTITUTION

The domain should publish logical events.

The transport may be:

    Redis Streams
    Kafka
    another approved event platform

depending on CrimeKit infrastructure.

Do not make business logic depend on one event transport.

---

# 147. STORAGE SUBSTITUTION

Evidence storage should remain behind existing CrimeKit storage abstractions.

Face intelligence should consume artifact references rather than embed storage implementation assumptions.

---

# 148. ARCHITECTURAL CODEOWNERS

The feature should have clear owners across:

    forensic
    backend
    frontend
    database
    security
    infrastructure

Actual ownership follows the team contribution model.

Do not manufacture ownership purely for documentation.

---

# 149. ARCHITECTURAL REVIEW CHECKLIST

Before implementation:

[ ] Existing evidence architecture inspected.

[ ] Existing video processing inspected.

[ ] Existing worker/workflow architecture inspected.

[ ] Existing database patterns inspected.

[ ] Existing pgvector implementation inspected.

[ ] Existing graph implementation inspected.

[ ] Existing event/WebSocket implementation inspected.

[ ] Existing authentication/RBAC inspected.

[ ] Existing frontend investigation workspace inspected.

[ ] Existing deployment model inspected.

[ ] Dependency overlap checked.

---

# 150. FINAL ARCHITECTURAL CONTRACT

CrimeKit Face Trace Investigator must preserve this separation:

                         USER
                          │
                          ▼
                       FRONTEND
                          │
                          ▼
                         API
                          │
                  AUTHORIZATION
                          │
                          ▼
                       WORKFLOW
                          │
               ┌──────────┴──────────┐
               ▼                     ▼
         VIDEO PROCESSING       REFERENCE PROCESSING
               │                     │
               ▼                     ▼
          DETECTION               DETECTION
               │                     │
               ▼                     ▼
           TRACKING               QUALITY
               │                     │
               ▼                     ▼
           QUALITY                EMBEDDING
               │                     │
               ▼                     │
           EMBEDDING ◄───────────────┘
               │
               ▼
            MATCHING
               │
               ▼
           SIGHTING
               │
        ┌──────┼──────┐
        ▼      ▼      ▼
       SQL  pgvector Neo4j
        │      │      │
        └──────┼──────┘
               ▼
             EVENTS
               │
               ▼
          WEBSOCKET/UI
               │
               ▼
        INVESTIGATOR REVIEW

The architecture must never collapse these boundaries merely to make
the implementation shorter.

The objective is not the largest architecture.

The objective is the smallest architecture that provides:

    strong forensic provenance
    controlled biometric processing
    reliable real-time behavior
    clear security boundaries
    scalable inference
    testable components
    replaceable model infrastructure
    maintainable CrimeKit integration
