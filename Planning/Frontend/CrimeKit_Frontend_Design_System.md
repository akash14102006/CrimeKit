# CrimeKit Frontend Design System

Version: 1.0

## Purpose

This single markdown file is the master frontend specification for
CrimeKit.

## Sections

1.  Design Principles
2.  Technology Stack
3.  Design Tokens
4.  Component Library
5.  Layout System
6.  Authentication
7.  Dashboard
8.  Evidence
9.  Investigation
10. Timeline
11. Knowledge Graph
12. AI Assistant
13. Reports
14. Settings
15. Motion
16. Responsive Design
17. Accessibility
18. Folder Structure
19. Design Rules
20. Build Order

## Design Principles

-   Enterprise First
-   Accessibility First
-   Investigator Focused
-   Minimal Cognitive Load
-   Consistency
-   Performance

## Technology

-   React 19
-   TypeScript
-   Vite
-   Tailwind CSS
-   shadcn/ui
-   Framer Motion
-   Lucide Icons
-   TanStack Query

## Design Tokens

Colors - Primary #1E3A8A - Secondary #334155 - Background #F8FAFC -
Surface #FFFFFF - Border #E2E8F0 - Text #0F172A - Success #16A34A -
Warning #F59E0B - Error #DC2626 - AI #7C3AED

Typography - Inter - JetBrains Mono

Radius - 8,12,16,20,24

Spacing - 4,8,12,16,24,32,48,64

## Component Library

Buttons, Inputs, Cards, Navigation, Tables, Forms, Dialogs, Toasts,
Skeletons, Charts, Maps, Timeline, Knowledge Graph.

## Layouts

-   Authentication
-   Dashboard
-   Investigation Workspace
-   Evidence Workspace
-   Reports
-   Settings

## Modules

Authentication Dashboard Evidence Investigation Timeline Knowledge Graph
AI Assistant Reports Settings

## Motion

150-250ms transitions Fade, Scale, Slide, Blur

## Responsive

Mobile Tablet Desktop Ultra-wide

## Accessibility

WCAG AA Keyboard Navigation Focus Ring Screen Reader Reduced Motion

## Folder Structure

``` text
frontend/
├── design-system.md
├── components/
├── layouts/
├── pages/
├── features/
├── services/
├── hooks/
├── styles/
└── assets/
```

## Design Rules

-   Glass only for overlays, navbar and dialogs.
-   Neumorphism only for KPI/upload cards.
-   Sticky tables.
-   Purple reserved for AI.
-   One typography family.
-   Consistent spacing.

## Build Order

1.  Tokens
2.  Components
3.  Layouts
4.  Pages
5.  Responsive
6.  Accessibility
7.  Final Polish
