# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 7 — Enterprise Investigation Timeline
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 7

Objective:

Develop ONLY the Enterprise Investigation Timeline Module.

The Timeline is one of the most critical forensic investigation tools in CrimeKit.

It must provide investigators with a complete chronological reconstruction of an investigation by combining every event generated across the entire platform.

This is NOT a simple activity log.

This is an interactive forensic timeline similar to:

• Magnet AXIOM Timeline
• Cellebrite Physical Analyzer Timeline
• IBM i2 Timeline
• Palantir Gotham Timeline
• Elastic Timeline
• Microsoft Defender Incident Timeline
• Splunk Timeline
• Nuix Timeline

Everything MUST integrate with the existing CrimeKit backend.

NO mock events.

NO fake timeline.

NO generated sample data.

Everything comes from backend APIs.

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Frontend Architect

Principal UX Architect

Principal Investigation Platform Architect

Principal Timeline Visualization Engineer

Principal React Engineer

Principal Next.js Engineer

Senior Product Designer

Senior Data Visualization Engineer

------------------------------------------------------------------------------

# SOURCE OF TRUTH

Before writing ANY code read EVERYTHING.

Priority

1.

graphify-out/

graph.json

GRAPH_REPORT.md

2.

Planning/

Timeline Planning

Investigation Planning

Workspace Planning

3.

Architecture/

4.

Timeline Constitution

5.

Frontend Constitution

6.

Backend Constitution

7.

Backend Timeline APIs

8.

Evidence APIs

9.

Processing APIs

10.

Chain of Custody APIs

11.

Knowledge Graph APIs

12.

AI APIs

13.

Search APIs

14.

Compliance APIs

15.

Audit APIs

16.

OpenAPI

17.

Existing Frontend

18.

Existing Components

19.

Existing Design System

Never redesign.

Never invent APIs.

Reuse existing architecture.

------------------------------------------------------------------------------

# IMPORTANT

DO NOT

Create fake timeline events

Create local JSON

Hardcode events

Generate sample investigations

Duplicate backend logic

Duplicate search

Duplicate filters

Duplicate API clients

Everything MUST come from backend.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY

Enterprise Investigation Timeline

Includes

✓ Chronological Timeline

✓ Multi-source Event Aggregation

✓ Timeline Search

✓ Timeline Filters

✓ Zoom Levels

✓ Event Details

✓ Event Correlation

✓ Timeline Navigation

✓ Timeline Export

✓ RBAC

Nothing else.

------------------------------------------------------------------------------

# TIMELINE PURPOSE

The Timeline reconstructs the entire investigation.

Every backend event becomes one chronological investigation story.

Sources include

Case Events

↓

Evidence Upload

↓

Evidence Processing

↓

Chain of Custody

↓

AI Findings

↓

Knowledge Graph

↓

Investigator Actions

↓

Reports

↓

Compliance

↓

Audit Logs

↓

System Events

Everything merged into one unified forensic timeline.

------------------------------------------------------------------------------

# PAGE LAYOUT

Reuse existing design.

Layout

Header

↓

Breadcrumb

↓

Timeline Toolbar

↓

Global Search

↓

Filters

↓

Zoom Controls

↓

Main Timeline

↓

Event Details Panel

↓

Correlation Panel

↓

Export Actions

------------------------------------------------------------------------------

# CHRONOLOGICAL TIMELINE

Display

Evidence Uploaded

Evidence Modified

Evidence Verified

Hash Verification

Processing Started

Processing Finished

OCR Completed

AI Analysis

Entity Extraction

Knowledge Graph Updates

Timeline Extraction

Risk Detection

Chain of Custody Transfer

Investigator Assignment

Case Created

Case Updated

Case Closed

Report Generated

Audit Events

Compliance Events

Every event must come from backend.

------------------------------------------------------------------------------

# TIMELINE MODES

Support

Vertical Timeline

Horizontal Timeline

Compact View

Expanded View

Grouped View

Continuous View

Cluster View

Investigator View

Evidence View

Case View

System View

Remember user preference.

------------------------------------------------------------------------------

# ZOOM LEVELS

Support

Minutes

Hours

Days

Weeks

Months

Years

Custom Range

Smooth zoom.

No performance degradation.

------------------------------------------------------------------------------

# SEARCH

Backend Search.

Support

Event ID

Evidence

Case

Hash

Entity

Investigator

Keyword

AI Finding

Knowledge Graph Entity

Timeline Event

Date

Tags

Processing Job

Chain of Custody

------------------------------------------------------------------------------

# FILTERS

Backend only.

Support

Event Type

Evidence Type

Investigator

Department

Case

Priority

Risk

Integrity

AI Confidence

Knowledge Graph

Processing Status

Chain of Custody

Date Range

Custom Filters

Persist filters.

------------------------------------------------------------------------------

# EVENT DETAILS

Selecting an event displays

Event Type

Timestamp

Case

Evidence

User

Action

Location

Description

Metadata

Hashes

Related AI Findings

Related KG Entities

Related Processing Jobs

Related Reports

Chain of Custody Link

Audit Information

Quick Actions

Everything from backend.

------------------------------------------------------------------------------

# CORRELATION PANEL

Display

Previous Event

Next Event

Related Events

Connected Evidence

Connected Cases

Connected Entities

Connected Timeline

Related AI Findings

Related Reports

Related Risks

------------------------------------------------------------------------------

# NAVIGATION

Support

Keyboard Navigation

Jump to Date

Jump to Event

Jump to Evidence

Jump to Case

Jump to AI Finding

Jump to Processing

Jump to Chain of Custody

Jump to Workspace

------------------------------------------------------------------------------

# EXPORT

Integrate backend.

Support

PDF

CSV

Excel

JSON

Timeline Snapshot

Court Timeline

Filtered Timeline

Investigator Timeline

Backend-generated exports only.

------------------------------------------------------------------------------

# TIMELINE LEGEND

Display

Evidence Event

Processing Event

AI Event

KG Event

Custody Event

Report Event

Compliance Event

Audit Event

System Event

Status Icons

Severity

Risk

------------------------------------------------------------------------------

# REALTIME

Support

Polling

WebSocket (if backend supports)

Live Updates

Auto Scroll

Manual Refresh

New Event Notification

------------------------------------------------------------------------------

# API INTEGRATION

Reuse existing API layer.

Use ONLY backend APIs.

Timeline

Evidence

Processing

KG

AI

Reports

Audit

Compliance

Workspace

------------------------------------------------------------------------------

# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

Timeline Store

Filter Store

Zoom Store

Selection Store

Search Store

No duplicated state.

------------------------------------------------------------------------------

# LOADING

Timeline Skeleton

Event Skeleton

Details Skeleton

Search Loading

Export Loading

Independent loading.

------------------------------------------------------------------------------

# ERROR HANDLING

Handle

401

403

404

409

429

500

503

Timeout

Offline

Retry

Per-panel isolation.

------------------------------------------------------------------------------

# EMPTY STATES

No Timeline

No Events

No Search Results

No Filters

No Permission

Backend Offline

------------------------------------------------------------------------------

# PERFORMANCE

Virtualized Timeline

Lazy Rendering

Infinite Scroll

Streaming

Memoization

Code Splitting

Progressive Loading

Large Dataset Optimization

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2 AA

Keyboard

ARIA

Screen Reader

Focus

Reduced Motion

High Contrast

Accessible Timeline Navigation

------------------------------------------------------------------------------

# RESPONSIVE

Desktop

Laptop

Tablet

Wide Screen

Maintain enterprise layout.

------------------------------------------------------------------------------

# SECURITY

Respect backend RBAC.

Never expose

Hidden Timeline

Restricted Events

Private Evidence

Other Organizations

Hidden AI Findings

------------------------------------------------------------------------------

# AUDIT

Timeline interactions

Search

Filter

Export

Jump

View Event

Must integrate with backend audit logging.

------------------------------------------------------------------------------

# VALIDATION

Verify

✓ Timeline loads

✓ Chronological ordering correct

✓ Zoom works

✓ Search works

✓ Filters work

✓ Event details work

✓ Correlation panel works

✓ Export works

✓ Backend integration complete

✓ Existing design preserved

✓ Existing components reused

✓ No mock data

✓ No runtime errors

✓ No TypeScript errors

✓ No ESLint errors

✓ Production-ready

------------------------------------------------------------------------------

# DELIVERABLES

Produce

1.

Timeline Architecture

2.

Timeline Data Flow

3.

Backend API Mapping

4.

Component Hierarchy

5.

Search Architecture

6.

Filter Architecture

7.

Zoom Architecture

8.

Export Workflow

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

Timeline Validation Report

16.

Timeline Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

Do NOT implement

Knowledge Graph

Reports

AI Chat

Compliance

Administration

Settings

Stop immediately after the Enterprise Timeline module is fully integrated with the backend and all validation criteria pass.

Only after successful completion should Phase 8 (Enterprise Knowledge Graph Visualization) begin.