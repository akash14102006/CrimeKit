# CRIMEKIT — GLOBAL KNOWLEDGE GRAPH DESIGN SYSTEM
## MASTER PROMPT — APPLY THE CURRENT KNOWLEDGE GRAPH THEME + DESIGN SYSTEM TO THE ENTIRE APPLICATION

Act as a world-class Principal Product Designer, Design Systems Architect, Frontend Architect, UX Engineer, Accessibility Engineer, and Enterprise SaaS UI Lead.

## MISSION

The current CrimeKit Knowledge Graph page has a strong dark enterprise visual language:

- near-black application shell
- dark sidebar
- cyan/blue active navigation
- dark surfaces
- thin subtle borders
- compact controls
- serif-style CrimeKit headings
- restrained cyan accents
- compact status pills
- dense enterprise layouts
- dark cards
- clean top search/header
- minimal visual noise

MAKE THIS THE SINGLE UNIFIED CRIMEKIT DESIGN SYSTEM FOR EVERY PAGE.

Do NOT redesign each page independently.

Do NOT create a different visual style per module.

Do NOT keep the old white/default SaaS appearance on other pages.

The entire application must feel like ONE PRODUCT.

## GLOBAL TARGET

Every page must visually belong to the same CrimeKit product:

```text
GLOBAL HEADER
+
GLOBAL SIDEBAR
+
GLOBAL TYPOGRAPHY
+
GLOBAL COLORS
+
GLOBAL SPACING
+
GLOBAL SURFACES
+
GLOBAL CONTROLS
+
GLOBAL STATUS STATES
+
GLOBAL INTERACTION PATTERNS
```

The Knowledge Graph visual language becomes the reference system.

## PAGES TO MIGRATE

Apply the same design language end-to-end to:

1. Dashboard
2. Cases
3. Evidence Library
4. Search
5. AI Workspace
6. Knowledge Graph
7. Timeline
8. Processing
9. Reports
10. Compliance
11. Settings
12. Notifications
13. Profile
14. all detail pages
15. all case workspaces
16. all entity/evidence inspectors
17. all dialogs/modals/drawers
18. all loading/empty/error states

Do not leave isolated legacy styling behind.

# 1. DESIGN REFERENCE

Use the currently shown Knowledge Graph / Case Atlas screen as the PRIMARY CrimeKit visual reference.

Match its visual grammar:

```text
DARK ENTERPRISE SHELL
        ↓
DARK SIDEBAR
        ↓
COMPACT TOP HEADER
        ↓
GLOBAL SEARCH
        ↓
CYAN ACTIVE STATES
        ↓
DARK CONTENT SURFACES
        ↓
THIN BORDERS
        ↓
COMPACT CARDS
        ↓
SERIF CRIMEKIT HEADINGS
        ↓
CLEAN DATA-DENSE CONTENT
```

The goal is not pixel-copying one screen.

The goal is to establish a reusable CrimeKit Design System from it.

# 2. GLOBAL SHELL

Every page must use the same application shell.

```text
┌─────────────────────────────────────────────────────────────────────┐
│ CrimeKit │ Global Search                         │ Theme │ Bell │ AM │
├──────────────┬──────────────────────────────────────────────────────┤
│              │                                                      │
│ Sidebar      │ Page Content                                         │
│              │                                                      │
│ Dashboard    │                                                      │
│ Cases        │                                                      │
│ Evidence     │                                                      │
│ Search       │                                                      │
│ AI Workspace │                                                      │
│ Knowledge    │                                                      │
│ Timeline     │                                                      │
│ Processing   │                                                      │
│ Reports      │                                                      │
│ Compliance   │                                                      │
│              │                                                      │
└──────────────┴──────────────────────────────────────────────────────┘
```

Never create page-specific global headers or sidebars unless there is a proven requirement.

# 3. SIDEBAR

Use the Knowledge Graph sidebar as the canonical shell.

Requirements:

- dark surface
- consistent width
- CrimeKit logo/brand
- grouped navigation
- compact section headings
- consistent icons
- active item highlighted in CrimeKit cyan/blue
- hover state
- selected state
- keyboard focus state
- scroll behavior
- bottom account/sign-out area

All pages use the same sidebar component.

Do not duplicate sidebar markup across pages.

# 4. TOP HEADER

Use one reusable global header.

Include only useful items:

```text
Global Search
Theme Toggle
Notifications
Profile
```

Keep it compact.

Do not place page-specific technical information in the global header.

# 5. THEME SYSTEM

Create one global theme system.

Preferred:

```text
CrimeKit Dark
CrimeKit Light
System
```

The existing top-right theme toggle controls the entire application.

Theme switching must affect:

- sidebar
- header
- cards
- tables
- forms
- dialogs
- drawers
- timeline
- processing
- reports
- AI workspace
- Knowledge Graph
- 2D graph
- 3D graph
- charts
- notifications

Never let one page hard-code its own theme.

# 6. DESIGN TOKENS

Create reusable semantic tokens.

Examples:

```text
--ck-bg
--ck-surface
--ck-surface-elevated
--ck-surface-hover
--ck-border
--ck-border-subtle
--ck-text
--ck-text-muted
--ck-text-dim
--ck-accent
--ck-accent-hover
--ck-focus
--ck-success
--ck-warning
--ck-danger
--ck-info
```

Graph-specific tokens:

```text
--ck-graph-bg
--ck-graph-edge
--ck-graph-edge-muted
--ck-graph-selection
--ck-node-person
--ck-node-device
--ck-node-location
--ck-node-evidence
--ck-node-artifact
--ck-node-event
```

Do not scatter hard-coded colors across components.

# 7. TYPOGRAPHY

Use a single CrimeKit typography system.

Maintain the visual hierarchy seen in the Knowledge Graph:

```text
Page title
Section title
Card title
Body
Metadata
Caption
```

Headings should retain the distinctive CrimeKit serif character where already established.

Body/UI text should remain highly readable and consistent.

Do not allow random font families per page.

# 8. SPACING

Create one spacing scale.

Use consistently for:

- page margins
- card padding
- form gaps
- table rows
- toolbar spacing
- sidebar spacing
- modal spacing
- inspector spacing

Do not allow every page to invent different spacing.

# 9. BORDERS

Use the subtle Knowledge Graph border language:

- thin
- low contrast
- consistent radius
- minimal decoration

Avoid:

- heavy borders
- giant shadows
- excessive glassmorphism
- colorful outlines everywhere

# 10. CARDS

Use one global CrimeKit card system.

Card styles:

```text
default
interactive
selected
warning
error
success
```

The Cases page, Dashboard, Evidence Library, Reports, and AI Workspace must use the same card language.

# 11. BUTTONS

Create one global button system:

```text
Primary
Secondary
Ghost
Danger
Icon
```

Maintain:

- same height
- same radius
- same typography
- same hover
- same focus
- same disabled state

Do not create unique button styles per page.

# 12. INPUTS

All search boxes, filters, forms and selectors must share the same visual language.

Use:

```text
dark/light surface
thin border
consistent radius
consistent focus ring
same icon alignment
same placeholder treatment
```

This includes:

- global search
- case search
- evidence search
- graph search
- AI input
- report filters
- timeline filters

# 13. STATUS SYSTEM

Unify statuses across CrimeKit.

Use one semantic vocabulary:

```text
OPEN
CLOSED
PROCESSING
COMPLETED
FAILED
WARNING
REVIEW
ACTIVE
INACTIVE
LIVE
OFFLINE
PENDING
```

Use consistent chips/pills.

Do not invent random status colors.

# 14. TABLES

Cases, evidence, processing jobs, reports and search results must share one enterprise table system.

Requirements:

- compact rows
- subtle separators
- readable headers
- hover row state
- selected row state
- pagination
- sorting
- filtering
- keyboard support

The table should feel like the same product as the Knowledge Graph.

# 15. FORMS

All forms must use the same:

- labels
- helper text
- inputs
- dropdowns
- validation
- error messages
- buttons
- spacing

# 16. MODALS + DRAWERS

Use one global system for:

- confirmation
- create case
- evidence upload
- entity inspector
- report export
- settings
- processing details

Do not create unrelated modal appearances.

# 17. BREADCRUMBS

Use a consistent CrimeKit breadcrumb style.

Example:

```text
CrimeKit / Cases / Case CK-001
```

Knowledge Graph's breadcrumb style can become the canonical pattern.

# 18. PAGE HEADERS

Every page should use a common page-header component:

```text
Page Title
Short useful description
Actions
```

Do NOT fill pages with long explanatory text.

Keep content concise.

# 19. CONTENT DENSITY

The product must be enterprise-dense.

Prefer:

```text
useful data
+
clear hierarchy
```

over:

```text
large decorative whitespace
+
marketing copy
```

Do not turn operational pages into landing pages.

# 20. DASHBOARD

Convert Dashboard into the same CrimeKit visual system:

- dark cards
- concise metrics
- consistent charts
- compact sections
- cyan interaction states
- same header/sidebar
- same typography

Do not make it visually unrelated to Knowledge Graph.

# 21. CASES

Cases must use:

- same background
- same cards
- same headings
- same buttons
- same status chips
- same search/filter controls

Case Atlas / case selection should visually connect naturally into Knowledge Graph.

# 22. EVIDENCE LIBRARY

Use the same CrimeKit system for:

- evidence cards
- metadata
- file status
- upload controls
- hash information
- provenance actions
- preview panels

The Evidence Library should feel like the same forensic product.

# 23. SEARCH

Use the same search language as Knowledge Graph.

Search results:

```text
Case
Evidence
Entity
Artifact
Event
```

Use compact results and clear provenance/status indicators.

# 24. AI WORKSPACE

AI Workspace must use the same CrimeKit shell and controls.

Do NOT turn the entire application into a ChatGPT clone.

AI should remain an integrated forensic workspace.

Preserve evidence-grounding and human review.

# 25. KNOWLEDGE GRAPH

Keep the immersive 3D graph experience.

It may remain visually specialized inside its canvas:

- deep-space background
- 3D nodes
- wireframes
- orbit rings
- curved edges
- spatial labels
- graph particles

BUT:

The surrounding shell must use the SAME global CrimeKit theme.

# 26. TIMELINE

Timeline should use:

- same background
- same panels
- same typography
- same status colors
- same controls
- same selected-state language

Timeline events should visually connect with Knowledge Graph and Evidence.

# 27. PROCESSING

Processing should use:

- same cards
- same status chips
- same progress indicators
- same technical metadata treatment
- same table system

Do not create a separate “developer console” appearance.

# 28. REPORTS

Reports must use the same shell and visual language.

Export actions must use global buttons and dialogs.

# 29. COMPLIANCE

Compliance must use the same:

- page header
- cards
- tables
- status indicators
- controls
- typography

# 30. ENTITY / EVIDENCE INSPECTORS

Every inspector/drawer must use a shared CrimeKit Inspector component.

Tabs may include:

```text
Overview
Relationships
Evidence
Timeline
Provenance
Analytics
```

# 31. LOADING STATES

Use one global loading system.

Avoid random spinners on every page.

Preferred:

- skeleton
- subtle progress indicator
- inline loading
- table skeleton
- graph loading state

# 32. EMPTY STATES

Keep them short.

Bad:

```text
Large paragraph explaining why there is no data...
```

Good:

```text
No evidence found.
```

with one useful action.

# 33. ERROR STATES

Use concise enterprise errors.

Example:

```text
Unable to load cases.
Retry
```

Do not expose technical stack traces.

# 34. TOASTS / NOTIFICATIONS

Use one global notification system.

Types:

```text
Success
Info
Warning
Error
```

Keep messages short.

# 35. ICON SYSTEM

Use one consistent icon library/style.

Do not mix unrelated icon styles.

# 36. RESPONSIVE DESIGN

The global shell must work at:

- desktop
- laptop
- tablet
- reduced viewport

3D graph gets its own responsive renderer behavior.

Do not redesign the product separately for every breakpoint.

# 37. ACCESSIBILITY

All shared components must support:

- keyboard navigation
- focus visibility
- sufficient contrast
- semantic labels
- ARIA where required
- reduced motion

Theme switching must preserve accessibility in both themes.

# 38. SECURITY

Never put sensitive data in visual-only client logic.

The visual redesign MUST NOT alter:

- RBAC
- authorization
- case isolation
- API security
- evidence security
- provenance rules

# 39. PERFORMANCE

Create shared components instead of duplicated implementations.

Avoid:

- unnecessary re-renders
- giant CSS bundles
- duplicated state
- duplicate API requests
- unnecessary graph rerenders

# 40. IMPLEMENTATION STRATEGY

FIRST inspect the repository.

Find:

- global layout
- sidebar
- topbar
- theme provider
- CSS variables
- Tailwind configuration
- design tokens
- reusable UI components
- Knowledge Graph components
- all page routes

Create an inventory:

```text
Component
Current style
Target style
Reuse?
Refactor?
Replace?
```

Do not start by blindly editing every page.

# 41. REFACTOR TO SHARED COMPONENTS

Create or reuse:

```text
CrimeKitShell
CrimeKitSidebar
CrimeKitHeader
CrimeKitPageHeader
CrimeKitCard
CrimeKitButton
CrimeKitInput
CrimeKitSelect
CrimeKitBadge
CrimeKitTable
CrimeKitModal
CrimeKitDrawer
CrimeKitTabs
CrimeKitToast
CrimeKitEmptyState
CrimeKitErrorState
CrimeKitLoadingState
```

Use the repository's existing component architecture where possible.

# 42. DO NOT DUPLICATE

There must be one source for:

```text
theme
sidebar
header
button styles
input styles
status colors
spacing tokens
typography
card styles
modal styles
```

# 43. REMOVE LEGACY VISUAL SYSTEMS

Identify and remove/replace inconsistent legacy styles such as:

- old white shell
- page-specific font overrides
- unrelated colors
- unrelated border radii
- old card styles
- old button styles
- inconsistent sidebar variants
- inconsistent topbars

Do not change business behavior while removing styling duplication.

# 44. SPECIAL RULE FOR KNOWLEDGE GRAPH

Do NOT flatten the 3D Knowledge Graph into ordinary page styling.

Keep the specialized 3D canvas.

Only unify:

```text
global shell
topbar
sidebar
toolbar
panels
buttons
inputs
inspector
theme
```

The graph itself can retain immersive spatial rendering.

# 45. GLOBAL THEME TOGGLE

The top-right theme control must be global.

Example:

```text
[ Global Search ]          [☾] [Bell] [AM]
```

Theme changes must affect every page instantly.

Do not create:

```text
Dashboard theme
Cases theme
Graph theme
```

Create:

```text
ONE CRIMEKIT THEME
```

# 46. VISUAL CONSISTENCY TEST

Open every route and compare:

```text
Dashboard
Cases
Evidence
Search
AI
Knowledge Graph
Timeline
Processing
Reports
Compliance
```

Ask:

> Does this look like the same application?

If not, fix it.

# 47. FINAL DESIGN PRINCIPLE

The user should be able to move:

```text
Cases
 ↓
Evidence
 ↓
Knowledge Graph
 ↓
Timeline
 ↓
Processing
 ↓
Reports
```

without feeling that they opened different products.

# 48. FINAL ACCEPTANCE CRITERIA

The implementation is COMPLETE only when:

[ ] One global theme system exists.

[ ] Top-right theme toggle controls the entire application.

[ ] All pages share the same CrimeKit shell.

[ ] All pages share the same sidebar.

[ ] All pages share the same header.

[ ] All pages use the same typography.

[ ] All pages use the same spacing.

[ ] All pages use the same buttons.

[ ] All pages use the same inputs.

[ ] All pages use the same cards.

[ ] All pages use the same status system.

[ ] All pages use the same table system.

[ ] All pages use the same modal/drawer system.

[ ] All pages use the same loading/empty/error states.

[ ] Knowledge Graph retains its immersive 3D specialization.

[ ] 3D canvas responds to the global theme.

[ ] Existing functionality is preserved.

[ ] Existing routes are preserved.

[ ] Existing APIs are preserved.

[ ] RBAC is preserved.

[ ] Evidence security is preserved.

[ ] Case isolation is preserved.

[ ] Provenance is preserved.

[ ] No duplicate theme systems remain.

[ ] No inconsistent legacy shell remains.

[ ] Desktop layout is visually consistent.

[ ] Accessibility works.

[ ] Type checking passes.

[ ] Build passes.

[ ] Visual regression passes.

# 49. FINAL COMMAND

Do not merely recolor the application.

Transform the existing CrimeKit UI into ONE coherent enterprise forensic product using the current Knowledge Graph visual language as the design-system reference.

The desired result is:

```text
CrimeKit
   ↓
ONE DESIGN SYSTEM
   ↓
ONE THEME
   ↓
ONE SHELL
   ↓
ONE VISUAL LANGUAGE
   ↓
ALL PAGES
```

with:

```text
Knowledge Graph
=
same global CrimeKit product
+
specialized immersive 3D forensic canvas
```

Do not add unnecessary text.
Do not add decorative UI.
Do not redesign working functionality.
Do not create page-specific visual systems.

Make every page feel like it belongs to the same international enterprise forensic platform.
