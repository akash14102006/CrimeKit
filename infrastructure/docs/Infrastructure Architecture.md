# CrimeKit Infrastructure Architecture

## Overview
CrimeKit runs on a containerized microservices architecture using Docker Compose.

## Components
- **Backend**: FastAPI Python 3.12 application (uvicorn)
- **PostgreSQL 16**: Primary relational database with pgvector
- **Redis 7**: Caching, sessions, rate limiting, pub/sub
- **Neo4j 5**: Knowledge graph database
- **MinIO**: S3-compatible object storage for evidence/files
- **Nginx**: Reverse proxy, TLS termination, rate limiting
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

## Network Architecture
All services communicate via the `crimekit_network` Docker bridge network.
External access is through Nginx on ports 80/443.

## Data Flow
1. Client -> Nginx (TLS termination, rate limiting)
2. Nginx -> Backend (reverse proxy, WebSocket upgrade)
3. Backend -> PostgreSQL (persistence)
4. Backend -> Redis (caching, sessions)
5. Backend -> Neo4j (knowledge graph)
6. Backend -> MinIO (file storage)

## Security Layers
- Network isolation (Docker bridge)
- Non-root containers
- Secrets management via environment variables
- TLS at Nginx layer
- Authentication via JWT
- RBAC authorization

## Scalability
- Horizontal: Scale backend containers behind Nginx
- Vertical: Increase resource limits per service
- Database: PostgreSQL read replicas
- Cache: Redis Sentinel/Cluster
- Storage: MinIO distributed mode
