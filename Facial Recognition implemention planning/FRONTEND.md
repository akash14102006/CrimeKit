# CrimeKit Face Trace Investigator — FRONTEND SPECIFICATION

**Document:** `FRONTEND.md`  
**Subsystem:** Face Trace Investigator  
**Frontend:** Existing CrimeKit React/TypeScript application  
**Audience:** Frontend engineers, UI engineers, backend engineers, QA, accessibility, security, product  
**Status:** Authoritative frontend implementation specification

---

# 1. PURPOSE

This document defines how the Face Trace Investigator is integrated into the CrimeKit frontend.

The frontend must present a professional investigation workspace for:

- reference-face preparation
- evidence selection
- search configuration
- asynchronous processing
- live processing status
- candidate sightings
- source-frame verification
- provenance
- timeline
- graph context
- investigator review

The frontend is a presentation and interaction layer.

It is not the authoritative security, biometric, matching, or forensic-processing layer.

---

# 2. PRIMARY USER JOURNEY

The primary investigator journey is:

    Open Case
       ↓
    Open Face Trace Investigator
       ↓
    Upload Reference Image
       ↓
    Validate Reference
       ↓
    Select Authorized Evidence
       ↓
    Choose Search Scope
       ↓
    Start Face Trace
       ↓
    See Processing Immediately
       ↓
    Watch Live Findings
       ↓
    Open Candidate Sighting
       ↓
    Verify Source Frame
       ↓
    Inspect Provenance
       ↓
    Review Candidate
       ↓
    Inspect Timeline / Graph
       ↓
    Export/Report where authorized

The experience must keep the investigator oriented throughout the process.

---

# 3. FRONTEND RESPONSIBILITY

The frontend owns:

- presentation
- user interaction
- local view state
- API communication
- WebSocket subscription
- loading states
- error presentation
- evidence selection UI
- candidate visualization
- timeline visualization
- review interaction
- accessibility
- responsive behavior

The frontend must not own:

- final authorization
- similarity thresholds
- model inference
- vector search
- evidence integrity
- authoritative job state
- forensic provenance creation
- case security decisions

---

# 4. INTEGRATION WITH EXISTING CRIMEKIT FRONTEND

Before adding components, inspect the existing CrimeKit frontend.

Identify:

- app entry point
- router
- layouts
- page conventions
- feature folder conventions
- component library
- design tokens
- state management
- API client
- authentication hooks
- authorization guards
- WebSocket/event utilities
- error handling
- notification/toast system
- modal/drawer primitives
- table/list primitives
- timeline/graph components
- evidence viewer
- testing framework

Reuse existing patterns.

Do not create a second frontend architecture.

---

# 5. FEATURE BOUNDARY

Use the existing CrimeKit feature organization.

Conceptually:

    features/
        face-trace/

Possible internal structure:

    components/
    pages/
    hooks/
    api/
    state/
    types/
    utils/

The exact path must follow the current CrimeKit frontend architecture.

Do not create unnecessary folders solely to match this document.

---

# 6. PAGE MODEL

The primary feature page is conceptually:

    FaceTraceInvestigatorPage

It should orchestrate feature-level state and child components.

It should not contain all rendering or business logic in one file.

Potential major components:

    FaceTraceHeader
    ReferenceFacePanel
    EvidenceSelector
    SearchScopeSelector
    InvestigationControls
    ProcessingStatus
    LiveFindings
    VideoEvidenceViewer
    CandidateSightingCard
    CandidateDetail
    ProvenancePanel
    TimelinePanel
    ReviewPanel

Only create components that map to real responsibilities.

---

# 7. PAGE LAYOUT

Recommended desktop structure:

    ┌──────────────────────────────────────────────────────────┐
    │ Face Trace Investigator                    Case / Status │
    ├──────────────────────────────────────────────────────────┤
    │ Reference       Evidence / Video          Live Findings │
    │ Face            Workspace                  / Results     │
    │                                                          │
    ├──────────────────────────────────────────────────────────┤
    │ Timeline / Sightings / Provenance                         │
    └──────────────────────────────────────────────────────────┘

The exact grid must follow existing CrimeKit design standards.

---

# 8. INFORMATION HIERARCHY

The investigator should understand, in this order:

1. What investigation is open?
2. What reference image is being used?
3. What evidence is being searched?
4. What is the processing state?
5. What candidate sightings were found?
6. Where did each candidate come from?
7. What is the machine-generated evidence?
8. What has the investigator reviewed?

Do not lead with decorative charts.

Investigation context comes first.

---

# 9. REFERENCE FACE PANEL

The reference panel should show:

    Reference Image
    Face Detection Status
    Quality State
    Face Count
    Reference Ready State

Example:

    REFERENCE FACE

    [image]

    Face detected        ✓
    Faces                1
    Quality              Good
    Status               Ready

Possible actions:

    Replace Image
    View Source
    Remove Reference

The UI must not expose raw embedding vectors.

---

# 10. REFERENCE UPLOAD FLOW

States:

    EMPTY
       ↓
    SELECTING
       ↓
    UPLOADING
       ↓
    VALIDATING
       ↓
    READY

Failure:

    INVALID
    NO_FACE
    MULTIPLE_FACES
    LOW_QUALITY
    PROCESSING_FAILED

The UI must provide a meaningful action for each recoverable state.

---

# 11. REFERENCE IMAGE UI

The upload area should support:

- click to upload
- drag and drop where existing CrimeKit patterns permit
- supported format indication
- file-size guidance
- clear preview
- remove/replace

Do not expose technical model details before they are useful to the investigator.

---

# 12. MULTIPLE-FACE REFERENCE

If multiple faces are detected:

    Multiple faces detected.

The interface must:

- show detected face regions if applicable
- allow explicit selection if the implementation supports it
- otherwise request a new/appropriate reference

Never silently choose a detected face.

---

# 13. REFERENCE QUALITY PRESENTATION

Quality states:

    GOOD
    REVIEW
    REJECTED

Use clear labels.

Do not show a misleading numeric "identity confidence" when the backend is only reporting quality.

---

# 14. EVIDENCE SELECTOR

The evidence selector should integrate with the existing CrimeKit evidence browser.

Possible filters:

    video
    CCTV
    image
    case artifact
    date
    source

The frontend must only display evidence the backend says the user is allowed to access.

---

# 15. EVIDENCE SELECTION

Each selected evidence item may show:

    name
    type
    source
    timestamp/date
    duration where applicable
    processing availability
    selection state

Do not trust local UI state as proof that an artifact can be processed.

The backend remains authoritative.

---

# 16. SEARCH SCOPE

Provide explicit scope choices where supported:

    Selected Evidence
    Selected Videos
    Entire Case

Cross-case search must never appear as an ordinary default option.

If the backend supports privileged cross-case search, it should be visibly and explicitly governed.

---

# 17. START SEARCH CONTROL

The Start button should only become actionable when minimum prerequisites are satisfied:

    reference ready
    valid evidence selected
    authorized scope
    required configuration valid

Button state:

    disabled
    ready
    starting
    started

Do not let the frontend decide authorization.

The frontend reflects backend permission/result.

---

# 18. CONFIRMATION FOR EXPENSIVE SEARCH

For large or multi-source searches, a confirmation step may show:

    Evidence:
    3 videos

    Estimated scope:
    large

    Search:
    Face Trace

    Start Search?

Only use estimates when the backend can provide meaningful values.

Do not fabricate duration/cost estimates.

---

# 19. SEARCH JOB CREATION

The frontend calls the backend command endpoint.

Expected response:

    investigation_id
    job_id
    status

The UI must transition immediately into the processing state.

Do not block waiting for the entire search.

---

# 20. JOB STATE MODEL

Frontend state must reflect backend state.

Recommended mapping:

    CREATED
       → Created

    QUEUED
       → Queued

    PROCESSING
       → Processing

    MATCHING
       → Matching

    FINALIZING
       → Finalizing

    COMPLETED
       → Completed

    FAILED
       → Failed

    CANCELLED
       → Cancelled

The exact labels can be localized.

---

# 21. REALTIME CONNECTION

The live investigation page should subscribe to approved CrimeKit WebSocket/event infrastructure.

Conceptual:

    Page open
       ↓
    initial GET state
       ↓
    WebSocket connect
       ↓
    receive event updates
       ↓
    update UI
       ↓
    reconnect when needed

The initial API response is authoritative.

---

# 22. WEBSOCKET IS NOT SOURCE OF TRUTH

If an event is missed:

    reconnect
       ↓
    fetch authoritative state
       ↓
    continue live events

Do not reconstruct the entire investigation from the browser event history.

---

# 23. WEBSOCKET AUTHORIZATION

The frontend may request a stream.

The backend decides whether the user can subscribe.

The frontend must not assume that possessing:

    investigation_id

grants event access.

---

# 24. EVENT HANDLING

Possible events:

    face_job.created
    face_job.started
    face_job.progress
    face_track.created
    face_candidate.detected
    face_sighting.created
    face_sighting.updated
    face_job.failed
    face_job.completed
    face_job.cancelled
    face_review.updated

Use the actual backend event names when implemented.

---

# 25. EVENT DEDUPLICATION

The frontend should tolerate duplicate events.

If an event contains:

    event_id

use it where useful to prevent duplicate UI insertion.

The frontend must not treat duplicate event delivery as a backend failure.

---

# 26. EVENT ORDERING

Do not assume global ordering.

Use authoritative API state for reconciliation where needed.

Example:

    sighting.created

may arrive after another UI update.

The state layer must be resilient.

---

# 27. PROCESSING STATUS COMPONENT

Processing status should communicate:

    current state
    evidence scope
    progress where available
    current source
    elapsed/processing information where meaningful
    failures
    cancellation action

Do not display fake progress.

---

# 28. PROGRESS BAR

Only show a percentage when the backend provides a meaningful progress metric.

Otherwise show:

    Processing

with an indeterminate progress indicator.

Never use:

    0 → 100

based merely on elapsed wall-clock time.

---

# 29. PROCESSING SOURCES

For multi-video searches, show source-level state.

Example:

    CCTV-01     ✓ Completed
    CCTV-02     ● Processing
    CCTV-03     ! Failed

This makes partial results understandable.

---

# 30. PARTIAL RESULTS

The UI must distinguish:

    COMPLETED

from:

    COMPLETED WITH PARTIAL SOURCE COVERAGE

where applicable.

It should show which sources were not successfully processed.

---

# 31. NO-MATCH STATE

"No matches found" is not an error.

Display:

    Search completed
    No candidate sightings found in the processed scope.

Do not show an error-red failure state.

---

# 32. PROCESSING ERROR STATE

For errors:

    Search failed

show:

    safe user-facing message
    affected source/job
    retry action when supported
    job/reference identifier when useful

Do not display raw stack traces.

---

# 33. LIVE FINDINGS

Live findings should appear as meaningful investigative events.

Example:

    Candidate Found
    CCTV-01
    14:21:03
    Similarity: 0.91
    Quality: Good

Do not create a new card for every recognized frame.

Use backend sighting/candidate events.

---

# 34. CANDIDATE TERMINOLOGY

Preferred:

    Candidate
    Candidate Sighting
    Possible Match
    Machine-Generated Candidate

Avoid:

    Criminal Found
    Guilty
    Confirmed Criminal
    AI Proved Identity

unless an explicitly authorized legal workflow defines different terminology.

---

# 35. CANDIDATE CARD

A candidate card may contain:

    source
    timestamp
    thumbnail/frame
    similarity
    quality
    track
    candidate tier
    review status

Example:

    CANDIDATE SIGHTING

    CCTV-01
    14:21:03

    Similarity       0.91
    Quality          Good
    Track            TRACK-017

    Review            Pending

    [View Evidence]

---

# 36. SIMILARITY DISPLAY

Label the metric accurately.

Use:

    Similarity: 0.91

not:

    Confidence: 91%

unless the backend explicitly provides a calibrated confidence metric.

---

# 37. QUALITY DISPLAY

Show quality separately:

    Quality: Good

Possible states:

    Good
    Moderate
    Poor

Exact terminology follows backend policy.

---

# 38. CANDIDATE RANKING

If candidates are ranked:

    #1
    #2
    #3

the UI may display rank.

Do not imply that rank equals legal certainty.

---

# 39. LIVE FINDINGS ORDER

Default order should prioritize:

    newest sighting

or:

    most relevant candidate

according to the product requirement.

Allow the investigator to switch sorting if useful.

---

# 40. CANDIDATE DETAIL PANEL

When a candidate is selected, open a detail view.

Recommended sections:

    Candidate Summary
    Source Evidence
    Source Frame
    Match Metadata
    Track Context
    Timeline Context
    Provenance
    Review

---

# 41. SOURCE FRAME VIEWER

This is one of the most important UI surfaces.

It should show:

    original frame
       +
    non-destructive bounding box
       +
    timestamp
       +
    source identifier

Do not modify the original evidence.

The displayed overlay is a presentation/derived view.

---

# 42. FRAME CONTEXT

The investigator should be able to see enough context around the face.

Where supported:

    previous frame
    current frame
    next frame

or:

    nearby timeline context

Do not fetch excessive video data unnecessarily.

---

# 43. VIDEO VIEWER

Where appropriate, allow:

    play
    pause
    seek
    timestamp
    source name

The video viewer must enforce backend access controls.

Do not assume the user can play the full source simply because a candidate exists.

---

# 44. SOURCE EVIDENCE NAVIGATION

Candidate:

    ↓

Sighting:

    ↓

Source Frame:

    ↓

Original Evidence

This navigation path should be explicit and fast.

---

# 45. PROVENANCE PANEL

Display:

    Evidence
    Artifact
    Video
    Frame
    Timestamp
    Processing Run
    Model
    Model Version
    Matching Policy
    Review State

The panel should make the machine-generated origin visible.

---

# 46. PROVENANCE LANGUAGE

Use wording such as:

    Source Evidence
    Processing Run
    Machine-Generated Candidate
    Matching Policy
    Investigator Review

Avoid misleading terms such as:

    Proof
    Guaranteed Identity

---

# 47. MODEL INFORMATION

An authorized user may see:

    Provider: InsightFace
    Model: <approved model>
    Version: <version>

Whether this is shown by default depends on the CrimeKit information hierarchy.

The underlying API must preserve the metadata even if the UI hides advanced details.

---

# 48. MATCHING POLICY INFORMATION

Advanced users may inspect:

    Matching Policy
    Version

Do not expose secret/internal configuration values.

---

# 49. TIMELINE VIEW

Face sightings should integrate with the existing CrimeKit timeline.

Example:

    14:21:03  ● Candidate sighting
    14:25:11  ● Track ended
    15:03:42  ● Candidate sighting

Selecting an event should open its evidence context.

---

# 50. TIMELINE SEMANTICS

A timeline event should use the source-event timestamp.

Processing wall-clock time may be shown separately if operationally useful.

Do not silently replace event time with processing time.

---

# 51. TRACK VISUALIZATION

The UI may show:

    TRACK-017
    14:21:01 → 14:21:05

Track state is temporal visual association.

Do not label a track:

    confirmed identity

unless an explicit reviewed relationship exists.

---

# 52. MAP / LOCATION CONTEXT

If CrimeKit already has location visualization and the sighting has authorized location data, show:

    sighting
       ↓
    location

The location must come from actual evidence/metadata.

Do not infer a precise location merely from a camera name.

---

# 53. GRAPH INTEGRATION

Where CrimeKit's graph UI exists, a face sighting can become an entry point.

Example:

    Face Sighting
        ↓
    Evidence
        ↓
    Camera
        ↓
    Location
        ↓
    Timeline

Do not render a graph relationship as stronger than its underlying evidence.

---

# 54. REVIEW PANEL

The review panel should clearly distinguish:

    Machine Result

from:

    Investigator Decision

Example:

    Machine-Generated Candidate
    Similarity: 0.91
    Quality: Good

    Investigator Review

    [ Needs Further Review ]
    [ Reject Candidate ]
    [ Confirm Candidate ]

Exact options must match backend domain semantics.

---

# 55. REVIEW UX

Review actions should:

1. Show what is being reviewed.
2. Require the authorized action.
3. Optionally require a reason where policy requires.
4. Submit to backend.
5. Show resulting state.
6. Preserve review history in the UI where available.

---

# 56. REVIEW CONFIRMATION

For consequential actions, consider confirmation:

    Are you sure you want to mark this candidate as
    Confirmed Candidate?

The wording must reflect actual domain semantics.

Do not use "Confirm identity" unless the backend/legal workflow explicitly supports that concept.

---

# 57. REVIEW AUDIT

After review, display:

    Reviewed by
    Reviewed at
    Decision
    Reason

only according to the authorized data contract.

---

# 58. ACCESS DENIED STATES

If the backend returns authorization failure:

    Access restricted

Do not leak whether another restricted artifact exists beyond what the endpoint contract permits.

---

# 59. CASE CHANGE

If the user changes case while the Face Trace page is open:

- invalidate case-scoped data
- disconnect/re-scope realtime subscriptions
- refresh authorized evidence
- never display stale data from the previous case

---

# 60. INVESTIGATION CHANGE

If the user navigates between investigations:

    unsubscribe old
    subscribe new

Do not let events from the old investigation update the new page.

---

# 61. TAB / WINDOW BEHAVIOR

If multiple tabs are open:

    Tab A → Investigation A
    Tab B → Investigation B

each tab must maintain the correct case/investigation event context.

---

# 62. DATA REFRESH

Use automatic refresh only where it adds value.

Realtime events should reduce unnecessary polling.

Polling may be used as a fallback or reconciliation mechanism.

---

# 63. REFRESH AFTER RECONNECT

On reconnect:

    GET current investigation
       ↓
    reconcile state
       ↓
    continue realtime stream

This prevents stale UI state.

---

# 64. API CLIENT

Use the existing CrimeKit API client.

Do not create ad-hoc:

    fetch()
    axios()
    websocket()

implementations throughout individual components if a shared infrastructure already exists.

---

# 65. API TYPES

Use shared TypeScript types where available.

Important types may include:

    FaceInvestigation
    FaceReference
    FaceSearchJob
    FaceCandidate
    FaceSighting
    FaceReview
    FaceProcessingEvent

The exact names must follow the codebase.

---

# 66. TYPE SAFETY

Do not use:

    any

for the core face-investigation data model merely to move faster.

Use explicit types.

Unknown backend fields should be handled deliberately.

---

# 67. ASYNC REQUEST HANDLING

For each API command:

    idle
    submitting
    success
    failure

Prevent duplicate user actions where necessary.

Example:

    Start Search

should not submit five identical jobs because the user clicked five times.

---

# 68. ABORT / CANCELLATION

Where supported, the frontend may issue cancellation.

The backend remains authoritative.

After cancellation:

    refresh state
    stop showing active controls
    preserve completed observations

---

# 69. CLIENT-SIDE CACHE

Follow existing CrimeKit data-fetching/cache architecture.

Cache keys must include sufficient case/investigation scope.

Do not reuse:

    face-sightings

across multiple cases without scoped keys.

---

# 70. STALE DATA

A candidate should show stale/loading state while refreshing if appropriate.

Do not continue showing a previous case's candidate as though it belongs to the current case.

---

# 71. ERROR PRESENTATION

Error messages should be:

- clear
- safe
- actionable
- non-technical where possible

Example:

    "This video could not be processed. Open the processing details
     to review the failure."

rather than:

    "CUDAExecutionProvider initialization failed at node 142."

---

# 72. TECHNICAL DETAILS

Advanced details may be available in:

    Processing Details
    Diagnostics

Only authorized users should see sensitive diagnostics.

---

# 73. LOADING SKELETONS

Use existing CrimeKit skeleton/loading components where available.

The UI must indicate what is loading.

Do not freeze the entire application because one panel is waiting.

---

# 74. EMPTY STATE

Initial state should communicate:

    Upload a reference face
    Select evidence
    Start an investigation

Avoid giant decorative illustrations that hide the primary workflow.

---

# 75. NO MATCH EMPTY STATE

After a successful search with no candidates:

    No candidate sightings found.

Also show:

    processed scope
    source status

where available.

---

# 76. FAILURE EMPTY STATE

A failed job is not an empty state.

Show:

    Failed
    affected source
    safe error
    retry where available

---

# 77. PARTIAL STATE

For partially successful searches:

    2 sources completed
    1 source failed
    1 source still processing

This should be visible without opening several dialogs.

---

# 78. RESPONSIVE DESIGN

Desktop is primary for forensic investigation.

Tablet should remain usable.

Mobile support should prioritize:

- candidate review
- status
- source frame
- timeline

but does not need to reproduce the full desktop workspace if CrimeKit's product scope is desktop-first.

---

# 79. KEYBOARD ACCESS

All major controls must be keyboard accessible:

- upload
- evidence selection
- start/cancel
- candidate navigation
- source frame
- review controls

---

# 80. FOCUS MANAGEMENT

When opening:

    modal
    drawer
    candidate detail

move focus appropriately.

Restore focus after closing.

Follow existing CrimeKit accessibility primitives.

---

# 81. SCREEN READER SEMANTICS

Live processing updates should use accessible status semantics where appropriate.

Do not announce every low-level processing event.

Announce meaningful changes such as:

    Search started
    Candidate found
    Search completed
    Search failed

---

# 82. COLOR ACCESSIBILITY

Do not communicate meaning by color alone.

For example:

    green = completed

should also have:

    Completed ✓

Likewise:

    Failed !

---

# 83. MOTION

Avoid excessive animation.

Use animation for:

- state transition
- live update
- progress

not for decoration.

Respect reduced-motion preferences where existing CrimeKit standards support it.

---

# 84. VISUAL LANGUAGE

The feature should feel like:

    professional investigation software

not:

    social media
    consumer camera app
    gaming HUD

Prefer clarity, hierarchy, evidence visibility, restrained motion, and information density appropriate for forensic work.

---

# 85. UI TERMINOLOGY

Recommended:

    Face Trace Investigator
    Reference Face
    Evidence
    Processing
    Candidate
    Candidate Sighting
    Source Frame
    Provenance
    Similarity
    Quality
    Track
    Investigator Review

Avoid ambiguous marketing language.

---

# 86. COLOR SEMANTICS

Follow existing CrimeKit design tokens.

Conceptual status:

    neutral → informational
    blue → active/processing
    green → completed/success
    amber → review/warning
    red → failure/restriction

Do not introduce a new color system for this feature.

---

# 87. GLASS / VISUAL EFFECTS

Use the existing CrimeKit design system.

Do not make the whole investigation screen glassmorphic.

Glass or elevated surfaces may be used selectively for:

- panels
- overlays
- detail drawers

Readability and evidence visibility take priority.

---

# 88. VIDEO FRAME OVERLAY

Bounding boxes should be:

- clearly visible
- non-destructive
- accessible
- visually distinct from video content

Do not make overlays so bright or thick that they obscure the face.

---

# 89. CANDIDATE TIER PRESENTATION

If candidate tiers exist:

    High Candidate
    Medium Candidate
    Low Candidate

must not visually imply legal certainty.

Use neutral labels and supporting context.

---

# 90. SOURCE FRAME THUMBNAILS

Thumbnails should be generated according to backend/storage policy.

Do not ask the browser to download full source videos just to create thumbnail cards.

---

# 91. PERFORMANCE

The frontend should remain responsive while processing large searches.

Do not render:

    every frame observation

as a React list.

Render:

    sightings
    selected candidate
    relevant timeline points

and fetch detailed observations on demand.

---

# 92. VIRTUALIZATION

If candidate/sighting lists can become large, use the existing virtualized list/table mechanism.

Do not add a new virtualization library if the platform already has one.

---

# 93. LIVE UPDATE PERFORMANCE

Batch/coalesce rapid progress updates where appropriate.

Do not trigger a full page re-render for every minor processing event.

---

# 94. STATE MANAGEMENT

Use existing CrimeKit state management.

The feature should have clear separation between:

    server state
    realtime events
    transient UI state

Do not put all data into one giant global store.

---

# 95. SERVER STATE

Server state includes:

    investigation
    job
    sightings
    candidates
    reviews

Use the existing API data-fetching approach.

---

# 96. TRANSIENT UI STATE

Examples:

    open panel
    selected candidate
    selected tab
    playback position
    upload dialog open

Keep these local unless shared behavior requires global state.

---

# 97. REALTIME STATE

Realtime events should update server-state representations using the existing state architecture.

Do not make WebSocket data a completely separate unofficial copy of the backend state.

---

# 98. STATE RECONCILIATION

After:

    reconnect
    refresh
    route change

the frontend should reconcile against authoritative API data.

---

# 99. SECURITY

Frontend security responsibilities include:

- not exposing secrets
- not storing raw embeddings unnecessarily
- not bypassing backend authorization
- respecting protected routes
- limiting sensitive data in local state

The backend remains authoritative.

---

# 100. LOCAL STORAGE

Do not store raw face embeddings, sensitive source images, or protected candidate data in localStorage by default.

Only store non-sensitive UI preferences where appropriate.

---

# 101. BROWSER CACHE

Do not intentionally persist sensitive face data in long-lived browser storage unless required and governed.

Use controlled HTTP caching semantics.

---

# 102. ERROR RECOVERY

The UI should provide:

    retry
    refresh
    reconnect
    return to case

where meaningful.

Do not automatically retry unsafe commands indefinitely.

---

# 103. COMMAND DUPLICATION

Protect against duplicate:

    Start Search
    Cancel
    Review

commands caused by double clicks or network retries.

Use backend idempotency where applicable.

---

# 104. REVIEW COMMAND SAFETY

After a review action:

    disable duplicate submission
    wait for authoritative response
    update state from server

Do not optimistically display a permanent review state if the backend rejected the action.

---

# 105. SEARCH COMMAND SAFETY

After Start Search:

    disable or transition button
    show job status

If request times out:

    query authoritative investigation state

Do not blindly create another job.

---

# 106. SOURCE FRAME SECURITY

The frontend must obtain source frames through the existing authorized artifact-access mechanism.

Do not construct storage URLs manually.

---

# 107. MEDIA FETCHING

Fetch only the media required for the selected view.

Do not prefetch entire case video archives.

---

# 108. VIDEO SEEKING

Where direct video access is supported, seeking should use the backend/media infrastructure rather than loading the whole file.

---

# 109. CANDIDATE DETAIL DEEP LINK

Where CrimeKit routing supports deep links, candidate detail may be addressable through:

    investigation
    +
    sighting/candidate

The route must remain authorization-protected.

---

# 110. BROWSER REFRESH

After refresh:

    restore investigation
    fetch authoritative state
    restore selected candidate if route allows
    reconnect realtime

Do not lose the ability to inspect a running search.

---

# 111. NETWORK LOSS

If the network is lost:

    show connection degraded
    keep local UI context
    reconnect
    reconcile state

Do not claim the search stopped unless the backend says so.

---

# 112. SESSION EXPIRY

If authentication expires:

    stop protected data access
    follow existing CrimeKit re-authentication flow

Do not keep trying protected API requests indefinitely.

---

# 113. CASE ACCESS REVOCATION

If authorization is revoked:

    hide protected content
    stop/re-scope realtime
    display access restriction

Do not retain visible sensitive data longer than necessary.

---

# 114. BROWSER SECURITY

Follow the existing CrimeKit:

- CSP
- secure headers
- trusted origins
- cookie/token handling
- dependency policies

Do not create custom security behavior unless required.

---

# 115. API RESPONSE MINIMIZATION

The frontend should request only the data required for each screen.

Do not request raw biometric vectors.

Do not request all frame observations for the whole investigation.

---

# 116. PERFORMANCE BUDGET

Set project-specific budgets after measuring.

Useful indicators:

    initial page load
    investigation state load
    candidate list render
    WebSocket update latency
    source-frame load latency

Do not invent numeric guarantees without measurement.

---

# 117. FRONTEND TEST STRUCTURE

Test:

    components
    hooks
    reducers/state
    API client
    event handling
    routing
    authorization states
    accessibility

Then run feature-level integration tests.

---

# 118. COMPONENT TESTS

Test:

- reference upload states
- evidence selection
- start button states
- processing states
- candidate card
- candidate detail
- provenance
- review controls

---

# 119. REALTIME TESTS

Test:

    event received
       ↓
    UI updated

and:

    duplicate event
       ↓
    no duplicate UI item

and:

    disconnect
       ↓
    reconnect
       ↓
    authoritative refresh

---

# 120. ROUTING TESTS

Verify:

- unauthorized route access
- missing investigation
- wrong case/investigation context
- deep-linked candidate
- refresh on running investigation

---

# 121. REVIEW TESTS

Verify:

    review available
    ↓
    authorized submit
    ↓
    successful state update

and:

    backend rejects
    ↓
    UI does not claim review succeeded

---

# 122. ERROR TESTS

Test:

- upload failure
- reference validation failure
- search creation failure
- WebSocket failure
- source frame failure
- review failure
- authorization failure

---

# 123. ACCESSIBILITY TESTING

Verify:

- keyboard navigation
- focus
- labels
- screen-reader status
- color-independent meaning
- modal/drawer accessibility

Use existing CrimeKit accessibility tooling.

---

# 124. RESPONSIVE TESTING

Verify:

    desktop
    tablet

and mobile critical flows where required.

---

# 125. SECURITY TESTING

Verify the browser never receives:

- raw embeddings unnecessarily
- internal secrets
- unrestricted storage credentials
- hidden case data

---

# 126. FRONTEND API CONTRACT TEST

The frontend must use the real backend response shapes.

Do not hard-code mock response assumptions in production code.

---

# 127. MOCK DATA POLICY

Mocks may be used for:

    component unit tests
    local UI development

They must not be presented as real forensic results.

Demo environment should use clearly designated test data.

---

# 128. TEST FIXTURE POLICY

Use:

- synthetic images
- public test images
- synthetic/authorized videos

Do not add real case evidence to the repository.

---

# 129. UI TELEMETRY

Frontend telemetry may record:

    page load
    API latency
    connection status
    feature errors

Do not send:

    face embeddings
    raw face images
    sensitive source frames

to generic analytics systems.

---

# 130. UI LOGGING

Production browser logs must not include:

- embeddings
- source image data
- sensitive evidence URLs
- tokens

Prefer concise diagnostic identifiers.

---

# 131. FEATURE FLAG

If CrimeKit has an existing feature-flag mechanism, Face Trace Investigator may be gated during rollout.

Do not create a new feature-flag system.

---

# 132. PERMISSION UI

Where the backend returns feature permission information, the UI may hide/disable controls.

However:

    UI permission
       ≠
    security enforcement

Backend remains authoritative.

---

# 133. ACCESSIBILITY OF LIVE FINDINGS

When a new candidate is found, announce a concise status update where appropriate:

    "New candidate sighting found."

Do not announce every low-level frame event.

---

# 134. LOADING AND LIVE COMPOSITION

A live processing page should not constantly shift layout.

Reserve space for:

    status
    findings
    timeline

to reduce visual instability.

---

# 135. INVESTIGATOR FOCUS

When a candidate arrives:

Do not automatically steal keyboard focus from the investigator.

Use a subtle notification/live-region and let the investigator choose to inspect.

---

# 136. REVIEW SAFETY

Do not make the most consequential action visually dominant simply for conversion.

Review decisions must be deliberate.

---

# 137. SOURCE-FIRST INVESTIGATION UX

Candidate cards should make:

    "View Evidence"

easy.

Do not make:

    "Confirm"

the easiest/most visually dominant action.

---

# 138. SEARCH SUMMARY

At the top of completed investigation show:

    Reference
    Sources searched
    Processing status
    Sightings found
    Review status

This gives investigators immediate orientation.

---

# 139. INVESTIGATION SUMMARY EXAMPLE

    FACE TRACE COMPLETE

    Reference:
    [thumbnail]

    Evidence searched:
    3 videos

    Candidate sightings:
    7

    Reviewed:
    2
    Pending:
    5

Do not imply that "7 sightings" means "7 separate people."

---

# 140. TRACK/ SIGHTING DISTINCTION

The UI should distinguish:

    Detection
    Track
    Sighting

Do not use these terms interchangeably.

---

# 141. MULTI-SOURCE RESULTS

Show source labels clearly:

    CCTV-01
    CCTV-02
    Body Camera
    Phone Video

The source should be visible alongside timestamp.

---

# 142. TEMPORAL CONTEXT

For a candidate:

    14:21:03

show enough context to know:

    what happened
    where it came from
    which source

---

# 143. CANDIDATE DETAIL NAVIGATION

Candidate detail may provide tabs:

    Overview
    Evidence
    Timeline
    Provenance
    Review

Use existing CrimeKit tabs/segmented-control patterns.

---

# 144. ADVANCED DIAGNOSTICS

Technical diagnostics should be behind an advanced/authorized view.

Possible:

    model version
    runtime
    processing run
    execution provider
    policy version

Do not expose infrastructure secrets.

---

# 145. MODEL VERSION DISPLAY

For expert users:

    Model:
    InsightFace / approved model

    Version:
    X

This supports forensic transparency.

---

# 146. PROCESSING RUN DISPLAY

Show:

    Processing Run:
    RUN-00391

when useful for audit/investigation operations.

---

# 147. PROVENANCE COPY

Preferred:

    "Generated from CCTV-01, frame 9921, at 14:21:03."

This is much more useful than:

    "AI detected a match."

---

# 148. SOURCE FRAME ACTIONS

Possible:

    Open Source
    View Nearby Frames
    View Video
    View Evidence Details

Actual capabilities follow backend support.

---

# 149. DOWNLOAD / EXPORT

Only expose download/export actions when authorized.

Use the existing CrimeKit export system.

Do not create direct browser downloads from storage without authorization.

---

# 150. REPORT INTEGRATION

Where CrimeKit supports reporting:

    candidate/sighting
       ↓
    Add to report

The report should preserve machine-vs-investigator semantics.

---

# 151. GRAPH NAVIGATION

If selecting a candidate highlights a graph node/edge, the UI should preserve source context.

Do not make the graph a dead-end visualization.

---

# 152. TIMELINE NAVIGATION

Selecting a timeline sighting should open:

    candidate
    source frame
    provenance

where supported.

---

# 153. DEEP-LINK STATE

A deep link should be sufficient to restore:

    case
    investigation
    candidate/sighting

provided the user is authorized.

---

# 154. UI ERROR BOUNDARIES

A failed panel should not necessarily break the entire investigation workspace.

Example:

    Neo4j graph unavailable

may leave:

    source evidence
    timeline
    candidates

usable.

---

# 155. GRAPH DEGRADED STATE

If graph projection is pending/unavailable:

    Graph temporarily unavailable

Do not show:

    No graph data

if the actual state is dependency failure.

---

# 156. REAL-TIME DEGRADED STATE

If WebSocket is unavailable but API works:

    Live updates temporarily unavailable
    Refreshing state automatically

The underlying job may continue.

---

# 157. SOURCE MEDIA DEGRADED STATE

If source frame cannot be loaded:

    Candidate metadata remains visible
    Source unavailable message
    Retry

Do not delete candidate state because one display artifact failed.

---

# 158. FRONTEND ARCHITECTURE PRINCIPLE

The page is a view over authoritative backend state.

It should not become a second forensic engine.

---

# 159. NO CLIENT-SIDE MATCHING

Never implement:

    fetch embeddings
       ↓
    compare in browser

Raw biometric vectors should not be sent to the browser.

Matching belongs to the controlled backend/inference environment.

---

# 160. NO CLIENT-SIDE AUTHORIZATION

Never implement:

    if user.role === "admin"
        show source

as the security boundary.

The backend must enforce authorization.

---

# 161. NO CLIENT-SIDE PROVENANCE GENERATION

The frontend may display provenance.

It must not fabricate provenance fields.

---

# 162. NO CLIENT-SIDE THRESHOLDING

Do not implement:

    similarity >= threshold

as the authoritative candidate decision in React.

The backend provides candidate semantics.

---

# 163. FRONTEND DATA MINIMIZATION

For list views, retrieve summarized candidate data.

For detail views, retrieve richer provenance data.

Avoid unnecessary sensitive data transfer.

---

# 164. UI STATE MACHINE

Conceptual page state:

    EMPTY
       ↓
    REFERENCE_READY
       ↓
    EVIDENCE_READY
       ↓
    STARTING
       ↓
    PROCESSING
       ↓
    FINDINGS
       ↓
    COMPLETED

Error states:

    REFERENCE_ERROR
    SEARCH_ERROR
    CONNECTION_ERROR

The exact implementation should follow the existing frontend state architecture.

---

# 165. COMPLETION STATE

Completed state should summarize:

    sources processed
    sightings
    no-match/partial state
    review state

Do not force the investigator to navigate through every detail just to understand whether the job finished.

---

# 166. CANCELLATION STATE

After cancellation:

    show cancelled
    show processed portion
    show remaining scope where available

Do not imply full search completion.

---

# 167. REVIEW STATUS BADGES

Use statuses such as:

    Pending Review
    Reviewed
    Needs Further Review
    Rejected

Exact names must match backend semantics.

---

# 168. STATUS COLOR RULE

Status color must follow existing CrimeKit design tokens.

Do not introduce one-off colors.

---

# 169. COMPONENT COMPOSITION

Prefer:

    Page
      ↓
    Feature container
      ↓
    focused components

Avoid:

    2,000-line page component

---

# 170. HOOKS / CONTROLLERS

Feature hooks may manage:

    reference upload
    investigation state
    sightings
    realtime subscription
    review

Avoid putting all backend behavior into one giant hook.

---

# 171. API HOOKS

Use existing shared API/data hooks.

Do not directly use low-level HTTP code inside every component.

---

# 172. WEBSOCKET HOOK

If the project already has a shared WebSocket hook, reuse it.

Otherwise implement the smallest reusable abstraction required for the feature.

Do not create a generalized event framework for one feature.

---

# 173. NOTIFICATIONS

Use existing CrimeKit notification/toast system.

Meaningful notifications:

    Search started
    Candidate found
    Search completed
    Search failed

Do not toast every frame/sighting update.

---

# 174. URL STATE

Use URL state only for useful navigational context:

    selected candidate
    tab
    investigation

Do not put sensitive embeddings or source data into URLs.

---

# 175. BROWSER HISTORY

Opening candidate detail may use normal navigation/history where consistent with CrimeKit.

Back navigation should return the investigator to the same investigation context.

---

# 176. UNSAVED STATE

Before leaving a reference/search configuration with unsaved or unsubmitted choices, follow the existing CrimeKit navigation policy.

Do not create custom browser prompts unnecessarily.

---

# 177. LARGE SCREEN OPTIMIZATION

For desktop forensic investigation, use available screen space for:

    source video
    findings
    timeline

but maintain clear visual hierarchy.

---

# 178. DENSITY

Use information-dense tables/cards where appropriate.

Avoid excessive spacing that forces investigators to scroll through operationally related data.

---

# 179. DECORATION

Do not add decorative face silhouettes, AI particles, neon effects, or animated scanning effects unless they genuinely communicate system state.

CrimeKit should look operational, not fictional.

---

# 180. PERFORMANCE OF VIDEO UI

Avoid rendering high-resolution video as a React image on every frame.

Use proper media elements/streaming mechanisms.

---

# 181. FRAME OVERLAY PERFORMANCE

For interactive overlays:

- avoid unnecessary full React rerenders
- use efficient rendering
- throttle pointer/seek updates
- preserve stable video playback

Use canvas/overlay techniques only where the existing architecture justifies them.

---

# 182. TIMELINE PERFORMANCE

If many observations exist, render:

    sightings

rather than:

    every frame observation

Use on-demand detail.

---

# 183. GRAPH PERFORMANCE

Do not load the entire case graph because the user opened one face candidate.

Use focused graph context where possible.

---

# 184. DATA PREFETCHING

Prefetch only high-value next actions.

For example:

    candidate selected
       ↓
    source metadata

rather than:

    entire source video

---

# 185. MOBILE / SMALL VIEW

On narrow layouts prioritize:

    candidate
    source frame
    provenance
    review

Move less important context into drawers/tabs.

---

# 186. VISUAL REGRESSION

Add visual regression tests where CrimeKit already uses them.

Key screens:

    empty
    reference ready
    processing
    candidate
    source verification
    completed
    failed

---

# 187. FRONTEND CI

The feature must pass existing:

    lint
    typecheck
    tests
    build

Do not bypass CI.

---

# 188. FRONTEND DEPENDENCY RULE

Before adding UI packages:

    inspect existing dependencies

Reuse:

    existing modal
    existing table
    existing tabs
    existing icons
    existing graph/timeline components

where applicable.

---

# 189. ICON POLICY

Use the existing CrimeKit icon library.

Do not introduce arbitrary icon packs.

Avoid emoji as production UI icons.

---

# 190. DESIGN TOKEN POLICY

Use existing:

    colors
    typography
    spacing
    radius
    shadow
    motion

Do not create a separate Face Trace design system.

---

# 191. DARK/LIGHT MODE

Follow the existing CrimeKit appearance mode.

The feature must remain usable in every supported theme.

---

# 192. HIGH-CONTRAST EVIDENCE VIEW

Source-frame visualization must remain readable in the selected theme.

Do not use transparent overlays that disappear against dark footage.

---

# 193. TOOLTIP POLICY

Use tooltips for advanced terms only when necessary.

Examples:

    Similarity
    Processing Run
    Execution Provider

The primary UI should remain understandable without technical expertise.

---

# 194. INVESTIGATOR EDUCATION

Where useful, a small contextual explanation may clarify:

    "Similarity is a machine-generated comparison signal. Review the source evidence before making an investigative decision."

Do not overwhelm the workflow with warnings.

---

# 195. INLINE DISCLAIMER

Where required by product/legal policy, present a concise distinction:

    "Results are candidate matches generated from the selected evidence
     and require investigator review."

Exact legal text follows the project's approved wording.

---

# 196. NO DARK PATTERNS

Do not:

- default to the most consequential review action
- hide uncertainty
- hide source evidence
- hide failed processing
- auto-confirm candidates
- make irreversible actions one click without appropriate confirmation

---

# 197. FRONTEND ACCEPTANCE CRITERIA

The frontend is acceptable when:

[ ] Authorized investigator can open Face Trace Investigator.

[ ] Reference upload works.

[ ] Reference validation states are visible.

[ ] Multiple reference faces are handled explicitly.

[ ] Evidence selection integrates with existing CrimeKit evidence.

[ ] Search scope is explicit.

[ ] Start creates an asynchronous job.

[ ] Processing appears immediately.

[ ] Live events update the UI.

[ ] WebSocket reconnect works.

[ ] Candidate sightings appear without frame-level spam.

[ ] Similarity is labeled correctly.

[ ] Quality is displayed separately.

[ ] Source frame can be opened.

[ ] Provenance is visible.

[ ] Timeline integration works where backend support exists.

[ ] Review is explicit.

[ ] Review failure is handled correctly.

[ ] No raw embeddings are unnecessarily sent to the browser.

[ ] Unauthorized data is not exposed.

[ ] No-match is distinguishable from failure.

[ ] Partial processing is visible.

[ ] Accessibility requirements are met.

[ ] Existing CrimeKit design system is reused.

[ ] Existing API/state infrastructure is reused.

[ ] Frontend build/tests/lint pass.

---

# 198. FRONTEND IMPLEMENTATION ORDER

Implement in this order:

    1. Discover existing CrimeKit frontend architecture
    2. Create/locate Face Trace feature boundary
    3. Define TypeScript domain/API types
    4. Integrate reference upload
    5. Integrate evidence selector
    6. Integrate search creation
    7. Implement job-state UI
    8. Implement realtime events
    9. Implement candidate list
    10. Implement source-frame verification
    11. Implement provenance
    12. Implement review
    13. Integrate timeline
    14. Integrate graph where supported
    15. Optimize rendering
    16. Accessibility hardening
    17. Error/reconnect hardening
    18. Visual regression/integration testing

Do not begin with visual polish before the domain flow works.

---

# 199. FRONTEND REVIEW QUESTIONS

Before merge:

## User Journey

Can an investigator start a search without confusion?

## Processing

Can the investigator understand what is happening?

## Realtime

Do findings appear without page refresh?

## Source

Can the investigator reach the exact source frame?

## Provenance

Can the investigator understand where the candidate originated?

## Review

Can a human explicitly review the candidate?

## Security

Can the browser see data it should not see?

## Accessibility

Can the workflow be operated without a mouse?

## Performance

Does the UI remain responsive with many sightings?

---

# 200. FINAL FRONTEND CONTRACT

The Face Trace Investigator frontend must implement this experience:

    CASE
      ↓
    FACE TRACE INVESTIGATOR
      ↓
    REFERENCE FACE
      ↓
    AUTHORIZED EVIDENCE
      ↓
    START SEARCH
      ↓
    PROCESSING
      ↓
    LIVE FINDINGS
      ↓
    CANDIDATE SIGHTING
      ↓
    SOURCE FRAME
      ↓
    PROVENANCE
      ↓
    TIMELINE / GRAPH CONTEXT
      ↓
    INVESTIGATOR REVIEW

The frontend must make the investigation understandable without
pretending that the browser is the forensic engine.

The UI must consistently separate:

    SOURCE EVIDENCE
    MACHINE-GENERATED CANDIDATE
    INVESTIGATOR REVIEW

The frontend quality bar is:

    clear
    fast
    accessible
    evidence-centered
    secure
    resilient
    professionally designed
    consistent with CrimeKit

not:

    flashy
    overloaded
    AI-theatrical
    technically misleading
