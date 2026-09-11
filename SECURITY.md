# CrimeKit — Security Architecture & Threat Model

## 1. Security Principles
1. **Separation of Concerns**: Forensic data is immutable and cryptographically verified. AI outputs are treated as derived analysis/hypotheses and never overwrite or alter original evidence.
2. **Defense in Depth**: Security controls operate at the network layer (VPC/Security Groups), application layer (FastAPI security headers, rate limiting, JWT validation), database layer (parameterized queries, tenant isolation rules), and storage layer (S3 WORM / Object Lock).
3. **Least Privilege**: Role-Based Access Control (RBAC) is enforced on all endpoints on the server side. Frontend UI checks are strictly for UX, not security boundaries.

---

## 2. RBAC Permission Matrix

| Role | Cases | Evidence Upload | Forensic Jobs | AI Query | Legal Hold / Export | User Admin |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Admin** | Full | Full | Full | Full | Full | Full |
| **Investigator** | Own / Assigned | Read/Write | Submit / View | Full | View | None |
| **Analyst** | Assigned | Read-Only | Run Deep Analysis | Full | None | None |
| **Evidence Officer** | Assigned | Custody Log | View Status | None | Custody Management | None |
| **Compliance Officer** | Audit All | Read-Only | Read-Only | None | Legal Hold / Export | None |
| **Auditor** | Read-Only | Read-Only | Read-Only | None | Audit Logs Only | None |
| **Viewer** | Assigned | Read-Only | Read-Only | Read-Only | None | None |

---

## 3. Threat Mitigation Matrix

| Threat Category | Potential Attack | Mitigation in CrimeKit |
| :--- | :--- | :--- |
| **Forensic Tampering** | Bit flip or timestamp rewrite in disk image | Merkle tree anchoring, SHA-256 verification before/after processing, blockchain ledger. |
| **Cross-Case Data Leak** | Investigator queries Case A and receives Case B evidence | Vector retrieval filters strictly by `case_id`; SQL queries enforce `tenant_id` and `case_id` predicates. |
| **Malicious Uploads** | ZIP bomb, executable disguised as image | Non-executable sandboxed extraction, strict MIME sniffing via magic bytes, chunked streaming limits. |
| **Credential & Key Exposure** | Hardcoded secrets in client or repo | `.gitignore` ignores `.env`, zero private keys in repo, credentials injected via environment/Secrets Manager. |
| **Denial of Service** | Gigabyte upload exhaustion | Streaming pipeline with connection pooling and chunk-based hashing without loading full file to RAM. |
| **SQL Injection** | Parameter tampering | 100% SQLAlchemy ORM parameterized queries; raw SQL is strictly banned across all routers. |
| **API Abuse** | Brute force or API flooding | In-memory and Redis token-bucket rate limiting middleware (`RateLimitMiddleware`). |
