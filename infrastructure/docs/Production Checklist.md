# Production Checklist

## Pre-Deployment

### Security
- [ ] All default passwords changed
- [ ] .env file secured (chmod 600)
- [ ] JWT_SECRET_KEY is 64+ chars random
- [ ] APP_SECRET_KEY is 64+ chars random
- [ ] MinIO access/secret keys are secure
- [ ] Neo4j password is secure
- [ ] Redis password is set
- [ ] PostgreSQL password is secure

### Configuration
- [ ] APP_ENV=production
- [ ] APP_DEBUG=false
- [ ] APP_LOG_LEVEL=warning
- [ ] UVICORN_WORKERS=4 (or higher)
- [ ] CORS_ORIGINS set to your domain
- [ ] BACKUP_RETENTION_DAYS configured

### Infrastructure
- [ ] Docker Compose files validated
- [ ] All images built and tagged
- [ ] Persistent volumes mapped to reliable storage
- [ ] Nginx SSL configured (if TLS required)
- [ ] Resource limits set appropriately

### Data
- [ ] MinIO buckets initialized
- [ ] Database migrations run
- [ ] Default roles created
- [ ] Backup schedule configured

## Deployment

### Steps
1. `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`
2. `docker compose ps` (all healthy)
3. `curl http://localhost:8000/health/detailed`
4. `./infrastructure/scripts/health-check.sh`
5. Verify logs are structured JSON

## Post-Deployment

### Verification
- [ ] Backend health endpoint returns 200
- [ ] Database connection pool active
- [ ] Redis responding
- [ ] Neo4j connected (if configured)
- [ ] MinIO buckets accessible
- [ ] Nginx routing correctly
- [ ] No error logs
- [ ] Monitoring dashboards showing data

### Monitoring
- [ ] Prometheus scraping targets
- [ ] Grafana dashboards loaded
- [ ] Alert rules configured
- [ ] Log aggregation working

### Backup
- [ ] Backup script tested
- [ ] Backup schedule verified
- [ ] Restore procedure tested

## Ongoing Operations

### Daily
- [ ] Check health endpoints
- [ ] Review error logs
- [ ] Monitor resource usage

### Weekly
- [ ] Review backup integrity
- [ ] Check disk space
- [ ] Review security alerts

### Monthly
- [ ] Update Docker images
- [ ] Review access logs
- [ ] Test disaster recovery
