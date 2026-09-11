# CrimeKit Frontend Implementation Guide

## Purpose

This document is the implementation blueprint for building the CrimeKit
frontend.

------------------------------------------------------------------------

# 1. Technology Stack

-   React 19
-   TypeScript
-   Vite
-   Tailwind CSS
-   shadcn/ui
-   Framer Motion
-   TanStack Query
-   React Hook Form
-   Zod
-   React Router
-   Lucide Icons

------------------------------------------------------------------------

# 2. Project Structure

``` text
src/
├── app/
├── assets/
├── components/
│   ├── ui/
│   ├── common/
│   ├── dashboard/
│   ├── evidence/
│   ├── investigation/
│   ├── timeline/
│   ├── graph/
│   └── ai/
├── features/
├── layouts/
├── pages/
├── hooks/
├── services/
├── api/
├── lib/
├── utils/
├── types/
├── styles/
└── constants/
```

------------------------------------------------------------------------

# 3. Architecture

Feature-based architecture.

Flow:

UI → Components → Hooks → Services → API → Backend

------------------------------------------------------------------------

# 4. Routing

Public - Login - Forgot Password

Protected - Dashboard - Cases - Evidence - Investigation - Timeline -
Knowledge Graph - Reports - Settings

Role-based route guards.

------------------------------------------------------------------------

# 5. State Management

Use React Query for server state.

Use Context only for: - Theme - Authentication - User Preferences

Keep component state local whenever possible.

------------------------------------------------------------------------

# 6. API Layer

Separate API modules.

-   auth.ts
-   case.ts
-   evidence.ts
-   ai.ts
-   reports.ts
-   users.ts

Never call fetch directly inside components.

------------------------------------------------------------------------

# 7. Forms

React Hook Form

Validation: - Zod

Common Forms: - Login - Create Case - Upload Evidence - Settings

------------------------------------------------------------------------

# 8. Error Handling

-   Error Boundary
-   Toast Notifications
-   Retry Failed Requests
-   Friendly Error Pages

------------------------------------------------------------------------

# 9. Performance

-   Lazy Loading
-   Route Splitting
-   Image Optimization
-   Virtualized Tables
-   Memoization
-   Debounced Search

------------------------------------------------------------------------

# 10. Security

-   JWT Authentication
-   Refresh Token
-   RBAC
-   Secure Storage
-   Input Validation
-   XSS Protection
-   CSRF Protection

------------------------------------------------------------------------

# 11. Accessibility

-   WCAG AA
-   Keyboard Navigation
-   Focus Management
-   Screen Reader Labels
-   High Contrast Support

------------------------------------------------------------------------

# 12. Coding Standards

-   TypeScript Strict Mode
-   Reusable Components
-   One Responsibility Per Component
-   No Inline Styles
-   Named Exports
-   Absolute Imports

------------------------------------------------------------------------

# 13. Naming

Components: PascalCase

Hooks: useSomething

Files: kebab-case

Constants: UPPER_SNAKE_CASE

------------------------------------------------------------------------

# 14. Testing

-   Unit Tests
-   Component Tests
-   Integration Tests
-   E2E Tests

------------------------------------------------------------------------

# 15. Production Checklist

-   Responsive
-   Accessible
-   Error Boundaries
-   Loading States
-   Empty States
-   Skeletons
-   Security Review
-   Performance Audit
-   Dark Mode
-   API Integration
-   Logging
-   Monitoring

------------------------------------------------------------------------

# 16. Deployment

Build → Test → Preview → Production

Environment Files

-   .env.local
-   .env.production

------------------------------------------------------------------------

# 17. Development Order

1.  Design System
2.  Components
3.  Layouts
4.  Authentication
5.  Dashboard
6.  Evidence
7.  Investigation
8.  Timeline
9.  Knowledge Graph
10. AI Assistant
11. Reports
12. Settings
13. Testing
14. Deployment

This completes the frontend documentation set.
