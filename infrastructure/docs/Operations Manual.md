# Operations Manual

## Daily Operations

### Health Checks
```bash
# Run health check script
./infrastructure/scripts/health-check.sh --verbose

# Check via API
curl http://localhost:8000/health/detailed
```

### Log Viewing
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail 100 backend
```

### Performance Monitoring
- Grafana dashboard: http://localhost:3000
- Prometheus: http://localhost:9090
- Backend metrics: http://localhost:8000/metrics (if enabled)

## Common Operations

### Restart a Service
```bash
docker compose restart backend
```

### Scale Backend
```bash
docker compose up -d --scale backend=3
```

### Database Maintenance
```bash
# PostgreSQL vacuum
docker compose exec postgres vacuumdb -U crimekit_app crimekit

# Redis memory check
docker compose exec redis redis-cli -a $REDIS_PASSWORD info memory
```

### Update Services
```bash
docker compose pull
docker compose up -d --remove-orphans
```

## Incident Response
1. Check health endpoints
2. Review service logs
3. Check resource usage
4. Scale if needed
5. Restart if necessary
6. Escalate if unresolved
