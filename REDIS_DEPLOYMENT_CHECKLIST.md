# CRIMEKIT REDIS DEPLOYMENT CHECKLIST
**Document Version:** 1.0.0  
**Target Engine:** Redis 7.x (e.g. AWS ElastiCache for Redis)  
**Broker Implementation:** Redis Streams (NOT Celery / NOT RabbitMQ)  

---

## 1. Engine & Connectivity Specifications

* **Version:** Redis 7.0 or higher.
* **Port:** 6379.
* **Protocol:** `redis://` or `rediss://` (TLS encrypted in production).
* **Connection String:**
  `redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB:-0}`
* **Authentication:** Require strong password/auth token (`AUTH <token>`).

---

## 2. Redis Streams Topology

CrimeKit's distributed task queue is implemented in `backend/app/distributed/__init__.py`.

* **Priority Stream Names:**
  - `crimekit:tasks:critical`: High-priority real-time analysis (e.g., active face sighting alerts).
  - `crimekit:tasks:high`: Immediate evidence processing and timeline reconstruction.
  - `crimekit:tasks:normal`: Standard document OCR and batch hashing.
  - `crimekit:tasks:low`: Deep unallocated space carving, archival re-indexing.
* **Dead-Letter Queue:**
  - `crimekit:dlq`: Dead-letter stream storing payloads after `CRIMEKIT_MAX_RETRIES=6` failed attempts with exponential backoff (`BACKOFF_BASE=1s`, `BACKOFF_MAX=30s`).
* **Consumer Group:**
  - Group name: `crimekit-workers`.
  - Consumers: Automatically registered as `worker-{uuid[:8]}`.
* **Progress & Heartbeats:**
  - `crimekit:progress:{job_id}`: Hash tracking active task percentage and stages.
  - `crimekit:worker:{id}:hb`: Heartbeat key with TTL of 30 seconds (`CRIMEKIT_HEARTBEAT_TTL=30`).

---

## 3. Realtime Pub/Sub Channels

* `crimekit:events:case:{case_id}`: Case-scoped knowledge graph mutations and forensic updates.
* `crimekit:forensic:{case_id}:{evidence_id}`: Granular TSK filesystem traversal and stage milestones.
* Subscribed by `backend/app/realtime_relay.py` and broadcast to WebSocket clients.

---

## 4. Eviction & Persistence Configuration

* **Maxmemory Policy:** `volatile-lru` or `noeviction` for task streams.
  - **CRITICAL:** Do NOT use `allkeys-lru`, or Redis may silently evict pending forensic jobs from Redis Streams under memory pressure!
* **AOF (Append Only File):** Enable AOF persistence (`appendonly yes`, `appendfsync everysec`) to ensure zero task loss on container restart.

---

## 5. Third-Party Queue Verification

* **Celery:** NOT used (explicitly omitted in codebase).
* **RabbitMQ / Kafka:** NOT required.
* **Temporal:** NOT imported or required by active codebase.
