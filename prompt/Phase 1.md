# CrimeKit Frontend Development
# Phase 1 — Enterprise Frontend Foundation

---

# ROLE

You are joining an existing enterprise project called **CrimeKit**.

You are acting as:

- Principal Frontend Architect
- Principal Software Engineer
- Staff UI Engineer
- Staff UX Engineer
- React Architect
- Next.js Architect
- Enterprise Design System Architect

This is NOT a greenfield project.

This project already contains:

- Enterprise backend
- Enterprise architecture
- Enterprise APIs
- Enterprise Graphify knowledge graph
- Existing frontend
- Existing UI components
- Existing layouts
- Existing planning
- Existing design system

Your responsibility is to create ONLY the frontend foundation.

---

# SOURCE OF TRUTH

Before making ANY modification, study EVERYTHING.

Priority order:

1. graphify-out/
    - graph.json
    - GRAPH_REPORT.md

2. Planning/

3. Architecture/

4. Constitution/

5. Research/

6. Backend OpenAPI

7. Backend routes

8. Backend schemas

9. Existing frontend source

10. Existing design system

11. Existing components

12. Existing layouts

Never guess.

Never invent architecture.

Never redesign.

---

# IMPORTANT RULES

DO NOT

- redesign UI
- change colors
- change typography
- change spacing
- change animations
- replace components
- rewrite existing pages
- break folder structure
- delete existing code
- duplicate components
- create business pages
- create fake APIs
- create mock data
- create placeholder authentication
- create fake RBAC

Reuse everything already available.

---

# OBJECTIVE

Create ONLY the frontend foundation required for every future phase.

No business functionality.

No dashboard.

No evidence module.

No AI pages.

No reports.

No workspace.

No graph pages.

No timeline.

No settings.

Only infrastructure.

---

# ANALYZE EXISTING FRONTEND

Before coding,

perform a complete audit.

Produce a report including

- existing folder structure
- reusable components
- duplicate components
- dead components
- unused utilities
- existing providers
- current routing
- current layouts
- existing API layer
- existing state management
- current styling approach
- current theme
- existing hooks
- reusable UI primitives

Reuse as much as possible.

---

# BUILD FOUNDATION

Implement enterprise-grade frontend architecture.

---

## 1 Root Application

Configure

Next.js App Router

Route Groups

Nested Layouts

Global Metadata

Root Layout

Error Layout

Loading Layout

Not Found

Global Fonts

Theme Initialization

---

## 2 Folder Architecture

Restructure ONLY if necessary.

Target architecture similar to:

src/

app/

components/

features/

shared/

providers/

hooks/

services/

lib/

stores/

types/

styles/

config/

constants/

utils/

assets/

Do NOT break imports.

Maintain backward compatibility.

---

## 3 Providers

Create enterprise providers.

Theme Provider

Query Provider

Auth Provider

RBAC Provider

Toast Provider

Modal Provider

Command Provider

Settings Provider

Session Provider

---

## 4 API Layer

Create production API architecture.

Use existing backend contracts.

Implement

Axios instance

Request interceptors

Response interceptors

Refresh token handling

Retry strategy

Timeouts

Error normalization

Typed API client

Environment support

No endpoint duplication.

---

## 5 Authentication Foundation

NO login page.

NO register page.

Only infrastructure.

Implement

Session Context

Token storage

Refresh handling

Protected Route wrapper

Role Context

Permission Context

Auth hooks

Auth utilities

Do NOT create UI.

---

## 6 RBAC Foundation

Support backend roles.

Admin

Investigator

Analyst

Viewer

User

Implement

Permission checker

Role checker

Feature guards

Route guards

Component guards

Hooks

Utilities

---

## 7 TanStack Query

Configure

QueryClient

Mutation defaults

Retry strategy

Cache policy

Invalidation helpers

Optimistic update helpers

Error handlers

Suspense integration

Hydration support

---

## 8 Zustand

Create stores only.

No business logic.

App Store

Theme Store

Auth Store

Sidebar Store

Notification Store

Settings Store

Workspace UI Store

Loading Store

Modal Store

---

## 9 Error Handling

Enterprise Error Boundary

API Error Boundary

Async Error Boundary

Global Fallback

Toast Errors

Typed Errors

404

500

Unauthorized

Forbidden

Offline

---

## 10 Loading System

Global Loader

Page Loader

Section Loader

Skeleton System

Table Skeleton

Card Skeleton

Chart Skeleton

Sidebar Skeleton

Workspace Skeleton

Graph Skeleton

---

## 11 Navigation Framework

Do NOT create pages.

Create only navigation architecture.

Sidebar

Header

Breadcrumb

Top Navigation

Quick Actions

User Menu

Notifications

Search Entry

Command Palette

---

## 12 Shared UI

Build reusable primitives only.

Button

Input

Textarea

Checkbox

Switch

Select

Dialog

Popover

Tooltip

Tabs

Accordion

Badge

Avatar

Card

Data Table wrapper

Empty State

Error State

Loading State

Status Badge

Metric Card

Section Header

Page Header

---

## 13 Shared Hooks

Create

useAuth

usePermission

useRole

useTheme

useToast

useModal

useLoading

useDebounce

useLocalStorage

useBreakpoint

useInfiniteScroll

useKeyboard

---

## 14 Utilities

Create

API utilities

Date utilities

Evidence formatting

Case formatting

Role formatting

Permission helpers

Validation helpers

File helpers

Download helpers

Upload helpers

Search helpers

Color helpers

String helpers

Number helpers

---

## 15 Types

Generate

API types

User types

Evidence types

Case types

KG types

Timeline types

Workspace types

AI types

Processing types

Search types

Compliance types

Audit types

Common types

Infer from backend.

Never duplicate manually.

---

## 16 Styling

Use existing design system.

Do NOT redesign.

Wire

CSS Variables

Tailwind Tokens

Dark Theme

Light Theme

Spacing Scale

Typography

Elevation

Radius

Animations

Focus Rings

Accessibility Colors

---

## 17 Accessibility

Keyboard Navigation

Focus Management

ARIA

Screen Reader

Contrast

Reduced Motion

Semantic HTML

Skip Links

Accessible Dialogs

Accessible Tables

Accessible Forms

---

## 18 Performance

Streaming

Server Components

Suspense

Lazy Loading

Dynamic Imports

Image Optimization

Code Splitting

Prefetch

Virtualization Ready

Memoization Strategy

---

## 19 Security

Secure Token Storage

Route Protection

Permission Guards

XSS Prevention

CSRF Preparation

CSP Compatible

Secure Cookies Support

Sanitized Rendering

---

## 20 Logging

Prepare frontend logging.

No third-party service yet.

Support future

OpenTelemetry

Sentry

Datadog

Azure Monitor

---

# VALIDATION

After implementation verify

✓ Existing pages still work

✓ Existing design unchanged

✓ Existing components reused

✓ Existing imports working

✓ No duplicated architecture

✓ No broken routing

✓ No TypeScript errors

✓ No ESLint errors

✓ No build errors

✓ No hydration errors

✓ No runtime errors

✓ No API contract mismatch

✓ Backend compatibility maintained

✓ RBAC infrastructure ready

✓ Authentication infrastructure ready

✓ Foundation production-ready

---

# OUTPUT

At completion produce

1.

Architecture summary

2.

Folder tree

3.

Files created

4.

Files modified

5.

Files reused

6.

Components reused

7.

Providers added

8.

Stores added

9.

Utilities added

10.

Hooks added

11.

Validation report

12.

Performance summary

13.

Security summary

14.

Accessibility summary

15.

Foundation Readiness Score

Only after every item passes should Phase 2 (Authentication) begin.