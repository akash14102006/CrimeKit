# CRIMEKIT FORENSIC WORKER DEPLOYMENT CHECKLIST
**Subsystem:** Distributed Forensic Worker Pool  
**Message Broker:** Redis Streams (`crimekit-workers` group)  
**Execution Runtime:** Docker OCI Container (Python 3.12 + C/C++ native forensic libraries)  

---

## 1. Workload Categorization & Resource Footprint

| Forensic Task | Libraries Involved | Resource Class | Memory Limit | Timeout |
|---|---|---|---|---|
| **Hashing & MIME** | Python `hashlib`, `mimetypes` | I/O-bound | 512 MB | 120s |
| **Document OCR** | `pytesseract`, `poppler-utils`, `pypdf` | CPU-heavy | 2048 MB | 600s |
| **Image Analysis** | `Pillow`, `ExifTags` | CPU-light | 1024 MB | 120s |
| **Disk Forensics (TSK)** | `pytsk3`, `libewf` | CPU & Disk-heavy | 4096 MB | 1800s |
| **Entity Extraction (NER)**| `GLiNER`, `torch`, `transformers` | CPU & RAM-heavy | 3072 MB | 300s |
| **Face Detection & ArcFace**| `onnxruntime`, `insightface` | GPU (or Heavy CPU)| 4096 MB | 600s |

---

## 2. Process Sandboxing & Safety Controls

As implemented in `backend/app/tsk_engine/worker.py:56`:
* **Worker Isolation:** Each disk forensic task runs under isolated process semantics with Linux `setrlimit` enforcing memory caps (`memory_limit_mb=2048`) and CPU limits (`cpu_limit_percent=80.0`).
* **Non-Root Execution:** Runs under UID 1000 (`crimekit:crimekit`).
* **Graceful Cancellation:** Listens to cancellation signals via Redis Streams and the `_cancelled_jobs` thread-safe registry.

---

## 3. Worker Sizing & Autoscaling

* **ECS Fargate Task Sizing:** 4 vCPU, 8GB RAM per worker task.
* **Autoscaling Policy:** Scale from 1 to 8 workers based on Redis Stream backlog:
  - Scale Up: When `crimekit:tasks:critical` + `crimekit:tasks:high` depth $> 10$.
  - Scale Down: When total stream depth $< 2$ for 5 minutes.
