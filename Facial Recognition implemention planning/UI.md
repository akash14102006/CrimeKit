# CrimeKit Face Trace Investigator — UI / UX SPECIFICATION

**Document:** `UI.md`  
**Subsystem:** Face Trace Investigator  
**Product surface:** CrimeKit Investigation Workspace  
**Primary interaction:** Reference Face → Evidence Search → Live Analysis → Candidate Sighting → Source Verification → Investigator Review  
**Audience:** Product designers, UI/UX engineers, frontend engineers, accessibility, QA, security reviewers  
**Status:** Authoritative visual and interaction specification

---

# 1. PURPOSE

This document defines the user interface and user experience for CrimeKit's Face Trace Investigator.

The objective is to make a technically complex forensic workflow understandable to an authorized investigator without hiding uncertainty, provenance, processing state, or review requirements.

The interface must communicate:

    SOURCE EVIDENCE
          ↓
    MACHINE PROCESSING
          ↓
    CANDIDATE SIGHTING
          ↓
    SOURCE VERIFICATION
          ↓
    INVESTIGATOR REVIEW

The UI must never turn a machine-generated similarity result into an apparently certain conclusion.

---

# 2. PRODUCT EXPERIENCE PRINCIPLE

CrimeKit should feel like professional investigative software.

The design should communicate:

- evidence
- control
- precision
- traceability
- confidence boundaries
- operational status
- human oversight

It should not feel like:

- a consumer camera app
- a social-media face search
- a gaming HUD
- an AI marketing dashboard
- a fictional surveillance interface

Visual polish must support investigator comprehension.

---

# 3. CORE UX PRINCIPLE

The primary investigator question is:

> "Show me where this reference face appears in the evidence, and show me exactly why CrimeKit surfaced it."

Therefore the UI must make the following path extremely easy:

    Candidate
       ↓
    Source Frame
       ↓
    Timestamp
       ↓
    Evidence
       ↓
    Processing Context
       ↓
    Review

---

# 4. PRIMARY FEATURE NAME

Use the product-facing name:

# Face Trace Investigator

Optional supporting descriptor:

> Trace a reference face across authorized evidence.

Do not use:

    "Criminal Finder"
    "Suspect Finder"
    "AI Criminal Search"

---

# 5. PRIMARY WORKSPACE

The main workspace consists of:

    1. Investigation Header
    2. Reference Panel
    3. Evidence Selection
    4. Search Controls
    5. Processing Status
    6. Live Findings
    7. Video/Source Viewer
    8. Candidate Detail
    9. Timeline
    10. Provenance
    11. Investigator Review

These areas may be tabs, panels, split panes, or drawers depending on the existing CrimeKit design system.

---

# 6. DESKTOP INFORMATION ARCHITECTURE

Preferred conceptual layout:

┌─────────────────────────────────────────────────────────────┐
│ FACE TRACE INVESTIGATOR                    Case / Status    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  REFERENCE       EVIDENCE / VIDEO        LIVE FINDINGS      │
│  FACE             WORKSPACE              / CANDIDATES       │
│                                                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ TIMELINE / SIGHTINGS / PROVENANCE                            │
└─────────────────────────────────────────────────────────────┘

The actual grid should follow existing CrimeKit layout primitives.

---

# 7. INVESTIGATION HEADER

Header should display:

    Face Trace Investigator
    Case identifier/name
    Investigation status
    Evidence scope summary

Example:

    Face Trace Investigator
    Case #CK-2026-001

    ● Processing

Do not overcrowd the header with technical details.

Advanced processing information belongs in a details surface.

---

# 8. HEADER ACTIONS

Possible actions:

    Back to Investigation
    Processing Details
    Cancel
    More

Only expose actions supported by backend permissions/state.

---

# 9. REFERENCE FACE PANEL

Purpose:

Clearly show what the investigator is searching for.

Contents:

    Reference image
    Face detection state
    Quality state
    Reference status

Example:

    REFERENCE FACE

    ┌───────────────────┐
    │                   │
    │      IMAGE        │
    │                   │
    └───────────────────┘

    Face detected      ✓
    Faces              1
    Quality            Good
    Status             Ready

Actions:

    Replace
    View Source

---

# 10. REFERENCE IMAGE STATES

States:

    EMPTY
    UPLOADING
    VALIDATING
    READY
    INVALID
    NO_FACE
    MULTIPLE_FACES
    LOW_QUALITY
    PROCESSING_FAILED

Each state must have:

    visual state
    text explanation
    next action

---

# 11. REFERENCE EMPTY STATE

Example:

    Reference Face

    Upload a clear image containing the face you want
    CrimeKit to trace across authorized evidence.

    [ Upload Reference ]

Do not use unexplained ML jargon.

---

# 12. REFERENCE VALIDATING STATE

Display:

    Checking reference image
    Detecting face
    Assessing quality

Use an indeterminate/progress state according to backend information.

Do not display fake percentages.

---

# 13. MULTIPLE-FACE STATE

Example:

    Multiple faces detected

    CrimeKit found more than one face in this image.
    Select the intended face or upload a single-person image.

Where face-selection UI exists:

    show face boxes
    allow explicit selection

Never silently select the first detected face.

---

# 14. NO-FACE STATE

Example:

    No usable face detected

    Try a clearer image with a visible face.

Provide:

    Replace Image

---

# 15. LOW-QUALITY STATE

Example:

    Reference quality is insufficient

    The face may be too small, blurred, occluded, or otherwise
    unsuitable for reliable comparison.

Do not display:

    "AI confidence = 43%"

unless such a calibrated metric actually exists.

---

# 16. REFERENCE READY STATE

Use clear success state:

    Reference Ready ✓

Then expose the next step:

    Select evidence to search.

---

# 17. EVIDENCE SELECTION PANEL

Purpose:

Allow investigator to define search scope.

Show existing CrimeKit evidence items.

Useful fields:

    source
    evidence name
    type
    date/time
    duration
    status
    selection

---

# 18. EVIDENCE TYPES

Potential supported display categories:

    CCTV
    Video
    Body Camera
    Phone Video
    Image
    Extracted Media

Use the evidence metadata actually provided by the backend.

Do not invent source types.

---

# 19. EVIDENCE ROW

Example:

    ☑ CCTV-01.mp4
       Video
       14:00 – 16:00
       Ready

Do not expose unnecessary internal storage paths.

---

# 20. SEARCH SCOPE CONTROL

Possible options:

    Selected Evidence
    Selected Videos
    Entire Case

The available choices must reflect backend authorization and capability.

---

# 21. CROSS-CASE SEARCH UI

Cross-case searching should not appear as the normal/default search.

If the feature exists:

    Advanced Search Scope
      Restricted

and explain that it requires additional authorization.

Do not create an "entire database" checkbox for ordinary investigators.

---

# 22. START SEARCH CARD

Before search:

    Reference
    Evidence Scope
    Matching Policy/processing profile where appropriate

Then:

    [ Start Face Trace ]

The main action should be clear.

---

# 23. START BUTTON RULES

Disabled when:

    reference not ready
    no evidence selected
    required authorization unavailable
    required configuration incomplete

Enabled:

    all prerequisites satisfied

Submitting:

    Starting…

After accepted:

    Processing

Prevent accidental duplicate submissions.

---

# 24. EXPENSIVE SEARCH CONFIRMATION

For large jobs, optionally show:

    You selected:
    4 video sources

    Search will process the selected evidence asynchronously.

    [ Cancel ] [ Start Search ]

Only display an estimated processing duration when the backend provides a defensible estimate.

Do not invent:

    "2 minutes remaining"

from a generic timer.

---

# 25. PROCESSING VIEW

Once a search begins, transition to an operational view.

Show:

    job status
    selected sources
    progress
    current source
    live findings
    cancel action

---

# 26. PROCESSING STATUS HEADER

Example:

    FACE TRACE
    Processing

    2 of 4 sources processed

or:

    Processing CCTV-02

Do not falsely imply completion.

---

# 27. SOURCE PROCESSING LIST

For multi-source search:

    CCTV-01       ✓ Completed
    CCTV-02       ● Processing
    CCTV-03       Queued
    CCTV-04       ! Failed

This gives immediate operational context.

---

# 28. PROGRESS DESIGN

If the backend supplies meaningful progress:

    64%

show the percentage.

Otherwise:

    Processing…

with an indeterminate indicator.

Never generate fake progress based solely on time.

---

# 29. LIVE FINDINGS PANEL

Live findings should be event-driven.

Example:

    NEW CANDIDATE

    CCTV-02
    14:21:03

    Similarity      0.91
    Quality         Good
    Track           TRACK-017

    [ Inspect ]

A candidate should appear as a meaningful event, not as an individual-frame spam stream.

---

# 30. LIVE FINDING PRIORITY

Prioritize:

    new sighting
    important processing state
    failure
    completion

Do not visually prioritize every frame.

---

# 31. CANDIDATE CARD

Recommended structure:

┌───────────────────────────────────────┐
│ Candidate Sighting                    │
│                                       │
│ [Source Frame Thumbnail]              │
│                                       │
│ CCTV-02                    14:21:03   │
│ Similarity: 0.91                      │
│ Quality: Good                         │
│ Track: TRACK-017                      │
│                                       │
│ Review: Pending                       │
│                                       │
│ [ View Evidence ]                     │
└───────────────────────────────────────┘

---

# 32. CANDIDATE TERMINOLOGY

Preferred labels:

    Candidate
    Candidate Sighting
    Possible Match
    Machine-Generated Candidate

Avoid:

    Confirmed Criminal
    Criminal Detected
    Guilty
    Identity Proven

---

# 33. SIMILARITY PRESENTATION

Display:

    Similarity: 0.91

Do not display:

    Confidence: 91%

unless the backend actually provides a calibrated confidence probability.

---

# 34. QUALITY PRESENTATION

Display separately:

    Quality: Good

Possible states:

    Good
    Moderate
    Poor

Use actual backend semantics.

---

# 35. CANDIDATE DETAIL DRAWER

Selecting a candidate should open a focused detail view.

Suggested sections:

    Summary
    Source Evidence
    Source Frame
    Track
    Match Details
    Timeline
    Provenance
    Review

---

# 36. SOURCE FRAME VIEWER

This is a primary evidence surface.

Show:

    Source Frame
    Bounding Box
    Timestamp
    Source Identifier

The bounding box is a non-destructive visual overlay.

Never overwrite source evidence.

---

# 37. FRAME VIEWER TOOLBAR

Possible:

    Previous Observation
    Next Observation
    Open Video
    Open Evidence
    Zoom where supported

Do not implement actions that the backend cannot authorize.

---

# 38. FRAME CONTEXT

Where the backend supports it, allow:

    previous frame
    current frame
    next frame

or:

    nearby observations

This helps the investigator visually verify the candidate.

---

# 39. SOURCE VIDEO VIEWER

Where supported:

    Play
    Pause
    Seek
    Timestamp
    Source

The viewer must use authorized media access.

---

# 40. VIDEO TIMESTAMP

The investigator should see:

    14:21:03.120

where source precision supports it.

Keep processing time separate from evidence-event time.

---

# 41. TRACK INFORMATION

Example:

    Track
    TRACK-017

    First observed:
    14:21:01

    Last observed:
    14:21:05

This describes a visual track, not a confirmed real-world identity.

---

# 42. OBSERVATION SUMMARY

Show:

    Observations: 5
    Best Similarity: 0.93
    Quality: Good

Do not imply:

    5 observations = 5 independent identity confirmations

---

# 43. PROVENANCE PANEL

Recommended layout:

    SOURCE
    CCTV-02.mp4

    ARTIFACT
    VID-002

    FRAME
    9921

    TIMESTAMP
    14:21:03.120

    PROCESSING RUN
    RUN-00391

    MODEL
    InsightFace / approved model

    MODEL VERSION
    X

    MATCHING POLICY
    POLICY-X

    REVIEW
    Pending

---

# 44. PROVENANCE LANGUAGE

Preferred:

    Generated from CCTV-02, frame 9921, at 14:21:03.

Avoid:

    AI proved this person was present.

---

# 45. SOURCE CHAIN VISUALIZATION

A compact provenance chain can be displayed:

    Case
      ↓
    Investigation
      ↓
    Search Job
      ↓
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

Selecting a node opens its details.

---

# 46. PROCESSING DETAILS

Advanced users may inspect:

    model
    model version
    runtime
    execution provider
    preprocessing version
    matching policy
    processing run

Keep advanced information available without overwhelming the primary workflow.

---

# 47. MACHINE VS HUMAN DISTINCTION

The UI must visibly separate:

    MACHINE-GENERATED

from:

    INVESTIGATOR REVIEW

Example:

    MACHINE-GENERATED CANDIDATE
    Similarity: 0.91

    INVESTIGATOR REVIEW
    Pending

This is a core trust boundary.

---

# 48. REVIEW PANEL

Recommended:

    Investigator Review

    Candidate:
    CCTV-02 / 14:21:03

    Machine result:
    Similarity 0.91
    Quality Good

    Decision:

    [ Needs Further Review ]
    [ Reject Candidate ]
    [ Confirm Candidate ]

The exact action names must match backend domain semantics.

---

# 49. REVIEW SAFETY

Do not make "confirm" visually dominant merely because it is the positive action.

The investigator should first have easy access to the evidence.

Recommended order:

    Source Evidence
    ↓
    Candidate Metadata
    ↓
    Review Action

---

# 50. REVIEW CONFIRMATION

For consequential review actions, use an explicit confirmation where appropriate.

Example:

    Confirm candidate review?

    This records your investigative decision.

    [ Cancel ] [ Confirm ]

Do not use misleading legal language.

---

# 51. REVIEW RESULT

After successful review:

    Review Recorded ✓

    Reviewed by:
    Investigator Name/ID

    Reviewed at:
    timestamp

The backend remains authoritative.

---

# 52. REVIEW FAILURE

If backend rejects review:

    Review could not be recorded.

Then:

    Retry

Do not optimistically display a permanent successful review state.

---

# 53. TIMELINE DESIGN

The timeline should represent source-event time.

Example:

    14:21:03     Candidate sighting
       ●
       │
    14:25:11     Track ended
       ●
       │
    15:03:42     Candidate sighting
       ●

Selecting a timeline event opens candidate/source context.

---

# 54. TIMELINE DENSITY

Do not display every frame as a timeline event.

Default to:

    sightings
    major processing events

Frame-level details remain available inside candidate detail.

---

# 55. TIMELINE FILTERS

Useful filters:

    source
    candidate tier
    review status
    time range

Follow existing CrimeKit timeline patterns.

---

# 56. GRAPH CONTEXT

If the CrimeKit graph exists:

    Candidate Sighting
          │
          ├── Evidence
          ├── Camera
          ├── Location
          └── Timeline Event

Opening graph context should preserve the selected candidate.

---

# 57. GRAPH LANGUAGE

Graph labels should remain neutral.

Do not show:

    Criminal

because a face candidate exists.

Prefer:

    Candidate
    Sighting
    Evidence
    Track
    Location
    Device

---

# 58. LIVE GRAPH UPDATE

If backend graph projection is realtime:

    new sighting
       ↓
    event
       ↓
    graph context update

Do not rebuild the entire graph for every event.

---

# 59. SEARCH COMPLETION SCREEN

Example:

    FACE TRACE COMPLETE

    Evidence searched:
    4 sources

    Candidate sightings:
    7

    Reviewed:
    3

    Pending:
    4

    [ Review Findings ]

---

# 60. NO MATCH SCREEN

Example:

    SEARCH COMPLETE

    No candidate sightings found
    in the processed evidence scope.

    Sources processed:
    4

This is a valid successful result.

Do not show red error treatment.

---

# 61. PARTIAL COMPLETION SCREEN

Example:

    SEARCH PARTIALLY COMPLETE

    Completed:
    3 sources

    Failed:
    1 source

    Candidate sightings:
    5

    Review the failed source or retry it.

Do not label this as a fully completed search.

---

# 62. FAILURE SCREEN

Example:

    SEARCH FAILED

    CCTV-03 could not be processed.

    Reason:
    Video processing failed.

    [ Retry ]

Use safe, meaningful error text.

---

# 63. CONNECTION FAILURE

Example:

    Live updates temporarily unavailable.

    The search may still be running.

    Reconnecting…

The UI should not say:

    Search failed

unless the backend confirms job failure.

---

# 64. WEBSOCKET RECONNECT UX

After reconnect:

    Reconnecting…
       ↓
    Syncing investigation state…
       ↓
    Live

Do not flash stale candidate states.

---

# 65. CASE CONTEXT

The feature must visibly show which case it belongs to.

Example:

    Case 2026-001
    Investigation:
    Face Trace — Reference A

This prevents accidental cross-case confusion.

---

# 66. INVESTIGATION NAMING

Use investigator-friendly names.

Example:

    Face Trace — CCTV Search
    Face Trace — Reference A

Do not expose internal UUIDs as the primary title.

IDs may appear in advanced details.

---

# 67. SEARCH HISTORY

If CrimeKit supports investigation history, show:

    Search started
    Search completed
    Reference changed
    Review performed

Do not create a second unrelated activity log.

---

# 68. EMPTY SEARCH HISTORY

Example:

    No face-trace searches yet.

    Start a new search by uploading a reference face
    and selecting evidence.

---

# 69. MULTI-REFERENCE FUTURE

The UI may eventually support:

    Reference A
    Reference B
    Reference C

The initial design should not require this complexity.

Do not implement a full multi-reference workflow unless backend support exists.

---

# 70. MULTI-VIDEO EXPERIENCE

For multiple videos:

    Search scope
        ↓
    Source status
        ↓
    Combined sightings
        ↓
    Timeline

The investigator should always know which source generated the candidate.

---

# 71. SOURCE COLOR / STATUS

Use existing CrimeKit status semantics.

Do not create unique per-camera color systems that could confuse meaning.

---

# 72. VIDEO SOURCE LABEL

Every candidate should show source clearly.

Example:

    CCTV-02
    14:21:03

not merely:

    14:21:03

---

# 73. CANDIDATE GROUPING

Candidates can be grouped:

    by source
    by time
    by sighting
    by review status

Default should follow investigator workflow.

---

# 74. SORTING

Useful sorting options:

    Newest
    Oldest
    Highest Similarity
    Review Pending

The backend should provide authoritative values.

---

# 75. PAGINATION

Large candidate lists should use pagination/virtualization.

Do not render thousands of candidate observations simultaneously.

---

# 76. FRAME OBSERVATIONS

Do not display all frame-level observations in the main list.

Show:

    sighting summary

and load detailed observations on demand.

---

# 77. PROVENANCE LOAD

Do not fetch the complete provenance tree for every candidate card.

Load deeper provenance when a candidate is selected.

---

# 78. GRAPH LOAD

Do not fetch the entire case graph to display a single sighting.

Use focused context.

---

# 79. VIDEO PREFETCH

Avoid prefetching large videos for all candidates.

Fetch source media only when the investigator chooses to inspect it.

---

# 80. PERFORMANCE

The page should stay responsive during active processing.

Avoid full-page rerenders for every event.

Use focused state updates.

---

# 81. LIVE EVENT COALESCING

If progress events arrive rapidly:

    1%
    2%
    3%
    4%
    ...

the UI may coalesce them according to the existing frontend architecture.

Do not visually animate every event.

---

# 82. CANDIDATE ANIMATION

A newly created sighting may receive a restrained highlight.

Avoid:

    flashing
    neon scanning
    dramatic face animations

Operational clarity is more important.

---

# 83. MOTION

Use motion to indicate:

    state transition
    new finding
    drawer opening
    timeline navigation

Do not animate for decoration.

---

# 84. REDUCED MOTION

Respect user reduced-motion preferences where supported by the existing CrimeKit design system.

---

# 85. THEME

Follow existing CrimeKit theme tokens.

Support all existing themes.

Do not create feature-specific dark/light themes.

---

# 86. GLASSMORPHISM

Glassmorphism may be used selectively for:

    candidate detail
    provenance drawer
    processing overlay

Do not make the entire workspace transparent.

Evidence and text must remain highly readable over video content.

---

# 87. TYPOGRAPHY

Use existing CrimeKit typography tokens.

Prioritize:

    source
    timestamp
    similarity
    review state

These should scan quickly.

---

# 88. ICONOGRAPHY

Use the existing project icon library.

Icons should reinforce labels.

Do not use emoji as production UI icons.

---

# 89. BUTTON HIERARCHY

Primary:

    Start Face Trace

Secondary:

    Replace
    View Evidence
    View Details

Destructive/administrative:

    Cancel
    Delete

Review controls should follow the semantic importance of the action.

---

# 90. TOOLTIP GUIDANCE

Use tooltips for specialist terms:

    Processing Run
    Execution Provider
    Matching Policy

Do not make core workflow meaning dependent on tooltips.

---

# 91. ACCESSIBILITY

All controls must be:

- keyboard accessible
- labeled
- focusable
- screen-reader understandable where appropriate

---

# 92. FOCUS

When opening a candidate drawer/modal:

    move focus into the surface

When closing:

    return focus to the invoking control

Use existing accessible dialog primitives.

---

# 93. LIVE REGIONS

Announce meaningful events:

    Search started
    New candidate sighting found
    Search completed
    Search failed

Do not announce every frame processed.

---

# 94. COLOR INDEPENDENCE

Do not rely solely on color.

Example:

    green + "Completed ✓"

rather than:

    green only

---

# 95. CONTRAST

Status text, source labels, timestamps, and review state must remain legible against:

- dark video
- bright video
- light theme
- dark theme

---

# 96. KEYBOARD SHORTCUTS

If CrimeKit already supports keyboard shortcuts, candidate navigation and video actions may integrate with them.

Do not invent a large feature-specific shortcut system.

---

# 97. RESPONSIVE DESIGN

Desktop-first.

For narrower widths:

    collapse secondary panels
    use drawers/tabs
    preserve candidate/source/review access

Do not simply shrink the full desktop layout until it becomes unreadable.

---

# 98. MOBILE PRIORITY

If mobile access is required, prioritize:

    status
    candidate
    source frame
    provenance
    review

The full multi-pane forensic workspace may remain desktop-first.

---

# 99. ERROR COPY

Use:

    Problem
    Impact
    Action

Example:

    "This video could not be processed.
     You can retry the source or continue reviewing completed sources."

---

# 100. TECHNICAL ERROR DETAILS

Advanced users may open:

    Processing Details

to see controlled diagnostic information.

Never expose secrets.

---

# 101. SECURITY COPY

If access is denied:

    Access restricted

Do not reveal hidden case/evidence information.

---

# 102. LOADING COPY

Prefer specific:

    Validating reference…
    Preparing search…
    Processing CCTV-02…
    Building sightings…

Avoid generic:

    Loading…

when useful context is available.

---

# 103. SEARCH QUEUED COPY

Example:

    Search queued

    Your evidence will be processed asynchronously.

This sets correct expectations.

---

# 104. PROCESSING COPY

Example:

    Processing evidence

    CrimeKit is analyzing the selected video sources.

---

# 105. MATCHING COPY

Example:

    Searching detected faces

This is clearer than:

    AI thinking…

---

# 106. FINALIZING COPY

Example:

    Finalizing findings

    CrimeKit is consolidating observations and preparing the investigation results.

---

# 107. SOURCE FAILURE COPY

Example:

    CCTV-03 could not be processed.

    Completed sources remain available.

---

# 108. REVIEW PENDING

Use:

    Review Pending

not:

    Unverified Criminal

---

# 109. REVIEWED CANDIDATE

Use backend-authorized terminology such as:

    Reviewed
    Candidate Reviewed

Do not invent legal semantics.

---

# 110. DATA FRESHNESS

When results update:

    "Updated just now"

may be shown where useful.

Do not imply source-event time equals update time.

---

# 111. TIME ZONE

Display investigator-local time according to CrimeKit's existing time policy.

Allow source timestamp context where relevant.

---

# 112. PRECISION

Preserve source precision.

If source supports milliseconds:

    14:21:03.120

If not:

    14:21:03

Do not create false precision.

---

# 113. DATE FORMATTING

Follow existing CrimeKit locale/date conventions.

Do not introduce another date format.

---

# 114. CONFIRMATION DIALOGS

Use confirmation for:

    cancellation with consequences
    deleting/forgetting reference
    consequential review actions

Do not use confirmation for every minor click.

---

# 115. CANCEL CONFIRMATION

If cancellation may discard unprocessed work:

    Cancel this search?

    Completed observations will remain available.
    Remaining processing will stop.

Use actual backend semantics.

---

# 116. REFERENCE REPLACEMENT

If replacing a reference while a search is active:

    Explain impact.

Do not allow ambiguous state where the running job changes reference silently.

---

# 117. ACTIVE JOB NAVIGATION

If investigator leaves the page while job continues:

    job continues

On return:

    current authoritative state
    live status
    findings

should restore.

---

# 118. BROWSER REFRESH

After refresh:

    load investigation
    load job state
    load findings
    reconnect realtime

The investigator should not lose the search.

---

# 119. SESSION EXPIRY

If session expires:

    stop protected requests
    show existing CrimeKit auth flow

Do not show cached sensitive content as if it remains authorized.

---

# 120. CASE ACCESS REVOCATION

If case access is revoked:

    stop realtime subscription
    stop sensitive fetches
    display access restriction

---

# 121. NO LOCAL BIOMETRIC STORAGE

Do not store raw face embeddings or protected source images in:

    localStorage
    indexedDB
    URL parameters

unless specifically required and governed.

---

# 122. BROWSER CACHE

Avoid unnecessary long-lived caching of sensitive biometric resources.

Use existing application caching policy.

---

# 123. TELEMETRY

Frontend telemetry may track:

    feature load
    API latency
    connection errors

Do not transmit:

    face embeddings
    raw candidate images
    source evidence
    sensitive biometric data

to generic analytics.

---

# 124. UI LOGGING

Production browser logs must not contain:

    embeddings
    authentication tokens
    sensitive source URLs
    raw source images

---

# 125. DATA MINIMIZATION

List view:

    summary only

Detail view:

    richer provenance

Deep evidence view:

    source-specific detail

Do not download all case data at once.

---

# 126. CANDIDATE DETAIL DATA

A candidate detail response may provide:

    source
    timestamp
    similarity
    quality
    track
    provenance references
    review state

Only expose advanced fields where useful.

---

# 127. RAW EMBEDDING RULE

The frontend should never require raw face embeddings for normal operation.

Any accidental exposure is a security defect.

---

# 128. CLIENT-SIDE MATCHING RULE

The browser must never become the face matcher.

Do not implement:

    download vectors
       ↓
    browser similarity

---

# 129. CLIENT-SIDE THRESHOLD RULE

The browser must not determine candidate eligibility from a local threshold.

Backend supplies the candidate state.

---

# 130. CLIENT-SIDE AUTHORIZATION RULE

The browser may hide unavailable actions.

The browser must never be the only authorization boundary.

---

# 131. SOURCE ACCESS

Source frame/media requests must use the existing authorized backend mechanism.

Do not build direct object-storage URLs in React.

---

# 132. GRAPH AUTHORIZATION

Graph context must obey the same case/evidence authorization model.

---

# 133. TIMELINE AUTHORIZATION

Timeline records must not reveal restricted source evidence.

---

# 134. REVIEW AUTHORIZATION

Only authorized roles may receive active review controls.

The backend must enforce this.

---

# 135. EXPORT

Only show export actions when authorized.

Exports should use the existing CrimeKit reporting/export architecture.

---

# 136. UI INTEGRATION WITH REPORTING

Candidate:

    ↓
    Add to Report

where supported.

Report preview should retain machine/human distinction.

---

# 137. VISUAL STATUS MODEL

Recommended semantic states:

    Neutral
    Processing
    Attention
    Success
    Failure
    Restricted

Use existing CrimeKit tokens.

---

# 138. NO MISLEADING SUCCESS

Do not style:

    high similarity

as:

    completed identity

Similarity and process completion are different concepts.

---

# 139. NO MISLEADING FAILURE

Do not style:

    no matches

as failure.

No matches is a valid result.

---

# 140. NO MISLEADING SECURITY

Do not tell users:

    "No person exists"

when the actual response is:

    "You do not have access."

---

# 141. PROCESSING VISUALIZATION

A compact process stage can show:

    Reference ✓
      ↓
    Evidence ✓
      ↓
    Detection ●
      ↓
    Matching ○
      ↓
    Sightings ○
      ↓
    Review ○

This makes internal process transparency visible without exposing implementation secrets.

---

# 142. STAGE DETAIL

Clicking a stage may show:

    what has completed
    what is active
    any safe error information

Do not expose raw stack traces.

---

# 143. LIVE PROCESSING PANEL

Possible:

    DETECTION
    4,231 frames sampled
    382 faces detected

    TRACKING
    49 active tracks

    MATCHING
    18 candidates evaluated

Only display metrics that are real backend values.

Do not fabricate them.

---

# 144. OPERATIONAL METRICS

For authorized advanced users:

    Frames processed
    Faces detected
    Candidates generated
    Sources processed
    Processing rate

Do not expose sensitive data unnecessarily.

---

# 145. PERFORMANCE COPY

Avoid:

    "Ultra-fast AI"

Prefer actual:

    "Processing 18.4 frames/sec"

only when measured and supplied by backend.

---

# 146. MODEL DETAILS SURFACE

Advanced details may show:

    Model
    Model Version
    Runtime
    Execution Provider

This is valuable for technical audit.

---

# 147. MATCH POLICY SURFACE

Advanced details may show:

    Matching Policy
    Version

Do not expose secrets/internal configuration.

---

# 148. INVESTIGATION SUMMARY CARD

Completed investigation:

    Reference Face
    4 sources searched
    7 sightings
    3 reviewed
    4 pending

This is the investigator's high-level summary.

---

# 149. INVESTIGATION HEALTH

Where supported:

    Healthy
    Processing
    Degraded
    Failed

"Degraded" should mean an actual dependency/processing limitation.

---

# 150. GRAPH/TIMELINE CROSS-LINKING

Selecting:

    Timeline event

should optionally highlight:

    Candidate
    Evidence
    Graph context

This creates one coherent investigation experience.

---

# 151. CANDIDATE TO GRAPH

Selecting a candidate:

    Candidate
      ↓
    Open Graph

The graph opens focused context.

---

# 152. CANDIDATE TO TIMELINE

Selecting a candidate:

    Candidate
      ↓
    Highlight Timeline Event

---

# 153. TIMELINE TO SOURCE

Selecting a sighting:

    Timeline
      ↓
    Source Frame

---

# 154. SOURCE TO PROVENANCE

Selecting frame details:

    Source Frame
      ↓
    Provenance

The navigation should preserve investigator context.

---

# 155. INVESTIGATION COHERENCE

The candidate, timeline, graph, and source viewer should all refer to the same investigation context.

Do not open isolated screens that lose the current case.

---

# 156. INTERACTION LATENCY

UI interactions should feel immediate.

Long backend work must show state rather than freeze controls.

---

# 157. OPTIMISTIC UI

Use optimistic updates only for low-risk UI state.

Do not optimistically finalize:

    review
    deletion
    cancellation

unless rollback behavior is fully implemented.

---

# 158. REVIEW UPDATE

After backend success:

    update UI from response/server state

Do not rely only on local optimistic state.

---

# 159. CANCEL UPDATE

After cancel:

    fetch/receive authoritative state

Do not simply hide processing controls and assume cancellation succeeded.

---

# 160. SEARCH CREATION FAILURE

If Start Search returns error:

    remain on configuration view
    preserve valid reference/evidence selection
    explain safe failure
    allow retry

---

# 161. REFERENCE UPLOAD FAILURE

If reference upload fails:

    preserve prior reference only if still valid
    otherwise show upload failure

Do not silently replace an existing valid reference with a failed upload state.

---

# 162. EVIDENCE LOAD FAILURE

If evidence browser fails:

    show evidence unavailable
    allow retry

Do not assume no evidence exists.

---

# 163. WEBSOCKET FAILURE

If WebSocket repeatedly fails:

    degrade live updates
    use API reconciliation
    display connection state

Do not stop forensic processing.

---

# 164. GRAPH FAILURE

If graph service is unavailable:

    candidates and source evidence remain accessible where possible.

Do not turn graph failure into investigation failure.

---

# 165. SOURCE FRAME FAILURE

If source frame cannot load:

    candidate metadata remains visible
    retry action available
    source availability state clear

---

# 166. SIGHTING LIST

Recommended columns/fields:

    Source
    Timestamp
    Similarity
    Quality
    Track
    Review
    Action

Keep the list scannable.

---

# 167. TABLE VS CARDS

Use:

    table/list

for many sightings.

Use:

    card/detail

for selected candidate.

Do not use giant cards for hundreds of results.

---

# 168. SEARCH FILTER BAR

Possible:

    All
    High Candidate
    Pending Review
    Reviewed
    Rejected

plus source/time filters.

Only expose categories supported by backend semantics.

---

# 169. BULK ACTIONS

Bulk review/export should not be assumed.

If introduced, require explicit product/security design.

Do not create dangerous bulk operations merely for visual completeness.

---

# 170. SORTABLE TIMELINE

Timeline may support:

    chronological
    reverse chronological

as appropriate.

---

# 171. CANDIDATE THUMBNAIL

Thumbnail should show the relevant frame.

Do not crop so tightly that the investigator loses contextual information.

---

# 172. FACE BOX THUMBNAIL

If a bounding box is shown on the thumbnail:

    clearly distinguish overlay from source content.

Do not permanently modify source media.

---

# 173. SOURCE FRAME FULLSCREEN

Fullscreen viewing may be supported if existing CrimeKit media viewer supports it.

Maintain:

    timestamp
    source
    evidence context

---

# 174. DETAIL DRAWER WIDTH

Use enough width to read:

    provenance
    metadata
    review

Do not force critical evidence information into tiny sidebars.

---

# 175. PANEL RESIZING

If CrimeKit supports resizable panels, investigators may resize:

    video
    findings
    timeline

Do not introduce a complex layout engine solely for this feature.

---

# 176. STATE PERSISTENCE

Transient layout choices may persist according to existing UI conventions.

Sensitive information must not persist unnecessarily.

---

# 177. URL SECURITY

URLs may contain:

    case ID
    investigation ID
    candidate ID

but must not contain:

    embeddings
    signed secrets
    raw sensitive image data

---

# 178. DEEP LINK

A candidate deep link should:

    open case
    verify authorization
    open investigation
    open candidate

---

# 179. REFRESHED DEEP LINK

After refresh:

    fetch authorization
    fetch candidate
    load source context
    reconnect realtime if job active

---

# 180. NOTIFICATION CENTER

If CrimeKit already has a notification center:

    Candidate found
    Search completed
    Search failed

may be summarized there.

Do not create a separate face-only notification system.

---

# 181. NOTIFICATION CONTENT

Example:

    Face Trace
    New candidate sighting found in CCTV-02 at 14:21:03.

Avoid:

    Criminal detected!

---

# 182. NOTIFICATION NAVIGATION

Click notification:

    open investigation
       ↓
    highlight candidate

---

# 183. ACCESSIBILITY OF NOTIFICATIONS

Notifications should be accessible and not rely only on animation.

---

# 184. UI SECURITY REVIEW CHECKLIST

[ ] No raw embeddings in browser.

[ ] No secrets in browser.

[ ] No direct database access.

[ ] No uncontrolled evidence URLs.

[ ] Case context always visible.

[ ] Unauthorized source frames are not shown.

[ ] Review actions are permission-aware.

[ ] Cross-case search is controlled.

---

# 185. UX TRUST CHECKLIST

[ ] Candidate called candidate.

[ ] Similarity called similarity.

[ ] Quality shown separately.

[ ] Source evidence easy to open.

[ ] Provenance easy to inspect.

[ ] Machine result separated from investigator decision.

[ ] No automatic guilt/identity language.

---

# 186. REALTIME CHECKLIST

[ ] Search starts asynchronously.

[ ] Status appears immediately.

[ ] Live findings appear.

[ ] WebSocket reconnect works.

[ ] API state reconciliation works.

[ ] No frame-level UI spam.

[ ] Partial results are visible.

[ ] Failure state is visible.

---

# 187. INVESTIGATOR EFFICIENCY CHECKLIST

[ ] Reference is obvious.

[ ] Evidence scope is obvious.

[ ] Candidate source is obvious.

[ ] Timestamp is obvious.

[ ] Source frame is one action away.

[ ] Provenance is one action away.

[ ] Review is one action away after evidence inspection.

---

# 188. VISUAL QUALITY CHECKLIST

[ ] Existing CrimeKit design tokens reused.

[ ] Typography consistent.

[ ] Icons consistent.

[ ] Spacing consistent.

[ ] Dark/light themes work.

[ ] Evidence remains readable.

[ ] Motion is restrained.

[ ] No unnecessary AI theatrics.

---

# 189. PERFORMANCE CHECKLIST

[ ] Large candidate lists remain responsive.

[ ] Timeline is virtualized/paginated where required.

[ ] WebSocket events are efficiently handled.

[ ] Source videos are not unnecessarily prefetched.

[ ] Candidate detail loads on demand.

[ ] Graph context is focused.

---

# 190. FINAL UI ACCEPTANCE

An investigator should be able to understand the feature in a few seconds:

    What face am I tracing?
    What evidence am I searching?
    Is processing active?
    Has CrimeKit found a candidate?
    Where did the candidate come from?
    What is the similarity?
    What is the source evidence?
    What has been reviewed?

The UI succeeds when those answers are visible without hiding complexity or inventing certainty.

---

# 191. FINAL UX PRINCIPLE

The ultimate interaction should feel like:

    "CrimeKit found a candidate here.
     Let me inspect exactly where it came from."

not:

    "The AI says this is the criminal."

The interface must make evidence verification easier than blind trust.

That is the defining UX principle of Face Trace Investigator.
