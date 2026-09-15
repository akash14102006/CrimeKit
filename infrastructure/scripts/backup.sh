#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
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
NEO4J_DATABASE="${NEO4J_DATABASE:-neo4j}"
NEO4J_BACKUP_METHOD="${NEO4J_BACKUP_METHOD:-cypher}"

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

export_neo4j_cypher() {
  local out_file="$1"
  if command -v python3 &>/dev/null; then
    python3 - <<PYEOF 2>>"$LOG_FILE"
import subprocess
import sys

def run_cypher(q):
    cmd = [
        "cypher-shell",
        "-u", "${NEO4J_USER}",
        "-p", "${NEO4J_PASSWORD}",
        "-a", "${NEO4J_URI}",
        "-d", "${NEO4J_DATABASE}",
        "--format", "plain",
        q
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr)
        sys.exit(res.returncode)
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]

try:
    nodes = run_cypher("MATCH (n) RETURN labels(n)[0], properties(n);")
    rels = run_cypher("MATCH (a)-[r]->(b) RETURN labels(a)[0], a.id, type(r), labels(b)[0], b.id, properties(r);")
    with open("${out_file}", "w") as f:
        f.write("// Neo4j CrimeKit Export\n")
        f.write("// Database: ${NEO4J_DATABASE}\n")
        f.write("MATCH (n) DETACH DELETE n;\n")
        for line in nodes[1:]:
            parts = line.split(", ", 1)
            if len(parts) == 2:
                lbl = parts[0].strip('"')
                props = parts[1]
                f.write(f"CREATE (n:\`{lbl}\` {props});\n")
        for line in rels[1:]:
            parts = [p.strip().strip('"') for p in line.split(", ")]
            if len(parts) >= 5:
                a_lbl, a_id, r_type, b_lbl, b_id = parts[0], parts[1], parts[2], parts[3], parts[4]
                f.write(f"MATCH (a:\`{a_lbl}\` {{id: '{a_id}'}}), (b:\`{b_lbl}\` {{id: '{b_id}'}}) CREATE (a)-[:\`{r_type}\`]->(b);\n")
    sys.exit(0)
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)
PYEOF
  else
    return 1
  fi
}

backup_neo4j() {
  local dest="${BACKUP_DIR}/neo4j/${TIMESTAMP}"
  mkdir -p "$dest"
  log "Starting Neo4j backup (database: ${NEO4J_DATABASE})..."

  local backup_done=0

  # Strategy 1: Online Cypher export via cypher-shell
  if [ "${NEO4J_BACKUP_METHOD:-cypher}" != "admin" ] && command -v cypher-shell &>/dev/null; then
    local dump_file="${dest}/neo4j_${TIMESTAMP}.cypher"
    log "Attempting online Cypher graph export via cypher-shell..."
    if export_neo4j_cypher "$dump_file"; then
      log "Neo4j cypher dump created: $dump_file"
      backup_done=1
    else
      log "cypher-shell dump failed, attempting neo4j-admin..."
    fi
  fi

  # Strategy 2: Admin database dump (for offline/admin backups)
  if [ "$backup_done" -eq 0 ]; then
    if command -v neo4j-admin &>/dev/null; then
      backup_neo4j_admin "$dest"
      backup_done=1
    else
      die "No Neo4j backup tool available or backup failed"
    fi
  fi

  local checksums=()
  for f in "${dest}"/*; do
    [ -f "$f" ] && sha256sum "$f" > "${f}.sha256"
    checksums+=("${f}.sha256")
  done
  log "Neo4j backup complete"
}

backup_neo4j_admin() {
  local dest="$1"
  log "Using neo4j-admin for Neo4j backup (database: ${NEO4J_DATABASE})..."
  # Note: in Neo4j 5, --to-path expects a directory
  if neo4j-admin database dump --to-path="$dest" "$NEO4J_DATABASE" 2>>"$LOG_FILE"; then
    log "Neo4j admin dump created in: $dest"
  else
    die "Neo4j admin backup failed"
  fi
}

backup_minio() {
  local dest="${BACKUP_DIR}/minio/${TIMESTAMP}"
  mkdir -p "$dest"
  mkdir -p "${dest}/data"
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

  local tar_file="${dest}/configs_${TIMESTAMP}.tar.gz"

  local files_to_tar=()
  [ -f "${PROJECT_ROOT}/docker-compose.yml" ] && files_to_tar+=("docker-compose.yml")
  [ -f "${PROJECT_ROOT}/docker-compose.prod.yml" ] && files_to_tar+=("docker-compose.prod.yml")
  [ -f "${PROJECT_ROOT}/docker-compose.dev.yml" ] && files_to_tar+=("docker-compose.dev.yml")
  [ -f "${PROJECT_ROOT}/.env.example" ] && files_to_tar+=(".env.example")
  [ -f "${PROJECT_ROOT}/.env.production.example" ] && files_to_tar+=(".env.production.example")
  [ -f "${PROJECT_ROOT}/.env.development.example" ] && files_to_tar+=(".env.development.example")
  [ -d "${PROJECT_ROOT}/infrastructure" ] && files_to_tar+=("infrastructure")

  if [ "${#files_to_tar[@]}" -eq 0 ]; then
    die "No configuration files found to back up in $PROJECT_ROOT"
  fi

  # Safely archive configurations from project root, excluding active secrets
  if tar -czf "$tar_file" \
    -C "$PROJECT_ROOT" \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='.env' \
    --exclude='.env.production' \
    --exclude='.env.local' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    "${files_to_tar[@]}" \
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

  local git_commit="unknown"
  if command -v git &>/dev/null && [ -d "${PROJECT_ROOT}/.git" ]; then
    git_commit=$(cd "$PROJECT_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
  fi

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
  "version": "1.1.0",
  "git_commit": "${git_commit}",
  "postgres_database": "${POSTGRES_DB}",
  "neo4j_database": "${NEO4J_DATABASE}",
  "minio_endpoint": "${MINIO_ENDPOINT}",
  "components": ${component_json},
  "checksums": ${checksum_json},
  "config_categories": ["compose", "environment_templates", "service_configs"],
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
