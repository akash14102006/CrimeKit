# 03_COMPONENT_TESTING_CONSTITUTION.md

# Enterprise Component Testing Constitution
Version: 1.0
Authority:
- 00_TESTING_SUPREME_CONSTITUTION
- 01_TEST_ARCHITECTURE_CONSTITUTION
- 02_UNIT_TESTING_CONSTITUTION

## Mission

Ensure every UI component is functional, accessible, resilient, responsive, secure, maintainable, and production-ready.

Applies To:

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Hook Form
- Zod
- TanStack Query
- Zustand

---

# Component Testing Philosophy

Components are business interfaces.

Users interact with behavior.

Tests must validate:

✓ User behavior
✓ Business outcomes
✓ Accessibility
✓ Responsiveness

Never test implementation details.

---

# Constitutional Principles

1. Test behavior, not implementation.
2. Accessibility is mandatory.
3. Responsiveness is mandatory.
4. Every state must be tested.
5. Design system consistency is required.
6. Components are production assets.
7. UI failures are business failures.

---

# Component Classification

Tier 1:
Critical Business Components

Tier 2:
Authentication Components

Tier 3:
Payment Components

Tier 4:
Administrative Components

Tier 5:
Shared Components

Higher tiers require stronger validation.

---

# Mandatory State Validation

Every component must test:

✓ Loading State
✓ Success State
✓ Error State
✓ Empty State
✓ Disabled State

Missing state coverage is a defect.

---

# React 19 Testing Rules

Validate:

- Rendering behavior
- User interactions
- Event handling
- State transitions
- Concurrent updates

Avoid:

- internal implementation testing
- hook implementation testing
- framework internals

---

# Next.js 15 Testing Rules

Validate:

- Server Components
- Client Components
- Route Boundaries
- Suspense States
- Error Boundaries
- Streaming States

Server-first architecture must be preserved.

---

# Form Testing Constitution

Required:

✓ Field Validation
✓ Error Messages
✓ Success Messages
✓ Submit Flow
✓ Loading Flow
✓ Disabled Flow

Validate:

- React Hook Form behavior
- Zod validation rules
- Server validation handling

---

# Accessibility Constitution

Target:

WCAG 2.1 AA Minimum

Required Validation:

✓ Keyboard Navigation
✓ Screen Reader Support
✓ Focus Management
✓ ARIA Labels
✓ Semantic HTML
✓ Color Contrast

Accessibility defects are release blockers.

---

# Responsive Testing Constitution

Required Viewports:

Mobile:
320px+

Tablet:
768px+

Desktop:
1024px+

Large Desktop:
1440px+

Validate:

✓ Layout integrity
✓ Navigation
✓ Forms
✓ Tables
✓ Modals

Horizontal scrolling is forbidden.

---

# Design System Governance

Validate:

- Design tokens
- Typography scale
- Spacing system
- Color system
- Component variants

No random styling.

No inconsistent behavior.

---

# shadcn/ui Governance

Validate:

✓ Variant behavior
✓ Composition behavior
✓ Accessibility compliance
✓ Theme compatibility

Generated components must remain testable.

---

# TanStack Query Testing

Validate:

- Loading state
- Success state
- Error state
- Retry state
- Refetch state

Never assume network success.

---

# Zustand Testing

Validate:

- State updates
- State resets
- Derived state
- Persistence behavior

Global state requires verification.

---

# Security Validation

Validate:

- XSS protection
- Input sanitization
- Output encoding
- Authorization UI

Sensitive information must never appear in UI.

---

# Visual Regression Governance

Required For:

- Design systems
- Shared components
- Payment flows
- Authentication flows

Validate:

✓ Layout consistency
✓ Visual consistency
✓ Theme consistency

---

# Enterprise Quality Gates

Required:

✓ Component Tests Pass
✓ Accessibility Tests Pass
✓ Responsive Tests Pass
✓ Visual Regression Pass
✓ Security Validation Pass

Failure blocks release.

---

# Anti-Patterns

Forbidden:

✗ Snapshot-only testing
✗ CSS selector dependence
✗ Implementation testing
✗ Flaky UI tests
✗ Hidden assertions
✗ Untested states

---

# Definition of Done

Component testing is complete only when:

✓ User behavior validated
✓ Accessibility validated
✓ Responsiveness validated
✓ Error handling validated
✓ State coverage validated
✓ Security validated
✓ Visual consistency validated

Anything less is incomplete.

End of Constitution.
