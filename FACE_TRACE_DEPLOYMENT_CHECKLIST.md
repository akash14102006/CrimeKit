# CRIMEKIT FACE TRACE DEPLOYMENT CHECKLIST
**Subsystem:** Face Trace Investigator  
**Provider:** InsightFace / ONNX Runtime  
**Artifact Model:** `buffalo_l` (SCRFD detector + ArcFace recognizer)  

---

## 1. Subsystem Architecture & Models

* **Detector:** SCRFD (Sample and Computation Redistribution Face Detection) via ONNX Runtime.
* **Feature Extractor:** ArcFace generating 512-dimensional normalized FP32 embedding vectors.
* **Vector Matching:** PostgreSQL `embeddings` table with `pgvector` HNSW cosine distance index (`<=>`).
* **Similarity Thresholds:**
  - `VERIFIED_MATCH`: Cosine similarity $\ge 0.68$ (High confidence sighting).
  - `POTENTIAL_CANDIDATE`: Cosine similarity $0.50 - 0.67$ (Flagged for human investigator review).
  - `NON_MATCH`: Cosine similarity $< 0.50$.

---

## 2. Workload Classification & Hardware Sizing

| Workload Category | Typical Scenario | Minimum Hardware | Platform Recommendation |
|---|---|---|---|
| **LIGHT CPU** | Single photo comparison, passport scan, profile reference face | 2 vCPU, 4GB RAM | AWS ECS Fargate (Standard CPU) |
| **HEAVY CPU** | Short video clips (< 2 min), small batch of 50 images | 4–8 vCPU, 16GB RAM | AWS ECS Fargate (Compute Optimized) |
| **GPU REQUIRED** | Real-time CCTV / RTSP video streams (30 FPS), multi-hour evidentiary footage | 1x NVIDIA T4 GPU (16GB VRAM), 4 vCPU, 16GB RAM | **AWS EC2 `g4dn.xlarge`** (Mumbai `ap-south-1`) |

---

## 3. Model Storage & Licensing

* **Storage Path:** Model ONNX weights (`det_10g.onnx`, `w600k_r50.onnx`) stored at `/models/insightface/buffalo_l/`.
* **Container Delivery:** Pre-baked into GPU worker Docker image or mounted from Amazon EFS.
* **Commercial Compliance Gate:** The InsightFace Python codebase is MIT-licensed, but pre-trained model weights (`buffalo_l`) have specific non-commercial/research clauses; production commercial deployment requires verified licensing agreement or substitution with open-license ArcFace ONNX weights.
