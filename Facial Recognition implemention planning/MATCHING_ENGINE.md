# CRIMEKIT — FACE TRACE INVESTIGATOR
# MATCHING ENGINE SPECIFICATION

**Document:** `MATCHING_ENGINE.md`  
**Subsystem:** Face Trace Investigator  
**Scope:** Face embedding comparison, pgvector retrieval, scoring, policy evaluation, candidate ranking, aggregation, deduplication, cross-source correlation, human review  
**Primary concern:** Produce technically correct, explainable, policy-controlled machine candidates without treating similarity as identity or guilt  
**Audience:** ML engineers, backend engineers, forensic engineers, database engineers, security, QA, frontend, investigators  
**Status:** Authoritative implementation specification

---

# 1. PURPOSE

This document defines the matching layer that turns face embeddings into investigator-facing candidate observations.

The matching engine is responsible for:

    Reference Face
          ↓
    Reference Embedding
          ↓
    Authorized Search Scope
          ↓
    Candidate Embeddings
          ↓
    Similarity Retrieval
          ↓
    Policy Evaluation
          ↓
    Candidate Ranking
          ↓
    Deduplication
          ↓
    Sighting Aggregation
          ↓
    Investigator Review

The engine must preserve the distinction between:

    similarity
    candidate
    identity
    human conclusion

These are not interchangeable.

---

# 2. CORE PRINCIPLE

The matching engine answers:

> Which authorized observations are sufficiently similar to the reference under the configured and documented matching policy?

It does not answer:

> Who is legally responsible?

It does not answer:

> Is this person the suspect?

It does not determine guilt.

---

# 3. SCOPE

This specification covers:

- reference embedding preparation
- candidate embedding compatibility
- vector retrieval
- similarity calculation
- threshold policy
- top-K retrieval
- quality gates
- candidate scoring
- candidate ranking
- source-aware aggregation
- duplicate suppression
- cross-camera correlation
- cross-case restrictions
- temporal grouping
- human review state
- explainability
- model/policy provenance
- testing and evaluation
- operational performance

---

# 4. OUT OF SCOPE

This document does not define:

- unauthorized face databases
- unrestricted public-web face search
- autonomous identity decisions
- legal conclusions
- automatic suspect labeling
- criminality prediction
- demographic profiling
- emotion inference
- protected-trait inference

---

# 5. TERMINOLOGY

## 5.1 Reference

The authorized face supplied by the investigator for the investigation.

## 5.2 Reference Embedding

The machine-generated vector representing the reference face under the selected model.

## 5.3 Candidate Embedding

A vector generated from a face observation in authorized evidence.

## 5.4 Candidate Observation

One machine-generated comparison result.

## 5.5 Candidate

A UI/domain representation of one or more observations that merit investigator attention under policy.

## 5.6 Sighting

An aggregated sequence/group of candidate observations associated with the same track/source context.

## 5.7 Similarity

A numerical measure of vector similarity under the selected metric.

## 5.8 Matching Policy

The versioned rules that determine retrieval, filtering, ranking, and aggregation behavior.

---

# 6. NON-NEGOTIABLE RULE

A similarity score is evidence for review, not proof of identity.

Therefore never expose:

    similarity = 0.91
    ↓
    confirmed person

without a human review stage.

---

# 7. MATCHING ARCHITECTURE

Recommended architecture:

    Reference Image
          ↓
    Reference Face Detection
          ↓
    Reference Quality
          ↓
    Reference Embedding
          ↓
    Matching Request
          ↓
    Authorized Scope Filter
          ↓
    pgvector Retrieval
          ↓
    Candidate Compatibility Filter
          ↓
    Similarity / Distance
          ↓
    Matching Policy
          ↓
    Candidate Ranking
          ↓
    Sighting Aggregation
          ↓
    PostgreSQL
          ↓
    Neo4j Projection
          ↓
    Realtime Event
          ↓
    Investigator Review

---

# 8. PROVIDER BOUNDARY

Use an internal abstraction such as:

    FaceEmbeddingProvider

InsightFace should be one provider implementation.

Example:

    FaceEmbeddingProvider
          └── InsightFaceProvider

Do not make the entire CrimeKit matching engine depend directly on one model SDK.

---

# 9. EMBEDDING COMPATIBILITY

A reference embedding may only be compared to candidate embeddings that are compatible with the configured matching policy.

Compatibility may include:

    same model family
    compatible model version
    same dimensionality
    compatible preprocessing
    compatible vector representation

Do not compare incompatible embeddings simply because both are arrays.

---

# 10. MODEL IDENTITY

Matching records must retain:

    provider
    model_id
    model_version
    embedding_dimension

Where material:

    preprocessing_version
    normalization convention

---

# 11. MODEL CONSISTENCY

A single processing run should normally use one defined recognition context.

Do not silently mix:

    Model A embeddings

with:

    Model B reference embeddings

unless the architecture explicitly defines a compatible comparison mechanism.

---

# 12. REFERENCE CREATION

Reference pipeline:

    reference image
       ↓
    detect face
       ↓
    validate exactly intended face
       ↓
    quality check
       ↓
    crop/preprocess
       ↓
    embedding
       ↓
    provenance

---

# 13. REFERENCE MULTI-FACE INPUT

If the investigator uploads an image containing multiple faces:

    do not silently choose one

unless the existing product contract explicitly defines a deterministic selection rule.

Preferred:

    show detected faces
       ↓
    investigator selects reference face

---

# 14. REFERENCE QUALITY

Reference quality should be evaluated before embedding.

Potential signals:

    face size
    blur
    pose
    illumination
    occlusion

Only use fields actually implemented.

---

# 15. REFERENCE REJECTION

If reference quality is insufficient:

    block matching

or explicitly mark:

    low-quality reference

Do not hide the reason.

---

# 16. REFERENCE PROVENANCE

Reference embedding must link to:

    case_id
    investigation_id
    reference artifact
    selected face
    processing run
    model/version
    preprocessing/version

---

# 17. EMBEDDING NORMALIZATION

The matching system must use the normalization semantics expected by the active provider.

For normalized embeddings:

    cosine similarity
    or equivalent dot-product behavior

may be used according to the provider contract.

Do not perform unexplained mathematical transformations.

---

# 18. METRIC

The metric must be explicit.

Example:

    cosine similarity

Alternative metrics must be documented and evaluated before use.

---

# 19. DISTANCE VS SIMILARITY

Do not mix semantics.

For example:

    greater similarity = stronger candidate

while some vector databases expose:

    smaller distance = closer candidate

The adapter must normalize interpretation into a consistent CrimeKit contract.

---

# 20. INTERNAL SCORE CONTRACT

Define a stable domain representation such as:

    raw_similarity
    metric
    rank
    policy_result

Avoid presenting a raw database-specific distance without interpretation.

---

# 21. VECTOR STORE

pgvector is the preferred vector retrieval layer where established by CrimeKit architecture.

It should support:

    authorized nearest-neighbor retrieval
    metadata filtering
    indexing
    scalable retrieval

---

# 22. VECTOR STORE IS NOT SOURCE OF TRUTH

The vector index is a retrieval mechanism.

The authoritative candidate/sighting record remains in the CrimeKit domain persistence layer.

---

# 23. VECTOR RECORD

A vector record should be traceable to:

    embedding_id
    source observation
    case/investigation scope
    model/version
    processing run

---

# 24. VECTOR METADATA FILTERING

Do not retrieve globally and filter authorization later when sensitive cross-case retrieval could occur.

Prefer applying authorization/scope constraints as part of the retrieval architecture.

---

# 25. CASE ISOLATION

Default:

    query only current authorized case/investigation scope

Cross-case matching must be a deliberate capability.

---

# 26. INVESTIGATION ISOLATION

A narrower investigation scope may be applied than case scope.

Example:

    Case A
      ├── Investigation 1
      └── Investigation 2

A search in Investigation 1 must not automatically retrieve Investigation 2 observations.

---

# 27. CROSS-CASE POLICY

If CrimeKit later supports cross-case search:

    explicit authorization
    explicit policy
    explicit audit
    explicit UI labeling

must exist.

---

# 28. RETENTION FILTER

Expired biometric observations must not be retrievable.

Vector retrieval must respect retention state.

---

# 29. SOURCE ACCESS FILTER

Only observations tied to accessible evidence may participate.

---

# 30. VECTOR SEARCH REQUEST

Conceptual request:

    investigation_id
    reference_embedding_id
    search_scope
    model_context
    top_k
    matching_policy_id
    policy_version

Do not accept arbitrary global search parameters from untrusted clients.

---

# 31. TOP-K RETRIEVAL

Top-K means:

    retrieve the K nearest eligible candidates.

It does not mean:

    K valid matches.

---

# 32. TOP-K POLICY

Use a policy-configured upper bound.

Do not allow clients to request:

    K = 1,000,000

and cause uncontrolled workload.

---

# 33. TWO-STAGE RETRIEVAL

A practical design may use:

    Stage 1:
        vector retrieval

    Stage 2:
        policy/ranking evaluation

This allows efficient retrieval while retaining explicit forensic logic.

---

# 34. PRE-FILTERING

Where supported:

    case
    investigation
    source
    model
    retention

should be filtered before expensive candidate evaluation.

---

# 35. POST-FILTERING

Additional rules may be applied after retrieval:

    quality
    time range
    source constraints
    duplicate handling
    threshold

---

# 36. THRESHOLD

Matching thresholds must be versioned policy.

Never scatter thresholds across code.

---

# 37. THRESHOLD MEANING

A threshold means:

> Under this evaluated policy, observations below this criterion are not promoted to the selected candidate tier.

It does not mean:

> score above threshold = certain identity.

---

# 38. MULTI-TIER THRESHOLDS

The system may support tiers such as:

    HIGH_REVIEW_PRIORITY
    REVIEW
    LOW_SIGNAL
    REJECTED

Only if actually implemented and evaluated.

---

# 39. THRESHOLD CALIBRATION

Thresholds must be evaluated with representative validation data.

Do not select values because they:

    "look good in the demo."

---

# 40. THRESHOLD STORAGE

Recommended policy representation:

    matching_policy_id
    version
    metric
    threshold
    top_k
    quality_policy
    aggregation_policy

---

# 41. POLICY IMMUTABILITY

Once a processing run has used a policy version:

    historical result → policy version

must remain stable.

---

# 42. POLICY CHANGE

When threshold changes materially:

    new policy version

and, where required:

    new processing run

---

# 43. SCORE NORMALIZATION

Do not convert similarity into:

    probability

unless a calibrated statistical model exists.

---

# 44. CONFIDENCE LANGUAGE

Avoid:

    91% sure

when the stored value is merely:

    cosine similarity = 0.91

Prefer:

    similarity = 0.91

---

# 45. CANDIDATE QUALITY

Similarity should not be the only candidate signal.

Other eligible signals may include:

    face quality
    track consistency
    observation count
    source context

Only use signals that are implemented and documented.

---

# 46. QUALITY-AWARE RANKING

A candidate with strong similarity but very poor source quality may be ranked differently from a high-quality observation.

The exact formula must be explicitly documented and evaluated.

---

# 47. TRACK-AWARE AGGREGATION

Multiple similar frames from the same track should generally become one sighting rather than independent alerts.

---

# 48. TRACK CONSISTENCY

A sustained sequence of compatible observations may improve review priority.

It must not be represented as independent identity proof.

---

# 49. TEMPORAL CONSISTENCY

Observations from nearby source timestamps may belong to one sighting.

The time-window rule must be configurable/versioned.

---

# 50. SOURCE CONSISTENCY

Observations from one camera/source should preserve their source identity.

Do not merge across cameras without explicit correlation logic.

---

# 51. CROSS-CAMERA CORRELATION

Potential flow:

    Camera A candidate
          +
    Camera B candidate
          ↓
    cross-camera correlation
          ↓
    investigation-level trace

The underlying source sightings remain separate.

---

# 52. CROSS-CAMERA MERGE RULE

Never destroy source-local sightings just because an investigation-level correlation exists.

Use:

    source sighting
       ↓
    higher-level correlation

---

# 53. CROSS-CAMERA TIME

Cross-camera matching should account for source-clock limitations.

Do not assume:

    Camera A 14:20:00
    =
    Camera B 14:20:00

with perfect synchronization.

---

# 54. TRACK-LOCAL DUPLICATION

For:

    20 frames
    one face
    one track

do not normally emit:

    20 separate investigator alerts.

---

# 55. CANDIDATE DE-DUPLICATION KEY

A deduplication strategy may use:

    investigation
    source
    track
    time window
    reference
    processing run

Exact implementation follows the domain model.

---

# 56. DUPLICATE RUNS

Results from separate processing runs must remain distinguishable.

Do not deduplicate across runs so aggressively that model/version history disappears.

---

# 57. REPROCESSING

Example:

    RUN-A → Model-1
    RUN-B → Model-2

Both can produce observations from the same frame.

They are different machine-processing histories.

---

# 58. CANDIDATE IDENTITY

A candidate observation should have its own stable domain ID.

Example:

    CAND-0042

Do not use vector database internal row IDs as the public forensic identifier.

---

# 59. SIGHTING IDENTITY

A sighting should have its own stable domain ID.

Example:

    SIGHT-0091

The sighting references its observations.

---

# 60. RANKING

Ranking should be deterministic for the same:

    input
    model
    policy
    candidate set

where deterministic behavior is expected.

---

# 61. RANKING TIE

Define a stable tie-breaker.

Potential ordering:

    similarity descending
    quality descending
    source timestamp ascending
    stable candidate ID

Use the actual approved rule.

---

# 62. RANKING TRANSPARENCY

The investigator should be able to understand:

    why this candidate is ranked higher

without exposing proprietary/internal implementation details unnecessarily.

---

# 63. EXPLANATION SIGNALS

Potential explanation:

    similarity
    face quality
    source timestamp
    track duration
    observation count
    source camera

These are explanatory signals, not proof.

---

# 64. DO NOT USE UNSUPPORTED SIGNALS

Do not claim:

    "same hairstyle"
    "same clothing"
    "same gait"

unless those signals are actually produced and governed by the relevant subsystem.

---

# 65. MATCHING RESULT SCHEMA

Conceptual:

    candidate_id
    investigation_id
    source_id
    evidence_id
    artifact_id
    detection_id
    track_id
    reference_embedding_id
    candidate_embedding_id
    similarity
    metric
    rank
    quality_state
    matching_policy_id
    policy_version
    processing_run_id
    created_at

Exact schema follows CrimeKit backend conventions.

---

# 66. SOURCE TIMESTAMP

Candidate must retain the source observation timestamp.

---

# 67. PROCESSING TIMESTAMP

Store processing time separately.

Do not conflate:

    observed_at

and:

    processed_at.

---

# 68. FRAME NUMBER

Where available retain:

    frame_number

alongside timestamp.

---

# 69. BOUNDING BOX

Candidate observation may reference:

    bbox

so the investigator can inspect exact face location.

---

# 70. SOURCE FRAME

Candidate should be able to resolve to the source frame through provenance.

---

# 71. CANDIDATE IMAGE

If a face crop is shown:

    derived crop

must link to the source observation.

---

# 72. RAW EMBEDDING EXPOSURE

Do not send raw vectors to the frontend by default.

The investigator needs:

    score
    source
    frame
    timestamp
    provenance

not a 512-dimensional array.

---

# 73. EMBEDDING STORAGE

Retention of every candidate embedding should be deliberate.

Do not assume every intermediate vector must be permanently persisted.

---

# 74. EMBEDDING RETENTION

Retention should follow the biometric/data-retention policy.

---

# 75. SEARCH CACHE

Do not place sensitive vectors/results in globally shared caches.

---

# 76. SEARCH RESULT CACHE

Any cache key must include scope such as:

    case_id
    investigation_id
    reference identity/context
    policy version

according to architecture.

---

# 77. CACHE INVALIDATION

Invalidate/avoid stale results after:

    access changes
    evidence deletion
    policy changes
    retention changes

---

# 78. MATCHING FAILURE

If vector search fails:

    do not report:
        0 matches

Report:

    search unavailable / failed

---

# 79. NO-CANDIDATE RESULT

A successful search with no qualifying candidates means:

    processed successfully
    no candidate met the configured policy

This is different from:

    processing failed.

---

# 80. PARTIAL SEARCH

If some evidence was processed and some failed:

    expose partial completion

Do not report complete coverage.

---

# 81. CANDIDATE PROVENANCE

Every accepted candidate must resolve:

    investigation
    processing run
    evidence
    artifact
    frame/detection where applicable
    model/version
    policy/version

---

# 82. SOURCE-LEVEL STATUS

For a multi-source search:

    source A → complete
    source B → failed
    source C → complete

The UI should reflect this where relevant.

---

# 83. CANDIDATE STATUS

Possible lifecycle:

    MACHINE_GENERATED
       ↓
    REVIEW_PENDING
       ↓
    UNDER_REVIEW
       ↓
    REVIEWED

Review outcomes should follow approved domain vocabulary.

---

# 84. REVIEW OUTCOME

Possible outcome examples:

    RELEVANT
    NOT_RELEVANT
    NEEDS_MORE_CONTEXT

Use actual product terminology.

Do not use:

    GUILTY
    CONFIRMED_CRIMINAL

as machine-review outcomes.

---

# 85. REVIEW IS NOT MODEL TRUTH

A reviewer decision should not overwrite the original similarity result.

Store:

    machine observation
    human review

as distinct facts.

---

# 86. MULTIPLE REVIEWERS

If multi-reviewer workflows are implemented:

    preserve reviewer identity
    preserve timestamp
    preserve each decision

Do not collapse disagreement silently.

---

# 87. REVIEW NOTES

Notes should be associated with the candidate/sighting.

Do not modify source evidence.

---

# 88. DISPUTED RESULT

If reviewers disagree:

    represent disagreement

rather than synthesizing an unsupported "consensus."

---

# 89. AI AGENT CONSUMPTION

An AI agent can query:

    candidate sightings
    source frames
    timestamps
    similarity
    review state

The agent must preserve source references.

---

# 90. AGENT ANSWER

Preferred:

    "CrimeKit has a machine-generated candidate sighting
     at CCTV-02 around 14:21:03, similarity 0.91,
     pending investigator review."

Avoid:

    "The suspect was definitely identified."

---

# 91. AGENT PROVENANCE

Every AI-generated answer should be traceable to structured CrimeKit records.

---

# 92. VECTOR SEARCH AUDIT

Record:

    requester
    time
    investigation
    policy
    scope
    result count

according to audit requirements.

Do not log raw vectors.

---

# 93. MATCHING REQUEST AUDIT

Search initiation should be auditable.

---

# 94. CROSS-CASE SEARCH AUDIT

If cross-case matching is ever enabled:

    stronger audit requirements

should apply.

---

# 95. PERFORMANCE — VECTOR SEARCH

Measure:

    query latency
    candidate count
    filtered count
    final candidates

---

# 96. PERFORMANCE — EMBEDDING

Measure separately:

    preprocessing
    model inference
    vector insertion
    vector query

---

# 97. BATCH MATCHING

Where many candidate embeddings are available, batch retrieval/processing where the vector architecture supports it.

Do not sacrifice authorization filtering for batching.

---

# 98. CONCURRENCY

Bound concurrent matching jobs.

---

# 99. FAIRNESS OF RESOURCE USE

One large investigation must not consume all matching resources indefinitely.

Use:

    quotas
    concurrency limits
    scheduling

as appropriate.

---

# 100. TIMEOUTS

Vector search and downstream matching calls should have bounded timeouts.

---

# 101. RETRY

Retry only safe/idempotent operations.

---

# 102. DATABASE FAILURE

Do not emit a final candidate event if the authoritative candidate state cannot be safely persisted.

---

# 103. EVENT FAILURE

If persistence succeeded but event delivery failed:

    retain durable result
    retry event/projection

Do not lose the candidate.

---

# 104. GRAPH PROJECTION

Neo4j should receive relationship projections from authoritative domain records.

---

# 105. GRAPH MATCH RESULT

A graph relationship should not invent identity.

Example:

    Sighting-42
       → observed_in → CCTV-02

not:

    CCTV-02
       → proves_person_X

---

# 106. TIMELINE PROJECTION

Candidate/sighting can become timeline entries through the common CrimeKit timeline architecture.

---

# 107. TIMELINE LANGUAGE

Use:

    Candidate sighting observed at source time

not:

    Suspect confirmed at source time.

---

# 108. SEARCH FILTERS

Investigator may filter:

    camera
    time range
    candidate tier
    review status
    similarity range

Only filters allowed by policy should be exposed.

---

# 109. TIME RANGE FILTER

Time filtering must use the source event time, not processing time, unless explicitly requested.

---

# 110. SOURCE FILTER

Source filters must remain inside authorized scope.

---

# 111. SIMILARITY FILTER

Similarity filter reflects machine metric.

It must not be represented as confidence probability.

---

# 112. SORTING

Supported sorting may include:

    similarity
    time
    quality
    source

The default sort should follow the product investigation workflow.

---

# 113. PAGINATION

Candidate lists must be paginated.

Do not return all face observations at once.

---

# 114. SEARCH RESULT COUNT

Counts should distinguish:

    retrieved
    policy-qualified
    displayed

---

# 115. CANDIDATE EXPLANATION VIEW

Candidate detail should show:

    reference face
    source frame
    similarity
    metric
    quality
    timestamp
    camera/source
    processing run
    model/version
    policy/version
    review state

---

# 116. SOURCE VERIFICATION

Investigator should be able to move from:

    candidate
       ↓
    source frame
       ↓
    source video/image
       ↓
    evidence record

---

# 117. NO SOURCE = NO TRUST

If source verification is unavailable:

    candidate should be marked accordingly

and should not be presented as fully verified.

---

# 118. CANDIDATE THUMBNAIL

Thumbnail may be optimized for UI.

The source frame remains authoritative.

---

# 119. SOURCE FRAME OVERLAY

Display overlay:

    machine candidate

not:

    confirmed identity.

---

# 120. MATCHING POLICY VERSION IN UI

Advanced details should reveal policy/version for technical review.

---

# 121. MODEL VERSION IN UI

Advanced details should reveal model/version where appropriate.

---

# 122. REVIEW ACTIONS

Possible:

    Mark relevant
    Mark not relevant
    Request more context

Exact actions follow approved UI design.

---

# 123. NO AUTOMATIC IDENTITY ACTION

Do not provide:

    "Confirm person"

as a machine-only action without required human review and domain safeguards.

---

# 124. CANDIDATE COMMENTS

Use investigator-authored notes with explicit attribution.

---

# 125. REPROCESS ACTION

If an investigator requests reprocessing:

    create new processing run

Do not mutate old candidate results.

---

# 126. POLICY EXPERIMENT

If a new threshold/policy is being evaluated:

    record experiment context

Do not overwrite production policy history.

---

# 127. MODEL A/B

If two models are compared:

    Run A / Model A
    Run B / Model B

keep outputs distinguishable.

---

# 128. EVALUATION DATA

Threshold evaluation requires representative non-production validation data.

Do not tune solely on one demo video.

---

# 129. FALSE POSITIVE EVALUATION

Measure:

    false matches

under the actual intended operating context.

---

# 130. FALSE NEGATIVE EVALUATION

Measure:

    missed valid matches

where appropriate.

---

# 131. ROC/PR ANALYSIS

Use appropriate evaluation curves/metrics for the deployment objective.

Do not select a threshold from a single metric without understanding the tradeoff.

---

# 132. OPERATING POINT

The selected operating point should reflect the intended investigative workflow and acceptable review burden.

---

# 133. THRESHOLD DOCUMENTATION

Store:

    dataset/evaluation context
    selected threshold
    metric
    model
    date/version
    owner/approval

where organizational policy requires it.

---

# 134. THRESHOLD DRIFT

Performance may change when source conditions change:

    camera quality
    lighting
    face size
    angle
    compression

Monitor this.

---

# 135. MODEL DRIFT

When a model version changes:

    re-evaluate matching policy

Do not assume old thresholds remain valid.

---

# 136. CAMERA DRIFT

A new camera configuration can alter candidate quality.

Track source-specific performance where appropriate.

---

# 137. DATASET LEAKAGE

Do not evaluate thresholds using data that improperly leaks training/reference identities into validation in a misleading way.

---

# 138. DEMO-BIASED THRESHOLDS

A threshold that works only on a few demo faces is not production evidence.

---

# 139. REFERENCE SELECTION BIAS

Poor references can create weak retrieval.

UI should help investigators choose a usable reference.

---

# 140. MULTIPLE REFERENCE IMAGES

A future implementation may allow multiple reference images.

Possible architecture:

    reference set
       ↓
    reference embeddings
       ↓
    aggregate matching

The exact aggregation must be explicitly specified before implementation.

---

# 141. DO NOT INVENT MULTI-REFERENCE LOGIC

Until implemented, do not claim:

    average embedding
    max similarity
    consensus embedding

as supported behavior.

---

# 142. CANDIDATE AGGREGATION

A sighting can aggregate candidate observations.

It should preserve:

    observation count
    source
    time range
    best observation
    processing context

---

# 143. BEST-SCORE AGGREGATION

A possible policy:

    best_similarity = max(observation similarity)

But this must be an explicit policy, not an assumed formula.

---

# 144. TIME-SUSTAINED AGGREGATION

A sighting can carry:

    duration
    observation count

as context.

Do not convert duration automatically into identity certainty.

---

# 145. SIGHTING SCORE

If a sighting receives an aggregate score:

    define the formula

and preserve underlying observations.

---

# 146. NO MAGIC AGGREGATION

Do not compute:

    score = similarity × track_duration

without a documented evaluation basis.

---

# 147. CANDIDATE PRIORITIZATION

Prioritization may consider:

    similarity
    quality
    persistence
    source relevance

only where validated and documented.

---

# 148. SOURCE IMPORTANCE

If investigators prioritize certain cameras, make this an explicit investigation configuration.

Do not hide source weighting inside machine scoring.

---

# 149. HUMAN PRIORITY

An investigator may manually prioritize a candidate.

That is a human workflow state, not a model confidence value.

---

# 150. MATCHING RESULT STATES

Suggested:

    NOT_ELIGIBLE
    RETRIEVED
    QUALIFIED
    REVIEW_PENDING
    REVIEWED

Exact states follow domain implementation.

---

# 151. NOT ELIGIBLE

Examples:

    incompatible model
    expired record
    unauthorized source
    quality failure

Keep reasons explainable.

---

# 152. RETRIEVED VS QUALIFIED

A vector can be among top-K yet fail policy.

Therefore distinguish:

    retrieved candidate

from:

    policy-qualified candidate.

---

# 153. SEARCH COMPLETION

Search completion means the defined workload finished according to policy.

It does not mean:

    identity confirmed.

---

# 154. ZERO RESULTS

Successful zero-result search should tell the investigator:

    no candidates met this policy

not:

    person not present.

---

# 155. ABSENCE CLAIM

The system must avoid strong negative claims such as:

    "person was not in the video"

when sampling/quality/coverage is incomplete.

Prefer:

    "No qualifying candidate was found under the selected processing policy."

---

# 156. SAMPLING IMPACT

A lower sampling rate may reduce candidate opportunity.

Results should retain coverage context from the processing run.

---

# 157. COVERAGE WARNING

Where relevant, UI should indicate:

    sampled
    partial
    degraded

---

# 158. MATCHING DURING DEGRADED PROCESSING

A candidate generated during a degraded run should preserve the degraded-run state.

---

# 159. LIVE MATCHING

Live matching follows:

    current reference
       ↓
    incoming face embedding
       ↓
    authorized vector retrieval
       ↓
    candidate
       ↓
    sighting update
       ↓
    event

---

# 160. LIVE CANDIDATE COOLDOWN

To avoid repeated alerts, the live system may use:

    per-track cooldown
    per-sighting update policy

Exact semantics must be documented.

---

# 161. NO HIDDEN COOLDOWN

Do not suppress repeated candidates through an undocumented arbitrary timer.

---

# 162. LIVE SIGHTING UPDATES

Use updates such as:

    sighting.created
    sighting.updated

rather than flooding the UI with identical candidate creation events.

---

# 163. EVENT IDEMPOTENCY

Events must be safely replayable.

---

# 164. LIVE RECONNECT

After service/UI reconnect:

    current sighting state

should be recoverable from durable APIs.

---

# 165. MATCHING AND WEBSOCKET

WebSocket should deliver:

    candidate/sighting metadata

not:

    raw embedding vectors.

---

# 166. SOURCE IMAGE DELIVERY

Source frame retrieval uses authorized HTTP/object access path.

---

# 167. BATCH LIVE MATCHING

Multiple face embeddings in one frame may be batched for retrieval if supported.

Each resulting candidate retains individual source detection identity.

---

# 168. MULTI-FACE FRAME

One frame:

    Face A
    Face B
    Face C

may create:

    Candidate A
    Candidate B
    Candidate C

Each has independent lineage.

---

# 169. MULTI-REFERENCE SEARCH

If multiple references are supported later, the result must identify:

    which reference embedding

generated each candidate.

---

# 170. REFERENCE VERSION

If a reference is reprocessed:

    reference version/run

must remain attributable.

---

# 171. REFERENCE CHANGE

Changing the reference image means a new reference-processing context.

Do not silently replace the old reference.

---

# 172. SEARCH REPEATABILITY

For a file and fixed:

    reference
    model
    policy
    evidence
    processing configuration

the system should aim for reproducible candidate ordering.

Hardware/runtime nondeterminism must be documented if material.

---

# 173. NUMERICAL TOLERANCE

Floating-point differences may occur.

Tests should use reasonable tolerance rather than unjustified exact equality.

---

# 174. VECTOR INDEX REBUILD

A vector index rebuild must not alter domain semantics.

After rebuild, retrieval quality/performance should be verified.

---

# 175. VECTOR INDEX VERSION

Where material to reproducibility, record index/configuration version.

---

# 176. VECTOR SEARCH FAILURE RECOVERY

On transient vector-store failure:

    retry safely

On persistent failure:

    mark matching stage unavailable.

---

# 177. PARTIAL VECTOR DATA

Do not silently ignore missing embeddings and report complete coverage.

---

# 178. MISSING EMBEDDING

A source observation without embedding may be:

    processing incomplete

not:

    non-match.

---

# 179. MISSING DETECTION

No detection means:

    detector found no face

or:

    detection was unavailable

These states must remain distinct.

---

# 180. MATCHING TELEMETRY

Track:

    searches
    retrieval latency
    top-K count
    qualified candidates
    rejected candidates
    average similarity
    high-tier candidate count

Use aggregate metrics carefully to avoid leaking sensitive information.

---

# 181. PRIVACY OF METRICS

Do not build public/global metrics that expose:

    case-specific biometric result details.

---

# 182. SECURITY TEST

Attempt:

    Investigation A reference
       →
    Investigation B vector corpus

Expected:

    denied.

---

# 183. MODEL COMPATIBILITY TEST

Compare incompatible model embeddings.

Expected:

    blocked.

---

# 184. THRESHOLD TEST

Candidate below threshold:

    not promoted

according to policy.

---

# 185. TOP-K TEST

If K=10:

    retrieval must not expose more than configured limit to downstream logic.

---

# 186. NO-RESULT TEST

Valid search with no qualifying candidates:

    successful
    zero candidates

---

# 187. FAILURE TEST

Unavailable vector store:

    search failed/degraded

not:

    zero candidates.

---

# 188. PROVENANCE TEST

Accepted candidate must resolve to:

    evidence
    frame
    processing run
    model
    policy.

---

# 189. DEDUP TEST

Multiple frames from one track:

    one sighting

according to configured aggregation policy.

---

# 190. CROSS-CAMERA TEST

Two cameras:

    two source sightings

with optional investigation-level correlation.

---

# 191. CROSS-CASE TEST

Unauthorized cross-case retrieval:

    denied.

---

# 192. REPROCESS TEST

Same source with new model:

    new processing context

and distinguishable results.

---

# 193. REVIEW TEST

Human review does not overwrite:

    raw similarity
    source timestamp
    machine processing context.

---

# 194. EVENT TEST

Candidate persistence succeeds but event publication fails.

Expected:

    candidate remains durable
    event can retry.

---

# 195. UI TEST

Candidate detail displays:

    source
    timestamp
    similarity
    model
    policy
    review state

without raw embeddings.

---

# 196. LOAD TEST

Evaluate:

    concurrent searches
    large vector corpus
    high candidate density
    multi-camera processing

under realistic hardware.

---

# 197. LATENCY TEST

Measure:

    embedding → vector retrieval
    vector retrieval → candidate persistence
    persistence → realtime event

---

# 198. THROUGHPUT TEST

Measure:

    embeddings/sec
    vector queries/sec
    candidates/sec

under production-like load.

---

# 199. DATABASE INDEX TEST

Verify vector and relational indexes support actual query patterns.

---

# 200. DATA RETENTION TEST

Expired vectors/embeddings must not appear in new matching queries.

---

# 201. DELETION TEST

Deleting an allowed biometric artifact should remove/disable matching according to policy.

---

# 202. AUDIT TEST

Search creation and relevant administrative operations must be auditable.

---

# 203. LOG SAFETY TEST

Verify logs contain no:

    raw embeddings
    credentials
    unauthorized source frames.

---

# 204. MODEL VERSION TEST

Candidate:

    model_version = actual runtime model version.

---

# 205. POLICY VERSION TEST

Candidate:

    policy_version = actual policy used.

---

# 206. SOURCE TIMESTAMP TEST

Candidate timestamp equals source observation timestamp under the test fixture.

---

# 207. RANKING TEST

Known candidate set should produce deterministic ordering according to policy.

---

# 208. TIE TEST

Equal-score candidates should use deterministic tie-breaking.

---

# 209. QUALITY TEST

A low-quality observation follows the configured quality policy.

---

# 210. PARTIAL COVERAGE TEST

Search where one source fails:

    UI must show partial coverage.

---

# 211. ABSENCE-CLAIM TEST

Zero candidates from sampled video must not generate language claiming the person was absent.

---

# 212. MODEL CHANGE TEST

Change model.

Expected:

    new run
    new model context.

---

# 213. POLICY CHANGE TEST

Change threshold.

Expected:

    new policy context
    historical result retained.

---

# 214. REFERENCE CHANGE TEST

Change reference.

Expected:

    new reference-processing context.

---

# 215. SECURITY PRINCIPLE

Every matching request must answer:

    Who requested it?
    For which case?
    For which investigation?
    Against what evidence?
    Under which model?
    Under which policy?

---

# 216. AUTHORIZATION ORDER

Recommended:

    authenticate
       ↓
    authorize case/investigation
       ↓
    validate reference
       ↓
    validate source scope
       ↓
    start matching

Do not retrieve vectors first and authorize later.

---

# 217. MATCHING POLICY OWNERSHIP

Policies should have controlled ownership/review.

Do not let arbitrary frontend users invent thresholds.

---

# 218. CONFIGURATION SOURCE

Thresholds/top-K/policy must come from approved server-side configuration.

---

# 219. FRONTEND RESTRICTION

Frontend may request:

    approved policy

but should not directly define authoritative:

    threshold
    vector metric
    model ID

for production searches.

---

# 220. ADMIN POLICY UI

If policy management exists:

    version
    effective date
    model compatibility
    approval
    evaluation context

should be visible.

---

# 221. MODEL/POLICY MATRIX

Maintain compatibility such as:

| Model | Version | Embedding Dim | Metric | Policy |
|---|---|---:|---|---|
| Approved model | X | recorded | cosine | Policy-X |

The actual production values must come from deployment configuration, not this example.

---

# 222. NO HARDCODED PRODUCTION MODEL CLAIMS

Do not hard-code a model as the official production model inside documentation or frontend unless the deployment has actually approved it.

---

# 223. INSIGHTFACE INTEGRATION

For InsightFace-based processing:

    detector
       ↓
    quality
       ↓
    face crop
       ↓
    recognition model
       ↓
    embedding
       ↓
    matching engine

The matching layer should remain independent of provider-specific detection APIs.

---

# 224. PRIVATE/OFFLINE MODEL CONTEXT

Where production deployment uses an approved local/private model:

    model metadata

must be recorded.

Do not rely on a remote hosted evaluation endpoint for long-term production matching when the approved architecture requires local inference.

---

# 225. LICENSE/APPROVAL

Model deployment must follow the applicable license/approval record for the selected weights.

Do not describe a model as production-approved without verification.

---

# 226. RAW SCORE RETENTION

Store the raw similarity where required for reproducibility.

Do not replace it with an interpreted label only.

---

# 227. DERIVED TIER

A candidate tier may be derived from policy.

Example:

    HIGH_REVIEW_PRIORITY

The underlying score remains available to authorized users.

---

# 228. POLICY DECISION RECORD

Potential structure:

    passed_threshold = true
    quality_passed = true
    eligible = true
    tier = REVIEW

Only record fields actually used.

---

# 229. DECISION EXPLANATION

An authorized API can return:

    similarity = X
    threshold = Y
    metric = cosine
    quality = GOOD
    policy = Policy-3

This provides technical transparency.

---

# 230. DO NOT CALL SCORE "ACCURACY"

Accuracy is a model/evaluation property, not an individual candidate score.

Do not label:

    0.91 = 91% accuracy.

---

# 231. DO NOT CALL SCORE "PROBABILITY"

Unless calibrated:

    similarity ≠ probability.

---

# 232. NO GUILT INFERENCE

Never derive:

    similarity
       ↓
    suspect likelihood
       ↓
    guilt

---

# 233. NO RISK SCORING

Face Trace matching must not secretly become:

    person = high risk

unless a separate, explicitly governed subsystem exists.

---

# 234. NO DEMOGRAPHIC FILTERING

Do not filter/rank candidates by:

    race
    religion
    gender identity
    protected attributes

---

# 235. NO EMOTIONAL INTERPRETATION

Do not use facial expression as investigative evidence unless separately governed and actually supported.

---

# 236. SOURCE RELEVANCE

Source relevance should be investigator/configuration input, not an unexplainable model factor.

---

# 237. HUMAN REVIEW

Every promoted candidate should be:

    review pending

unless an explicit lower-risk informational workflow exists.

---

# 238. REVIEW EVIDENCE

Reviewer must have access to:

    source frame
    timestamp
    candidate context
    reference context

subject to authorization.

---

# 239. REVIEW ESCALATION

Low-quality or ambiguous candidates can be escalated for:

    more frames
    source video context
    alternate evidence

without changing machine score retroactively.

---

# 240. MORE CONTEXT

A reviewer request for more context may retrieve:

    nearby frames
    track interval
    neighboring source evidence

while preserving provenance.

---

# 241. SOURCE-CONTEXT WINDOW

Context windows must be bounded.

Do not expose entire case media unnecessarily.

---

# 242. MATCHING DETAIL

Candidate detail should include:

    exact source timestamp
    source ID
    frame
    track
    similarity
    quality
    model
    policy
    processing run

---

# 243. INVESTIGATOR TRUST

The UI should make machine/human distinction obvious.

Example:

    MACHINE-GENERATED CANDIDATE

Then:

    INVESTIGATOR REVIEW

---

# 244. PROVENANCE LINK

Every candidate should have:

    View provenance

action.

---

# 245. SOURCE VERIFICATION ACTION

Every candidate should support:

    View source frame
    View evidence
    View timeline context

subject to permissions.

---

# 246. GRAPH EXPLANATION

If graph integration exists:

    candidate
       ↓
    sighting
       ↓
    source evidence

should be navigable.

---

# 247. SEARCH HISTORY

Investigators should be able to see their own authorized search history where product policy allows.

---

# 248. SEARCH REPEAT

Repeated search with identical inputs may be optimized, but cached output must retain correct provenance and access semantics.

---

# 249. AUDIT TRAIL

Search creation, review, export, and administrative changes should remain auditable.

---

# 250. FINAL MATCHING CONTRACT

The matching engine contract is:

    VALID REFERENCE
       ↓
    COMPATIBLE EMBEDDING SPACE
       ↓
    AUTHORIZED VECTOR CORPUS
       ↓
    CONTROLLED TOP-K RETRIEVAL
       ↓
    EXPLICIT SIMILARITY METRIC
       ↓
    VERSIONED MATCHING POLICY
       ↓
    QUALITY-AWARE EVALUATION
       ↓
    CANDIDATE RANKING
       ↓
    SOURCE/TIME/Track AGGREGATION
       ↓
    TRACEABLE SIGHTING
       ↓
    HUMAN REVIEW

---

# 251. DEFINITION OF DONE

The Matching Engine is complete when:

[ ] Reference embedding is validated.

[ ] Candidate embeddings are model-compatible.

[ ] pgvector retrieval is authorized.

[ ] Cross-case access is blocked by default.

[ ] Top-K is bounded.

[ ] Similarity metric is explicit.

[ ] Thresholds are versioned.

[ ] Raw similarity remains distinct from probability.

[ ] Candidate records preserve provenance.

[ ] Track observations can aggregate into sightings.

[ ] Duplicate alert flooding is controlled.

[ ] Reprocessing creates distinguishable history.

[ ] Source-frame verification works.

[ ] Review state is separate from machine output.

[ ] Events are idempotent.

[ ] Failures are distinguishable from zero matches.

[ ] Partial processing is visible.

[ ] Security tests pass.

[ ] Evaluation data supports selected policy.

[ ] Load/latency tests pass for target deployment.

---

# 252. FINAL PRINCIPLE

The CrimeKit Matching Engine should never say:

    "The algorithm recognized the criminal."

It should say:

    "A machine-generated candidate observation exceeded the
     configured matching policy for an authorized source,
     using a recorded model, metric, and processing run.
     The source evidence and provenance are available for
     investigator verification."

That is the correct technical and forensic contract.
