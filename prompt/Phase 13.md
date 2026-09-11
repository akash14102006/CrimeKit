# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 13 — Enterprise Compliance & Legal Governance
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 13

Objective:

Develop ONLY the Enterprise Compliance & Legal Governance module.

This module enables investigators, administrators, legal officers, and compliance teams to manage evidence retention, legal holds, GDPR requests, audit readiness, regulatory compliance, and export operations.

Everything MUST integrate with the existing backend.

DO NOT implement compliance logic in the frontend.

DO NOT calculate retention locally.

DO NOT determine GDPR eligibility.

DO NOT enforce legal hold locally.

Everything must come from backend APIs.

This module should be comparable to:

• Microsoft Purview

• IBM OpenPages

• OneTrust

• ServiceNow GRC

• OpenText Compliance

• AWS Macie Console

• Cellebrite Enterprise Compliance

• Magnet AXIOM Enterprise Governance

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Enterprise Compliance Architect

Principal Frontend Architect

Principal Legal Technology Architect

Principal UX Architect

Principal React Architect

Principal Next.js Architect

Principal Governance Platform Engineer

Principal Enterprise Product Designer

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

Compliance Planning

Retention Planning

Legal Planning

Audit Planning

Workspace Planning

Architecture/

Compliance Constitution

Frontend Constitution

Backend Constitution

OpenAPI

Backend Compliance APIs

Audit APIs

Evidence APIs

Case APIs

Chain of Custody APIs

Workspace APIs

Authentication APIs

RBAC APIs

Existing Components

Existing Design System

Reuse everything.

Never redesign.

Never invent APIs.

------------------------------------------------------------------------------

# IMPORTANT

DO NOT

Implement GDPR logic locally

Implement retention calculations

Create fake compliance records

Generate mock audit reports

Store compliance decisions locally

Everything MUST come from backend.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY

Enterprise Compliance Module

Includes

✓ GDPR Requests

✓ Legal Hold

✓ Evidence Retention

✓ Compliance Dashboard

✓ Compliance Export

✓ Retention Policies

✓ Legal Case Holds

✓ Compliance History

✓ Audit Compliance

✓ Regulatory Status

Nothing else.

------------------------------------------------------------------------------

# PAGE PURPOSE

Provide a centralized governance dashboard for enterprise compliance.

Users should be able to

Review compliance status

Manage retention

Apply legal holds

Process GDPR requests

Export compliance reports

Track regulatory actions

View audit history

Everything backend-driven.

------------------------------------------------------------------------------

# PAGE LAYOUT

Reuse existing design.

Header

↓

Compliance KPI Cards

↓

Compliance Dashboard

↓

GDPR Requests

↓

Legal Hold

↓

Retention Policies

↓

Compliance Timeline

↓

Audit Summary

↓

Export Center

------------------------------------------------------------------------------

# DASHBOARD KPI

Display

Open GDPR Requests

Legal Holds

Retention Policies

Evidence Near Expiry

Compliance Violations

Pending Reviews

Export Requests

Audit Events

Cases Under Hold

Evidence Protected

Everything from backend.

------------------------------------------------------------------------------

# GDPR MANAGEMENT

Backend only.

Display

Request ID

User

Case

Evidence

Request Type

Access

Deletion

Correction

Restriction

Portability

Objection

Status

Created

Completed

Assigned Officer

Processing Time

Investigator Notes

------------------------------------------------------------------------------

# GDPR WORKFLOW

Display

Request Submitted

↓

Validation

↓

Legal Review

↓

Investigator Review

↓

Evidence Impact Analysis

↓

Decision

↓

Completed

Show live backend status.

------------------------------------------------------------------------------

# LEGAL HOLD

Display

Hold ID

Case

Evidence

Reason

Court

Jurisdiction

Requested By

Approved By

Applied Date

Expiry

Status

Affected Evidence

Backend controlled.

------------------------------------------------------------------------------

# LEGAL HOLD MANAGEMENT

Support

View Hold

Search Hold

Filter Hold

Release Hold

Extend Hold

View Impact

Generate Hold Report

Everything backend validated.

------------------------------------------------------------------------------

# RETENTION MANAGEMENT

Display

Policy Name

Evidence Type

Retention Period

Current Status

Expiry Date

Deletion Date

Archive Date

Policy Owner

Compliance Status

Affected Evidence Count

------------------------------------------------------------------------------

# RETENTION POLICIES

Support

View Policy

Search Policy

Filter Policy

Policy Details

Evidence Covered

Compliance Status

No frontend policy calculations.

------------------------------------------------------------------------------

# COMPLIANCE TIMELINE

Display

GDPR Events

Retention Events

Legal Hold Events

Audit Events

Evidence Deletion

Evidence Archive

Policy Changes

Investigator Actions

Everything chronological.

------------------------------------------------------------------------------

# COMPLIANCE HISTORY

Display

Who

When

Action

Reason

Affected Evidence

Affected Case

Regulation

Outcome

Searchable.

------------------------------------------------------------------------------

# AUDIT SUMMARY

Display

Authentication Events

Policy Changes

Retention Actions

Legal Hold Actions

GDPR Processing

Evidence Access

Exports

Downloads

Everything from backend.

------------------------------------------------------------------------------

# COMPLIANCE EXPORT

Backend only.

Support

Compliance Report

GDPR Report

Retention Report

Legal Hold Report

Audit Report

Evidence Register

CSV

Excel

PDF

JSON

ZIP

Backend generated only.

------------------------------------------------------------------------------

# FILTERS

Support

Status

Policy

Jurisdiction

Case

Evidence

Investigator

Officer

Date

Retention

Legal Hold

GDPR

------------------------------------------------------------------------------

# SEARCH

Search

Case

Evidence

Policy

GDPR Request

Legal Hold

Officer

Investigator

Compliance ID

------------------------------------------------------------------------------

# API INTEGRATION

Reuse existing API layer.

Integrate

Compliance APIs

GDPR APIs

Legal Hold APIs

Retention APIs

Audit APIs

Evidence APIs

Case APIs

Workspace APIs

Authentication APIs

RBAC APIs

------------------------------------------------------------------------------

# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

Compliance Store

Retention Store

GDPR Store

Legal Hold Store

History Store

Export Store

No duplicate state.

------------------------------------------------------------------------------

# LOADING

Dashboard Skeleton

GDPR Skeleton

Retention Skeleton

Legal Hold Skeleton

Audit Skeleton

Export Skeleton

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

Policy Conflict

Retention Conflict

Export Failed

Retry

------------------------------------------------------------------------------

# EMPTY STATES

No GDPR Requests

No Legal Holds

No Policies

No Audit Records

No Exports

Backend Offline

------------------------------------------------------------------------------

# PERFORMANCE

Lazy Panels

Virtualized Tables

Infinite Scroll

Memoization

Streaming Updates

Background Refresh

Optimized Export Queue

------------------------------------------------------------------------------

# SECURITY

Respect backend RBAC.

Compliance Officer

Legal Officer

Administrator

Investigator (read-only where applicable)

Never expose

Other Organizations

Hidden Policies

Private Evidence

Restricted Compliance Data

------------------------------------------------------------------------------

# AUDIT

Every action

View Policy

Open GDPR Request

Export Report

Release Hold

Extend Hold

Search

Filter

Must create backend audit entries.

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2 AA

Keyboard Navigation

ARIA

Screen Reader

Accessible Tables

Accessible Forms

High Contrast

Reduced Motion

------------------------------------------------------------------------------

# RESPONSIVE

Desktop

Laptop

Tablet

Enterprise Layout

------------------------------------------------------------------------------

# VALIDATION

Verify

✓ Compliance Dashboard loads

✓ GDPR Requests work

✓ Legal Hold works

✓ Retention Policies work

✓ Compliance Timeline works

✓ Audit Summary works

✓ Compliance Export works

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

Compliance Architecture

2.

GDPR Workflow

3.

Legal Hold Workflow

4.

Retention Workflow

5.

Compliance Dashboard Flow

6.

Backend API Mapping

7.

Component Hierarchy

8.

Compliance Timeline Flow

9.

Export Flow

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

Compliance Validation Report

17.

Enterprise Compliance Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

Do NOT implement

Administration

Developer Tools

Monitoring

Infrastructure

Stop immediately after the Enterprise Compliance & Legal Governance module is fully integrated with the backend and all validation criteria pass.

Only after successful completion should Phase 14 (Enterprise Administration & System Management) begin.