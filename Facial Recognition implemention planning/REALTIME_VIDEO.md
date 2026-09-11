# CRIMEKIT — FACE TRACE INVESTIGATOR
# REAL-TIME VIDEO PROCESSING SPECIFICATION

**Document:** `REALTIME_VIDEO.md`  
**Subsystem:** Face Trace Investigator  
**Scope:** MP4/video files + RTSP/CCTV live streams  
**Primary concern:** Real-time, bounded, observable, failure-tolerant face-trace processing  
**Audience:** Forensic engineers, backend engineers, ML engineers, infrastructure, frontend, QA, security  
**Status:** Authoritative implementation specification

---

# 1. PURPOSE

This document defines how CrimeKit processes video evidence and live CCTV streams for Face Trace Investigator.

The objective is not merely:

    decode video
    detect faces
    compare embeddings

The objective is:

    Authorized Evidence
          ↓
    Controlled Ingestion
          ↓
    Video Decode
          ↓
    Frame Scheduling
          ↓
    Face Detection
          ↓
    Quality Filtering
          ↓
    Multi-Object Face Tracking
          ↓
    Face Embedding
          ↓
    Similarity Search
          ↓
    Candidate Observation
          ↓
    Sighting Aggregation
          ↓
    Provenance
          ↓
    Real-Time Events
          ↓
    Investigator UI

The implementation must remain forensic, resource-bounded, observable, and explainable.

---

# 2. SUPPORTED INPUT MODES

Face Trace Investigator must support two distinct processing modes.

## 2.1 FILE MODE

Examples:

    MP4
    MOV
    MKV
    AVI

Primary workflow:

    stored evidence
       ↓
    deterministic processing
       ↓
    archived forensic results

## 2.2 LIVE MODE

Examples:

    RTSP CCTV stream
    approved network camera
    authorized live source

Primary workflow:

    live stream
       ↓
    bounded real-time pipeline
       ↓
    continuous sightings/events

These modes share inference and matching components but do not share identical lifecycle semantics.

---

# 3. NON-GOALS

This specification does not define:

- unauthorized surveillance
- bypassing camera authentication
- hidden camera discovery
- facial identification from unrestricted public sources
- automatic guilt determination
- autonomous police decision-making
- destructive evidence modification

CrimeKit operates only on authorized sources.

---

# 4. CORE REAL-TIME PRINCIPLE

Real-time processing must be bounded.

Never allow:

    incoming frames
         ↓
    unbounded memory queue

The system must use explicit:

    queue limits
    frame policies
    backpressure
    cancellation
    worker limits

---

# 5. FILE PROCESSING PRINCIPLE

Forensic file processing should favor reproducibility over pretending to be real-time.

The system should make explicit:

    sampled frames
    processing rate
    skipped frames
    model versions
    processing run

Do not claim:

    "entire video analyzed"

unless the actual processing policy supports that statement.

---

# 6. LIVE PROCESSING PRINCIPLE

Live processing should favor bounded latency.

When the system cannot process every incoming frame:

    do not allow backlog to grow indefinitely.

Prefer controlled frame dropping/sampling over unlimited queue growth.

---

# 7. INPUT VALIDATION

Before processing a file:

    validate file identity
    validate authorization
    validate media accessibility
    validate decoder compatibility
    validate metadata where available

Before connecting to RTSP:

    validate source authorization
    validate stream configuration
    validate credentials
    validate network policy

---

# 8. EVIDENCE BOUNDARY

For file evidence:

    Evidence → Artifact → Video Processing Run

For live evidence:

    Camera/Stream Source → Live Processing Run

Do not treat a transient live buffer as a replacement for authoritative evidence storage.

---

# 9. SOURCE IDENTIFICATION

Each processing job must identify:

    case_id
    investigation_id
    source_id
    artifact_id where applicable
    processing_run_id

---

# 10. SOURCE ACCESS

Source access must use existing CrimeKit evidence/storage abstractions.

Do not implement an independent evidence repository inside Face Trace.

---

# 11. MP4 INGESTION

For a video file:

    source artifact
       ↓
    secure read
       ↓
    media metadata
       ↓
    decoding

Metadata should include when available:

    duration
    frame rate
    width
    height
    codec
    stream count
    audio/video stream identity

---

# 12. RTSP INGESTION

For an RTSP source:

    authorized URI/config
       ↓
    connection
       ↓
    demux/decode
       ↓
    frame pipeline

Do not expose RTSP credentials to frontend clients.

---

# 13. RTSP CREDENTIAL SECURITY

Credentials must remain server-side.

Never:

    send RTSP username/password to React
    include credentials in event payloads
    store secrets in logs
    place secrets in source code

---

# 14. LIVE SOURCE REGISTRY

Live sources should be represented by an internal source identity.

Example:

    CAM-001

The identifier should not expose:

    password
    secret URI
    private infrastructure details

---

# 15. STREAM HEALTH

A live source should expose an operational state such as:

    CONNECTING
    LIVE
    DEGRADED
    RECONNECTING
    OFFLINE

Exact state names may follow platform conventions.

---

# 16. CONNECTION ESTABLISHMENT

RTSP startup should:

    authenticate
    connect
    negotiate
    begin decoding
    publish source health

A stream is not considered healthy merely because the TCP/RTSP connection exists.

Frames must actually arrive.

---

# 17. CONNECTION TIMEOUT

Use bounded connect/read timeouts.

Do not leave a worker blocked indefinitely.

---

# 18. RECONNECT POLICY

Temporary live-stream failures should use controlled reconnect attempts.

Recommended structure:

    disconnect
       ↓
    mark degraded
       ↓
    backoff
       ↓
    reconnect
       ↓
    validate frame flow
       ↓
    resume

---

# 19. EXPONENTIAL BACKOFF

Reconnect timing should prevent an outage from causing:

    reconnect storm

Use bounded backoff with jitter where appropriate.

---

# 20. RECONNECT LIMIT

Retry policy must define:

    max delay
    optional attempt limit
    permanent-failure behavior

Do not retry forever without an operational policy.

---

# 21. LIVE GAP PROVENANCE

If a stream disconnects:

    last source timestamp
    disconnect time
    reconnect time

should be represented where operationally required.

Do not fabricate observations during the gap.

---

# 22. VIDEO DECODER

Decoder selection should be compatible with the approved deployment environment.

Potential implementation tools include:

    FFmpeg
    OpenCV
    hardware-accelerated decode

Use the implementation already approved for CrimeKit where one exists.

---

# 23. DECODER RESPONSIBILITY

Decoder responsibilities:

    read compressed media
    decode frames
    expose timestamps
    report errors

Decoder should not own:

    face matching
    investigator state
    review decisions

---

# 24. DECODE PIPELINE

Conceptual:

    source
      ↓
    demuxer
      ↓
    decoder
      ↓
    timestamped frame
      ↓
    frame scheduler

---

# 25. FRAME OBJECT

A normalized internal frame should contain, as applicable:

    source_id
    artifact_id
    processing_run_id
    frame_number
    source_timestamp
    image dimensions
    frame payload/reference

Avoid attaching excessive derived data to every frame object.

---

# 26. FRAME MEMORY POLICY

Do not copy large frames unnecessarily.

Use:

    bounded buffers
    reusable memory
    explicit ownership

where practical.

---

# 27. FRAME LIFETIME

A frame should remain in memory only as long as required by downstream processing.

After completion:

    release/recycle

Do not keep the entire video in RAM.

---

# 28. FRAME SAMPLING

Sampling is a first-class processing policy.

Examples:

    every N frames
    target FPS
    adaptive sampling
    keyframe-oriented sampling

The selected policy must be recorded in the Processing Run.

---

# 29. FILE MODE SAMPLING

For stored video, a sampling profile may be:

    1 FPS
    2 FPS
    5 FPS
    every Nth frame

Actual rate must be configurable by the processing profile.

---

# 30. LIVE MODE SAMPLING

For live CCTV:

    process every frame

may be unnecessary.

A controlled target rate may be used to achieve:

    predictable latency
    bounded GPU load

---

# 31. ADAPTIVE SAMPLING

Adaptive sampling may increase processing around:

    active faces
    movement
    scene changes

Only implement this if explicitly supported and tested.

Do not describe a fixed-rate system as adaptive.

---

# 32. FRAME-DROP POLICY

When processing capacity is lower than source rate, define a frame-drop policy.

Potential policies:

    DROP_OLDEST
    DROP_NEWEST
    SAMPLE_LATEST

For live systems, a latest-frame policy can favor low latency.

Choose one deliberately and document it.

---

# 33. FORENSIC FILE DROPS

For deterministic evidence processing, accidental frame drops are different from intentional sampling.

Record:

    intended sampling policy
    actual processing statistics

---

# 34. BACKPRESSURE

Pipeline stages must have bounded queues.

Example:

    decode queue = 8
    detection queue = 8
    tracking queue = 16

Numbers are examples only.

Do not copy these values blindly into production.

---

# 35. QUEUE OWNERSHIP

Each queue must have:

    producer
    consumer
    capacity
    overflow policy

Avoid invisible queues inside multiple libraries.

---

# 36. QUEUE METRICS

Track:

    queue depth
    queue wait time
    drops
    blocked producers
    consumer throughput

---

# 37. PIPELINE STAGES

Recommended separation:

    Ingest
       ↓
    Decode
       ↓
    Schedule
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

---

# 38. STAGE ISOLATION

Do not place all processing inside:

    one giant function

Each stage should have a clear responsibility.

---

# 39. STAGE FAILURE

A failure in one frame should not necessarily terminate the entire video job.

Classify errors:

    frame-level
    segment-level
    stream-level
    job-level

---

# 40. FRAME-LEVEL FAILURE

Example:

    corrupted frame

Expected:

    log/report controlled error
    skip according to policy
    continue if safe

---

# 41. SEGMENT-LEVEL FAILURE

Example:

    decoder cannot read a section

Expected:

    record affected interval
    continue if recovery is possible

---

# 42. JOB-LEVEL FAILURE

Example:

    evidence cannot be accessed

Expected:

    fail job clearly

Do not return:

    0 faces found

when the source could not be processed.

---

# 43. DETECTION STAGE

Input:

    timestamped frame

Output:

    zero or more FaceDetection records

Each detection must carry provenance.

---

# 44. DETECTOR BOUNDARY

The detector must remain separate from:

    recognition model

The detector answers:

    where are faces?

The recognition model answers:

    how similar are face representations?

---

# 45. DETECTOR PERFORMANCE

Face detection should support:

    batching where appropriate
    GPU acceleration
    configurable resolution
    controlled thresholds

Do not degrade source evidence resolution destructively.

---

# 46. DETECTOR OUTPUT

Typical output:

    bbox
    detector_score
    optional keypoints

Exact output follows selected detector.

---

# 47. QUALITY FILTER

Quality gate occurs after detection and before expensive recognition where practical.

Conceptual:

    Detection
       ↓
    Quality
       ↓
    Embedding

---

# 48. QUALITY SIGNALS

Possible quality indicators:

    face size
    blur
    pose
    illumination
    occlusion
    crop quality

Use only signals actually implemented.

---

# 49. QUALITY POLICY

Quality thresholds must be configuration-driven.

Avoid hard-coded magic values scattered across code.

---

# 50. QUALITY REJECTION

A rejected detection may still be recorded as a machine observation when required for forensic completeness.

Do not confuse:

    rejected for recognition

with:

    no face detected

---

# 51. TRACKING

Tracking connects face detections across frames.

Conceptual:

    detection_t1
    detection_t2
    detection_t3
         ↓
      Track-7

---

# 52. TRACKER RESPONSIBILITY

Tracker should:

    associate detections over time
    manage track lifecycle
    provide track IDs

Tracker should not decide identity.

---

# 53. TRACKER AND IDENTITY

Never interpret:

    same track ID

as:

    confirmed same person

A track is a visual association.

---

# 54. TRACKER CONFIGURATION

Record:

    tracker name
    version
    relevant configuration

in the Processing Run.

---

# 55. TRACK TERMINATION

Tracks may end due to:

    disappearance
    scene change
    timeout
    stream interruption

The reason may be preserved where useful.

---

# 56. STREAM INTERRUPTION AND TRACKS

During a camera reconnect:

    old tracks should not silently continue

unless the tracker explicitly supports safe continuation.

---

# 57. FACE EMBEDDING STAGE

Only eligible detections/tracks should proceed to recognition according to the configured pipeline.

Embedding stage:

    face crop
       ↓
    recognition model
       ↓
    normalized embedding

---

# 58. INSIGHTFACE BOUNDARY

The implementation should use the approved InsightFace runtime/provider adapter.

Do not tie the entire CrimeKit backend directly to a single vendor SDK.

Preferred:

    FaceEmbeddingProvider
         ↓
    InsightFaceProvider

---

# 59. MODEL CONTEXT

Every embedding must reference the model context described by `INSIGHTFACE.md`.

At minimum retain:

    provider
    model ID
    version
    embedding dimension
    preprocessing version

---

# 60. EMBEDDING NORMALIZATION

Where the selected provider returns normalized embeddings, preserve the provider behavior and do not introduce unnecessary repeated transformations.

---

# 61. GPU WORKER

GPU inference should be isolated from CPU-heavy orchestration.

Conceptual:

    CPU
      ↓
    frame preparation
      ↓
    GPU
      ↓
    inference
      ↓
    CPU
      ↓
    matching/persistence

---

# 62. GPU MEMORY

Batch sizes must be bounded.

Do not allow incoming workload to increase GPU batch size without limit.

---

# 63. CUDA FAILURE

If GPU execution fails:

    detect failure
    mark worker unhealthy
    avoid corrupt output
    apply configured recovery/fallback policy

Do not silently continue with a mixed runtime without recording it.

---

# 64. CPU FALLBACK

CPU fallback may be allowed only if explicitly supported by the deployment design.

If used, record the actual execution provider.

---

# 65. GPU WORKER CONCURRENCY

Do not start unlimited inference workers on one GPU.

Capacity must be based on:

    model memory
    frame size
    batch size
    expected latency

---

# 66. MODEL WARMUP

Long-lived GPU workers may warm up the model before processing production workload.

Warmup should not be confused with actual evidence processing.

---

# 67. MODEL INITIALIZATION

Model initialization failures must fail worker startup clearly.

Do not start a worker that cannot produce valid embeddings.

---

# 68. MATCHING STAGE

Embedding comparison:

    reference embedding
          +
    candidate embedding
          ↓
    similarity

---

# 69. SEARCH SCOPE

Search only within the investigator's authorized evidence scope.

Do not search:

    all cases
    all users
    hidden tenant data

unless explicitly authorized by policy.

---

# 70. VECTOR SEARCH

pgvector may provide candidate retrieval.

Typical path:

    embedding
       ↓
    vector index
       ↓
    top-K candidates
       ↓
    policy filtering
       ↓
    sightings

---

# 71. VECTOR RESULT PROVENANCE

Every retrieved candidate must remain tied to its:

    embedding
    source observation
    processing run

---

# 72. TOP-K

Top-K is a retrieval configuration, not proof.

Do not treat:

    rank #1

as:

    confirmed identity.

---

# 73. SIMILARITY THRESHOLD

Similarity thresholds must come from the matching policy.

Do not hard-code:

    0.8
    0.9
    0.95

without an evaluated policy.

---

# 74. CROSS-CAMERA MATCHING

A candidate can connect observations from different cameras only when the investigation scope permits cross-source matching.

Each observation retains:

    original camera/source

---

# 75. CROSS-CASE MATCHING

Cross-case matching must be explicitly authorized.

Default:

    deny

Do not create cross-case vector retrieval merely because pgvector makes it technically possible.

---

# 76. REAL-TIME CANDIDATE GENERATION

For live mode:

    frame
      ↓
    detection
      ↓
    tracking
      ↓
    embedding
      ↓
    match
      ↓
    candidate
      ↓
    event

The event should reference an authoritative persisted/identified domain record where appropriate.

---

# 77. CANDIDATE DEDUPLICATION

Do not emit:

    100 duplicate alerts

for 100 frames belonging to one track.

Use sighting aggregation.

---

# 78. SIGHTING AGGREGATION

Conceptual:

    Track-7
       ↓
    candidate observations
       ↓
    one Face Sighting

The sighting may update as additional frames arrive.

---

# 79. SIGHTING UPDATE

Example:

    SIGHTING-17
    first_seen = 14:21:03
    last_seen = 14:21:08
    observation_count = 6

The UI can show the sighting as continuously updating.

---

# 80. BEST FRAME

A sighting may retain a best observation based on configured evidence/quality criteria.

Do not use an arbitrary latest frame if a better source observation exists.

---

# 81. LIVE EVENT MODEL

Possible events:

    face_detection.created
    face_track.updated
    face_candidate.created
    face_sighting.created
    face_sighting.updated
    processing.progress
    processing.health
    processing.failed

Use existing CrimeKit event conventions where available.

---

# 82. EVENT DESIGN

Event payload should contain identifiers and concise state.

Avoid embedding:

    raw image bytes
    raw embedding vectors
    credentials

---

# 83. WEBSOCKET DELIVERY

React can subscribe to authorized investigation/job channels.

Conceptual:

    Backend Event Bus
       ↓
    WebSocket Gateway
       ↓
    Investigator UI

---

# 84. WEBSOCKET AUTHORIZATION

Authorization must happen before subscribing.

Do not expose:

    /ws/all-cases

type uncontrolled subscription.

---

# 85. WEBSOCKET CASE ISOLATION

Every event must be filtered by:

    user permissions
    case membership
    investigation scope

---

# 86. EVENT ORDERING

Events should contain enough metadata to allow clients to handle ordering issues.

Possible fields:

    event_id
    sequence
    occurred_at

Follow the established CrimeKit event contract.

---

# 87. EVENT DUPLICATION

WebSocket delivery may repeat messages.

Frontend handlers should be idempotent by:

    event_id

or another stable event key.

---

# 88. EVENT RECONNECT

When a client reconnects:

    do not assume it received every event.

Use a state refresh/snapshot mechanism where appropriate.

---

# 89. LIVE UI CONSISTENCY

Recommended client behavior:

    initial API snapshot
       ↓
    subscribe realtime
       ↓
    merge events
       ↓
    refresh on detected gap

---

# 90. PROGRESS FOR FILES

For file jobs, progress should reflect:

    frames read
    frames processed
    estimated total where available
    sightings found

Do not fabricate precise percentages when total work is unknown.

---

# 91. LIVE PROGRESS

For live streams there may be no finite percentage.

Prefer:

    FPS
    processing latency
    queue depth
    detections
    active tracks
    sightings
    health state

---

# 92. REAL-TIME LATENCY

Measure:

    frame arrival time
    decode completion
    detection completion
    embedding completion
    matching completion
    persistence
    event publication

---

# 93. END-TO-END LATENCY

Primary live metric:

    source frame available
       ↓
    investigator UI receives update

Measure this explicitly.

---

# 94. LATENCY TARGETS

Define target SLOs by deployment capacity.

Do not promise a universal millisecond number without benchmarking the actual model, GPU, resolution, camera count, and network.

---

# 95. THROUGHPUT

Track:

    source FPS
    processed FPS
    dropped FPS
    effective FPS

Example:

    source = 25 FPS
    processed = 8 FPS

This is materially different from:

    analyzed at 25 FPS

---

# 96. RESOURCE METRICS

Collect:

    CPU
    RAM
    GPU utilization
    GPU memory
    decode time
    detection time
    embedding time
    matching time
    queue depth

---

# 97. HEALTH METRICS

Useful counters:

    frames_received
    frames_processed
    frames_dropped
    decode_errors
    detections
    quality_rejections
    embeddings
    candidates
    sightings
    reconnects

---

# 98. LOGGING

Logs should use stable IDs:

    case_id
    investigation_id
    source_id
    processing_run_id
    job_id

Do not log sensitive image/vector contents.

---

# 99. STRUCTURED LOGGING

Prefer structured logs:

    level
    timestamp
    event
    IDs
    duration
    error_code

This supports incident investigation.

---

# 100. TRACE CONTEXT

Distributed trace context should connect:

    API request
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

# 101. LIVE RESOURCE ISOLATION

Do not allow one noisy CCTV source to consume all workers.

Use per-source or per-job limits where required.

---

# 102. FAIR SCHEDULING

With multiple sources:

    CAM-001
    CAM-002
    CAM-003

the scheduler should avoid permanent starvation of one source.

---

# 103. GPU SCHEDULING

GPU workload may be shared through:

    bounded batches
    worker pools
    controlled concurrency

Do not queue unlimited GPU jobs.

---

# 104. CPU/GPU BALANCE

Monitor whether bottleneck is:

    decoding
    preprocessing
    detection
    embedding
    vector search
    persistence

Optimize the actual bottleneck, not assumptions.

---

# 105. IMAGE RESOLUTION

Do not blindly downscale all input video.

Choose a processing resolution appropriate to:

    detector performance
    face size
    GPU capacity
    evidence requirements

---

# 106. SOURCE PRESERVATION VS INFERENCE RESOLUTION

Inference may use a resized image.

The source evidence remains unchanged.

Provenance must connect:

    inference frame
       ↓
    original source frame

---

# 107. CROP CONTEXT

Face crops used for recognition must preserve enough margin according to the selected provider/preprocessing configuration.

The crop is derived data.

---

# 108. ZERO-FACE FRAME

A valid frame may have:

    zero detections

This is normal.

Do not mark the job failed.

---

# 109. MULTIPLE-FACE FRAME

A frame can produce:

    face A
    face B
    face C

Each detection needs a distinct identity within the frame.

---

# 110. MULTIPLE TRACKS

A scene may produce:

    Track-1
    Track-2
    Track-3

Track IDs must remain separate.

---

# 111. OCCLUSION

Tracking may survive partial occlusion according to tracker behavior.

Do not invent continuity when the tracker loses the subject.

---

# 112. MOTION BLUR

Quality gating should reduce low-quality embeddings.

A low-quality detection may remain a recorded machine observation.

---

# 113. CAMERA MOTION

Large camera motion can degrade tracking.

The system should expose degraded quality/track behavior rather than creating false confidence.

---

# 114. SCENE CHANGES

A hard scene change may require:

    reset/reinitialize tracker

depending on implementation.

---

# 115. MULTI-CAMERA NORMALIZATION

Every camera has its own:

    source ID
    time context
    processing run/stream context

Do not merge camera-local identities automatically.

---

# 116. CAMERA TIMESTAMP

Preserve camera/source timestamps when available.

Also retain processing timestamps separately.

---

# 117. CLOCK SKEW

If multiple cameras have unsynchronized clocks:

    preserve source timestamps
    avoid pretending they are perfectly synchronized

Cross-camera timeline logic must be explicit about time assumptions.

---

# 118. LIVE EVIDENCE RECORDING

If live findings need long-term forensic use, the product should retain authorized source evidence according to the broader CrimeKit evidence policy.

Do not treat WebSocket events as the permanent evidence record.

---

# 119. EVENT IS NOT EVIDENCE

Important rule:

    WebSocket event ≠ source evidence

The event communicates a machine observation.

Source evidence remains authoritative.

---

# 120. BUFFER POLICY

Live processing may keep only a bounded rolling buffer.

Example uses:

    recent context
    source frame recovery
    temporary decoding

A rolling buffer must have explicit retention semantics.

---

# 121. BUFFER SECURITY

Temporary live buffers must:

    be access-controlled
    avoid unnecessary persistence
    avoid unencrypted disk spill unless approved

---

# 122. MEMORY PRESSURE

When memory pressure occurs:

    drop according to policy
    reduce workload if supported
    mark degraded state

Do not allow uncontrolled OOM behavior.

---

# 123. OOM PROTECTION

Workers should be restartable without corrupting persistent forensic results.

---

# 124. WORKER CRASH

On crash:

    mark work interrupted
    preserve durable results
    restart/recover according to workflow policy

Do not claim successful completion.

---

# 125. JOB RESUME

File processing may support resumability where designed.

Resume must not cause duplicate sightings without idempotency handling.

---

# 126. LIVE WORKER RESTART

A restarted live worker should create a clear processing continuation boundary where required.

---

# 127. IDENTITY ACROSS RESTART

Do not assume tracker IDs remain stable across a worker restart.

Preserve the restart boundary.

---

# 128. SIGHTING MERGE ACROSS RESTART

Merging observations across worker restarts requires explicit safe semantics.

Do not automatically stitch two tracks simply because timestamps are close.

---

# 129. FILE SEEKING

For stored video, seeking may be used for:

    source-frame recovery
    precise extraction

Record exact source context.

---

# 130. FRAME EXTRACTION FOR UI

When investigator requests a frame:

    locate source
    seek/extract
    verify context
    apply non-destructive overlay if requested

---

# 131. SOURCE FRAME ENDPOINT

Potential pattern:

    GET /face-sightings/{id}/source-frame

Response should be authorized and traceable to the source artifact.

Exact path follows backend conventions.

---

# 132. IMAGE DELIVERY

Use secure, short-lived access mechanisms where appropriate.

Do not expose permanent public object-storage URLs for sensitive evidence.

---

# 133. THUMBNAILS

Generate thumbnails as derived display artifacts.

Preserve their lineage.

---

# 134. VIDEO SEEK PERFORMANCE

For long videos, source-frame retrieval should avoid decoding the entire video when possible.

Use decoder/index capabilities where available.

---

# 135. RANDOM ACCESS LIMITATION

Some codecs/container structures make exact seeking approximate.

The system should preserve actual extracted frame context and avoid falsely claiming frame-perfect access when it is not.

---

# 136. FILE COMPLETION

On completion:

    finalize statistics
    finalize sightings
    persist provenance
    publish completion event

---

# 137. LIVE CONTINUOUS OPERATION

For live mode:

    process continuously
    aggregate sightings
    publish updates
    maintain health

There is no natural "100%" completion.

---

# 138. LIVE STOP

When investigator stops the stream job:

    stop ingestion
    drain/cancel safely
    finalize current sightings
    persist final state
    close connection

---

# 139. CANCELLATION

Cancellation should be cooperative.

Stages should observe cancellation signals and release resources.

---

# 140. IDEMPOTENCY

Starting the same file processing request twice must follow explicit idempotency policy.

Do not silently create duplicated forensic records when a request is retried.

---

# 141. FILE JOB IDENTITY

Stable:

    job_id
    processing_run_id

must distinguish separate processing executions.

---

# 142. EVENT IDEMPOTENCY

Duplicate events must not create:

    duplicate sightings
    duplicate reviews
    duplicate graph records

---

# 143. PERSISTENCE ORDER

Recommended conceptual order:

    source context
       ↓
    processing run
       ↓
    detection/track/candidate
       ↓
    sighting
       ↓
    event

Actual transaction boundaries depend on implementation.

---

# 144. DATABASE WRITE PRESSURE

Do not write one heavy transaction for every video frame when unnecessary.

Use controlled batching while preserving forensic record semantics.

---

# 145. FRAME-LEVEL VS SIGHTING-LEVEL PERSISTENCE

Not every internal frame needs to become a permanent database row.

Persist according to the forensic retention design.

But every retained candidate/sighting must retain sufficient provenance.

---

# 146. TEMPORARY PROCESSING DATA

Intermediate tensors/crops may be ephemeral.

Their retention must be intentional.

---

# 147. VECTOR INSERTION

Only insert embeddings into the approved vector store according to retention/security policy.

Do not permanently store every video-frame embedding by default without a documented need.

---

# 148. VECTOR SEARCH PRIVACY

Vector search must respect:

    case scope
    authorization
    retention

---

# 149. SEARCH CACHING

Avoid caching sensitive biometric search results in shared/global caches.

---

# 150. LIVE CACHING

Short-lived per-investigation caches may be used when approved.

Cache keys must contain the appropriate scope.

---

# 151. CACHE INVALIDATION

Changes to:

    access
    retention
    evidence availability

must not leave stale unauthorized cache results accessible.

---

# 152. ERROR TAXONOMY

Recommended categories:

    INPUT_INVALID
    SOURCE_UNAVAILABLE
    DECODER_ERROR
    MODEL_UNAVAILABLE
    GPU_ERROR
    MATCHING_ERROR
    PERSISTENCE_ERROR
    EVENT_ERROR
    AUTHORIZATION_ERROR
    CANCELLED

Actual codes follow backend conventions.

---

# 153. ERROR VISIBILITY

Frontend should show investigators useful operational status.

Do not expose internal stack traces or secrets.

---

# 154. FAIL-CLOSED SECURITY

If authorization cannot be established:

    do not process source.

---

# 155. FAIL-SAFE FORENSICS

If result integrity cannot be guaranteed:

    do not promote result as trusted forensic finding.

---

# 156. PIPELINE HEALTH STATE

A processing run can be:

    HEALTHY
    DEGRADED
    FAILED

where supported.

---

# 157. DEGRADED STATE EXAMPLES

Examples:

    GPU unavailable → CPU fallback
    source FPS > processing FPS
    frame drops increasing
    detector latency high

These should be visible operationally.

---

# 158. NO FAKE HEALTH

Do not display:

    "Real-time"
    "100% processing"

when the actual pipeline is degraded.

---

# 159. NO FAKE PROGRESS

For an unknown-length live stream:

    do not show arbitrary percentage progress.

---

# 160. FORENSIC STATISTICS

For file jobs, capture:

    total decoded frames
    sampled frames
    processed frames
    dropped/skipped frames
    face detections
    quality-approved detections
    tracks
    embeddings
    candidates
    sightings

where applicable.

---

# 161. STATISTICS ACCURACY

Statistics must distinguish:

    source count
    decoded count
    sampled count
    processed count

These are not interchangeable.

---

# 162. SAMPLE COVERAGE

If a file has:

    360,000 source frames
    36,000 sampled

the system should make coverage understandable.

Do not call this:

    full-frame analysis.

---

# 163. REAL-TIME SAMPLE COVERAGE

For live mode, show effective processing rate relative to incoming rate.

---

# 164. MULTI-STREAM DASHBOARD DATA

The backend may expose:

    active streams
    healthy streams
    degraded streams
    current FPS
    active sightings

without exposing restricted source details.

---

# 165. STREAM ISOLATION

A failed camera must not crash all camera pipelines.

Use failure isolation.

---

# 166. WORKER ISOLATION

Workers should be restartable independently where infrastructure permits.

---

# 167. DEPLOYMENT TOPOLOGY

Recommended conceptual:

    React
      ↓
    FastAPI
      ↓
    Workflow/Job Orchestrator
      ↓
    CPU Workers
      ↓
    GPU Inference Workers
      ↓
    PostgreSQL / pgvector
      ↓
    Neo4j
      ↓
    Event/WebSocket Gateway

---

# 168. API DOES NOT DECODE VIDEO

Do not make the synchronous FastAPI request handler:

    decode entire MP4
    run GPU inference
    wait for completion

Use asynchronous job/workflow execution.

---

# 169. WORKFLOW BOUNDARY

The durable workflow coordinates:

    ingestion
    processing
    retries
    completion
    failure

Inference workers perform compute.

---

# 170. LONG-RUNNING FILE JOBS

Large video jobs must not depend on an HTTP request remaining open.

Return:

    job_id

and process asynchronously.

---

# 171. LIVE JOBS

Live stream processing is also a long-running job.

Use durable lifecycle management.

---

# 172. WORKFLOW RETRY

Retry only operations that are safe to retry.

Do not blindly repeat non-idempotent database writes.

---

# 173. ACTIVITY IDEMPOTENCY

Workflow activities that create forensic records should use deterministic/idempotent keys or controlled transaction patterns.

---

# 174. GPU ACTIVITY

If workflow calls a GPU worker:

    request must include processing context
    worker must return structured result/status

Do not let workflow state depend on undocumented worker memory.

---

# 175. WORKER QUEUE

A queue may separate:

    orchestration
    CPU preprocessing
    GPU inference

Queue names should be explicit and operationally observable.

---

# 176. PRIORITY

Where required, prioritize:

    investigator-requested active search

over:

    background reprocessing

Do not starve critical work indefinitely.

---

# 177. RESOURCE QUOTAS

Per investigation/case/source quotas can protect shared infrastructure.

---

# 178. RATE LIMITING

API/job creation should be rate-limited to prevent accidental/excessive workload.

---

# 179. LIVE STREAM LIMIT

Deployment must define maximum concurrent live sources per environment based on tested capacity.

Do not invent a universal number.

---

# 180. MODEL CAPACITY TEST

Before increasing camera count:

    benchmark actual GPU throughput

using representative:

    resolution
    FPS
    face density
    model
    detector
    tracker

---

# 181. LOAD TEST

Load tests should cover:

    one video
    many videos
    one live stream
    many live streams
    bursty candidates
    reconnect storms

---

# 182. SOAK TEST

Run long-duration live processing and measure:

    memory
    GPU memory
    latency
    queue growth
    reconnect behavior

---

# 183. MEMORY LEAK TEST

A stable live pipeline should not show unbounded memory growth over time.

---

# 184. GPU MEMORY LEAK TEST

Repeated inference should not continuously increase GPU memory without bounded reuse.

---

# 185. DECODER STABILITY TEST

Long MP4 playback should not crash after extended frame processing.

---

# 186. RTSP RECONNECT TEST

Test:

    disconnect
    5xx/network error
    reconnect
    frame recovery

Verify no duplicated uncontrolled pipeline.

---

# 187. CAMERA FAILURE TEST

Stop camera source.

Expected:

    health changes
    no fake sightings
    no worker starvation
    controlled recovery

---

# 188. FRAME-DROP TEST

Intentionally overload a test pipeline.

Verify:

    queue remains bounded
    drop count increases
    latency does not grow without bound

---

# 189. BACKPRESSURE TEST

Verify that slow inference does not cause unlimited decode buffering.

---

# 190. CANCELLATION TEST

Cancel a live/file job.

Verify:

    workers stop
    resources release
    job state finalizes
    no orphaned processing loop remains

---

# 191. DUPLICATE JOB TEST

Submit duplicate job request.

Verify behavior matches idempotency policy.

---

# 192. DUPLICATE EVENT TEST

Replay the same event.

Verify frontend/backend projections remain idempotent.

---

# 193. SOURCE ACCESS TEST

Attempt processing without source authorization.

Expected:

    rejected before decode/inference.

---

# 194. CROSS-CASE TEST

Attempt a candidate search against unauthorized evidence.

Expected:

    denied.

---

# 195. CREDENTIAL LEAK TEST

Inspect:

    logs
    events
    errors
    frontend payloads

Verify RTSP credentials never appear.

---

# 196. VECTOR SECURITY TEST

Verify vectors from one case cannot be retrieved by an unauthorized investigation.

---

# 197. PROVENANCE TEST

For every accepted test sighting:

    source
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
       ↓
    processing run

must resolve.

---

# 198. UI REAL-TIME TEST

The frontend should:

    load current snapshot
    subscribe
    receive new sighting
    update candidate list
    show source frame
    preserve review state

---

# 199. UI RECONNECT TEST

Disconnect network.

Reconnect.

Verify:

    snapshot refresh
    event reconciliation
    no duplicate cards

---

# 200. PERFORMANCE ACCEPTANCE

Do not define performance acceptance using only:

    average FPS

Also evaluate:

    p50 latency
    p95 latency
    queue depth
    frame drops
    GPU memory
    CPU
    source FPS
    processed FPS

---

# 201. PRODUCTION OBSERVABILITY

Dashboards should expose:

    active jobs
    active streams
    worker health
    queue depth
    processing rate
    candidate rate
    error rate
    reconnect rate

---

# 202. ALERTS

Potential alerts:

    repeated decoder failure
    GPU worker unavailable
    queue saturation
    memory pressure
    repeated RTSP reconnects
    processing failure spikes

---

# 203. FORENSIC ALERT VS OPERATIONS ALERT

Do not confuse:

    operational alert

with:

    forensic candidate

A GPU outage is not an investigative finding.

---

# 204. DATA RETENTION

Live intermediate data must obey CrimeKit retention policy.

Do not keep:

    every frame
    every crop
    every embedding

indefinitely by default.

---

# 205. TEMP FILE CLEANUP

Temporary decoder/cache files must be cleaned after processing according to lifecycle policy.

---

# 206. FAILED JOB CLEANUP

Failed jobs must not leave:

    unlimited temporary frames
    orphan containers
    stale buffers
    leaked GPU memory

---

# 207. SECURITY BOUNDARY

Security checks must occur at:

    job creation
    source access
    worker execution
    result retrieval
    event subscription
    frame retrieval

---

# 208. ZERO TRUST INTERNAL MODEL

Do not assume that a worker is automatically authorized merely because it is internal.

Propagate authorization/context required by the architecture.

---

# 209. SECRET MANAGEMENT

Secrets belong in:

    approved secret manager
    environment injection
    secure configuration

Never in:

    Git
    frontend bundle
    event payload
    logs

---

# 210. SUPPLY CHAIN

Pin/track relevant:

    decoder libraries
    ML runtime
    GPU runtime
    tracker
    detector
    model

Use the CrimeKit dependency/security process.

---

# 211. MODEL AVAILABILITY

If the recognition model is unavailable:

    job should fail/degrade explicitly

Do not silently use an unapproved alternative.

---

# 212. MODEL VERSION CONSISTENCY

One processing run should not silently switch models midway.

---

# 213. MIXED MODEL DETECTION

A worker should preserve model context per output.

Historical results remain attributable.

---

# 214. PROVIDER FAILURE

If InsightFace provider fails:

    propagate structured provider error
    preserve source/frame provenance
    do not fabricate embedding

---

# 215. FRAME DECODING FAILURE

If a source frame cannot be decoded:

    no embedding
    no fake candidate
    record failure according to policy

---

# 216. MATCHING FAILURE

If vector/matching service fails:

    preserve successful upstream observations
    mark downstream stage unavailable

Do not claim no matches.

---

# 217. DATABASE FAILURE

If persistence fails:

    do not report permanent success

Use controlled retry/idempotency policy.

---

# 218. EVENT FAILURE

If event publication fails after durable persistence:

    do not roll back source forensic history merely because UI delivery failed

Use event retry/projection mechanisms.

---

# 219. FINALIZED RUN

A completed file Processing Run should record:

    input scope
    sampling policy
    processing statistics
    model context
    runtime context
    outcome
    provenance

---

# 220. LIVE RUN SUMMARY

When a live run stops, record:

    start
    end
    source
    processing statistics
    reconnects
    drops
    sightings
    outcome

---

# 221. REAL-TIME QUALITY OF SERVICE

A useful live state can combine:

    HEALTHY
    DEGRADED
    OFFLINE

with metrics such as:

    FPS
    latency
    drop rate

---

# 222. INVESTIGATOR-FACING LANGUAGE

Use:

    "Candidate sighting"
    "Machine-generated"
    "Source frame"
    "Observed at"
    "Review required"

Avoid:

    "Confirmed suspect"
    "Guilty"
    "AI proved identity"

---

# 223. LIVE INVESTIGATOR VIEW

Recommended information:

    Camera
    Source time
    Latest sighting
    Candidate similarity
    Quality
    Track
    Source frame
    Review state

---

# 224. REAL-TIME UI UPDATE MODEL

Use:

    latest authoritative snapshot
       +
    incremental events

Avoid requiring full-page refresh for every sighting.

---

# 225. EVENT RATE CONTROL

If a scene creates large numbers of low-value updates:

    aggregate/coalesce updates

while preserving important forensic state.

---

# 226. UI THROTTLING

Frontend may visually throttle high-frequency track updates.

This must not change authoritative backend records.

---

# 227. SOURCE FRAME REFRESH

When sighting updates:

    UI can request latest/best source frame

rather than sending raw high-resolution frames over WebSocket.

---

# 228. WEBSOCKET PAYLOAD SIZE

Keep payloads small.

Use identifiers and metadata.

Fetch binary/image content through authorized endpoints.

---

# 229. VIDEO PREVIEW

If a live preview is shown:

    streaming transport

should be separate from the forensic candidate event channel where possible.

Do not send full video frames through the same JSON WebSocket event stream.

---

# 230. PREVIEW VS EVIDENCE

Live preview is presentation.

Evidence capture/storage is forensic.

Do not treat preview availability as proof that source evidence has been preserved.

---

# 231. FILE PREVIEW VS SOURCE

An investigator preview may use transcoded media.

The report/provenance chain must still point to authoritative evidence.

---

# 232. SOURCE AUDIO

Face Trace does not require audio for face matching.

Audio processing belongs to other CrimeKit pipelines.

Do not couple face matching to audio decode unnecessarily.

---

# 233. MULTI-STREAM SYNCHRONIZATION

Cross-camera correlation may use source timestamps, but synchronization accuracy must not be overstated.

---

# 234. GLOBAL TIMELINE

The timeline subsystem should receive normalized sighting events with provenance.

Do not create a parallel independent timeline.

---

# 235. NEO4J INTEGRATION

Neo4j can receive relationships such as:

    Sighting → observed_in → Evidence
    Sighting → on_track → Track

Projection must preserve stable IDs and lineage.

---

# 236. POSTGRESQL INTEGRATION

PostgreSQL should remain authoritative for structured forensic/result state according to CrimeKit architecture.

---

# 237. PGVECTOR INTEGRATION

pgvector should provide authorized retrieval.

It should not become the sole source of forensic truth.

---

# 238. REDIS

Redis may support:

    queues
    transient coordination
    caching

Do not use Redis alone as permanent forensic storage.

---

# 239. CELERY / WORKERS

Where Celery is used for compute/background tasks:

    use explicit queues
    retry policies
    result state

Do not create duplicate workflow orchestration responsibilities.

---

# 240. TEMPORAL

Where Temporal is the durable workflow authority:

    Temporal owns long-running workflow state
    workers execute activities

Do not create a second competing job lifecycle.

---

# 241. GRAPH PROJECTION DELAY

Face sighting persistence should not wait indefinitely for Neo4j projection before returning its core state.

---

# 242. VECTOR PROJECTION DELAY

Where vectors are asynchronously indexed:

    candidate retrieval availability

may lag persistence.

Expose this state where necessary.

---

# 243. PROVENANCE COMPLETENESS GATE

A candidate should only be considered normal investigator output when required lineage exists.

---

# 244. REAL-TIME FAILURE GATE

If the live pipeline loses source timestamps or cannot establish authorized source identity:

    degrade/stop according to policy

Do not publish ambiguous forensic findings.

---

# 245. MODEL HOT-SWAP

Do not hot-swap recognition models within a processing run unless explicitly designed and provenance-safe.

---

# 246. CONFIGURATION HOT-SWAP

Changes to:

    sampling
    thresholds
    detector
    tracker
    model

must not silently alter an active forensic run's historical context.

---

# 247. DEPLOYMENT ROLLOUT

New model/runtime versions should be validated in:

    test
    staging
    controlled production

before full deployment.

---

# 248. CANARY

A canary deployment may compare:

    latency
    failure
    memory
    candidate rate

without mixing outputs incorrectly.

---

# 249. ROLLBACK

Rollback must not delete valid historical results from previous runs.

---

# 250. IMPLEMENTATION ORDER

Recommended implementation sequence:

## Phase 1 — Video foundations

    source abstraction
    decoder
    frame object
    bounded queue
    sampling

## Phase 2 — Detection

    detector adapter
    detection records
    quality gate

## Phase 3 — Tracking

    tracker adapter
    track lifecycle

## Phase 4 — InsightFace

    provider adapter
    embedding generation
    model metadata

## Phase 5 — Matching

    pgvector retrieval
    policy filtering

## Phase 6 — Sighting

    aggregation
    provenance
    persistence

## Phase 7 — Realtime

    event schema
    event bus
    WebSocket gateway

## Phase 8 — Live CCTV

    RTSP
    reconnect
    stream health
    live metrics

## Phase 9 — Frontend

    snapshot
    realtime subscription
    source-frame view
    candidate/sighting UI

## Phase 10 — Hardening

    load
    soak
    failure
    security
    provenance
    observability

---

# 251. MINIMUM SIH VERTICAL SLICE

The first convincing end-to-end version should demonstrate:

    Reference Image
          ↓
    Select MP4
          ↓
    Start Search
          ↓
    Async Processing
          ↓
    Video Decode
          ↓
    Face Detection
          ↓
    Tracking
          ↓
    InsightFace Embedding
          ↓
    Similarity Search
          ↓
    Candidate Sighting
          ↓
    Source Frame
          ↓
    Provenance
          ↓
    Live UI Update
          ↓
    Investigator Review

---

# 252. REAL-TIME DEMO EXPECTATION

The demo should show actual pipeline state changing.

Example:

    00:00 Processing started
    00:04 1,240 frames sampled
    00:07 34 faces detected
    00:08 7 tracks active
    00:09 2 candidate sightings
    00:10 Sighting updated
    00:11 Source frame opened
    00:12 Investigator review pending

Use actual measured values from the run.

Do not fake telemetry.

---

# 253. DEFINITION OF DONE — VIDEO FILE

A file pipeline is complete when:

[ ] Authorized source can be loaded.

[ ] Evidence remains immutable.

[ ] Decoder produces timestamped frames.

[ ] Sampling is configurable/recorded.

[ ] Queues are bounded.

[ ] Detector produces provenance.

[ ] Quality gate is explicit.

[ ] Tracker creates source-scoped tracks.

[ ] InsightFace produces attributable embeddings.

[ ] Matching obeys policy.

[ ] Candidates are persisted.

[ ] Sightings aggregate observations.

[ ] Source frames are recoverable.

[ ] Provenance is complete.

[ ] Processing statistics are accurate.

[ ] Failures are explicit.

[ ] Reprocessing is distinguishable.

[ ] Tests cover critical failure modes.

---

# 254. DEFINITION OF DONE — LIVE CCTV

A live pipeline is complete when:

[ ] Authorized RTSP source connects.

[ ] Credentials remain server-side.

[ ] Health state is visible.

[ ] Decoder produces timestamped frames.

[ ] Processing queue is bounded.

[ ] Frame drop policy is explicit.

[ ] Detector runs continuously.

[ ] Tracker maintains bounded state.

[ ] InsightFace embeddings are generated.

[ ] Matching is authorized.

[ ] Candidate sightings are aggregated.

[ ] Events are published.

[ ] WebSocket access is authorized.

[ ] Frontend receives live updates.

[ ] Disconnect/reconnect works.

[ ] Shutdown releases resources.

[ ] Long-duration soak test passes.

---

# 255. FINAL ARCHITECTURAL RULE

The real-time engine is not:

    RTSP → Face Recognition

It is:

    Authorized Source
         ↓
    Timestamped Media
         ↓
    Bounded Processing
         ↓
    Detection
         ↓
    Quality
         ↓
    Tracking
         ↓
    Recognition
         ↓
    Authorized Matching
         ↓
    Candidate Observation
         ↓
    Sighting Aggregation
         ↓
    Provenance
         ↓
    Durable Forensic Record
         ↓
    Real-Time Investigator Event

Every stage must be observable, bounded, attributable, and recoverable.

---

# 256. FINAL RULE

Real-time speed must never be purchased by sacrificing:

    evidence integrity
    authorization
    provenance
    human review
    reproducibility

CrimeKit should prefer:

    truthful degraded processing

over:

    impressive but misleading real-time claims.

That is the real-time standard for Face Trace Investigator.
