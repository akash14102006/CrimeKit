# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 11 — Enterprise Processing Queue & Forensic Job Management
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 11

Objective:

Develop ONLY the Enterprise Processing Queue and Forensic Job Management module.

This page is the operational control center for all forensic processing jobs.

Everything must integrate with the existing backend.

Do NOT create fake queues.

Do NOT simulate processing.

Do NOT create frontend timers.

Everything must come from backend APIs, WebSockets, or polling.

Comparable Enterprise Systems

• Magnet AXIOM
• Cellebrite Physical Analyzer
• Palantir Foundry
• IBM i2
• Splunk SOAR
• Elastic Security
• Microsoft Sentinel
• Cortex XSOAR

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Frontend Architect

Principal Distributed Systems Engineer

Principal Queue Management Engineer

Principal UX Architect

Principal React Architect

Principal Next.js Architect

Principal Product Designer

Principal Enterprise Dashboard Designer

------------------------------------------------------------------------------

# PROJECT KNOWLEDGE

Before writing ANY code

Read completely

graphify-out/

graph.json

GRAPH_REPORT.md

Planning/

Processing Planning

Queue Planning

Worker Planning

Evidence Planning

Workspace Planning

Architecture/

Frontend Constitution

Backend Constitution

Distributed Processing Constitution

Infrastructure Constitution

OpenAPI

Backend Processing APIs

Advanced Forensics APIs

Worker APIs

AI Processing APIs

Knowledge Graph APIs

Workspace APIs

Reuse everything.

Never redesign.

Never invent APIs.

------------------------------------------------------------------------------

# IMPORTANT

Do NOT

Create fake workers

Create fake queues

Generate fake progress

Generate random processing %

Use frontend timers

Simulate retries

Everything must come directly from backend.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY

Enterprise Processing Queue Module

Includes

✓ Queue Dashboard

✓ Live Processing Jobs

✓ Worker Status

✓ Queue Statistics

✓ Job Details

✓ Progress Tracking

✓ Retry Processing

✓ Cancel Processing

✓ Failed Jobs

✓ Processing History

✓ Worker Monitoring

Nothing else.

------------------------------------------------------------------------------

# PAGE PURPOSE

This page is the operational dashboard for investigators and administrators.

Users should instantly understand

Current Queue

Running Jobs

Completed Jobs

Failed Jobs

Cancelled Jobs

Worker Health

Queue Performance

Processing Throughput

------------------------------------------------------------------------------

# PAGE LAYOUT

Reuse existing design.

Header

↓

Processing Overview Cards

↓

Worker Status Panel

↓

Live Queue

↓

Running Jobs

↓

Completed Jobs

↓

Failed Jobs

↓

History

↓

Job Details Drawer

↓

Logs Panel

------------------------------------------------------------------------------

# OVERVIEW KPI CARDS

Display

Queued Jobs

Running Jobs

Completed Jobs

Failed Jobs

Cancelled Jobs

Retry Queue

Average Processing Time

Average Queue Time

Worker Utilization

Total Evidence Processed

Today's Jobs

System Throughput

All values from backend.

------------------------------------------------------------------------------

# PROCESSING QUEUE

Display queue

Queued

↓

Waiting

↓

Running

↓

Completed

↓

Failed

↓

Cancelled

Support

Sorting

Filtering

Searching

Pagination

Real-time updates

------------------------------------------------------------------------------

# LIVE JOBS

Display

Job ID

Evidence Name

Evidence Type

Case

Current Processor

Priority

Queue Position

Assigned Worker

Started Time

Estimated Remaining

Progress

Status Badge

Processing Speed

------------------------------------------------------------------------------

# WORKER STATUS

Display all backend workers.

Each worker

Worker ID

Status

Idle

Busy

Offline

Restarting

CPU Usage

Memory Usage

Running Job

Completed Today

Failed Today

Queue Assigned

Heartbeat

Last Seen

Worker Version

------------------------------------------------------------------------------

# JOB PROGRESS

Display

Overall Progress

Processor Progress

Pipeline Stage

Current Processor

Elapsed Time

Remaining Time

Completed Stages

Pending Stages

Skipped Stages

Failed Stage

Visual progress timeline.

------------------------------------------------------------------------------

# PROCESSING PIPELINE

Display actual forensic pipeline.

Example

Integrity Verification

↓

Metadata Extraction

↓

Hash Verification

↓

OCR

↓

Thumbnail Generation

↓

AI Pipeline

↓

Knowledge Graph

↓

Timeline Extraction

↓

Entity Extraction

↓

Correlation

↓

Final Report

Highlight

Completed

Running

Pending

Failed

Cancelled

------------------------------------------------------------------------------

# PROCESSOR DETAILS

Display

Processor Name

Processor Version

Execution Time

Output Size

Status

Warnings

Errors

Retries

Artifacts Produced

Logs

------------------------------------------------------------------------------

# JOB DETAILS DRAWER

Opens when selecting a job.

Display

Job Metadata

Evidence

Case

Assigned Worker

Pipeline

Outputs

AI Findings

KG Status

Timeline Status

Forensic Results

Processing Logs

Retry Count

Audit History

------------------------------------------------------------------------------

# RETRY PROCESSING

Backend only.

Allow retry only when backend permits.

Display

Retry Reason

Retry Count

Retry History

Retry Status

Confirmation dialog.

------------------------------------------------------------------------------

# CANCEL PROCESSING

Allow cancellation only if backend allows.

Display

Reason

Confirmation

Audit Trail

Cancelled By

Cancelled Time

Update queue immediately.

------------------------------------------------------------------------------

# FAILED JOBS

Dedicated section.

Display

Failure Reason

Processor

Stack Summary

Retry Available

Evidence

Case

Timestamp

Worker

Quick Retry

Open Logs

------------------------------------------------------------------------------

# PROCESSING HISTORY

Display

Completed Jobs

Cancelled Jobs

Failed Jobs

Average Runtime

Historical Queue

Historical Worker

Export History

Search History

Filters

Date

Case

Worker

Processor

Status

------------------------------------------------------------------------------

# PROCESSING LOGS

Backend logs only.

Display

Timestamp

Processor

Stage

Severity

Message

Duration

Worker

Support

Filter

Search

Download

Copy

------------------------------------------------------------------------------

# QUEUE ANALYTICS

Display

Jobs per Hour

Processing Time

Worker Utilization

Success Rate

Failure Rate

Average Retry

Queue Length Trend

Processing Trend

Evidence Types

Charts from backend.

------------------------------------------------------------------------------

# FILTERS

Support

Status

Priority

Case

Worker

Evidence Type

Processor

Date

User

AI

Processing Stage

------------------------------------------------------------------------------

# SEARCH

Search

Job ID

Evidence

Case

Worker

Processor

Hash

Status

------------------------------------------------------------------------------

# EXPORT

Export

Queue Report

CSV

Excel

PDF

Processing Logs

Worker Report

History

------------------------------------------------------------------------------

# REALTIME

Support

Live Queue

Live Progress

Worker Status

Job Completion

Failures

Retries

Queue Changes

WebSocket if backend supports.

Otherwise polling.

------------------------------------------------------------------------------

# API INTEGRATION

Reuse existing backend.

Integrate

Processing APIs

Queue APIs

Worker APIs

Evidence APIs

AI APIs

Knowledge Graph APIs

Timeline APIs

Audit APIs

Workspace APIs

No duplicate logic.

------------------------------------------------------------------------------

# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

Queue Store

Worker Store

History Store

Filter Store

Progress Store

No duplicated state.

------------------------------------------------------------------------------

# LOADING

Queue Skeleton

Worker Skeleton

Progress Skeleton

History Skeleton

Analytics Skeleton

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

Queue Offline

Worker Offline

Retry Failed

Cancel Failed

------------------------------------------------------------------------------

# EMPTY STATES

No Queue

No Jobs

No Workers

No Failed Jobs

No History

Backend Offline

------------------------------------------------------------------------------

# PERFORMANCE

Virtualized Tables

Infinite Scroll

Lazy Logs

Memoization

Streaming Updates

Optimistic UI

Background Refresh

Large Dataset Support

------------------------------------------------------------------------------

# SECURITY

Respect backend RBAC.

Investigators

View queue

Administrators

Manage workers

Retry jobs

Cancel jobs

Never expose unauthorized jobs.

------------------------------------------------------------------------------

# AUDIT

Every action

Retry Job

Cancel Job

View Logs

Export

Open Job

Worker Actions

Must generate backend audit entries.

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2 AA

Keyboard Navigation

ARIA

Screen Readers

Accessible Progress Bars

Accessible Tables

------------------------------------------------------------------------------

# RESPONSIVE

Desktop

Laptop

Tablet

Enterprise Layout

No mobile redesign.

------------------------------------------------------------------------------

# VALIDATION

Verify

✓ Queue displays backend jobs

✓ Worker status updates correctly

✓ Progress updates live

✓ Retry works

✓ Cancel works

✓ History loads

✓ Analytics display correctly

✓ Logs load correctly

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

Processing Queue Architecture

2.

Queue Workflow

3.

Worker Monitoring Workflow

4.

Processing Pipeline Visualization

5.

Backend API Mapping

6.

Component Hierarchy

7.

State Management Flow

8.

Realtime Update Strategy

9.

Retry & Cancel Flow

10.

Queue Analytics Flow

11.

Files Created

12.

Files Modified

13.

Files Reused

14.

Performance Report

15.

Security Report

16.

Accessibility Report

17.

Enterprise Processing Queue Validation Report

18.

Processing Queue Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

Do NOT implement

Reports

Compliance

Administration

Settings

Stop immediately after the Enterprise Processing Queue module is fully integrated with the backend and all validation criteria pass.

Only after successful completion should Phase 12 (Enterprise Reports & Court Documentation) begin.