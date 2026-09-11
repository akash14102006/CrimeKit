# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 5 — Enterprise Evidence Management
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 5

Objective:

Develop ONLY the Enterprise Evidence Management module.

This is NOT a simple file uploader.

This is a complete Digital Evidence Management System comparable to:

• Magnet AXIOM
• Cellebrite Pathfinder
• Nuix
• FTK
• EnCase
• IBM i2
• Palantir Gotham

Everything MUST integrate with the existing CrimeKit enterprise backend.

NO mock uploads.

NO fake evidence.

NO local JSON.

NO placeholder APIs.

Everything must use existing backend APIs.

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Frontend Architect

Principal Forensic Software Architect

Principal UX Architect

Principal Digital Evidence Engineer

Principal React Engineer

Principal Next.js Engineer

Enterprise Product Designer

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

Evidence Planning

3.

Architecture/

4.

Evidence Constitution

5.

Frontend Constitution

6.

Backend Constitution

7.

OpenAPI

8.

Evidence APIs

9.

Chain of Custody APIs

10.

Processing APIs

11.

Storage APIs

12.

AI APIs

13.

Workspace APIs

14.

Search APIs

15.

Audit APIs

16.

Existing frontend

17.

Existing components

18.

Existing providers

19.

Existing API client

20.

Existing design system

Never guess.

Never redesign.

Reuse existing architecture.

------------------------------------------------------------------------------

# IMPORTANT

DO NOT

Create fake uploads

Create fake evidence

Create local storage

Create mock metadata

Create placeholder hashes

Generate fake integrity

Create duplicate upload logic

Duplicate API layer

Everything must come from backend.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY

Enterprise Evidence Module

Includes

✓ Evidence Upload

✓ Drag & Drop Upload

✓ Upload Queue

✓ Upload Progress

✓ Resume Upload

✓ Retry Upload

✓ Cancel Upload

✓ Evidence Details

✓ Metadata Viewer

✓ Hash Viewer

✓ Integrity Status

✓ Preview Support

✓ File Information

✓ Processing Status

✓ Chain of Custody Summary

✓ RBAC

Nothing else.

------------------------------------------------------------------------------

# EVIDENCE WORKFLOW

Enterprise workflow

Select Files

↓

Validate

↓

Calculate Client Metadata (only if backend requires)

↓

Upload

↓

Progress

↓

Resume / Retry

↓

Backend Storage

↓

Hash Verification

↓

Processing Queue

↓

AI Pipeline

↓

Knowledge Graph

↓

Evidence Ready

Everything must follow backend workflow.

------------------------------------------------------------------------------

# PAGE STRUCTURE

Evidence List

↓

Toolbar

↓

Upload Button

↓

Drag & Drop Area

↓

Search

↓

Filters

↓

Evidence Grid/Table

↓

Details Panel

↓

Metadata Panel

↓

Integrity Panel

↓

Processing Status

------------------------------------------------------------------------------

# EVIDENCE LIST

Integrate backend.

Display

Evidence ID

Filename

Original Filename

Extension

MIME Type

Size

Category

Uploaded By

Upload Date

Case

Status

Processing Status

Integrity Status

Hash Status

AI Status

Knowledge Graph Status

Chain of Custody Status

Storage Location

Thumbnail

Quick Actions

------------------------------------------------------------------------------

# EVIDENCE UPLOAD

Enterprise uploader.

Support

Single Upload

Multi Upload

Folder Upload

Large Files

Very Large Files

Chunk Upload

Streaming Upload

Pause

Resume

Retry

Cancel

Duplicate Detection

Drag & Drop

Browse

Clipboard Paste

File Validation

Progress

ETA

Transfer Speed

Remaining Time

Upload Queue

Parallel Upload

Sequential Upload

Upload History

Everything integrated with backend.

------------------------------------------------------------------------------

# DRAG & DROP

Support

Desktop

Folders

Multiple Files

Nested Folders (if backend supports)

Visual Drop Zone

Highlight

Keyboard Alternative

Accessibility

------------------------------------------------------------------------------

# UPLOAD VALIDATION

Validate

Maximum Size

Allowed Extensions

Allowed MIME

Duplicate Files

Corrupted Files

Permission

Case Assignment

Backend validation only.

------------------------------------------------------------------------------

# UPLOAD PROGRESS

Per File

Global Queue

Display

Progress %

Speed

ETA

Uploaded Bytes

Remaining Bytes

Status

Queued

Uploading

Paused

Retrying

Completed

Failed

Cancelled

------------------------------------------------------------------------------

# RESUME

Integrate backend.

Support

Interrupted Upload

Browser Refresh

Network Disconnect

Resume Token

Chunk Resume

Background Resume

No fake implementation.

------------------------------------------------------------------------------

# RETRY

Support

Automatic Retry

Manual Retry

Retry Count

Retry Delay

Exponential Backoff

Failure Reason

------------------------------------------------------------------------------

# CANCEL

Allow

Single Upload

Queue

Confirmation

Cleanup

Backend cancellation

------------------------------------------------------------------------------

# EVIDENCE DETAILS

Dedicated page

Display

Evidence ID

Filename

Original Name

Extension

Category

Description

Uploaded By

Created

Modified

Case

Tags

Labels

Comments

Current Owner

Storage Information

------------------------------------------------------------------------------

# METADATA VIEWER

Integrate backend.

Display

General Metadata

File System Metadata

EXIF Metadata

Document Metadata

Email Metadata

Video Metadata

Audio Metadata

Image Metadata

Archive Metadata

Mobile Metadata

Browser Metadata

Memory Metadata

Network Metadata

Structured Tree View

Search

Copy

Expand

Collapse

------------------------------------------------------------------------------

# HASH VIEWER

Display

SHA256

SHA1

MD5

Hash Length

Hash Verification

Copy

Compare

Integrity Timestamp

Hash Status

------------------------------------------------------------------------------

# INTEGRITY STATUS

Backend only.

Display

Verified

Modified

Corrupted

Pending

Unknown

Visual Indicators

Timeline

Verification Date

Last Checked

------------------------------------------------------------------------------

# FILE PREVIEW

Support backend preview.

Images

PDF

Text

JSON

Audio

Video

Office

Email

If unsupported

Display appropriate placeholder

Never parse unsupported files in frontend.

------------------------------------------------------------------------------

# PROCESSING STATUS

Integrate backend.

Display

Queued

Running

Completed

Failed

Cancelled

Current Processor

Progress

Started

Finished

Elapsed

Worker

Retry Count

------------------------------------------------------------------------------

# CHAIN OF CUSTODY SUMMARY

Display

Current Owner

Previous Owner

Transfers

Evidence Movement

Latest Event

Verification

Open Full Custody

Backend only.

------------------------------------------------------------------------------

# SEARCH

Backend Search

Filename

Hash

Uploader

Evidence ID

Metadata

Tags

Labels

Case

Category

------------------------------------------------------------------------------

# FILTERS

Backend filters

Type

Category

Processing Status

Integrity

Uploader

Date

Case

AI Status

Knowledge Graph Status

Storage

------------------------------------------------------------------------------

# QUICK ACTIONS

View

Download

Copy Hash

Open Workspace

Processing

AI Analysis

Knowledge Graph

Timeline

Chain of Custody

Delete (RBAC)

------------------------------------------------------------------------------

# BULK ACTIONS

Upload

Delete

Export

Assign

Move

Reprocess

Generate Report

Verify Integrity

RBAC controlled.

------------------------------------------------------------------------------

# API INTEGRATION

Reuse existing API client.

Support

AbortController

Chunk Upload

Retry

Timeout

Streaming

Progress Events

Typed Responses

No duplicate axios.

------------------------------------------------------------------------------

# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

Upload Queue Store

Evidence Cache

Filter State

Selection State

No duplicate logic.

------------------------------------------------------------------------------

# LOADING

Upload Skeleton

Evidence Skeleton

Metadata Skeleton

Hash Skeleton

Preview Skeleton

Independent loading.

------------------------------------------------------------------------------

# ERROR HANDLING

Support

Upload Failed

Chunk Failed

Hash Failed

Metadata Failed

Storage Offline

Network

Timeout

Permission

Unsupported File

Quota Exceeded

Retry

------------------------------------------------------------------------------

# EMPTY STATES

No Evidence

No Uploads

No Search Results

No Metadata

No Preview

No Permission

------------------------------------------------------------------------------

# PERFORMANCE

Streaming Upload

Virtualized List

Lazy Preview

Progressive Loading

Memoization

Request Deduplication

Image Optimization

Chunk Rendering

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2

Keyboard Upload

ARIA

Screen Reader

Focus

Reduced Motion

Accessible Progress

------------------------------------------------------------------------------

# RESPONSIVE

Desktop

Laptop

Tablet

Wide Screen

Maintain enterprise layout.

------------------------------------------------------------------------------

# SECURITY

Never expose

Unauthorized Evidence

Hidden Metadata

Restricted Files

Private Hashes

Other Organizations

Backend RBAC is source of truth.

------------------------------------------------------------------------------

# AUDIT

Every action

Upload

Resume

Retry

Cancel

Delete

Download

Hash Copy

Preview

Must use backend audit APIs.

------------------------------------------------------------------------------

# VALIDATION

Verify

✓ Upload works

✓ Drag & Drop works

✓ Multiple upload works

✓ Resume works

✓ Retry works

✓ Cancel works

✓ Queue works

✓ Metadata viewer works

✓ Hash viewer works

✓ Integrity status works

✓ Preview works

✓ Processing status works

✓ Chain of Custody summary works

✓ Search works

✓ Filters work

✓ Bulk actions work

✓ RBAC works

✓ Audit integration works

✓ Backend integrated

✓ Existing design unchanged

✓ Existing components reused

✓ No mock data

✓ No TypeScript errors

✓ No ESLint errors

✓ No runtime errors

✓ Production-ready

------------------------------------------------------------------------------

# DELIVERABLES

Produce

1.

Evidence Module Architecture

2.

Upload Workflow Diagram

3.

Backend API Mapping

4.

Component Hierarchy

5.

Upload Queue Architecture

6.

Evidence State Flow

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

Evidence Management Validation Report

14.

Evidence Module Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

Do NOT implement

Workspace

Timeline

Knowledge Graph

AI Chat

Reports

Compliance

Administration

Settings

Stop immediately after the Enterprise Evidence Management module is fully integrated with the backend and every validation item passes.

Only then should Phase 6 (Enterprise Investigation Workspace) begin.