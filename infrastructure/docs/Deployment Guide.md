# Deployment Guide

## Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.20+
- 8GB RAM minimum (16GB recommended)
- 50GB disk space

## Quick Start (Development)
```bash
# Clone repository
git clone <repo-url>
cd crimekit

# Copy environment file
cp .env.example .env

# Start services
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Access services
# Backend API: http://localhost:8000
# Nginx: http://localhost:80
# pgAdmin: http://localhost:5050
# Neo4j Browser: http://localhost:7474
# MinIO Console: http://localhost:9001
```

## Production Deployment
```bash
# Use production compose
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With monitoring
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile monitoring up -d
```

## First-Time Setup
1. Copy `.env.example` to `.env`
2. Generate secure passwords for all services
3. Update JWT_SECRET_KEY and APP_SECRET_KEY
4. For production, update .env.production.example values
5. Run: `docker compose up -d`
6. Verify: `docker compose ps` (all services healthy)
7. Initialize MinIO buckets: `docker compose run --rm minio-init`

## SSL/TLS Setup
1. Place certs in `infrastructure/nginx/ssl/`
2. Update `infrastructure/nginx/sites/default.conf` to enable HTTPS
3. Restart nginx: `docker compose restart nginx`
