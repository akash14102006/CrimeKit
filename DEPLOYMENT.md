# CrimeKit — Enterprise Deployment Guide

## Overview
This document describes how to deploy CrimeKit locally (Docker Compose), in Kubernetes clusters, to AWS (`ap-south-1`), and how the frontend is hosted via Zoho Catalyst.

---

## 1. Local Development (Docker Compose)

### Prerequisites
- Docker Desktop / Engine 24+
- Docker Compose v2.20+

### Quickstart
```bash
# 1. Clone repository
git clone <repo-url>
cd crimekit

# 2. Configure environment
cp .env.example .env

# 3. Start complete local stack (Postgres, Redis, MinIO, Neo4j, Backend, Nginx)
docker compose up -d

# 4. Verify service health
docker compose ps
curl http://localhost:8002/health
```

### Running Frontend Locally
```bash
cd frontend
npm install
npm run dev
# Accessible at http://localhost:3000
```

---

## 2. Frontend Production Deployment: Zoho Catalyst Web Client

The CrimeKit frontend is architected as a Next.js 16 application with static export (`output: "export"`), producing pure static assets in `frontend/out/`.

### Deployment Steps
```bash
# 1. Build Next.js static output
cd frontend
npm ci
npm run build

# 2. Deploy static client to Zoho Catalyst
cd ..
catalyst deploy --only client
```

`catalyst.json` is configured as:
```json
{
  "client": {
    "source": "frontend/out"
  }
}
```

---

## 3. Cloud Production Architecture: AWS (ap-south-1 Mumbai)

When deploying to cloud infrastructure:
1. **Terraform**: Located in `infrastructure/terraform/`.
   ```bash
   cd infrastructure/terraform
   cp terraform.tfvars.example terraform.tfvars
   # Fill in production values
   terraform init
   terraform plan -out=tfplan
   terraform apply tfplan
   ```
2. **Kubernetes (Helm)**: Located in `k8s/charts/crimekit/`.
   ```bash
   helm upgrade --install crimekit k8s/charts/crimekit \
     --namespace crimekit \
     --create-namespace \
     --values k8s/charts/crimekit/values.yaml
   ```
3. **Database Migrations**:
   ```bash
   python -m alembic upgrade head
   ```
