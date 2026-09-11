# CRIMEKIT DEPLOYMENT READINESS REPORT
**Document Version:** 1.0.0-STEP0  
**Audit Date:** 2026-09-10  
**Status:** STEP 0 AUDIT COMPLETE — AWAITING USER APPROVAL  
**Roles:** Principal Software Architect, DevOps Engineer, Security Engineer  

---

## 1. Repository Summary

A comprehensive, non-destructive discovery was conducted across the entire CrimeKit repository. The repository is an enterprise-grade digital forensics, AI investigation, and knowledge graph intelligence platform.

### Repository Tree & Organization
```
c:\Users\akash\Downloads\Enterprise grade - CrimeKit - front error
├── .catalystrc                      # Zoho Catalyst project configuration (Project: CodeMafiaweb3)
├── catalyst.json                    # Catalyst deployment map (client source: "frontend/out")
├── Makefile                         # Automation targets for build, test, docker, clean
├── docker-compose.yml               # Base multi-container definition (pg, redis, neo4j, minio, backend)
├── docker-compose.prod.yml          # Production resource limits and logging overrides
├── docker-compose.dev.yml           # Development tooling overrides
├── .env.example                     # Reference environment template
├── .env.development.example         # Development defaults
├── .env.production.example          # Production template with security guidelines
├── .github/                         # CI/CD workflows (GitHub Actions: ci.yml, backend-tests.yml, infra-validate.yml)
├── k8s/charts/crimekit/             # Production Kubernetes Helm chart (Deployment, Service, Ingress, PDB)
├── infrastructure/                  # Infrastructure configurations
│   ├── nginx/                       # Nginx reverse proxy configs (rate-limiting, WS upgrades, SSL)
│   ├── postgres/                    # Database init script (init.sql: extensions, roles, permissions)
│   ├── redis/                       # Redis configuration (redis.conf: persistence, memory policies)
│   ├── neo4j/                       # Neo4j configs and Cypher constraints initialization
│   ├── minio/                       # MinIO bucket initialization scripts
│   └── monitoring/                  # Prometheus scraping rules and pre-provisioned Grafana dashboards
├── frontend/                        # Next.js 16.2.12 + React 19.2.4 Web Application
│   ├── package.json                 # UI dependencies (@descope/react-sdk, @xyflow/react, recharts, zustand)
│   ├── next.config.ts               # Next.js config (configured with output: "export")
│   ├── client-package.json          # Catalyst client packaging definition (type: "basic")
│   └── src/                         # Application source code
│       ├── app/                     # Next.js App Router (dashboard, cases, evidence, workspace, graph)
│       ├── features/                # Domain features (cases, evidence, graph, timeline, disk-analyzer)
│       └── lib/                     # API client (Axios with Descope JWT interceptor), WebSocket client
├── backend/                         # FastAPI 0.109+ Core Backend Engine
│   ├── Dockerfile                   # Multi-stage production OCI build (Python 3.12-slim + C forensic libs)
│   ├── requirements.txt             # Locked Python dependencies
│   ├── alembic/                     # Database migrations (alembic.ini, versions/)
│   └── app/                         # Application modules
│       ├── main.py                  # FastAPI entrypoint, middleware, lifespan startup/shutdown
│       ├── database.py              # SQLAlchemy 2.0 connection pool and session factory
│       ├── models.py                # Database models (User, Case, Evidence, Embedding, AuditLog)
│       ├── auth.py                  # Descope OIDC JWT validation and local RBAC auto-provisioning
│       ├── processing.py            # Local forensic worker loop and job orchestration
│       ├── distributed/             # Redis Streams distributed task queue (NOT Celery)
│       ├── realtime_relay.py        # Redis Pub/Sub to WebSocket event relay
│       ├── websocket_manager.py     # Stateful WebSocket connection manager (/ws/case/{case_id})
│       ├── kg.py                    # Neo4j Bolt knowledge graph client with provenance tracking
│       ├── storage/                 # Boto3 S3-compatible storage with WORM Object Lock
│       ├── search/                  # 3-tier enterprise search (Postgres FTS, OpenSearch, Vector)
│       ├── tsk_engine/              # The Sleuth Kit (pytsk3) & libewf native disk forensic worker
│       ├── entity_extractor.py      # GLiNER ML-based token classification & regex fallback
│       └── compliance/              # Legal hold, retention schedules, immutable audit logging
├── Facial Recognition implemention planning/ # 16 authoritative specifications for Face Trace subsystem
└── Planning/                        # Master design documents (Constitution, Architecture, Backend)
```

---

## 2. Actual Runtime Architecture

CrimeKit's actual runtime is built upon a high-performance, modular forensic pipeline:

```
[ BROWSER CLIENT ]
       |
       +--- HTTPS (Static SPA Assets) ----> [ Zoho Catalyst CDN Hosting ] (frontend/out)
       |
       +--- HTTPS REST & WSS -------------> [ Nginx Reverse Proxy / Load Balancer ]
                                                          |
                                                          v
                                            [ FastAPI Backend API Service ]
                                            - Descope OIDC JWT Auth & RBAC
                                            - REST Endpoints & Presigned URLs
                                            - WebSocket Gateway (/ws/case/{id})
                                            - Realtime Relay (Redis Pub/Sub)
                                                          |
                 +----------------------------------------+----------------------------------------+
                 |                                        |                                        |
                 v                                        v                                        v
     [ Redis In-Memory Bus ]                  [ PostgreSQL 16 Database ]                  [ Neo4j Graph Database ]
     - Streams: Task Queues                   - Relational Tables & Audits                - Graph Topology (Bolt: 7687)
     - Pub/Sub: Realtime Events               - pgvector 512-d & 1536-d Vectors           - Cross-case Provenance
     - Token Blocklist & Cache                - PostgreSQL Full-Text Search               - Entity Relationships
                 |                                        ^                                        ^
                 v (Task Claim)                           | (Write Results)                        | (Cypher Ingest)
     [ Forensic Worker Pool ] ----------------------------+----------------------------------------+
     - pytsk3 & libewf (Disk Image Analysis)
     - Tesseract & Poppler (OCR & Document Parsing)
     - GLiNER (Named Entity Recognition)
     - InsightFace (Face Detection & ArcFace Embeddings)
                 |
                 v (Presigned Upload / Download / WORM Object Lock)
     [ AWS S3 / MinIO Object Storage ]
     - crimekit-evidence / crimekit-documents / crimekit-court-reports
```

---

## 3. Frontend Readiness

### Configuration & Tooling
- **Framework:** Next.js 16.2.12 with React 19.2.4.
- **Export Mode:** Configured with `output: "export"` in `frontend/next.config.ts`.
- **Target Output Directory:** `frontend/out` (as mapped in `catalyst.json`).
- **Dependencies:** `@descope/react-sdk`, `@descope/nextjs-sdk`, `@xyflow/react` (v12.11.5), `@tanstack/react-query`, `axios`, `recharts`, `tailwindcss` v4.

### Local Verification Run Results
1. **Type Check (`npm run type-check`):**
   - **Command:** `tsc --noEmit`
   - **Result:** **PASSED (Exit Code 0)**. Zero TypeScript compile errors across the entire UI codebase.
2. **Production Build (`npm run build`):**
   - **Command:** `next build`
   - **Result:** **FAILED (Exit Code 1)** during the page data collection phase.
   - **Exact Error:**
     ```
     Error: Page "/ai/[caseId]" is missing "generateStaticParams()" so it cannot be used with "output: export" config.
     ```
   - **Root Cause:** Next.js with `output: "export"` requires that every dynamic route (`[caseId]`, `[evidenceId]`) either export `generateStaticParams()` (even returning an empty array `[]` for client-side hydration) or avoid static export mode. The repository contains 5 dynamic routes:
     - `frontend/src/app/(dashboard)/ai/[caseId]`
     - `frontend/src/app/(dashboard)/cases/[caseId]`
     - `frontend/src/app/(dashboard)/disk-analyzer/[evidenceId]`
     - `frontend/src/app/(dashboard)/evidence/[evidenceId]`
     - `frontend/src/app/(dashboard)/workspace/[caseId]`
   - **Status:** **P0 Deployment Blocker**. Must be addressed before running `catalyst deploy`.

### Environment & URL Configuration
- **API URL:** Handled dynamically via `api-client.ts` in `getBaseUrl()`:
  - If `NEXT_PUBLIC_API_URL` is set, it is used.
  - Fallback: `http://${window.location.hostname}:8002`.
- **WebSocket URL:** Configured via `NEXT_PUBLIC_WS_URL`.
- **Descope Project ID:** Configured via `NEXT_PUBLIC_DESCOPE_PROJECT_ID`.

---

## 4. Backend Readiness

### Runtime & Entrypoint
- **Framework:** FastAPI with Uvicorn standard.
- **Python Version:** Python 3.12.6 verified.
- **Entrypoint:** `python -m uvicorn app.main:app --host 0.0.0.0 --port 8002`.
- **Health Endpoints:** `/health` (system liveness/readiness), `/health/ready`, `/health/live`.

### Dependency Audit
- **Core Dependencies (Verified in venv):**
  - `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `redis`, `boto3`, `descope`, `neo4j`, `web3` $\rightarrow$ **INSTALLED & VERIFIED (Exit Code 0)**.
- **Native Forensic C Libraries:**
  - `pytsk3` (The Sleuth Kit C bindings): **OK (installed in local venv)**.
  - `libewf` (Expert Witness Compression Format): **MISSING locally on Windows**; installed in production Linux container via `libewf2` apt package.
  - `pytesseract` (Tesseract OCR): **MISSING locally on Windows**; installed in production Linux container via `tesseract-ocr` apt package.
- **Containerization Assessment:**
  - The production multi-stage [backend/Dockerfile](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/Dockerfile) cleanly installs all required native packages (`libtsk19t64`, `libewf2`, `tesseract-ocr`, `poppler-utils`) under non-root user `crimekit` (UID 1000).

---

## 5. Worker Readiness

### Architecture Findings
- **Message Broker:** **Redis Streams** (NOT Celery). Explicitly confirmed in [backend/app/distributed/__init__.py:9](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/distributed/__init__.py#L9):
  - Stream topology: `crimekit:tasks:critical`, `crimekit:tasks:high`, `crimekit:tasks:normal`, `crimekit:tasks:low`.
  - Dead-letter stream: `crimekit:dlq`.
  - Consumer group: `crimekit-workers`.
- **Local Fallback Worker:** [backend/app/processing.py](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/processing.py) implements an in-process thread pool worker (`WORKER_POOL_SIZE=4`) with database row-level locking (`SELECT FOR UPDATE`) for lightweight dev/test deployments.
- **Long-running Jobs:** Forensic disk image analysis and OCR tasks are offloaded asynchronously; job status is tracked in the `forensic_jobs` table and published to Redis Pub/Sub.

---

## 6. Database Readiness

### PostgreSQL & Extensions
- **Engine:** PostgreSQL 16.
- **Required Extensions (from `infrastructure/postgres/init.sql`):**
  - `uuid-ossp`: UUID generation.
  - `pgcrypto`: Cryptographic hashing and key management.
  - `pg_trgm`: Trigram indexing for fuzzy text search.
  - `btree_gist`: GIST index support.
  - `vector`: pgvector extension for high-dimensional vector similarity.
- **Migrations:** Managed via Alembic (`backend/alembic/`).
  - Base revision: `a8e67154f876_initial.py` (roles, users, cases, evidence, custody, jobs).
  - Migration script: `001_add_blockchain_tables.py`.
  - Automated sync: `database.init_db()` calls `Base.metadata.create_all()` on startup, creating all models across compliance, multitenancy, and blockchain modules.

---

## 7. Redis Readiness

### Realtime & Queue Topology
- **Version:** Redis 7.
- **Connection URL:** `REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}`.
- **Consumer Group:** `crimekit-workers` with `XREADGROUP` and `XACK`.
- **Pub/Sub Channels:**
  - `crimekit:events:case:{case_id}`: Knowledge graph node/edge mutations.
  - `crimekit:forensic:{case_id}:{evidence_id}`: TSK forensic progress updates.
- **Persistence Requirement:** AOF (Append-Only File) or scheduled RDB snapshots are required to ensure task stream durability across restarts.

---

## 8. Neo4j Readiness

### Knowledge Graph Architecture
- **Version:** Neo4j 5.
- **Connection URI:** `NEO4J_URI=bolt://neo4j:7687` (authenticated via `NEO4J_USER` and `NEO4J_PASSWORD`).
- **Driver:** Official Python `neo4j` driver v5.28.0.
- **Schema:**
  - Nodes: `Case`, `Evidence`, `Person`, `Phone`, `Email`, `Device`, `Location`, `Organization`, `IP_Address`, `Domain`, `TimelineEvent`.
  - Constraints: Unique constraints on `(name, type)` per entity.
  - Provenance: Every relationship and entity node records `evidence_id`, `case_id`, `confidence`, and `source`.
- **Fallback:** If Neo4j is offline, [backend/app/processing.py:250](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/processing.py#L250) records graph JSON structures directly into the `forensic_results` PostgreSQL table.

---

## 9. Object Storage Readiness

### S3 & Immutability Architecture
- **Client:** `boto3` v1.34+ wrapped inside [backend/app/storage/__init__.py](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/storage/__init__.py).
- **Target Buckets:**
  - `crimekit-evidence`: Raw forensic disk images, audio, video, phone extractions.
  - `crimekit-documents`: Extracted documents, OCR text buffers.
  - `crimekit-court-reports`: Court-admissible generated PDF reports.
  - `crimekit-ai-outputs`: Model artifacts and cropped face thumbnails.
  - `crimekit-backups`: System backups.
- **WORM Compliance:** Supports S3 Object Lock in Compliance Mode (WORM — Write Once, Read Many), guaranteeing digital evidence cannot be overwritten or deleted during legal hold periods.
- **Integrity:** SHA-256 checksums are verified upon upload completion before chain-of-custody logging.

---

## 10. Authentication Readiness

### Descope Enterprise IDP
- **Provider:** Descope OIDC/JWT.
- **Integration:** Verified active project ID `P3FF4lAVyrTtQeqlbuAeSdoCbrIX`.
- **Backend Flow:** [backend/app/auth.py](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/auth.py) validates the incoming Bearer token using the Descope SDK and auto-provisions or syncs user records into PostgreSQL.
- **Roles & RBAC:** 8 enterprise roles (`admin`, `investigator`, `analyst`, `viewer`, `evidence_officer`, `compliance_officer`, `auditor`, `user`).
- **Token Invalidation:** Redis-backed token blocklist in [security/token_blacklist.py](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/security/token_blacklist.py).

---

## 11. AI Readiness

### Architecture & Providers
- **Local NER:** GLiNER (`urchade/gliner_mediumv2.1`) for token-level entity extraction with zero external API calls. Falls back to comprehensive regex patterns if model is uninitialized.
- **Embeddings:** Dual-mode provider in [backend/app/embeddings.py](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/embeddings.py):
  1. `DeterministicProvider` (Default): Built-in SHA-256 pseudo-embedding (32-dim) with zero external cost.
  2. `OpenAIProvider`: Optional `text-embedding-3-small` (1536-dim) via `OPENAI_API_KEY`.
- **LLM Independence:** No local LLM hosting required. The platform uses targeted NLP extractors and optional SaaS LLM APIs for summarization.

---

## 12. Face Trace Readiness

### Subsystem Specification (from `Facial Recognition implemention planning/`)
- **Status:** Architecture and specification complete; implementation planned for Phase 8.
- **Engine:** ONNX Runtime executing SCRFD (detector) and ArcFace (`buffalo_l` 512-dim recognizer).
- **Compute Sizing:**
  - **Demo / Light:** CPU mode with ONNX Runtime CPU EP (~2–5 FPS).
  - **Production Video:** GPU acceleration (`g4dn.xlarge` NVIDIA T4 with TensorRT in AWS Mumbai `ap-south-1`) for real-time 30 FPS multi-stream RTSP CCTV analysis.
- **Storage:** Feature vectors indexed in PostgreSQL via pgvector HNSW cosine distance.

---

## 13. WebSocket Readiness

### Realtime Streaming Pipeline
- **Endpoint:** `wss://api.crimekit.yourdomain.com/ws/case/{case_id}?token={jwt}`.
- **Authentication:** JWT verified on handshake connection; case-level RBAC verified in `_verify_case_access`.
- **Relay Worker:** [backend/app/realtime_relay.py](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/realtime_relay.py) runs as an asyncio background task subscribed to Redis Pub/Sub channels `crimekit:events:case:*` and forwards events to connected browser sessions.
- **Hosting Constraint:** Requires a proxy/load balancer that supports HTTP/1.1 WebSocket upgrades with long-lived idle timeouts (1200s+).

---

## 14. Security Findings

1. **Hardcoded Secrets Audit:**
   - Development files contain loose placeholder credentials (e.g. `dev-jwt-secret-key...`, `crimekit_dev_password`).
   - `.env.production.example` clearly requires strong random secrets for production.
   - **No live production credentials or private keys are exposed in git.**
2. **CORS Hardening:**
   - Backend [main.py:82](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/main.py#L82) allows `catalystserverless.in` and `catalystappsail.in` domains. Must ensure the final production frontend domain is explicitly listed in `CORS_ORIGINS`.
3. **Evidence Protection:**
   - S3 buckets must enforce S3 Object Lock and SSE-KMS encryption.

---

## 15. Environment Variables Required

*(Variable names only — zero secret values printed)*

| Variable Name | Consumer | Type | Required in Production? |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | Frontend | Public | Yes |
| `NEXT_PUBLIC_WS_URL` | Frontend | Public | Yes |
| `NEXT_PUBLIC_DESCOPE_PROJECT_ID` | Frontend | Public | Yes |
| `NEXT_PUBLIC_AUTH_DEMO_MODE` | Frontend | Public | No (Set to `false`) |
| `APP_ENV` | Backend | Internal | Yes (`production`) |
| `APP_DEBUG` | Backend | Internal | Yes (`false`) |
| `DATABASE_URL` | Backend / Workers | Secret | Yes |
| `POSTGRES_USER` | Backend / DB | Internal | Yes |
| `POSTGRES_PASSWORD` | Backend / DB | Secret | Yes |
| `REDIS_URL` | Backend / Workers | Secret | Yes |
| `REDIS_PASSWORD` | Backend / Redis | Secret | Yes |
| `NEO4J_URI` | Backend / Workers | Internal | Yes |
| `NEO4J_USER` | Backend / Neo4j | Internal | Yes |
| `NEO4J_PASSWORD` | Backend / Neo4j | Secret | Yes |
| `S3_ENDPOINT_URL` / `MINIO_ENDPOINT` | Backend / Workers | Internal | Yes |
| `AWS_ACCESS_KEY_ID` / `MINIO_ACCESS_KEY` | Backend / Workers | Secret | Yes |
| `AWS_SECRET_ACCESS_KEY` / `MINIO_SECRET_KEY` | Backend / Workers | Secret | Yes |
| `EVIDENCE_BUCKET` | Backend / Workers | Internal | Yes |
| `JWT_SECRET_KEY` | Backend | Secret | Yes |
| `DESCOPE_PROJECT_ID` | Backend | Internal | Yes |
| `DESCOPE_MANAGEMENT_KEY` | Backend | Secret | Yes |
| `OPENAI_API_KEY` | Backend / Workers | Secret | Optional |
| `BLOCKCHAIN_ENABLED` | Backend | Internal | Optional (`false`) |

---

## 16. Docker & Infrastructure Requirements

- **Backend Dockerfile:** [backend/Dockerfile](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/Dockerfile) is multi-stage and production-ready.
- **Nginx Configuration:** [infrastructure/nginx/sites/default.conf](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/infrastructure/nginx/sites/default.conf) configures:
  - WebSocket upgrades (`Upgrade $http_upgrade`, `Connection "upgrade"`).
  - Rate limiting (10 req/s on `/api/`, 2 req/s on `/uploads/`).
  - Client max body size (500M).
- **Kubernetes Helm Charts:** [k8s/charts/crimekit/](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/k8s/charts/crimekit) provides full production manifests (HorizontalPodAutoscaler, PodDisruptionBudget, security contexts).

---

## 17. CI/CD Status

- **Workflow:** `.github/workflows/ci.yml`.
- **Automated Gates:**
  1. `lint`: Runs Black, isort, Ruff, and MyPy.
  2. `test`: Spins up ephemeral PostgreSQL 16 and Redis 7 service containers to execute pytest with coverage.
  3. `docker`: Builds and pushes OCI container images to GitHub Container Registry (`ghcr.io`).

---

## 18. Deployment Blockers

| Priority | Category | Blocker Description | Required Remediation |
|---|---|---|---|
| **P0** | Frontend Build | `next build` fails: dynamic routes (`[caseId]`, `[evidenceId]`) lack `generateStaticParams()` required by `output: "export"`. | Add `generateStaticParams()` returning `[]` to the 5 dynamic route pages to allow static HTML compilation. |
| **P0** | Catalyst Target | Directory `frontend/out` does not exist because the Next.js build failed. `catalyst deploy` will fail immediately. | Fix P0 build blocker and run `npm run build` to generate the `out/` artifact. |
| **P1** | Database | Production PostgreSQL database must have `vector` (pgvector) extension compiled and active. | Ensure target cloud database supports pgvector (e.g. AWS RDS PostgreSQL 16). |
| **P1** | Security | Production secrets (`JWT_SECRET_KEY`, database credentials, Descope Management Key) must be generated. | Store in AWS Secrets Manager or secure runtime environment. |
| **P2** | Native Binaries | `libewf` and `pytesseract` are missing in local Windows environment. | Must be deployed via the Linux container (`backend/Dockerfile`) where they are built from source. |
| **P3** | Search | OpenSearch is currently unprovisioned. | Non-blocking: PostgreSQL FTS (Tier 1) fulfills all search functionality. |
| **P4** | Documentation | Old planning documents reference Celery and Temporal. | Non-blocking: Active code runs on Redis Streams. Planning docs should be annotated accordingly. |

---

## 19. Recommended Hosting Architecture

### Primary Recommendation: **Balanced Hybrid Architecture**
- **Frontend:** **Zoho Catalyst Web Client Hosting** (Serving `frontend/out` via global CDN).
  - *Project:* `CodeMafiaweb3` (ID `20246000000010171`).
  - *Custom Domain / HTTPS:* Configured via Catalyst Web Client console.
- **Backend API & Forensic Workers:** **AWS ECS Fargate** (in `ap-south-1` Mumbai).
  - Containers built from [backend/Dockerfile](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/Dockerfile).
  - Handles native C libraries (`libtsk`, `libewf`, `tesseract`) with complete process isolation.
  - Sits behind an Application Load Balancer with WebSocket upgrade support.
- **Databases & Caches:**
  - **Relational & Vectors:** **AWS RDS for PostgreSQL 16 Multi-AZ** (with pgvector).
  - **Message Broker & Pub/Sub:** **AWS ElastiCache for Redis 7**.
  - **Knowledge Graph:** **Neo4j AuraDB Professional** (or self-hosted Neo4j on EC2).
- **Object Storage:** **AWS S3** with S3 Object Lock (Compliance mode WORM) and KMS encryption.

---

## 20. Estimated Monthly Cost

| Tier | Monthly Estimate | Details |
|---|---|---|
| **₹0 / Free Possible** | **₹0 / month** | Zoho Catalyst Free Tier (Web Client CDN) + Descope Free Tier (7,500 MAUs) + Local/Dev SQLite/MinIO/Docker. |
| **Low Cost (Demo / Staging)** | **~$80 – $140 / month** | Catalyst Web Client (Free) + AWS App Runner / single ECS task ($30) + RDS `db.t4g.medium` ($40) + ElastiCache `cache.t4g.medium` ($25) + Neo4j AuraDB Free + S3 ($5). |
| **Heavy Production** | **~$450 – $850 / month** | Multi-AZ RDS PostgreSQL 16 `db.m6g.xlarge` ($300) + Multi-AZ Redis ($100) + ECS Auto-scaling Worker Pool ($100) + S3 WORM ($30) + Neo4j AuraDB Pro ($150) + Optional EC2 Spot GPU `g4dn.xlarge` for Face Trace ($120). |

*First Likely Cost Trigger:* Provisioning a Multi-AZ managed PostgreSQL instance on AWS RDS.

---

## 21. Deployment Order

When authorized, execute in the following exact sequence:

```
 1. Fix P0 Frontend Static Export blocker (add generateStaticParams to 5 dynamic routes).
 2. Run local frontend build validation (`npm run build`) -> verifies `frontend/out` creation.
 3. Verify Zoho Catalyst CLI authentication and project binding (`CodeMafiaweb3`).
 4. Provision AWS VPC, subnets, and security groups in `ap-south-1` (Mumbai).
 5. Provision AWS S3 Buckets with S3 Object Lock enabled.
 6. Provision AWS RDS PostgreSQL 16 instance and execute extension init (`init.sql` + pgvector).
 7. Provision AWS ElastiCache for Redis cluster (Redis Streams broker).
 8. Provision Neo4j AuraDB instance and initialize Cypher schema constraints.
 9. Store production secrets in AWS Secrets Manager.
10. Build backend container image via Docker Buildx and push to Amazon ECR.
11. Run Alembic database migrations against RDS PostgreSQL.
12. Deploy backend API service to AWS ECS Fargate behind Application Load Balancer.
13. Deploy distributed forensic worker tasks to AWS ECS Fargate.
14. Deploy frontend to Zoho Catalyst: `catalyst deploy --only client`.
15. Configure Route 53 DNS records and SSL certificates (ACM & Catalyst Custom Domain).
16. Run End-to-End verification: User Login -> Evidence Upload -> S3 WORM -> Forensic TSK/OCR -> Neo4j Graph -> WebSocket Stream.
```

---

## 22. STEP 1 PREREQUISITES

Before any deployment command or cloud resource modification in Step 1, the following must be confirmed:
1. **Approval of this Step 0 Report.**
2. **Approval to patch the 5 dynamic Next.js routes** (`[caseId]`, `[evidenceId]`) with `generateStaticParams()` to allow `output: "export"` to build cleanly into `frontend/out`.
3. **Confirmation of the Zoho Catalyst project target** (`CodeMafiaweb3` vs creating a new dedicated project).
4. **Cloud credentials provisioned** for target infrastructure (AWS / RDS / S3).

---
*STEP 0 COMPLETE. AWAITING USER APPROVAL TO PROCEED.*
