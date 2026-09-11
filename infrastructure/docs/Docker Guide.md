# Docker Guide

## Architecture
CrimeKit uses Docker Compose v2 with multiple profiles.

## Profiles
- **default**: Core services (backend, postgres, redis, neo4j, minio, nginx)
- **monitoring**: Prometheus + Grafana
- **dev-tools**: pgAdmin, Redis Commander, Neo4j Browser

## Building Images

### Backend (Production)
```bash
docker build -t crimekit-backend -f backend/Dockerfile backend/
```

### Backend (Development)
```bash
docker build -t crimekit-backend-dev -f backend/Dockerfile.dev backend/
```

## Running Services

### Development
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile dev-tools up -d
```

### Production
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### With Monitoring
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile monitoring up -d
```

## Container Management

### View Running Containers
```bash
docker compose ps
```

### View Resource Usage
```bash
docker stats
```

### Restart a Service
```bash
docker compose restart backend
```

### Scale Backend
```bash
docker compose up -d --scale backend=3
```

### Enter a Container
```bash
docker compose exec backend bash
docker compose exec postgres psql -U crimekit_app crimekit
```

## Volumes
Named volumes for persistence:
- postgres_data: PostgreSQL data
- redis_data: Redis persistence
- neo4j_data: Neo4j graph data
- minio_data: Object storage
- backend_logs: Application logs

## Networking
All services on `crimekit_network` bridge.
External access via Nginx (ports 80/443).

## Cleanup
```bash
# Stop and remove containers
docker compose down

# Remove volumes (DELETES DATA)
docker compose down -v

# Remove unused images
docker image prune -a
```
