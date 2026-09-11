# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 3 — Executive Dashboard
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 3

Objective:

Develop ONLY the Enterprise Dashboard.

The dashboard is the command center of CrimeKit.

It must provide investigators, forensic analysts, administrators, supervisors, and judges with a real-time overview of the entire investigation ecosystem.

This is NOT a UI redesign.

This is NOT a prototype.

This is NOT a demo dashboard.

This is a production-grade enterprise dashboard similar to:

• Microsoft Defender XDR

• CrowdStrike Falcon

• SentinelOne

• IBM i2 Analyst Notebook

• Magnet Axiom

• Cellebrite Pathfinder

• Splunk Enterprise Security

• Azure Security Center

• Elastic Security

Everything MUST integrate with the existing enterprise backend.

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Frontend Architect

Principal Product Designer

Principal Dashboard Architect

Principal UX Engineer

Staff React Engineer

Staff Next.js Engineer

Enterprise Design System Architect

Senior Security Product Designer

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

3.

Frontend Planning

4.

Dashboard Planning

5.

Design Bible

6.

Design System

7.

Architecture

8.

Backend OpenAPI

9.

Backend Routes

10.

Backend Schemas

11.

Backend Workspace Module

12.

Evidence APIs

13.

Case APIs

14.

Processing APIs

15.

AI APIs

16.

Knowledge Graph APIs

17.

Audit APIs

18.

Metrics APIs

19.

Health APIs

20.

Existing frontend

Never guess.

Never invent APIs.

Never redesign UI.

Reuse existing frontend.

------------------------------------------------------------------------------

# IMPORTANT

DO NOT

Create mock data

Create fake charts

Create fake KPIs

Create placeholder cards

Use local JSON

Use dummy arrays

Create random statistics

Every number MUST come from backend APIs.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY Dashboard.

NO

Workspace

Evidence Viewer

Timeline

Knowledge Graph

Reports

Compliance

Settings

Administration

AI Chat

Case Details

Only Dashboard.

------------------------------------------------------------------------------

# DASHBOARD PURPOSE

The dashboard is the first screen after login.

It answers immediately:

How many active investigations exist?

How much evidence is waiting?

Are forensic jobs healthy?

Any AI alerts?

Any chain-of-custody risks?

Any failed processing?

System health?

Recent activity?

Investigator productivity?

------------------------------------------------------------------------------

# LAYOUT

Reuse the existing design.

Do NOT redesign.

Maintain:

Spacing

Typography

Cards

Colors

Icons

Navigation

Animations

Dashboard Sections

Header

↓

Global Search

↓

Quick Actions

↓

Executive KPI Row

↓

Operational Metrics

↓

Investigation Overview

↓

Processing Overview

↓

AI Intelligence

↓

Evidence Overview

↓

System Health

↓

Activity Feed

------------------------------------------------------------------------------

# HEADER

Implement

Dynamic greeting

Current investigator

Current organization

Current project

Breadcrumb

Global search shortcut

Notifications

Profile

Quick command

Real backend session.

------------------------------------------------------------------------------

# KPI ROW

Integrate backend.

Display

Total Cases

Active Cases

Evidence Count

Processing Queue

Completed Jobs

Pending Jobs

Critical Alerts

AI Findings

Storage Usage

Connected Investigators

Never hardcode.

Support

Loading

Error

Empty

Realtime updates

------------------------------------------------------------------------------

# ACTIVE CASES

Backend integration.

Show

Case Number

Title

Priority

Status

Assigned Investigator

Evidence Count

Last Activity

Quick Open

Filters

Sorting

Search

Pagination

RBAC

------------------------------------------------------------------------------

# RECENT EVIDENCE

Backend integration.

Display

Evidence Name

Type

Hash

Status

Upload Time

Owner

Integrity

Chain of Custody

Processing Status

Quick View

Download

------------------------------------------------------------------------------

# AI ALERTS

Integrate backend AI.

Display

Critical Findings

Suspicious Correlations

Anomalies

Risk Score

Suggested Investigation

Related Case

Confidence

Source

Status

------------------------------------------------------------------------------

# PROCESSING QUEUE

Real backend.

Show

Queued

Running

Completed

Failed

Cancelled

Average Time

Worker Utilization

Retry Queue

Job Progress

Live updates.

------------------------------------------------------------------------------

# SYSTEM HEALTH

Integrate

Health API

Metrics API

Prometheus

Infrastructure

Display

Backend

Database

Redis

Neo4j

MinIO

Queue

AI Pipeline

Workers

Storage

CPU

Memory

Disk

Status indicators.

------------------------------------------------------------------------------

# ACTIVITY FEED

Real audit events.

Display

Evidence Upload

Case Created

Case Updated

User Login

Processing Started

Processing Finished

AI Completed

KG Updated

Report Generated

Role Changed

Compliance Event

Newest first.

Realtime.

------------------------------------------------------------------------------

# QUICK ACTIONS

Reuse backend.

Actions

New Case

Upload Evidence

Search

Open Workspace

Run AI

Generate Report

Create Investigation

Invite Investigator

Only if RBAC permits.

------------------------------------------------------------------------------

# CHARTS

Use ONLY backend metrics.

Possible charts

Case Trend

Evidence Growth

Processing Trend

AI Findings

Queue Throughput

Storage Usage

Investigator Productivity

No fake chart data.

------------------------------------------------------------------------------

# SEARCH

Global dashboard search.

Integrate backend.

Support

Cases

Evidence

Investigators

Timeline

Knowledge Graph

Reports

AI Findings

Search suggestions.

------------------------------------------------------------------------------

# FILTERS

Global filters.

Date

Case Status

Investigator

Priority

Organization

Evidence Type

Department

------------------------------------------------------------------------------

# RBAC

Everything must obey backend permissions.

Hide

Buttons

Cards

Widgets

Metrics

Charts

Actions

Menus

Routes

Never expose unauthorized information.

------------------------------------------------------------------------------

# REALTIME

Support

Polling

WebSocket if backend exists

Automatic refresh

Manual refresh

Cache invalidation

Optimistic updates

------------------------------------------------------------------------------

# STATE

Use

TanStack Query

Zustand

Existing stores

No duplicate state.

------------------------------------------------------------------------------

# API INTEGRATION

Use existing API client.

No duplicate axios.

Reuse

Interceptors

Refresh

Retry

Timeout

Typed responses

------------------------------------------------------------------------------

# LOADING

Every widget

Skeleton

Progress

Partial loading

Independent loading

No full-page blocking.

------------------------------------------------------------------------------

# ERROR

Each widget

Own error state.

Retry

Refresh

Error boundary.

------------------------------------------------------------------------------

# EMPTY

Enterprise empty states.

No blank widgets.

Guide investigator.

------------------------------------------------------------------------------

# PERFORMANCE

Streaming

Server Components

Lazy Loading

Dynamic Imports

Suspense

Virtualization

Memoization

Prefetch

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2

Keyboard

ARIA

Focus

Screen Reader

Contrast

Reduced Motion

------------------------------------------------------------------------------

# RESPONSIVE

Desktop

Laptop

Tablet

Large Monitor

Ultra-wide

Maintain enterprise layout.

------------------------------------------------------------------------------

# SECURITY

Never expose

Hidden metrics

Unauthorized cases

Unauthorized AI findings

Unauthorized reports

Unauthorized system health

Respect backend RBAC.

------------------------------------------------------------------------------

# VALIDATION

Verify

✓ Dashboard loads

✓ All cards use backend

✓ No mock data

✓ Charts use backend

✓ Activity uses backend

✓ Health uses backend

✓ Queue uses backend

✓ AI alerts use backend

✓ Recent evidence uses backend

✓ Cases use backend

✓ RBAC works

✓ Search works

✓ Filters work

✓ Loading works

✓ Errors handled

✓ Empty states implemented

✓ No runtime errors

✓ No TypeScript errors

✓ No ESLint errors

✓ Existing design preserved

✓ Existing frontend reused

✓ Production ready

------------------------------------------------------------------------------

# DELIVERABLES

Produce

1.

Dashboard Architecture

2.

Dashboard Widget Map

3.

API Mapping

4.

Backend Endpoint Mapping

5.

Component Tree

6.

State Flow

7.

Files Created

8.

Files Modified

9.

Files Reused

10.

Performance Report

11.

Security Report

12.

Accessibility Report

13.

Dashboard Validation Report

14.

Dashboard Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

DO NOT implement

Workspace

Evidence

Timeline

Knowledge Graph

Reports

AI Chat

Compliance

Settings

Administration

Stop immediately after the Dashboard is completely integrated with the backend and all acceptance criteria pass.

Only then should Phase 4 (Case Management) begin.