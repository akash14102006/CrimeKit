# CrimeKit Infrastructure

Enterprise-grade containerized infrastructure for the CrimeKit Digital Forensics Platform.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx (80/443)                       │
│              TLS Termination / Rate Limiting                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     Backend (8000)                          │
│              FastAPI / Python 3.12                          │
└──┬──────────┬──────────┬──────────┬────────────────────────┘
   │          │          │          │
   ▼          ▼          ▼          ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐
│ PgSQL│ │Redis │ │Neo4j │ │  MinIO   │
│(5432)│ │(6379)│ │(7687)│ │(9000/9001│
└──────┘ └──────┘ └──────┘ └──────────┘
```

## Quick Start

### Development
```bash
# Copy environment file
cp .env.example .env

# Start all services with dev tools
make dev

# Or manually:
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile dev-tools up -d
```

### Production
```bash
# Copy and configure production environment
cp .env.production.example .env

# Start production stack
make prod

# Or manually:
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Backend | 8000 | FastAPI application |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache & sessions |
| Neo4j | 7474/7687 | Knowledge graph |
| MinIO | 9000/9001 | Object storage |
| Nginx | 80/443 | Reverse proxy |
| pgAdmin | 5050 | DB admin (dev) |
| Redis Commander | 6380 | Redis admin (dev) |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Dashboards |

## Directory Structure

```
infrastructure/
├── docker/           # Dockerfiles (backend)
├── compose/          # Docker Compose files (root level)
├── nginx/            # Nginx configuration
│   ├── nginx.conf
│   ├── sites/
│   └── conf.d/
├── postgres/         # PostgreSQL configuration
│   ├── init.sql
│   ├── postgresql.conf
│   └── pg_hba.conf
├── redis/            # Redis configuration
│   └── redis.conf
├── neo4j/            # Neo4j configuration
│   ├── neo4j.conf
│   └── init.cypher
├── minio/            # MinIO initialization
│   └── init.sh
├── monitoring/       # Prometheus & Grafana
│   ├── prometheus/
│   └── grafana/
├── scripts/          # Backup, restore, health
│   ├── backup.sh
│   ├── restore.sh
│   └── health-check.sh
├── docs/             # Documentation
└── terraform/        # Cloud deployment (AWS)
```

## Configuration

### Environment Files
- `.env.example` - Base configuration template
- `.env.production.example` - Production overrides
- `.env.development.example` - Development overrides

### Key Variables
| Variable | Description |
|----------|-------------|
| APP_ENV | Environment (development/production) |
| DATABASE_URL | PostgreSQL connection URL |
| REDIS_URL | Redis connection URL |
| NEO4J_URI | Neo4j bolt URI |
| JWT_SECRET_KEY | JWT signing key |
| MINIO_ACCESS_KEY | MinIO access key |

## Operations

### Health Checks
```bash
# Quick check
make health

# API health
make health-api

# Manual check
curl http://localhost:8000/health/detailed
```

### Backups
```bash
# Full backup
make db-backup

# Manual backup
./infrastructure/scripts/backup.sh
```

### Logs
```bash
# All services
make logs

# Backend only
make logs-backend
```

### Database
```bash
# PostgreSQL shell
make db-shell

# Run tests
make test
```

## Documentation

- [Infrastructure Architecture](docs/Infrastructure%20Architecture.md)
- [Deployment Guide](docs/Deployment%20Guide.md)
- [Disaster Recovery](docs/Disaster%20Recovery.md)
- [Operations Manual](docs/Operations%20Manual.md)
- [Environment Variables](docs/Environment%20Variables.md)
- [Backup Guide](docs/Backup%20Guide.md)
- [Troubleshooting Guide](docs/Troubleshooting%20Guide.md)
- [Docker Guide](docs/Docker%20Guide.md)
- [Production Checklist](docs/Production%20Checklist.md)

## Security

- All containers run as non-root users
- Secrets managed via environment variables
- Network isolation via Docker bridge
- TLS termination at Nginx
- Rate limiting on API endpoints
- Security headers configured

## Cloud Deployment

The `terraform/` directory contains AWS infrastructure scaffolding:
- VPC with public/private subnets
- RDS PostgreSQL
- S3 for evidence storage
- ECS/EKS for container orchestration

See [Terraform README](terraform/README.md) for details.
