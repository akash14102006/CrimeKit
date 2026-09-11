# CRIMEKIT — FACE TRACE INVESTIGATOR
# API & EVENT CONTRACT SPECIFICATION

**Document:** `API_EVENTS.md`  
**Subsystem:** Face Trace Investigator  
**Scope:** REST APIs, WebSocket channels, domain events, request/response contracts, idempotency, authorization, pagination, source-frame retrieval, provenance access, errors, versioning, realtime synchronization  
**Primary concern:** Provide a secure, stable, traceable contract between React, FastAPI, workers, persistence, vector search, graph projection, and realtime delivery  
**Audience:** Frontend, backend, ML, forensic, infrastructure, security, QA  
**Status:** Authoritative API/event specification

---

# 1. PURPOSE

Face Trace Investigator requires a clear boundary between:

    React UI
       ↓
    FastAPI API
       ↓
    workflow/job layer
       ↓
    processing workers
       ↓
    PostgreSQL / pgvector / Neo4j
       ↓
    event/realtime layer

This document defines the contract across those boundaries.

The API must expose:

    what the investigator needs

without exposing:

    raw secrets
    raw biometric vectors
    unauthorized evidence
    internal implementation details

---

# 2. CORE API PRINCIPLE

The public API is a domain contract.

It should not mirror:

    Python classes
    ORM internals
    database tables
    model SDK objects

directly.

---

# 3. API DESIGN PRINCIPLES

The API must be:

- authenticated
- authorized
- case-scoped
- versioned where appropriate
- idempotent where required
- pagination-aware
- explicit about job state
- explicit about partial processing
- provenance-aware
- safe for realtime synchronization

---

# 4. DOMAIN RESOURCES

Recommended resources:

    cases
    investigations
    face-references
    face-searches
    processing-runs
    face-candidates
    face-sightings
    provenance
    source-frames
    reviews

Actual route naming should align with existing CrimeKit API conventions.

---

# 5. API BASE PATH

A versioned path is recommended:

    /api/v1

Exact prefix must follow the existing backend architecture.

Do not create a second API-versioning scheme.

---

# 6. AUTHENTICATION

Every protected Face Trace endpoint requires the existing CrimeKit authentication mechanism.

Do not implement a separate authentication stack inside this feature.

---

# 7. AUTHORIZATION

Authentication answers:

    Who are you?

Authorization answers:

    What may you access?

Both are required.

---

# 8. CASE AUTHORIZATION

Every sensitive request must resolve:

    user → case → permission

before exposing evidence or biometric-derived records.

---

# 9. INVESTIGATION AUTHORIZATION

Where investigations are separately scoped:

    user → case → investigation

must be validated.

---

# 10. SOURCE AUTHORIZATION

A user who can access a case may still lack access to a restricted source.

Source-level authorization must remain enforceable.

---

# 11. API REQUEST CONTEXT

Internally propagate:

    request_id
    user_id
    case_id
    investigation_id
    job_id
    processing_run_id

where applicable.

---

# 12. DO NOT TRUST CLIENT SCOPE

Do not rely only on:

    case_id sent by frontend

for authorization.

The server must validate access.

---

# 13. CREATE FACE SEARCH

Conceptual:

    POST /api/v1/face-searches

Request:

    {
      investigation_id,
      reference_id,
      source_scope,
      policy_id
    }

The actual schema follows CrimeKit implementation.

---

# 14. SEARCH REQUEST VALIDATION

Validate:

    reference exists
    reference belongs to authorized case
    source scope is authorized
    policy is valid
    model is compatible
    requested workload is within limits

---

# 15. SEARCH CREATION RESPONSE

Return a stable search/job identity.

Example:

    {
      "search_id": "...",
      "job_id": "...",
      "status": "QUEUED"
    }

Do not keep the HTTP request open until video processing finishes.

---

# 16. IDEMPOTENCY

For create/search endpoints, support an idempotency mechanism where repeated client retries could otherwise create duplicate jobs.

Potential header:

    Idempotency-Key

Use the existing CrimeKit convention if one exists.

---

# 17. IDEMPOTENCY SEMANTICS

For the same authorized logical operation:

    retry
       ↓
    same logical job/result

where the endpoint contract promises idempotency.

Do not silently treat two intentionally separate searches as the same operation.

---

# 18. SEARCH STATUS

Suggested states:

    QUEUED
    RUNNING
    DEGRADED
    COMPLETED
    PARTIAL
    FAILED
    CANCELLED

Use exact backend state names consistently.

---

# 19. GET SEARCH

Conceptual:

    GET /api/v1/face-searches/{search_id}

Response should include:

    search_id
    investigation_id
    status
    progress where meaningful
    source summary
    candidate summary
    timestamps

---

# 20. FILE SEARCH PROGRESS

For finite video jobs:

    processed_frames
    sampled_frames
    total_frames where known
    candidates
    sightings

Do not provide fake percentages.

---

# 21. LIVE SEARCH PROGRESS

For live streams, percentage is generally inappropriate.

Provide:

    source FPS
    processed FPS
    latency
    active tracks
    sightings
    health

---

# 22. GET SEARCH SOURCES

Potential:

    GET /api/v1/face-searches/{search_id}/sources

Return source-level state:

    source_id
    status
    frames
    detections
    candidates
    errors

---

# 23. SOURCE STATUS

A source may be:

    QUEUED
    PROCESSING
    COMPLETED
    FAILED
    DEGRADED
    CANCELLED

Exact names follow implementation.

---

# 24. CANCEL SEARCH

Potential:

    POST /api/v1/face-searches/{search_id}/cancel

Cancellation must be authorized and idempotent.

---

# 25. CANCEL SEMANTICS

Cancellation should stop future work where possible.

Already durable results remain valid and traceable.

---

# 26. LIVE SOURCE START

Potential:

    POST /api/v1/face-streams

Request may include:

    investigation_id
    source_id
    reference_id
    policy_id

Do not accept raw RTSP credentials from the browser unless the architecture explicitly supports secure secret handling.

---

# 27. LIVE SOURCE STOP

Potential:

    POST /api/v1/face-streams/{stream_id}/stop

Return current stream/job state.

---

# 28. STREAM STATUS

Potential:

    GET /api/v1/face-streams/{stream_id}

Response:

    stream_id
    source_id
    status
    health
    started_at
    metrics
    active_sightings

---

# 29. REFERENCE RESOURCE

Potential:

    POST /api/v1/face-references

A reference belongs to:

    case/investigation

and links to:

    source artifact
    selected face
    embedding context

---

# 30. REFERENCE CREATION

The backend should validate:

    authorized artifact
    face selection
    quality
    model compatibility

---

# 31. REFERENCE LIST

Potential:

    GET /api/v1/investigations/{id}/face-references

Return only authorized references.

---

# 32. REFERENCE DETAIL

Potential:

    GET /api/v1/face-references/{reference_id}

Do not return raw embedding vectors.

---

# 33. REFERENCE IMAGE

Reference image access should use the secure artifact mechanism.

Do not embed permanent public object-storage URLs.

---

# 34. CANDIDATE LIST

Potential:

    GET /api/v1/face-searches/{search_id}/candidates

Filters may include:

    source_id
    time_from
    time_to
    review_status
    similarity_min
    similarity_max
    tier

---

# 35. CANDIDATE PAGINATION

Use cursor or page-based pagination according to CrimeKit standards.

Never return an unbounded candidate list.

---

# 36. PAGINATION RESPONSE

Conceptual:

    items
    next_cursor
    has_more

or the established project pagination shape.

---

# 37. CANDIDATE DETAIL

Potential:

    GET /api/v1/face-candidates/{candidate_id}

Response should include:

    candidate_id
    source
    evidence
    timestamp
    frame_number
    bbox
    similarity
    metric
    quality
    rank
    model
    policy
    review_state
    sighting_id

---

# 38. RAW EMBEDDING EXCLUSION

The candidate endpoint must not expose:

    embedding vector

by default.

---

# 39. SOURCE FRAME ENDPOINT

Potential:

    GET /api/v1/face-candidates/{candidate_id}/source-frame

The backend must:

    authorize
    resolve provenance
    obtain source frame
    provide secure access

---

# 40. SOURCE FRAME SEMANTICS

The response must represent the exact source observation.

If the returned image is an annotated derivative:

    explicitly identify it as derived.

---

# 41. CONTEXT FRAMES

Potential:

    GET /api/v1/face-sightings/{sighting_id}/context

Return bounded neighboring frames/timestamps.

Do not return entire videos by default.

---

# 42. SOURCE VIDEO

Source video access remains governed by the CrimeKit evidence subsystem.

Face Trace should reference it rather than implement a second evidence download system.

---

# 43. SIGHTING LIST

Potential:

    GET /api/v1/face-searches/{search_id}/sightings

Filters:

    source
    time range
    review state
    candidate tier

---

# 44. SIGHTING DETAIL

Potential:

    GET /api/v1/face-sightings/{sighting_id}

Response may include:

    sighting_id
    source
    time range
    best_observation
    observation_count
    candidate summary
    review state
    provenance summary

---

# 45. SIGHTING OBSERVATIONS

Potential:

    GET /api/v1/face-sightings/{sighting_id}/observations

Paginate if the observation count can become large.

---

# 46. PROVENANCE ENDPOINT

Potential:

    GET /api/v1/face-sightings/{sighting_id}/provenance

Return:

    case
    investigation
    search
    processing run
    evidence
    artifact
    frame
    detection
    track
    model
    policy
    review

subject to authorization and data minimization.

---

# 47. PROVENANCE DEPTH

Default response should be a useful summary.

Technical details can be expanded on demand.

---

# 48. REVIEW ENDPOINT

Potential:

    POST /api/v1/face-sightings/{sighting_id}/review

Request:

    {
      "decision": "...",
      "notes": "..."
    }

Exact review vocabulary follows the approved domain.

---

# 49. REVIEW AUTHORIZATION

Only authorized investigators should be able to change review state.

---

# 50. REVIEW IMMUTABILITY

Review must not change:

    source evidence
    similarity
    source timestamp
    model version
    processing run

---

# 51. REVIEW AUDIT

Persist:

    reviewer
    timestamp
    previous state
    new state
    notes where applicable

---

# 52. REVIEW HISTORY

Potential:

    GET /api/v1/face-sightings/{sighting_id}/reviews

Return historical decisions according to the audit policy.

---

# 53. SEARCH HISTORY

Potential:

    GET /api/v1/investigations/{investigation_id}/face-searches

Paginate.

---

# 54. SEARCH HISTORY SECURITY

Only searches visible to the authorized investigator/role should appear.

Do not leak another team's activity.

---

# 55. ERROR MODEL

Use structured errors.

Conceptual:

    {
      "error": {
        "code": "SOURCE_UNAVAILABLE",
        "message": "The selected source is unavailable.",
        "request_id": "..."
      }
    }

---

# 56. ERROR CODES

Potential:

    UNAUTHORIZED
    FORBIDDEN
    NOT_FOUND
    VALIDATION_ERROR
    SOURCE_UNAVAILABLE
    MODEL_UNAVAILABLE
    VECTOR_SEARCH_FAILED
    PROCESSING_FAILED
    PROCESSING_PARTIAL
    CANNOT_CANCEL
    INVALID_REFERENCE
    INVALID_POLICY
    CONFLICT
    RATE_LIMITED

Only implement codes actually needed.

---

# 57. HTTP STATUS

Follow established REST semantics.

Typical mapping:

    400 → invalid request
    401 → unauthenticated
    403 → unauthorized
    404 → resource not found
    409 → conflict/idempotency
    422 → validation failure where framework convention applies
    429 → rate limit
    500 → unexpected server error
    503 → dependency unavailable

---

# 58. ERROR DATA MINIMIZATION

Do not include:

    stack traces
    database queries
    RTSP credentials
    object-store secrets
    raw biometric vectors

---

# 59. NOT FOUND VS FORBIDDEN

Security policy may intentionally avoid revealing whether a restricted resource exists.

Follow the broader CrimeKit authorization strategy.

---

# 60. REQUEST IDs

Every API response should expose a request/correlation identifier where the existing platform supports it.

---

# 61. ETAG / CONDITIONAL READS

Where useful, GET endpoints can support:

    ETag
    If-None-Match

for efficient polling.

Do not invent this requirement where infrastructure already handles caching differently.

---

# 62. CACHE POLICY

Sensitive candidate/source/provenance responses should not be publicly cached.

Use appropriate private/no-store controls.

---

# 63. PAGINATION CONSISTENCY

Use stable ordering for paginated candidate/sighting results.

---

# 64. CURSOR SECURITY

Opaque cursor values must not expose:

    internal database secrets
    raw SQL
    sensitive identifiers unnecessarily.

---

# 65. FILTER VALIDATION

Validate:

    time format
    source IDs
    status values
    numeric score bounds

---

# 66. SEARCH PARAMETERS

Do not allow arbitrary client-provided:

    SQL
    vector operator
    database index
    model path

---

# 67. POLICY SELECTION

Frontend may request an approved policy identifier.

Server validates:

    policy exists
    policy applies to model/context
    caller can use it.

---

# 68. MODEL SELECTION

Do not let an ordinary investigator supply:

    arbitrary model path

from frontend.

Use approved model configuration.

---

# 69. ADMIN MODEL/POLICY ENDPOINTS

If administrative configuration APIs exist, they should be separate and strongly authorized.

---

# 70. EVENT SYSTEM

Face Trace should publish domain events for important state changes.

---

# 71. EVENT NAMING

Suggested names:

    face.search.created
    face.search.started
    face.search.progress
    face.processing.degraded
    face.candidate.created
    face.sighting.created
    face.sighting.updated
    face.review.updated
    face.search.completed
    face.search.failed
    face.stream.health_changed

Use CrimeKit's established naming conventions if available.

---

# 72. EVENT VERSIONING

Each event should carry a schema version.

Example:

    event_type
    event_version

Do not change payload semantics silently.

---

# 73. EVENT ENVELOPE

Conceptual:

    {
      "event_id": "...",
      "event_type": "face.sighting.created",
      "event_version": 1,
      "occurred_at": "...",
      "case_id": "...",
      "investigation_id": "...",
      "aggregate_id": "...",
      "payload": { ... }
    }

---

# 74. EVENT ID

Every event requires a stable unique ID.

---

# 75. AGGREGATE ID

Events should identify the primary domain aggregate:

    search_id
    candidate_id
    sighting_id
    stream_id

as appropriate.

---

# 76. EVENT PAYLOAD MINIMIZATION

Payload should contain identifiers and necessary state.

Do not send:

    raw image bytes
    raw embedding vectors
    credentials

---

# 77. EVENT SOURCE

A candidate event should identify source context sufficiently for authorized consumers.

---

# 78. EVENT TIMESTAMP

Distinguish:

    occurred_at

from:

    published_at

where both are needed.

---

# 79. EVENT ORDER

Clients must not assume network delivery order is perfect.

Use:

    event_id
    sequence/version
    occurred_at

where required.

---

# 80. AGGREGATE VERSION

Where practical, include a domain version/sequence for conflict detection and reconciliation.

---

# 81. IDEMPOTENT EVENT CONSUMPTION

Consumers should store or detect processed event IDs to avoid duplicate application.

---

# 82. EVENT REPLAY

Replay must not create duplicate forensic facts.

---

# 83. EVENT RETRY

Publisher may retry event delivery.

The same event ID should represent the same logical event.

---

# 84. DEAD LETTER

Failed event processing can enter an operational dead-letter mechanism.

This must not delete the authoritative domain record.

---

# 85. WEBSOCKET CHANNEL

Recommended conceptual:

    /ws/investigations/{investigation_id}/face-trace

Authorization required.

---

# 86. CHANNEL AUTHORIZATION

At connection/subscription time:

    authenticate
    authorize investigation

---

# 87. CHANNEL ISOLATION

A connection may only receive events for authorized scopes.

---

# 88. SOURCE-SPECIFIC CHANNEL

A more granular channel can be used if required:

    /ws/face-streams/{stream_id}

Still enforce authorization.

---

# 89. INITIAL SNAPSHOT

Realtime clients should not depend on events alone.

Recommended:

    API snapshot
       ↓
    WebSocket subscribe
       ↓
    incremental events

---

# 90. EVENT GAP

If client detects missed sequence/version:

    refetch authoritative snapshot

Do not attempt to reconstruct critical state from incomplete events.

---

# 91. WEBSOCKET HEARTBEAT

Use heartbeat/ping handling consistent with infrastructure.

Do not implement an independent incompatible keepalive protocol.

---

# 92. RECONNECT

Frontend reconnect should:

    re-authenticate if necessary
    resubscribe
    reconcile state

---

# 93. DUPLICATE EVENT HANDLING

Frontend state reducer should be idempotent.

---

# 94. EVENT BACKPRESSURE

A high-volume stream must not generate unlimited frontend memory growth.

Use:

    coalescing
    bounded client buffers
    state replacement

where appropriate.

---

# 95. TRACK UPDATE EVENTS

High-frequency track updates can be throttled/coalesced for UI.

This must not alter authoritative forensic records.

---

# 96. CANDIDATE CREATION EVENTS

Candidate creation should be relatively low frequency after aggregation.

---

# 97. SIGHTING EVENTS

Prefer:

    sighting.created
    sighting.updated

for investigator-facing realtime UI.

---

# 98. PROGRESS EVENTS

Progress events may be emitted at controlled intervals.

Do not publish every internal frame counter.

---

# 99. HEALTH EVENTS

Live source health changes should be event-driven where useful.

---

# 100. EVENT SECURITY

Events must not leak:

    cross-case IDs
    restricted source names
    private evidence URLs
    raw vectors

---

# 101. SOURCE FRAME ACCESS

Events can contain:

    candidate_id

The frontend then requests source image through authorized API.

---

# 102. EVENT + API PATTERN

Recommended:

    event:
        sighting_id
        changed fields

    API:
        full authoritative detail

---

# 103. WEBHOOKS

External webhooks should not be added merely for convenience.

If used, they require:

    authentication
    signing
    replay protection
    scope controls

---

# 104. WEBHOOK PAYLOAD

Never include unnecessary biometric content.

---

# 105. API VERSIONING

Breaking changes require a versioning strategy.

---

# 106. BACKWARD COMPATIBILITY

Event consumers may lag behind producers.

Schema evolution must preserve compatibility where required.

---

# 107. EVENT OPTIONAL FIELDS

New optional fields are safer than breaking changes when compatible with consumer behavior.

---

# 108. ENUM EVOLUTION

Clients should tolerate unknown future statuses where the API contract permits.

---

# 109. API DEPRECATION

Deprecated fields/routes must have a documented migration path.

---

# 110. SCHEMA VALIDATION

Use shared schema validation between:

    backend
    event payload
    frontend

where practical.

---

# 111. OPENAPI

FastAPI should expose the authoritative REST schema through OpenAPI where project standards allow.

---

# 112. FRONTEND TYPES

Generate or maintain TypeScript types from the actual API/event contract.

Avoid manually drifting copies.

---

# 113. API CLIENT

Frontend should use a centralized Face Trace API client.

Do not scatter raw fetch calls throughout components.

---

# 114. AUTH INTERCEPTOR

API client should use existing authentication/session mechanisms.

---

# 115. ERROR INTERCEPTOR

Centralize handling of:

    401
    403
    429
    dependency errors

without hiding domain-specific messages.

---

# 116. RETRY POLICY

Frontend may retry safe GETs and authorized transient operations.

Do not automatically retry every POST without idempotency semantics.

---

# 117. REQUEST CANCELLATION

Long polling/search list requests should support cancellation where appropriate.

---

# 118. POLLING FALLBACK

If WebSocket is unavailable, the UI may use bounded polling for job state.

Polling must not become a second source of truth.

---

# 119. POLLING INTERVAL

Use controlled polling/backoff.

Do not poll every 100 ms indefinitely.

---

# 120. REALTIME PRIORITY

Realtime events are for timely UI synchronization.

The API remains authoritative.

---

# 121. SOURCE-LEVEL PROGRESS

A job status endpoint may summarize source progress.

---

# 122. AGGREGATED PROGRESS

Search-level progress may be estimated only when meaningful.

---

# 123. UNKNOWN TOTAL

For live streams or unknown-length input:

    use metrics instead of percentage.

---

# 124. PARTIAL STATE

Search status should distinguish:

    COMPLETED
    PARTIAL
    FAILED

---

# 125. ZERO CANDIDATES

Successful search with no candidates:

    COMPLETED + candidate_count = 0

not:

    FAILED

---

# 126. FAILURE STATE

Processing failure should expose:

    error code
    safe message
    request/job ID

---

# 127. SOURCE FAILURE

A source-specific failure should remain distinguishable from whole-job failure.

---

# 128. MULTI-SOURCE RESPONSE

Search detail should allow investigators to understand:

    source A complete
    source B failed
    source C complete

---

# 129. RESULT COUNTS

Counts should be clearly labeled:

    candidates
    sightings
    processed sources

Do not call similarity retrieval count "confirmed matches."

---

# 130. DATE/TIME FORMAT

Use a consistent canonical timestamp format across API/events.

---

# 131. TIME ZONE

Where CrimeKit uses UTC canonical storage:

    return explicit timezone/offset semantics.

Do not silently strip timezone.

---

# 132. SOURCE TIME VS API TIME

Clearly distinguish:

    source_timestamp
    created_at
    processed_at
    published_at

---

# 133. BOUNDING BOX CONTRACT

Represent:

    x
    y
    width
    height

or the established coordinate format.

Document whether coordinates are:

    absolute pixels
    normalized

Do not mix formats.

---

# 134. FRAME DIMENSIONS

If bbox is returned, provide enough frame metadata to interpret coordinates.

---

# 135. PAGINATED OBSERVATIONS

Track observations may be numerous.

Use pagination.

---

# 136. LARGE PROVENANCE

Do not return all frame/detection relationships inline by default.

Use detail endpoints.

---

# 137. GRAPH DATA

Do not return the entire Neo4j graph for a candidate API.

Expose domain-level relationships needed by the UI.

---

# 138. VECTOR DATA

Do not return raw pgvector records.

---

# 139. INTERNAL IDS

Public IDs may be opaque.

Avoid leaking sequential DB primary keys if security policy discourages them.

---

# 140. RESOURCE OWNERSHIP

Every resource should be tied to a case/investigation where relevant.

---

# 141. ORPHAN RESOURCE HANDLING

Resources missing required parent context should not appear as normal investigator data.

---

# 142. API TRANSACTION SEMANTICS

Creation endpoints should return only after authoritative state is safely persisted according to the contract.

---

# 143. ASYNC JOB CONTRACT

Create endpoint:

    request
       ↓
    validate
       ↓
    create durable job
       ↓
    return job/search ID

---

# 144. JOB PROGRESS CONTRACT

Progress endpoint reflects durable state, not an in-memory worker counter alone.

---

# 145. WORKER COMPLETION

Worker should persist final result/state before publishing completion event.

---

# 146. EVENT FAILURE

If event publish fails:

    GET search

must still return the durable state.

---

# 147. API CONSISTENCY

The same candidate retrieved through:

    search list
    candidate detail
    sighting detail

must resolve to the same authoritative domain record.

---

# 148. NO DUPLICATE IDENTITIES

Do not create one object per layer such as:

    vector candidate
    API candidate
    graph candidate

without stable shared domain identity.

---

# 149. CORRELATION IDS

Pass a stable correlation ID through asynchronous work.

---

# 150. LOG CORRELATION

API logs and worker logs should be searchable by:

    request_id
    job_id
    processing_run_id

---

# 151. METRIC LABEL SECURITY

Do not use high-cardinality sensitive identifiers such as:

    raw user names
    case names
    biometric IDs

as unrestricted global metric labels.

---

# 152. RATE LIMITING

Protect expensive endpoints:

    search creation
    reprocessing
    source-frame extraction

---

# 153. QUERY LIMITS

Bound:

    page size
    top-K
    context frame count
    time-window expansion

---

# 154. EXPORT ENDPOINTS

If Face Trace supports exports:

    authorize case
    audit operation
    enforce retention
    preserve provenance

---

# 155. REPORT GENERATION

Report creation should use durable domain records.

Do not recompute matching merely to generate a report.

---

# 156. REVIEW EXPORT

If review state is exported, identify:

    machine result
    reviewer decision

separately.

---

# 157. API CONTRACT TESTS

Every endpoint should have:

    success test
    validation test
    authorization test
    not-found test
    dependency failure test

as appropriate.

---

# 158. EVENT CONTRACT TESTS

Every event should have:

    schema validation
    version compatibility
    idempotency
    authorization

tests where applicable.

---

# 159. FRONTEND CONTRACT TESTS

Verify TypeScript types match:

    actual API payloads
    actual event payloads.

---

# 160. OPENAPI SNAPSHOT

Where CI supports it, detect accidental breaking API changes through schema diff.

---

# 161. EVENT SCHEMA SNAPSHOT

Maintain versioned event schemas to prevent silent breaking changes.

---

# 162. ERROR CONTRACT TEST

Verify:

    error code
    safe message
    request ID

remain available.

---

# 163. SECURITY CONTRACT TEST

For every sensitive endpoint:

    authorized → success
    unauthorized → denied

---

# 164. CROSS-CASE CONTRACT TEST

Candidate endpoint:

    Case B candidate
       ↓
    Case A investigator

must not return data.

---

# 165. SOURCE FRAME CONTRACT TEST

Unauthorized source-frame access:

    denied.

---

# 166. PROVENANCE CONTRACT TEST

Authorized candidate:

    provenance resolves

Unauthorized candidate:

    no leakage.

---

# 167. LIVE EVENT CONTRACT TEST

Authorized stream:

    events delivered

Unauthorized stream:

    events not delivered.

---

# 168. RECONNECT CONTRACT TEST

WebSocket disconnect:

    client reconnects
       ↓
    snapshot
       ↓
    events

without inconsistent state.

---

# 169. IDEMPOTENCY CONTRACT TEST

Repeated search creation with same idempotency key:

    one logical operation

---

# 170. CONCURRENCY CONTRACT TEST

Two authorized investigators operating on the same sighting/review must follow review concurrency policy.

---

# 171. OPTIMISTIC CONCURRENCY

Where review is versioned:

    if_version

or equivalent may protect against overwriting a newer review.

---

# 172. CONFLICT RESPONSE

Concurrent update conflict may return:

    409 CONFLICT

with safe information.

---

# 173. REVIEW AUDIT CONTRACT

Review API must preserve historical change information according to audit policy.

---

# 174. DELETE OPERATIONS

Do not expose destructive deletion of source evidence through Face Trace.

Deletion of derived biometric records must follow retention/admin policy.

---

# 175. SOFT DELETE

Use soft deletion only where the broader data model requires it.

Do not silently invent a second deletion semantics.

---

# 176. RETENTION STATUS

API may expose:

    active
    expired

where useful.

Do not expose internal retention mechanisms unnecessarily.

---

# 177. EXPIRED RESOURCE

Expired biometric result should not be searchable.

---

# 178. CACHE SECURITY

Ensure stale API cache cannot reveal resources after access revocation.

---

# 179. OBJECT STORAGE

Prefer secure short-lived access URLs or streamed authorized access.

---

# 180. SOURCE FRAME EXPIRATION

Temporary signed URLs should have bounded lifetime.

---

# 181. API OBSERVABILITY

Monitor:

    request latency
    status codes
    dependency failures
    search creation rate
    candidate retrieval rate

---

# 182. WEB SOCKET OBSERVABILITY

Monitor:

    active connections
    reconnects
    dropped events
    subscription failures

---

# 183. EVENT OBSERVABILITY

Monitor:

    published
    delivered
    failed
    retried
    dead-lettered

---

# 184. NO BIOMETRIC CONTENT IN METRICS

Do not put:

    image
    vector
    sensitive source information

into metrics.

---

# 185. VERSIONED DOMAIN CONTRACT

The stable conceptual contract is:

    Search
       ↓
    Processing Run
       ↓
    Candidate
       ↓
    Sighting
       ↓
    Review
       ↓
    Provenance

---

# 186. API EXAMPLE — SEARCH

Conceptual:

    POST /api/v1/face-searches

    {
      "investigation_id": "INV-001",
      "reference_id": "REF-004",
      "source_scope": {
        "evidence_ids": ["E-01", "E-02"]
      },
      "policy_id": "face-policy"
    }

Response:

    {
      "search_id": "SEARCH-001",
      "job_id": "JOB-001",
      "status": "QUEUED"
    }

Example only; actual IDs/schema are project-defined.

---

# 187. API EXAMPLE — CANDIDATE

Conceptual:

    {
      "candidate_id": "CAND-001",
      "sighting_id": "SIGHT-001",
      "source_id": "CAM-02",
      "source_timestamp": "...",
      "frame_number": 9921,
      "similarity": 0.91,
      "metric": "cosine",
      "quality_state": "GOOD",
      "review_state": "REVIEW_PENDING"
    }

No probability or guilt label.

---

# 188. API EXAMPLE — PROVENANCE

Conceptual:

    {
      "sighting_id": "SIGHT-001",
      "processing_run_id": "RUN-001",
      "evidence_id": "E-02",
      "artifact_id": "ART-02",
      "frame_number": 9921,
      "model_id": "...",
      "model_version": "...",
      "policy_id": "...",
      "policy_version": "..."
    }

---

# 189. API EXAMPLE — EVENT

Conceptual:

    {
      "event_id": "EVT-001",
      "event_type": "face.sighting.created",
      "event_version": 1,
      "occurred_at": "...",
      "aggregate_id": "SIGHT-001",
      "payload": {
        "source_id": "CAM-02",
        "candidate_id": "CAND-001"
      }
    }

---

# 190. CONTRACT LANGUAGE

API documentation must use:

    candidate
    observation
    sighting
    similarity
    machine-generated
    review pending

Avoid:

    confirmed suspect
    criminal identified
    certainty

---

# 191. NEGATIVE RESULT CONTRACT

Successful no-match:

    status = COMPLETED
    candidate_count = 0

Message:

    no qualifying candidate found under the configured policy

---

# 192. PARTIAL RESULT CONTRACT

Partial processing:

    status = PARTIAL

Return source-level reason/status.

---

# 193. FAILURE RESULT CONTRACT

Failure:

    status = FAILED

with structured safe error.

---

# 194. LIVE DEGRADED CONTRACT

Live degraded:

    status = DEGRADED

with operational reason:

    GPU fallback
    source reconnecting
    processing slower than source

only if actually detected.

---

# 195. EVENTUAL CONSISTENCY CONTRACT

Neo4j/vector projections may lag.

API should distinguish:

    authoritative state

from:

    projection status

when useful.

---

# 196. PROJECTION STATUS

Potential:

    vector_index_status
    graph_projection_status

Do not expose internal implementation unless useful to the client.

---

# 197. FRONTEND FALLBACK

If realtime event fails:

    API polling/snapshot refresh

must recover the UI.

---

# 198. SOURCE FRAME FAILURE

If source frame extraction fails:

    return safe structured error

Do not substitute a random neighboring frame without labeling it.

---

# 199. SOURCE FRAME APPROXIMATION

If decoder seeking returns an approximate frame:

    preserve actual returned frame context

and avoid claiming exactness unless guaranteed.

---

# 200. API SECURITY FINAL CHECK

Before release:

[ ] Authentication integrated

[ ] Case authorization integrated

[ ] Investigation authorization integrated

[ ] Source authorization integrated

[ ] Vector scope enforced

[ ] Raw embedding excluded

[ ] RTSP secrets excluded

[ ] Source-frame access protected

[ ] WebSocket channels protected

[ ] Rate limits configured

[ ] Pagination bounded

[ ] Errors sanitized

[ ] Audit integrated

---

# 201. API PERFORMANCE FINAL CHECK

[ ] Search creation is non-blocking

[ ] Candidate lists are paginated

[ ] Provenance is summarized by default

[ ] Source frames are fetched on demand

[ ] WebSocket payloads are bounded

[ ] Expensive filters are indexed

[ ] Rate limits prevent abuse

---

# 202. EVENT FINAL CHECK

[ ] Stable event ID

[ ] Event type

[ ] Event version

[ ] Aggregate ID

[ ] Timestamp

[ ] Scope IDs

[ ] Minimal payload

[ ] Idempotent consumption

[ ] Replay-safe behavior

---

# 203. API TEST MATRIX

| Contract | Success | Auth | Validation | Failure | Realtime |
|---|---|---|---|---|---|
| Search create | ✓ | ✓ | ✓ | ✓ | ✓ |
| Search status | ✓ | ✓ | ✓ | ✓ | ✓ |
| Candidates | ✓ | ✓ | ✓ | ✓ | ✓ |
| Candidate detail | ✓ | ✓ | ✓ | ✓ | — |
| Source frame | ✓ | ✓ | ✓ | ✓ | — |
| Sighting | ✓ | ✓ | ✓ | ✓ | ✓ |
| Provenance | ✓ | ✓ | ✓ | ✓ | — |
| Review | ✓ | ✓ | ✓ | ✓ | ✓ |
| Live stream | ✓ | ✓ | ✓ | ✓ | ✓ |

---

# 204. DEFINITION OF DONE

The API/Event layer is complete when:

[ ] REST resources follow CrimeKit conventions.

[ ] Authentication is integrated.

[ ] Authorization is enforced server-side.

[ ] Search creation is asynchronous.

[ ] Job status is durable.

[ ] Candidate/sighting APIs are paginated.

[ ] Source-frame retrieval is protected.

[ ] Provenance endpoint works.

[ ] Review endpoint is auditable.

[ ] Errors are structured and sanitized.

[ ] Events are versioned and idempotent.

[ ] WebSocket channels are authorized.

[ ] Reconnect/reconciliation works.

[ ] Raw biometric vectors are not exposed.

[ ] Cross-case leakage tests pass.

[ ] OpenAPI/event contracts are validated.

---

# 205. FINAL CONTRACT

The Face Trace API is not a thin transport wrapper around a face model.

It is the controlled boundary between:

    Investigator
       ↓
    CrimeKit
       ↓
    Forensic Processing
       ↓
    Machine Matching
       ↓
    Durable Evidence Intelligence
       ↓
    Human Review

The contract must preserve:

    authorization
    provenance
    reproducibility
    realtime usability
    data minimization
    human oversight

A successful API implementation makes the machine result accessible without making the machine result more authoritative than the evidence and the investigator review that support it.
