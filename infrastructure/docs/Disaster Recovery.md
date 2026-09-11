# Disaster Recovery

## Recovery Time Objectives
- **RTO**: 1 hour (target)
- **RPO**: 1 hour (with hourly backups)

## Backup Schedule
- PostgreSQL: Daily at 02:00 UTC, retained 30 days
- Neo4j: Daily at 03:00 UTC, retained 30 days
- MinIO: Weekly mirror to secondary location
- Configs: On every deployment

## Recovery Procedures

### PostgreSQL Recovery
```bash
# List available backups
ls -la /backups/postgres/

# Restore specific backup
docker compose exec postgres pg_restore -U crimekit_app -d crimekit -c /backups/postgres/crimekit_YYYYMMDD_HHMMSS.dump
```

### Neo4j Recovery
```bash
# Stop Neo4j
docker compose stop neo4j

# Restore data volume
docker compose run --rm -v neo4j_data:/data -v /backups/neo4j:/backup neo4j neo4j-admin database import full --from=/backup/neo4j_YYYYMMDD

# Start Neo4j
docker compose start neo4j
```

### Full Stack Recovery
```bash
# Stop all services
docker compose down

# Restore volumes
./infrastructure/scripts/restore.sh --component all --backup-file /backups/latest/

# Start services
docker compose up -d
```

## Failover Procedures
1. PostgreSQL: Promote read replica
2. Redis: Failover to Sentinel
3. Neo4j: Restore from backup
4. MinIO: Switch to secondary site
