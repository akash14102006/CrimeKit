# CrimeKit — Nebius AI Cloud Production Deployment Architecture

This directory defines production-grade deployment manifests and serverless configurations for hosting **CrimeKit** on **Nebius AI Cloud** with **NVIDIA Nemotron** inference acceleration.

---

## 1. Architecture Overview

```
                      Investigator Browser (Next.js)
                                     │
                                     ▼
                     Nebius Ingress / Load Balancer
                                     │
               ┌─────────────────────┼─────────────────────┐
               ▼                                           ▼
   CrimeKit FastAPI Backend                    Nebius Serverless Jobs
   (Multi-Agent REST & WS)                     (Heavy Forensics & Extraction)
               │                                           │
       ┌───────┴───────┐                           ┌───────┴───────┐
       ▼               ▼                           ▼               ▼
  PostgreSQL         Redis                    Apache Tika       Speech NIM
   (pgvector)       (PubSub)                  (Metadata)         (Audio ASR)
               │
               ▼
   NVIDIA NemoClaw / OpenShell Security Boundary
               │
               ▼
      NeMo Agent Toolkit Tracing
               │
               ▼
   Nebius Token Factory Gateway
   (nvidia/nemotron-4-340b-instruct)
```

---

## 2. Directory Structure

- `backend/Dockerfile`: Container image for FastAPI backend with forensic dependencies (`pytsk3`, `tika`, `gliner`).
- `workers/celery-worker.yaml`: Manifest for asynchronous forensic processing queues.
- `agent-runtime/runtime-deployment.yaml`: Scalable agent runtime with NeMo Agent Toolkit and OpenShell sandbox.
- `agent-runtime/serverless-job-forensics.yaml`: Nebius Serverless Job specification for deep disk and multimedia parsing.

---

## 3. Environment Configuration

| Variable | Description | Example / Production Value |
| :--- | :--- | :--- |
| `NEBIUS_API_KEY` | Nebius Token Factory Auth Token | `secret:nebius-token-factory-key` |
| `NEBIUS_BASE_URL` | Nebius Token Factory Gateway URL | `https://api.tokenfactory.nebius.com/v1` |
| `NEBIUS_MODEL` | Flagship Nemotron Model Name | `nvidia/nemotron-4-340b-instruct` |
| `TAVILY_API_KEY` | Tavily External Search API Key | `secret:tavily-api-key` |
| `NVIDIA_SPEECH_NIM_URL` | Self-hosted or Cloud Speech NIM | `http://speech-nim.nebius.internal:9000/v1` |
| `AGENT_RUNTIME_MODE` | Runtime execution strategy | `live` |

---

## 4. Deployment Steps

```bash
# 1. Build and push backend image to Nebius Container Registry
docker build -t cr.nebius.cloud/crimekit/backend:latest -f deployment/nebius/backend/Dockerfile .
docker push cr.nebius.cloud/crimekit/backend:latest

# 2. Apply Kubernetes manifests
kubectl apply -f deployment/nebius/backend/
kubectl apply -f deployment/nebius/workers/
kubectl apply -f deployment/nebius/agent-runtime/

# 3. Verify AI Provider Gateway Connectivity
curl -s https://api.crimekit.ai/api/v1/ai/provider/health | jq .
```
