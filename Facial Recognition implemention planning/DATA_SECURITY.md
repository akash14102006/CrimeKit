# CrimeKit Face Trace Investigator — DATA SECURITY & PRIVACY SPECIFICATION

**Document:** `DATA_SECURITY.md`  
**Subsystem:** Face Trace Investigator  
**Scope:** Biometric data, source evidence, authorization, storage, transport, retention, audit, privacy, and threat protection  
**Audience:** Security engineers, backend engineers, forensic engineers, infrastructure, database, frontend, QA, operations  
**Status:** Authoritative security and privacy implementation specification

---

# 1. PURPOSE

This document defines how CrimeKit protects sensitive data used by Face Trace Investigator.

The subsystem processes potentially sensitive:

- reference face images
- source video/images
- face crops
- face detections
- face tracks
- face embeddings
- candidate matches
- sightings
- investigator review decisions
- provenance metadata
- audit records

The security objective is:

    authorized access
       +
    minimum necessary exposure
       +
    strong case isolation
       +
    protected biometric processing
       +
    complete auditability

Security must not be added after the feature is implemented.

It is part of the architecture.

---

# 2. SECURITY PRINCIPLE

The central rule is:

> A valid face-analysis result is not useful if the wrong person can access it.

Therefore the system must enforce security at:

    API
    ↓
    Service
    ↓
    Worker
    ↓
    Storage
    ↓
    Database
    ↓
    Vector Search
    ↓
    Graph
    ↓
    Realtime
    ↓
    Export

No single frontend control is sufficient.

---

# 3. DATA CLASSIFICATION

The subsystem should classify data into appropriate protection levels.

## 3.1 Critical/Sensitive

Examples:

    raw face images
    reference images
    face crops
    face embeddings
    restricted source video
    cross-case search results

These require the strongest controls.

## 3.2 Investigative

Examples:

    candidate sightings
    similarity values
    tracks
    processing metadata
    source timestamps
    review status

These remain case-controlled.

## 3.3 Operational

Examples:

    job IDs
    processing latency
    queue depth
    worker health

Operational data must still avoid sensitive biometric values.

---

# 4. DATA FLOW SECURITY MODEL

Secure flow:

    Investigator
        ↓
    Authentication
        ↓
    Case Authorization
        ↓
    Evidence Authorization
        ↓
    Face Investigation
        ↓
    Protected Processing
        ↓
    Protected Persistence
        ↓
    Authorized Retrieval
        ↓
    Investigator

Never:

    Browser
       ↓
    Direct biometric database

Never:

    Browser
       ↓
    Direct object storage without authorization

---

# 5. TRUST BOUNDARIES

The major trust boundaries are:

    Internet / browser
        ↓
    CrimeKit API
        ↓
    private application network
        ↓
    workers
        ↓
    data services
        ↓
    evidence/model storage

Each transition must have explicit controls.

---

# 6. AUTHENTICATION

Use the existing CrimeKit authentication system.

Do not create a second login system for Face Trace Investigator.

Every sensitive request must have an authenticated identity unless the project explicitly defines a controlled service-to-service operation.

---

# 7. SERVICE AUTHENTICATION

If the architecture separates:

    API
    Face Worker
    Video Worker
    Projection Worker

service-to-service calls should use the existing internal authentication mechanism.

Do not trust network location alone.

---

# 8. AUTHORIZATION

Authorization must be evaluated for:

- case access
- evidence access
- face-investigation access
- source-frame access
- candidate access
- review actions
- export
- cross-case search
- administrative model operations

---

# 9. ROLE-BASED ACCESS CONTROL

Use existing CrimeKit RBAC.

Conceptual permissions:

    face_investigation.read
    face_investigation.create
    face_investigation.search
    face_investigation.review
    face_investigation.export
    face_investigation.cross_case_search
    face_model.manage

Exact permission names must follow existing CrimeKit conventions.

---

# 10. RESOURCE-LEVEL AUTHORIZATION

Roles alone are not enough.

The backend must verify:

    user
       ↓
    role
       ↓
    case
       ↓
    investigation
       ↓
    evidence
       ↓
    requested resource

A user with permission to use Face Trace does not automatically receive access to every case.

---

# 11. CASE ISOLATION

Every face investigation must have a case context.

The system must prevent:

    Case A
      ↓
    accidental access
      ↓
    Case B biometric data

Case ID must be a first-class authorization boundary.

---

# 12. TENANT ISOLATION

If CrimeKit is multi-tenant:

    tenant
       ↓
    case
       ↓
    investigation
       ↓
    biometric data

Tenant boundaries must be enforced server-side.

Never rely on tenant IDs supplied by the browser.

---

# 13. EVIDENCE AUTHORIZATION

Before processing evidence:

    authenticate
       ↓
    case authorization
       ↓
    evidence authorization
       ↓
    evidence state validation
       ↓
    processing

Do not accept an evidence ID as proof of access.

---

# 14. SOURCE FRAME AUTHORIZATION

A candidate contains a pointer to source evidence.

That pointer is not an access token.

When viewing a source frame:

    authenticate
       ↓
    case access
       ↓
    evidence access
       ↓
    artifact access
       ↓
    frame

---

# 15. CROSS-CASE SEARCH

Cross-case search is a privileged capability.

Default:

    current case only

Privileged:

    explicit permission
       ↓
    explicit scope
       ↓
    restricted search
       ↓
    audit

Do not expose a global biometric search control to ordinary investigators.

---

# 16. CROSS-CASE RESULT MINIMIZATION

If cross-case search is authorized, return only the minimum information necessary.

Do not expose:

- unrelated case details
- unrestricted source media
- unrelated investigator identities
- unnecessary case metadata

A candidate from another case must remain subject to its own access policy.

---

# 17. CASE CLOSURE / ACCESS REVOCATION

If case access changes while a user is active:

    revalidate

Do not assume a previously loaded page still has permission indefinitely.

The backend remains authoritative.

---

# 18. USER DEACTIVATION

If a user is deactivated:

    future access
       ↓
    denied

Any running job follows case/workflow rules.

Do not rely on the browser session to remain valid.

---

# 19. BIOMETRIC DATA PRINCIPLE

Face embeddings must be treated as sensitive biometric-derived data.

They are not normal application preferences.

They must not be handled casually in:

- browser storage
- logs
- analytics
- URLs
- notifications
- screenshots
- error messages

---

# 20. RAW IMAGE PROTECTION

Reference images and source evidence must be stored using the approved CrimeKit evidence/storage system.

Do not create a second unmanaged image store for Face Trace.

---

# 21. FACE CROP PROTECTION

A face crop derived from evidence remains sensitive.

If stored:

    source artifact
    processing run
    access policy
    retention policy

must be associated.

Do not create anonymous files such as:

    face_001.jpg

without domain metadata.

---

# 22. EMBEDDING STORAGE

Embeddings must be stored only when required by the feature.

When stored:

- scope them to the appropriate case/collection
- associate model/version
- protect access
- enforce retention
- prevent unauthorized search

---

# 23. RAW EMBEDDINGS MUST NOT BE LOGGED

Never log complete embedding arrays.

Bad:

    embedding=[0.02, -0.19, ...]

Correct diagnostic metadata:

    embedding_dimension=512
    model_version=X
    processing_run=RUN-001

---

# 24. RAW EMBEDDINGS MUST NOT BE SENT TO BROWSER

The browser normally requires:

    similarity
    candidate ID
    quality
    timestamp
    provenance references

It does not require:

    raw vector

Any accidental API exposure of embeddings is a security defect unless explicitly authorized.

---

# 25. URL SECURITY

Never put:

- embeddings
- face crops encoded into URLs
- access credentials
- signed secrets
- unrestricted source tokens

into application routes.

IDs are acceptable where required, but IDs do not provide authorization.

---

# 26. LOCAL BROWSER STORAGE

Do not store protected biometric data in:

    localStorage
    sessionStorage
    IndexedDB

by default.

Sensitive data should remain server-controlled unless a specifically approved UX requirement exists.

---

# 27. BROWSER CACHE

Avoid long-lived caching of sensitive biometric resources.

Use appropriate cache-control behavior through the existing backend/frontend security architecture.

---

# 28. NETWORK ENCRYPTION

Sensitive data must travel over secure transport.

Use the existing CrimeKit TLS/HTTPS architecture.

Do not transmit biometric data over unencrypted external networks.

---

# 29. INTERNAL NETWORK SECURITY

Private services should use protected internal networking.

Examples:

    API → worker
    worker → PostgreSQL
    worker → pgvector
    worker → Neo4j

Do not expose databases directly to the public internet.

---

# 30. OBJECT STORAGE SECURITY

Original evidence and sensitive derived artifacts should use protected object storage.

Prefer:

    private bucket/container
    authenticated access
    scoped access
    time-limited access where supported

Do not make case evidence public.

---

# 31. SIGNED MEDIA ACCESS

If signed URLs are used:

- make them short-lived where practical
- scope them to the requested artifact
- never place unrestricted bucket credentials in them
- use existing CrimeKit mechanisms

---

# 32. STORAGE ENCRYPTION

Use platform-approved encryption at rest.

Do not invent custom encryption algorithms.

Protect:

    database
    vector data
    evidence storage
    backups
    derived media

according to the environment's security policy.

---

# 33. KEY MANAGEMENT

Use the existing CrimeKit/infrastructure secret and key-management system.

Do not hard-code:

- encryption keys
- database credentials
- object storage secrets
- model credentials

---

# 34. SECRET MANAGEMENT

Secrets belong in:

    approved secret manager
    deployment secret
    protected environment configuration

Never:

    source code
    frontend bundle
    Git history
    logs

---

# 35. MODEL CREDENTIALS

If a licensed/private InsightFace model requires credentials:

- keep them server-side
- restrict access
- rotate as required
- never send them to browsers
- never log them

---

# 36. HOSTED MODEL ENDPOINT SECURITY

The project-provided InsightFace evaluation document describes a restricted hosted evaluation endpoint.

If used for authorized evaluation:

- keep endpoint credentials private
- do not commit URL/credentials
- do not expose them to browser
- do not configure production inference to depend on the evaluation service

---

# 37. DATA MINIMIZATION

Only collect/process data necessary for:

    reference generation
    candidate search
    provenance
    review
    reporting

Do not add unrelated biometric attributes.

---

# 38. PROHIBITED FACE ATTRIBUTES

Do not introduce unrelated inference such as:

- race
- religion
- political affiliation
- sexual orientation
- emotion
- inferred criminal propensity

These are outside the Face Trace Investigator scope.

---

# 39. PURPOSE LIMITATION

Face analysis must occur within an authorized investigative purpose.

Do not reuse the feature as a general-purpose people profiling engine.

---

# 40. RETENTION

Define retention for:

    reference image
    derived face crop
    embedding
    detection
    track
    candidate
    sighting
    review
    audit

Different data types may have different retention periods.

---

# 41. DEFAULT RETENTION PRINCIPLE

Do not retain sensitive derived biometric data indefinitely by default.

Follow CrimeKit's governing retention policy.

---

# 42. EMBEDDING RETENTION

An embedding should remain searchable only for the duration defined by policy.

Deleting relational metadata must not be treated as sufficient if a searchable vector remains in an index.

---

# 43. VECTOR DELETION

When an embedding expires/deletes:

    authoritative record
       ↓
    vector index
       ↓
    cached representation
       ↓
    derived search structure

must be considered.

Do not leave searchable biometric remnants.

---

# 44. DERIVED CROP RETENTION

Face crops should only be retained when justified by:

- provenance
- source verification
- operational workflow
- reporting

Do not automatically persist every recognized frame crop.

---

# 45. FRAME SNAPSHOT RETENTION

Annotated source-frame snapshots are derived artifacts.

They must follow:

    provenance
    access control
    retention

Do not retain infinite duplicates of source frames.

---

# 46. DATA DELETION

Deletion workflows must consider the full dependency chain.

Example:

    investigation removal/expiry
       ↓
    reference
       ↓
    embedding
       ↓
    candidates
       ↓
    sightings
       ↓
    vectors
       ↓
    graph projection
       ↓
    derived media

Actual order follows the database/domain constraints.

---

# 47. LEGAL HOLD / GOVERNANCE

If CrimeKit has a legal-hold/evidence-preservation mechanism, Face Trace data associated with preserved evidence must follow it.

Do not automatically delete protected records.

---

# 48. AUDITABILITY

Every sensitive action should be auditable.

Minimum:

    create investigation
    upload reference
    select evidence
    start search
    cancel search
    view candidate
    view source
    perform review
    export
    cross-case search

---

# 49. AUDIT RECORD

Audit should identify:

    actor
    action
    target
    case
    investigation
    timestamp
    outcome

Service execution should be distinguishable from human initiation.

---

# 50. AUDIT IMMUTABILITY

Audit history should not be freely edited by application users.

Follow the existing CrimeKit audit architecture for append-only/tamper-resistant behavior.

---

# 51. REVIEW AUDIT

Every review transition should preserve:

    reviewer
    previous state
    new state
    timestamp
    reason/notes

Do not silently overwrite the previous decision.

---

# 52. SOURCE ACCESS AUDIT

Where policy requires, viewing protected source frames/media should be auditable.

Do not silently expose sensitive evidence without an access trail.

---

# 53. EXPORT AUDIT

Record:

    who exported
    what investigation
    scope
    export type
    when

Do not make exports invisible.

---

# 54. CROSS-CASE AUDIT

Every cross-case face search must produce an audit event.

Include:

    actor
    source case/scope
    authorized target scope
    time
    result count where appropriate

Do not log raw biometric data.

---

# 55. SECURITY LOGGING

Security logs may include:

    request ID
    user ID
    case ID
    investigation ID
    action
    result

They must not include raw:

    embeddings
    face images
    credentials

---

# 56. ERROR MESSAGE SECURITY

User-facing errors must not reveal:

- stack traces
- filesystem paths
- database connection strings
- credentials
- model secrets
- internal network addresses

---

# 57. API IDOR PROTECTION

Never authorize by:

    candidate_id exists

Only authorize through the resource relationship.

Example:

    user
       ↓
    case
       ↓
    investigation
       ↓
    candidate

---

# 58. PATH TRAVERSAL

Never construct file access paths directly from user-controlled filenames or paths.

Use safe storage IDs and the existing artifact abstraction.

---

# 59. FILE UPLOAD SECURITY

Reference images and videos are untrusted inputs.

Validate:

- size
- content
- type
- decoding
- supported format

Do not trust extension alone.

---

# 60. MEDIA DECODE ISOLATION

Where supported by the architecture, run media parsing/decoding in isolated workers/containers.

Malformed media must not compromise the API process.

---

# 61. RESOURCE EXHAUSTION

Protect against:

- huge images
- huge videos
- extremely long streams
- excessive concurrent searches
- enormous frame counts
- excessive batch sizes

Use configurable admission limits.

---

# 62. DENIAL OF SERVICE

Potential abusive workflow:

    create hundreds of face searches
       ↓
    GPU exhaustion

Mitigations:

- authentication
- authorization
- rate limits
- queue limits
- per-user limits
- per-case limits
- resource quotas

Use the existing CrimeKit mechanisms.

---

# 63. REQUEST RATE LIMITING

Protect high-cost operations such as:

    investigation creation
    reference processing
    search creation
    source-frame retrieval

Do not over-restrict normal investigator workflows.

---

# 64. UPLOAD LIMITS

Apply limits to:

    file size
    image resolution
    video duration
    batch size

The exact limits must be configurable.

---

# 65. PROCESSING LIMITS

Apply limits to:

    job duration
    concurrent videos
    concurrent inference
    frame queue depth

Do not allow unbounded work.

---

# 66. WEBSOCKET SECURITY

WebSocket connections must be authenticated and authorized.

A browser subscribing to:

    CASE-001

must only receive events for cases the user can access.

---

# 67. WEBSOCKET DATA MINIMIZATION

Realtime events should contain:

    candidate ID
    sighting ID
    timestamp
    source ID
    similarity
    quality
    status

Do not send:

    embedding
    raw source video
    unrestricted face image

---

# 68. WEBSOCKET RECONNECT SECURITY

On reconnect:

    re-authenticate where required
       ↓
    reauthorize
       ↓
    resync state

Do not automatically restore access based only on a previous connection.

---

# 69. WEB AUTHORIZATION FAILURE

If access is revoked:

    unsubscribe
    stop protected retrieval
    clear sensitive state

Follow existing session/case security behavior.

---

# 70. API TOKEN SECURITY

Do not put long-lived secrets in:

    query parameters
    source-frame URLs
    WebSocket messages

Use the existing secure token/session mechanism.

---

# 71. CORS

Follow existing CrimeKit CORS policy.

Do not use:

    allow_origins=["*"]

for sensitive production APIs merely to simplify local development.

---

# 72. CSRF

If CrimeKit uses cookie-based authentication, protect state-changing browser requests according to the existing CSRF strategy.

Do not invent another mechanism.

---

# 73. SECURITY HEADERS

Follow the platform's existing security-header policy, including appropriate:

    CSP
    frame protections
    content-type protections
    transport security

Do not weaken global policy for Face Trace.

---

# 74. CONTENT SECURITY POLICY

Do not permit arbitrary third-party script execution merely because the face viewer needs video/image support.

Use the existing CSP strategy.

---

# 75. FRONTEND SECRET RULE

No secret required to access:

    InsightFace
    PostgreSQL
    Redis
    Neo4j
    object storage

may be bundled into the frontend application.

---

# 76. BROWSER DEVTOOLS

Assume a user can inspect all frontend-visible data.

Therefore:

    do not send sensitive data unless the user is authorized and the UI truly needs it.

Client-side obfuscation is not security.

---

# 77. API RESPONSE MINIMIZATION

Endpoints should return only necessary fields.

List:

    candidate summary

Detail:

    richer metadata

Source:

    authorized evidence

Do not return full domain records indiscriminately.

---

# 78. GRAPH SECURITY

Neo4j data access must follow case authorization.

Do not allow arbitrary graph traversal that escapes the authorized scope.

---

# 79. GRAPH QUERY SECURITY

Use parameterized Cypher.

Never concatenate investigator input into executable Cypher strings.

---

# 80. VECTOR QUERY SECURITY

Use parameterized vector queries.

Do not build SQL from raw user input.

---

# 81. VECTOR SEARCH SCOPE

Apply authorization before/during retrieval as supported by the data model.

Do not:

    retrieve all vectors
       ↓
    filter unauthorized rows in application memory

---

# 82. DATABASE LEAST PRIVILEGE

Face workers should have only the database permissions required for their responsibilities.

Do not use an unrestricted database superuser.

---

# 83. NEO4J LEAST PRIVILEGE

Graph projection workers should use the minimum required permissions.

Do not provide arbitrary administration credentials to normal workers.

---

# 84. OBJECT STORAGE LEAST PRIVILEGE

Workers should access only relevant buckets/containers/prefixes according to project policy.

---

# 85. SECRET ROTATION

Credentials should be rotatable without modifying source code.

Use environment/secret-manager configuration.

---

# 86. BACKUP SECURITY

Backups containing:

    face embeddings
    reference images
    source evidence

must receive the same or stronger access protection as primary data.

---

# 87. BACKUP RETENTION

Backup retention must align with evidence/biometric retention policy.

Do not delete primary biometric data while leaving indefinite accessible backups without governance.

---

# 88. DISASTER RECOVERY SECURITY

Recovery environments must preserve:

- case isolation
- access controls
- secrets
- encryption
- auditability

Do not create an insecure temporary recovery database.

---

# 89. DEVELOPMENT ENVIRONMENT

Development should use:

- synthetic/public/authorized media
- non-production secrets
- non-production data

Do not copy production biometric databases to developer laptops unless explicitly authorized and protected.

---

# 90. LOCAL DEVELOPMENT DATA

Do not commit:

- real faces
- real CCTV
- real embeddings
- real evidence

to Git.

---

# 91. TEST DATA

Use:

    synthetic
    public
    explicitly authorized

test datasets.

Document the provenance of any sensitive test fixture.

---

# 92. TEST SECRETS

Use separate test credentials.

Never reuse production secrets in automated tests.

---

# 93. SECURITY TESTING

Required security tests include:

- unauthorized case
- unauthorized evidence
- IDOR
- cross-case search
- protected source frame
- review permission
- export permission
- WebSocket authorization
- vector query scope
- graph query scope

---

# 94. EMBEDDING LEAK TEST

API tests should ensure ordinary candidate/detail responses do not contain raw embeddings.

---

# 95. LOG LEAK TEST

Automated tests or log inspection should ensure embeddings/secrets do not appear in application logs.

---

# 96. STORAGE LEAK TEST

Verify that protected evidence cannot be accessed using:

- guessed URLs
- old signed URLs after expiration
- another case's artifact ID
- unauthenticated requests

where those attack paths apply.

---

# 97. REVIEW AUTHORIZATION TEST

Verify only authorized roles can perform review transitions.

---

# 98. CROSS-CASE TEST

Verify:

    Case A investigator
       ↓
    Case B vector search

returns:

    Access Denied

unless explicitly authorized.

---

# 99. WEBSOCKET CASE ISOLATION TEST

Connect a user authorized for:

    Case A

and verify they do not receive:

    Case B events

---

# 100. TENANT ISOLATION TEST

For multi-tenant deployments:

    Tenant A
       ↓
    cannot read
       ↓
    Tenant B face data

Test both API and data-access layers.

---

# 101. SESSION SECURITY

Use existing CrimeKit session/token expiration.

Sensitive pages must not remain authorized forever because a browser tab stays open.

---

# 102. RE-AUTHENTICATION

For especially sensitive operations, CrimeKit may require re-authentication/step-up authentication depending on policy.

Potential examples:

    cross-case search
    export
    administrative model management

Do not invent step-up policy without product/security approval.

---

# 103. ADMINISTRATION

Model management operations should be restricted to authorized administrative roles.

Examples:

    activate model
    deactivate model
    change matching policy
    change retention
    change GPU settings

Investigators should not normally perform these actions.

---

# 104. MODEL CONFIGURATION SECURITY

Matching thresholds/policies are security-sensitive because they affect system behavior.

Restrict modification permissions.

---

# 105. MODEL ARTIFACT SECURITY

Model artifacts should be loaded only from approved locations.

Do not allow an investigator to upload an arbitrary model and make the production worker execute it.

---

# 106. SUPPLY CHAIN

Review:

    InsightFace package
    ONNX Runtime
    OpenCV
    model artifacts
    tracking libraries
    container base images

Use existing dependency scanning.

---

# 107. PACKAGE PINNING

Pin/lock dependencies according to CrimeKit standards.

Do not casually upgrade inference dependencies in production.

---

# 108. MODEL ARTIFACT INTEGRITY

Verify:

    expected artifact
    checksum/manifest where available
    version

before activation.

---

# 109. RUNTIME SECURITY

Containerized workers should use:

- minimum permissions
- non-root execution where feasible
- restricted filesystem
- restricted network
- resource limits

Follow platform security standards.

---

# 110. WORKER ISOLATION

Inference workers should not automatically have:

    admin database access
    unrestricted filesystem access
    unrestricted internet access

Only grant required capabilities.

---

# 111. MEDIA PROCESSOR ISOLATION

Video processing may interact with complex codecs/parsers.

Where feasible, isolate media processing from public API processes.

---

# 112. SECURITY OF TEMP FILES

Temporary face/video files must:

- use controlled directories
- use restrictive permissions
- have cleanup policy
- not remain indefinitely

Do not store sensitive temporary files in publicly served directories.

---

# 113. TEMP FILE CLEANUP

After processing:

    remove unneeded temporary media

according to retention policy.

Preserve only artifacts required for forensic workflow.

---

# 114. MEMORY PROTECTION

Do not intentionally persist sensitive biometric content in long-lived process memory beyond required processing.

Exact memory zeroization is platform/runtime dependent; do not claim it unless implemented and verified.

---

# 115. ERROR RECOVERY SECURITY

Failed processing must not accidentally expose:

- source media
- embeddings
- temporary paths
- credentials

Clean up temporary resources safely.

---

# 116. FAILED JOB SECURITY

A failed job must still enforce the same access rules as a successful job.

Do not make failed-job diagnostics publicly accessible.

---

# 117. DEBUG MODE

Debug mode must be:

- disabled by default
- restricted
- audited where sensitive
- safe against biometric leakage

---

# 118. DEVELOPMENT DEBUGGING

Never ask engineers to solve matching issues by printing complete face vectors into logs.

Use:

    model version
    vector dimension
    similarity
    quality
    processing IDs

---

# 119. PRIVACY-AWARE TELEMETRY

Generic analytics systems must not receive:

- face images
- embeddings
- raw video
- candidate source frames

unless explicitly approved.

---

# 120. LOGGING IDENTIFIERS

Safe correlation identifiers include:

    request_id
    job_id
    investigation_id
    processing_run_id
    evidence_id

where policy permits.

---

# 121. NO BIOMETRIC METRIC LABELS

Do not create metrics such as:

    person_name="..."

or:

    embedding_id="..."

where that creates sensitive leakage.

Use non-sensitive operational identifiers.

---

# 122. SECURITY INCIDENT RESPONSE

A suspected biometric-data exposure should follow CrimeKit's security incident response process.

Potential triggers:

- embedding exposure
- unauthorized source media
- secret leakage
- cross-case access
- storage misconfiguration
- compromised model credentials

---

# 123. INCIDENT CONTAINMENT

When exposure occurs:

1. stop further exposure
2. preserve incident metadata
3. rotate credentials when appropriate
4. identify affected scope
5. audit access
6. restore secure configuration
7. follow organizational incident procedures

Do not delete evidence needed for incident investigation.

---

# 124. SECURITY MONITORING

Monitor for:

- repeated authorization failures
- suspicious cross-case requests
- unusual search volume
- abnormal export activity
- repeated source-media access failures

Use existing CrimeKit security monitoring.

---

# 125. ABUSE DETECTION

Possible signals:

    hundreds of searches in minutes
    massive evidence access
    repeated unauthorized cross-case attempts

Do not automatically label a user malicious without policy; record/alert according to security controls.

---

# 126. PRIVILEGED OPERATIONS

Administrative actions should be separately auditable.

Examples:

    change matching policy
    activate model
    modify retention
    enable cross-case search

---

# 127. SECURITY OF MATCHING POLICY

A threshold/policy modification can materially change investigative output.

Restrict who can change it.

Record:

    old policy
    new policy
    actor
    time
    reason/change record

---

# 128. SECURITY OF MODEL ACTIVATION

Model activation should require:

    approved artifact
    licensing status
    evaluation record
    authorization

Do not permit arbitrary model activation from the investigator UI.

---

# 129. DATA ACCESS INTERFACE

The security model should make these relationships explicit:

    User
      ↓
    Role
      ↓
    Case
      ↓
    Investigation
      ↓
    Evidence
      ↓
    Face Data

Avoid implicit access paths.

---

# 130. SECURE API DESIGN

Every sensitive endpoint should define:

    authentication
    authorization
    input validation
    output minimization
    audit behavior

---

# 131. API RESOURCE ENUMERATION

Do not allow an unauthorized user to infer large amounts of information by iterating IDs.

Use:

- authorization
- safe error semantics
- rate limits

Do not leak whether a restricted candidate exists unless policy permits.

---

# 132. ERROR SEMANTICS

Where appropriate, distinguish:

    access denied

from:

    resource not found

according to the existing security model.

Do not leak restricted resource existence.

---

# 133. SECURITY OF SEARCH RESULTS

Candidate results should inherit the source evidence's access constraints.

Do not make a candidate less protected than its source.

---

# 134. PROVENANCE SECURITY

Provenance should reveal only what the current investigator is authorized to see.

A provenance chain must not become a side channel for restricted case information.

---

# 135. GRAPH SIDE-CHANNEL PROTECTION

A graph query must not allow investigators to discover:

    restricted evidence
    unrelated case entities
    hidden relationships

through connected-node traversal.

---

# 136. TIMELINE SIDE-CHANNEL PROTECTION

Timeline APIs must apply the same case/evidence authorization as direct candidate APIs.

---

# 137. REPORT SIDE-CHANNEL PROTECTION

A report containing a face candidate must not accidentally include restricted evidence from another case.

---

# 138. EXPORT CONTENT CONTROL

Exports should contain only the approved scope.

Potential controls:

    case
    investigation
    source
    review state

---

# 139. EXPORT MEDIA

If exporting source frames:

    use authorized artifact pipeline

Do not bypass storage security to generate downloads.

---

# 140. DATA MASKING

Where some fields are unnecessary for a role, consider reducing exposure according to CrimeKit's authorization model.

Do not invent masking that makes investigations unusable.

---

# 141. PRIVACY BY DESIGN

At each feature decision ask:

    Is this data necessary?
    Is the user authorized?
    Is retention required?
    Can we avoid storing it?
    Can we avoid sending it?
    Can we restrict the scope?

---

# 142. DEFAULT DENY

For uncertain permissions:

    deny access

Do not assume:

    allow

---

# 143. FAIL CLOSED

If authorization service is unavailable and the architecture cannot safely determine access:

    do not expose sensitive biometric data

Follow CrimeKit's availability/security policy.

---

# 144. AUTHORIZATION CACHE

If authorization results are cached, define:

    scope
    TTL
    invalidation

Do not allow stale permissions to expose sensitive data indefinitely.

---

# 145. TOKEN EXPIRATION

Short-lived access tokens and signed URLs should follow existing security policy.

Do not create permanent media access tokens.

---

# 146. SECURE HTTP HEADERS

Use existing secure headers and transport configuration.

Do not weaken the application's global security configuration for Face Trace.

---

# 147. DEPENDENCY VULNERABILITY

Monitor critical dependencies.

If a high-severity vulnerability affects:

    InsightFace
    ONNX Runtime
    OpenCV
    media codecs

follow the existing remediation policy.

---

# 148. PATCH MANAGEMENT

Model/runtime updates must be tested together.

Do not patch a GPU inference library in isolation without compatibility testing.

---

# 149. SECURITY REGRESSION

Every major release should re-run:

    authorization tests
    embedding exposure tests
    source access tests
    cross-case tests
    WebSocket tests
    secret scan
    dependency scan

---

# 150. SECURITY REVIEW CHECKLIST

Before merge:

[ ] Authentication uses existing CrimeKit.

[ ] Backend authorization is enforced.

[ ] Case isolation is enforced.

[ ] Evidence access is enforced.

[ ] Cross-case search is restricted.

[ ] Raw embeddings are not exposed.

[ ] Raw embeddings are not logged.

[ ] Sensitive source media is protected.

[ ] Object storage is private/controlled.

[ ] Secrets are not in source/frontend.

[ ] Temporary files are controlled.

[ ] API IDs do not bypass authorization.

[ ] WebSocket subscriptions are authorized.

[ ] Graph queries are scoped.

[ ] Vector queries are scoped.

[ ] Review actions are permission-controlled.

[ ] Exports are authorized.

[ ] Audit events exist.

[ ] Retention is defined.

[ ] Deletion covers vector/derived data.

[ ] Security tests pass.

---

# 151. PRIVACY REVIEW CHECKLIST

[ ] Purpose is documented.

[ ] Data collection is minimized.

[ ] Reference image handling is documented.

[ ] Embedding retention is documented.

[ ] Derived crop retention is documented.

[ ] Source media retention follows evidence policy.

[ ] Cross-case usage is controlled.

[ ] Test datasets are authorized.

[ ] Telemetry does not contain raw biometric data.

[ ] Analytics do not receive sensitive biometric data.

---

# 152. PRODUCTION READINESS SECURITY CHECKLIST

Before production:

[ ] TLS is configured.

[ ] Secrets use approved management.

[ ] Object storage is private.

[ ] Databases are private.

[ ] Inference workers are isolated.

[ ] Model artifacts are verified.

[ ] Dependency vulnerabilities are reviewed.

[ ] Authorization tests pass.

[ ] Audit works.

[ ] Backup security is validated.

[ ] Retention/deletion behavior is tested.

[ ] Incident process exists.

[ ] Operational monitoring exists.

---

# 153. SECURITY ACCEPTANCE CRITERIA

The subsystem is secure enough for its intended deployment only when:

1. An unauthorized investigator cannot access another case's face data.
2. Raw embeddings are not exposed through normal APIs.
3. Source media requires authorization.
4. Cross-case search requires explicit permission.
5. WebSocket events are case-scoped.
6. Review operations are permission-controlled.
7. Sensitive actions are audited.
8. Temporary sensitive files are controlled.
9. Secrets are not present in source/frontend/logs.
10. Vector and graph queries respect authorization.
11. Retention and deletion include derived biometric data.
12. Model configuration is protected.
13. Failure paths do not leak sensitive information.
14. Security regression tests exist.

---

# 154. THREAT MODEL SUMMARY

Primary threats:

    T1 — Unauthorized case access
    T2 — Cross-case biometric leakage
    T3 — IDOR through resource IDs
    T4 — Embedding leakage
    T5 — Source-media leakage
    T6 — WebSocket data leakage
    T7 — Malicious media upload
    T8 — GPU/worker resource exhaustion
    T9 — Secret leakage
    T10 — Supply-chain/model compromise
    T11 — Unauthorized policy/model modification
    T12 — Retention/deletion failure
    T13 — Graph/vector side-channel
    T14 — Audit tampering
    T15 — Excessive export

Every threat must have an applicable mitigation.

---

# 155. THREAT: UNAUTHORIZED CASE ACCESS

Attack:

    User has Case A
       ↓
    requests Face Investigation for Case B

Mitigation:

    backend case authorization

Expected:

    Access Denied

---

# 156. THREAT: IDOR

Attack:

    /face-sightings/12345

where the attacker guesses an existing ID.

Mitigation:

    resource-level authorization

Expected:

    inaccessible without case permission

---

# 157. THREAT: VECTOR LEAK

Attack:

    API returns raw embeddings

Mitigation:

    response schema excludes embedding

Expected:

    no raw vector in normal response

---

# 158. THREAT: SOURCE MEDIA LEAK

Attack:

    guess object-storage URL

Mitigation:

    private storage + authorized access

Expected:

    unauthorized access fails

---

# 159. THREAT: CROSS-CASE SEARCH ABUSE

Attack:

    ordinary investigator searches entire biometric index

Mitigation:

    privileged permission + explicit scope + audit

Expected:

    denied by default

---

# 160. THREAT: WEBSOCKET LEAK

Attack:

    user subscribes to another case's event channel

Mitigation:

    backend subscription authorization

Expected:

    subscription denied

---

# 161. THREAT: MALICIOUS VIDEO

Attack:

    malformed/hostile media file

Mitigation:

    isolated decoder worker + resource limits + safe parsing

Expected:

    processing failure without API compromise

---

# 162. THREAT: RESOURCE EXHAUSTION

Attack:

    many large video searches

Mitigation:

    rate limits + queue limits + worker quotas

Expected:

    controlled backpressure

---

# 163. THREAT: MODEL SUPPLY CHAIN

Attack:

    unauthorized model artifact

Mitigation:

    approved artifact source + checksum/manifest + activation controls

Expected:

    worker rejects unapproved artifact

---

# 164. THREAT: POLICY TAMPERING

Attack:

    unauthorized threshold change

Mitigation:

    privileged configuration + audit + versioning

Expected:

    unauthorized modification denied

---

# 165. THREAT: LOG LEAK

Attack:

    exception accidentally logs embeddings

Mitigation:

    structured logging + redaction + review/tests

Expected:

    no raw biometric vector

---

# 166. THREAT: RETENTION FAILURE

Attack:

    embedding deleted from PostgreSQL but remains searchable in vector store

Mitigation:

    deletion workflow includes vector cleanup and verification

Expected:

    vector no longer searchable

---

# 167. THREAT: GRAPH SIDE CHANNEL

Attack:

    graph traversal exposes restricted evidence

Mitigation:

    scoped graph queries / authorized projection

Expected:

    restricted relationships are not visible

---

# 168. THREAT: EXPORT ABUSE

Attack:

    unauthorized user exports candidate/source data

Mitigation:

    export authorization + audit

Expected:

    denied

---

# 169. SECURITY ARCHITECTURE PRINCIPLE

The system should assume:

    every client request is untrusted
    every uploaded media file is untrusted
    every resource ID is untrusted
    every frontend authorization decision is advisory
    every model artifact requires verification

Trust must be explicitly established.

---

# 170. SECURITY OPERATIONS

Security monitoring should support:

    alert
    investigate
    contain
    recover
    audit

for suspicious face-data access.

---

# 171. PRIVACY OPERATIONS

Operational procedures should define:

    access requests
    retention
    deletion
    incident response
    export
    legal hold
    model/provider changes

according to organizational policy.

---

# 172. SECURITY OF TEST/DEMO MODE

Demo mode must not disable:

    authorization
    provenance
    access controls

merely to simplify the SIH demonstration.

Use controlled test data instead.

---

# 173. NO DEBUG BYPASS

Never implement:

    DEBUG_AUTH_BYPASS=true

for production.

Temporary local development bypasses must not reach production configurations.

---

# 174. NO GLOBAL ADMIN BYPASS

Do not create code such as:

    if admin:
        skip all security

Administrative roles still follow least privilege.

---

# 175. NO SECURITY THROUGH HIDDEN UI

Hiding a button does not secure it.

Every protected endpoint must enforce permission server-side.

---

# 176. NO SECURITY THROUGH OBFSCURITY

Opaque IDs, hidden routes, or frontend obfuscation are not authorization mechanisms.

---

# 177. DATA FLOW AUDIT

Review every path:

    upload
    process
    store
    retrieve
    stream
    export
    delete

for sensitive data exposure.

---

# 178. DEPENDENCY AUDIT

Before release:

    package scan
    container scan
    model artifact verification
    secret scan

according to CrimeKit CI.

---

# 179. CONTAINER SECURITY

Where applicable:

- non-root
- read-only filesystem where practical
- minimal image
- no unnecessary utilities
- limited network
- CPU/memory/GPU limits

Follow existing infrastructure standards.

---

# 180. NETWORK SEGMENTATION

Keep:

    databases
    object storage
    GPU workers

behind appropriate private network controls.

---

# 181. FIREWALL RULES

Only required ports/services should communicate.

Do not make:

    PostgreSQL
    Neo4j
    Redis

public merely to simplify development.

---

# 182. ADMIN PORTS

Administrative interfaces should not be directly exposed publicly unless explicitly secured.

---

# 183. MONITORING DATA CLASSIFICATION

Operational dashboards should avoid showing:

    raw faces
    embeddings
    restricted source frames

unless specifically authorized.

---

# 184. SUPPORT ACCESS

Support/operations staff should not automatically receive investigator access to biometric case data.

Separate operational access from investigative access.

---

# 185. BREAK-GLASS ACCESS

If CrimeKit supports emergency/break-glass access:

    explicit reason
    strong authorization
    audit

must apply.

Do not create an informal support backdoor.

---

# 186. SECURITY TEST ENVIRONMENT

Security testing must use isolated infrastructure.

Do not penetration-test production face databases casually.

---

# 187. PENETRATION TEST SCOPE

Future security testing should include:

    API
    object storage
    WebSocket
    vector queries
    graph queries
    upload pipeline
    authentication
    authorization

---

# 188. SECURITY DOCUMENTATION

Security docs must distinguish:

    implemented
    planned
    assumed
    externally provided

Do not claim a security control exists until verified.

---

# 189. SECURITY CHANGE CONTROL

Changes to:

    authentication
    authorization
    vector scope
    storage access
    retention
    model activation
    matching policy

require security review as appropriate.

---

# 190. SECURITY REVIEW BEFORE RELEASE

Before release, answer:

    Who can search?
    What can they search?
    What can they see?
    What can they export?
    What remains case-scoped?
    What is cross-case?
    What is retained?
    What is deleted?
    What is logged?
    What happens if a dependency fails?

---

# 191. FINAL SECURITY PRINCIPLE

The strongest CrimeKit security model is:

    minimum data
        +
    minimum access
        +
    explicit authorization
        +
    protected processing
        +
    complete provenance
        +
    auditable actions
        +
    controlled retention

The Face Trace Investigator must never become a global, unrestricted biometric database simply because the underlying vector search technology makes it technically possible.

---

# 192. FINAL SECURITY CONTRACT

The trusted path is:

    AUTHENTICATED USER
          ↓
    AUTHORIZED CASE
          ↓
    AUTHORIZED EVIDENCE
          ↓
    PROTECTED FACE PROCESSING
          ↓
    PROTECTED BIOMETRIC RESULT
          ↓
    AUTHORIZED RETRIEVAL
          ↓
    SOURCE VERIFICATION
          ↓
    HUMAN REVIEW
          ↓
    AUDITED ACTION

Every stage must preserve:

    confidentiality
    integrity
    availability
    least privilege
    provenance
    accountability

That is the security standard for CrimeKit Face Trace Investigator.
