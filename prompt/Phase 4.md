# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 4 — Enterprise Case Management
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 4

Objective:

Develop ONLY the complete Enterprise Case Management Module.

This is NOT a CRUD page.

This is the core investigation management system used by investigators, supervisors, forensic analysts, administrators and judges.

The module must behave like enterprise investigation platforms including:

• IBM i2
• Magnet AXIOM
• Cellebrite Pathfinder
• Nuix Investigate
• Palantir Gotham
• Microsoft Defender XDR
• CrowdStrike Falcon

Everything MUST integrate with the existing CrimeKit backend.

NO mock data.

NO placeholder APIs.

NO redesign.

NO fake workflows.

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Frontend Architect

Principal Product Designer

Principal UX Architect

Principal Investigation Platform Architect

Senior React Engineer

Senior Next.js Engineer

Senior Enterprise UI Engineer

Senior Security Engineer

------------------------------------------------------------------------------

# SOURCE OF TRUTH

Before writing ANY code

Read EVERYTHING.

Priority

1.

graphify-out/

graph.json

GRAPH_REPORT.md

2.

Planning/

3.

Case Management Planning

4.

Architecture/

5.

Frontend Constitution

6.

Backend Constitution

7.

Investigation Workflow

8.

Design Bible

9.

OpenAPI

10.

Case APIs

11.

Evidence APIs

12.

Workspace APIs

13.

RBAC

14.

Audit APIs

15.

Existing Frontend

16.

Existing Components

17.

Existing Providers

18.

Existing API Client

19.

Existing Stores

20.

Existing Design System

Never guess.

Never invent APIs.

Never redesign.

Reuse everything.

------------------------------------------------------------------------------

# IMPORTANT

DO NOT

Create mock cases

Create fake IDs

Create local JSON

Create placeholder investigators

Create fake search

Create fake pagination

Create duplicate API layer

Create duplicate components

Create duplicate stores

Everything must come from backend.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY

Enterprise Case Management.

Includes

✓ Case List

✓ Case Details

✓ Create Case

✓ Edit Case

✓ Delete Case

✓ Case Search

✓ Filters

✓ Pagination

✓ Sorting

✓ RBAC

✓ Audit Integration

Nothing else.

Do NOT implement

Dashboard

Workspace

Evidence Viewer

Timeline

Knowledge Graph

Reports

Settings

AI Chat

------------------------------------------------------------------------------

# MODULE PURPOSE

Case Management is the central entity of CrimeKit.

Everything revolves around a Case.

Evidence

↓

AI

↓

Knowledge Graph

↓

Timeline

↓

Reports

↓

Chain of Custody

↓

Processing Jobs

All connect to Cases.

------------------------------------------------------------------------------

# PAGE STRUCTURE

Enterprise Layout

Header

↓

Breadcrumb

↓

Toolbar

↓

Search

↓

Filters

↓

Bulk Actions

↓

Case Table

↓

Pagination

↓

Quick Preview

------------------------------------------------------------------------------

# CASE LIST

Integrate backend.

Display

Case Number

Case ID

Title

Description Preview

Status

Priority

Category

Assigned Investigator

Assigned Team

Created By

Created Date

Updated Date

Evidence Count

AI Findings Count

Timeline Events

Knowledge Graph Status

Processing Status

Compliance Status

Storage Usage

Quick Actions

Everything must be live.

------------------------------------------------------------------------------

# TABLE FEATURES

Enterprise Data Table

Support

Sorting

Pagination

Column Resize

Column Hide

Column Reorder

Pinned Columns

Sticky Header

Infinite Scroll

CSV Export

Excel Export

Selection

Bulk Selection

Keyboard Navigation

------------------------------------------------------------------------------

# SEARCH

Enterprise Search

Backend only.

Support

Case Number

Title

Description

Tags

Case Owner

Investigator

Status

Priority

Category

Evidence

Date

AI Findings

Case ID

Organization

Project

No client-side filtering.

------------------------------------------------------------------------------

# FILTERS

Backend Filters

Status

Priority

Investigator

Department

Organization

Project

Evidence Count

Date Range

Updated Date

Created Date

Category

Tags

Risk Level

Processing Status

AI Status

Compliance Status

Combine filters.

Persist filters.

------------------------------------------------------------------------------

# CASE DETAILS

Dedicated page.

Display

General Information

Description

Status

Priority

Owner

Organization

Department

Created

Updated

Assigned Investigators

Evidence Summary

AI Summary

Timeline Summary

Processing Summary

Knowledge Graph Summary

Compliance Summary

Storage Summary

Recent Activity

Quick Actions

Everything from backend.

------------------------------------------------------------------------------

# CREATE CASE

Real backend.

Form

Case Title

Description

Priority

Category

Organization

Department

Assign Investigators

Tags

Notes

Validation

Duplicate Detection

Draft Save

Autosave

Cancel

Submit

Success

Failure

Audit

No mock validation.

------------------------------------------------------------------------------

# EDIT CASE

Load existing data.

Track changes.

Support

Autosave

Conflict Detection

Version Check

Optimistic Updates

Unsaved Changes Dialog

Audit Trail

RBAC

------------------------------------------------------------------------------

# DELETE CASE

Enterprise deletion.

Soft Delete if backend supports.

Otherwise backend API.

Confirmation

Impact Warning

Dependent Evidence Warning

Permission Check

Audit Entry

Undo if supported.

------------------------------------------------------------------------------

# QUICK ACTIONS

Per row

Open

Edit

Delete

Workspace

Upload Evidence

Timeline

Knowledge Graph

Generate Report

Only visible if RBAC permits.

------------------------------------------------------------------------------

# BULK ACTIONS

Support

Delete

Assign

Change Status

Change Priority

Export

Archive

Close Cases

Only backend supported actions.

------------------------------------------------------------------------------

# RBAC

Everything obeys backend.

Hide

Delete

Edit

Assign

Bulk Actions

Sensitive Fields

Archived Cases

Compliance Information

Only authorized users.

------------------------------------------------------------------------------

# API INTEGRATION

Reuse existing API layer.

No duplicate axios.

Support

Retry

Timeout

Refresh

Cancellation

AbortController

Interceptors

Typed responses

------------------------------------------------------------------------------

# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

No duplicate state.

Separate

List Cache

Detail Cache

Search Cache

Filter State

Pagination State

Selection State

------------------------------------------------------------------------------

# LOADING

Independent loading.

Case Table Skeleton

Card Skeleton

Search Loading

Filter Loading

Details Loading

Create Loading

Edit Loading

Delete Loading

------------------------------------------------------------------------------

# ERROR HANDLING

Support

401

403

404

409

422

429

500

Network

Timeout

Conflict

Validation Errors

Retry

------------------------------------------------------------------------------

# EMPTY STATES

No Cases

No Search Results

No Assigned Cases

No Permission

Backend Offline

No Organization

------------------------------------------------------------------------------

# PERFORMANCE

Server Components

Streaming

Suspense

Lazy Loading

Memoization

Prefetch Details

Virtualized Table

Request Deduplication

Optimistic Updates

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2

Keyboard Navigation

ARIA

Focus Management

Screen Reader

High Contrast

Reduced Motion

------------------------------------------------------------------------------

# RESPONSIVE

Desktop

Laptop

Tablet

Large Monitor

Maintain enterprise layout.

------------------------------------------------------------------------------

# SECURITY

Never expose

Hidden Cases

Restricted Cases

Deleted Cases

Other Organizations

Unauthorized Metadata

Backend RBAC is source of truth.

------------------------------------------------------------------------------

# AUDIT

Every mutation

Create

Edit

Delete

Assign

Bulk Action

Must use backend audit.

No frontend logging.

------------------------------------------------------------------------------

# VALIDATION

Verify

✓ Case List works

✓ Search works

✓ Filters work

✓ Pagination works

✓ Sorting works

✓ Details page works

✓ Create works

✓ Edit works

✓ Delete works

✓ Bulk Actions work

✓ RBAC works

✓ Audit works

✓ Loading works

✓ Error handling works

✓ Empty states work

✓ Existing design unchanged

✓ Existing components reused

✓ Backend integrated

✓ No mock data

✓ No console errors

✓ No TypeScript errors

✓ No ESLint errors

✓ Production-ready

------------------------------------------------------------------------------

# DELIVERABLES

Produce

1.

Case Module Architecture

2.

Backend Endpoint Mapping

3.

Screen Flow

4.

Component Hierarchy

5.

Case State Flow

6.

Search Architecture

7.

Filter Architecture

8.

Pagination Strategy

9.

Files Created

10.

Files Modified

11.

Files Reused

12.

Performance Report

13.

Security Report

14.

Accessibility Report

15.

Case Management Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

Do NOT implement

Evidence

Workspace

Timeline

Knowledge Graph

Reports

AI

Compliance

Administration

Settings

Stop immediately after the Enterprise Case Management module is completely integrated with the backend and all validation criteria pass.

Only then should Phase 5 (Enterprise Evidence Management) begin.