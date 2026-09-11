# CRIMEKIT — FACE TRACE INVESTIGATOR
# TESTING & EVALUATION SPECIFICATION

**Document:** `TESTING_EVALUATION.md`  
**Subsystem:** Face Trace Investigator  
**Scope:** Unit tests, integration tests, model evaluation, threshold evaluation, end-to-end forensic validation, realtime testing, security testing, performance testing, regression testing, release gates  
**Primary concern:** Prove that Face Trace is technically correct, reproducible, secure, observable, and honest about what its results mean  
**Audience:** QA, ML engineers, backend engineers, forensic engineers, frontend engineers, security, DevOps, investigators, reviewers  
**Status:** Authoritative testing and evaluation specification

---

# 1. PURPOSE

Face Trace Investigator must not be considered complete because:

    the camera connects
    +
    a face is detected
    +
    a similarity score appears

The feature is complete only when the complete chain is tested:

    authorized source
       ↓
    decode
       ↓
    sampling
       ↓
    detection
       ↓
    quality
       ↓
    tracking
       ↓
    embedding
       ↓
    vector retrieval
       ↓
    policy
       ↓
    candidate
       ↓
    sighting
       ↓
    provenance
       ↓
    realtime event
       ↓
    frontend
       ↓
    investigator review

Testing must prove both:

    what works

and:

    what the system correctly refuses to claim.

---

# 2. TESTING PRINCIPLES

The feature must follow these principles:

1. Test evidence integrity separately from AI correctness.
2. Test machine outputs separately from human review.
3. Test security at every sensitive boundary.
4. Test failures, not only happy paths.
5. Test partial processing explicitly.
6. Test reproducibility across processing runs.
7. Test model/policy versioning.
8. Test realtime behavior under overload.
9. Test provenance completeness.
10. Never use demo success as production validation.

---

# 3. TEST LEVELS

The test strategy contains:

    Unit
      ↓
    Component
      ↓
    Integration
      ↓
    Workflow
      ↓
    End-to-End
      ↓
    Security
      ↓
    Performance
      ↓
    Reliability
      ↓
    Model Evaluation
      ↓
    Release Validation

Each level has a different purpose.

---

# 4. UNIT TESTS

Unit tests validate individual deterministic behaviors.

Examples:

    similarity calculation
    distance conversion
    threshold evaluation
    ranking
    deduplication
    timestamp normalization
    bbox validation
    provenance construction
    policy loading

---

# 5. UNIT TEST ISOLATION

Unit tests should not depend on:

    live RTSP
    external model servers
    production databases
    real evidence

Use controlled fixtures.

---

# 6. SIMILARITY UNIT TEST

Given two known vectors:

    v1
    v2

verify expected similarity under the configured metric.

---

# 7. NORMALIZATION UNIT TEST

Where normalized vectors are required:

    verify expected representation

and reject invalid dimensions/values as appropriate.

---

# 8. DIMENSION UNIT TEST

Example:

    reference dimension = D
    candidate dimension = D

Expected:

    compatible

Mismatch:

    explicit failure

Do not allow vector-shape mismatch to reach the similarity operation.

---

# 9. METRIC UNIT TEST

Verify that:

    cosine

is interpreted correctly.

If a vector store returns distance:

    distance → CrimeKit similarity semantics

must be correct.

---

# 10. THRESHOLD UNIT TEST

Test:

    below threshold
    exactly threshold
    above threshold

Verify behavior against the defined inclusive/exclusive policy.

---

# 11. TOP-K UNIT TEST

For a candidate set:

    K = 5

verify no more than 5 results proceed to the downstream stage according to policy.

---

# 12. RANKING UNIT TEST

Given:

    candidate A = higher similarity
    candidate B = lower similarity

Expected:

    A ranks before B

---

# 13. TIE-BREAK UNIT TEST

Equal scores must follow the documented deterministic tie-break policy.

---

# 14. QUALITY UNIT TEST

Test:

    valid quality
    low quality
    missing quality signal
    invalid quality signal

---

# 15. BBOX UNIT TEST

Reject:

    negative dimensions
    out-of-frame invalid boxes
    impossible coordinates

according to implementation policy.

---

# 16. TIMESTAMP UNIT TEST

Verify:

    source timestamp
    processing timestamp

remain distinct.

---

# 17. TRACK UNIT TEST

Verify:

    detections are associated correctly

under controlled fixture sequences.

---

# 18. TRACK TERMINATION TEST

Verify track state transitions on:

    disappearance
    timeout
    stream interruption

according to tracker semantics.

---

# 19. DEDUPLICATION UNIT TEST

Given repeated observations from one track:

    one sighting

according to aggregation policy.

---

# 20. PROVENANCE UNIT TEST

Creating a candidate should generate all required lineage references.

Expected:

    case
    investigation
    processing run
    evidence
    detection
    track where applicable
    model
    policy

---

# 21. POLICY LOADING TEST

Invalid policy configuration must fail clearly.

Examples:

    missing threshold
    invalid metric
    unsupported model
    invalid top-K

---

# 22. POLICY VERSION TEST

Two versions must remain distinguishable.

---

# 23. REPROCESSING UNIT TEST

A new processing run must not overwrite old run metadata.

---

# 24. EVENT IDEMPOTENCY UNIT TEST

Repeated event:

    same event_id

must not create duplicate domain state.

---

# 25. SECURITY UNIT TEST

Unauthorized access to a candidate/provenance/source must be rejected.

---

# 26. COMPONENT TESTS

Component tests validate one subsystem with realistic dependencies.

Examples:

    InsightFace adapter
    detector adapter
    tracker adapter
    vector repository
    provenance repository
    event publisher
    RTSP adapter

---

# 27. INSIGHTFACE ADAPTER TEST

Verify:

    model loads
    detector/recognizer boundary works
    input preprocessing works
    expected embedding shape is returned
    model metadata is propagated

---

# 28. INSIGHTFACE FAILURE TEST

Simulate:

    model file missing
    model initialization failure
    invalid input
    inference exception
    runtime/provider failure

Expected:

    structured failure
    no fabricated embedding

---

# 29. MODEL VERSION TEST

Verify the adapter returns the actual configured:

    model ID
    model version

---

# 30. VECTOR REPOSITORY TEST

Verify:

    insert
    query
    metadata filter
    case scope
    retention filter

---

# 31. VECTOR SECURITY TEST

Verify an authorized query cannot retrieve data outside the allowed scope.

---

# 32. PROVENANCE REPOSITORY TEST

Create:

    evidence
    frame
    detection
    track
    candidate
    sighting

Verify all references resolve.

---

# 33. EVENT PUBLISHER TEST

Verify:

    event schema
    event version
    IDs
    timestamps
    idempotency key

---

# 34. WEBSOCKET COMPONENT TEST

Verify:

    authenticated connection
    authorized subscription
    event delivery
    reconnect handling

---

# 35. RTSP ADAPTER TEST

Use a controlled local test stream rather than a production camera.

Test:

    connect
    decode
    disconnect
    reconnect

---

# 36. VIDEO DECODER TEST

Use deterministic test clips containing:

    zero faces
    one face
    multiple faces
    motion
    occlusion
    varied lighting

---

# 37. INTEGRATION TESTS

Integration tests validate multiple connected CrimeKit components.

Example:

    FastAPI
       ↓
    job/workflow
       ↓
    video worker
       ↓
    InsightFace
       ↓
    PostgreSQL/pgvector
       ↓
    event layer

---

# 38. FILE SEARCH INTEGRATION

Upload/reference a controlled test artifact.

Expected:

    job accepted
    source validated
    processing run created

---

# 39. FILE PROCESSING INTEGRATION

Run a known test video.

Verify:

    decoding
    detections
    tracks
    embeddings
    candidates
    sightings
    provenance

---

# 40. ZERO-MATCH INTEGRATION

Use a video where no qualifying candidate should exist.

Expected:

    successful processing
    zero qualified candidates

Not:

    processing failure

---

# 41. MATCHING INTEGRATION

Use a controlled fixture where a known reference should produce an expected candidate.

Validate:

    retrieval
    score ordering
    policy
    provenance

Do not require a fragile exact floating-point value unless justified.

---

# 42. FALSE-MATCH INTEGRATION

Include visually similar but non-matching faces.

Verify:

    policy behavior
    ranking
    review state

---

# 43. MULTI-FACE INTEGRATION

A frame with multiple faces must create independent detections/tracks/candidates as appropriate.

---

# 44. MULTI-CAMERA INTEGRATION

Process:

    Camera A
    Camera B

Verify source identities remain separate.

---

# 45. CROSS-CAMERA CORRELATION

If implemented:

    source sightings

must remain traceable after cross-camera correlation.

---

# 46. PARTIAL SOURCE FAILURE

Process multiple sources where one fails.

Expected:

    successful sources persist
    failed source marked failed/degraded
    overall result indicates partial coverage

---

# 47. VECTOR FAILURE INTEGRATION

Disable vector service.

Expected:

    matching unavailable/failed

Not:

    zero candidates.

---

# 48. DATABASE FAILURE INTEGRATION

Simulate transient persistence failure.

Expected:

    controlled retry
    no duplicate result
    no false completion

---

# 49. EVENT FAILURE INTEGRATION

Persist candidate successfully, then simulate event failure.

Expected:

    durable candidate remains
    event retries

---

# 50. GRAPH PROJECTION FAILURE

Persist relational result and fail Neo4j projection.

Expected:

    relational result remains authoritative
    graph projection shows pending/failed state if implemented

---

# 51. WORKFLOW TESTS

Workflow tests validate durable long-running behavior.

---

# 52. WORKFLOW START

Verify:

    request
       ↓
    authorization
       ↓
    job
       ↓
    processing run
       ↓
    execution

---

# 53. WORKFLOW COMPLETION

Verify:

    successful processing
       ↓
    result finalization
       ↓
    event
       ↓
    completed job

---

# 54. WORKFLOW RETRY

Inject transient worker failure.

Expected:

    retry according to policy
    no duplicate forensic history

---

# 55. WORKFLOW CANCELLATION

Cancel active file processing.

Verify:

    workers stop
    resources release
    job state becomes cancelled
    partial results retain provenance

---

# 56. WORKFLOW CRASH RECOVERY

Terminate a worker mid-processing.

Verify:

    durable workflow remains recoverable
    no corrupted result
    retry/resume follows defined policy

---

# 57. DUPLICATE REQUEST TEST

Submit the same idempotent request twice.

Expected:

    behavior matches API/job idempotency contract.

---

# 58. LIVE WORKFLOW TEST

Start RTSP processing.

Verify:

    workflow becomes active
    source is connected
    pipeline health is visible

---

# 59. LIVE STOP TEST

Stop active live stream.

Expected:

    decoder closes
    workers stop
    sightings finalize
    source health closes
    workflow completes/stops

---

# 60. LIVE RECONNECT WORKFLOW TEST

Disconnect source.

Expected:

    degraded/reconnecting
       ↓
    retry
       ↓
    live

if recovery succeeds.

---

# 61. REAL-TIME TESTING

Realtime testing validates:

    latency
    throughput
    stability
    frame drops
    queue behavior
    event delivery

---

# 62. FRAME ARRIVAL TEST

Verify the pipeline records source timestamps correctly.

---

# 63. QUEUE BOUND TEST

Overload downstream inference.

Expected:

    queue remains within configured capacity.

---

# 64. FRAME DROP TEST

When overload occurs:

    explicit drop policy

must apply.

Verify drop counts.

---

# 65. BACKPRESSURE TEST

Slow model inference intentionally.

Expected:

    no unbounded RAM growth.

---

# 66. LIVE LATENCY TEST

Measure:

    source frame arrival
       ↓
    detection
       ↓
    embedding
       ↓
    matching
       ↓
    persistence
       ↓
    event
       ↓
    UI

Collect p50/p95 where appropriate.

---

# 67. THROUGHPUT TEST

Measure:

    source FPS
    processed FPS
    effective FPS

---

# 68. GPU LOAD TEST

Measure under representative:

    resolution
    source FPS
    face density
    batch size
    model

---

# 69. GPU MEMORY TEST

Run sustained inference and monitor:

    GPU memory growth
    allocation failures
    worker stability

---

# 70. CPU LOAD TEST

Measure:

    decoding
    preprocessing
    tracking
    persistence

---

# 71. MEMORY LEAK TEST

Run live processing for an extended period.

Expected:

    no unbounded RAM growth.

---

# 72. DECODER SOAK TEST

Run long clips.

Expected:

    no progressive decoder instability.

---

# 73. RTSP SOAK TEST

Run a long-lived controlled RTSP source.

Monitor:

    reconnects
    latency
    memory
    CPU
    GPU
    frame drops

---

# 74. RECONNECT STORM TEST

Repeatedly interrupt a source.

Expected:

    controlled retries
    no worker explosion
    bounded resource consumption.

---

# 75. MULTI-CAMERA LOAD TEST

Run multiple streams at target deployment characteristics.

Measure:

    per-camera latency
    aggregate throughput
    source starvation
    GPU utilization

---

# 76. FAIRNESS TEST

Verify that a noisy source cannot indefinitely starve other sources.

---

# 77. LIVE EVENT RATE TEST

Generate many track updates.

Expected:

    backend remains stable
    event payloads remain bounded
    frontend does not freeze

---

# 78. EVENT COALESCING TEST

Verify high-frequency updates are handled according to the event policy.

---

# 79. WEBSOCKET RECONNECT TEST

Disconnect frontend network.

Reconnect.

Expected:

    snapshot refresh
    event reconciliation
    no duplicate visible sightings

---

# 80. EVENT ORDER TEST

Deliver events out of order in a controlled test.

Verify client handles ordering according to event contract.

---

# 81. DUPLICATE EVENT TEST

Send same event twice.

Expected:

    no duplicate domain state/card.

---

# 82. FILE SAMPLING TEST

Known video:

    total frames = N

Configured sampling policy:

    S

Verify actual sampled count is consistent with policy.

---

# 83. FRAME COVERAGE TEST

Verify UI/API distinguishes:

    sampled frames
    processed frames
    skipped frames

---

# 84. SOURCE FRAME TEST

For every accepted test sighting:

    source frame is retrievable
    frame timestamp is correct
    bbox is valid
    source evidence resolves

---

# 85. PROVENANCE TEST

Candidate lineage:

    candidate
      ↓
    sighting
      ↓
    detection
      ↓
    frame
      ↓
    evidence
      ↓
    processing run
      ↓
    model
      ↓
    policy

must resolve.

---

# 86. PROVENANCE REPAIR TEST

Remove a non-authoritative projection.

Expected:

    controlled rebuild/repair

Do not fabricate missing forensic data.

---

# 87. PROVENANCE ORPHAN TEST

Create an orphan embedding/candidate fixture.

Integrity checker should detect it.

---

# 88. SECURITY TESTING

Security testing must treat biometric data as sensitive.

Test:

    authentication
    authorization
    case isolation
    vector isolation
    frame access
    WebSocket access
    logs
    exports
    retention/deletion

---

# 89. AUTHENTICATION TEST

Unauthenticated matching request:

    denied.

---

# 90. CASE AUTHORIZATION TEST

Authenticated user without case access:

    denied.

---

# 91. INVESTIGATION AUTHORIZATION TEST

User with case access but without investigation access:

    denied if investigation-level restriction exists.

---

# 92. SOURCE AUTHORIZATION TEST

User can access case but not specific restricted source:

    source excluded/denied.

---

# 93. VECTOR AUTHORIZATION TEST

Vector query must enforce:

    authorized scope

before retrieval/exposure.

---

# 94. CROSS-CASE TEST

Attempt:

    Case A reference
       →
    Case B embeddings

Expected:

    denied by default.

---

# 95. PROVENANCE SIDE-CHANNEL TEST

Request restricted source/provenance by guessed ID.

Expected:

    no meaningful unauthorized disclosure.

---

# 96. FRAME ACCESS TEST

Attempt direct source-frame URL without authorization.

Expected:

    denied/expired access.

---

# 97. WEBSOCKET ACCESS TEST

Attempt to subscribe to another case.

Expected:

    denied.

---

# 98. WEBSOCKET TOKEN TEST

Expired/invalid credentials:

    connection rejected.

---

# 99. RTSP SECRET TEST

Inspect:

    frontend bundle
    API responses
    logs
    events
    exception traces

Verify RTSP secrets are absent.

---

# 100. EMBEDDING LEAK TEST

Inspect logs/events/frontend payloads.

Verify raw embeddings are not exposed unintentionally.

---

# 101. SQL/QUERY INJECTION TEST

Test API filters/search parameters.

---

# 102. OBJECT STORAGE ACCESS TEST

Verify direct object access cannot bypass application authorization.

---

# 103. RATE-LIMIT TEST

Submit excessive search/job requests.

Expected:

    controlled throttling.

---

# 104. RESOURCE EXHAUSTION TEST

Attempt:

    huge top-K
    huge concurrent jobs
    oversized input
    excessive live streams

Expected:

    bounded rejection/limiting.

---

# 105. MALICIOUS MEDIA TEST

Use controlled malformed video files.

Expected:

    decoder failure
    no process crash
    no arbitrary file access.

---

# 106. ZIP/BOMB-LIKE INPUT TEST

If archives are accepted elsewhere in the evidence pipeline, ensure extraction limits are enforced upstream.

---

# 107. PATH TRAVERSAL TEST

Source/artifact identifiers must never allow arbitrary filesystem paths.

---

# 108. SSRF TEST

RTSP/source configuration must not permit unauthorized internal network access through arbitrary URLs.

---

# 109. INPUT VALIDATION TEST

Reject unsupported:

    file formats
    malformed metadata
    invalid identifiers
    invalid policy parameters

---

# 110. MODEL EVALUATION

Model evaluation is distinct from software tests.

Software test asks:

    Does the code behave as specified?

Model evaluation asks:

    How well does the model perform under intended conditions?

Both are required.

---

# 111. EVALUATION DATA

Use an approved validation dataset representative of intended deployment conditions.

Include variation in:

    pose
    illumination
    blur
    compression
    face size
    camera quality
    occlusion

only where relevant to the intended use.

---

# 112. NO PRODUCTION EVIDENCE IN TEST DATA

Do not place real case evidence in development/test environments unless explicitly approved.

---

# 113. TEST DATA LABELING

Test datasets should clearly indicate:

    synthetic
    consented
    public-permitted
    controlled evaluation

according to organizational policy.

---

# 114. EVALUATION SPLIT

Keep evaluation data separate from development/tuning data where possible.

Do not tune thresholds repeatedly against the final test set.

---

# 115. IDENTIFICATION TASK DEFINITION

Before evaluation, define whether the system is evaluated as:

    verification
    candidate retrieval
    rank-based search

Do not mix metrics from different task definitions.

---

# 116. VERIFICATION

Verification asks:

    Does this candidate pair represent the same enrolled/reference identity?

Use the metric appropriate to the task.

---

# 117. RETRIEVAL

Retrieval asks:

    Can the correct gallery/reference instance be surfaced among candidates?

Evaluate:

    rank
    recall
    retrieval quality

---

# 118. TOP-K RETRIEVAL EVALUATION

Useful metrics may include:

    Recall@K
    Precision@K

Use metrics appropriate to the dataset/design.

---

# 119. THRESHOLD CURVE

Evaluate performance over a range of thresholds.

Do not choose a threshold from one arbitrary score.

---

# 120. FALSE ACCEPTANCE

Measure unwanted matches under the intended task.

---

# 121. FALSE REJECTION

Measure missed valid matches under the intended task.

---

# 122. OPERATING POINT

Choose operating point based on:

    intended investigative use
    acceptable false-match burden
    acceptable missed-match risk
    human review capacity

---

# 123. THRESHOLD APPROVAL

Threshold selection should have:

    documented dataset
    model/version
    evaluation results
    policy version
    approval/owner

where required.

---

# 124. MODEL VERSION EVALUATION

Every new model version should undergo comparative validation.

---

# 125. MODEL CHANGE GATE

Do not deploy a new model solely because:

    demo looks better

Require evidence from the evaluation process.

---

# 126. PREPROCESSING EVALUATION

Changing preprocessing can alter embeddings.

Re-evaluate materially changed preprocessing.

---

# 127. DETECTOR EVALUATION

Recognition quality can be affected by detector quality.

Evaluate the detector pipeline in realistic conditions.

---

# 128. TRACKER EVALUATION

For video:

    detector association
       ↓
    track consistency

can change candidate aggregation behavior.

Evaluate tracking independently enough to understand its impact.

---

# 129. QUALITY GATE EVALUATION

Measure:

    accepted observations
    rejected observations
    candidate retrieval impact

---

# 130. QUALITY THRESHOLD TRADEOFF

A stricter quality gate may:

    reduce low-quality false candidates

but may also:

    increase missed valid candidates.

Document this tradeoff.

---

# 131. CAMERA-SPECIFIC EVALUATION

Where sources differ significantly, evaluate representative camera classes.

---

# 132. VIDEO-SPECIFIC EVALUATION

Evaluate:

    stationary camera
    moving camera
    crowded scene
    sparse scene
    low-light
    compression-heavy

only as relevant to intended deployment.

---

# 133. LIVE VS FILE EVALUATION

Do not assume live-stream performance equals file processing performance.

Evaluate separately.

---

# 134. LIVE LATENCY EVALUATION

Measure:

    source → event

under realistic stream conditions.

---

# 135. LIVE DROP EVALUATION

Measure candidate impact when frames are intentionally dropped.

---

# 136. PARTIAL COVERAGE EVALUATION

Verify system correctly represents:

    incomplete source coverage.

---

# 137. NEGATIVE CLAIM TEST

Create a case where no matching candidate exists.

Verify language remains:

    "No qualifying candidate found under the configured policy"

and does not become:

    "person was absent."

---

# 138. EXPLAINABILITY TEST

Candidate detail must accurately show:

    similarity
    metric
    source
    time
    model
    policy
    provenance

---

# 139. EXPLANATION CONSISTENCY TEST

UI explanation must match backend structured fields.

---

# 140. SCORE LABEL TEST

Verify:

    similarity

is not displayed as:

    probability
    accuracy
    certainty

---

# 141. HUMAN REVIEW TESTING

Human review workflow must be tested independently.

---

# 142. REVIEW STATE TRANSITION

Example:

    REVIEW_PENDING
       ↓
    UNDER_REVIEW
       ↓
    REVIEWED

Verify allowed transitions.

---

# 143. REVIEW AUDIT TEST

Every review should preserve:

    reviewer
    timestamp
    decision

as required.

---

# 144. REVIEW IMMUTABILITY

Original machine score and source context must not be changed by review.

---

# 145. REVIEW DISAGREEMENT TEST

If multi-reviewer support exists:

    conflicting decisions

must be represented correctly.

---

# 146. FRONTEND TESTING

Frontend tests should cover:

    reference selection
    evidence selection
    job start
    progress
    candidate list
    source frame
    provenance
    review
    realtime updates
    reconnect

---

# 147. REFERENCE UI TEST

Multiple detected faces in reference image:

    user can select intended face
    no silent selection unless product contract says so.

---

# 148. CANDIDATE UI TEST

Candidate card must show:

    machine-generated
    similarity
    source
    time
    review state

---

# 149. PROVENANCE UI TEST

User can navigate:

    candidate → source frame → evidence.

---

# 150. REALTIME UI TEST

New sighting:

    appears without full-page refresh.

---

# 151. UI DUPLICATION TEST

Repeated event:

    no duplicate candidate/sighting card.

---

# 152. UI RECONNECT TEST

Network interruption:

    state recovers after reconnect.

---

# 153. UI AUTHORIZATION TEST

Unauthorized source data never appears in UI state.

---

# 154. ACCESSIBILITY TEST

Critical review actions should support:

    keyboard navigation
    visible focus
    readable contrast
    semantic labels

---

# 155. ERROR UI TEST

Backend errors should become clear operational messages.

Never expose:

    stack trace
    secret
    internal storage path.

---

# 156. SEARCH STATE TEST

UI should distinguish:

    processing
    completed
    partial
    failed
    cancelled
    no results.

---

# 157. PERFORMANCE REGRESSION TEST

Track benchmark values across releases.

Potential metrics:

    embedding latency
    vector latency
    end-to-end latency
    throughput
    memory
    GPU memory

---

# 158. REGRESSION BASELINE

Maintain benchmark baselines by:

    model version
    deployment hardware
    representative source type

---

# 159. PERFORMANCE REGRESSION GATE

A major regression must be reviewed before release.

Do not define a universal number without benchmark context.

---

# 160. LOAD PROFILE

Use realistic:

    frame rate
    resolution
    camera count
    face density
    evidence size

---

# 161. SOAK PROFILE

Run:

    hours of live processing

or another approved duration sufficient to reveal long-term resource problems.

---

# 162. FAILURE INJECTION

Inject controlled failures:

    decoder
    network
    GPU
    model
    database
    vector store
    event bus

---

# 163. CHAOS-LIKE TESTING

For staging/test only, combine failures such as:

    camera disconnect
    worker restart
    event delay

Verify system remains truthful.

---

# 164. NO DATA CORRUPTION

Failure tests must verify:

    no corrupted source evidence
    no duplicate forensic history
    no false successful completion.

---

# 165. BACKUP/RESTORE TEST

Restore test environment.

Verify:

    source references
    candidates
    sightings
    provenance
    reviews

remain consistent.

---

# 166. MIGRATION TEST

Database schema changes must preserve:

    candidate lineage
    model/policy metadata
    review state.

---

# 167. ROLLBACK TEST

Application/model rollback must not erase historical results.

---

# 168. VECTOR INDEX REBUILD TEST

Rebuild vector index in test.

Verify:

    retrieval remains correct
    domain records remain unchanged.

---

# 169. GRAPH REBUILD TEST

Reproject Neo4j from authoritative records.

Verify:

    lineage preserved
    no duplicate relationships.

---

# 170. EVENT REPLAY TEST

Replay stored events.

Expected:

    projections converge correctly
    no duplicate forensic facts.

---

# 171. RETENTION TEST

Simulate expiration.

Verify:

    expired biometric records cannot participate in new searches.

---

# 172. DELETION TEST

Delete/expire an allowed biometric artifact.

Verify:

    vectors
    derived crops
    dependent references

follow policy.

---

# 173. LEGAL-HOLD TEST

If legal hold exists:

    retention must not accidentally purge protected records.

---

# 174. AUDIT TESTING

Verify audit records for:

    search
    source access
    review
    export
    policy/model administration

according to security requirements.

---

# 175. LOG SANITIZATION TEST

Search logs for forbidden patterns:

    embedding arrays
    RTSP password
    source secrets
    raw biometric payloads

Expected:

    none.

---

# 176. SBOM/DEPENDENCY TEST

Use the CrimeKit supply-chain process to identify:

    vulnerable dependencies
    unapproved packages
    runtime mismatches.

---

# 177. MODEL ARTIFACT TEST

Verify deployed model artifacts:

    are the expected version
    are loaded from approved location
    are not unexpectedly replaced.

---

# 178. CONFIGURATION DRIFT TEST

Compare deployed:

    model
    policy
    runtime
    thresholds

against approved configuration.

---

# 179. ENVIRONMENT PARITY TEST

Verify important differences between:

    development
    staging
    production

are known and documented.

---

# 180. RELEASE CANDIDATE TEST

Before production:

    full automated suite
    integration suite
    security suite
    performance smoke
    model validation
    provenance validation

must pass required gates.

---

# 181. RELEASE BLOCKERS

Block release for:

    authorization bypass
    provenance loss
    source evidence mutation
    raw biometric leakage
    duplicate forensic result corruption
    fabricated completion
    unsupported identity claims

---

# 182. ACCEPTABLE WARNINGS

Examples:

    graph projection delayed
    optional thumbnail unavailable
    CPU fallback active

only if the product explicitly represents the degraded condition.

---

# 183. DEMO VALIDATION

Before a demo:

    verify live source
    verify reference
    verify processing
    verify candidates
    verify source frame
    verify provenance
    verify review

using actual test data.

---

# 184. NO FAKE DEMO DATA

Do not manufacture:

    fake FPS
    fake candidate cards
    fake similarity
    fake processing logs

and present them as real system results.

---

# 185. DEMO RESET

After demo:

    clear temporary test data
    close live sources
    release GPU resources
    remove temporary credentials where applicable.

---

# 186. TEST EVIDENCE STORAGE

Automated tests should retain enough artifacts to diagnose failures:

    logs
    metrics
    job IDs
    fixture IDs
    screenshots where useful

Do not retain sensitive raw media unnecessarily.

---

# 187. TEST REPORT

A release test report should include:

    build/version
    model/version
    policy/version
    environment
    test suite
    passed
    failed
    skipped
    benchmark summary
    known limitations

---

# 188. MODEL EVALUATION REPORT

Should include:

    dataset description
    task definition
    model/version
    preprocessing
    detector
    tracker where relevant
    metrics
    threshold
    limitations

---

# 189. NO OVERCLAIMING

If evaluation was conducted on:

    controlled test videos

do not claim:

    "works reliably in all CCTV environments."

---

# 190. KNOWN LIMITATIONS

Release notes should explicitly state known limits such as:

    low-light performance
    small faces
    heavy occlusion
    compression
    sampling coverage
    unsupported codecs

only where actually observed/tested.

---

# 191. TEST OWNERSHIP

Each critical domain should have an owner:

    backend
    ML
    realtime
    security
    frontend
    provenance
    reporting

---

# 192. TEST NAMING

Use stable, searchable names such as:

    test_candidate_provenance
    test_cross_case_denied
    test_rtsp_reconnect
    test_vector_failure_not_zero_match

---

# 193. CI TEST LAYERS

Recommended:

    pull request:
        unit + fast integration

    merge:
        full integration + security smoke

    release:
        end-to-end + model + performance + provenance

Exact CI policy follows CrimeKit governance.

---

# 194. TEST PARALLELIZATION

Parallelize safe tests.

Do not allow concurrent tests to share mutable biometric state unexpectedly.

---

# 195. TEST ISOLATION

Each test should use:

    isolated case IDs
    isolated investigations
    isolated vector scope

where relevant.

---

# 196. DETERMINISTIC FIXTURES

Prefer deterministic:

    media
    timestamps
    reference selection
    policy

for software tests.

---

# 197. MODEL NON-DETERMINISM

Where inference may have hardware/runtime nondeterminism:

    test tolerances

should reflect that.

Do not weaken assertions unnecessarily.

---

# 198. RETRIEVAL DETERMINISM

For fixed input/configuration:

    candidate ordering

should be stable enough for tests.

---

# 199. TEST DATA VERSIONING

Record test fixture version when results are benchmarked.

---

# 200. EVALUATION DRIFT

Re-run model evaluation when:

    model changes
    preprocessing changes
    detector changes materially
    source population/conditions change materially
    policy changes materially

---

# 201. THRESHOLD RE-EVALUATION

Do not reuse a threshold automatically after a model change.

---

# 202. CAMERA ONBOARDING GATE

A new camera class should pass:

    media compatibility
    frame-rate test
    face-size test
    latency test
    source-time validation

where applicable.

---

# 203. NEW GPU GATE

Before moving to new GPU hardware:

    model load
    memory
    throughput
    latency

must be benchmarked.

---

# 204. NEW RUNTIME GATE

A new ONNX Runtime/CUDA/TensorRT stack should pass:

    inference correctness
    performance
    memory stability

tests.

---

# 205. SECURITY REGRESSION

Security tests must run after meaningful changes to:

    API
    vector scope
    provenance
    WebSocket
    object access.

---

# 206. PROVENANCE REGRESSION

Every release must retain:

    candidate → source

traceability.

---

# 207. REVIEW REGRESSION

Machine results must remain distinct from human review.

---

# 208. NEGATIVE TEST REGRESSION

Ensure no release introduces claims such as:

    "confirmed suspect"

from raw matching output.

---

# 209. RELEASE ACCEPTANCE MATRIX

| Area | Required validation |
|---|---|
| Source | Authorized and immutable |
| Decode | Correct timestamps/errors |
| Sampling | Recorded and truthful |
| Detection | Correct outputs |
| Quality | Explicit policy |
| Tracking | Stable semantics |
| Embedding | Model-compatible |
| Vector search | Scoped/authorized |
| Matching | Versioned metric/policy |
| Candidate | Provenance complete |
| Sighting | Aggregation correct |
| Realtime | Events delivered |
| UI | Review workflow works |
| Security | No bypass/leak |
| Performance | Target benchmark |
| Reliability | Failure/recovery |
| Reporting | Source traceability |

---

# 210. DEFINITION OF DONE — SOFTWARE

[ ] Unit tests pass.

[ ] Integration tests pass.

[ ] Workflow tests pass.

[ ] Realtime tests pass.

[ ] Security tests pass.

[ ] Provenance tests pass.

[ ] Frontend tests pass.

[ ] Regression suite passes.

---

# 211. DEFINITION OF DONE — MODEL

[ ] Model/version recorded.

[ ] Embedding compatibility verified.

[ ] Evaluation dataset documented.

[ ] Retrieval/verification task defined.

[ ] Threshold evaluated.

[ ] False-match behavior evaluated.

[ ] Miss behavior evaluated.

[ ] Known limitations documented.

---

# 212. DEFINITION OF DONE — PRODUCTION

[ ] Source authorization works.

[ ] Evidence immutability preserved.

[ ] Model deployment approved.

[ ] Matching policy approved.

[ ] Realtime capacity benchmarked.

[ ] Monitoring dashboards active.

[ ] Security logging active.

[ ] Retention policy implemented.

[ ] Backup/restore tested.

[ ] Incident procedures defined.

---

# 213. FINAL TESTING PRINCIPLE

Face Trace Investigator is trustworthy only when the system can demonstrate all of the following:

    The source was authorized.

    The evidence was preserved.

    The processing actually happened.

    The selected model is known.

    The matching policy is known.

    The candidate can be traced back to a source frame.

    Failures are not represented as zero matches.

    Partial processing is visible.

    Reprocessing does not erase history.

    The vector store respects case scope.

    Realtime events do not become fake evidence.

    Human review remains separate from machine output.

    Performance claims are measured.

    Evaluation claims are supported by actual test data.

---

# 214. FINAL RULE

A green demo is not a passing forensic system.

A passing CrimeKit Face Trace Investigator must demonstrate:

    correctness
    provenance
    security
    reproducibility
    operational resilience
    measured performance
    evaluated matching behavior
    honest investigator-facing language

The test system must prove not only that CrimeKit can find candidates, but that CrimeKit knows exactly what it did, what it did not do, and how the investigator can verify the result.
