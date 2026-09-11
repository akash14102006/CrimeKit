# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 6 — Enterprise Investigation Workspace (Flagship Module)
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 6

Objective:

Develop ONLY the Enterprise Investigation Workspace.

This is the MOST IMPORTANT page in the entire CrimeKit platform.

It is the page investigators, forensic analysts, cyber teams, supervisors and judges will spend nearly all of their time using.

This page must feel comparable to:

• Palantir Gotham Investigation Workspace
• IBM i2 Analyst Notebook
• Magnet AXIOM Examine
• Cellebrite Pathfinder
• Nuix Investigate
• Microsoft Defender XDR Investigation
• Elastic Security Investigation Timeline

This is NOT a dashboard.

This is NOT a CRUD page.

This is NOT a redesign.

It is a unified investigation cockpit powered entirely by the existing CrimeKit backend.

NO mock data.

NO fake APIs.

NO placeholder components.

Everything MUST integrate with the existing backend.

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Frontend Architect

Principal UX Architect

Principal Investigation Platform Architect

Principal Digital Forensics Architect

Principal React Architect

Principal Next.js Architect

Principal Product Designer

Senior AI UX Engineer

Senior Security UX Engineer

------------------------------------------------------------------------------

# SOURCE OF TRUTH

Before writing ANY code, perform COMPLETE project discovery.

Priority

1.
graphify-out/

- graph.json
- GRAPH_REPORT.md

2.
Planning/

- Workspace Planning
- Investigation Workflow
- Evidence Workflow
- AI Workflow
- Timeline Workflow
- KG Workflow

3.
Architecture/

4.
Design/

5.
Frontend Constitution

6.
Backend Constitution

7.
Workspace APIs

8.
Evidence APIs

9.
Chain of Custody APIs

10.
Timeline APIs

11.
Knowledge Graph APIs

12.
AI APIs

13.
Processing APIs

14.
Search APIs

15.
Compliance APIs

16.
OpenAPI

17.
Backend Models

18.
Existing Frontend

19.
Existing Components

20.
Existing Design System

Read everything.

Never guess.

Never redesign.

Reuse existing frontend.

Reuse existing layouts.

Reuse existing design system.

------------------------------------------------------------------------------

# IMPORTANT RULES

DO NOT

Redesign

Change colors

Change typography

Change spacing

Change navigation

Replace layouts

Invent APIs

Create mock data

Create placeholder AI

Duplicate backend logic

Duplicate state

Duplicate components

Everything must reuse the existing frontend architecture.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY

Enterprise Investigation Workspace

Do NOT develop

Dashboard

Authentication

Case Management

Reports

Administration

Settings

Compliance

AI Chat

Only Workspace.

------------------------------------------------------------------------------

# WORKSPACE PURPOSE

The Investigation Workspace is the single screen where investigators solve an entire case.

Everything must be visible together.

Instead of switching pages,

the investigator should investigate from one unified workspace.

Workspace

↓

Case Overview

↓

Evidence

↓

Timeline

↓

AI Findings

↓

Knowledge Graph

↓

Chain of Custody

↓

Processing Status

↓

Related Cases

↓

Risk Indicators

↓

Quick Actions

Everything synchronized.

------------------------------------------------------------------------------

# LAYOUT

Maintain existing design.

Suggested enterprise layout

Header

↓

Breadcrumb

↓

Case Summary Bar

↓

Resizable Multi-Panel Workspace

Left Panel

Evidence Explorer

Center Panel

Investigation Canvas

Right Panel

AI + Processing + Risk

Bottom Panel

Timeline + Custody + Activity

Panels must support

Resize

Collapse

Expand

Remember Layout

Keyboard Shortcuts

Fullscreen

------------------------------------------------------------------------------

# CASE SUMMARY BAR

Display

Case Number

Title

Priority

Status

Assigned Investigator

Organization

Department

Evidence Count

Processing Status

AI Findings Count

Timeline Events

Knowledge Graph Status

Compliance Status

Storage Usage

Last Updated

Everything from backend.

------------------------------------------------------------------------------

# EVIDENCE EXPLORER

Backend only.

Display

Folders

Evidence Tree

Categories

Images

Videos

Documents

Audio

Emails

Archives

Disk Images

Memory Dumps

Mobile Artifacts

Browser Artifacts

Network Captures

Support

Search

Filter

Sorting

Preview

Selection

Multi-selection

Context Menu

Pinned Evidence

Favorites

Recently Viewed

------------------------------------------------------------------------------

# EVIDENCE DETAILS PANEL

Display

Filename

Metadata

Hashes

Integrity

Size

Category

MIME

Uploaded By

Upload Date

Processing Status

AI Status

Knowledge Graph Status

Chain of Custody Status

Preview

Quick Actions

------------------------------------------------------------------------------

# TIMELINE

Enterprise investigation timeline.

Integrate backend.

Display

Evidence Events

Custody Events

Processing Events

AI Events

Knowledge Graph Events

Investigator Activity

Reports

System Events

Filters

Zoom

Grouping

Date Range

Search

Highlight

------------------------------------------------------------------------------

# AI FINDINGS PANEL

Backend AI only.

Display

Summary

Entities

Relationships

Timeline Events

Anomalies

Risk Score

Confidence

Correlations

Suggested Leads

Similar Evidence

Related Cases

Supporting Evidence

Processing Confidence

Never generate AI locally.

------------------------------------------------------------------------------

# KNOWLEDGE GRAPH PANEL

Integrate backend.

Display

Entities

Relationships

Evidence Links

People

Devices

Locations

Organizations

Timeline Links

Interactive Graph

Zoom

Search

Highlight

Expand

Collapse

Context Menu

Only visualize backend graph.

------------------------------------------------------------------------------

# CHAIN OF CUSTODY

Backend only.

Display

Chronological Events

Transfers

Owners

Signatures

Verification

Integrity Checks

Location

Timestamp

Status

Search

Filters

Export

Never edit in frontend.

------------------------------------------------------------------------------

# PROCESSING PANEL

Integrate backend.

Display

Queue Status

Current Processor

Progress

Completed Processors

Remaining

Worker

Retry Count

Duration

Logs Summary

Processor Results

Supported processors

OCR

Metadata

Image Analysis

Video Analysis

PDF

Office

Email

Archive

Mobile

Memory

Network

Browser

------------------------------------------------------------------------------

# RELATED CASES

Backend only.

Display

Case Number

Similarity Score

Shared Evidence

Shared Entities

Shared Devices

Shared Locations

Shared People

Shared Timeline

AI Correlation

Open Case

Compare

------------------------------------------------------------------------------

# RISK INDICATORS

Display

Integrity Failure

Missing Custody

Processing Failure

Hash Mismatch

AI Confidence Low

Missing Metadata

Compliance Risk

Storage Risk

Duplicate Evidence

High Priority Alerts

Risk colors must follow existing design system.

------------------------------------------------------------------------------

# QUICK ACTIONS

Backend integrated.

Upload Evidence

Run Processing

Run AI

View KG

Generate Report

Assign Investigator

Verify Integrity

Open Timeline

Open Evidence

Open Related Case

Only show permitted actions.

------------------------------------------------------------------------------

# GLOBAL SEARCH

Workspace-wide search.

Backend only.

Support

Evidence

Metadata

Timeline

Entities

Cases

Processing

Custody

AI Findings

------------------------------------------------------------------------------

# FILTERS

Evidence Type

Date

Category

Processing Status

Integrity

Investigator

Entity

Timeline

AI Confidence

Risk Level

Backend filtering only.

------------------------------------------------------------------------------

# REALTIME

Support

Polling

WebSocket (if backend supports)

Auto Refresh

Manual Refresh

Background Updates

Cache Invalidation

------------------------------------------------------------------------------

# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

Workspace Store

Panel State

Selection State

Timeline State

Graph State

Filter State

No duplicated state.

------------------------------------------------------------------------------

# API INTEGRATION

Reuse existing API client.

Integrate ONLY existing backend endpoints.

Workspace APIs

Evidence APIs

Timeline APIs

KG APIs

AI APIs

Processing APIs

Custody APIs

Related Cases APIs

Health APIs

Search APIs

------------------------------------------------------------------------------

# LOADING

Independent loading.

Evidence Skeleton

Timeline Skeleton

AI Skeleton

Graph Skeleton

Processing Skeleton

Custody Skeleton

Risk Skeleton

No full-page blocking.

------------------------------------------------------------------------------

# ERROR HANDLING

Handle

401

403

404

409

422

429

500

503

Timeout

Offline

Retry

Each panel isolated.

------------------------------------------------------------------------------

# EMPTY STATES

No Evidence

No Timeline

No AI Findings

No Related Cases

No Risks

No Processing

No Graph

Guide investigators.

------------------------------------------------------------------------------

# PERFORMANCE

Server Components

Streaming

Suspense

Virtualization

Memoization

Code Splitting

Lazy Loading

Prefetch

Graph Virtualization

Large Timeline Optimization

Large Evidence Optimization

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2 AA

Keyboard Navigation

ARIA

Screen Reader

Focus Management

High Contrast

Reduced Motion

Resizable Panels Accessible

------------------------------------------------------------------------------

# RESPONSIVE

Desktop

Laptop

Large Monitor

Ultra-wide

Tablet (read-only optimized)

Maintain enterprise layout.

------------------------------------------------------------------------------

# SECURITY

Respect backend RBAC.

Never expose

Hidden Evidence

Hidden Cases

Hidden AI

Hidden KG

Hidden Custody

Restricted Processing

Other Organizations

------------------------------------------------------------------------------

# AUDIT

Every workspace action

Open Evidence

Preview

Run AI

Run Processing

Open Timeline

Open KG

Verify Integrity

Generate Report

Must call backend audit endpoints.

------------------------------------------------------------------------------

# VALIDATION

Verify

✓ Workspace loads

✓ Evidence explorer works

✓ Timeline works

✓ AI Findings work

✓ Knowledge Graph works

✓ Chain of Custody works

✓ Processing panel works

✓ Related Cases work

✓ Risk Indicators work

✓ Search works

✓ Filters work

✓ Quick Actions work

✓ Resizable panels work

✓ Layout persistence works

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

Workspace Architecture

2.

Panel Architecture Diagram

3.

Workspace Data Flow

4.

Backend API Mapping

5.

Component Hierarchy

6.

Evidence Flow

7.

Timeline Flow

8.

AI Flow

9.

Knowledge Graph Flow

10.

Chain of Custody Flow

11.

Risk Analysis Flow

12.

State Management Flow

13.

Files Created

14.

Files Modified

15.

Files Reused

16.

Performance Report

17.

Security Report

18.

Accessibility Report

19.

Workspace Validation Report

20.

Workspace Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

Do NOT implement

Reports

Administration

Compliance

Settings

AI Chat

Stop immediately after the Enterprise Investigation Workspace is fully integrated with the existing backend and every validation criterion passes.

Only after successful completion should Phase 7 (Enterprise Knowledge Graph & Timeline Experience) begin.