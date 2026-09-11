# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 14 — Enterprise Administration & Identity Management
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 14

Objective:

Develop ONLY the Enterprise Administration & Identity Management module.

This is the operational control center of CrimeKit.

It allows Super Administrators, Organization Administrators, Security Officers, and Compliance Administrators to manage the entire enterprise platform.

Everything MUST integrate with the existing backend.

Do NOT create local users.

Do NOT implement RBAC in frontend.

Do NOT create fake organizations.

Do NOT store permissions locally.

Everything must come directly from backend APIs.

Comparable Enterprise Platforms

• Microsoft Entra ID (Azure AD)

• Okta Admin Console

• Keycloak Admin Console

• Auth0 Dashboard

• GitHub Enterprise Admin

• Atlassian Administration

• AWS IAM Console

• Google Workspace Admin

• Microsoft Defender XDR Administration

------------------------------------------------------------------------------

# ROLE

You are acting as

Principal Frontend Architect

Principal Identity Architect

Principal Security Architect

Principal React Architect

Principal Next.js Architect

Principal UX Architect

Principal Enterprise Product Designer

Principal IAM Engineer

Principal RBAC Architect

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

Administration Planning

RBAC Planning

Authentication Planning

Organization Planning

Security Planning

Workspace Planning

3.

Architecture/

Administration Constitution

Frontend Constitution

Backend Constitution

Security Constitution

Identity Constitution

4.

OpenAPI

5.

Authentication APIs

6.

RBAC APIs

7.

Role APIs

8.

User APIs

9.

Organization APIs

10.

Project APIs

11.

API Key APIs

12.

MFA APIs

13.

Audit APIs

14.

Compliance APIs

15.

Existing Components

16.

Existing Design System

Never redesign.

Never invent APIs.

Reuse existing architecture.

------------------------------------------------------------------------------

# IMPORTANT

DO NOT

Create fake users

Store permissions locally

Create fake organizations

Implement authentication logic

Duplicate RBAC

Duplicate backend validation

Everything MUST come from backend.

------------------------------------------------------------------------------

# OBJECTIVE

Develop ONLY

Enterprise Administration Module

Includes

✓ User Management

✓ Role Management

✓ Permission Management

✓ API Key Management

✓ MFA Management

✓ Organization Management

✓ Project Management

✓ Security Dashboard

✓ Audit Access

✓ Identity Management

Nothing else.

------------------------------------------------------------------------------

# PAGE PURPOSE

Provide complete enterprise administration.

Administrators must be able to manage

Users

Organizations

Projects

Permissions

Roles

Security

API Keys

MFA

Sessions

Audit

Everything from backend.

------------------------------------------------------------------------------

# PAGE LAYOUT

Reuse existing design.

Header

↓

Security Overview Cards

↓

Administration Navigation

↓

User Management

↓

Role Management

↓

Permission Management

↓

Organization Management

↓

Project Management

↓

API Keys

↓

MFA

↓

Audit Summary

------------------------------------------------------------------------------

# SECURITY OVERVIEW

Display

Total Users

Active Users

Organizations

Projects

API Keys

MFA Enabled

Failed Logins

Locked Accounts

Administrators

Investigators

System Health

Everything from backend.

------------------------------------------------------------------------------

# USER MANAGEMENT

Display

User ID

Avatar

Name

Email

Organization

Project

Role

Status

MFA

Last Login

Created

Updated

Permissions

API Keys

Session Count

Quick Actions

Support

Search

Filter

Pagination

Sorting

Bulk Actions

------------------------------------------------------------------------------

# USER DETAILS

Selecting user opens

Profile

Roles

Permissions

Organization

Projects

Sessions

API Keys

MFA

Audit History

Activity

Login History

Recent Actions

------------------------------------------------------------------------------

# ROLE MANAGEMENT

Backend only.

Display

Role

Description

Permission Count

Assigned Users

Created

Updated

System Role

Status

Support

Create

Edit

Assign

Remove

Clone

Search

Filter

------------------------------------------------------------------------------

# PERMISSION MANAGEMENT

Display

Permission

Module

Description

Assigned Roles

Assigned Users

Risk Level

Scope

Support

Search

Filter

Group

View Matrix

Permission Details

------------------------------------------------------------------------------

# PERMISSION MATRIX

Display

Users

↓

Roles

↓

Permissions

Matrix View

Allow

Deny

Inherited

System

Read Only

Visual permission matrix.

Backend controlled.

------------------------------------------------------------------------------

# ORGANIZATION MANAGEMENT

Display

Organization

Logo

Name

Status

Users

Projects

Storage

Cases

Evidence

Created

Administrator

Support

Search

Filter

View

Edit

Archive

------------------------------------------------------------------------------

# ORGANIZATION DETAILS

Display

Overview

Users

Projects

Cases

Storage

Security

Audit

Usage

Limits

Settings

Backend driven.

------------------------------------------------------------------------------

# PROJECT MANAGEMENT

Display

Project

Organization

Owner

Cases

Evidence

Investigators

Created

Status

Storage

AI Usage

Knowledge Graph

Support

Create

Edit

Archive

Transfer

------------------------------------------------------------------------------

# API KEY MANAGEMENT

Backend only.

Display

Key Name

Prefix

Environment

Scopes

Owner

Created

Last Used

Expires

Status

Support

Generate

Rotate

Revoke

Copy

Search

Filter

Never expose full key after creation.

------------------------------------------------------------------------------

# MFA MANAGEMENT

Display

Users with MFA

Disabled MFA

Recovery Codes

Authenticator Type

Last Verification

Failed Attempts

Support

Enable

Disable

Reset

View Status

Backend validation only.

------------------------------------------------------------------------------

# SESSION MANAGEMENT

Display

Active Sessions

Expired Sessions

Device

Browser

IP

Location

Login Time

Last Activity

Support

Terminate

Terminate All

View Details

------------------------------------------------------------------------------

# SECURITY EVENTS

Display

Failed Login

Password Reset

API Key Creation

Role Change

Permission Change

MFA Change

Organization Change

Project Change

Audit Event

Chronological timeline.

------------------------------------------------------------------------------

# AUDIT PANEL

Display

Recent Admin Actions

Role Assignments

Permission Updates

Organization Changes

Project Changes

API Key Events

Authentication Events

Everything backend driven.

------------------------------------------------------------------------------

# FILTERS

Support

Organization

Project

Role

Permission

User

Status

MFA

API Key

Created Date

Last Login

------------------------------------------------------------------------------

# SEARCH

Search

Users

Organizations

Projects

Roles

Permissions

API Keys

Audit

------------------------------------------------------------------------------

# EXPORT

Backend only.

Export

Users

Organizations

Projects

Roles

Permissions

API Keys

Audit

PDF

CSV

Excel

JSON

------------------------------------------------------------------------------

# API INTEGRATION

Reuse existing API layer.

Integrate

Authentication APIs

RBAC APIs

Role APIs

Permission APIs

User APIs

Organization APIs

Project APIs

API Key APIs

MFA APIs

Audit APIs

Compliance APIs

------------------------------------------------------------------------------

# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

User Store

Role Store

Permission Store

Organization Store

Project Store

API Key Store

MFA Store

Audit Store

No duplicate state.

------------------------------------------------------------------------------

# LOADING

Users Skeleton

Roles Skeleton

Permissions Skeleton

Organization Skeleton

Projects Skeleton

Security Skeleton

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

Permission Denied

Session Expired

Conflict

Retry

------------------------------------------------------------------------------

# EMPTY STATES

No Users

No Organizations

No Projects

No Roles

No Permissions

No API Keys

Backend Offline

------------------------------------------------------------------------------

# PERFORMANCE

Virtualized Tables

Infinite Scroll

Memoization

Lazy Panels

Code Splitting

Background Refresh

Optimistic Updates

Large Dataset Support

------------------------------------------------------------------------------

# SECURITY

Respect backend RBAC.

Super Admin

Organization Admin

Security Admin

Compliance Admin

Investigator

Never expose

Other Organizations

Hidden Users

Restricted Roles

Private API Keys

Sensitive Audit Data

Secrets

------------------------------------------------------------------------------

# AUDIT

Every admin action

Create User

Update User

Delete User

Assign Role

Remove Role

Update Permission

Generate API Key

Rotate API Key

Enable MFA

Disable MFA

Organization Changes

Project Changes

Export

Must generate backend audit entries.

------------------------------------------------------------------------------

# ACCESSIBILITY

WCAG 2.2 AA

Keyboard Navigation

ARIA

Screen Reader

Accessible Tables

Accessible Forms

Accessible Dialogs

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

✓ User Management works

✓ Role Management works

✓ Permission Management works

✓ Organization Management works

✓ Project Management works

✓ API Key Management works

✓ MFA Management works

✓ Session Management works

✓ Audit integration works

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

Administration Architecture

2.

Identity Management Flow

3.

RBAC Flow

4.

Organization Hierarchy

5.

Project Hierarchy

6.

Backend API Mapping

7.

Component Hierarchy

8.

Permission Matrix Architecture

9.

Security Workflow

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

Administration Validation Report

17.

Enterprise Administration Readiness Score

------------------------------------------------------------------------------

# FINAL RULE

Do NOT implement

Developer Tools

Monitoring

Infrastructure

Analytics

Stop immediately after the Enterprise Administration & Identity Management module is fully integrated with the existing backend and every validation criterion passes.

Only after successful completion should the final phase begin:

**Phase 15 — Enterprise Performance, Optimization, Accessibility, Security Audit, End-to-End QA, Production Release & Deployment Readiness.**