# FILE MIGRATION MATRIX & EXECUTION GUIDE

**Version:** 1.0 (Ready for Migration)  
**Files:** 124 markdown files  
**Target Structure:** 12-tier governance hierarchy  
**Status:** Ready to execute

---

## QUICK REFERENCE: FILE COUNTS BY CATEGORY

| Category | Current | New | Change |
|----------|---------|-----|--------|
| SUPREME CONSTITUTION | 1 | 1 | → Root |
| DOMAIN CONSTITUTIONS | 9 | 9 | Reorganized |
| RULES | 18 | 18 | Regrouped |
| SKILLS | 42 | 42 | Reorganized |
| INSTRUCTIONS | 15 | 15 | Reorganized |
| AGENTS | 6 | 8 | +2 to create |
| REVIEW BOARDS | 6 | 8 | Clarified |
| GOVERNANCE | 10 | 10 | Reorganized |
| WORKFLOWS | 0 | 6 | +6 to create |
| CONTEXT | 0 | 8 | +8 to create |
| REFERENCE | 0 | 15 | +15 to create |
| DOCUMENTATION | 0 | 5 | +5 to create |
| DUPLICATES | 2 | 0 | DELETE |
| **TOTAL** | **124** | **150+** | **Net: +26 new files** |

---

## MIGRATION ACTION ITEMS

### IMMEDIATE ACTIONS (This Week)

#### DELETE DUPLICATES
```
1. constitution\Frontend Constitution\01_ENGINEERING_PHILOSOPHY_MASTER_PROMPT (1).md
   → DELETE (exact duplicate of non-numbered version)

2. Fullstack Rules\Frontend\react-typescript-nextjs-nodejs-cursorrules-prompt- (1).mdc
   → DELETE (exact duplicate of non-numbered version)
```

#### VERIFY CLASSIFICATIONS
- [ ] Review all 124 files in classification table
- [ ] Resolve any ambiguous categorizations
- [ ] Get domain expert sign-off on contested moves
- [ ] Prepare detailed migration script

---

## DETAILED FILE MIGRATION MAP

### A: SUPREME CONSTITUTION

| File | Current Path | New Path | Action | Notes |
|------|--------------|----------|--------|-------|
| 00_TESTING_SUPREME_CONSTITUTION.md | Testing Constitution | `00_SUPREME_CONSTITUTION/` | MOVE | Cross-cutting authority |

---

### B: COMMON FOUNDATION

| File | Current Path | New Path | Action | Notes |
|------|--------------|----------|--------|-------|
| 01_ENGINEERING_PHILOSOPHY_MASTER_PROMPT.md | Frontend Constitution | `01_COMMON_FOUNDATION/ENGINEERING_PHILOSOPHY.md` | MOVE + RENAME | Remove _MASTER_PROMPT |

---

### C: GLOBAL RULES (18 files)

#### Backend Rules (3)
| File | Current | New | Action |
|------|---------|-----|--------|
| 15_BACKEND_AI_CODING_RULES_MASTER_PROMPT.md | Backend Constitution | `02_GLOBAL_RULES/BACKEND/BACKEND_AI_CODING_RULES.md` | MOVE + RENAME |
| 07_BACKEND_SECURITY_MASTER_PROMPT.md | Backend Constitution | `02_GLOBAL_RULES/SECURITY/BACKEND_SECURITY_RULES.md` | MOVE + RENAME |
| 11_DATABASE_AI_CODING_RULES_MASTER_PROMPT.md | Database and API | `02_GLOBAL_RULES/DATABASE/DATABASE_RULES.md` | MOVE + RENAME |

#### Frontend Rules (3)
| File | Current | New | Action |
|------|---------|-----|--------|
| 09_SECURITY_MASTER_PROMPT.md | Frontend Constitution | `02_GLOBAL_RULES/SECURITY/FRONTEND_SECURITY_RULES.md` | MOVE + RENAME |
| 11_ACCESSIBILITY_MASTER_PROMPT.md | Frontend Constitution | `02_GLOBAL_RULES/ACCESSIBILITY/ACCESSIBILITY_RULES.md` | MOVE + RENAME |
| 15_AI_CODING_RULES_MASTER_PROMPT.md | Frontend Constitution | `02_GLOBAL_RULES/FRONTEND/FRONTEND_AI_CODING_RULES.md` | MOVE + RENAME |
| 17_FRONTEND_GOLDEN_RULES_MASTER_PROMPT.md | Frontend Constitution | `02_GLOBAL_RULES/FRONTEND/FRONTEND_GOLDEN_RULES.md` | MOVE + RENAME |

#### Code Quality Rules (3)
| File | Current | New | Action |
|------|---------|-----|--------|
| 03_CODE_QUALITY_MASTER_PROMPT.md | Build Tools | `02_GLOBAL_RULES/CODE_QUALITY/CODE_QUALITY_STANDARDS.md` | MOVE + RENAME |
| 05_ENGINEERING_STANDARDS_MASTER_PROMPT.md | Build Tools | `02_GLOBAL_RULES/CODE_QUALITY/ENGINEERING_STANDARDS.md` | MOVE + RENAME |
| 09_ANTI_OVERENGINEERING_MASTER_PROMPT.md | Build Tools | `02_GLOBAL_RULES/ANTI_OVERENGINEERING/ANTI_OVERENGINEERING.md` | MOVE + RENAME |

#### Other Rules (6)
| File | Current | New | Action |
|------|---------|-----|--------|
| 08_DATA_SECURITY_MASTER_PROMPT.md | Database and API | `02_GLOBAL_RULES/SECURITY/DATA_SECURITY_RULES.md` | MOVE + RENAME |
| 06_ACCESSIBILITY_MASTER_PROMPT.md | UIUX design | `02_GLOBAL_RULES/ACCESSIBILITY/ACCESSIBILITY_UIUX_RULES.md` | MOVE + RENAME |
| 12_UI_AI_CODING_RULES_MASTER_PROMPT.md | UIUX design | `02_GLOBAL_RULES/UI_AI_CODING/UI_AI_RULES.md` | MOVE + RENAME |
| 13_DESIGN_SYSTEM_GOLDEN_RULES_MASTER_PROMPT.md | UIUX design | `02_GLOBAL_RULES/DESIGN_SYSTEM/DESIGN_SYSTEM_RULES.md` | MOVE + RENAME |
| 09_SECURITY_TESTING_CONSTITUTION.md | Testing | `02_GLOBAL_RULES/TESTING/SECURITY_TESTING_RULES.md` | MOVE + RENAME |
| 13_OBSERVABILITY_TESTING_CONSTITUTION.md | Testing | `02_GLOBAL_RULES/TESTING/OBSERVABILITY_TESTING_RULES.md` | MOVE + RENAME |
| 09_STATE_AI_CODING_RULES_MASTER_PROMPT.md | State Management | `02_GLOBAL_RULES/STATE_MANAGEMENT/STATE_AI_RULES.md` | MOVE + RENAME |

---

### D: GLOBAL INSTRUCTIONS (15 files)

#### Architecture Instructions (4)
| File | Current | New | Action |
|------|---------|-----|--------|
| 02_BACKEND_ARCHITECTURE_MASTER_PROMPT.md | Backend Constitution | `03_GLOBAL_INSTRUCTIONS/ARCHITECTURE/BACKEND_ARCHITECTURE.md` | MOVE + RENAME |
| 02_ARCHITECTURE_MASTER_PROMPT.md | Frontend Constitution | `03_GLOBAL_INSTRUCTIONS/ARCHITECTURE/FRONTEND_ARCHITECTURE.md` | MOVE + RENAME |
| 02_DATABASE_ARCHITECTURE_MASTER_PROMPT.md | Database and API | `03_GLOBAL_INSTRUCTIONS/ARCHITECTURE/DATABASE_ARCHITECTURE.md` | MOVE + RENAME |
| 02_DESIGN_SYSTEM_ARCHITECTURE_MASTER_PROMPT.md | UIUX design | `03_GLOBAL_INSTRUCTIONS/ARCHITECTURE/DESIGN_SYSTEM_ARCHITECTURE.md` | MOVE + RENAME |

#### DDD/Methodology Instructions (2)
| File | Current | New | Action |
|------|---------|-----|--------|
| 03_DOMAIN_DRIVEN_BACKEND_MASTER_PROMPT.md | Backend Constitution | `03_GLOBAL_INSTRUCTIONS/METHODOLOGY/DDD_BACKEND.md` | MOVE + RENAME |
| 03_DOMAIN_DRIVEN_FRONTEND_MASTER_PROMPT.md | Frontend Constitution | `03_GLOBAL_INSTRUCTIONS/METHODOLOGY/DDD_FRONTEND.md` | MOVE + RENAME |

#### Backend Execution Instructions (2)
| File | Current | New | Action |
|------|---------|-----|--------|
| 16_BACKEND_SYSTEMS_ARCHITECTURE_MASTER_PROMPT.md | Backend Constitution | `03_GLOBAL_INSTRUCTIONS/BACKEND_EXECUTION/BACKEND_SYSTEMS.md` | MOVE + RENAME |
| 13_TESTING_QUALITY_MASTER_PROMPT.md | Backend Constitution | `03_GLOBAL_INSTRUCTIONS/BACKEND_EXECUTION/TESTING_EXECUTION.md` | MOVE + RENAME |

#### Frontend Execution Instructions (6)
| File | Current | New | Action |
|------|---------|-----|--------|
| 16_FRONTEND_SYSTEMS_ARCHITECTURE_MASTER_PROMPT.md | Frontend Constitution | `03_GLOBAL_INSTRUCTIONS/FRONTEND_EXECUTION/SYSTEMS_ARCHITECTURE.md` | MOVE + RENAME |
| 12_TESTING_QUALITY_MASTER_PROMPT.md | Frontend Constitution | `03_GLOBAL_INSTRUCTIONS/FRONTEND_EXECUTION/TESTING_EXECUTION.md` | MOVE + RENAME |
| 05_STATE_MANAGEMENT_MASTER_PROMPT.md | Frontend Constitution | `03_GLOBAL_INSTRUCTIONS/FRONTEND_EXECUTION/STATE_MANAGEMENT.md` | MOVE + RENAME |
| 06_API_INTEGRATION_MASTER_PROMPT.md | Frontend Constitution | `03_GLOBAL_INSTRUCTIONS/FRONTEND_EXECUTION/API_INTEGRATION.md` | MOVE + RENAME |
| 07_AUTHENTICATION_MASTER_PROMPT.md | Frontend Constitution | `03_GLOBAL_INSTRUCTIONS/FRONTEND_EXECUTION/AUTHENTICATION.md` | MOVE + RENAME |
| 08_FORMS_VALIDATION_MASTER_PROMPT.md | Frontend Constitution | `03_GLOBAL_INSTRUCTIONS/FRONTEND_EXECUTION/FORMS_VALIDATION.md` | MOVE + RENAME |

#### Design System Instructions (1)
| File | Current | New | Action |
|------|---------|-----|--------|
| 13_DESIGN_SYSTEM_MASTER_PROMPT.md | Frontend Constitution | `03_GLOBAL_INSTRUCTIONS/DESIGN_SYSTEM/DESIGN_SYSTEM_EXECUTION.md` | MOVE + RENAME |

---

### E: GLOBAL SKILLS (42 files)

#### TypeScript Skills (2)
| File | Current | New | Action |
|------|---------|-----|--------|
| 02_TYPESCRIPT_MASTER_PROMPT.md | Build Tools | `04_GLOBAL_SKILLS/TYPESCRIPT/CORE/TYPESCRIPT_EXPERTISE.md` | MOVE + RENAME |
| 21_TYPESCRIPT_SUPREME_CONSTITUTION.md | Build Tools | `04_GLOBAL_SKILLS/TYPESCRIPT/CONSTITUTION/TYPESCRIPT_SUPREME.md` | MOVE |

#### Next.js Ecosystem (2)
| File | Current | New | Action |
|------|---------|-----|--------|
| 22_NEXTJS_ENTERPRISE_CONSTITUTION.md | Build Tools | `04_GLOBAL_SKILLS/NEXTJS_ECOSYSTEM/NEXTJS/NEXTJS_EXPERTISE.md` | MOVE + RENAME |
| 23_REACT_ENTERPRISE_CONSTITUTION.md | Build Tools | `04_GLOBAL_SKILLS/NEXTJS_ECOSYSTEM/REACT/REACT_EXPERTISE.md` | MOVE + RENAME |

#### Node.js Skills (1)
| File | Current | New | Action |
|------|---------|-----|--------|
| 24_NODEJS_ENTERPRISE_CONSTITUTION.md | Build Tools | `04_GLOBAL_SKILLS/NODEJS/NODEJS_EXPERTISE.md` | MOVE + RENAME |

#### Database Skills (5)
| File | Current | New | Action |
|------|---------|-----|--------|
| 03_POSTGRESQL_MASTER_PROMPT.md | Database and API | `04_GLOBAL_SKILLS/DATABASE/POSTGRESQL/POSTGRESQL_EXPERTISE.md` | MOVE + RENAME |
| 04_PRISMA_MASTER_PROMPT.md | Database and API | `04_GLOBAL_SKILLS/DATABASE/PRISMA/PRISMA_EXPERTISE.md` | MOVE + RENAME |
| 28_SUPABASE_ENTERPRISE_CONSTITUTION.md | Build Tools | `04_GLOBAL_SKILLS/DATABASE/SUPABASE/SUPABASE_EXPERTISE.md` | MOVE + RENAME |
| 09_MULTI_TENANT_DATA_MASTER_PROMPT.md | Database and API | `04_GLOBAL_SKILLS/DATABASE/MULTI_TENANT/MULTI_TENANT_PATTERNS.md` | MOVE + RENAME |
| 10_DATABASE_PERFORMANCE_MASTER_PROMPT.md | Database and API | `04_GLOBAL_SKILLS/DATABASE/PERFORMANCE/DATABASE_OPTIMIZATION.md` | MOVE + RENAME |

#### Caching Skills (1)
| File | Current | New | Action |
|------|---------|-----|--------|
| 11_REDIS_CACHING_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/CACHING/REDIS/REDIS_CACHING.md` | MOVE + RENAME |

#### API Design Skills (3)
| File | Current | New | Action |
|------|---------|-----|--------|
| 04_API_DESIGN_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/API_DESIGN/CORE/API_DESIGN_PATTERNS.md` | MOVE + RENAME |
| 06_REST_API_MASTER_PROMPT.md | Database and API | `04_GLOBAL_SKILLS/API_DESIGN/REST/REST_EXPERTISE.md` | MOVE + RENAME |
| 07_GRAPHQL_MASTER_PROMPT.md | Database and API | `04_GLOBAL_SKILLS/API_DESIGN/GRAPHQL/GRAPHQL_EXPERTISE.md` | MOVE + RENAME |

#### State Management Skills (8)
| File | Current | New | Action |
|------|---------|-----|--------|
| 02_SERVER_STATE_MASTER_PROMPT.md | State Management | `04_GLOBAL_SKILLS/STATE_MANAGEMENT/SERVER_STATE/EXPERTISE.md` | MOVE + RENAME |
| 03_CLIENT_STATE_MASTER_PROMPT.md | State Management | `04_GLOBAL_SKILLS/STATE_MANAGEMENT/CLIENT_STATE/EXPERTISE.md` | MOVE + RENAME |
| 04_CACHE_ARCHITECTURE_MASTER_PROMPT.md | State Management | `04_GLOBAL_SKILLS/STATE_MANAGEMENT/CACHE/CACHE_EXPERTISE.md` | MOVE + RENAME |
| 05_AUTH_SESSION_STATE_MASTER_PROMPT.md | State Management | `04_GLOBAL_SKILLS/STATE_MANAGEMENT/AUTH_SESSION/AUTH_EXPERTISE.md` | MOVE + RENAME |
| 06_MULTI_TENANT_STATE_MASTER_PROMPT.md | State Management | `04_GLOBAL_SKILLS/STATE_MANAGEMENT/MULTI_TENANT/MULTI_TENANT_STATE.md` | MOVE + RENAME |
| 07_OFFLINE_SYNC_STATE_MASTER_PROMPT.md | State Management | `04_GLOBAL_SKILLS/STATE_MANAGEMENT/OFFLINE_SYNC/OFFLINE_PATTERNS.md` | MOVE + RENAME |
| 08_STATE_PERFORMANCE_MASTER_PROMPT.md | State Management | `04_GLOBAL_SKILLS/STATE_MANAGEMENT/PERFORMANCE/STATE_OPTIMIZATION.md` | MOVE + RENAME |
| 10_STATE_ARCHITECT_REVIEW_MASTER_PROMPT.md | State Management | `05_AI_AGENTS/STATE_MANAGEMENT_ARCHITECT/ROLE.md` | MOVE + RECLASSIFY |

#### Frontend Component Skills (2)
| File | Current | New | Action |
|------|---------|-----|--------|
| 04_COMPONENT_ARCHITECTURE_MASTER_PROMPT.md | Frontend Constitution | `04_GLOBAL_SKILLS/FRONTEND_ARCHITECTURE/COMPONENT_ARCHITECTURE.md` | MOVE + RENAME |
| 03_COMPONENT_ARCHITECTURE_MASTER_PROMPT.md | UIUX design | `04_GLOBAL_SKILLS/UIUX_DESIGN/COMPONENT_SYSTEMS/COMPONENT_ARCHITECTURE.md` | MOVE + RENAME |

#### Frontend Performance Skills (1)
| File | Current | New | Action |
|------|---------|-----|--------|
| 10_PERFORMANCE_MASTER_PROMPT.md | Frontend Constitution | `04_GLOBAL_SKILLS/FRONTEND_PERFORMANCE/FRONTEND_OPTIMIZATION.md` | MOVE + RENAME |

#### Frontend Observability Skills (1)
| File | Current | New | Action |
|------|---------|-----|--------|
| 14_OBSERVABILITY_MASTER_PROMPT.md | Frontend Constitution | `04_GLOBAL_SKILLS/FRONTEND_OBSERVABILITY/MONITORING.md` | MOVE + RENAME |

#### UIUX Design Skills (8)
| File | Current | New | Action |
|------|---------|-----|--------|
| 08_MOTION_ANIMATION_MASTER_PROMPT.md | UIUX design | `04_GLOBAL_SKILLS/UIUX_DESIGN/MOTION_ANIMATION/ANIMATION_PATTERNS.md` | MOVE + RENAME |
| 07_RESPONSIVE_DESIGN_MASTER_PROMPT.md | UIUX design | `04_GLOBAL_SKILLS/UIUX_DESIGN/RESPONSIVE_DESIGN/RESPONSIVE_EXPERTISE.md` | MOVE + RENAME |
| 10_FORMS_INTERACTIONS_MASTER_PROMPT.md | UIUX design | `04_GLOBAL_SKILLS/UIUX_DESIGN/FORMS_INTERACTIONS/FORM_PATTERNS.md` | MOVE + RENAME |
| 11_DESIGN_TOKENS_MASTER_PROMPT.md | UIUX design | `04_GLOBAL_SKILLS/UIUX_DESIGN/DESIGN_TOKENS/DESIGN_TOKEN_SYSTEMS.md` | MOVE + RENAME |
| 04_VISUAL_DESIGN_MASTER_PROMPT.md | UIUX design | `04_GLOBAL_SKILLS/UIUX_DESIGN/VISUAL/VISUAL_DESIGN_EXPERTISE.md` | MOVE + RENAME |
| 05_UX_RESEARCH_MASTER_PROMPT.md | UIUX design | `04_GLOBAL_SKILLS/UIUX_DESIGN/RESEARCH/UX_RESEARCH.md` | MOVE + RENAME |
| 09_SAAS_DASHBOARD_DESIGN_MASTER_PROMPT.md | UIUX design | `04_GLOBAL_SKILLS/UIUX_DESIGN/SAAS_DASHBOARDS/DASHBOARD_EXPERTISE.md` | MOVE + RENAME |
| 14_PRODUCT_DESIGN_SYSTEMS_MASTER_PROMPT.md | UIUX design | `04_GLOBAL_SKILLS/UIUX_DESIGN/PRODUCT_DESIGN/PRODUCT_DESIGN_EXPERTISE.md` | MOVE + RENAME |

#### UIUX Frameworks (2)
| File | Current | New | Action |
|------|---------|-----|--------|
| 25_TAILWIND_ENTERPRISE_CONSTITUTION.md | Build Tools | `04_GLOBAL_SKILLS/UIUX_DESIGN/TAILWIND/TAILWIND_EXPERTISE.md` | MOVE + RENAME |
| 26_SHADCN_UI_ENTERPRISE_CONSTITUTION.md | Build Tools | `04_GLOBAL_SKILLS/UIUX_DESIGN/SHADCN_UI/SHADCN_EXPERTISE.md` | MOVE + RENAME |

#### Backend Services Skills (4)
| File | Current | New | Action |
|------|---------|-----|--------|
| 08_SCALABILITY_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/BACKEND_ARCHITECTURE/SCALABILITY/SCALABILITY_PATTERNS.md` | MOVE + RENAME |
| 09_OBSERVABILITY_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/BACKEND_ARCHITECTURE/OBSERVABILITY/OBSERVABILITY_PATTERNS.md` | MOVE + RENAME |
| 10_BACKGROUND_JOBS_EVENTS_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/BACKEND_ARCHITECTURE/ASYNC_JOBS/ASYNC_PATTERNS.md` | MOVE + RENAME |
| 12_STRIPE_PAYMENTS_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/PAYMENT_SYSTEMS/STRIPE/STRIPE_INTEGRATION.md` | MOVE + RENAME |

#### Specialized Skills (5)
| File | Current | New | Action |
|------|---------|-----|--------|
| 18_MULTI_TENANCY_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/MULTI_TENANCY/BACKEND/MULTI_TENANCY_PATTERNS.md` | MOVE + RENAME |
| 19_SAAS_ARCHITECTURE_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/SAAS_ARCHITECTURE/SAAS_PATTERNS.md` | MOVE + RENAME |
| 20_ENTERPRISE_INTEGRATION_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/INTEGRATION/ENTERPRISE/ENTERPRISE_PATTERNS.md` | MOVE + RENAME |
| 23_DATA_ENGINEERING_MASTER_PROMPT.md | Backend Constitution | `04_GLOBAL_SKILLS/DATA_ENGINEERING/DATA_PIPELINE_EXPERTISE.md` | MOVE + RENAME |
| 27_ZOD_ENTERPRISE_CONSTITUTION.md | Build Tools | `04_GLOBAL_SKILLS/VALIDATION/ZOD/ZOD_EXPERTISE.md` | MOVE + RENAME |

#### Dev Tools Skills (2)
| File | Current | New | Action |
|------|---------|-----|--------|
| 04_GIT_GITHUB_MASTER_PROMPT.md | Build Tools | `04_GLOBAL_SKILLS/VERSION_CONTROL/GIT_GITHUB/GIT_WORKFLOWS.md` | MOVE + RENAME |
| 08_BUILD_PERFORMANCE_MASTER_PROMPT.md | Build Tools | `04_GLOBAL_SKILLS/BUILD_TOOLS/PERFORMANCE/BUILD_OPTIMIZATION.md` | MOVE + RENAME |

#### Testing Skills (2)
| File | Current | New | Action |
|------|---------|-----|--------|
| 10_PERFORMANCE_TESTING_CONSTITUTION.md | Testing | `04_GLOBAL_SKILLS/TESTING/PERFORMANCE/PERFORMANCE_TESTING.md` | MOVE + RENAME |
| 14_CHAOS_ENGINEERING_CONSTITUTION.md | Testing | `04_GLOBAL_SKILLS/TESTING/CHAOS_ENGINEERING/CHAOS_EXPERTISE.md` | MOVE + RENAME |

---

### F: AI AGENTS (6 existing → 8 with 2 new)

#### Existing Agents (6 files to move)
| File | Current | New | Action |
|------|---------|-----|--------|
| MASTER_SYSTEM_PROMPT.md | Frontend Constitution | `05_AI_AGENTS/FRONTEND_ARCHITECT/ROLE.md` | MOVE + RENAME |
| 25_ENTERPRISE_ARCHITECT_REVIEW_MASTER_PROMPT.md | Backend Constitution | `05_AI_AGENTS/PRINCIPAL_ARCHITECT/ROLE.md` | MOVE + RENAME |
| 29_FRONTEND_ARCHITECT_REVIEW_BOARD.md | Build Tools | `05_AI_AGENTS/FRONTEND_ARCHITECT/AUTHORITY.md` | MOVE + RECLASSIFY |
| 30_PRINCIPAL_TYPESCRIPT_ARCHITECT_BOARD.md | Build Tools | `05_AI_AGENTS/TYPESCRIPT_ARCHITECT/AUTHORITY.md` | MOVE + CREATE NEW AGENT |
| 12_DATABASE_ARCHITECT_REVIEW_MASTER_PROMPT.md | Database and API | `05_AI_AGENTS/DATABASE_ARCHITECT/ROLE.md` | MOVE + RENAME |
| 20_PRINCIPAL_TEST_ARCHITECT_REVIEW_BOARD.md | Testing | `07_REVIEW_BOARDS/TESTING/CHARTER.md` | MOVE + RECLASSIFY |

#### New Agents to Create (2)
| Agent | Path | Description |
|-------|------|-------------|
| Backend Architect | `05_AI_AGENTS/BACKEND_ARCHITECT/` | Backend system design authority |
| Security Architect | `05_AI_AGENTS/SECURITY_ARCHITECT/` | Security governance authority |

---

### G: REVIEW BOARDS (6 existing → 8 formal)

#### Formal Review Boards (Move & Formalize)
| Board | Current Files | New Path | Action |
|-------|--------------|----------|--------|
| Testing | 20_PRINCIPAL_TEST_ARCHITECT_REVIEW_BOARD.md | `07_REVIEW_BOARDS/TESTING/CHARTER.md` | MOVE + FORMALIZE |
| Frontend | 29_FRONTEND_ARCHITECT_REVIEW_BOARD.md | `07_REVIEW_BOARDS/FRONTEND/CHARTER.md` | MOVE + FORMALIZE |
| Backend | None | `07_REVIEW_BOARDS/BACKEND/CHARTER.md` | CREATE |
| Database | 12_DATABASE_ARCHITECT_REVIEW_MASTER_PROMPT.md | `07_REVIEW_BOARDS/DATABASE/CHARTER.md` | MOVE + FORMALIZE |
| Enterprise | 25_ENTERPRISE_ARCHITECT_REVIEW_MASTER_PROMPT.md | `07_REVIEW_BOARDS/ENTERPRISE_ARCHITECTURE/CHARTER.md` | MOVE + FORMALIZE |
| Engineering | 10_ENGINEERING_ARCHITECT_REVIEW_MASTER_PROMPT.md | `07_REVIEW_BOARDS/ENGINEERING/CHARTER.md` | MOVE + FORMALIZE |
| Security | None | `07_REVIEW_BOARDS/SECURITY/CHARTER.md` | CREATE |
| TypeScript | 30_PRINCIPAL_TYPESCRIPT_ARCHITECT_BOARD.md | `07_REVIEW_BOARDS/TYPESCRIPT/CHARTER.md` | MOVE + FORMALIZE |

---

### H: DOMAIN CONSTITUTIONS (9 files organized)

| File | Current | New | Action |
|------|---------|-----|--------|
| 01_FRONTEND_CONSTITUTION.md | Frontend Constitution | `08_DOMAIN_CONSTITUTIONS/01_FRONTEND/CONSTITUTION.md` | MOVE |
| 01_BACKEND_ENGINEERING_CONSTITUTION_MASTER_PROMPT.md | Backend Constitution | `08_DOMAIN_CONSTITUTIONS/02_BACKEND/CONSTITUTION.md` | MOVE + RENAME |
| 01_DATABASE_API_CONSTITUTION.md | Database and API | `08_DOMAIN_CONSTITUTIONS/03_DATABASE_API/CONSTITUTION.md` | MOVE |
| 01_TEST_ARCHITECTURE_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/CONSTITUTION.md` | MOVE |
| 01_STATE_MANAGEMENT_CONSTITUTION_MASTER_PROMPT.md | State Management | `08_DOMAIN_CONSTITUTIONS/05_STATE_MANAGEMENT/CONSTITUTION.md` | MOVE + RENAME |
| 01_UI_UX_DESIGN_CONSTITUTION_MASTER_PROMPT.md | UIUX design | `08_DOMAIN_CONSTITUTIONS/06_UIUX/CONSTITUTION.md` | MOVE + RENAME |
| 01_BUILD_TOOLS_DEVELOPMENT_CONSTITUTION.md | Build Tools | `08_DOMAIN_CONSTITUTIONS/07_BUILD_TOOLS/CONSTITUTION.md` | MOVE |
| HOSTING_DEPLOYMENT_CONSTITUTION_MASTER_PROMPT.md | Hosting and Deployments | `08_DOMAIN_CONSTITUTIONS/08_HOSTING_DEPLOYMENT/CONSTITUTION.md` | MOVE + RENAME |
| 21_TYPESCRIPT_SUPREME_CONSTITUTION.md | Build Tools | `08_DOMAIN_CONSTITUTIONS/09_TYPESCRIPT/CONSTITUTION.md` | MOVE |

#### Testing Sub-constitutions (10 files)
| File | Current | New | Action |
|------|---------|-----|--------|
| 02_UNIT_TESTING_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/UNIT/CONSTITUTION.md` | MOVE |
| 03_COMPONENT_TESTING_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/COMPONENT/CONSTITUTION.md` | MOVE |
| 04_INTEGRATION_TESTING_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/INTEGRATION/CONSTITUTION.md` | MOVE |
| 05_API_TESTING_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/API/CONSTITUTION.md` | MOVE |
| 06_CONTRACT_TESTING_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/CONTRACT/CONSTITUTION.md` | MOVE |
| 07_E2E_TESTING_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/E2E/CONSTITUTION.md` | MOVE |
| 08_ACCESSIBILITY_TESTING_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/ACCESSIBILITY/CONSTITUTION.md` | MOVE |
| 11_DATABASE_TESTING_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/DATABASE/CONSTITUTION.md` | MOVE |
| 12_MULTI_TENANT_TESTING_CONSTITUTION.md | Testing | `08_DOMAIN_CONSTITUTIONS/04_TESTING/MULTI_TENANT/CONSTITUTION.md` | MOVE |

---

### I: GOVERNANCE (10 files)

| File | Current | New | Action |
|------|---------|-----|--------|
| 06_AI_CODING_GOVERNANCE_MASTER_PROMPT.md | Build Tools | `09_GOVERNANCE/AI_CODING/AI_CODING_GOVERNANCE.md` | MOVE + RENAME |
| 15_RELEASE_READINESS_CONSTITUTION.md | Testing | `09_GOVERNANCE/RELEASE_READINESS/RELEASE_GOVERNANCE.md` | MOVE + RENAME |
| 16_AI_TESTING_GOVERNANCE_CONSTITUTION.md | Testing | `09_GOVERNANCE/AI_TESTING/AI_TESTING_GOVERNANCE.md` | MOVE + RENAME |
| 17_PR_REVIEW_CONSTITUTION.md | Testing | `09_GOVERNANCE/PR_REVIEW/PR_REVIEW_GOVERNANCE.md` | MOVE + RENAME |
| 18_DEFECT_MANAGEMENT_CONSTITUTION.md | Testing | `09_GOVERNANCE/DEFECT_MANAGEMENT/DEFECT_GOVERNANCE.md` | MOVE + RENAME |
| 19_QA_GOVERNANCE_CONSTITUTION.md | Testing | `09_GOVERNANCE/QA/QA_GOVERNANCE.md` | MOVE + RENAME |
| 21_COMPLIANCE_GOVERNANCE_MASTER_PROMPT.md | Backend Constitution | `09_GOVERNANCE/COMPLIANCE/COMPLIANCE_GOVERNANCE.md` | MOVE + RENAME |
| 22_FINOPS_COST_ENGINEERING_MASTER_PROMPT.md | Backend Constitution | `09_GOVERNANCE/FINOPS/FINANCIAL_OPERATIONS.md` | MOVE + RENAME |
| 24_PLATFORM_ENGINEERING_MASTER_PROMPT.md | Backend Constitution | `09_GOVERNANCE/PLATFORM_ENGINEERING/PLATFORM_GOVERNANCE.md` | MOVE + RENAME |
| 07_DEVELOPER_EXPERIENCE_MASTER_PROMPT.md | Build Tools | `09_GOVERNANCE/DEVELOPER_EXPERIENCE/DX_GOVERNANCE.md` | MOVE + RENAME |

---

### J: WORKFLOWS TO CREATE (6 new)

| Workflow | Path | Description |
|----------|------|-------------|
| Feature Development | `06_WORKFLOWS/FEATURE_DEVELOPMENT/WORKFLOW.md` | End-to-end feature delivery |
| Code Review | `06_WORKFLOWS/CODE_REVIEW/WORKFLOW.md` | PR review process |
| Security Review | `06_WORKFLOWS/SECURITY_REVIEW/WORKFLOW.md` | Security audit workflow |
| Architecture Review | `06_WORKFLOWS/ARCHITECTURE_REVIEW/WORKFLOW.md` | Architecture decision process |
| Deployment | `06_WORKFLOWS/DEPLOYMENT/WORKFLOW.md` | Release deployment process |
| Incident Response | `06_WORKFLOWS/INCIDENT_RESPONSE/WORKFLOW.md` | Emergency response procedures |

---

### K: PROJECT CONTEXT TO CREATE (8 new)

| Document | Path | Description |
|----------|------|-------------|
| Business Context | `10_PROJECT_CONTEXT/BUSINESS_CONTEXT.md` | Vision, mission, goals |
| User Personas | `10_PROJECT_CONTEXT/USER_PERSONAS.md` | Target users and personas |
| Architecture Decisions | `10_PROJECT_CONTEXT/ARCHITECTURE_DECISIONS.md` | ADRs and tech decisions |
| Bounded Contexts | `10_PROJECT_CONTEXT/BOUNDED_CONTEXTS.md` | DDD bounded contexts |
| Product Roadmap | `10_PROJECT_CONTEXT/PRODUCT_ROADMAP.md` | Product evolution |
| NFRs | `10_PROJECT_CONTEXT/ENTERPRISE_NFRS.md` | Non-functional requirements |
| Tech Stack | `10_PROJECT_CONTEXT/TECH_STACK_DECISIONS.md` | Technology selections |
| System Context | `10_PROJECT_CONTEXT/SYSTEM_ARCHITECTURE_DECISIONS.md` | System design decisions |

---

### L: REFERENCE KNOWLEDGE TO CREATE (15+ new)

**Design Patterns (5 files)**
**Templates (5 files)**
**Checklists (5 files)**
**Examples (3+ files)**

---

## EXECUTION CHECKLIST

### Pre-Migration (This Week)
- [ ] All stakeholders review classification
- [ ] Domain experts sign off on moves
- [ ] Migration script prepared
- [ ] Rollback plan documented
- [ ] Cross-reference validator built
- [ ] Git repository branched (migration branch)

### Migration Phase (Weeks 2-4)
- [ ] Delete duplicates
- [ ] Create new folder structure
- [ ] Move/rename files by category
- [ ] Update all internal cross-references
- [ ] Validate no file loss
- [ ] Create backwards compatibility layer
- [ ] Test with Copilot/Cursor

### Post-Migration (Weeks 5-8)
- [ ] Create all new governance files
- [ ] Create all new workflow files
- [ ] Create all new agent role files
- [ ] Create project context documents
- [ ] Create reference knowledge library
- [ ] Update master README
- [ ] Create navigation guides

### Launch (Weeks 9-16)
- [ ] Final validation
- [ ] Team training materials
- [ ] Role-specific guides
- [ ] FAQ documentation
- [ ] Public announcement
- [ ] Monitor adoption

---

## SUCCESS INDICATORS

**Week 2:** All files classified and migrations planned  
**Week 4:** Folder structure created, migrations tested  
**Week 6:** All 124 files migrated, no errors  
**Week 8:** New governance files created  
**Week 12:** All documentation complete  
**Week 16:** Full launch, 80% team adoption

---

**Status:** Ready for execution  
**Next Step:** Steering committee approval and Phase 1 kickoff

