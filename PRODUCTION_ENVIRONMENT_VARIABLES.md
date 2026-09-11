# CRIMEKIT PRODUCTION ENVIRONMENT VARIABLES
**Document Version:** 1.0.0  
**Security Policy:** Variable names and specifications ONLY. Zero plaintext secret values.  

---

## 1. Frontend Environment Variables (Build-Time Embedded)

| Variable | Required? | Purpose | Default / Example Format |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | **Yes** | Public HTTPS endpoint for CrimeKit FastAPI backend | `https://api.crimekit.yourdomain.com` |
| `NEXT_PUBLIC_WS_URL` | **Yes** | Public WSS endpoint for real-time WebSocket events | `wss://api.crimekit.yourdomain.com` |
| `NEXT_PUBLIC_DESCOPE_PROJECT_ID` | **Yes** | Descope Project ID for Enterprise OIDC authentication | String identifier from Descope Console |
| `NEXT_PUBLIC_AUTH_DEMO_MODE` | **Yes** | Disable demo/test auth in production | `false` |
| `NEXT_PUBLIC_REQUEST_TIMEOUT_MS` | No | Axios client request timeout in milliseconds | `30000` |

---

## 2. Backend Server & Security Configuration (Secrets Manager)

| Variable | Secret? | Required? | Purpose |
|---|---|---|---|
| `APP_ENV` | No | Yes | Application environment flag (`production`) |
| `APP_DEBUG` | No | Yes | Debug mode (`false`) |
| `APP_LOG_LEVEL` | No | Yes | Logging level (`info` or `warning`) |
| `PORT` | No | Yes | Internal listening port (`8002`) |
| `CORS_ORIGINS` | No | Yes | Comma-separated list of allowed origins (e.g. Catalyst domain) |
| `JWT_SECRET_KEY` | **YES** | **Yes** | 64-character random string for internal JWT signing |
| `JWT_ALGORITHM` | No | Yes | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Yes | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | Yes | `7` |

---

## 3. Database Credentials (PostgreSQL + pgvector)

| Variable | Secret? | Required? | Purpose |
|---|---|---|---|
| `POSTGRES_HOST` | No | Yes | RDS Endpoint hostname |
| `POSTGRES_PORT` | No | Yes | `5432` |
| `POSTGRES_DB` | No | Yes | Database name (`crimekit`) |
| `POSTGRES_USER` | No | Yes | Application user (`crimekit_app`) |
| `POSTGRES_PASSWORD` | **YES** | **Yes** | RDS database password |
| `DATABASE_URL` | **YES** | **Yes** | Full connection URL (`postgresql://user:pass@host:5432/db`) |
| `DB_POOL_SIZE` | No | Yes | SQLAlchemy connection pool size (`10` to `20`) |
| `DB_MAX_OVERFLOW` | No | Yes | Maximum overflow connections (`20`) |

---

## 4. Redis Configuration (ElastiCache)

| Variable | Secret? | Required? | Purpose |
|---|---|---|---|
| `REDIS_HOST` | No | Yes | ElastiCache Redis primary endpoint |
| `REDIS_PORT` | No | Yes | `6379` |
| `REDIS_PASSWORD` | **YES** | **Yes** | Redis authentication token |
| `REDIS_DB` | No | Yes | `0` |
| `REDIS_URL` | **YES** | **Yes** | Full Redis URL (`redis://:pass@host:6379/0`) |

---

## 5. Neo4j Configuration (AuraDB)

| Variable | Secret? | Required? | Purpose |
|---|---|---|---|
| `NEO4J_URI` | No | Yes | Bolt connection URI (`neo4j+s://<dbid>.databases.neo4j.io`) |
| `NEO4J_USER` | No | Yes | Username (`neo4j`) |
| `NEO4J_PASSWORD` | **YES** | **Yes** | Neo4j AuraDB instance password |

---

## 6. Object Storage (AWS S3)

| Variable | Secret? | Required? | Purpose |
|---|---|---|---|
| `AWS_DEFAULT_REGION` | No | Yes | Target AWS region (`ap-south-1`) |
| `S3_ENDPOINT_URL` | No | No | Custom S3 endpoint (omit in AWS to use standard regional endpoint) |
| `AWS_ACCESS_KEY_ID` | **YES** | Yes (if IAM role not used) | S3 access key |
| `AWS_SECRET_ACCESS_KEY` | **YES** | Yes (if IAM role not used) | S3 secret access key |
| `EVIDENCE_BUCKET` | No | Yes | Primary evidence bucket (`crimekit-evidence-prod`) |
| `DOCUMENTS_BUCKET` | No | Yes | Parsed documents bucket (`crimekit-documents-prod`) |
| `REPORTS_BUCKET` | No | Yes | Court reports bucket (`crimekit-court-reports-prod`) |

---

## 7. Authentication & AI Integrations

| Variable | Secret? | Required? | Purpose |
|---|---|---|---|
| `DESCOPE_PROJECT_ID` | No | Yes | Descope Project ID |
| `DESCOPE_MANAGEMENT_KEY` | **YES** | **Yes** | Descope Management API Key for RBAC syncing |
| `EMBEDDING_PROVIDER` | No | Yes | `deterministic` (default) or `openai` |
| `OPENAI_API_KEY` | **YES** | Optional | OpenAI API key for text-embedding-3-small |
| `GLINER_MODEL` | No | Optional | HuggingFace model (`urchade/gliner_mediumv2.1`) |
| `BLOCKCHAIN_ENABLED` | No | Optional | Enable Polygon evidence anchoring (`false` by default) |
