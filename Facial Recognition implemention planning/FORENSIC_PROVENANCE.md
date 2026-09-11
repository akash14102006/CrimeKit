# CrimeKit Face Trace Investigator — FORENSIC PROVENANCE SPECIFICATION

**Document:** `FORENSIC_PROVENANCE.md`  
**Subsystem:** Face Trace Investigator  
**Purpose:** Define the complete evidentiary lineage of every machine-generated face observation, candidate, and sighting  
**Audience:** Forensic engineers, backend engineers, database engineers, security, QA, reporting, investigators  
**Status:** Authoritative provenance specification

---

# 1. PURPOSE

This document defines how CrimeKit preserves the complete provenance of face-analysis results.

A face-recognition result is not complete merely because the system has:

    similarity = 0.91

A complete CrimeKit result must answer:

    What source produced this?
    Which exact artifact?
    Which frame?
    Which timestamp?
    Which face detection?
    Which track?
    Which embedding?
    Which model?
    Which preprocessing?
    Which matching policy?
    Which processing run?
    Who reviewed it?
    When?

The core provenance principle is:

> Every machine-generated face finding must be traceable back to the original authorized evidence without ambiguity.

---

# 2. FORENSIC PRINCIPLE

The authoritative relationship is:

    Original Evidence
          ↓
    Derived Artifact
          ↓
    Source Frame
          ↓
    Face Detection
          ↓
    Face Track
          ↓
    Face Embedding
          ↓
    Candidate Observation
          ↓
    Face Sighting
          ↓
    Investigator Review

Each stage must preserve enough information to identify its upstream source.

---

# 3. WHAT PROVENANCE MEANS IN CRIMEKIT

For this subsystem, provenance means:

- source identity
- source version/state
- exact artifact identity
- processing run
- source frame
- timestamp
- spatial location in frame
- detector identity/version
- tracker identity/version
- recognition model identity/version
- preprocessing version
- matching policy version
- generated result
- investigator review history

Provenance is a domain requirement, not optional logging.

---

# 4. SOURCE OF TRUTH

The original evidence remains authoritative.

Face intelligence generates derived records.

Conceptually:

    SOURCE
       ↓
    DERIVED

Never:

    DERIVED
       ↓
    overwrite SOURCE

---

# 5. ORIGINAL EVIDENCE

Every face investigation must reference an existing CrimeKit evidence record whenever the product workflow is based on case evidence.

At minimum, preserve:

    evidence_id
    case_id
    artifact_id where applicable
    source metadata
    evidence status

Do not create a second unrelated evidence identity for the same source.

---

# 6. EVIDENCE IMMUTABILITY

The Face Trace subsystem must never:

- overwrite original video
- overwrite original image
- replace original media
- destructively annotate source media
- crop the original in place
- re-encode the original in place

All processing outputs are derived artifacts.

---

# 7. EVIDENCE HASH / INTEGRITY

If the existing CrimeKit evidence system records cryptographic hashes, Face Trace must retain references to those authoritative evidence-integrity records.

Do not create an independent competing evidence-integrity system unless the architecture requires it.

Where a derived artifact is hashed, clearly distinguish:

    source evidence hash

from:

    derived artifact hash

---

# 8. ARTIFACT IDENTITY

Every processed input should have a stable artifact identity.

Examples:

    EVIDENCE-001
    ARTIFACT-0042
    VIDEO-0007

The actual identifier format follows existing CrimeKit conventions.

Do not use filenames as the authoritative identity.

---

# 9. PROCESSING RUN

Every significant Face Trace execution must have a Processing Run.

Example:

    RUN-000391

The processing run records the environment/context that produced results.

---

# 10. PROCESSING RUN RESPONSIBILITY

A Processing Run should identify:

    investigation_id
    job_id
    evidence scope
    model
    model version
    detector version
    tracker version
    preprocessing version
    matching policy version
    runtime
    execution provider
    worker
    configuration/profile
    start time
    end time
    outcome

This is the core reproducibility boundary.

---

# 11. PROCESSING RUN LIFECYCLE

Conceptual:

    CREATED
       ↓
    STARTED
       ↓
    PROCESSING
       ↓
    FINALIZING
       ↓
    COMPLETED

Failure:

    FAILED

Cancellation:

    CANCELLED

Actual state names must follow the existing workflow architecture.

---

# 12. PROCESSING RUN IMMUTABILITY

Once a Processing Run has produced forensic results, its processing context must not be silently changed.

If:

    model version changes

create a new run.

If:

    matching policy changes

create a new run or processing context according to domain design.

Do not rewrite history.

---

# 13. SOURCE FRAME

A video-derived face observation must identify the source frame.

Minimum:

    evidence_id
    artifact_id
    frame_number where available
    source timestamp
    processing run ID

Frame numbering is not a substitute for timestamp.

Preserve both when available.

---

# 14. SOURCE TIMESTAMP

The source/event timestamp is the primary temporal reference where reliable source timing exists.

Do not replace it with:

    processing wall-clock time

Store processing time separately.

---

# 15. PROCESSING TIMESTAMP

Processing timestamp may indicate:

    when CrimeKit analyzed the frame

It must not be silently interpreted as:

    when the event occurred

---

# 16. FRAME POSITION

Where a face detection exists, preserve:

    bbox
    frame width/height as needed
    keypoints where supported

The bounding box allows the investigator to locate the machine-observed face.

---

# 17. DETECTION PROVENANCE

A Face Detection must identify:

    detection_id
    evidence_id
    artifact_id
    frame_number
    source_timestamp
    bbox
    detector_score
    processing_run_id

Optional:

    keypoints
    quality metadata

---

# 18. DETECTION VERSION

Record the detector implementation/model when required by the processing context.

Example:

    detector_model = SCRFD
    detector_version = X

Do not assume the current detector configuration explains historical detections.

---

# 19. FACE QUALITY PROVENANCE

If the detection passes through a quality gate, retain:

    quality_policy/version
    quality state
    relevant measurements

Example:

    quality_state = GOOD
    face_size = ...
    blur = ...
    pose = ...

The exact fields follow the implementation.

---

# 20. QUALITY DECISION LINEAGE

A candidate should be able to answer:

    Was the observation quality-approved?

The provenance path is:

    Detection
       ↓
    Quality Evaluation
       ↓
    Eligible / Rejected
       ↓
    Embedding if eligible

Do not lose the reason an observation was rejected where operationally useful.

---

# 21. TRACK PROVENANCE

A Face Track groups temporal detections.

It must identify:

    track_id
    source artifact
    processing run
    first timestamp
    last timestamp
    detection IDs
    tracker version

---

# 22. TRACK SEMANTICS

A track means:

> These observations were associated by the tracking algorithm as one visual track.

It does not mean:

> These observations are legally or conclusively the same person.

Do not allow UI/database semantics to collapse these concepts.

---

# 23. TRACK SOURCE NAMESPACE

Track IDs should be unique within an appropriate source/run namespace.

Do not assume:

    TRACK-017 in CCTV-01
    =
    TRACK-017 in CCTV-02

unless a separate correlation entity establishes that relationship.

---

# 24. TRACK LIFECYCLE

Recommended conceptual states:

    CREATED
    ACTIVE
    LOST
    CLOSED

The actual implementation follows the selected tracker and CrimeKit workflow.

---

# 25. TRACK VERSION

Where relevant, retain:

    tracker
    tracker version
    tracker configuration/profile

Historical tracks must remain attributable to the tracker that created them.

---

# 26. EMBEDDING PROVENANCE

Every stored embedding must identify:

    source detection/track
    processing run
    model provider
    model ID
    model version
    embedding dimension
    preprocessing version

Do not store a vector without its generating context.

---

# 27. EMBEDDING IDENTITY

An embedding is a derived representation.

It is not itself the authoritative identity of a person.

The data model should avoid implying:

    embedding = person

Instead:

    embedding
       ↓
    generated from observation/reference
       ↓
    used for candidate comparison

---

# 28. REFERENCE EMBEDDING PROVENANCE

A reference embedding must link to:

    case
    investigation
    reference artifact
    reference face selection
    processing run
    model/version
    preprocessing/version

---

# 29. CANDIDATE OBSERVATION PROVENANCE

A Candidate Observation should contain or reference:

    candidate_observation_id
    investigation_id
    evidence_id
    artifact_id
    detection_id
    track_id
    embedding_id where persisted
    similarity
    quality context
    model/version
    policy/version
    processing_run_id
    timestamp

---

# 30. CANDIDATE SEMANTICS

A candidate represents:

> A machine-generated comparison result that merits investigator attention under the configured matching policy.

It does not represent:

- guilt
- criminal status
- legal identity
- conviction
- automatic proof

---

# 31. SIMILARITY PROVENANCE

Every similarity value must be attributable to:

    reference embedding
    candidate embedding
    similarity metric
    model compatibility
    processing run

Do not store:

    similarity = 0.91

without knowing what produced the values.

---

# 32. SIMILARITY METRIC

Record the metric used.

Example:

    cosine similarity

Do not assume all providers use the same metric.

---

# 33. MATCHING POLICY PROVENANCE

Each candidate must identify:

    matching_policy_id
    matching_policy_version

The policy should define relevant:

    thresholds
    quality requirements
    aggregation rules

---

# 34. THRESHOLD PROVENANCE

A candidate result must be explainable against the policy that existed at the time of processing.

Do not evaluate historical candidates using today's threshold and present that as historical truth.

---

# 35. MODEL PROVENANCE

Record at least:

    provider
    model ID
    model name
    model version
    embedding dimension

Where needed also record:

    detector model
    tracker
    runtime

---

# 36. PREPROCESSING PROVENANCE

Preprocessing may materially affect face embeddings.

Therefore record:

    preprocessing version/profile

where material.

The exact implementation must be documented.

---

# 37. RUNTIME PROVENANCE

Record relevant runtime context:

    Python/runtime version
    ONNX Runtime version
    execution provider

where required to explain historical behavior.

Do not store every host detail unless operational policy requires it.

---

# 38. EXECUTION PROVIDER

Where applicable record:

    CUDAExecutionProvider
    CPUExecutionProvider
    TensorRTExecutionProvider

or the actual selected runtime provider.

Historical output should reflect actual execution.

---

# 39. CONFIGURATION PROVENANCE

Where processing behavior depends on configuration, associate an immutable configuration/profile identifier with the run.

Do not rely exclusively on the mutable current environment.

---

# 40. EVIDENCE SCOPE PROVENANCE

The search must record exactly what evidence scope was selected.

Examples:

    selected evidence
    selected videos
    entire case

For a multi-source search, record the individual source IDs.

---

# 41. SEARCH REQUEST PROVENANCE

Record:

    requester
    case
    investigation
    requested scope
    created time
    idempotency key where applicable

Do not store unnecessary sensitive request payloads.

---

# 42. ACTOR PROVENANCE

Distinguish:

    initiated_by = investigator
    executed_by = worker/service

This preserves the distinction between human action and machine execution.

---

# 43. REVIEW PROVENANCE

Every investigator review should identify:

    reviewer
    review timestamp
    candidate/sighting
    previous status
    new status
    reason/notes where required

---

# 44. REVIEW HISTORY

Do not simply overwrite review history when the audit model requires historical transitions.

Example:

    PENDING
       ↓
    NEEDS_FURTHER_REVIEW
       ↓
    REJECTED

The transition history remains available.

---

# 45. HUMAN VS MACHINE PROVENANCE

The system must clearly distinguish:

    Machine-generated candidate

from:

    Human investigator review

Never attribute a machine conclusion to a human.

Never attribute a human review decision to the model.

---

# 46. SIGHTING PROVENANCE

A Face Sighting is an aggregation of observations.

It must identify:

    sighting_id
    evidence
    track
    source time range
    best candidate observation
    observation count
    processing run
    matching policy
    model context

---

# 47. SIGHTING AGGREGATION PROVENANCE

The system must preserve the underlying observations used to form a sighting.

Example:

    Detection 101
    Detection 102
    Detection 103
          ↓
    Sighting 001

The observations must remain discoverable.

---

# 48. SIGHTING TIME RANGE

Store:

    first_observed_at
    last_observed_at

These represent the source-observation window.

Do not substitute job processing time.

---

# 49. BEST OBSERVATION

If the sighting records a best frame:

    best_observation_id

must reference the exact underlying candidate observation.

Do not create a synthetic frame that has no source lineage.

---

# 50. SOURCE FRAME RECOVERY

For every video-derived candidate/sighting, the system should support:

    candidate
       ↓
    sighting
       ↓
    track/detection
       ↓
    frame
       ↓
    source evidence

This is a core acceptance criterion.

---

# 51. SOURCE FRAME INTEGRITY

The source frame should be obtained from the authoritative evidence/media pipeline.

An annotated display frame is derived/presentation data.

Do not replace source evidence with an annotated copy.

---

# 52. DERIVED FRAME PROVENANCE

If a snapshot is generated:

    derived_frame_id
    source_artifact_id
    frame_number
    timestamp
    bbox
    processing_run_id

must be recorded as appropriate.

---

# 53. FACE CROP PROVENANCE

If a face crop is retained:

    crop_id
    source_frame
    bbox
    processing_run
    model/preprocessing context

must be linked.

Do not retain anonymous image files without provenance.

---

# 54. ANNOTATED FRAME PROVENANCE

If an annotated frame is created for the UI:

    original source frame
       +
    overlay
       ↓
    derived display artifact

It must be clearly marked as derived.

Never overwrite the original.

---

# 55. PROVENANCE TREE

Conceptual tree:

    Case
    └── Investigation
        ├── Reference
        │   └── Reference Embedding
        │
        └── Search Job
            └── Processing Run
                ├── Evidence
                │   └── Video
                │       └── Frame
                │           └── Detection
                │               └── Track
                │                   └── Embedding
                │                       └── Candidate
                │                           └── Sighting
                │                               └── Review

The exact database model may differ, but the semantic lineage must remain.

---

# 56. PROVENANCE GRAPH

For graph-capable systems:

    Evidence
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

These relationships may be represented in Neo4j where appropriate.

The relational forensic record remains authoritative.

---

# 57. PROVENANCE EDGE REQUIREMENT

Any face-derived graph relationship must identify its source domain record.

Example:

    FaceSighting
       └── FROM_EVIDENCE → Evidence

The edge should be explainable through the corresponding relational record.

---

# 58. GRAPH PROJECTION PROVENANCE

When a graph projection is created, retain enough information to identify:

    source domain record
    projection/version if relevant
    projection time

Do not make an inference edge impossible to trace.

---

# 59. VECTOR PROJECTION PROVENANCE

Vector-search records should identify:

    source embedding
    model/version
    case scope
    processing context

A vector index must not become an anonymous biometric database.

---

# 60. VECTOR INDEX VERSION

If the vector-search configuration changes materially, record:

    index/version/profile

where necessary to explain historical retrieval behavior.

---

# 61. PROVENANCE ACROSS DISTRIBUTED SYSTEMS

The subsystem may span:

    API
    workflow
    video worker
    inference worker
    database
    vector store
    graph
    event system

Use correlation IDs:

    request_id
    investigation_id
    job_id
    processing_run_id

to connect operations across services.

---

# 62. DISTRIBUTED TRACE

A processing operation should conceptually trace:

    request
      ↓
    job
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

This is operational traceability.

It supplements forensic provenance.

---

# 63. FORENSIC VS OPERATIONAL PROVENANCE

Keep separate:

## Forensic provenance

    where did the evidence/result originate?

## Operational trace

    which service/process handled it?

Both are useful.

Neither should replace the other.

---

# 64. PROVENANCE OF FAILED PROCESSING

Failed processing attempts may still need provenance.

Example:

    RUN-003
    Evidence = CCTV-02
    Failure = decode error

This helps establish what was and was not processed.

---

# 65. PARTIAL PROCESSING PROVENANCE

For a partially completed search:

    CCTV-01 → completed
    CCTV-02 → failed
    CCTV-03 → processing

the system must preserve source-level status.

Do not flatten it to:

    search completed

---

# 66. SKIPPED FRAME PROVENANCE

If frame sampling intentionally skips source frames:

    sampling profile

must be associated with the Processing Run.

The system should make the processing scope understandable.

Do not claim that every frame was analyzed when it was not.

---

# 67. DROPPED FRAME PROVENANCE

If frames are dropped because of resource/backpressure conditions, record relevant processing statistics/state where required.

Do not silently represent a degraded run as full frame coverage.

---

# 68. TIMESTAMP PROVENANCE

Where timestamps come from:

    source metadata
    decoder
    container
    camera stream

the source should be preserved where the implementation can reliably identify it.

Do not invent source precision.

---

# 69. CLOCK DIFFERENCE

For live CCTV, distinguish:

    source capture time
    processing time
    event publication time

These can differ.

Do not confuse them.

---

# 70. TIMEZONE PROVENANCE

Store canonical timestamps according to CrimeKit's temporal policy.

Where source timezone matters, preserve the source context.

Do not silently rewrite historical event times.

---

# 71. EVIDENCE VERSIONING

If CrimeKit evidence has versions:

    result → evidence version

must remain attributable.

A later replacement must not silently make an old processing run appear to have analyzed the new media.

---

# 72. SOURCE REVISION

If evidence metadata changes after processing:

    historical processing context

must remain interpretable.

Do not mutate past processing records to reflect current metadata.

---

# 73. PROCESSING RE-RUN

When reprocessing:

    new processing run

must be created.

Old output remains associated with old run.

---

# 74. MODEL RE-RUN

When testing a new model:

    new processing run
    new model version
    new embedding context

Do not overwrite old model results.

---

# 75. THRESHOLD RE-RUN

Changing matching policy requires a new evaluation/processing context if it materially changes result classification.

Do not silently recalculate old candidate labels without preserving historical state.

---

# 76. REVIEW AFTER REPROCESSING

If a new processing run produces a new candidate for the same source:

    old candidate
    new candidate

must remain distinguishable.

Do not merge them without explicit domain semantics.

---

# 77. PROVENANCE AND DEDUPLICATION

Deduplication may combine observations into a sighting.

It must not erase the underlying source identities.

---

# 78. PROVENANCE AND RETENTION

Retention policies must consider the complete lineage:

    reference
    embedding
    detection
    track
    candidate
    sighting
    derived crop
    source-frame snapshot

Deleting one record must not accidentally leave an untraceable biometric artifact.

---

# 79. PROVENANCE AND DELETION

When a derived record is deleted:

    determine whether dependent derived records
    must also be deleted/expired.

Follow the governing CrimeKit retention policy.

---

# 80. PROVENANCE AND LEGAL HOLD

If evidence is under preservation/legal hold:

    related face-intelligence artifacts should follow the applicable preservation policy.

Do not automatically purge protected data.

---

# 81. PROVENANCE ACCESS CONTROL

Provenance must itself be access-controlled.

A user authorized to view a candidate should not automatically see restricted unrelated case data through provenance traversal.

---

# 82. PROVENANCE SIDE CHANNEL

A provenance API must not reveal:

    existence of hidden evidence
    hidden case names
    unauthorized persons
    restricted relationships

through error messages or graph traversal.

---

# 83. PROVENANCE API

Potential endpoint:

    GET /face-sightings/{sighting_id}/provenance

It should return an authorized lineage.

Exact API path follows CrimeKit conventions.

---

# 84. PROVENANCE RESPONSE

Potential response structure:

    sighting
      ↓
    evidence
      ↓
    frame
      ↓
    detection
      ↓
    track
      ↓
    processing run
      ↓
    model
      ↓
    matching policy
      ↓
    review

Do not expose raw biometric vectors.

---

# 85. PROVENANCE UI

Recommended visible sequence:

    Source Evidence
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

Technical metadata can appear in an advanced section.

---

# 86. PROVENANCE "WHY" VIEW

The investigator should be able to answer:

    Why did CrimeKit show this?

Possible visible evidence:

    Similarity
    Quality
    Track
    Source
    Timestamp
    Model
    Policy

Do not generate unsupported explanations.

---

# 87. MACHINE-GENERATED LABEL

Candidate UI/API should identify:

    machine_generated = true

or equivalent domain semantics.

Do not imply human authorship.

---

# 88. HUMAN REVIEW LABEL

Review should explicitly identify:

    reviewed_by
    reviewed_at
    decision

Do not infer review from the existence of a candidate.

---

# 89. AUDIT VS PROVENANCE

Audit answers:

    Who did what?

Provenance answers:

    Where did this result come from?

Both are required.

---

# 90. SOURCE-OF-TRUTH MATRIX

Recommended:

| Information | Authoritative source |
|---|---|
| Case | CrimeKit relational/domain layer |
| Evidence | CrimeKit evidence system |
| Source media | Approved evidence storage |
| Processing state | Workflow/domain |
| Face result metadata | PostgreSQL/domain |
| Embedding retrieval | pgvector |
| Relationship projection | Neo4j |
| Live delivery | Event/WebSocket layer |
| Human review | Review/audit domain |

Do not make a secondary store silently authoritative.

---

# 91. PROVENANCE CONSISTENCY

When multiple stores contain references to the same domain object:

    use stable domain IDs

Example:

    sighting_id = S-001

may be referenced by:

    PostgreSQL
    Neo4j
    event
    frontend

---

# 92. EVENT PROVENANCE

A face event should identify:

    event_id
    event_type
    event_version
    occurred_at
    investigation_id
    job_id
    aggregate ID

Events should reference domain records rather than reproduce all sensitive data.

---

# 93. EVENT TO RECORD TRACE

An event such as:

    face_sighting.created

must be resolvable to the authoritative sighting record.

---

# 94. EVENT REPLAY

If events are replayed:

    replayed event

must not create an indistinguishable new forensic fact.

Use idempotent projections.

---

# 95. PROJECTION STATUS

If Neo4j/vector projection is asynchronous:

    projection status

may be retained where useful.

Example:

    PostgreSQL = authoritative
    Neo4j = projected
    projection_status = COMPLETE

---

# 96. FAILED PROJECTION

Example:

    Sighting persisted
       ↓
    Neo4j projection failed

The relational sighting remains authoritative.

Graph should show:

    projection pending/failed

not:

    no sighting exists

---

# 97. PROVENANCE RECONCILIATION

Operational tooling should support finding:

    relational records without graph projections
    embeddings without valid source records
    derived crops without provenance
    candidates without processing runs

These are integrity exceptions.

---

# 98. ORPHAN DETECTION

Periodic integrity checks may detect:

    orphan embedding
    orphan candidate
    orphan sighting
    orphan derived artifact

These should be observable and remediated.

---

# 99. PROVENANCE INTEGRITY CHECK

A validation job may verify:

    every candidate
       → processing run exists

    every sighting
       → source evidence exists

    every source frame
       → frame context exists

    every embedding
       → model metadata exists

---

# 100. PROVENANCE FAILURE POLICY

If provenance is incomplete:

    do not promote the result to normal investigator output

unless the domain policy explicitly defines a degraded state.

---

# 101. PROVENANCE REPAIR

Repair mechanisms must not fabricate missing history.

If a relationship can be safely reconstructed from authoritative records:

    repair

Otherwise:

    flag as incomplete

Do not guess.

---

# 102. DATABASE CONSTRAINTS

Use relational constraints where practical to protect provenance relationships.

Examples:

    foreign keys
    unique IDs
    non-null critical references

---

# 103. PROVENANCE TRANSACTION

When creating a critical forensic record, use an appropriate transaction so the record is not committed without required provenance metadata.

---

# 104. DISTRIBUTED TRANSACTION

Do not assume one transaction can atomically cover:

    PostgreSQL
    pgvector
    Neo4j
    Redis

Use controlled projection/event patterns where needed.

---

# 105. PROVENANCE DURABILITY

Once a valid forensic result is persisted, event delivery failure must not erase its source lineage.

---

# 106. PROVENANCE BACKUP

Back up relevant provenance records with the primary domain data.

A backup containing results but not provenance is incomplete.

---

# 107. PROVENANCE RESTORE

After restore, verify that:

    candidate
       ↓
    sighting
       ↓
    source evidence

relationships remain navigable.

---

# 108. PROVENANCE EXPORT

Reports/exports should preserve enough provenance to identify:

    source
    time
    frame
    model
    policy
    review

Do not export more sensitive data than required.

---

# 109. REPORT LANGUAGE

Recommended:

    "Machine-generated candidate derived from CCTV-02,
     frame 9921, at 14:21:03, using the recorded processing run."

Avoid:

    "AI proved the suspect was present."

---

# 110. COURT/FORENSIC PRESENTATION

Where CrimeKit produces court-oriented reports, the reporting layer must use the stored authoritative provenance.

Do not regenerate unsupported claims at report time.

---

# 111. PROVENANCE AND INVESTIGATOR NOTES

Investigator notes should reference the relevant:

    candidate
    sighting
    evidence

rather than becoming the sole record of what was observed.

---

# 112. COMMENTARY VS EVIDENCE

Investigator comments are human commentary.

They must remain distinguishable from:

    source evidence
    machine observation
    system-generated metadata

---

# 113. PROVENANCE OF REVIEW NOTES

Where review notes are retained:

    reviewer
    timestamp
    target candidate/sighting

must be identifiable.

---

# 114. PROVENANCE AND GRAPH EXPLANATION

When graph UI highlights a face-derived edge:

    edge
       ↓
    source sighting
       ↓
    source evidence

must remain accessible.

---

# 115. PROVENANCE AND TIMELINE

Timeline events should retain:

    sighting ID
    source evidence
    source timestamp

A timeline point without source context is incomplete.

---

# 116. PROVENANCE AND SEARCH RESULTS

Search results should not be treated as authoritative simply because they came from pgvector.

Vector retrieval is a computational retrieval step.

The authoritative forensic candidate record remains the domain result.

---

# 117. PROVENANCE AND MODEL CHANGES

Historical result:

    RUN-001
    Model-A
    Policy-A

New result:

    RUN-002
    Model-B
    Policy-B

Both remain distinct.

---

# 118. PROVENANCE AND THRESHOLD CHANGES

Do not modify a historical candidate from:

    candidate

to:

    rejected

solely because the current threshold changed.

Create a new evaluation/processing interpretation where required.

---

# 119. PROVENANCE AND PREPROCESSING CHANGES

If preprocessing changes materially:

    new preprocessing version

Historical results retain old context.

---

# 120. PROVENANCE AND TRACKER CHANGES

If tracker changes materially:

    new tracker version/context

Historical tracks remain attributable to the old tracker.

---

# 121. PROVENANCE AND MODEL LICENSE

The model identity used for a historical result must remain identifiable even if that model is later deprecated.

Do not erase model identity after deprecation.

---

# 122. PROVENANCE AND MODEL DELETION

Deleting a model artifact from active deployment must not make historical processing metadata meaningless.

Retain model metadata sufficient for historical interpretation under policy.

---

# 123. PROVENANCE AND EXPERIMENTS

Experimental runs must clearly identify:

    experimental model
    experiment ID
    dataset
    processing run

Do not mix experimental output into production history without explicit semantics.

---

# 124. PROVENANCE AND DEMO DATA

Demo results should be explicitly identifiable as:

    test/demo data

and must not be mistaken for real case evidence.

---

# 125. PROVENANCE AND SYNTHETIC DATA

Synthetic test data may be used for evaluation.

Its synthetic status should remain identifiable.

---

# 126. SOURCE MEDIA FINGERPRINTING

If CrimeKit evidence already stores cryptographic hashes, use them to identify source integrity where appropriate.

Do not invent a new hash chain merely for face intelligence.

---

# 127. DERIVED ARTIFACT HASHING

When derived artifacts are retained and need integrity tracking:

    derived artifact hash

may be recorded.

Keep source and derived hashes distinct.

---

# 128. FRAME HASH

A frame hash may be used where operationally useful.

It should not replace:

    evidence ID
    frame number
    timestamp

It is an integrity/supporting identifier, not the complete provenance chain.

---

# 129. PROVENANCE DEPTH

Do not force investigators to traverse every technical node manually.

The UI should provide:

    concise provenance summary
       +
    expandable technical detail

---

# 130. PROVENANCE API PERFORMANCE

Do not generate enormous provenance payloads for list pages.

Use:

    summary
       ↓
    detail on demand

---

# 131. PROVENANCE SECURITY

Technical provenance fields may contain internal identifiers.

Only return what the investigator's role can view.

---

# 132. PROVENANCE PRIVACY

Do not include unrelated personal information in provenance.

Only include information necessary to explain the result.

---

# 133. PROVENANCE ACCESS LOGGING

Where required, access to highly sensitive provenance/source evidence should be auditable.

---

# 134. PROVENANCE EXPORT SECURITY

Export operations must inherit case/evidence permissions.

---

# 135. PROVENANCE DELETION

If retention requires deletion of a derived result:

    remove/expire dependent references according to policy

Do not leave misleading orphan links.

---

# 136. PROVENANCE CONSISTENCY CHECK

A result is considered provenance-complete only if:

[ ] Case identified

[ ] Investigation identified

[ ] Processing run identified

[ ] Source evidence identified

[ ] Artifact identified where applicable

[ ] Source frame identified for video results

[ ] Timestamp identified

[ ] Detection identified

[ ] Track identified where applicable

[ ] Model identified

[ ] Model version identified

[ ] Matching policy identified

[ ] Sighting identified

[ ] Review state identified

---

# 137. PROVENANCE INTEGRITY TEST

Automated tests should prove:

    create candidate
       ↓
    retrieve candidate
       ↓
    retrieve sighting
       ↓
    retrieve source
       ↓
    retrieve frame
       ↓
    retrieve processing context

All relationships must resolve.

---

# 138. PROVENANCE FAILURE TEST

Simulate missing source/provenance relationship.

Expected behavior:

    controlled failure or incomplete state

Never silently substitute another source.

---

# 139. PROVENANCE RETRY TEST

Retrying processing must not create:

    duplicate provenance chains

where idempotency is expected.

---

# 140. PROVENANCE REPLAY TEST

Replaying a projection/event must not create duplicate graph/vector records.

---

# 141. PROVENANCE SECURITY TEST

Attempt:

    candidate from Case B
       ↓
    Case A investigator

Expected:

    denied

---

# 142. PROVENANCE SIDE-CHANNEL TEST

Attempt to request restricted provenance by ID.

Expected:

    no unauthorized source disclosure

---

# 143. SOURCE FRAME TEST

For every accepted test candidate:

    source frame loads
    source metadata matches
    timestamp matches expected fixture
    bbox is within frame

---

# 144. MODEL PROVENANCE TEST

For a real model test:

    result.model_id
    result.model_version

must match the active model context.

---

# 145. POLICY PROVENANCE TEST

Candidate result must identify the matching policy version used to create it.

---

# 146. PROCESSING RUN TEST

Candidate result must resolve to a valid Processing Run.

---

# 147. REPROCESSING TEST

Run the same video with:

    model version A

then:

    model version B

Verify that results remain distinguishable.

---

# 148. RETENTION TEST

Simulate expiration according to policy.

Verify:

    expired embedding no longer searchable
    associated data is handled correctly
    provenance does not falsely claim availability

---

# 149. BACKUP/RESTORE TEST

Restore a test dataset and verify:

    source evidence references
    candidates
    sightings
    review
    provenance

remain consistent.

---

# 150. PROVENANCE REVIEW CHECKLIST

Before release:

[ ] Original evidence is immutable.

[ ] Every candidate has source evidence.

[ ] Every video candidate has frame provenance.

[ ] Every candidate has a processing run.

[ ] Every candidate identifies model/version.

[ ] Every candidate identifies policy/version.

[ ] Tracks are source-scoped.

[ ] Sighting aggregation preserves observations.

[ ] Review history is preserved.

[ ] Graph edges are traceable.

[ ] Vector records are traceable.

[ ] Events reference authoritative records.

[ ] Partial failures are visible.

[ ] Reprocessing creates new context.

[ ] Historical results remain interpretable.

---

# 151. PROVENANCE INCIDENT RESPONSE

If provenance is found to be broken:

    stop promoting affected results
       ↓
    identify affected processing runs
       ↓
    identify affected candidates/sightings
       ↓
    preserve original evidence
       ↓
    investigate integrity issue
       ↓
    repair only from authoritative information
       ↓
    record remediation

Do not silently repair missing history with guessed values.

---

# 152. PROVENANCE QUALITY LEVELS

Where useful, classify:

    COMPLETE
    PARTIAL
    INVALID

Do not call incomplete provenance complete merely because the candidate score exists.

---

# 153. PROVENANCE VALIDATION AT CREATION

Before a candidate is exposed to investigators:

    validate required lineage

If required lineage is missing:

    do not expose as normal candidate

---

# 154. PROVENANCE VALIDATION AT READ

Even after persistence, sensitive read paths may validate key relationships.

This provides defense in depth.

---

# 155. PROVENANCE AND EVENTUAL CONSISTENCY

If graph/vector projections are asynchronous:

    core relational provenance

should remain available before downstream projection completes.

The UI may display:

    Graph projection pending

without losing source evidence context.

---

# 156. PROVENANCE AND CONCURRENCY

Concurrent workers processing the same source must not produce ambiguous provenance.

Use processing-run and source identifiers to separate runs.

---

# 157. PROVENANCE AND DUPLICATE JOBS

If duplicate jobs are intentionally permitted:

    separate processing runs

must remain distinguishable.

If duplicate requests should be idempotent:

    same logical operation

should resolve to one job according to API policy.

---

# 158. PROVENANCE AND JOB CANCELLATION

A cancelled job may still have valid partial results.

Those results retain their original provenance.

---

# 159. PROVENANCE AND JOB FAILURE

A failed job may have partial outputs.

The UI/API must indicate completeness.

Do not discard provenance merely because the overall job failed.

---

# 160. PROVENANCE AND MULTI-SOURCE SEARCH

For a job processing:

    CCTV-01
    CCTV-02
    CCTV-03

every sighting must retain its own source lineage.

---

# 161. PROVENANCE AND LIVE CCTV

Live stream findings must record:

    camera/source ID
    source timestamp
    processing run
    detection/track
    candidate/sighting

Live processing must remain auditable.

---

# 162. LIVE STREAM DISCONNECT

If a camera disconnects:

    source health event

must not erase the previous sightings' provenance.

---

# 163. LIVE CLOCK DRIFT

If source clock synchronization is uncertain:

    preserve source timestamp
    preserve processing timestamp
    expose uncertainty where required

Do not silently rewrite source times.

---

# 164. PROVENANCE AND QUALITY

A candidate should be able to distinguish:

    detection score
    face quality
    similarity

These are different measurements.

---

# 165. PROVENANCE AND CONFIDENCE

Do not store:

    "confidence = 91%"

unless a calibrated confidence model exists.

Prefer:

    similarity
    quality
    candidate tier

with documented semantics.

---

# 166. PROVENANCE AND INVESTIGATIVE ENTITY

If a candidate is associated with an existing CrimeKit entity:

    preserve the candidate provenance

Do not overwrite the candidate with the entity ID and lose the original machine observation.

---

# 167. PROVENANCE AND ENTITY RESOLUTION

If a later identity-resolution process correlates a face candidate with another entity:

    face candidate
       ↓
    identity resolution decision
       ↓
    entity relationship

The original face candidate remains intact.

---

# 168. PROVENANCE AND GRAPH CORRELATION

If a graph relationship is created from a face sighting:

    edge
       ↓
    sighting
       ↓
    source evidence

The relationship is explainable.

---

# 169. PROVENANCE AND AI AGENTS

When an AI agent uses a face finding:

    AI response
       ↓
    structured face result
       ↓
    source evidence

The AI should cite/reference the structured source rather than invent evidence.

---

# 170. AI RESPONSE PROVENANCE

AI-generated explanations must distinguish:

    observed by machine
    inferred by AI
    reviewed by investigator

Do not collapse these categories.

---

# 171. PROVENANCE AND REPORTS

A report generated from a face investigation should consume stored authoritative records.

Do not rerun model inference merely to regenerate evidence history.

---

# 172. REPORT PROVENANCE FIELDS

Where appropriate:

    case
    investigation
    evidence
    source frame
    timestamp
    processing run
    model
    policy
    review state

---

# 173. REPORT VERSION

If a report is regenerated after a new model run:

    report version

must remain distinguishable from the original report when required.

---

# 174. EXPORT INTEGRITY

Exports should preserve stable identifiers where appropriate.

Do not create exported records that cannot be mapped back to the source investigation.

---

# 175. PROVENANCE AND UI THUMBNAILS

A thumbnail is a display artifact.

It must not become the only remaining copy of the source.

---

# 176. SOURCE ARTIFACT LINK

The candidate should always retain an authoritative source-artifact reference.

---

# 177. SOURCE ARTIFACT ACCESS

The UI obtains source data through the secure artifact-access mechanism.

The provenance record does not itself grant access.

---

# 178. PROVENANCE AND AUTHORIZATION

A provenance chain must enforce the same access policy as the underlying evidence.

---

# 179. PROVENANCE AND DELEGATION

If a case is shared with another investigator/agency:

    provenance access

must follow the shared-case permissions.

---

# 180. PROVENANCE AND MULTI-AGENCY

Cross-agency data sharing must not automatically expose:

    hidden case metadata
    unrelated evidence
    unrelated biometric data

---

# 181. PROVENANCE AND DATA RESIDENCY

Provenance records and biometric data must remain within approved environments.

---

# 182. PROVENANCE AND REMOTE PROCESSING

If any remote processing is used:

    provider
    endpoint/service
    processing context

must be recorded as required.

Production architecture should avoid unauthorized external biometric transfer.

---

# 183. PROVENANCE AND HOSTED EVALUATION

If an InsightFace hosted evaluation endpoint is used under authorized evaluation:

    evaluation run

must be clearly distinguished from:

    production/local processing

Do not mix records without clear provider/runtime context.

---

# 184. PROVENANCE AND LICENSED MODELS

If a licensed/private model is used:

    model identity
    license/approval context

should be available in deployment records.

---

# 185. PROVENANCE AND MODEL RETIREMENT

When a model is retired:

    historical results retain model metadata

so investigators can understand historical processing.

---

# 186. PROVENANCE AND SECURITY EVENTS

If unauthorized access occurs:

    access event
       ↓
    audit

Do not modify forensic source data to conceal an access incident.

---

# 187. PROVENANCE AND SECURITY INCIDENTS

A security incident involving face data should identify potentially affected:

    investigations
    evidence
    embeddings
    candidates
    sightings

according to incident-response policy.

---

# 188. PROVENANCE AND DATA BREACH

If biometric data is exposed:

    preserve incident evidence
    contain exposure
    follow security response
    assess affected data

Do not silently delete records to hide exposure.

---

# 189. PROVENANCE AND OPERATIONS

Operations dashboards may show:

    processing run
    job
    evidence ID

but must not expose protected biometric vectors/source images without authorization.

---

# 190. PROVENANCE AND DEBUGGING

Debugging must use identifiers and metadata, not raw biometric vectors.

Preferred:

    run ID
    model version
    similarity
    quality
    frame ID

---

# 191. PROVENANCE AND TESTING

Every critical processing path should have provenance assertions.

Do not consider an inference test successful if it only checks:

    embedding exists

without checking source lineage.

---

# 192. PROVENANCE TEST FIXTURES

Test fixtures should include:

    case
    evidence
    video
    known frame
    expected detection
    expected track
    expected candidate/sighting

Use approved non-sensitive test media.

---

# 193. GOLDEN PROVENANCE TEST

A golden test should be able to validate:

    known source
       ↓
    known frame
       ↓
    known detection
       ↓
    known track
       ↓
    candidate
       ↓
    sighting

The exact similarity may be tolerance-based rather than bit-exact.

---

# 194. PROVENANCE PERFORMANCE

Provenance queries must be performant enough for investigator workflows.

Common query:

    sighting
       ↓
    source frame

should not require an unbounded full-database scan.

---

# 195. PROVENANCE INDEXING

Index common lineage fields:

    case_id
    investigation_id
    evidence_id
    processing_run_id
    track_id
    timestamp
    sighting_id

according to actual query patterns.

---

# 196. PROVENANCE QUERY PAGINATION

Do not return millions of frame observations merely because the user opened provenance.

Use summaries and pagination/on-demand detail.

---

# 197. PROVENANCE API AUTHORIZATION

The provenance endpoint must perform authorization before returning lineage.

---

# 198. PROVENANCE API DATA MINIMIZATION

Return only the fields needed to understand lineage.

Do not expose:

    raw embedding

by default.

---

# 199. FINAL PROVENANCE CONTRACT

The authoritative lineage for Face Trace Investigator is:

    CASE
      ↓
    INVESTIGATION
      ↓
    SEARCH JOB
      ↓
    PROCESSING RUN
      ↓
    SOURCE EVIDENCE
      ↓
    SOURCE ARTIFACT
      ↓
    SOURCE FRAME
      ↓
    FACE DETECTION
      ↓
    QUALITY EVALUATION
      ↓
    FACE TRACK
      ↓
    FACE EMBEDDING
      ↓
    CANDIDATE OBSERVATION
      ↓
    FACE SIGHTING
      ↓
    INVESTIGATOR REVIEW

Every step must retain enough identifiers to navigate backward toward source evidence and forward toward the investigator decision.

---

# 200. FINAL FORENSIC PRINCIPLE

A Face Trace result is not:

    "Similarity = 0.91"

A complete CrimeKit result is:

    "CrimeKit generated a machine candidate from an authorized
     source artifact, at a specific source frame and timestamp,
     using a recorded detector, tracker, recognition model,
     preprocessing version, matching policy, and processing run;
     the candidate was grouped into a traceable sighting and
     remains explicitly distinguishable from investigator review."

That is the provenance standard for CrimeKit Face Trace Investigator.
