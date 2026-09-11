#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/backup.log"
TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-crimekit}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"

NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-}"

MINIO_ENDPOINT="${MINIO_ENDPOINT:-localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minioadmin}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-minioadmin}"

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

log() {
  local msg="[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1"
  echo "$msg" | tee -a "$LOG_FILE"
}

die() {
  log "FATAL: $1"
  exit 1
}

setup_directories() {
  log "Creating backup directory structure..."
  for subdir in postgres neo4j minio configs; do
    mkdir -p "${BACKUP_DIR}/${subdir}"
  done
}

backup_postgres() {
  local dest="${BACKUP_DIR}/postgres/${TIMESTAMP}"
  mkdir -p "$dest"
  log "Starting PostgreSQL backup..."

  export PGPASSWORD="$POSTGRES_PASSWORD"

  local dump_file="${dest}/crimekit_${TIMESTAMP}.dump"
  if pg_dump \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -F c \
    -Z 9 \
    -f "$dump_file" 2>>"$LOG_FILE"; then
    log "PostgreSQL dump created: $dump_file"
  else
    die "PostgreSQL backup failed"
  fi

  log "Verifying PostgreSQL backup..."
  if pg_restore -l "$dump_file" > /dev/null 2>>"$LOG_FILE"; then
    log "PostgreSQL backup verified"
  else
    die "PostgreSQL backup verification failed"
  fi

  sha256sum "$dump_file" > "${dump_file}.sha256"
  log "PostgreSQL backup complete"
}

backup_neo4j() {
  local dest="${BACKUP_DIR}/neo4j/${TIMESTAMP}"
  mkdir -p "$dest"
  log "Starting Neo4j backup..."

  if command -v cypher-shell &>/dev/null; then
    local dump_file="${dest}/neo4j_${TIMESTAMP}.cypher"
    if cypher-shell \
      -u "$NEO4J_USER" \
      -p "$NEO4J_PASSWORD" \
      -a "$NEO4J_URI" \
      "CALL dbms.dump.query('YIELD cypher FROM queries RETURN cypher')" \
      > "$dump_file" 2>>"$LOG_FILE"; then
      log "Neo4j cypher dump created: $dump_file"
    else
      log "cypher-shell dump failed, attempting neo4j-admin..."
      backup_neo4j_admin "$dest"
    fi
  elif command -v neo4j-admin &>/dev/null; then
    backup_neo4j_admin "$dest"
  else
    die "No Neo4j backup tool available (neither cypher-shell nor neo4j-admin found)"
  fi

  local checksums=()
  for f in "${dest}"/*; do
    sha256sum "$f" > "${f}.sha256"
    checksums+=("${f}.sha256")
  done
  log "Neo4j backup complete"
}

backup_neo4j_admin() {
  local dest="$1"
  log "Using neo4j-admin for Neo4j backup..."
  local dump_file="${dest}/neo4j_${TIMESTAMP}.dump"
  if neo4j-admin database dump --to-path="$dump_file" crimekit 2>>"$LOG_FILE"; then
    log "Neo4j admin dump created: $dump_file"
  else
    die "Neo4j admin backup failed"
  fi
}

backup_minio() {
  local dest="${BACKUP_DIR}/minio/${TIMESTAMP}"
  mkdir -p "$dest"
  log "Starting MinIO backup..."

  export MINIO_ROOT_USER="$MINIO_ACCESS_KEY"
  export MINIO_ROOT_PASSWORD="$MINIO_SECRET_KEY"

  if command -v mc &>/dev/null; then
    mc alias set crimekit_backup "http://${MINIO_ENDPOINT}" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" 2>>"$LOG_FILE"
    if mc mirror --overwrite crimekit_backup "${dest}/data" 2>>"$LOG_FILE"; then
      log "MinIO mirror backup created"
    else
      die "MinIO mirror backup failed"
    fi
  else
    log "mc client not found, attempting tar of /data volumes..."
    if tar -czf "${dest}/minio_volumes_${TIMESTAMP}.tar.gz" \
      --exclude='*.lock' \
      --exclude='*.pid' \
      /data/minio 2>>"$LOG_FILE"; then
      log "MinIO tar backup created"
    else
      die "MinIO tar backup failed"
    fi
  fi

  for f in "${dest}"/*; do
    [ -f "$f" ] && sha256sum "$f" > "${f}.sha256"
  done
  log "MinIO backup complete"
}

backup_configs() {
  local dest="${BACKUP_DIR}/configs/${TIMESTAMP}"
  mkdir -p "$dest"
  log "Starting config backup..."

  local infra_dir="${SCRIPT_DIR}/../"
  local tar_file="${dest}/configs_${TIMESTAMP}.tar.gz"

  if tar -czf "$tar_file" \
    -C "$infra_dir" \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.log' \
    docker-compose.yml \
    .env* \
    nginx/ \
    postgres/ \
    neo4j/ \
    minio/ \
    2>>"$LOG_FILE"; then
    log "Config backup created: $tar_file"
  else
    die "Config backup failed"
  fi

  sha256sum "$tar_file" > "${tar_file}.sha256"
  log "Config backup complete"
}

verify_backup() {
  log "Verifying all backup checksums..."
  local failed=0
  while IFS= read -r -d '' checksum_file; do
    local dir
    dir="$(dirname "$checksum_file")"
    if (cd "$dir" && sha256sum -c "$(basename "$checksum_file")" 2>>"$LOG_FILE"); then
      log "Checksum OK: $(basename "${checksum_file%.sha256}")"
    else
      log "Checksum FAILED: $(basename "${checksum_file%.sha256}")"
      failed=1
    fi
  done < <(find "$BACKUP_DIR" -name "*.sha256" -type f -print0)

  if [ "$failed" -ne 0 ]; then
    die "Backup verification failed for one or more files"
  fi
  log "All checksums verified successfully"
}

generate_manifest() {
  local manifest="${BACKUP_DIR}/manifest_${TIMESTAMP}.json"
  log "Generating manifest: $manifest"

  local components=()
  [ -d "${BACKUP_DIR}/postgres/${TIMESTAMP}" ] && components+=("postgres")
  [ -d "${BACKUP_DIR}/neo4j/${TIMESTAMP}" ] && components+=("neo4j")
  [ -d "${BACKUP_DIR}/minio/${TIMESTAMP}" ] && components+=("minio")
  [ -d "${BACKUP_DIR}/configs/${TIMESTAMP}" ] && components+=("configs")

  local component_json="["
  local first=1
  for comp in "${components[@]}"; do
    [ "$first" -eq 1 ] && first=0 || component_json+=","
    component_json+="\"${comp}\""
  done
  component_json+="]"

  local all_checksums=()
  while IFS= read -r line; do
    local hash file
    hash=$(echo "$line" | awk '{print $1}')
    file=$(echo "$line" | awk '{print $2}')
    all_checksums+=("${file}:${hash}")
  done < <(find "${BACKUP_DIR}" -path "*/${TIMESTAMP}/*" -name "*.sha256" -exec cat {} \;)

  local checksum_json="["
  first=1
  for entry in "${all_checksums[@]}"; do
    [ "$first" -eq 1 ] && first=0 || checksum_json+=","
    checksum_json+="\"${entry}\""
  done
  checksum_json+="]"

  cat > "$manifest" <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "version": "1.0.0",
  "components": ${component_json},
  "checksums": ${checksum_json},
  "retention_days": ${RETENTION_DAYS},
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

  log "Manifest generated: $manifest"
}

cleanup_old_backups() {
  log "Cleaning up backups older than ${RETENTION_DAYS} days..."
  local count=0
  while IFS= read -r -d '' dir; do
    log "Removing old backup: $dir"
    rm -rf "$dir"
    count=$((count + 1))
  done < <(find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d -mtime +"$RETENTION_DAYS" -print0)

  while IFS= read -r -d '' manifest; do
    rm -f "$manifest"
  done < <(find "$BACKUP_DIR" -maxdepth 1 -name "manifest_*.json" -mtime +"$RETENTION_DAYS" -type f -print0)

  log "Removed ${count} old backup(s)"
}

main() {
  log "=========================================="
  log "CrimeKit Backup - Starting"
  log "Timestamp: ${TIMESTAMP}"
  log "=========================================="

  setup_directories
  backup_postgres
  backup_neo4j
  backup_minio
  backup_configs
  verify_backup
  generate_manifest
  cleanup_old_backups

  log "=========================================="
  log "CrimeKit Backup - Completed Successfully"
  log "=========================================="
}

trap 'die "Backup interrupted by signal"; exit 1' INT TERM

main
