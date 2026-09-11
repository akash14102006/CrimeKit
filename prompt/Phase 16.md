# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 16 — Enterprise Production Polish & Release Readiness
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 16 (FINAL)

Objective:

This is the FINAL frontend phase.

DO NOT create any new pages.

DO NOT redesign existing pages.

DO NOT modify the design system.

DO NOT change colors.

DO NOT change typography.

DO NOT change layouts.

DO NOT change spacing.

DO NOT create additional features.

This phase is ONLY about making the existing enterprise frontend completely production-ready.

Everything must integrate with the existing enterprise backend.

This phase should make CrimeKit feel comparable to:

• Microsoft Defender XDR
• Palantir Gotham
• IBM i2 Analyst Notebook
• Microsoft Azure Portal
• GitHub Enterprise
• Atlassian Cloud
• Elastic Security
• Splunk Enterprise
• AWS Console
• Google Cloud Console

==============================================================================

# ROLE

You are acting as

Principal Frontend Architect

Principal Performance Engineer

Principal UX Engineer

Principal Accessibility Engineer

Principal React Architect

Principal Next.js Architect

Principal Enterprise QA Engineer

Principal Security Engineer

Principal Production Release Engineer

==============================================================================

# PROJECT KNOWLEDGE

Before changing ANYTHING

Read EVERYTHING.

Priority

graphify-out/

graph.json

GRAPH_REPORT.md

Planning/

Architecture/

Frontend Constitution

Backend Constitution

UI Constitution

Performance Constitution

Security Constitution

Accessibility Constitution

OpenAPI

Entire frontend

Entire backend

Existing Design System

Reuse everything.

Never redesign.

==============================================================================

# IMPORTANT

DO NOT

Create pages

Create components that already exist

Redesign UI

Change colors

Change spacing

Change typography

Change layouts

Duplicate API calls

Duplicate stores

Duplicate components

Everything must polish the existing frontend only.

==============================================================================

# PRIMARY OBJECTIVE

Transform the existing frontend into an enterprise production-grade application.

Focus ONLY on

✓ API Integration

✓ Performance

✓ Accessibility

✓ Error Handling

✓ UX Polish

✓ Security

✓ Code Quality

✓ Production Optimization

==============================================================================

# PHASE 16 TASKS

==============================================================================
1. COMPLETE BACKEND INTEGRATION
==============================================================================

Audit the ENTIRE frontend.

Verify

Every page

Every widget

Every dialog

Every modal

Every drawer

Every chart

Every table

Every filter

Every form

Every search

Every timeline

Every graph

Every AI feature

Every workspace

Every report

Every compliance screen

Every admin screen

Every settings screen

must use the real backend.

Remove

Fake APIs

Static JSON

Hardcoded objects

Mock data

Placeholder arrays

Temporary data

Dummy users

Dummy evidence

Dummy reports

Everything must call backend.

==============================================================================

2. REMOVE ALL MOCK DATA
==============================================================================

Search entire project for

mock

dummy

sample

example

placeholder

fake

testData

demo

json

local arrays

fixtures

temporary

Replace everything with backend integration.

==============================================================================

3. API OPTIMIZATION
==============================================================================

Audit every API call.

Fix

Duplicate requests

Unnecessary refetches

Waterfall loading

Sequential requests

Cache invalidation

Retry logic

Timeout handling

AbortController

Optimistic updates

Background refresh

Deduplication

Request batching

Proper pagination

==============================================================================

4. TANSTACK QUERY OPTIMIZATION
==============================================================================

Verify

Query Keys

Invalidation

Prefetching

Optimistic Updates

Infinite Queries

Mutations

Background Refetch

Cache Time

Stale Time

Retry

Error Boundaries

Offline cache

==============================================================================

5. GLOBAL ERROR HANDLING
==============================================================================

Handle every backend error.

401

403

404

409

422

429

500

502

503

504

Timeout

Offline

Cancelled Request

Validation Error

Rate Limit

Token Expired

Session Expired

Connection Lost

Every error

must have

Friendly UI

Retry

Recovery

Audit

==============================================================================

6. LOADING EXPERIENCE
==============================================================================

Replace every spinner with

Skeletons

Progressive Loading

Streaming

Partial Rendering

Section Loading

Button Loading

Table Skeleton

Card Skeleton

Timeline Skeleton

Graph Skeleton

Report Skeleton

AI Skeleton

Workspace Skeleton

==============================================================================

7. EMPTY STATES
==============================================================================

Design enterprise empty states.

No Cases

No Evidence

No Reports

No AI Findings

No Graph

No Timeline

No Search Results

No Notifications

No History

No Queue

No Users

No Projects

No Organizations

No Sessions

No API Keys

No Compliance

Backend Offline

Permission Denied

==============================================================================

8. PERFORMANCE OPTIMIZATION
==============================================================================

Optimize

React Rendering

Memoization

React.memo

useMemo

useCallback

Code Splitting

Dynamic Imports

Tree Shaking

Lazy Components

Streaming

RSC

Partial Hydration

Suspense

Bundle Splitting

Route Splitting

==============================================================================

9. LARGE DATASET SUPPORT
==============================================================================

Virtualize

Evidence Tables

Timeline

Audit Logs

Queue

Reports

Search Results

Knowledge Graph Lists

Users

Organizations

Projects

Processing Logs

Support

100,000+

records.

==============================================================================

10. NEXT.JS 15 OPTIMIZATION
==============================================================================

Use

App Router

Server Components

Client Components

Streaming

Suspense

Metadata API

Dynamic Routes

Parallel Routes

Intercepting Routes

Image Optimization

Font Optimization

Edge Runtime where appropriate

==============================================================================

11. ACCESSIBILITY
==============================================================================

Achieve WCAG 2.2 AA.

Audit

ARIA

Keyboard Navigation

Focus

Contrast

Screen Readers

Labels

Forms

Dialogs

Menus

Graphs

Timeline

Tables

Charts

Toast

Notifications

Reduced Motion

High Contrast

==============================================================================

12. SECURITY HARDENING
==============================================================================

Verify

RBAC

Protected Routes

Permission Guards

Session Validation

CSRF Protection

CSP

Secure Cookies

Token Refresh

XSS Prevention

No sensitive data leakage

Never expose hidden backend routes.

==============================================================================

13. OFFLINE SUPPORT
==============================================================================

Implement

Offline Detection

Reconnect

Cached Queries

Retry Queue

Background Sync

Graceful Degradation

Read-only mode

==============================================================================

14. NOTIFICATIONS
==============================================================================

Enterprise notification center.

Support

Success

Warning

Error

Info

AI

Queue

Reports

Compliance

Security

Backend events

Toast queue

Notification center

==============================================================================

15. SEARCH EXPERIENCE
==============================================================================

Improve

Keyboard shortcuts

Debouncing

Search suggestions

Search history

Recent searches

Saved searches

Highlighted matches

==============================================================================

16. TABLE EXPERIENCE
==============================================================================

Every enterprise table should support

Sorting

Filtering

Column Visibility

Column Resize

Sticky Header

Sticky Columns

Pagination

Selection

Bulk Actions

Export

Copy

CSV

Keyboard

==============================================================================

17. FORM EXPERIENCE
==============================================================================

Every form

Autosave

Validation

Zod

React Hook Form

Inline Errors

Async Validation

Reset

Undo

Optimistic Save

==============================================================================

18. CHARTS
==============================================================================

Verify

Responsive

Lazy Loading

Backend Data

Loading Skeleton

No hardcoded datasets

==============================================================================

19. KNOWLEDGE GRAPH
==============================================================================

Optimize

Large Graph Rendering

Node Clustering

Edge Virtualization

Incremental Expansion

Mini Map

Viewport Culling

==============================================================================

20. TIMELINE
==============================================================================

Optimize

Virtualization

Zoom

Incremental Rendering

Lazy Events

Search

Filtering

==============================================================================

21. AI WORKSPACE
==============================================================================

Improve

Streaming

Markdown

Tables

Evidence Citations

Typing Animation

Retry

Abort

Conversation Restore

Pinned Conversations

==============================================================================

22. CODE QUALITY
==============================================================================

Eliminate

Duplicate Components

Dead Code

Unused Imports

Unused Hooks

Unused APIs

Unused Assets

Unused CSS

Unused Icons

Unused Routes

==============================================================================

23. TYPESCRIPT
==============================================================================

Achieve

Zero

TypeScript errors.

No

any

unless absolutely necessary.

Strong typing everywhere.

==============================================================================

24. ESLINT
==============================================================================

Achieve

Zero

warnings

Zero

errors.

==============================================================================

25. BUILD VALIDATION
==============================================================================

Verify

npm run lint

npm run type-check

npm run build

All succeed.

==============================================================================

26. TESTING
==============================================================================

Verify

Unit Tests

Component Tests

Integration Tests

E2E Tests

Critical User Flows

Authentication

Evidence

Timeline

AI

Reports

Search

Administration

Compliance

==============================================================================

27. RESPONSIVENESS
==============================================================================

Verify

Desktop

Laptop

Tablet

Ultra-wide

4K

No layout breaking.

==============================================================================

28. RELEASE AUDIT
==============================================================================

Audit

Performance

Accessibility

Security

Bundle Size

API Coverage

Code Coverage

Dead Code

Production Readiness

==============================================================================

# FINAL VALIDATION CHECKLIST

The frontend is complete ONLY IF

✓ Zero mock data remains

✓ 100% backend integration

✓ 100% RBAC respected

✓ All APIs connected

✓ All loading states polished

✓ All error states handled

✓ Accessibility WCAG 2.2 AA

✓ Lighthouse Performance ≥95

✓ Lighthouse Accessibility ≥100

✓ Lighthouse Best Practices ≥100

✓ Lighthouse SEO ≥95 (where applicable)

✓ Zero TypeScript errors

✓ Zero ESLint errors

✓ Production build succeeds

✓ No console errors

✓ No hydration errors

✓ No React warnings

✓ No memory leaks

✓ No duplicate API requests

✓ No dead code

✓ Offline mode works

✓ Optimistic updates work

✓ Skeletons everywhere

✓ Virtualization for large datasets

✓ Enterprise UX throughout

==============================================================================

# DELIVERABLES

Produce

1. Enterprise Frontend Audit Report

2. Backend Integration Report

3. Mock Data Removal Report

4. API Coverage Report

5. Performance Optimization Report

6. Accessibility Audit Report

7. Security Audit Report

8. Offline Support Report

9. Code Quality Report

10. Bundle Analysis Report

11. Lighthouse Report

12. Testing Report

13. Production Readiness Checklist

14. Files Created

15. Files Modified

16. Files Removed

17. Remaining Technical Debt (if any)

18. Final Enterprise Readiness Score

19. Judge Experience Score

20. Production Release Approval Report

==============================================================================

# FINAL RULE

Do NOT add any new features.

Do NOT create new pages.

Do NOT redesign any UI.

Do NOT modify the design system.

Focus exclusively on transforming the existing CrimeKit frontend into a fully production-ready, enterprise-grade application that integrates flawlessly with the backend and is ready for deployment.

The phase is complete only when the application is ready to be released to production with no known critical issues remaining.