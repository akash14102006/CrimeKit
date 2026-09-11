# Phase 1 Report — Enterprise Frontend Foundation

**Status:** COMPLETE — lint, type-check, and production build all pass at zero errors.

**Scope:** Enterprise Foundation layer for the CrimeKit frontend (Next.js 16.2.12 + React 19.2.4 + shadcn/base-nova + TanStack Query + Zustand).

---

## 1. Files Created (new)

### Types (`src/types/`)
- `common.ts` — `ID`, `ISOString`, `Dict`, `Nullable`, `PaginationParams`, `PaginatedResponse`, `ApiErrorBody`, `ThemeMode`
- `auth.ts` — `RoleName`, `Permission`, `LoginRequest`, `RegisterRequest`, `TokenResponse`, `UserProfile`, `AuthSession`
- `case.ts` — `CaseStatus`, `CaseCreate`, `CaseUpdate`, `CaseOut`, `CaseSummary`
- `evidence.ts` — `Evidence`, `EvidenceUploadResponse`, `CustodyHistoryEntry`, `CustodyStatus`, `CustodyAppendRequest`
- `kg.ts` — `GraphNode`, `GraphEdge`, `CaseGraph`, `CypherQuery`, `KGQueryResponse`, `EntityRef`
- `timeline.ts` — `TimelineEvent`, `TimelineQuery`
- `workspace.ts` — `InvestigationWorkspace` + all sub-schemas (evidence, custody, timeline, KG summary, AI findings, related evidence, similar cases, progress, risks, court report)
- `search.ts` — `SearchResponse`, `SearchResult`, `SearchFacet`, all request models (General/Evidence/Case/Timeline/Entity/Relationship/Hybrid/Semantic/CrossCorrelation), `ReindexResponse`
- `processing.ts` — `QueueStats`, `ProcessingJob`, `JobProgress`, `EnqueueRequest`, `ForensicProcessRequest`
- `compliance.ts` — GDPR, RetentionPolicy, LegalHold, ComplianceReport, DataClassification, export requests
- `audit.ts` — `AuditLogEntry`
- `health.ts` — `HealthStatus`, `ReadinessResponse`, `LivenessResponse`, `DetailedHealthResponse`
- `api.ts` — `ApiRequestOptions`
- `index.ts` — barrel export

### Constants / Config (`src/constants/`, `src/config/`)
- `roles.ts` — canonical backend roles, role→permission matrix (mirrors backend), labels
- `api-endpoints.ts` — all verified backend route paths (from `backend/app/*.py`)
- `navigation.ts` — nav sections keyed to existing routes with RBAC permission gates
- `env.ts` — runtime config with `NEXT_PUBLIC_*` fallbacks
- `query.ts` — TanStack Query defaults (staleTime 30s, no refetch on focus)

### Lib (`src/lib/`)
- `errors.ts` — `AppError`, `isAppError`, `AppError.fromHttpStatus`
- `logger.ts` — level-aware structured client logger
- `rbac.ts` — `resolvePermissions`, `hasPermission`, `hasAnyPermission`, `hasRole` (canonical)
- `sanitize.ts` — `stripTags`, `normalizeWhitespace`, `clampText`, `isValidEmail`, `redactEmails`, `maskToken`
- `session.ts` — pending-MFA sessionStorage helpers
- `api-client.ts` — **hardened**: refresh-token queue with reject-on-failure, auth-endpoint toast suppression, typed `api.get/post/put/patch/delete/upload` helpers, upload progress callback, `getErrorMessage`

### Services (`src/services/`)
- `authService`, `caseService`, `evidenceService`, `searchService`, `kgService`, `workspaceService`, `timelineService`, `processingService`, `complianceService`, `healthService`, `rolesService`, `reportService`, `index.ts`
- All typed against verified backend contracts (no mock data, no invented endpoints)

### Hooks (`src/hooks/`)
- `useDebounce`, `useMediaQuery` (+`useIsMobile`), `useLocalStorage`, `useMounted` (via `useSyncExternalStore`), `useHasHydrated` (persist-hydration aware), `index.ts`
- `useRBAC.ts` — **rewritten** to canonicalize against backend role set
- `queries/*` — **all refactored** to consume services: `useCases`, `useEvidence`, `useGlobalSearch`, `useKnowledgeGraph`, `useTimeline`, `useWorkspace`, `useStats`

### UI Primitives (`src/components/ui/`)
- `textarea`, `checkbox`, `switch`, `select`, `tabs`, `accordion`, `separator`, `popover`, `tooltip` (base-nova style, data-slot conventions)
- `status-badge` (semantic tone mapping), `metric-card`

### Shared Components (`src/components/shared/`)
- `LoadingState`, `ErrorState`, `EmptyState`
- `AuthGuard.tsx` — **rewritten**: no setState-in-effect, redirect via effect, hydration-aware
- `Sidebar.tsx` — **rewritten**: RBAC-filtered nav from constants, proper logout via service
- `Header.tsx` — **updated**: role label, working logout + settings link

### App Error/Loading System
- `src/app/(dashboard)/error.tsx` (new)
- `src/app/(dashboard)/not-found.tsx` (new)
- `src/app/(dashboard)/loading.tsx` (new)

### Other
- `src/app/(auth)/layout.tsx` — **fixed** broken `/grid.svg` reference (replaced with CSS radial gradients)
- `src/app/global-error.tsx` — fixed unescaped entity lint error
- `src/features/auth/components/LoginForm.tsx` — **refactored** onto `authService`; fixes `any`-type lint errors and `Date.now()` purity issue
- `src/features/evidence/components/EvidenceUploadModal.tsx` — **refactored** onto typed upload mutation with progress
- `src/features/workspace/components/WorkspaceLayout.tsx` — **typed** to `InvestigationWorkspace` contracts
- `src/store/authStore.ts` — typed to `UserProfile`, added `setUser`
- `src/components/providers.tsx` — Query defaults + `TooltipProvider`
- `src/components/auth/RoleGate.tsx`, `src/components/shared/RoleGuard.tsx` — use canonical `lib/rbac`
- `src/app/(dashboard)/dashboard/page.tsx` — fixed `QueueStats` field names + health status comparison
- `src/app/(dashboard)/search/page.tsx` — fixed lint errors **and removed XSS vector** (`dangerouslySetInnerHTML`), uses `stripTags` + typed `SearchResult`
- `src/features/cases/components/CaseList.tsx` — `StatusBadge` + backend status values
- `eslint.config.mjs` — ignores `**/._*` / `**/._*/**`
- `tsconfig.json` — excludes `**/._*`
- `package.json` — added `type-check` script

## 2. Backend APIs Integrated
Only existing backend contracts were used (verified via code exploration of `backend/app/*.py`): auth (login/register/me/refresh/logout/mfa), cases (CRUD), evidence (list/detail/byCase/upload/custody), search (`/api/v1/search*`), knowledge graph (`/kg/*`), workspace (`/workspace/cases/{id}/*`), timeline (`/timeline`), processing (`/processing/*`), compliance (`/api/v1/compliance/*`), reports (`/reports`), roles (`/roles/*`), health (`/health*`).

## 3. Architecture Decisions
1. **Service layer** centralizes all HTTP; hooks/features never call axios directly.
2. **Canonical RBAC** — `src/constants/roles.ts` permission matrix mirrors the backend; legacy `user` role maps to `viewer` permissions; `lib/rbac` + `hooks/useRBAC` used everywhere.
3. **No mock/placeholder data** — services are typed to real responses; pages degrade to empty/error states.
4. **Refresh-queue hardening** — refresh subscribers now reject on failed refresh (previous code could hang queued requests).
5. **Hydration-safe guards** — `useHasHydrated`/`useSyncExternalStore` replace setState-in-effect (lint-driven).
6. **XSS remediation** — search results sanitized with `stripTags`; no `dangerouslySetInnerHTML` remains.

## 4. Validation Report
| Check | Command | Result |
|---|---|---|
| Lint | `npm run lint` | 0 errors, 0 warnings |
| Type-check | `npm run type-check` | 0 errors |
| Build | `npm run build` | Compiled + typed + 14 routes (12 static, 1 dynamic, `_not-found`) |

## 5. Remaining Issues / Notes
- **Font conflict unresolved**: design system mandates Inter + JetBrains Mono; `layout.tsx` loads Poppins (`--font-sans`). Needs a design decision before Phase 2.
- Backend not running on `:8002` — no live smoke tests performed (contracts verified statically only).
- Search backend contract caveats (from backend audit): `/search/relationships`, `/search/facets`, `/search/cross-correlation`, `/search/health` reference missing `SearchEngine` methods and may 500 — frontend services are typed but these should not be wired to UI until backend is fixed.
- `/compliance` and `/audit` nav routes were **omitted** (pages don't exist yet); add with those phases.
- Descope provider kept but unused for auth (backend JWT flow is primary).
- `._*` AppleDouble sidecars remain untouched (lint/tsconfig now ignore them).
