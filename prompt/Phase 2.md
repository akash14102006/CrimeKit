# CrimeKit Frontend Development
# Phase 2 — Enterprise Authentication & Authorization

---

# ROLE

You are a:

- Principal Frontend Architect
- Principal Security Engineer
- Principal Identity Architect
- Staff React Engineer
- Staff Next.js Engineer
- Enterprise UI Engineer

You are continuing the CrimeKit frontend.

Phase 1 (Foundation) is already complete.

DO NOT recreate anything from Phase 1.

Reuse everything.

---

# SOURCE OF TRUTH

Before writing ANY code, read everything.

Priority

1.
graphify-out/

- graph.json
- GRAPH_REPORT.md

2.

Planning/

3.

Architecture/

4.

Frontend Constitution

5.

Backend Constitution

6.

Authentication Documents

7.

OpenAPI

8.

Backend Routes

9.

Backend Schemas

10.

Backend Auth Module

11.

RBAC Module

12.

JWT Implementation

13.

Security Modules

14.

Audit Logging

15.

Existing Frontend

16.

Existing Providers

17.

Existing API Client

18.

Existing Zustand Stores

19.

Existing TanStack Query

20.

Existing Design System

Everything already exists.

Integrate.

Do NOT duplicate.

---

# IMPORTANT

Never create

fake login

fake JWT

fake refresh token

fake RBAC

fake users

fake permissions

fake API

fake backend

fake validation

Everything MUST use the existing backend.

---

# ENTERPRISE OBJECTIVE

Implement ONLY Authentication & Authorization.

Nothing else.

Do NOT touch

Dashboard

Workspace

Evidence

Timeline

Reports

Knowledge Graph

AI

Processing

Admin

Settings

Case Management

Only identity.

---

# BACKEND CONTRACT

Use ONLY existing backend endpoints.

Understand backend implementation.

Reuse:

JWT

Refresh Token

Token Blacklist

Password Policy

MFA

Audit Logging

Rate Limiting

Brute Force Protection

RBAC

API Security

Session Restore

Logout

OpenAPI Contracts

Do NOT invent endpoints.

---

# IMPLEMENT

---

## 1 Login Page

Enterprise login.

Must support

Email

Password

Remember Me

Show Password

Loading State

Disabled State

Caps Lock Detection

Password Manager Support

Browser Autofill

Accessibility

Validation

Rate-limit errors

Backend validation

Account Locked

Invalid Credentials

MFA Required

Session Expired

Network Error

Server Error

Do NOT hardcode anything.

---

## 2 Forgot Password

Real backend integration.

Support

Email validation

Request reset

Success state

Rate limit handling

Expired reset token

Invalid reset token

Already requested

Server failure

Loading state

Success animation

No fake flows.

---

## 3 Password Reset

Integrate existing backend.

Support

Strong password validation

Password policy

Confirm password

Strength indicator

Breached password response

Expired link

Token validation

Success redirect

---

## 4 MFA

Implement backend MFA.

Support

TOTP

6-digit code

Countdown

Recovery flow

Invalid code

Expired code

Resend

Remember device

Loading

Failure

Success

Accessibility

No fake OTP.

---

## 5 Session Restore

On refresh

Automatically restore session.

Restore

User

Role

Permissions

Organization

Settings

Theme

Workspace

Refresh token

Expiration

No flicker.

---

## 6 Refresh Token

Silent refresh.

Automatically

before expiration.

Handle

401

403

Expired Refresh

Revoked Token

Offline

Network Failure

Retry

Logout

Queue pending requests

Replay after refresh

Prevent duplicate refreshes.

---

## 7 Logout

Enterprise logout.

Backend logout endpoint.

Revoke token.

Clear

Session

Cache

Queries

Stores

Local Storage

Cookies

Broadcast logout across tabs.

Redirect safely.

---

## 8 Protected Routes

Implement

Protected Layout

Route Guards

Nested Guards

Role Guards

Permission Guards

Redirect Rules

Unauthorized Page

Forbidden Page

Session Expired Page

Loading Page

Support

Server Components

Client Components

Middleware

---

## 9 RBAC

Integrate backend RBAC.

Support

Admin

Investigator

Analyst

Viewer

User

Implement

Role Hook

Permission Hook

Feature Guards

Page Guards

Button Guards

Action Guards

Table Guards

Navigation Guards

Menu Guards

No duplicated permission logic.

Everything centralized.

---

## 10 API Integration

Use existing API client.

No duplicate axios.

Support

Retry

Timeout

Refresh

Interceptors

Error Mapping

Correlation IDs

Request IDs

Audit Headers

API Keys

Bearer Token

---

## 11 Forms

React Hook Form

Zod

Server Validation

Inline Errors

Focus Invalid Field

Keyboard Support

Autocomplete

Password Managers

Accessibility

---

## 12 State Management

Reuse existing stores.

Only extend.

Auth Store

Session Store

Permission Store

Profile Store

No duplicate stores.

---

## 13 Query Management

Use TanStack Query.

Implement

Current User

Session

Permissions

Roles

Invalidate on logout

Refresh after login

Optimistic updates

---

## 14 Middleware

Implement

Authentication Middleware

Permission Middleware

Guest Middleware

Admin Middleware

Investigator Middleware

Redirect Middleware

Remember destination.

---

## 15 Security

Enterprise frontend security.

Never store JWT insecurely.

Support backend strategy.

Implement

XSS Safe Rendering

CSRF Ready

Token Rotation

Replay Prevention

Secure Cookies Support

Tab Sync

Session Timeout

Idle Timeout

Device Trust

Content Security Policy Compatible

---

## 16 Error Handling

Support

401

403

404

419

429

500

502

503

504

Account Locked

Too Many Requests

Password Expired

Token Revoked

Session Expired

Display meaningful enterprise messages.

---

## 17 Loading States

Button Loading

Page Loading

Route Loading

Skeleton

Spinner

Progress Bar

Silent Refresh

Session Restore

---

## 18 Accessibility

WCAG 2.2

Keyboard

Focus

Screen Reader

ARIA

Labels

Error Announcements

Reduced Motion

High Contrast

---

## 19 Performance

Code Split

Lazy Load

Streaming

Suspense

Prefetch

Tree Shaking

Memoization

No unnecessary re-renders.

---

## 20 Audit Integration

Ensure frontend sends

Correlation ID

Request ID

Trace ID

Session ID

User Agent

Timezone

Locale

when required by backend.

Do NOT duplicate audit logging.

Backend remains source of truth.

---

# VALIDATION

Verify

✓ Login works

✓ Logout works

✓ Session restore works

✓ Refresh works

✓ MFA works

✓ Forgot password works

✓ Password reset works

✓ RBAC works

✓ Protected routes work

✓ Unauthorized redirect works

✓ Refresh race conditions handled

✓ Multiple tabs synchronized

✓ API client integrated

✓ Existing backend unchanged

✓ Existing design unchanged

✓ Existing providers reused

✓ Existing stores reused

✓ Existing components reused

✓ No fake authentication

✓ No mock API

✓ No TypeScript errors

✓ No ESLint errors

✓ No hydration issues

✓ No runtime errors

✓ No duplicate code

✓ Enterprise-ready

---

# DELIVERABLES

Produce

1.

Authentication Architecture

2.

Authentication Flow Diagram

3.

RBAC Flow

4.

Protected Route Flow

5.

Session Lifecycle

6.

Refresh Token Lifecycle

7.

Files Created

8.

Files Modified

9.

Files Reused

10.

Backend Endpoints Integrated

11.

Security Checklist

12.

Performance Report

13.

Accessibility Report

14.

Testing Report

15.

Authentication Readiness Score

---

# FINAL RULE

Do NOT implement Dashboard.

Do NOT implement Workspace.

Do NOT implement Evidence.

Do NOT implement AI.

Do NOT implement Reports.

Do NOT implement Timeline.

Do NOT implement Knowledge Graph.

Stop after Authentication is completely production-ready and fully integrated with the existing enterprise backend.

Only after every validation item passes should Phase 3 (Enterprise Dashboard) begin.