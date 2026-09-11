# Backup Guide

## Overview
CrimeKit provides automated backup scripts for all data stores.

## Backup Components
1. PostgreSQL database
2. Neo4j graph database
3. MinIO object storage
4. Configuration files

## Running Backups

### Full Backup
```bash
./infrastructure/scripts/backup.sh
```

### Manual PostgreSQL Backup
```bash
docker compose exec postgres pg_dump -U crimekit_app -Fc crimekit > backup_$(date +%Y%m%d).dump
```

### Manual MinIO Backup
```bash
docker run --rm -v minio_data:/data -v /backups/minio:/backup alpine tar czf /backup/minio_$(date +%Y%m%d).tar.gz -C /data .
```

## Backup Storage
- Local: `/backups/` directory
- Remote: Configure MINIO_BACKUP_BUCKET for off-site
- Recommended: Daily rotation, 30-day retention

## Verification
```bash
# Verify backup integrity
sha256sum /backups/postgres/crimekit_*.dump

# Test restore (to temp database)
docker compose exec postgres pg_restore -U crimekit_app -d crimekit_test /backups/postgres/crimekit_latest.dump
```

## Backup Automation
Add to crontab:
```bash
0 2 * * * /path/to/infrastructure/scripts/backup.sh >> /var/log/crimekit-backup.log 2>&1
```
