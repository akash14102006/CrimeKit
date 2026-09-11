# Troubleshooting Guide

## Common Issues

### Backend Won't Start
```bash
# Check logs
docker compose logs backend

# Common causes:
# - Database not ready (wait for postgres health check)
# - Missing environment variables
# - Port already in use
```

### Database Connection Refused
```bash
# Check postgres status
docker compose ps postgres

# Check logs
docker compose logs postgres

# Verify credentials match .env
docker compose exec postgres psql -U crimekit_app -d crimekit -c "SELECT 1"
```

### Redis Connection Failed
```bash
# Check redis status
docker compose exec redis redis-cli -a $REDIS_PASSWORD ping
```

### Neo4j Won't Start
```bash
# Check memory allocation
docker compose exec neo4j free -m

# Check logs
docker compose logs neo4j

# Verify password
docker compose exec neo4j cypher-shell -u neo4j -p $NEO4J_PASSWORD "RETURN 1"
```

### MinIO Bucket Creation Failed
```bash
# Check minio is ready
curl http://localhost:9000/minio/health/live

# Manually run init
docker compose run --rm minio-init
```

### Nginx 502 Bad Gateway
```bash
# Backend may not be ready
docker compose logs nginx

# Check backend health
curl http://localhost:8000/health

# Restart nginx
docker compose restart nginx
```

### High Memory Usage
```bash
# Check container stats
docker stats

# Adjust resource limits in docker-compose.yml
```

## Debug Mode
```bash
# Enable debug logging
export APP_LOG_LEVEL=debug
docker compose restart backend

# Check database queries
export APP_DEBUG=true
```

## Getting Help
1. Check service logs: `docker compose logs <service>`
2. Run health check: `./infrastructure/scripts/health-check.sh`
3. Review this guide
4. Check GitHub issues
