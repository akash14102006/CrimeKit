# CrimeKit Face Trace Investigator — RULES

**Document:** `RULES.md`  
**Subsystem:** Face Trace Investigator  
**Authority:** Non-negotiable engineering, forensic, security, biometric, and operational rules  
**Precedence:** These rules apply unless a higher-level CrimeKit security, legal, or architecture policy is stricter.

---

# 1. PURPOSE

This document defines the rules that every engineer, coding agent, reviewer, tester, and deployment operator must follow when implementing or modifying the CrimeKit Face Trace Investigator subsystem.

These are constraints, not suggestions.

When a requested implementation conflicts with a rule:

1. Stop the conflicting implementation.
2. Identify the conflict.
3. Preserve the stronger security/forensic requirement.
4. Escalate the architectural decision when necessary.
5. Never silently weaken a rule.

---

# 2. CORE PRINCIPLES

## RULE 001 — Evidence First

All machine-generated face observations must remain subordinate to the source evidence.

The system must always be able to navigate from:

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
    Source Evidence

A result without a traceable source is not a valid forensic result.

---

## RULE 002 — Evidence Immutability

Original evidence must never be modified, overwritten, re-encoded in place, cropped in place, or destructively transformed by the face-intelligence subsystem.

Derived artifacts must be stored separately and linked to their source.

---

## RULE 003 — No Automatic Guilt Determination

Face recognition may produce candidate observations.

It must never automatically determine:

- guilt
- criminal responsibility
- intent
- culpability
- legal identity
- conviction
- arrest justification

Do not create code, labels, graph node types, UI copy, or API semantics that imply the model has made a legal determination.

---

## RULE 004 — Candidate Does Not Mean Identity

A similarity result is a machine-generated candidate.

The system must not convert:

    similarity = X

into:

    identity = proven person

unless a separately authorized and documented workflow explicitly supports that conclusion.

The default state is:

    candidate
    pending review

---

## RULE 005 — Human Review Must Remain Explicit

Consequential candidate decisions must have an explicit investigator review state.

The review action must identify:

- reviewer
- timestamp
- decision
- reason/notes where required
- previous state
- resulting state

Never silently mark a candidate as investigator-confirmed.

---

# 3. ARCHITECTURE RULES

## RULE 006 — Follow Existing CrimeKit Architecture

Before creating anything new, inspect the current repository.

Reuse existing:

- evidence services
- authentication
- authorization
- workflow
- worker infrastructure
- object storage
- database abstractions
- event infrastructure
- logging
- observability
- frontend patterns

Do not build parallel infrastructure without an approved architectural reason.

---

## RULE 007 — Do Not Break Existing CrimeKit

Do not rewrite unrelated modules simply to fit the face-intelligence feature.

The feature must adapt to the existing system unless a documented architecture change is approved.

The current project governance explicitly prioritizes protecting working CrimeKit behavior over repository appearance or artificial complexity.

---

## RULE 008 — Forensic Processing Is Separate from AI Reasoning

Face detection, face quality evaluation, tracking, embedding, matching, aggregation, and provenance are forensic/computational processing.

Higher-level AI agents may consume their structured output.

Do not put deterministic face-processing logic into an LLM agent.

Do not use an LLM to replace exact evidence provenance.

---

## RULE 009 — API and Worker Separation

Do not perform long-running video inference inside a normal synchronous HTTP request.

The API creates and controls the job.

Workers perform the processing.

---

## RULE 010 — Model Adapter Boundary

Application code must not depend directly on scattered InsightFace implementation objects.

Hide provider-specific implementation behind a stable CrimeKit interface.

Conceptually:

    FaceModelProvider
    FaceDetector
    FaceEmbedder
    FaceQualityEvaluator

The exact interface names must follow the existing project conventions.

---

## RULE 011 — No Business Logic in Frontend

React may present state and issue commands.

React must not become the authoritative location for:

- matching thresholds
- case authorization
- biometric policy
- investigator permissions
- evidence integrity
- model decisions
- database logic

---

## RULE 012 — No Direct Database Access from Browser

The frontend must not access PostgreSQL, pgvector, Neo4j, Redis, or internal worker systems directly.

Use authorized backend APIs and approved real-time channels.

---

# 4. INSIGHTFACE RULES

## RULE 013 — Local Production Inference

Do not make CrimeKit production inference dependent on a hosted per-image InsightFace evaluation endpoint.

The production architecture must use an approved local/self-hosted model runtime where licensing permits.

The project-provided InsightFace evaluation material explicitly distinguishes the hosted evaluation API from offline production deployment.

---

## RULE 014 — Hosted Evaluation Endpoint Is Not the Runtime Path

The hosted evaluation service may be used for controlled model benchmarking where authorized.

It must not become:

    CCTV frame
       ↓
    HTTP upload
       ↓
    hosted recognition
       ↓
    response

as the normal production hot path.

---

## RULE 015 — Model Licensing Is Mandatory

Never assume a model is commercially usable merely because its surrounding software is open source.

Before production deployment, document:

- provider
- exact model
- artifact source
- artifact version
- applicable license
- intended-use restrictions
- approval status

If licensing status is unresolved, do not represent the model as production-approved.

---

## RULE 016 — Model Version Is Immutable Per Processing Run

Every processing run must record the exact model identity/version used.

Historical results must not be silently re-labeled as having been generated by a newer model.

---

## RULE 017 — Never Mix Incompatible Embeddings

Do not place embeddings from incompatible model versions or incompatible dimensions into the same logical vector search space.

If a migration is required:

    old model/index
          +
    new model/index

must have an explicit migration/compatibility strategy.

---

## RULE 018 — Load Models Once

Inference workers must load models once per approved process/lifecycle.

Never initialize and destroy an InsightFace model for every image or frame.

---

## RULE 019 — Verify Model Artifacts

Before a production worker becomes READY:

1. Verify model availability.
2. Verify expected artifact/version.
3. Verify checksum/integrity where configured.
4. Initialize runtime.
5. Perform a health inference.
6. Confirm expected model outputs.
7. Mark worker READY only on success.

Unknown or unverified model artifacts must not be silently loaded.

---

## RULE 020 — Provider-Neutral Domain Model

CrimeKit domain records must not depend on one vendor's proprietary object structure.

Persist stable domain metadata such as:

- model provider
- model ID
- model version
- embedding dimension
- runtime version
- preprocessing version

---

# 5. BIOMETRIC DATA RULES

## RULE 021 — Treat Face Data as Sensitive

Reference images, derived face crops, embeddings, candidate results, and biometric metadata must be protected as sensitive investigative information.

Apply the strongest applicable CrimeKit security policy.

---

## RULE 022 — Never Log Raw Embeddings

Do not place embedding vectors in:

- normal logs
- exception messages
- analytics events
- WebSocket messages
- frontend state
- debug console output
- metrics labels

---

## RULE 023 — Do Not Send Embeddings to Browser by Default

The frontend normally needs:

- candidate ID
- similarity
- quality
- timestamp
- source artifact
- review state

It does not normally need the raw embedding.

---

## RULE 024 — Case Scope by Default

Every face investigation must be tied to a case.

Default search scope:

    current authorized case

not:

    entire CrimeKit database

---

## RULE 025 — Cross-Case Search Requires Explicit Authorization

A cross-case biometric search must:

1. Check explicit permission.
2. Record the authorization context.
3. Record the search.
4. Restrict returned data to authorized scope.
5. Create an audit event.

Never make cross-case search the default because it is technically convenient.

---

## RULE 026 — Least Privilege

Grant the minimum access necessary to:

- view reference images
- start face searches
- view source frames
- view candidate results
- perform reviews
- export results

Do not grant global biometric visibility to every investigator role.

---

## RULE 027 — No Public Media URLs

Do not expose sensitive face imagery or evidence media through uncontrolled public URLs.

Use authorized, time-limited, or server-mediated access as defined by CrimeKit's storage architecture.

---

# 6. REFERENCE IMAGE RULES

## RULE 028 — Validate Reference Images

Reference upload must validate:

- file type
- file size
- image decoding
- security constraints
- face count
- face quality
- image dimensions

---

## RULE 029 — Do Not Silently Pick a Face

If multiple faces are detected in a reference image:

    do not choose faces[0]

without an explicit and documented user-selection policy.

The system must ask for clarification or apply an approved deterministic selection rule that is visible to the investigator.

---

## RULE 030 — Exactly One Intended Reference Face

The reference pipeline should produce one intentional reference identity representation.

Zero faces:

    reject or request replacement

Multiple ambiguous faces:

    reject or request selection

One usable face:

    continue

---

## RULE 031 — Preserve Reference Provenance

A reference face must remain linked to:

- case
- investigation
- source artifact/image
- uploader
- upload event
- processing run

Do not create an orphan biometric representation.

---

## RULE 032 — Do Not Modify the Original Reference

Crop/alignment/normalization operations must produce derived representations.

The uploaded source remains preserved under the project's evidence policy.

---

# 7. VIDEO PROCESSING RULES

## RULE 033 — Source Timestamps Are Authoritative

When available, source timestamps are the event time.

Do not replace source-event time with worker processing time.

Store processing time separately.

---

## RULE 034 — Preserve Frame Identity

Every analyzed frame must be attributable to:

- source evidence
- source video
- frame number where available
- source timestamp
- processing run

---

## RULE 035 — Sampling Must Be Explicit

Frame sampling policy must be:

- configured
- versioned
- observable
- reproducible enough for forensic interpretation

Never silently discard frames without the system retaining knowledge of the sampling policy.

---

## RULE 036 — Do Not Process Every Frame by Default

Do not assume maximum frame-rate recognition is automatically better.

Use a controlled pipeline that balances:

- detection coverage
- recognition quality
- latency
- compute
- storage

Any production sample rate must be benchmarked.

---

## RULE 037 — Tracking Must Be Separate from Identity

A track indicates temporal association between visual detections.

A track does not itself prove real-world person identity.

Never name a track:

    confirmed_person_id

unless the domain semantics explicitly support that mapping.

---

## RULE 038 — Preserve Underlying Detections

When multiple frame observations are aggregated into one sighting, keep the underlying detections accessible.

Aggregation must not destroy source-level observations.

---

## RULE 039 — No Cross-Video Track ID Reuse

Track identifiers are source-specific unless the architecture explicitly defines a higher-level correlation identifier.

Do not assume:

    TRACK-17 in CCTV-01
    =
    TRACK-17 in CCTV-02

---

# 8. FACE DETECTION RULES

## RULE 040 — Detection and Recognition Are Different Stages

Do not treat a detected face as an identified face.

Pipeline:

    detect
      ↓
    quality
      ↓
    track
      ↓
    embed
      ↓
    compare

---

## RULE 041 — Record Detection Metadata

Each face detection must retain sufficient metadata to reproduce its location in the frame.

At minimum:

- bounding box
- detection score
- frame
- timestamp
- source
- processing run

---

## RULE 042 — Multiple Faces Require Multiple Observations

A frame containing five faces should create up to five face observations.

Do not collapse all faces into one frame-level person record.

---

# 9. FACE QUALITY RULES

## RULE 043 — Quality Is Independent from Similarity

Do not treat a high similarity score as proof that the face was well captured.

Store quality separately.

Potential quality dimensions include:

- face size
- blur
- pose
- occlusion
- illumination
- detector quality
- alignment quality

---

## RULE 044 — Poor Quality Must Affect Candidate Handling

Very poor-quality observations should not produce strong candidate displays simply because a numerical similarity happened to exceed a threshold.

Use an approved quality policy.

---

## RULE 045 — Do Not Hide Quality Failures

If a candidate was generated from a poor-quality observation, the investigator must be able to know that.

Do not silently suppress quality context.

---

# 10. EMBEDDING RULES

## RULE 046 — Validate Embedding Output

Every embedding must be checked for:

- expected dimension
- finite numeric values
- expected normalization
- model compatibility

Invalid vectors must not enter the search index.

---

## RULE 047 — Record Embedding Metadata

Every stored embedding must identify:

- model provider
- model ID
- model version
- embedding dimension
- preprocessing version
- created time
- source reference

---

## RULE 048 — Do Not Re-Normalize Blindly

If a model/runtime contract already provides normalized embeddings, follow that contract.

Do not blindly apply additional transformations without validation and documentation.

---

# 11. MATCHING RULES

## RULE 049 — Similarity Is Not Confidence

Similarity is a model comparison signal.

It is not automatically:

    probability of identity

and must not be labeled that way.

---

## RULE 050 — No Hard-Coded Magic Threshold

Do not permanently embed unexplained values such as:

    similarity > 0.55

inside application code.

Thresholds must belong to an explicit matching policy.

---

## RULE 051 — Matching Policy Must Be Versioned

Each candidate result must be attributable to a matching policy version.

Example conceptual policy:

    policy_id
    version
    similarity_metric
    candidate_threshold
    quality_requirement
    aggregation_rule

---

## RULE 052 — Thresholds Must Be Evaluated

A threshold is not production-ready merely because it works on one demonstration video.

Evaluate against a representative labeled dataset and relevant operating conditions.

---

## RULE 053 — Candidate Ranking Must Be Explainable

Where ranking combines multiple signals, store or expose enough information to explain why a candidate appeared above another candidate.

Do not create an opaque composite score with no documented formula.

---

# 12. VECTOR SEARCH RULES

## RULE 054 — Respect Model Compatibility

Vector search must only compare compatible embeddings.

Validate vector dimension and model compatibility before querying.

---

## RULE 055 — Search Must Enforce Authorization

Authorization must constrain vector retrieval.

Do not:

    query all embeddings
    then filter results in the browser

Apply authorization at the authoritative backend/data-access layer.

---

## RULE 056 — Index Strategy Must Be Measured

Exact search should be considered before approximate search.

If approximate indexing such as HNSW is used, measure:

- retrieval recall
- latency
- memory
- index build cost
- update behavior

Do not choose an index based only on popularity.

---

# 13. SIGHTING RULES

## RULE 057 — One Track Can Produce One Sighting, but Not Always

Aggregation logic must account for:

- temporal continuity
- track lifecycle
- gaps
- source boundaries
- matching persistence

Do not assume every track must be exactly one sighting.

---

## RULE 058 — Sighting Must Retain Source Observations

A sighting is a roll-up.

It must not destroy underlying evidence.

---

## RULE 059 — Sighting Needs Exact Temporal Context

Store:

- first observation time
- last observation time
- best candidate observation
- source evidence
- source track
- observation count

---

# 14. PROVENANCE RULES

## RULE 060 — Provenance Is Mandatory

Every candidate/sighting must be linked to source evidence.

No orphan candidates.

---

## RULE 061 — Record Processing Run

A result must identify the processing run that generated it.

This allows investigators to understand:

- which configuration ran
- which model ran
- when it ran
- which evidence version was processed

---

## RULE 062 — Record Model and Policy Versions

Every candidate must retain:

    model version
    preprocessing version
    matching policy version

This makes historical results interpretable.

---

## RULE 063 — Source Frame Must Be Recoverable

Where a candidate originates from a video frame, the investigator must be able to navigate to the source frame through authorized access.

---

## RULE 064 — Never Break the Evidence Chain for Convenience

Do not discard provenance merely because storing an extra identifier is inconvenient.

If an optimization removes provenance, reject the optimization.

---

# 15. REAL-TIME RULES

## RULE 065 — Real-Time Is Event Delivery, Not Repeated Polling Alone

Where CrimeKit has approved event infrastructure, use event-driven updates for live processing state.

Polling may still be used as an authoritative fallback.

---

## RULE 066 — WebSocket Is Not the Source of Truth

WebSocket messages are delivery mechanisms.

The API/database remains authoritative.

If the client reconnects:

    fetch authoritative state

then:

    resume live events

---

## RULE 067 — WebSocket Disconnect Must Not Stop Processing

A browser closing or network disconnecting must not cancel a running forensic job unless an explicit cancellation command is issued.

---

## RULE 068 — Events Must Be Idempotent

Every event should carry a stable identifier.

Consumers must tolerate duplicate delivery.

---

## RULE 069 — Do Not Send Raw Biometrics Over Events

Do not publish:

- face embeddings
- unnecessary raw face crops
- sensitive source imagery

through ordinary real-time event payloads.

---

## RULE 070 — Event Schemas Must Be Versioned

Use an explicit event version.

Consumers must not rely on undocumented payload shape.

---

# 16. ASYNC JOB RULES

## RULE 071 — Use Deterministic Job States

Use controlled job transitions such as:

    CREATED
    VALIDATING_REFERENCE
    REFERENCE_READY
    QUEUED
    PROCESSING
    MATCHING
    FINALIZING
    COMPLETED
    FAILED
    CANCELLED

Do not permit arbitrary state changes from unrelated modules.

---

## RULE 072 — Retry Safely

Retries must not:

- duplicate sightings
- duplicate audit entries incorrectly
- corrupt job progress
- overwrite evidence

Use idempotent identifiers and unique constraints where appropriate.

---

## RULE 073 — Cancellation Must Be Controlled

Cancellation should stop new processing work cleanly.

Already persisted valid forensic observations must not be deleted merely because the remaining job was cancelled.

---

## RULE 074 — Partial Results Must Be Explicit

A partially processed video must never be presented as a complete search.

Expose:

    completed scope
    incomplete scope
    processing status

where applicable.

---

# 17. SECURITY RULES

## RULE 075 — Authentication Is Required

No face-investigation operation is anonymous unless an approved public workflow explicitly requires it.

---

## RULE 076 — Authorization Is Required on Every Sensitive Operation

Verify authorization for:

- reference upload
- evidence selection
- job creation
- candidate viewing
- source-frame viewing
- review
- export
- cross-case search

Do not assume authorization because the user previously accessed the case.

---

## RULE 077 — Fail Closed

When authorization is uncertain:

    deny

Do not guess.

---

## RULE 078 — Never Trust Frontend Roles

Frontend route guards are UX controls.

Backend authorization is authoritative.

---

## RULE 079 — Audit Sensitive Operations

Audit at least:

- investigation creation
- reference upload
- evidence selection
- search start
- search cancellation
- candidate review
- source evidence access
- cross-case search
- export

---

# 18. STORAGE RULES

## RULE 080 — Originals and Derived Data Are Separate

Original evidence:

    immutable source

Derived data:

    detection
    crop
    embedding
    track
    sighting

must remain distinguishable.

---

## RULE 081 — Do Not Store Large Evidence in Git

Never commit:

- real CCTV footage
- real case photographs
- E01/EWF images
- memory dumps
- mobile dumps
- large extracted video
- real biometric datasets

Use controlled storage.

---

## RULE 082 — Follow CrimeKit Retention Policy

Do not create indefinite retention for:

- reference images
- face crops
- embeddings
- intermediate frames
- failed processing artifacts

unless the governing evidence policy explicitly requires it.

---

# 19. FRONTEND RULES

## RULE 083 — Clearly Label Machine Results

The UI must distinguish:

    MACHINE-GENERATED CANDIDATE

from:

    INVESTIGATOR REVIEW

and:

    SOURCE EVIDENCE

---

## RULE 084 — Never Use Misleading Language

Avoid UI text such as:

    "Criminal Found"
    "Guilty"
    "Confirmed Criminal"
    "AI proved identity"

unless a specific legal workflow and approved terminology requires it.

Default terminology should describe candidates and observations.

---

## RULE 085 — Source Verification Must Be Easy

The investigator should be able to go:

    candidate
      ↓
    source frame
      ↓
    original evidence

without complicated navigation.

---

## RULE 086 — Handle Every State

The frontend must explicitly handle:

    empty
    uploading
    validating
    ready
    queued
    processing
    matching
    finding
    completed
    no matches
    failed
    cancelled
    partial results

Never leave a blank screen while the worker is running.

---

## RULE 087 — No Browser Inference by Default

Do not place authoritative InsightFace inference in the browser.

Keep biometric processing inside the controlled backend/inference environment.

---

# 20. DATABASE RULES

## RULE 088 — Database Is Authoritative for State

Do not use frontend state or WebSocket state as the canonical source of job status.

---

## RULE 089 — Use Constraints

Where practical, database constraints must protect invariants such as:

- unique processing identifiers
- valid case relationships
- valid foreign keys
- compatible references

---

## RULE 090 — Avoid Premature Denormalization

Do not duplicate forensic records into several stores without a documented reason.

PostgreSQL, pgvector, Neo4j, and object storage each have distinct responsibilities.

---

# 21. NEO4J RULES

## RULE 091 — Graph Represents Relationships

Neo4j should express relationships derived from validated domain records.

It must not replace the primary forensic record.

---

## RULE 092 — No Automatic "CRIMINAL" Node from Face Match

Never create a graph entity such as:

    (:Criminal)

merely because a face candidate was found.

Use neutral investigative concepts.

---

## RULE 093 — Graph Edges Need Provenance

Where a face-derived edge is created, it should be possible to identify the evidence and processing source behind the edge.

---

# 22. OBSERVABILITY RULES

## RULE 094 — Every Job Must Be Observable

A production operator should be able to determine:

- whether the job exists
- whether it is queued
- where it is processing
- whether inference is available
- whether it failed
- why it failed

---

## RULE 095 — Metrics Must Be Measurable

At minimum, measure relevant:

- jobs
- frames
- detections
- embeddings
- candidates
- sightings
- queue depth
- latency
- throughput
- worker health
- GPU/CPU usage

---

## RULE 096 — Logs Must Be Structured

Logs should use stable fields such as:

    case_id
    investigation_id
    job_id
    processing_run_id
    evidence_id

Do not rely only on free-form strings.

---

# 23. ERROR HANDLING RULES

## RULE 097 — Errors Must Be Classified

Use explicit categories rather than generic:

    something went wrong

Examples:

    INPUT_INVALID
    NO_FACE
    MULTIPLE_FACES
    LOW_QUALITY
    ACCESS_DENIED
    UNSUPPORTED_MEDIA
    DECODE_FAILURE
    MODEL_UNAVAILABLE
    GPU_FAILURE
    DATABASE_FAILURE
    EVENT_FAILURE
    INTERNAL_ERROR

---

## RULE 098 — Never Fabricate Results on Failure

When inference fails:

    report failure

Do not:

    reuse stale result as current result
    return guessed identity
    silently switch to an undocumented model
    mark processing complete

---

# 24. PERFORMANCE RULES

## RULE 099 — Benchmark Before Optimizing

Measure first.

Do not optimize based on assumptions.

---

## RULE 100 — Keep API Latency Separate from Video Processing Latency

A fast API response does not mean the forensic job is fast.

Track:

    enqueue latency
    worker startup
    decode
    detection
    embedding
    vector search
    aggregation
    event publication
    end-to-end completion

---

## RULE 101 — Use Bounded Queues

Never allow uncontrolled frame accumulation that can exhaust memory.

---

## RULE 102 — Backpressure Is Preferable to Memory Exhaustion

When inference is saturated:

    slow admission
    queue
    apply controlled backpressure

Do not keep accepting unlimited work.

---

## RULE 103 — Resource Scaling Must Be Explicit

Separate API, general worker, and GPU inference scaling when required by actual workload.

Do not place every workload in one process for convenience.

---

# 25. MODEL EVALUATION RULES

## RULE 104 — Benchmark on CrimeKit Data Conditions

Do not assume public benchmark numbers represent CrimeKit performance.

Evaluate on a representative labeled dataset.

---

## RULE 105 — Test False Matches

A face search system used in investigation must measure the cost of false matches.

Evaluate false accepts and false rejects.

---

## RULE 106 — Evaluate Different Conditions

Where relevant, test:

- low light
- blur
- profile
- occlusion
- small faces
- compression
- distance
- crowding
- camera variation

---

## RULE 107 — Keep Evaluation Separate from Production Data

Experimental datasets and experimental model runs must not contaminate production indices without approval.

---

# 26. CONFIGURATION RULES

## RULE 108 — No Magic Configuration in Source

Do not hard-code environment-specific:

- model paths
- GPU device
- thresholds
- queue limits
- storage credentials
- database credentials
- event endpoints

Use approved configuration mechanisms.

---

## RULE 109 — No Secrets in Git

Never commit:

- API keys
- passwords
- tokens
- private keys
- cloud credentials
- database credentials
- model-provider credentials

---

## RULE 110 — No Real .env

Use safe environment templates such as:

    .env.example

Never commit a real environment file.

---

# 27. TESTING RULES

## RULE 111 — New Code Requires Tests

Any new non-trivial face-intelligence behavior must have appropriate tests.

---

## RULE 112 — Test Security Boundaries

Verify unauthorized users cannot:

- access another case's investigation
- search another case's embeddings
- view restricted source frames
- review candidates without permission
- perform restricted cross-case searches

---

## RULE 113 — Test Provenance

A successful candidate test must prove that:

    candidate
      ↓
    sighting
      ↓
    frame
      ↓
    evidence

remains navigable.

---

## RULE 114 — Test Retry Behavior

At least one integration test must verify that retried processing does not create uncontrolled duplicate results.

---

## RULE 115 — Test Reconnect Behavior

A WebSocket disconnect/reconnect test must prove that the browser can recover authoritative job state.

---

# 28. DEPLOYMENT RULES

## RULE 116 — Worker Readiness Requires Model Readiness

A face worker must not report READY if its required model cannot execute successfully.

---

## RULE 117 — GPU Failure Must Be Explicit

If GPU inference is unavailable:

    use approved fallback

or:

    mark degraded/not-ready

Do not silently claim the original performance/processing mode.

---

## RULE 118 — Deployment Must Be Reproducible

Record:

- model versions
- runtime versions
- container/image version
- configuration version
- matching policy version

A second environment must be able to understand which components generated a result.

---

# 29. CHANGE MANAGEMENT RULES

## RULE 119 — Model Changes Are Engineering Changes

Changing the model is not a normal dependency bump.

It requires:

- evaluation
- performance testing
- compatibility assessment
- licensing verification
- version recording
- deployment review

---

## RULE 120 — Threshold Changes Are Controlled Changes

Changing a matching threshold changes system behavior.

It requires:

- documented reason
- evaluation evidence
- version update
- regression testing

---

## RULE 121 — Schema Changes Must Preserve Historical Meaning

If a database schema changes, existing results must remain interpretable.

Never remove historical model/version/provenance information merely to simplify the schema.

---

# 30. CODE REVIEW RULES

Every face-intelligence pull request should answer:

    What changed?
    Why?
    What existing CrimeKit module does it integrate with?
    What evidence/provenance impact exists?
    What security impact exists?
    What performance impact exists?
    What tests were run?
    What limitations remain?

Reject PRs containing:

- unexplained thresholds
- direct browser model calls
- bypassed authorization
- missing provenance
- fake confidence
- duplicate infrastructure
- secrets
- untested critical paths

---

# 31. AGENT-SPECIFIC RULES

## RULE 122 — Inspect Before Editing

The coding agent must inspect the current repository before creating or modifying face-intelligence code.

---

## RULE 123 — Do Not Assume File Paths

Do not assume CrimeKit's directory structure from this document alone.

Discover the actual current structure first.

---

## RULE 124 — Do Not Invent Existing Components

Never claim that a queue, service, endpoint, or database abstraction exists until it has been verified.

---

## RULE 125 — Do Not Create Placeholder Complexity

Do not create empty modules, fake agents, fake workers, fake adapters, or unused interfaces merely to make the architecture diagram look complete.

---

## RULE 126 — Do Not Create Documentation to Hide Missing Implementation

Documentation may describe planned work only when clearly marked as planned.

Do not call planned modules implemented.

---

## RULE 127 — Keep Changes Reviewable

Prefer small, coherent changes.

Do not combine:

    face recognition
    unrelated refactor
    database migration
    UI redesign
    infrastructure rewrite

into one unexplained change.

---

## RULE 128 — Validate After Meaningful Changes

After each significant implementation layer:

    run tests
    run type checks
    run lint
    validate imports
    inspect diff
    verify runtime behavior

---

# 32. REPOSITORY/GIT RULES

## RULE 129 — Never Commit Real Evidence

The repository must never contain real case evidence or large biometric datasets.

---

## RULE 130 — Never Commit Secrets

No secrets in source control.

---

## RULE 131 — Never Fake Contributions

Do not artificially split one engineering change into meaningless commits.

Existing CrimeKit governance explicitly prioritizes authentic contribution over artificial commit count.

---

## RULE 132 — Main Must Remain Stable

Face-intelligence changes must follow the team's existing branch/PR/CI workflow.

Do not bypass review simply to demonstrate the feature.

---

# 33. UX AND INVESTIGATOR SAFETY RULES

## RULE 133 — Show the Source

Whenever possible, a candidate result should have a direct path to:

    source frame

not only:

    similarity score

---

## RULE 134 — Show Context

The investigator should be able to understand:

- timestamp
- camera/video
- track
- quality
- similarity
- source evidence

without opening multiple unrelated screens.

---

## RULE 135 — Never Hide Uncertainty

When evidence is weak, communicate uncertainty.

Do not use polished UI to make weak model results appear authoritative.

---

# 34. REAL-TIME CCTV RULES

## RULE 136 — RTSP Is a Stream, Not a File

A live camera pipeline must handle:

- reconnect
- packet loss
- decoder failure
- frame lag
- clock drift
- stream interruption

as first-class states.

---

## RULE 137 — Live Mode Must Not Corrupt Forensic Time

Live processing timestamp is not necessarily the same as source capture timestamp.

Preserve both where available.

---

## RULE 138 — Avoid Duplicate Alerts

A person remaining in front of a camera for many frames must not produce hundreds of identical investigator alerts.

Use track/sighting aggregation.

---

## RULE 139 — Live Mode Must Remain Auditable

Every live candidate must be tied to a source camera/stream identifier and recoverable observation data.

---

# 35. DATA EXPORT RULES

## RULE 140 — Export Only Authorized Data

Reports and exports must respect case and role permissions.

---

## RULE 141 — Preserve Model Context in Exports

Where candidate results are included in an export, preserve:

- model
- model version
- policy version
- timestamp
- evidence reference
- review state

---

## RULE 142 — Do Not Export Raw Biometrics by Default

Raw face vectors are not ordinary report content.

Export only under explicit policy.

---

# 36. OPERATIONAL RULES

## RULE 143 — No Silent Degradation

If the system switches from:

    GPU → CPU

or:

    high-quality mode → reduced mode

the processing run should record the actual mode.

---

## RULE 144 — No Silent Model Fallback

Do not automatically switch to another recognition model because the preferred model failed unless the fallback policy is explicitly configured, approved, and recorded.

---

## RULE 145 — Preserve Failure History

Do not erase failed processing attempts merely because a later retry succeeded.

The authoritative domain may retain attempt metadata as required.

---

# 37. COMPLIANCE-ORIENTED RULES

## RULE 146 — Purpose Limitation

Face analysis must be performed for an authorized investigative purpose.

Do not repurpose the subsystem for unrelated profiling.

---

## RULE 147 — Minimize Data

Process and retain only the data needed for the authorized investigative workflow.

---

## RULE 148 — Retention Must Be Governed

Define retention rules for:

- reference image
- derived face crops
- embeddings
- detections
- tracks
- sightings
- audit records

Do not assume indefinite retention is acceptable.

---

# 38. SECURITY INCIDENT RULES

## RULE 149 — Suspected Biometric Leakage Is a Security Incident

If credentials, embeddings, sensitive images, or restricted evidence are exposed:

1. Stop further exposure.
2. Preserve incident metadata.
3. Do not print secrets.
4. Follow CrimeKit incident response procedures.
5. Rotate credentials when authorized.
6. Audit access.

---

## RULE 150 — Never Publish Sensitive Debug Output

Debug screenshots, notebooks, logs, embeddings, real faces, and real CCTV frames must not be added to public repositories or issue trackers unless explicitly authorized by policy.

---

# 39. FINAL NON-NEGOTIABLE RULES

The following rules override implementation convenience:

1. Evidence must remain immutable.
2. Every candidate must be provenance-linked.
3. Human review remains explicit.
4. Face matching must never be presented as automatic guilt determination.
5. Case authorization must be enforced server-side.
6. Raw biometric embeddings must remain protected.
7. Production inference must not depend on a hosted evaluation endpoint.
8. Model identity/version must be recorded.
9. Matching thresholds must be evaluated and versioned.
10. Video processing must be asynchronous.
11. Real-time events must be idempotent.
12. WebSocket state is not the authoritative source of truth.
13. No silent model or threshold changes.
14. No silent authorization bypass.
15. No fake confidence.
16. No fake modules.
17. No fake data.
18. No fake commits.
19. No real evidence in Git.
20. No secrets in Git.

---

# 40. ENFORCEMENT CHECKLIST

Before merging any face-intelligence change, verify:

## Architecture

[ ] Existing CrimeKit components were inspected.

[ ] No duplicate infrastructure was introduced.

[ ] Forensic processing remains separate from AI reasoning.

[ ] API and worker responsibilities are separated.

## Model

[ ] Approved model/provider is documented.

[ ] Model version is recorded.

[ ] Licensing status is verified for intended use.

[ ] Model artifacts are integrity-checked where required.

[ ] Embedding compatibility is enforced.

## Security

[ ] Case-level authorization exists.

[ ] Cross-case behavior is restricted.

[ ] Raw embeddings are not logged.

[ ] Secrets are not exposed.

[ ] Sensitive media access is controlled.

## Forensics

[ ] Original evidence is unchanged.

[ ] Frame provenance is retained.

[ ] Track provenance is retained.

[ ] Sighting provenance is retained.

[ ] Processing run is recorded.

## Matching

[ ] Similarity is not mislabeled as probability or legal identity.

[ ] Threshold/policy is versioned.

[ ] Evaluation evidence exists.

## Realtime

[ ] Events are versioned.

[ ] Events are idempotent.

[ ] Reconnect works.

[ ] WebSocket is not treated as the source of truth.

## Reliability

[ ] Retry behavior is safe.

[ ] Cancellation is safe.

[ ] Partial processing is explicit.

[ ] Worker failure is observable.

## Testing

[ ] Unit tests pass.

[ ] Integration tests pass.

[ ] Security tests pass.

[ ] Provenance tests pass.

[ ] Performance baseline exists.

[ ] Failure scenarios are covered.

---

# 41. FINAL PRINCIPLE

CrimeKit must never optimize for:

    "The AI found someone."

CrimeKit must optimize for:

    "The system generated a candidate from authorized evidence,
     preserved the exact source and processing history,
     exposed the machine-generated uncertainty,
     and allowed an investigator to verify and review it."

The quality bar is therefore:

    Evidence
      ↓
    Traceability
      ↓
    Security
      ↓
    Reproducibility
      ↓
    Performance
      ↓
    Human Review

not:

    Model
      ↓
    Score
      ↓
    Automatic conclusion
