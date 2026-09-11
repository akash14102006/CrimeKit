# 01_FRONTEND_CONSTITUTION.md

# Enterprise Frontend Constitution

Target Stack:
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- Zod
- React Hook Form
- TanStack Query

---

# Section 1: Engineering Philosophy

## Mission
Build secure, scalable, maintainable, accessible, observable, testable, and high‑performance enterprise software.

## Principles
1. Correctness over speed
2. Security over convenience
3. Simplicity over cleverness
4. Maintainability over short-term productivity
5. Explicitness over magic
6. Server-first architecture
7. Type safety everywhere
8. Accessibility by default
9. Performance by design
10. Production readiness is mandatory

## Non-Goals
- Hackathon shortcuts
- Demo-only implementations
- Temporary code becoming permanent

---

# Section 2: Next.js 15 Architecture

## Mandatory Standards
- App Router only
- Server Components by default
- Route Handlers
- Suspense
- Streaming
- Metadata API
- Dynamic imports for heavy features

## Routing
- Route groups
- Parallel routes only when justified
- Colocation of feature code

## Rendering Strategy
Priority:
1. Static
2. ISR
3. Server Rendering
4. Client Rendering

Never use client rendering when server rendering solves the problem.

---

# Section 3: React 19 Standards

## Component Philosophy
One component = one responsibility.

## Avoid
- Massive components
- Deep prop drilling
- Unnecessary state

## Preferred
- Composition
- Reusable primitives
- Feature isolation

## Hooks
Use:
- useState
- useReducer
- useTransition
- useOptimistic

Minimize:
- useEffect
- useMemo
- useCallback

---

# Section 4: TypeScript Enterprise Standards

## Compiler
strict=true

## Forbidden
- any
- ts-ignore
- unsafe casts

## Required
- interfaces
- readonly
- discriminated unions
- utility types

Every API contract must be typed.

---

# Section 5: UI Architecture

Layers:
Page
→ Feature
→ Component
→ Primitive

Directory Structure:
app/
features/
components/
lib/
hooks/
types/
schemas/
services/

---

# Section 6: Tailwind Standards

## Rules
- Design tokens only
- Consistent spacing scale
- Responsive-first design
- No arbitrary values unless justified

## Forbidden
- Random spacing values
- Inconsistent typography

---

# Section 7: shadcn/ui Standards

Use shadcn as foundation.

Customize through:
- Tokens
- Variants
- Composition

Never modify generated files recklessly.

---

# Section 8: State Management

Priority:
1. Server State
2. URL State
3. Local State
4. Global State

TanStack Query manages server state.

Avoid global stores unless business requirements demand them.

---

# Section 9: Forms & Validation

React Hook Form required.

Zod required.

Validation:
- Client side
- Server side

Every form requires:
- Loading state
- Error state
- Success state
- Disabled state

---

# Section 10: Security

## Input Validation
Validate:
- Params
- Search params
- Forms
- API responses

## Prevent
- XSS
- CSRF
- Injection
- Open redirects

Never trust client input.

---

# Section 11: Performance

Targets:
- Lighthouse 90+
- Low CLS
- Fast LCP
- Small bundles

Rules:
- Code splitting
- Lazy loading
- Image optimization
- Font optimization

---

# Section 12: Accessibility

Target:
WCAG AA

Required:
- Semantic HTML
- Keyboard support
- Screen reader support
- Focus management

---

# Section 13: Authentication UI

Requirements:
- Session awareness
- Expiration handling
- Logout flow
- Permission-aware UI

Never expose secrets.

---

# Section 14: API Consumption

TanStack Query standards:
- Query keys centralized
- Typed fetchers
- Error handling
- Retry strategy

Never trust API responses without validation.

---

# Section 15: Testing

Required:
- Unit tests
- Integration tests

Critical flows:
- E2E tests

---

# Section 16: Code Review

Review:
- Security
- Performance
- Accessibility
- Types
- Architecture
- Testing

---

# Section 17: AI Coding Rules

AI must:
- Explain architecture
- Identify risks
- Generate typed code
- Respect existing patterns

AI must never:
- Invent APIs
- Ignore lint errors
- Disable TypeScript

---

# Section 18: Definition of Done

A feature is complete only when:

- Functional
- Typed
- Tested
- Accessible
- Secure
- Responsive
- Performant
- Maintainable
- Production Ready

End of Constitution.
