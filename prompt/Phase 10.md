# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 10 — Enterprise Search & Investigation Discovery Platform
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 10

Objective:

Develop ONLY the Enterprise Search & Investigation Discovery Platform.

This is NOT a normal search bar.

This is a unified intelligence search engine capable of searching the entire CrimeKit platform.

Everything must integrate with the existing backend.

Search must combine:

• PostgreSQL
• AI Pipeline
• Vector Database
• Neo4j Knowledge Graph
• OCR Results
• Evidence Metadata
• Timeline
• Cases
• Chain of Custody
• Processing Results
• Reports

There must NEVER be frontend searching over local data.

Every search request must use backend APIs.

NO mock search.

NO fake indexing.

NO local filtering for enterprise datasets.

Comparable systems:

• Elastic Security
• Splunk Enterprise Search
• Microsoft Sentinel Search
• Google Chronicle
• IBM QRadar
• Palantir Search
• Datadog Search
• Kibana Discovery
• Magnet AXIOM Search

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Search Architect

Principal Frontend Architect

Principal UX Architect

Principal React Architect

Principal Next.js Architect

Principal Enterprise Search Engineer

Principal AI Search Engineer

Principal Product Designer

Senior Information Retrieval Engineer

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

Search Planning

AI Planning

Workspace Planning

Knowledge Graph Planning

Timeline Planning

Evidence Planning

3.

Architecture/

4.

Search Constitution

5.

Frontend Constitution

6.

Backend Constitution

7.

Search APIs

8.

AI APIs

9.

Evidence APIs

10.

Knowledge Graph APIs

11.

Timeline APIs

12.

Workspace APIs

13.

Compliance APIs

14.

Reports APIs

15.

OpenAPI

16.

Existing Frontend

17.

Existing Components

18.

Existing Providers

19.

Existing Design System

Never redesign.

Never invent APIs.

Reuse existing architecture.

------------------------------------------------------------------------------

# IMPORTANT

DO NOT

Create local search

Create mock search

Create frontend OCR

Create fake semantic search

Implement vector search locally

Duplicate backend filtering

Duplicate AI

Everything MUST come from backend.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY

Enterprise Search Platform

Includes

✓ Global Search

✓ Semantic Search

✓ OCR Search

✓ Metadata Search

✓ Timeline Search

✓ Knowledge Graph Search

✓ Saved Searches

✓ Search History

✓ Advanced Filters

✓ Search Insights

✓ Search Suggestions

✓ Search Analytics

Nothing else.

------------------------------------------------------------------------------

# SEARCH PURPOSE

CrimeKit Search should allow investigators to search EVERYTHING from one place.

One query

↓

Cases

↓

Evidence

↓

OCR

↓

Metadata

↓

Timeline

↓

Knowledge Graph

↓

Entities

↓

Processing Results

↓

AI Findings

↓

Reports

↓

Compliance

↓

Audit Logs

Unified results.

------------------------------------------------------------------------------

# PAGE LAYOUT

Reuse existing design.

Layout

Header

↓

Universal Search Bar

↓

Search Suggestions

↓

Advanced Filters

↓

Search Tabs

↓

Search Results

↓

Preview Panel

↓

Evidence Preview

↓

Timeline Preview

↓

Knowledge Graph Preview

↓

Search Analytics

------------------------------------------------------------------------------

# GLOBAL SEARCH

Backend only.

Search across

Cases

Evidence

People

Organizations

Devices

Emails

URLs

Hashes

Processes

Timeline

Reports

Knowledge Graph

AI Findings

Chain of Custody

Processing

Compliance

Audit

Everything.

------------------------------------------------------------------------------

# SEMANTIC SEARCH

Use backend vector search.

Support

Natural Language

Questions

Concept Search

Meaning Search

Intent Search

Similar Documents

Similar Evidence

Related Investigations

Relevant AI Findings

Related Cases

No frontend embeddings.

------------------------------------------------------------------------------

# OCR SEARCH

Backend OCR only.

Support

Scanned PDF

Images

Screenshots

Photos

Passports

Invoices

Handwriting (if supported)

Search extracted text.

Highlight matches.

------------------------------------------------------------------------------

# METADATA SEARCH

Backend only.

Search

Filename

Extension

MIME

Hash

EXIF

GPS

Camera

Author

Company

Subject

Created

Modified

Software

Device

Browser

Registry

Network

Everything indexed by backend.

------------------------------------------------------------------------------

# TIMELINE SEARCH

Search

Events

Dates

Actions

Evidence

Investigators

Processing

AI Events

Custody Events

Reports

Jump directly to timeline.

------------------------------------------------------------------------------

# KNOWLEDGE GRAPH SEARCH

Search backend graph.

Support

Entities

Relationships

Communities

Nodes

Evidence Links

Cases

Devices

People

Organizations

URLs

Processes

Highlight graph.

Open graph workspace.

------------------------------------------------------------------------------

# SEARCH RESULTS

Categorized results

Cases

Evidence

Timeline

Knowledge Graph

Entities

AI Findings

Reports

Compliance

Processing

Audit

Each result

Title

Description

Snippet

Highlight

Confidence

Relevance

Last Updated

Quick Actions

------------------------------------------------------------------------------

# SEARCH PREVIEW

Preview

Evidence

Metadata

OCR

Timeline

Entity

Graph

Report

Without leaving search.

------------------------------------------------------------------------------

# SEARCH SUGGESTIONS

Backend only.

Support

Autocomplete

Recent Searches

Popular Searches

Suggested Investigations

Suggested Entities

Suggested Cases

Suggested Evidence

------------------------------------------------------------------------------

# ADVANCED FILTERS

Backend filters.

Support

Case

Evidence Type

File Type

Date Range

Timeline

Entity Type

Risk

Priority

Confidence

AI

Organization

Department

Hash

Metadata

Processing Status

Knowledge Graph

Compliance

Multiple filters.

------------------------------------------------------------------------------

# SAVED SEARCHES

Support

Create

Rename

Delete

Favorite

Pin

Share

Execute

Backend persistence.

------------------------------------------------------------------------------

# SEARCH HISTORY

Display

Recent Searches

Pinned Searches

Most Used

Last Executed

Frequency

Backend history.

------------------------------------------------------------------------------

# SEARCH ANALYTICS

Display

Result Count

Search Time

Indexed Sources

Matched Categories

AI Confidence

Semantic Confidence

Graph Matches

Timeline Matches

------------------------------------------------------------------------------

# QUICK ACTIONS

Open Case

Open Evidence

Open Timeline

Open Graph

Run AI

Generate Report

Copy Hash

Verify Integrity

Open Workspace

------------------------------------------------------------------------------

# EXPORT

Backend only.

Export

CSV

JSON

PDF

Excel

Saved Search

Search Report

Investigation Package

------------------------------------------------------------------------------

# REALTIME

Support

Live Suggestions

Incremental Results

Streaming Search

Polling

WebSocket (if backend supports)

Search Cancellation

------------------------------------------------------------------------------

# API INTEGRATION

Reuse existing API layer.

Integrate

Search APIs

AI APIs

Vector Search APIs

OCR APIs

Knowledge Graph APIs

Timeline APIs

Evidence APIs

Workspace APIs

Processing APIs

Report APIs

------------------------------------------------------------------------------

# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

Search Store

Filter Store

History Store

Suggestion Store

Result Store

No duplicated state.

------------------------------------------------------------------------------

# LOADING

Search Skeleton

Suggestion Skeleton

Preview Skeleton

Analytics Skeleton

Progressive rendering.

------------------------------------------------------------------------------

# ERROR HANDLING

Handle

401

403

404

429

500

503

Timeout

Search Cancelled

Backend Offline

Retry

------------------------------------------------------------------------------

# EMPTY STATES

No Results

No Suggestions

No History

No Saved Searches

No Permission

Backend Offline

------------------------------------------------------------------------------

# PERFORMANCE

Streaming Search

Virtualized Results

Incremental Loading

Lazy Preview

Memoization

Infinite Scroll

Large Dataset Optimization

Debounced Search

Cancelable Requests

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2 AA

Keyboard Navigation

ARIA

Screen Reader

Accessible Search

Accessible Filters

High Contrast

Reduced Motion

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

Hidden Cases

Hidden Evidence

Restricted Entities

Private Reports

Other Organizations

Unauthorized Search Results

------------------------------------------------------------------------------

# AUDIT

Every search action

Search Query

Open Result

Export

Save Search

Delete Search

Run Semantic Search

Must call backend audit APIs.

------------------------------------------------------------------------------

# VALIDATION

Verify

✓ Global Search works

✓ Semantic Search works

✓ OCR Search works

✓ Metadata Search works

✓ Timeline Search works

✓ Knowledge Graph Search works

✓ Search Suggestions work

✓ Saved Searches work

✓ Search History works

✓ Search Analytics work

✓ Preview works

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

Enterprise Search Architecture

2.

Unified Search Flow

3.

Backend API Mapping

4.

Component Hierarchy

5.

Semantic Search Flow

6.

OCR Search Flow

7.

Knowledge Graph Search Flow

8.

Timeline Search Flow

9.

Search Analytics Flow

10.

Files Created

11.

Files Modified

12.

Files Reused

13.

Performance Report

14.

Security Report

15.

Accessibility Report

16.

Enterprise Search Validation Report

17.

Enterprise Search Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

Do NOT implement

Reports

Compliance

Administration

Settings

Stop immediately after the Enterprise Search Platform is fully integrated with the existing backend search ecosystem and every validation criterion passes.

Only after successful completion should Phase 11 (Enterprise Reporting & Court Documentation) begin.