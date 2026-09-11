# CrimeKit Face Trace Investigator — INSIGHTFACE ENGINEERING SPECIFICATION

**Document:** `INSIGHTFACE.md`  
**Subsystem:** Face Trace Investigator  
**Primary provider:** InsightFace  
**Runtime:** ONNX Runtime where compatible with the selected model artifact  
**Audience:** ML engineers, backend engineers, forensic engineers, infrastructure, security, QA  
**Status:** Authoritative provider-integration specification

---

# 1. PURPOSE

This document defines how CrimeKit integrates InsightFace into the Face Trace Investigator subsystem.

InsightFace is the face-analysis provider.

CrimeKit remains responsible for:

- case management
- evidence handling
- authorization
- forensic provenance
- processing orchestration
- candidate semantics
- review
- persistence
- graph/timeline integration
- audit
- operational controls

InsightFace must therefore sit behind a controlled internal model boundary.

The system must not allow provider-specific implementation details to leak across the entire CrimeKit codebase.

---

# 2. PROVIDER ROLE

InsightFace is used for computational face analysis such as:

- face detection
- face alignment/analysis where provided by the selected model pipeline
- face recognition embedding generation

Tracking is a separate responsibility.

Video decoding is a separate responsibility.

Vector search is a separate responsibility.

Investigator review is a separate responsibility.

The conceptual pipeline is:

    Source Image/Frame
          ↓
    Face Detection
          ↓
    Quality Evaluation
          ↓
    Face Crop/Alignment
          ↓
    Recognition Model
          ↓
    Embedding
          ↓
    CrimeKit Matching Layer

Do not treat InsightFace as the entire investigation engine.

---

# 3. OFFICIAL PROJECT POSITION

InsightFace describes itself as an open-source face-analysis toolbox covering face recognition, face detection, and face alignment, with deployment-oriented implementations. The official repository directs users to its Python package for testing detection, recognition, and alignment models. citeturn745739search4

CrimeKit must use the provider in a controlled, versioned way.

The implementation must not assume that every InsightFace model artifact has identical licensing or operational characteristics.

---

# 4. LICENSE AND COMMERCIAL USE

This is a mandatory deployment gate.

The InsightFace repository states that its code is MIT licensed, while pretrained models have separate licensing conditions; it specifically directs users to contact InsightFace regarding licensing for pretrained recognition models. citeturn745739search4

Therefore:

    CODE LICENSE
        ≠
    AUTOMATIC MODEL COMMERCIAL LICENSE

Before describing a model as approved for commercial/production use, record:

    provider
    exact model/package
    model version
    source URL
    artifact checksum where applicable
    applicable model license
    intended use
    approval status

For the project-provided private-model evaluation material, the hosted endpoint is explicitly described as an evaluation mechanism, with controlled access and a limited evaluation window. Long-term deployment is described as local/offline inference using model files after the appropriate agreement. [Source: project-provided InsightFace evaluation document]

Never build the production runtime around that evaluation endpoint.

---

# 5. MODEL SELECTION PRINCIPLE

The model is an implementation dependency, not a hard-coded product assumption.

CrimeKit must expose a provider/model abstraction so that an approved recognition model can be replaced without rewriting:

- case management
- provenance
- API contracts
- UI
- review
- graph
- timeline

The first implementation may use an approved local InsightFace model package where the applicable license and deployment scope permit it.

---

# 6. INITIAL DEVELOPMENT MODEL

For local development and controlled demonstration, the team may use the selected public InsightFace model package when permitted by its model license.

The project has previously considered `buffalo_l`.

Do not automatically label `buffalo_l` "commercial production approved."

Its technical suitability and its license suitability are separate questions.

The exact model used by a given environment must be configurable and recorded.

---

# 7. HOSTED EVALUATION API RULE

The project-provided InsightFace evaluation document says the hosted API:

- is intended for evaluation
- requires controlled access
- has account/rate restrictions
- has a limited evaluation window
- should not be treated as the long-term inference architecture

The same document states that long-term production deployment uses locally deployed model files rather than relying on the hosted endpoint. [Source: project-provided InsightFace evaluation document]

Therefore:

    Evaluation:
        hosted endpoint may be used only where authorized

    CrimeKit runtime:
        local/self-hosted inference

Do not implement:

    CCTV
      ↓
    HTTP upload for every frame
      ↓
    hosted InsightFace endpoint

as the normal production architecture.

---

# 8. LOCAL INFERENCE ARCHITECTURE

Preferred conceptual path:

    CrimeKit FaceModelProvider
          ↓
    InsightFaceAdapter
          ↓
    InsightFace model pipeline
          ↓
    ONNX Runtime
          ↓
    CPU / CUDA / approved accelerator

The application sees:

    FaceModelProvider

not:

    raw InsightFace implementation objects

---

# 9. MODEL PROVIDER CONTRACT

The internal provider abstraction should conceptually support:

    initialize()
    health()
    detect_faces()
    embed_faces()
    metadata()

The exact method signatures must follow existing CrimeKit coding conventions.

The provider should return stable CrimeKit domain structures.

---

# 10. MODEL METADATA CONTRACT

Every model instance should expose or be associated with:

    provider
    model_id
    model_name
    model_version
    artifact_version
    detector_model
    recognition_model
    embedding_dimension
    runtime
    runtime_version
    execution_provider
    preprocessing_version

This metadata must be available to the processing layer.

---

# 11. MODEL STARTUP LIFECYCLE

Recommended lifecycle:

    PROCESS START
         ↓
    Load configuration
         ↓
    Resolve approved model
         ↓
    Verify artifact/integrity
         ↓
    Initialize runtime
         ↓
    Load model
         ↓
    Run smoke inference
         ↓
    Validate output shape
         ↓
    Verify execution provider
         ↓
    WORKER READY

If any required step fails:

    WORKER NOT_READY

Do not accept production inference work before model readiness.

---

# 12. MODEL LOADING PERFORMANCE

Do not repeatedly initialize the model.

Incorrect:

    for every frame:
        load InsightFace
        infer
        unload

Correct:

    worker startup:
        load model once

    processing:
        reuse model

This keeps initialization cost out of the hot path.

---

# 13. PROCESS ISOLATION

A model worker may be a long-lived process.

The worker should:

- own the model lifecycle
- process multiple jobs
- expose health/readiness
- enforce resource limits
- shut down cleanly
- report runtime metadata

Do not attach large model objects directly to short-lived API request state.

---

# 14. INSIGHTFACE PIPELINE RESPONSIBILITIES

Conceptually separate:

    Detection
    Alignment / preprocessing
    Recognition / embedding

InsightFace may provide multiple components through a model pack.

CrimeKit must still represent their responsibilities independently.

---

# 15. FACE DETECTION

The detector's output should include enough information for CrimeKit to create a forensic detection record.

At minimum:

    bbox
    detection_score
    keypoints when available
    source frame
    source timestamp
    processing run

The detector should not decide whether the person is a known person.

---

# 16. SCRFD

SCRFD is an InsightFace face-detection family designed around detection accuracy and computational efficiency.

CrimeKit may use an appropriate SCRFD configuration/model variant supported by the selected InsightFace package.

Model/variant selection must be benchmarked against CrimeKit source conditions.

Do not state that one detector size is universally optimal.

---

# 17. DETECTION SIZE

Input detector size is a performance/accuracy configuration.

Example:

    det_size = (640, 640)

is a configuration choice, not an immutable law.

The team must benchmark:

- small faces
- crowded frames
- high-resolution CCTV
- low-resolution CCTV
- GPU throughput
- CPU throughput

before finalizing production defaults.

---

# 18. FACE COUNT

Reference image:

    zero faces
        → reject/request replacement

    one usable face
        → continue

    multiple faces
        → explicit user resolution

Do not silently select the first detected face.

Video frame:

    zero or more faces

Every detected face becomes an independent observation.

---

# 19. KEYPOINTS / ALIGNMENT

Where detector keypoints are available, use the model pipeline's approved alignment path.

Do not invent a second alignment implementation without an accuracy/performance reason.

Alignment behavior is part of preprocessing compatibility.

---

# 20. REFERENCE IMAGE PROCESSING

Reference flow:

    Uploaded Image
        ↓
    Secure Decode
        ↓
    Face Detection
        ↓
    Face Count Validation
        ↓
    Quality Evaluation
        ↓
    Approved Alignment/Preprocessing
        ↓
    Recognition Embedding
        ↓
    Embedding Validation
        ↓
    Persist

The original reference remains unchanged.

---

# 21. REFERENCE IMAGE QUALITY

Quality policy should evaluate at least where practical:

- face size
- sharpness/blur
- pose
- occlusion
- illumination
- detection quality
- alignment

The exact quality implementation must be benchmarked.

Do not claim that any one metric alone determines suitability.

---

# 22. VIDEO FACE PIPELINE

For video/CCTV:

    Decoder
       ↓
    Frame Sampling
       ↓
    Detection
       ↓
    Quality
       ↓
    Tracking
       ↓
    Eligible Face Crop
       ↓
    Recognition
       ↓
    Similarity

The recognition stage must not run against every frame merely because the source video has a high FPS.

---

# 23. FRAME SAMPLING

Recognition sampling should be configurable.

Possible starting configuration:

    source FPS = high
    recognition FPS = lower configured rate

The exact rate is a benchmark-driven parameter.

Record it with the processing run.

---

# 24. ADAPTIVE SAMPLING

Adaptive sampling may be added after the baseline is validated.

Concept:

    low-interest interval
        ↓
    lower recognition frequency

    active face/track
        ↓
    higher recognition frequency

Any adaptive policy must record enough metadata to explain how the source was processed.

---

# 25. TRACKING

Tracking is not a function of InsightFace recognition.

Use a separate tracking implementation.

Flow:

    detector
       ↓
    tracker
       ↓
    track
       ↓
    recognition observations

Candidate track semantics must remain separate from identity semantics.

---

# 26. TRACKING FREQUENCY

Tracking can operate more frequently than recognition.

This may allow:

    detection/tracking
        ↓
    maintain track
        ↓
    run expensive recognition periodically

This is an important performance optimization.

It must not reduce evidence traceability.

---

# 27. RECOGNITION FREQUENCY

For a continuous track:

    Frame 100
    Frame 101
    Frame 102
    Frame 103

do not automatically run recognition at every frame.

Recognition may be sampled.

The aggregation layer must retain which observations were actually recognized.

---

# 28. FACE EMBEDDING

Recognition converts the approved face crop into a vector representation.

The CrimeKit adapter must validate:

    vector exists
    expected dimension
    finite values
    normalization expectation
    model compatibility

Invalid output must not enter persistence/indexing.

---

# 29. NORMALIZED EMBEDDINGS

The project-provided InsightFace evaluation material specifies normalized feature vectors for that evaluation service and recommends cosine similarity for comparison. [Source: project-provided InsightFace evaluation document]

For local InsightFace integrations, follow the exact output contract of the selected model pipeline.

Do not assume all future model providers have identical normalization behavior.

---

# 30. SIMILARITY

For compatible normalized vectors, cosine similarity can be computed through the equivalent normalized-vector dot product.

Example conceptual calculation:

    similarity = reference_embedding · candidate_embedding

The implementation must validate the selected model's embedding contract before relying on that assumption.

---

# 31. MATCH POLICY

Do not embed a production threshold inside the model adapter.

Keep:

    model
    inference
    matching policy

separate.

Conceptually:

    FaceEmbedding
        +
    MatchingPolicy
        ↓
    CandidateDecision

---

# 32. THRESHOLD POLICY

Do not copy an example threshold such as:

    0.55

into production without evaluation.

The project must create an explicit matching policy containing:

    policy_id
    policy_version
    similarity_metric
    candidate_threshold
    high_candidate_threshold
    quality_requirements
    aggregation_rules

---

# 33. THRESHOLD EVALUATION

Threshold selection must be based on an authorized evaluation dataset.

Measure:

    false accepts
    false rejects
    precision
    recall

Where appropriate:

    ROC
    DET
    operating point

The chosen operating point must be documented with the evaluation dataset and model version.

---

# 34. MODEL VS POLICY

A model update can change similarity distributions.

Therefore:

    model version
        +
    matching policy version

must be treated as a pair of processing context.

Do not assume a threshold from model version A remains valid for model version B.

---

# 35. VECTOR SEARCH

For a single reference searching a modest number of embeddings, direct similarity comparison may be sufficient.

For large candidate sets, use approved vector search infrastructure.

The search architecture should separate:

    embedding generation

from:

    candidate retrieval

from:

    candidate decision

---

# 36. PGVECTOR COMPATIBILITY

When pgvector is used:

- enforce vector dimension
- enforce model compatibility
- enforce authorization scope
- use parameterized queries
- evaluate index strategy

Do not query all biometric vectors and filter unauthorized data in application/UI logic.

---

# 37. MODEL PARTITIONING

If multiple model versions coexist, use explicit logical separation.

Possible approaches:

    model_version column
    separate indexes
    separate collections
    separate vector spaces

The selected strategy must prevent incompatible comparisons.

---

# 38. BATCH INFERENCE

Where the runtime/model supports batching, evaluate batch processing for throughput.

Example:

    Face Crop 1
    Face Crop 2
    Face Crop 3
    ...
        ↓
    one inference batch

The implementation must preserve:

    source mapping
    order
    frame ID
    detection ID
    timestamp

Batching must never destroy provenance.

---

# 39. PREPROCESSING

Preprocessing may include:

    decode
    crop
    alignment
    resize
    normalization

The exact sequence must follow the selected model pipeline.

Do not independently modify preprocessing merely to make the model accept a frame.

---

# 40. REFERENCE CROP GUIDANCE

The project-provided private-model evaluation document recommends a small crop margin and a lossless image representation for its evaluation workflow. [Source: project-provided InsightFace evaluation document]

That guidance should be treated as an evaluation-specific reference.

For local CrimeKit inference, benchmark the preprocessing pipeline against actual source conditions before locking production values.

---

# 41. IMAGE ENCODING

Avoid unnecessary lossy re-encoding before inference.

If a derived face crop is persisted, use the project-approved format and quality settings.

Do not repeatedly:

    decode
      ↓
    JPEG
      ↓
    decode
      ↓
    JPEG

as part of the inference hot path.

---

# 42. FRAME RESOLUTION

Do not unnecessarily resize the entire source video.

Prefer:

    source frame
       ↓
    detector
       ↓
    face crop
       ↓
    recognition preprocessing

where practical.

This can reduce unnecessary data transfer and processing.

---

# 43. SMALL FACE HANDLING

Small faces are a major CCTV challenge.

The system should identify when the face is too small for reliable recognition.

Do not force every detected face through recognition merely to increase the number of outputs.

A detection can be valid while recognition eligibility is poor.

---

# 44. OCCLUSION

Heavy occlusion may produce unreliable embeddings.

Store quality information.

Do not silently raise or lower thresholds to make poor-quality faces appear to match.

---

# 45. POSE

Profile/extreme-pose observations should be represented through quality/context signals.

Do not pretend that:

    frontal
    and
    extreme profile

are equivalent evidence conditions.

---

# 46. BLUR

Motion blur and compression can produce unstable embeddings.

Do not treat one high similarity observation from an obviously degraded frame as automatically strong evidence.

Use track-level aggregation and quality context.

---

# 47. MULTIPLE OBSERVATIONS

A strong candidate may have:

    many moderate-quality observations

rather than:

    one perfect frame

The aggregation layer should preserve all observations and generate an investigator-friendly sighting.

---

# 48. TRACK-LEVEL RECOGNITION

A track may be scored using multiple observed embeddings.

Potential strategy:

    Track
      ├── embedding 1
      ├── embedding 2
      ├── embedding 3
      └── embedding N

Then derive candidate evidence using a documented aggregation strategy.

Do not invent statistical semantics without evaluation.

---

# 49. DO NOT OVERFIT TO ONE SCORE

Candidate quality can depend on:

    similarity
    source quality
    track duration
    observation count
    temporal consistency

These are separate signals.

Do not hide them behind an unexplained "AI confidence."

---

# 50. MODEL CONFIDENCE TERMINOLOGY

Avoid saying:

    "92% probability this is the person"

when the system only has an embedding similarity score.

Use terminology such as:

    similarity
    candidate score
    quality
    candidate tier

unless a calibrated probabilistic model has actually been developed and validated.

---

# 51. MODEL FAILURE BEHAVIOR

If InsightFace initialization fails:

    worker = NOT_READY

If inference fails for one frame:

    record frame processing failure
    continue if policy permits

If the model becomes unavailable globally:

    mark worker degraded/unavailable
    stop accepting new inference work as appropriate

Never fabricate a result.

---

# 52. GPU EXECUTION

ONNX Runtime supports multiple execution providers and allows priority-based provider selection; CUDA and TensorRT are supported NVIDIA paths. citeturn745739search0

For a CUDA deployment:

    CUDAExecutionProvider

may be used as the primary GPU provider.

CPU can be a controlled fallback where supported and operationally appropriate.

---

# 53. TENSORRT

ONNX Runtime documents TensorRT execution as an NVIDIA acceleration path and recommends registering CUDA as a fallback for operations TensorRT does not support. citeturn745739search1

Do not introduce TensorRT simply because it sounds more production-grade.

Evaluate:

    CUDA
    vs
    TensorRT + CUDA fallback

on actual CrimeKit workloads.

---

# 54. CUDA COMPATIBILITY

ONNX Runtime's current CUDA provider documentation contains version-specific CUDA/cuDNN compatibility requirements. It also notes that modern `onnxruntime-gpu` packages have changing default CUDA major versions by release. citeturn745739search3

Therefore:

    ONNX Runtime version
        +
    CUDA version
        +
    cuDNN version
        +
    driver
        +
    container

must be treated as a tested compatibility matrix.

Do not upgrade one component blindly.

---

# 55. EXECUTION PROVIDER RECORDING

Every processing run should be able to identify:

    execution_provider

Examples:

    CUDAExecutionProvider
    CPUExecutionProvider

If TensorRT is used:

    TensorrtExecutionProvider

Record actual runtime behavior rather than desired configuration.

---

# 56. GPU WORKER DESIGN

A GPU worker should:

- load model once
- maintain bounded work queues
- avoid uncontrolled memory growth
- monitor GPU memory
- expose readiness
- support graceful shutdown
- record execution provider

Do not allow arbitrary requests to allocate unlimited GPU memory.

---

# 57. GPU MEMORY

Measure:

    model memory
    inference memory
    batch memory
    peak GPU memory

Do not guess maximum batch size.

Benchmark it.

---

# 58. CPU FALLBACK

If CPU fallback exists:

    GPU unavailable
        ↓
    approved CPU fallback

or:

    GPU unavailable
        ↓
    job paused/fails according to policy

The run must record which mode was used.

---

# 59. MODEL WARMUP

After model loading, perform a controlled health/smoke inference where practical.

Purpose:

- validate model loading
- validate runtime
- validate execution provider
- catch initialization errors before accepting jobs

Warmup data must not be real case biometric data unless explicitly authorized.

---

# 60. MODEL HEALTH

A worker is READY only if:

    model loaded
    runtime initialized
    inference succeeds
    expected output shape is correct

A worker with a broken model must not advertise readiness.

---

# 61. MODEL CHECKSUM

Where a checksum/manifest process exists, verify model artifacts before loading.

Possible metadata:

    sha256
    artifact version
    source package version

Do not silently replace model files in a production environment.

---

# 62. MODEL ARTIFACT STORAGE

Model files must be stored separately from user evidence.

Recommended conceptual separation:

    model registry/storage
        ≠
    case evidence storage

Do not place model files inside case directories.

---

# 63. MODEL SECRETS

If a provider requires credentials for a licensed/private model:

- use secret management
- never commit credentials
- never place credentials in frontend code
- never log credentials
- never send credentials to browsers

---

# 64. MODEL DOWNLOAD POLICY

Production runtime should not silently download arbitrary model artifacts at startup from an uncontrolled source.

Prefer:

    approved artifact
       ↓
    verified deployment
       ↓
    runtime

Any remote artifact retrieval must be explicitly governed.

---

# 65. OFFLINE RUNTIME PREFERENCE

Where operationally possible, production inference should remain functional without internet access after approved model deployment.

This reduces external dependency and protects sensitive case processing.

---

# 66. MULTI-MODEL SUPPORT

The adapter should conceptually permit:

    model A
    model B

but each model must have its own:

    model ID
    model version
    embedding dimension
    policy compatibility

Do not mix arbitrary embeddings.

---

# 67. MODEL ROLLOUT

Recommended rollout:

    candidate model
       ↓
    offline evaluation
       ↓
    regression
       ↓
    performance
       ↓
    security/license
       ↓
    staging
       ↓
    controlled production rollout

Keep historical processing metadata.

---

# 68. MODEL ROLLBACK

If a new model produces unacceptable behavior:

    deactivate new version
       ↓
    reactivate approved version
       ↓
    preserve historical runs

Do not rewrite prior records.

---

# 69. MODEL DEPRECATION

When retiring a model:

- stop new processing
- retain metadata for historical results
- retain ability to interpret historical runs
- migrate embeddings only through an explicit process

Do not delete historical model information merely because the model is deprecated.

---

# 70. MODEL REGISTRY

If CrimeKit eventually requires multiple models, use an internal model registry abstraction containing:

    model_id
    version
    provider
    artifact
    checksum
    license_status
    embedding_dimension
    runtime_requirements
    activation_status

The exact storage implementation should follow existing infrastructure.

---

# 71. MODEL CONFIGURATION

Configuration should not be scattered across code.

Centralize approved runtime settings for:

- model ID
- model version
- detector configuration
- execution provider
- batch size
- quality policy
- matching policy

Use existing CrimeKit configuration patterns.

---

# 72. MODEL OBSERVABILITY

Expose operational metadata such as:

    loaded_model
    model_version
    execution_provider
    inference_latency
    throughput
    failure_count

Do not expose raw embeddings.

---

# 73. MODEL AUDIT

A processing run must identify the model used.

Example:

    provider = InsightFace
    model = buffalo_l
    model_version = <version>
    runtime = ONNX Runtime
    execution_provider = CUDAExecutionProvider
    preprocessing_version = <version>
    matching_policy = <version>

Actual values depend on deployment.

---

# 74. MODEL EVALUATION DATASET

Maintain an authorized labeled evaluation set.

It should reflect intended CrimeKit conditions.

Do not use only ideal portrait photographs.

Where applicable include:

    CCTV
    low resolution
    blur
    profiles
    varied lighting
    occlusion
    compression
    camera variation

---

# 75. EVALUATION PROTOCOL

For model comparison:

    dataset
       ↓
    fixed preprocessing
       ↓
    model A
       ↓
    metrics

and separately:

    same dataset
       ↓
    same preprocessing
       ↓
    model B
       ↓
    metrics

Do not change multiple factors simultaneously and then attribute the improvement to the model.

---

# 76. EVALUATION METRICS

Measure according to the actual task.

Possible:

    false accept rate
    false reject rate
    precision
    recall
    ROC
    DET
    top-k retrieval recall

Also measure operational performance:

    latency
    throughput
    memory
    GPU usage

---

# 77. DEMO DATA

Use synthetic, public, or properly authorized test media for demonstrations.

Do not commit real case biometric data to the repository.

Do not upload real sensitive evidence to public model-testing services.

---

# 78. IMAGE SEARCH

For reference-image search against stored images:

    reference
       ↓
    embedding
       ↓
    vector search
       ↓
    candidates
       ↓
    provenance

The same model/policy/version principles apply.

---

# 79. VIDEO SEARCH

For video:

    reference
       ↓
    reference embedding

    video
       ↓
    frames
       ↓
    detections
       ↓
    tracks
       ↓
    embeddings
       ↓
    comparisons
       ↓
    sightings

---

# 80. LIVE CCTV

For live RTSP:

    RTSP
       ↓
    decoder
       ↓
    bounded buffer
       ↓
    detector
       ↓
    tracker
       ↓
    sampled recognition
       ↓
    matching
       ↓
    sighting
       ↓
    event

The model service itself should not be responsible for RTSP lifecycle unless the architecture explicitly chooses that boundary.

---

# 81. REAL-TIME LATENCY

Measure:

    source capture
       ↓
    decode
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
       ↓
    persistence
       ↓
    event
       ↓
    browser

Do not call the system "real time" based solely on model inference FPS.

---

# 82. MODEL HOT PATH

The hot path should minimize:

- model initialization
- unnecessary image conversions
- host/device copies
- disk writes
- repeated database round trips
- network calls
- redundant embedding generation

Optimize only after measuring.

---

# 83. DISK I/O

Do not save every intermediate face crop to disk by default.

Where a crop is not needed as a forensic artifact, keep it in memory long enough for approved processing.

When a derived crop is necessary, persist it through controlled storage with provenance.

---

# 84. GPU DATA PATH

Where practical:

    decode/preprocess
       ↓
    batch
       ↓
    inference

should minimize unnecessary CPU↔GPU transfers.

The exact optimization must follow the runtime/model implementation.

Do not prematurely introduce custom CUDA code.

---

# 85. BATCH SIZE

Batch size must be benchmarked based on:

    GPU
    model
    face count
    image dimensions
    memory

Do not hard-code a universal production batch size.

---

# 86. CONCURRENCY

Do not assume one GPU should run one unbounded process per CPU core.

Benchmark:

    processes
    threads
    batches
    queue depth

and choose based on measured throughput/latency.

---

# 87. QUEUE ARCHITECTURE

Inference requests should be bounded.

Example:

    Video Workers
         ↓
    Bounded Inference Queue
         ↓
    GPU Worker

When full:

    backpressure
    controlled rejection
    or queue delay

according to CrimeKit policy.

---

# 88. STARVATION PREVENTION

One massive video job must not consume all inference capacity.

Consider:

    job fairness
    per-job limits
    per-case limits
    priority

Only implement these when supported by actual product requirements.

---

# 89. ERROR ISOLATION

If one image/frame causes an inference failure:

    mark observation failure
       ↓
    continue if safe

Do not automatically fail the entire case unless the failure affects the integrity of the processing run.

---

# 90. MODEL EXCEPTION HANDLING

Do not expose low-level stack traces to investigators.

Internal logs may contain diagnostic information subject to security policy.

User-facing status should be understandable:

    "Face analysis temporarily unavailable."

rather than:

    raw ONNX/CUDA exception

---

# 91. MODEL TELEMETRY

Recommended metrics:

    face_inference_requests
    face_inference_success
    face_inference_failure
    detection_latency_ms
    embedding_latency_ms
    batch_size
    GPU_memory
    GPU_utilization
    CPU_utilization

Avoid sensitive labels.

Do not use:

    person_id

as a metrics label.

---

# 92. MODEL SECURITY

The model itself is not an authorization layer.

Authorization happens before accessing:

    reference
    evidence
    candidate data

Never assume:

    valid model request
        =
    authorized evidence access

---

# 93. INPUT LIMITS

The model endpoint/adapter should enforce:

- maximum image dimensions
- maximum batch size
- supported formats
- maximum request size
- resource timeouts

This reduces denial-of-service risk.

---

# 94. UNTRUSTED MEDIA

User-uploaded media must be considered untrusted.

Do not trust:

- filename
- MIME type alone
- embedded metadata
- codec/container contents

Use existing CrimeKit secure ingestion controls.

---

# 95. PREPROCESSING VALIDATION

Before inference:

    valid decoded frame/image
    expected channels
    expected data type
    valid dimensions

Do not send malformed tensors into the model.

---

# 96. OUTPUT VALIDATION

After inference:

    valid number of detections
    finite coordinates
    valid bbox bounds
    valid embedding dimension
    finite embedding values

Reject invalid output.

---

# 97. MODEL DRIFT MONITORING

Monitor operational indicators such as:

- candidate rates
- no-face rates
- low-quality rates
- average similarity distributions
- review rejection rates

A major unexpected shift may indicate:

    source-camera change
    preprocessing bug
    model change
    threshold issue
    data-quality change

Do not automatically retrain from these signals.

---

# 98. REVIEW FEEDBACK

Investigator review outcomes may be used for evaluation/quality analysis only according to approved governance.

Do not silently feed investigator decisions into model training.

---

# 99. NO ONLINE LEARNING

Do not implement automatic live model learning from case evidence.

A future training pipeline must be separately governed.

---

# 100. EXPERIMENT ISOLATION

Experimental models must use:

    experiment_id
    experiment dataset
    experiment processing run
    isolated vector index where necessary

Do not contaminate production data.

---

# 101. PROVIDER ABSTRACTION

CrimeKit should conceptually allow:

    InsightFaceProvider
         OR
    ApprovedFutureProvider

without changing the domain API.

The goal is vendor independence at the domain level.

---

# 102. PROVIDER-SPECIFIC METADATA

Provider-specific metadata may be stored in a dedicated infrastructure field if needed, but core domain records should use stable fields.

Do not make every domain object depend on InsightFace-specific class structures.

---

# 103. TEST DOUBLE

Unit tests must be able to run without loading a full production model where appropriate.

Use a deterministic test double/mock provider for domain tests.

Integration/model tests must separately validate the real InsightFace path.

Do not make all backend tests depend on GPU availability.

---

# 104. MODEL INTEGRATION TEST

At least one integration test should verify:

    image
      ↓
    real InsightFace adapter
      ↓
    valid detection/embedding
      ↓
    expected schema

Do not rely exclusively on mocks.

---

# 105. REGRESSION TEST DATA

Maintain small approved test fixtures that verify:

- model loads
- face detection works
- embedding dimensions remain expected
- similarity behavior does not unexpectedly change

Do not commit real biometric data.

---

# 106. GOLDEN TESTS

Where permitted, use stable synthetic/public fixtures for:

    known face
    non-match face
    multiple faces
    low-quality image

Record expected qualitative outcomes rather than brittle exact floating-point values unless deterministic equality is required.

---

# 107. EMBEDDING DIMENSION TEST

Every model activation must have a test confirming:

    configured dimension
       =
    actual model output dimension
       =
    vector storage dimension

---

# 108. EXECUTION PROVIDER TEST

Deployment CI/staging should verify:

    configured provider
       ↓
    actual provider available
       ↓
    inference succeeds

Do not assume the container has working CUDA merely because a GPU is assigned.

---

# 109. CPU/GPU PARITY

Where CPU and GPU paths are both supported, compare outputs within an approved numerical tolerance.

Do not expect bit-identical floating-point results.

Validate that differences do not materially change tested candidate behavior.

---

# 110. PERFORMANCE REGRESSION

If model/runtime changes:

    benchmark previous
       vs
    benchmark new

Compare:

    throughput
    p95 latency
    memory
    GPU usage
    candidate behavior

---

# 111. MODEL RUNTIME VERSION

Record ONNX Runtime version with model-processing metadata.

A runtime upgrade can affect performance or numerical behavior.

Treat runtime changes as controlled changes for the face subsystem.

---

# 112. ONNX MODEL VALIDATION

Where the selected model is ONNX:

- verify model can be loaded
- validate expected inputs
- validate expected outputs
- verify runtime compatibility
- verify execution provider

Do not manually edit production ONNX files without a controlled conversion/validation process.

---

# 113. ONNX GRAPH OPTIMIZATION

Runtime graph optimization may be used where supported.

Measure before/after.

Do not enable an optimization that changes output semantics without testing.

---

# 114. TENSORRT ENGINE CACHING

If TensorRT is adopted, engine caching may reduce session creation time.

ONNX Runtime documents TensorRT execution-provider caching mechanisms and performance settings. citeturn745739search1

Treat caches as deployment artifacts, not authoritative model identity.

---

# 115. MODEL CACHE INVALIDATION

When any of these change:

    model
    runtime
    TensorRT version
    GPU architecture
    relevant EP configuration

the compatibility of cached inference artifacts must be revalidated.

---

# 116. MODEL DOWNLOAD SECURITY

If model artifacts are downloaded during deployment:

    HTTPS/authenticated source
       ↓
    checksum/signature verification
       ↓
    approved artifact
       ↓
    deployment

Do not allow arbitrary user-controlled model paths.

---

# 117. CONTAINERIZATION

The face worker should be containerized according to existing CrimeKit infrastructure when containerization is the project standard.

Container should include:

    Python/runtime
    InsightFace dependency
    ONNX Runtime
    required model artifacts or controlled model mount
    system libraries
    media dependencies

Do not install random host packages during container startup.

---

# 118. NVIDIA CONTAINERIZATION

For GPU deployment, use the project's approved NVIDIA container/runtime configuration.

ONNX Runtime documentation states that GPU deployments depend on compatible NVIDIA drivers and runtime libraries. citeturn745739search3

The container's CUDA/cuDNN/runtime matrix must be tested together.

---

# 119. READINESS ENDPOINT

The face worker should expose or integrate with a readiness mechanism.

READY means:

    model loaded
    runtime ready
    inference smoke test passed

Not merely:

    process is alive

---

# 120. LIVENESS

Liveness indicates the process is responsive.

A live but model-broken process should be:

    LIVENESS = healthy
    READINESS = unhealthy

when that distinction matches the deployment framework.

---

# 121. GRACEFUL SHUTDOWN

When stopping a worker:

1. Stop accepting new work.
2. Finish/cancel according to policy.
3. Release model/runtime resources.
4. Flush required state/events.
5. Exit cleanly.

Do not terminate while corrupting job state.

---

# 122. TIMEOUTS

Inference and processing must have controlled timeouts.

Do not allow a malformed input to hold a worker indefinitely.

Timeout handling must preserve job/error state.

---

# 123. RETRIES

Retry transient infrastructure failures.

Do not blindly retry deterministic model errors forever.

Classify:

    transient
    permanent
    configuration
    input
    resource

before choosing retry behavior.

---

# 124. CIRCUIT BREAKING

If a dependency repeatedly fails:

    stop hammering dependency
    expose degraded state
    recover according to policy

Do not generate massive retry storms.

---

# 125. RATE LIMITING

Protect inference endpoints and job submission from abuse.

Rate limits must be scoped appropriately:

    user
    case
    job
    service

Do not apply a single arbitrary global limit without workload analysis.

---

# 126. PRIORITY

Where CrimeKit has urgent investigative workflows, priority may be supported through the existing workflow scheduler.

Do not bypass authorization or provenance for priority work.

---

# 127. EMBEDDING PERSISTENCE

Persist embeddings only when required by the approved workflow.

Where stored:

- protect them
- version them
- scope them
- audit access
- prevent incompatible mixing

---

# 128. EMBEDDING ENCRYPTION

Use platform-approved encryption at rest and in transit.

Do not invent custom cryptography.

Do not hash an embedding and then assume the hash can perform similarity search.

---

# 129. EMBEDDING DELETION

When retention policy requires deletion:

    relational record
    vector index
    derived artifact
    graph projection

must be considered.

Deletion must not silently leave searchable biometric data behind.

---

# 130. VECTOR INDEX CONSISTENCY

If embeddings are deleted or changed, ensure the vector search layer eventually reflects the authoritative data state.

Track projection status where necessary.

---

# 131. GRAPH PROJECTION

Face-related graph relationships should be created only from persisted domain records.

Preferred:

    FaceSighting persisted
       ↓
    graph projection
       ↓
    Neo4j

Do not let raw inference callbacks create arbitrary graph claims.

---

# 132. AI AGENT CONSUMPTION

AI agents may consume:

    candidate
    sighting
    timestamp
    evidence
    review state

They must not invent face matches.

---

# 133. AI EXPLANATIONS

If an AI agent explains a face result, use stored evidence:

    similarity
    quality
    timestamp
    source
    track
    review

Do not let the LLM fabricate a rationale.

---

# 134. INVESTIGATOR DISPLAY

Recommended candidate information:

    Candidate
    Similarity
    Quality
    Source
    Timestamp
    Track
    Model
    Review State

Avoid displaying raw model internals unless useful to authorized expert users.

---

# 135. MODEL TRANSPARENCY

The investigator should be able to determine which model generated a result.

The UI need not expose every internal model layer.

The system of record must contain model metadata.

---

# 136. PROVENANCE LINK

Every face candidate should allow:

    candidate
       ↓
    sighting
       ↓
    frame
       ↓
    source evidence

The model output without this chain is incomplete.

---

# 137. SOURCE FRAME ANNOTATION

When showing a face box overlay:

    original source frame
        +
    non-destructive visual overlay

Do not overwrite the source frame.

---

# 138. CROP STORAGE

If storing a face crop:

- record source artifact
- record frame
- record bbox
- record processing run
- protect access

Do not create anonymous face files.

---

# 139. MODEL OUTPUT PROVENANCE

The inference record should identify:

    model
    version
    runtime
    provider
    preprocessing
    processing run

This allows reproducibility analysis.

---

# 140. REPRODUCIBILITY

The system should preserve the context required to understand a result.

Do not claim exact repeatability unless the entire processing environment supports it.

---

# 141. MODEL CHANGE IMPACT

A model update can affect:

    embedding distribution
    candidate scores
    ranking
    latency
    memory

Therefore evaluate all five dimensions before activation.

---

# 142. PROVIDER FAILURE

If InsightFace is unavailable:

    do not silently substitute an unapproved provider

unless a documented fallback policy authorizes that provider and records the fallback.

---

# 143. FALLBACK POLICY

A fallback provider, if ever introduced, must have:

    provider ID
    model ID
    compatibility
    evaluation
    licensing
    policy
    auditability

Do not create silent vendor switching.

---

# 144. SECURITY REVIEW OF PROVIDER

Treat external provider dependencies as supply-chain risks.

Review:

    packages
    models
    containers
    downloads
    runtime libraries

Use the existing dependency/security scanning process.

---

# 145. DEPENDENCY PINNING

Pin versions according to CrimeKit dependency policy.

At minimum, review together:

    insightface
    onnxruntime
    opencv
    numpy
    runtime dependencies

Do not casually upgrade one package in production.

---

# 146. COMPATIBILITY MATRIX

Maintain a tested matrix where relevant:

    OS
    Python
    InsightFace
    ONNX Runtime
    CUDA
    cuDNN
    NVIDIA driver
    GPU
    model

A model/runtime combination that works on a developer laptop is not automatically production-supported.

---

# 147. WINDOWS VS LINUX

Development may happen on Windows.

Production GPU inference should follow the project's tested deployment platform.

Do not claim cross-platform production support without validation.

---

# 148. OBSERVABILITY WITHOUT PII LEAKAGE

Metrics/logs may identify:

    job_id
    processing_run_id
    evidence_id

subject to security policy.

Do not use raw face imagery or embeddings as telemetry payloads.

---

# 149. NO RAW VECTOR DEBUGGING

When debugging similarity issues:

Do not print:

    full embedding array

Instead log:

    vector dimension
    norm/status
    model version
    processing run
    similarity
    quality

where authorized.

---

# 150. MODEL DEBUG MODE

Any debug mode must:

- be disabled by default
- require authorization
- avoid biometric leakage
- be time-bounded where possible
- be audited if it exposes sensitive diagnostics

---

# 151. MODEL PERFORMANCE TARGETS

Do not invent universal requirements.

Define project-specific targets such as:

    minimum throughput
    target p95 latency
    maximum GPU memory
    acceptable queue delay

then benchmark them.

---

# 152. INFERENCE SLA

Any future SLA should separate:

    API response SLA
    queue SLA
    inference SLA
    end-to-end processing SLA

Do not call the whole system real-time because the API returns a job ID quickly.

---

# 153. SEARCH LATENCY

Measure:

    reference embedding
    candidate retrieval
    ranking

separately from:

    video processing

This allows actual bottleneck identification.

---

# 154. FACE DETECTION THROUGHPUT

Measure:

    images/sec
    frames/sec
    faces/sec

A detector can become the bottleneck even when the recognition model is fast.

---

# 155. EMBEDDING THROUGHPUT

Measure:

    embeddings/sec

under:

    batch size
    resolution
    GPU
    execution provider

Do not extrapolate from a one-image benchmark to many-camera operation.

---

# 156. GPU UTILIZATION

If GPU usage is low:

    investigate
    preprocessing
    batching
    host/device transfers
    decoding
    CPU bottlenecks

Do not immediately add more GPUs.

---

# 157. VIDEO DECODING BOTTLENECK

If decoding is the bottleneck:

    optimize decoder / worker architecture

not:

    replace the recognition model

Measure the entire pipeline.

---

# 158. MODEL WARMUP LATENCY

Record:

    cold start
    warm inference

Cold start should not be confused with steady-state throughput.

---

# 159. WORKER AUTOSCALING

If infrastructure supports autoscaling:

    scale GPU workers based on:
    queue depth
    processing latency
    resource utilization

Do not scale purely on API traffic.

---

# 160. GPU AFFINITY

When multiple GPUs exist, workers should have controlled device assignment.

Record:

    GPU/device ID

with operational metadata where useful.

---

# 161. MULTI-TENANT ISOLATION

If CrimeKit ever becomes multi-organization:

    tenant
       ↓
    case
       ↓
    face data

must remain properly isolated.

Do not assume case-level security alone is enough for multi-tenant deployment.

---

# 162. CROSS-ORGANIZATION DATA

Cross-organization face search must be explicitly authorized and governed.

Do not introduce it by simply removing a database filter.

---

# 163. MODEL DATA BOUNDARY

Model inference should receive only the image/crop data required for the operation.

Do not send unnecessary case metadata into the model service.

---

# 164. SERVICE-TO-SERVICE AUTHORIZATION

If inference is a separate service:

    API/worker
       ↓
    authenticated service request
       ↓
    inference

Use the existing internal service security pattern.

---

# 165. SERVICE HEALTH

Inference service health should distinguish:

    service process healthy
    model loaded
    GPU available
    inference functional

A process that is alive but cannot infer is not operationally READY.

---

# 166. MODEL RESOURCE QUOTAS

Use resource quotas where necessary:

    max concurrent inference
    max batch
    max image size
    max processing duration

This protects multi-job operation.

---

# 167. JOB FAIRNESS

One case should not automatically monopolize all face-analysis resources.

Where needed use:

    queue priority
    concurrency limits
    per-case limits

---

# 168. DATA RESIDENCY

Face data must remain within the project's approved storage/deployment regions.

Do not move sensitive data to a third-party hosted inference API without explicit approval.

---

# 169. NETWORK RESTRICTIONS

Production local inference should not require external network access for each image/frame.

This reduces:

- latency
- data exposure
- provider dependency
- rate-limit risk

---

# 170. OFFLINE MODEL PACKAGE

When using local models:

    deploy approved artifacts
       ↓
    verify integrity
       ↓
    load locally

Do not allow workers to download models from arbitrary URLs during case processing.

---

# 171. MODEL STORAGE PERMISSIONS

Only the required runtime/service account should read model artifacts where security policy requires such restriction.

---

# 172. MODEL ARTIFACT BACKUP

Back up model deployment metadata and approved artifacts according to infrastructure policy.

Do not put model binaries into Git unless repository policy explicitly permits and the artifact is appropriate for version control.

---

# 173. MODEL LICENSE DOCUMENTATION

The deployment documentation must identify:

    model
    provider
    version
    license status
    intended environment

A model cannot be "approved" based on memory or assumption.

---

# 174. EVALUATION API SEPARATION

If the team uses a hosted InsightFace evaluation API:

    evaluation environment

must be isolated from:

    production runtime

Do not accidentally configure production to use evaluation credentials.

---

# 175. TEST ENVIRONMENT

The test environment should use:

- synthetic/public test images
- controlled videos
- non-production credentials
- non-production model configuration where appropriate

---

# 176. BENCHMARK REPRODUCIBILITY

Benchmark documentation must record:

    model
    runtime
    hardware
    video
    resolution
    FPS
    sample rate
    batch size
    execution provider

Without these values, the result is incomplete.

---

# 177. ACCURACY CLAIMS

Do not state:

    "99% accurate"

without a defined:

    dataset
    protocol
    population
    metric
    operating point

A generic benchmark number is not a CrimeKit production guarantee.

---

# 178. FALSE MATCH COST

The evaluation process must explicitly consider false matches.

A face search system can create investigative noise if false candidates are frequent.

Threshold and aggregation policy should therefore be evaluated jointly.

---

# 179. TRACK CONSISTENCY

A candidate appearing consistently over a track may be stronger evidence than a single isolated observation, but the system must document the aggregation rule rather than inventing a legal certainty.

---

# 180. NO LEGAL CONCLUSION

Even if:

    similarity = high
    quality = good
    track = long

the system must still produce an investigative candidate rather than a legal conclusion.

---

# 181. REFERENCE ENROLLMENT

If a reference is saved for future investigation:

    enrollment
       ↓
    authorized case scope
       ↓
    protected embedding

Do not automatically create a globally searchable biometric identity.

---

# 182. FACE COLLECTION

The system may later support case-specific face collections.

Example:

    Case-001
       ├── Reference A
       ├── Reference B
       └── Reference C

Each collection must inherit the case authorization model.

---

# 183. FACE CLUSTERING

Future unsupervised clustering may identify recurring unknown faces.

This is a separate feature.

Do not mix unknown-face clustering with reference-face search in the first implementation.

---

# 184. UNKNOWN FACES

An unknown detected face may be stored as an observation without assigning a person identity.

Correct:

    Unknown Face Observation

Incorrect:

    Unknown Criminal

---

# 185. CANDIDATE IDENTITY LINK

A candidate identity link should be represented explicitly as a hypothesis/association.

It should remain distinguishable from:

    investigator-confirmed entity relationship

---

# 186. REVIEWED CANDIDATE

When an investigator reviews a candidate:

    machine result
       +
    human review

becomes a new domain state.

Do not mutate historical machine output to make it appear human-generated.

---

# 187. MODEL OUTPUT STORAGE

Keep the minimum required model output.

Do not store unnecessary raw intermediate tensors.

---

# 188. RAW IMAGE RETENTION

Raw face crops should be retained only when required by the forensic workflow and retention policy.

Do not automatically save every detected face crop from every frame.

---

# 189. DERIVED FRAME RETENTION

If source-frame snapshots are generated:

    link them to source
    protect access
    apply retention policy

Do not create unbounded derived-image storage.

---

# 190. MODEL SERVICE LOGGING

At INFO level, prefer:

    request/job ID
    latency
    model version
    execution provider
    outcome

At DEBUG level, still do not expose raw embeddings or secrets.

---

# 191. DEBUGGING SIMILARITY ISSUES

When investigating poor matches, inspect:

    source quality
    detector bbox
    crop/alignment
    model version
    embedding dimension
    normalization
    similarity metric
    threshold policy

Do not immediately change the threshold.

---

# 192. DEBUGGING FALSE MATCHES

Inspect:

    candidate quality
    similarity distribution
    track consistency
    reference quality
    model/version
    policy version
    dataset bias
    vector-search configuration

---

# 193. VECTOR SEARCH VS DIRECT COMPARISON

Use direct comparison when:

    one reference
    modest candidate set
    low query complexity

Use pgvector when:

    many stored embeddings
    repeated searches
    large candidate collection
    retrieval latency matters

Do not add vector infrastructure unnecessarily.

---

# 194. MODEL OUTPUT COMPATIBILITY TEST

Before activating any new InsightFace package/model:

    detect known fixture
       ↓
    generate embedding
       ↓
    validate dimension
       ↓
    compare known pairs/non-pairs
       ↓
    performance test

Only then approve activation.

---

# 195. VERSIONED PREPROCESSING

If preprocessing changes materially:

    preprocessing_version = new version

Historical results retain the old preprocessing metadata.

---

# 196. VERSIONED MATCHING

If matching logic changes:

    matching_policy_version = new version

Historical candidates retain the old policy metadata.

---

# 197. VERSIONED TRACKER

If tracker implementation/configuration changes materially:

    tracker_version = new version

Historical tracks remain attributable.

---

# 198. COMPLETE PROCESSING CONTEXT

A face result should conceptually identify:

    model
    detector
    tracker
    preprocessing
    matching policy
    runtime
    execution provider
    processing run

This is the complete forensic processing context.

---

# 199. MODEL CONFIG SNAPSHOT

Where practical, persist a safe configuration snapshot or immutable configuration ID associated with a run.

Do not rely on whatever configuration happens to exist months later.

---

# 200. FINAL INSIGHTFACE ARCHITECTURE CONTRACT

The authoritative integration is:

    CrimeKit API
          ↓
    Authorization
          ↓
    Workflow / Worker
          ↓
    FaceModelProvider
          ↓
    InsightFace Adapter
          ↓
    Face Detection
          ↓
    Quality / Preprocessing
          ↓
    InsightFace Recognition
          ↓
    Embedding Validation
          ↓
    Matching Layer
          ↓
    Track/Sighting Aggregation
          ↓
    Provenance
          ↓
    Persistence
          ↓
    Realtime Event
          ↓
    Investigator Review

InsightFace provides the model capability.

CrimeKit provides the forensic system around that capability.

The implementation must therefore optimize for:

    MODEL CORRECTNESS
    MODEL VERSIONING
    LICENSING AWARENESS
    PERFORMANCE
    SECURITY
    FORENSIC PROVENANCE
    REPRODUCIBILITY
    HUMAN REVIEW
    OPERATIONAL RELIABILITY

and must never reduce the system to:

    image
      ↓
    model
      ↓
    similarity
      ↓
    "person identified"

That simplified pipeline is not sufficient for CrimeKit.
