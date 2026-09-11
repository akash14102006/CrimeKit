# ==============================================================================
# CrimeKit Enterprise Frontend
# Phase 15 — Enterprise Settings & System Configuration
# ==============================================================================

Version: 1.0

Project: CrimeKit

Phase: 15

Objective:

Develop ONLY the Enterprise Settings & System Configuration module.

This module is the centralized configuration center of CrimeKit.

It allows every authenticated user to manage personal preferences while allowing administrators to configure enterprise-wide system behavior.

Everything MUST integrate with the existing backend.

DO NOT store settings permanently in localStorage.

DO NOT create fake preferences.

DO NOT hardcode configuration values.

Everything must be loaded, validated, and persisted through backend APIs.

This module should feel comparable to:

• GitHub Settings

• Atlassian Administration

• Microsoft Azure Portal Settings

• AWS Console Preferences

• Notion Settings

• Slack Preferences

• Google Workspace Settings

• Microsoft 365 Admin Center

------------------------------------------------------------------------------
# ROLE

You are acting as

Principal Frontend Architect

Principal Product Designer

Principal UX Architect

Principal Enterprise Platform Architect

Principal React Architect

Principal Next.js Architect

Principal Settings System Architect

Principal Identity & Security Architect

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

Settings Planning

Frontend Planning

Authentication Planning

Security Planning

Notifications Planning

Integration Planning

System Configuration Planning

3.

Architecture/

Frontend Constitution

Backend Constitution

Settings Constitution

Security Constitution

Infrastructure Constitution

OpenAPI

Backend Settings APIs

User APIs

Notification APIs

Authentication APIs

RBAC APIs

Organization APIs

Audit APIs

Existing Components

Existing Providers

Existing Design System

Reuse everything.

Never redesign.

Never invent APIs.

------------------------------------------------------------------------------
# IMPORTANT

DO NOT

Create fake settings

Store enterprise settings locally

Implement backend logic

Duplicate authentication

Duplicate RBAC

Everything MUST come from backend.

------------------------------------------------------------------------------
# OBJECTIVE

Develop ONLY

Enterprise Settings Module

Includes

✓ Profile

✓ Theme

✓ Notifications

✓ Security

✓ Integrations

✓ System Configuration

✓ Sessions

✓ Preferences

✓ Connected Accounts

✓ Personalization

Nothing else.

------------------------------------------------------------------------------
# PAGE PURPOSE

Provide one unified enterprise settings experience.

Allow users to

Manage profile

Manage password

Manage MFA

Manage API preferences

Manage notifications

Manage integrations

Manage sessions

Manage personal preferences

Administrators additionally manage

System configuration

Organization settings

Feature flags

Platform defaults

------------------------------------------------------------------------------
# PAGE LAYOUT

Reuse existing design.

Header

↓

Settings Navigation

↓

Profile

↓

Appearance

↓

Notifications

↓

Security

↓

Sessions

↓

API Preferences

↓

Integrations

↓

System Configuration

------------------------------------------------------------------------------
# SETTINGS NAVIGATION

Sidebar

General

↓

Profile

↓

Appearance

↓

Notifications

↓

Security

↓

Sessions

↓

Connected Accounts

↓

API Preferences

↓

Integrations

↓

Organization

(Admin)

↓

Platform Configuration

(Admin)

------------------------------------------------------------------------------
# PROFILE

Display

Avatar

Full Name

Email

Phone

Department

Organization

Designation

Role

Timezone

Language

Region

Date Format

Time Format

Bio

Support

Update

Upload Avatar

Delete Avatar

Reset Profile

Everything backend validated.

------------------------------------------------------------------------------
# APPEARANCE

Support

Theme

Light

Dark

System

Color Accent

Density

Sidebar Style

Font Size

Animations

Reduced Motion

High Contrast

Accessibility Theme

Remember preference through backend.

------------------------------------------------------------------------------
# NOTIFICATIONS

Backend only.

Support

Email Notifications

Push Notifications

Desktop Notifications

Browser Notifications

Case Updates

Evidence Updates

Processing Completion

AI Findings

Knowledge Graph Updates

Timeline Events

Compliance Alerts

Security Alerts

System Maintenance

Notification Frequency

Instant

Hourly

Daily

Weekly

------------------------------------------------------------------------------
# SECURITY

Display

Password Status

MFA Status

Recovery Codes

API Keys

Recent Login

Last Password Change

Security Score

Support

Change Password

Enable MFA

Disable MFA

Regenerate Recovery Codes

Logout All Sessions

View Security Activity

Everything backend validated.

------------------------------------------------------------------------------
# ACTIVE SESSIONS

Display

Current Device

Browser

Operating System

IP Address

Location

Login Time

Last Activity

Status

Support

Terminate Session

Terminate All

Session Details

------------------------------------------------------------------------------
# CONNECTED ACCOUNTS

Display

Google

Microsoft

GitHub

SSO Provider

LDAP

SAML

OAuth Providers

Support

Connect

Disconnect

Reconnect

View Status

Backend controlled.

------------------------------------------------------------------------------
# API PREFERENCES

Display

API Keys

Personal Tokens

Webhook Tokens

Scopes

Rate Limits

Usage

Support

Generate

Rotate

Revoke

View Usage

Never expose secrets after creation.

------------------------------------------------------------------------------
# INTEGRATIONS

Display

Neo4j

Redis

PostgreSQL

MinIO

OpenAI

Embedding Provider

OCR Engine

Email Service

Notification Service

Storage Provider

Support

Connection Status

Health

Reconnect

View Configuration

Admins only where applicable.

------------------------------------------------------------------------------
# SYSTEM CONFIGURATION

Admin only.

Display

Platform Name

Organization Branding

Logo

Feature Flags

Maintenance Mode

Default Theme

Default Language

Default Timezone

Upload Limits

Retention Defaults

Processing Defaults

AI Configuration

Search Configuration

Knowledge Graph Configuration

Audit Configuration

Notification Configuration

Storage Configuration

Everything from backend.

------------------------------------------------------------------------------
# FEATURE FLAGS

Display

Enabled

Disabled

Experimental

Internal

Beta

Admin only.

------------------------------------------------------------------------------
# PREFERENCES

Support

Language

Timezone

Date Format

Time Format

Measurement Units

Table Density

Pagination

Default Dashboard

Default Workspace

Default Search

------------------------------------------------------------------------------
# SEARCH

Search settings

Profile

Notification

Security

Theme

Integrations

Configuration

------------------------------------------------------------------------------
# EXPORT

Support

Export Profile

Export Preferences

Export Security Settings

Export Notifications

Export System Configuration

Backend only.

------------------------------------------------------------------------------
# API INTEGRATION

Reuse existing API layer.

Integrate

Settings APIs

Authentication APIs

User APIs

Notification APIs

Security APIs

API Key APIs

Organization APIs

Configuration APIs

Audit APIs

------------------------------------------------------------------------------
# STATE MANAGEMENT

Reuse

TanStack Query

Existing Stores

Profile Store

Theme Store

Notification Store

Security Store

Settings Store

Configuration Store

No duplicate state.

------------------------------------------------------------------------------
# LOADING

Profile Skeleton

Settings Skeleton

Security Skeleton

Configuration Skeleton

Notification Skeleton

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

Validation Error

Configuration Conflict

Retry

------------------------------------------------------------------------------
# EMPTY STATES

No Sessions

No Notifications

No Integrations

No API Keys

Backend Offline

------------------------------------------------------------------------------
# PERFORMANCE

Lazy Panels

Code Splitting

Memoization

Background Refresh

Optimistic Updates

Streaming Settings (if backend supports)

------------------------------------------------------------------------------
# SECURITY

Respect backend RBAC.

User

Own settings only

Admin

Organization settings

Platform settings

Never expose

Secrets

Passwords

Private API Keys

System Secrets

------------------------------------------------------------------------------
# AUDIT

Every settings action

Profile Update

Theme Change

Notification Update

Password Change

MFA Update

API Key Rotation

Session Termination

Configuration Update

Feature Flag Change

Must create backend audit entries.

------------------------------------------------------------------------------
# ACCESSIBILITY

WCAG 2.2 AA

Keyboard Navigation

ARIA

Screen Reader

Reduced Motion

High Contrast

Accessible Forms

------------------------------------------------------------------------------
# RESPONSIVE

Desktop

Laptop

Tablet

Enterprise Layout

------------------------------------------------------------------------------
# VALIDATION

Verify

✓ Profile updates correctly

✓ Theme switching works

✓ Notifications integrate with backend

✓ Security settings work

✓ Sessions work

✓ API Preferences work

✓ Integrations display correctly

✓ System Configuration works

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

Settings Architecture

2.

Profile Management Flow

3.

Theme Management Flow

4.

Notification Flow

5.

Security Flow

6.

Integration Flow

7.

System Configuration Flow

8.

Backend API Mapping

9.

Component Hierarchy

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

Enterprise Settings Validation Report

17.

Settings Readiness Score

------------------------------------------------------------------------------
# FINAL RULE

Do NOT implement

Developer Tools

Monitoring

CI/CD

Infrastructure Management

Stop immediately after the Enterprise Settings & System Configuration module is fully integrated with the existing backend and every validation criterion passes.

Only after successful completion should the final project-wide phase begin:

**Phase 16 — Enterprise Production Hardening, Performance Optimization, Accessibility Audit, Security Audit, End-to-End Testing, Production Deployment & Release Readiness.**