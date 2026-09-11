# CrimeKit Face Trace Investigator — MASTER SPECIFICATION

**Document:** `MASTER_SPEC.md`  
**Subsystem:** Face Trace Investigator  
**Project:** CrimeKit  
**Status:** Authoritative implementation specification  
**Audience:** Backend, frontend, forensic, ML, security, infrastructure, QA, and DevOps engineers  
**Primary principle:** Evidence-first, asynchronous, provenance-preserving, human-reviewed

---

# 1. PURPOSE

CrimeKit Face Trace Investigator is a forensic investigation subsystem that allows an authorized investigator to:

1. Upload a reference face image.
2. Validate and analyze the reference image.
3. Generate a versioned face representation using an approved local face-recognition model.
4. Select one or more authorized image/video/CCTV evidence sources.
5. Search video evidence for candidate appearances of the reference face.
6. Detect and track faces across frames.
7. Generate candidate embeddings only for eligible observations.
8. Compare candidate embeddings against the reference representation.
9. Aggregate frame-level observations into track-level sightings.
10. Persist complete evidence provenance.
11. Publish processing and finding events in real time.
12. Present candidate findings to the investigator.
13. Allow explicit investigator review.
14. Integrate findings with CrimeKit timeline and relationship graph where appropriate.

The subsystem is an investigative candidate-generation and evidence-correlation capability.

It is **not** a system for automatically determining guilt, criminal responsibility, or legal identity.

---

# 2. PRODUCT INTENT

## 2.1 Investigator problem

Digital investigations may contain:

- CCTV recordings
- body-camera footage
- phone videos
- photographs
- extracted media
- multiple camera angles
- duplicate sightings
- incomplete or low-quality frames

Manually searching large video collections for one person is expensive and error-prone.

CrimeKit should reduce the mechanical search burden while keeping source evidence visible and auditable.

## 2.2 Core user experience

```text
Reference Image
    ↓
Reference Validation
    ↓
Reference Face Representation
    ↓
Select Evidence
    ↓
Start Face Trace Investigation
    ↓
Asynchronous Processing
    ↓
Live Processing Updates
    ↓
Candidate Sightings
    ↓
Source Frame Verification
    ↓
Investigator Review
    ↓
Timeline / Graph Integration
```

## 2.3 Product statement

> Upload one reference face and trace candidate appearances across authorized evidence while preserving the complete evidence trail.

---

# 3. SCOPE

## 3.1 In scope

- Reference-image upload
- Face detection
- Reference-face quality assessment
- Face alignment/preprocessing
- Face embedding generation
- Video decoding
- Frame sampling
- Face detection in frames
- Face quality assessment
- Face tracking
- Candidate similarity computation
- Candidate ranking
- Track-level sighting aggregation
- Multi-video investigation
- PostgreSQL persistence
- pgvector similarity search
- Neo4j integration
- Evidence provenance
- Audit logging
- Role/case authorization
- Real-time event delivery
- Investigator review
- Processing cancellation
- Failure recovery
- Metrics and observability
- Performance/load testing
- Model/configuration versioning

## 3.2 Out of scope for the first implementation

Do not introduce these unless separately approved:

- Automatic criminal identification
- Automatic guilt inference
- Unbounded cross-case biometric search
- Unreviewed automatic identity merging
- Training a new face-recognition model
- Model fine-tuning using live CrimeKit evidence
- Cloud-hosted per-frame recognition as the production inference path
- Browser-side biometric inference
- Automatic legal conclusions
- Facial attribute inference unrelated to the investigation
- Emotion analysis
- Race/religion/gender inference
- Behavioral profiling based on face alone

---

# 4. NON-NEGOTIABLE PRINCIPLES

## Rule 1 — Evidence remains immutable

Original evidence must never be modified by the face-intelligence subsystem.

Derived artifacts must reference the original evidence.

## Rule 2 — Every result is traceable

Every candidate result must be traceable to:

- case
- evidence
- artifact
- source video/image
- frame
- timestamp
- bounding box
- processing run
- model identity/version
- preprocessing version
- matching policy version
- review status

## Rule 3 — Human review remains explicit

The system may generate candidate matches.

The system must not silently convert a candidate into an authoritative identity claim.

## Rule 4 — Case scope is mandatory

Every investigation and every face-analysis job must belong to an authorized case context.

## Rule 5 — No hidden thresholds

Similarity thresholds must be explicit, versioned, and evaluated.

Never hard-code an unexplained production threshold such as:

```python
if similarity > 0.55:
```

without an approved evaluation record.

## Rule 6 — No fake confidence

The system must distinguish:

- model similarity
- detection confidence
- quality score
- track consistency
- candidate rank
- investigator review state

Do not combine them into one artificial “AI confidence” number unless a documented scoring model exists.

## Rule 7 — Forensic processing is separate from AI reasoning

Face detection, tracking, embedding, and matching belong to the forensic/computational pipeline.

Higher-level AI reasoning may consume the resulting structured evidence, but must not replace deterministic provenance or forensic processing.

## Rule 8 — Production inference must be local/self-hosted

The production architecture must not depend on a hosted per-image evaluation endpoint.

The project-provided InsightFace evaluation document explicitly describes its hosted endpoint as evaluation-only and describes long-term inference using locally deployed model files. It also describes an evaluation window and rate limits. [Source: project-provided InsightFace document]

## Rule 9 — Model licensing must be verified

The exact model package used for production must have a verified legal/licensing basis.

InsightFace's current repository distinguishes code licensing from pretrained model licensing. Do not assume code licensing automatically grants unrestricted production rights to every pretrained model. [Source: current InsightFace repository]

## Rule 10 — No biometric data leakage

Embeddings, reference images, face crops, and matching results are sensitive investigative data and must follow CrimeKit authorization, retention, and audit requirements.

## Rule 11 — No processing in ordinary HTTP request lifetimes

Long-running video analysis must execute asynchronously through CrimeKit's workflow/worker architecture.

## Rule 12 — Reuse CrimeKit infrastructure

Before creating any new queue, storage abstraction, event bus, authentication layer, graph abstraction, or database layer, inspect existing CrimeKit implementations.

Do not create competing infrastructure.

---

# 5. ARCHITECTURAL POSITIONING

The Face Trace Investigator belongs primarily under the forensic processing boundary.

Preferred conceptual placement:

```text
forensic/
    face-intelligence/
```

It integrates with:

```text
Evidence
   ↓
Forensic Processing
   ↓
Face Intelligence
   ↓
Structured Face Evidence
   ↓
Timeline / Graph / Search
   ↓
AI Investigation
```

The face subsystem is not itself an AI agent.

---

# 6. HIGH-LEVEL ARCHITECTURE

```text
                    React Investigator Workspace
                                  │
                           REST + WebSocket
                                  │
                             FastAPI API
                                  │
                         Authorization / Case ACL
                                  │
                            Job Creation
                                  │
                         Workflow / Queue Layer
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ↓                   ↓                   ↓
      Reference Worker      Video Worker Pool   Search/Match Worker
              │                   │                   │
              ↓                   ↓                   ↓
        Face Detection       Decode/Sampling    Similarity Engine
              │                   │                   │
              ↓                   ↓                   ↓
         Quality Check       Face Detection       pgvector
              │                   │                   │
              ↓                   ↓                   ↓
         Embedding              Tracking         Candidate Rank
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ↓
                           Sighting Aggregator
                                  │
                 ┌────────────────┼────────────────┐
                 ↓                ↓                ↓
             PostgreSQL         pgvector          Neo4j
                 │                │                │
                 └────────────────┼────────────────┘
                                  ↓
                           Event Publication
                                  │
                           Redis/Event Bus
                                  │
                              WebSocket
                                  │
                                  ↓
                          Live Investigator UI
```

Original evidence remains in CrimeKit's existing evidence/object-storage system.

---

# 7. COMPONENT RESPONSIBILITIES

## 7.1 Frontend

Responsible for:

- upload UX
- evidence selection
- starting/cancelling investigations
- processing state
- live findings
- timeline visualization
- source-frame viewing
- provenance display
- review actions

Frontend must not:

- run authoritative matching logic
- directly access PostgreSQL
- directly access pgvector
- directly access Neo4j
- contain security decisions
- contain model inference code

## 7.2 API layer

Responsible for:

- authentication
- case authorization
- input validation
- job creation
- status endpoints
- review endpoints
- controlled source-artifact access

API routes must remain lightweight.

## 7.3 Workflow/queue layer

Responsible for:

- durable job orchestration
- retries
- cancellation
- timeouts
- worker coordination
- progress reporting

Use CrimeKit's existing workflow architecture when available.

## 7.4 Face workers

Responsible for:

- model loading
- face detection
- face quality assessment
- alignment
- embedding generation
- controlled inference execution

## 7.5 Video processing workers

Responsible for:

- decoding
- frame sampling
- frame ordering
- frame timestamps
- worker backpressure
- track input generation

## 7.6 Matching layer

Responsible for:

- similarity calculation
- nearest-neighbor lookup
- candidate ranking
- aggregation inputs

## 7.7 Sighting aggregation

Responsible for:

- converting repeated frame observations into track/sighting records
- deduplicating event noise
- determining start/end time windows
- preserving all underlying observations

## 7.8 Persistence

PostgreSQL:

- case linkage
- job state
- processing metadata
- face detections
- tracks
- sightings
- candidate records
- review state
- audit data

pgvector:

- face embeddings and nearest-neighbor retrieval where approved

Neo4j:

- evidence/entity relationships
- observation/candidate relationships
- cross-artifact investigation connections

Object storage:

- original evidence
- approved derived media artifacts
- source-frame references as appropriate

---

# 8. MODEL ARCHITECTURE

## 8.1 Model roles

Do not treat “InsightFace” as one monolithic function.

Separate:

- detection
- alignment/preprocessing
- recognition/embedding
- matching
- tracking

Each role must be versionable independently.

## 8.2 InsightFace integration

The first implementation may use an approved local InsightFace model package where licensing permits the intended use.

The model runtime must be isolated behind a CrimeKit interface.

Conceptual interfaces:

```text
FaceDetector
FaceEmbedder
FaceQualityEvaluator
FaceTracker
FaceMatcher
```

Do not allow the rest of the application to depend directly on low-level InsightFace objects.

## 8.3 Model adapter

Conceptual interface:

```text
FaceModelProvider
```

Responsibilities:

- load model
- report model identity
- expose detector
- expose embedding function
- expose runtime information
- validate model readiness

## 8.4 Runtime

ONNX Runtime is the preferred low-level inference runtime when the selected model is distributed as ONNX and the deployment environment supports it.

Execution provider selection must be explicit.

A GPU worker may prefer:

```text
CUDAExecutionProvider
CPUExecutionProvider
```

TensorRT may be introduced only after performance validation and compatible deployment packaging.

Current ONNX Runtime documentation describes execution-provider priority and supports CPU, CUDA, and TensorRT paths. [Source: current ONNX Runtime documentation]

## 8.5 Startup model loading

Models must be loaded once per worker process or approved inference lifecycle.

Do not load and unload the model for each frame or request.

---

# 9. REFERENCE IMAGE PIPELINE

```text
Upload
  ↓
MIME/type validation
  ↓
Security validation
  ↓
Decode
  ↓
Face detection
  ↓
Exactly one intended reference face
  ↓
Quality assessment
  ↓
Alignment/preprocessing
  ↓
Embedding
  ↓
Validation
  ↓
Persist reference metadata
  ↓
Persist protected embedding
```

## 9.1 Reference image requirements

The system should reject or flag:

- zero detected faces
- ambiguous multiple-face image
- extremely small face
- severe blur
- severe occlusion
- extreme pose
- unusable lighting
- corrupted image

Do not silently choose the first face from a multi-person image.

The user must explicitly resolve ambiguity.

## 9.2 Reference quality

Produce a structured result:

```text
PASS
REVIEW
REJECT
```

with machine-readable reasons.

Example:

```text
face_count = 1
detection_score = 0.98
sharpness = acceptable
pose = acceptable
occlusion = low
quality_state = PASS
```

## 9.3 Reference artifact

The reference image must remain linked to the case/evidence/artifact system according to CrimeKit policy.

Do not create an untraceable “face upload.”

---

# 10. VIDEO PIPELINE

```text
Evidence
  ↓
Authorization
  ↓
Decode
  ↓
Timestamp normalization
  ↓
Frame sampling
  ↓
Face detection
  ↓
Quality filtering
  ↓
Tracking
  ↓
Embedding
  ↓
Similarity
  ↓
Candidate observations
  ↓
Track aggregation
  ↓
Sightings
  ↓
Persistence
  ↓
Events
```

## 10.1 Do not infer on every frame by default

If a video is 25 FPS, do not automatically run expensive recognition at 25 recognition operations/second per stream.

Use controlled sampling and tracking.

Sampling policy must be configurable and measurable.

Example starting policy:

```text
decode_rate = source_fps
recognition_sample_rate = configurable
tracking_rate = configurable
```

Exact values must be benchmarked on CrimeKit hardware.

## 10.2 Adaptive processing

A later optimization may allow:

```text
low activity
   ↓
lower sampling

face/track activity
   ↓
temporarily increase sampling
```

This optimization must preserve timestamp correctness and reproducibility.

## 10.3 Timestamp integrity

Every processed frame must retain:

- source video ID
- frame number
- presentation timestamp
- processing timestamp
- source timezone/metadata when available

Do not use processing wall-clock time as the source-event time.

---

# 11. FACE DETECTION

Each detected face must produce at minimum:

```text
detection_id
evidence_id
artifact_id
frame_number
timestamp
bbox
detector_score
processing_run_id
```

For multi-face frames:

```text
Frame
  ├── Detection A
  ├── Detection B
  └── Detection C
```

Never flatten multiple faces into one record.

---

# 12. FACE TRACKING

Tracking converts frame observations into continuous subject tracks.

Example:

```text
Frame 101 → face
Frame 102 → face
Frame 103 → face
```

becomes:

```text
TRACK-017
```

## 12.1 Tracking requirements

Each track retains:

- track_id
- source evidence
- first observed timestamp
- last observed timestamp
- underlying detection IDs
- tracker configuration/version
- lifecycle state

## 12.2 Track lifecycle

Recommended states:

```text
CREATED
ACTIVE
LOST
CLOSED
```

## 12.3 Identity semantics

A track means:

> The tracker believes these detections belong to the same visual track.

It does not prove that the detections belong to the same real-world person.

Track identity and person identity must remain separate concepts.

---

# 13. FACE QUALITY

Quality is an independent signal.

Potential dimensions:

- face pixel size
- blur/sharpness
- pose
- occlusion
- illumination
- alignment quality
- detector quality

Store component values where practical.

Example:

```text
quality_state: GOOD
blur_score: ...
face_size: ...
pose_score: ...
occlusion_score: ...
```

Do not reduce quality to an unexplained arbitrary score if the components are available.

---

# 14. EMBEDDING GENERATION

The recognition stage converts an eligible face crop into a vector representation.

The embedding service must return:

```text
vector
dimension
normalization_state
model_id
model_version
preprocessing_version
```

Validate:

- expected dimensionality
- finite numeric values
- normalization expectations
- model compatibility

Do not mix incompatible embeddings inside one search index without an explicit migration strategy.

---

# 15. MODEL VERSIONING

Every embedding must be associated with a model identity.

Recommended metadata:

```text
provider = InsightFace
detector_model = ...
recognition_model = ...
model_pack = ...
model_version = ...
runtime_version = ...
preprocessing_version = ...
embedding_dimension = ...
created_at = ...
```

A model upgrade must create a controlled migration path.

Do not silently replace an existing model and continue writing into an old embedding index.

---

# 16. MATCHING ENGINE

```text
Reference Embedding
       ↓
Candidate Retrieval
       ↓
Similarity Calculation
       ↓
Quality Filtering
       ↓
Track Consistency
       ↓
Candidate Ranking
       ↓
Sighting Aggregation
```

## 16.1 Similarity

For L2-normalized embeddings, cosine similarity can be represented through the dot product.

The project-provided InsightFace material explicitly describes cosine comparison over normalized embeddings. [Source: project-provided InsightFace document]

## 16.2 Threshold policy

Thresholds must be stored as configuration.

Example:

```text
MatchingPolicy
  ├── policy_id
  ├── version
  ├── similarity_metric
  ├── candidate_threshold
  ├── high_candidate_threshold
  ├── min_face_quality
  ├── aggregation_rules
  └── evaluation_reference
```

Do not place production thresholds directly inside controller code.

## 16.3 Candidate tiers

Preferred display semantics:

```text
HIGH CANDIDATE
MEDIUM CANDIDATE
LOW / REJECTED
```

Exact rules must be backed by evaluation.

## 16.4 Never convert similarity directly into identity

Similarity is a model comparison result.

It is not:

- legal identity
- proof of presence
- guilt
- criminal classification

---

# 17. VECTOR SEARCH

pgvector may be used for embedding retrieval.

The implementation must ensure:

- vector dimension consistency
- correct distance metric
- appropriate index
- query filtering by authorized scope
- model/version compatibility
- predictable latency

The vector search layer must never bypass case authorization.

Potential query scope:

```text
case_id = current_case
```

or an explicitly authorized multi-case scope.

## 17.1 Index strategy

Evaluate exact search before choosing approximate search.

For larger datasets, an approximate index such as HNSW may be considered after benchmark testing.

Do not introduce an approximate index just because it is fashionable.

Measure:

- recall
- latency
- index build cost
- memory
- update cost

---

# 18. SIGHTING AGGREGATION

Frame-level observations should be aggregated.

Example:

```text
14:21:01  similarity 0.88
14:21:02  similarity 0.91
14:21:03  similarity 0.93
14:21:04  similarity 0.90
14:21:05  similarity 0.89
```

should produce:

```text
SIGHTING-001

source = CCTV-01
track = TRACK-017
start = 14:21:01
end = 14:21:05
best_similarity = 0.93
observation_count = 5
```

All source observations remain accessible.

Aggregation must not destroy frame-level evidence.

---

# 19. MULTI-VIDEO SEARCH

One investigation may select:

```text
CCTV-01
CCTV-02
CCTV-03
```

Each source must be processed independently.

Then:

```text
candidate observations
      ↓
source-specific tracks
      ↓
source-specific sightings
      ↓
case-level aggregation
```

Never merge track IDs across independent video sources.

A higher-level relationship may connect sightings, but original source-track identity must remain intact.

---

# 20. REAL-TIME EVENT ARCHITECTURE

```text
Worker
  ↓
Domain Event
  ↓
Redis/Event Bus
  ↓
WebSocket Gateway
  ↓
React
```

## 20.1 Event types

Recommended events:

```text
face_job.created
face_job.queued
face_job.started
face_job.progress
face_track.created
face_candidate.detected
face_sighting.created
face_sighting.updated
face_job.paused
face_job.failed
face_job.completed
face_job.cancelled
face_review.updated
```

## 20.2 Event payload principles

Events should contain:

- event_id
- event_type
- event_version
- occurred_at
- case_id
- investigation_id
- job_id
- relevant entity IDs
- concise display-safe metadata

Do not send raw biometric embeddings over WebSocket.

Do not send unnecessary original media.

## 20.3 Event idempotency

Every event must have a stable event ID.

Frontend consumers must tolerate duplicate delivery.

Workers must not create duplicate sightings because a retry occurs.

---

# 21. API CONTRACT PRINCIPLES

Recommended conceptual endpoints:

```text
POST /api/v1/cases/{case_id}/face-investigations

POST /api/v1/face-investigations/{id}/reference

POST /api/v1/face-investigations/{id}/search

GET /api/v1/face-investigations/{id}

GET /api/v1/face-investigations/{id}/sightings

GET /api/v1/face-sightings/{id}

POST /api/v1/face-sightings/{id}/review

POST /api/v1/face-investigations/{id}/cancel
```

Exact route names must follow existing CrimeKit API conventions.

Do not introduce duplicate route conventions.

---

# 22. ASYNCHRONOUS JOB STATE MACHINE

Recommended lifecycle:

```text
CREATED
  ↓
VALIDATING_REFERENCE
  ↓
REFERENCE_READY
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
```

Failure:

```text
ANY STATE → FAILED
```

Cancellation:

```text
QUEUED / PROCESSING / MATCHING
       ↓
CANCELLING
       ↓
CANCELLED
```

Every state transition must be validated.

Do not let arbitrary API calls write arbitrary states.

---

# 23. DATABASE MODEL — CONCEPTUAL

Recommended domain entities:

```text
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
```

Each entity should have:

- primary identifier
- case linkage where applicable
- created timestamp
- updated timestamp where applicable
- provenance references
- authorization scope where applicable

Avoid unnecessary denormalization until profiling proves it useful.

---

# 24. GRAPH MODEL — CONCEPTUAL

Neo4j should represent relationships, not replace the forensic relational record.

Example:

```text
(:FaceInvestigation)
        |
        | HAS_SIGHTING
        ↓
(:FaceSighting)
        |
        ├── FROM_EVIDENCE → (:Evidence)
        ├── TRACKED_AS → (:FaceTrack)
        ├── OCCURRED_AT → (:Time)
        └── AT_LOCATION → (:Location)
```

Where a candidate mapping is permitted:

```text
(:FaceSighting)
        |
        | CANDIDATE_FOR
        ↓
(:InvestigativeEntity)
```

Do not create:

```text
(:Criminal)
```

merely because the face matcher found a candidate.

The graph must represent investigative facts and candidate relationships with clear provenance.

---

# 25. FORENSIC PROVENANCE

Every candidate/sighting must answer:

```text
WHERE did this originate?
WHEN did the source event occur?
WHAT evidence produced it?
WHAT frame produced it?
WHICH model produced the embedding?
WHICH policy generated the candidate decision?
WHO reviewed it?
WHEN was it reviewed?
```

Minimum provenance chain:

```text
Case
  ↓
Investigation
  ↓
Search Job
  ↓
Processing Run
  ↓
Evidence
  ↓
Artifact
  ↓
Frame
  ↓
Detection
  ↓
Track
  ↓
Candidate
  ↓
Sighting
  ↓
Review
```

---

# 26. SOURCE FRAME ACCESS

When an investigator opens a candidate:

```text
Candidate
   ↓
Sighting
   ↓
Source artifact
   ↓
Exact frame
   ↓
Bounding box overlay
```

The UI should make it easy to navigate:

```text
candidate → source frame → original evidence
```

---

# 27. INVESTIGATOR REVIEW

Review states:

```text
PENDING
CONFIRMED_AS_CANDIDATE
REJECTED
NEEDS_FURTHER_REVIEW
```

Terminology must avoid implying a legally conclusive identity unless organizational/legal requirements explicitly authorize it.

Review actions must record:

```text
reviewer_id
review_time
previous_state
new_state
reason
optional notes
```

Review history must be auditable.

---

# 28. SECURITY AND AUTHORIZATION

## 28.1 Authentication

Use existing CrimeKit authentication.

Do not create a second authentication system.

## 28.2 Authorization

Every operation must verify:

```text
user
  ↓
role
  ↓
case access
  ↓
evidence access
  ↓
face investigation access
```

## 28.3 Cross-case search

Cross-case search requires explicit authorization.

Default behavior is case-scoped.

## 28.4 Embedding protection

Treat embeddings as protected data.

Do not:

- log vectors
- expose vectors in ordinary UI responses
- include vectors in exception messages
- put vectors in analytics payloads
- send vectors to the browser unnecessarily

## 28.5 Media access

Original media should be accessed through controlled authorization-aware mechanisms.

Do not expose public object-storage URLs unless explicitly permitted by the security model.

---

# 29. PRIVACY AND DATA LIFECYCLE

The subsystem must define:

- collection purpose
- authorized users
- retention
- deletion
- derived-artifact retention
- embedding deletion
- investigation closure behavior
- export behavior
- audit retention

Do not retain biometric-derived data indefinitely by default.

Retention must be configurable and tied to CrimeKit case/evidence governance.

---

# 30. OBSERVABILITY

Every processing run should expose structured telemetry.

## 30.1 Metrics

```text
jobs_started
jobs_completed
jobs_failed
frames_decoded
frames_sampled
faces_detected
faces_rejected_quality
embeddings_generated
candidates_generated
sightings_generated
review_confirmed
review_rejected
```

Performance:

```text
decode_fps
detection_latency_ms
embedding_latency_ms
vector_search_latency_ms
aggregation_latency_ms
end_to_end_latency_ms
```

Resource:

```text
gpu_utilization
gpu_memory
cpu_utilization
process_memory
queue_depth
```

## 30.2 Logging

Use structured logs.

Include identifiers:

```text
case_id
investigation_id
job_id
processing_run_id
evidence_id
```

Do not log:

- raw face vectors
- secrets
- access tokens
- unnecessary sensitive image content

---

# 31. PERFORMANCE ARCHITECTURE

Separate:

```text
API compute
video decode compute
inference compute
database compute
WebSocket/event compute
```

Recommended topology:

```text
API Nodes
     +
GPU Inference Worker Nodes
     +
General Video/Workflow Workers
     +
Database
     +
Object Storage
     +
Event Infrastructure
```

## 31.1 GPU worker model

Each GPU worker should:

- load model once
- process batches where supported
- avoid unnecessary host/device copies
- maintain bounded queues
- expose readiness/health
- release resources gracefully

## 31.2 Backpressure

```text
incoming work
   ↓
bounded queue
   ↓
controlled admission
```

Do not allow unbounded RAM growth.

## 31.3 Cancellation

Cancellation must stop new frame work and terminate downstream processing cleanly.

Already persisted forensic observations must remain valid.

---

# 32. RESILIENCE

The system must handle:

- worker crash
- video decode error
- corrupt frame
- GPU unavailable
- CUDA initialization error
- model loading failure
- database timeout
- Redis/event failure
- WebSocket disconnect
- client refresh
- duplicate task delivery
- job cancellation
- partial job completion

A WebSocket disconnect must not terminate the forensic job.

The UI should reconnect and retrieve authoritative state from the API.

---

# 33. IDEMPOTENCY

Retryable operations must be idempotent where practical.

Example:

```text
same frame
same processing_run
same detection key
```

must not create uncontrolled duplicate records.

Use deterministic processing IDs or unique constraints where appropriate.

---

# 34. DATA CONSISTENCY

Transactions must protect logically coupled writes.

Example:

```text
Candidate created
   +
Provenance linked
   +
Review state initialized
```

must not leave a partially committed candidate without provenance.

For distributed operations, prefer explicit state transitions and retry/compensation logic instead of assuming cross-system transactions.

---

# 35. ERROR HANDLING

Suggested categories:

```text
INPUT_INVALID
REFERENCE_INVALID
NO_FACE
MULTIPLE_REFERENCE_FACES
LOW_QUALITY
EVIDENCE_ACCESS_DENIED
UNSUPPORTED_MEDIA
DECODE_FAILURE
MODEL_UNAVAILABLE
GPU_UNAVAILABLE
VECTOR_SEARCH_FAILURE
DATABASE_FAILURE
EVENT_FAILURE
INTERNAL_ERROR
```

User-facing messages must be understandable and safe.

Internal diagnostic details belong in controlled logs.

---

# 36. TESTING REQUIREMENTS

Testing must cover five layers.

## 36.1 Unit tests

Test:

- reference validation
- bbox normalization
- quality policy
- embedding validation
- similarity calculation
- threshold policy
- track aggregation
- sighting aggregation
- event serialization
- state transitions

## 36.2 Integration tests

Test:

```text
API
  ↓
job
  ↓
worker
  ↓
persistence
  ↓
event
```

## 36.3 Model evaluation

Build a labeled evaluation set representative of CrimeKit conditions.

Measure at minimum:

- false accepts
- false rejects
- precision/recall at evaluated operating points
- ROC/DET where appropriate
- performance by image/video condition

Conditions should include where available:

- frontal
- profile
- low light
- blur
- occlusion
- distance
- compression
- crowded scenes
- multiple camera qualities

Do not copy a generic threshold from another project and call it validated.

## 36.4 Performance testing

Measure:

- frames/sec
- faces/sec
- embeddings/sec
- average latency
- p95 latency
- queue delay
- GPU utilization
- GPU memory
- CPU utilization
- database latency

## 36.5 Failure testing

Simulate:

- corrupt media
- no faces
- dozens of faces
- disconnected camera
- model load failure
- worker restart
- Redis restart
- database restart
- frontend reconnect
- duplicate events

---

# 37. ACCEPTANCE CRITERIA

The feature is not complete merely because a face can be detected.

## Reference

- reference image upload works
- invalid reference is rejected
- ambiguous reference is handled
- embedding is versioned
- reference is case-scoped

## Video

- MP4/local test video is processed
- frames receive correct source timestamps
- faces are detected
- tracks are generated
- candidate embeddings are generated
- similarity is computed
- candidate sightings are aggregated

## Evidence

- every sighting links to source evidence
- exact source frame can be opened
- provenance is visible
- original evidence remains unchanged

## Real time

- processing progress appears without page refresh
- candidate events appear live
- UI reconnects after WebSocket interruption

## Security

- unauthorized case access is denied
- biometric vectors are never sent to the browser by default
- sensitive data is not logged

## Reliability

- worker failure does not corrupt the case
- duplicate jobs/events do not create uncontrolled duplicates
- failed jobs have diagnosable status

---

# 38. DEMO / SIH VERTICAL SLICE

For the first implementation, prioritize this end-to-end path:

```text
Investigator
    ↓
Upload reference image
    ↓
Validate face
    ↓
Generate embedding
    ↓
Select one video
    ↓
Start investigation
    ↓
Worker processes video
    ↓
Face detection
    ↓
Tracking
    ↓
Matching
    ↓
Candidate sighting
    ↓
Live event
    ↓
React result
    ↓
Click candidate
    ↓
Exact source frame
    ↓
Provenance
    ↓
Investigator review
```

Only after this is stable should the team expand to:

- multiple videos
- cross-camera correlation
- graph integration
- advanced optimization
- live RTSP
- large-scale indexing

---

# 39. IMPLEMENTATION ORDER

## Phase 1 — Architecture integration

1. Inspect current CrimeKit repository.
2. Identify evidence APIs.
3. Identify worker/workflow system.
4. Identify storage.
5. Identify PostgreSQL schema conventions.
6. Identify pgvector implementation.
7. Identify Neo4j implementation.
8. Identify WebSocket/event infrastructure.
9. Identify authentication/authorization.
10. Identify existing video processing code.

Do not implement duplicate infrastructure before this analysis.

## Phase 2 — Reference pipeline

Implement:

```text
upload
↓
detection
↓
quality
↓
embedding
↓
persistence
```

## Phase 3 — Single-video search

Implement:

```text
video
↓
sampling
↓
detection
↓
tracking
↓
embedding
↓
matching
```

## Phase 4 — Sighting and provenance

Implement:

```text
observations
↓
tracks
↓
sightings
↓
source-frame provenance
```

## Phase 5 — Real-time UI

Implement:

```text
worker event
↓
event bus
↓
WebSocket
↓
React live findings
```

## Phase 6 — Review

Implement:

```text
candidate
↓
investigator review
↓
audit trail
```

## Phase 7 — Graph/timeline integration

Only after forensic records are stable:

```text
sighting
   ↓
timeline
   +
Neo4j relationship
```

## Phase 8 — Scale optimization

Then evaluate:

- batching
- GPU optimization
- vector indexing
- adaptive sampling
- worker scaling
- multiple cameras

---

# 40. CODE ORGANIZATION PRINCIPLES

Exact paths must follow the existing CrimeKit repository.

Conceptually:

```text
forensic/
  face-intelligence/
    detection/
    recognition/
    quality/
    tracking/
    matching/
    aggregation/
    provenance/
    models/
    workers/
```

Integrate with existing:

```text
backend/
workflow/
database/
storage/
```

Do not duplicate business logic across:

```text
router
worker
service
model
frontend
```

One domain rule should have one authoritative implementation.

---

# 41. FRONTEND DESIGN PRINCIPLES

The UI should feel like an investigation workspace, not a consumer AI demo.

Primary surfaces:

```text
Face Trace Investigator
Reference Face
Evidence Selection
Processing Status
Live Findings
Video Viewer
Timeline
Candidate Detail
Provenance
Review
```

The frontend must clearly distinguish:

```text
MACHINE-GENERATED CANDIDATE
INVESTIGATOR REVIEW
SOURCE EVIDENCE
```

Do not make a candidate look like an authoritative identity.

---

# 42. UX STATES

Every major UI must handle:

```text
EMPTY
UPLOADING
VALIDATING
READY
QUEUED
PROCESSING
MATCHING
FINDING
COMPLETED
FAILED
CANCELLED
NO_MATCHES
PARTIAL_RESULTS
```

The interface must never become blank during processing.

---

# 43. ACCESSIBILITY

The feature must support:

- keyboard navigation
- visible focus
- accessible labels
- non-color-only status indication
- readable source-frame controls
- high-contrast evidence overlays
- screen-reader compatible status messages where practical

Do not use color alone to communicate candidate state.

---

# 44. INTERNATIONALIZATION / TIME

CrimeKit may process evidence from different jurisdictions and systems.

Store timestamps in a canonical representation.

Display investigator-localized time at presentation level.

Preserve original source timestamp when available.

Never silently rewrite event time.

---

# 45. CONFIGURATION

Configuration should be externalized.

Potential settings:

```text
FACE_MODEL_ID
FACE_MODEL_VERSION
DETECTOR_SIZE
FRAME_SAMPLE_RATE
MAX_CONCURRENT_JOBS
MIN_FACE_SIZE
QUALITY_POLICY_ID
MATCH_POLICY_ID
VECTOR_INDEX_NAME
GPU_DEVICE_ID
WORKER_TIMEOUT
RETENTION_POLICY
```

Do not place environment-specific settings in application code.

Secrets must never be committed.

---

# 46. SECURITY OF DEPLOYMENT

Production deployment should use:

```text
TLS
authenticated APIs
authorization middleware
private databases
protected object storage
restricted worker networking
secret management
audit logs
monitoring
backup/recovery
```

GPU inference workers should not require public internet access for normal runtime inference unless a documented dependency requires it.

Where possible, model artifacts should be immutable and checksum-verified before runtime use.

---

# 47. MODEL ARTIFACT INTEGRITY

Before loading a model:

1. Verify model file availability.
2. Verify checksum/version.
3. Verify expected model metadata.
4. Verify runtime compatibility.
5. Load model.
6. Run health inference.
7. Mark worker READY.

If verification fails:

```text
worker = NOT_READY
```

Never silently load an unknown model.

---

# 48. MODEL UPGRADE POLICY

A model upgrade must go through:

```text
candidate model
   ↓
offline evaluation
   ↓
regression comparison
   ↓
performance test
   ↓
licensing verification
   ↓
deployment approval
   ↓
version activation
   ↓
monitoring
```

Existing results retain original model metadata.

Do not rewrite historical results to pretend they were generated by a new model.

---

# 49. EXPERIMENTATION POLICY

Experiments must not contaminate production data.

Use:

```text
experimental model
experimental processing run
isolated index/dataset
explicit experiment metadata
```

Do not mix experimental embeddings into the production index without authorization.

---

# 50. LICENSE / PROVIDER POLICY

## InsightFace hosted evaluation service

The project-provided document states that:

- the hosted service is for evaluation
- access requires an MOU
- the endpoint is private
- the evaluation period is limited
- the service is rate-limited
- long-term deployment uses locally deployed model files

Therefore:

```text
Hosted InsightFace endpoint
        ↓
   evaluation only
```

and:

```text
Approved production model
        ↓
   local inference
```

Do not build the production architecture around repeated hosted API calls.

## Model licensing

Before production commercialization, verify the exact model artifact/license for the selected deployment.

Documentation must record:

```text
provider
model
license
source
approval status
```

---

# 51. OPERATIONAL HEALTH

Expose health states:

```text
STARTING
READY
DEGRADED
NOT_READY
```

Inference worker readiness should verify:

- model loaded
- runtime initialized
- expected provider available
- test inference succeeded
- required dependencies for that worker role are reachable

Liveness and readiness are separate concepts.

---

# 52. DISASTER RECOVERY

The feature must not make the case unrecoverable if the face service is unavailable.

Core case evidence remains authoritative.

Face analysis is a derived processing layer.

Back up:

- domain records
- job state
- review history
- provenance
- configuration/version metadata

Original evidence follows the primary evidence backup policy.

---

# 53. DATA EXPORT

Any exported face-investigation report must include:

- case
- investigation
- source evidence
- sightings
- timestamps
- candidate metadata
- model/version metadata
- matching policy version
- investigator review state
- provenance references

Do not export raw embeddings unless the project's controlled forensic-export policy explicitly requires them.

---

# 54. AUDIT REQUIREMENTS

Audit at minimum:

```text
investigation_created
reference_uploaded
evidence_selected
search_started
search_cancelled
candidate_created
sighting_created
source_viewed
review_changed
export_created
cross_case_search_requested
access_denied
```

Audit records identify:

```text
actor
action
case
target
timestamp
outcome
```

---

# 55. SECURITY FAILURE PRINCIPLE

When uncertain:

```text
deny access
preserve evidence
record the failure
do not fabricate a result
```

Never:

```text
fail open
bypass case ACL
substitute a guessed identity
silently retry with a different model
hide model failures
```

---

# 56. PERFORMANCE FAILURE PRINCIPLE

When overloaded:

```text
apply backpressure
reduce nonessential processing
queue work
expose degraded state
```

Do not:

- exhaust memory
- drop provenance
- silently skip source evidence
- create false completion states

If frames are intentionally skipped by policy, that fact must remain knowable through processing metadata.

---

# 57. INVESTIGATIVE SAFETY PRINCIPLE

Preserve the distinction:

```text
MACHINE OBSERVATION
        ≠
INVESTIGATIVE CONCLUSION
```

Example:

```text
Machine observation:
Candidate similarity = X

Investigative record:
Candidate sighting from CCTV-01 at timestamp Y

Investigator action:
Reviewed / Rejected / Needs review
```

This separation is mandatory.

---

# 58. DO NOT IMPLEMENT THESE ANTI-PATTERNS

Do not build:

```text
React → InsightFace directly

FastAPI request → process entire 2-hour CCTV synchronously

Browser → PostgreSQL

Browser → pgvector

Face match → "CRIMINAL"

Hard-coded threshold with no evaluation record

Random embedding model changes

Duplicate message creates duplicate sighting

Hosted evaluation API as production inference

Unbounded global biometric search

Unversioned model deployment

Raw embedding in logs

Public face-image URLs

Destructive evidence transformations

Fake AI confidence

Automatic identity confirmation with no review path
```

---

# 59. DEFINITION OF DONE

The subsystem is complete only when:

## Architecture

- boundaries are respected
- existing CrimeKit services are reused
- no duplicate infrastructure exists

## Model

- approved model is versioned
- runtime is validated
- licensing status is documented

## Backend

- APIs are secured
- jobs are asynchronous
- states are deterministic
- retries are safe

## Forensics

- source evidence remains immutable
- provenance is complete
- frames/tracks/sightings are traceable

## Search

- similarity is evaluated
- policy is versioned
- vector search is authorized
- candidate ranking is explainable

## Real time

- events are emitted
- UI updates live
- reconnect works
- duplicate events are safe

## Frontend

- all states are designed
- source-frame verification works
- review is explicit

## Security

- case access is enforced
- embeddings are protected
- logs do not leak sensitive data

## Testing

- unit tests pass
- integration tests pass
- model evaluation exists
- performance baseline exists
- failure tests exist

## Operations

- health/readiness checks work
- metrics exist
- structured logs exist
- deployment configuration is documented

---

# 60. REQUIRED IMPLEMENTATION DELIVERABLES

The implementation agent must produce real working integration for:

1. Reference image processing
2. Face embedding generation
3. Video processing
4. Face detection
5. Face tracking
6. Candidate matching
7. Sighting aggregation
8. Provenance persistence
9. Real-time events
10. Investigator UI
11. Investigator review
12. Tests
13. Performance baseline
14. Security validation
15. Model/version metadata

Do not create placeholder modules and call the feature complete.

---

# 61. AGENT EXECUTION PROTOCOL

Before coding:

1. Read this `MASTER_SPEC.md`.
2. Read `RULES.md`.
3. Read `INSTRUCTIONS.md`.
4. Inspect the existing CrimeKit repository.
5. Map existing reusable infrastructure.
6. Identify exact integration points.
7. Produce an implementation plan.
8. State assumptions and unresolved conflicts.
9. Do not modify code until architecture integration is understood.

During coding:

1. Implement one bounded subsystem at a time.
2. Keep changes small and reviewable.
3. Run tests after every meaningful layer.
4. Do not rewrite unrelated modules.
5. Do not create duplicate abstractions.
6. Record model/configuration changes.
7. Preserve evidence provenance.
8. Inspect git diff frequently.

After coding:

1. Run backend tests.
2. Run frontend tests.
3. Run type checks.
4. Run lint.
5. Run integration tests.
6. Validate model loading.
7. Validate video processing.
8. Validate WebSocket events.
9. Validate database persistence.
10. Validate authorization.
11. Run performance tests.
12. Inspect git status/diff.
13. Confirm no secrets/evidence artifacts were added.
14. Confirm no unrelated CrimeKit behavior changed.

---

# 62. FINAL ENGINEERING PRINCIPLE

CrimeKit Face Trace Investigator is not successful because it can draw a bounding box around a face.

It is successful when an investigator can move from:

```text
REFERENCE IMAGE
      ↓
MACHINE-GENERATED CANDIDATE
      ↓
EXACT SOURCE FRAME
      ↓
TIMESTAMP
      ↓
EVIDENCE
      ↓
PROVENANCE
      ↓
INVESTIGATOR REVIEW
```

with every step being:

```text
traceable
reproducible
authorized
versioned
observable
explainable
maintainable
```

Optimize for:

```text
FORENSIC INTEGRITY
TRACEABILITY
SECURITY
PERFORMANCE
RELIABILITY
HUMAN REVIEW
MAINTAINABILITY
```

not for:

```text
FAKE COMPLEXITY
FAKE ACCURACY
FAKE CONFIDENCE
UNNECESSARY ABSTRACTIONS
```

---

# 63. AUTHORITATIVE SUMMARY

The target CrimeKit Face Trace Investigator architecture is:

```text
Authorized Investigator
          ↓
Reference Image
          ↓
Face Validation
          ↓
Local Face Model
          ↓
Reference Embedding
          ↓
Authorized Evidence
          ↓
Async Search Job
          ↓
Video Decoder
          ↓
Frame Sampling
          ↓
Face Detection
          ↓
Quality Filtering
          ↓
Face Tracking
          ↓
Face Embedding
          ↓
Similarity / Vector Search
          ↓
Candidate Ranking
          ↓
Sighting Aggregation
          ↓
Provenance
          ↓
PostgreSQL + pgvector + Neo4j
          ↓
Real-Time Event Stream
          ↓
WebSocket
          ↓
Investigator UI
          ↓
Source Verification
          ↓
Human Review
          ↓
Timeline / Graph / Reporting
```

Every connection must remain evidence-backed.

Every machine-generated candidate must remain distinguishable from a human investigative conclusion.

Every production model must be versioned and legally approved for its intended deployment.

Every original evidence item must remain immutable.

**This is the definition of the CrimeKit Face Trace Investigator.**
