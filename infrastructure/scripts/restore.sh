#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
LOG_FILE="${SCRIPT_DIR}/restore.log"

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-crimekit}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"

NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-}"
NEO4J_DATABASE="${NEO4J_DATABASE:-neo4j}"

MINIO_ENDPOINT="${MINIO_ENDPOINT:-localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minioadmin}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-minioadmin}"

BACKUP_DIR="${BACKUP_DIR:-/backups}"
FORCE=false
COMPONENT="all"
BACKUP_FILE=""
CONFIG_DEST="${CONFIG_DEST:-${RESTORE_CONFIG_DEST:-}}"
ALLOW_PROD_OVERWRITE=false

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --component COMPONENT       Component to restore: postgres, neo4j, minio, configs, all (default: all)
  --backup-file FILE          Path to a specific backup file or directory
  --dest-dir DIR              Destination directory for restored configurations (safe restore)
  --allow-overwrite-prod      Explicitly permit restoring configs into live project root
  --force                     Skip confirmation prompts
  -h, --help                  Show this help message

Environment variables:
  POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
  MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
  BACKUP_DIR (default: /backups)
  RESTORE_CONFIG_DEST (safe destination for config restore)
EOF
}

log() {
  local msg="[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1"
  echo "$msg" | tee -a "$LOG_FILE"
}

die() {
  log "FATAL: $1"
  exit 1
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --component)
        COMPONENT="$2"
        shift 2
        ;;
      --backup-file)
        BACKUP_FILE="$2"
        shift 2
        ;;
      --dest-dir)
        CONFIG_DEST="$2"
        shift 2
        ;;
      --allow-overwrite-prod)
        ALLOW_PROD_OVERWRITE=true
        shift
        ;;
      --force)
        FORCE=true
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "Unknown option: $1. Use --help for usage."
        ;;
    esac
  done

  if [[ ! "$COMPONENT" =~ ^(postgres|neo4j|minio|configs|all)$ ]]; then
    die "Invalid component: $COMPONENT. Must be one of: postgres, neo4j, minio, configs, all"
  fi
}

confirm_restore() {
  if [ "$FORCE" = true ]; then
    log "Force mode enabled, skipping confirmation"
    return
  fi

  echo ""
  echo "=========================================="
  echo "  RESTORE WARNING"
  echo "=========================================="
  echo "  Component:  $COMPONENT"
  echo "  Backup dir: ${BACKUP_FILE:-$BACKUP_DIR}"
  echo "  Target DB:  $POSTGRES_DB"
  echo "=========================================="
  echo ""
  read -rp "Are you sure you want to proceed with the restore? (type 'yes' to confirm): " answer
  if [[ "$answer" != "yes" ]]; then
    log "Restore cancelled by user"
    exit 0
  fi
  log "Restore confirmed by user"
}

find_latest_backup() {
  local component="$1"
  local dir="${BACKUP_DIR}/${component}"

  if [ -d "$dir" ]; then
    local latest
    latest=$(find "$dir" -maxdepth 1 -type d -name "2*" | sort -r | head -1)
    if [ -n "$latest" ]; then
      echo "$latest"
      return
    fi
  fi
  return 1
}

verify_backup_integrity() {
  local backup_dir="$1"
  log "Verifying backup integrity in: $backup_dir"

  local failed=0
  while IFS= read -r -d '' checksum_file; do
    local dir
    dir="$(dirname "$checksum_file")"
    if (cd "$dir" && sha256sum -c "$(basename "$checksum_file")" 2>>"$LOG_FILE"); then
      log "Integrity OK: $(basename "${checksum_file%.sha256}")"
    else
      log "Integrity FAILED: $(basename "${checksum_file%.sha256}")"
      failed=1
    fi
  done < <(find "$backup_dir" -name "*.sha256" -type f -print0)

  if [ "$failed" -ne 0 ]; then
    die "Backup integrity check failed. Restore aborted."
  fi
  log "Backup integrity verified"
}

create_restore_point() {
  local component="$1"
  local restore_point="${BACKUP_DIR}/restore_points/${component}_$(date -u +%Y%m%d_%H%M%S)"
  mkdir -p "$restore_point"
  log "Creating restore point: $restore_point"

  case "$component" in
    postgres)
      export PGPASSWORD="$POSTGRES_PASSWORD"
      pg_dump \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        -F c \
        -Z 9 \
        -f "${restore_point}/crimekit_pre_restore.dump" 2>>"$LOG_FILE" \
        && log "PostgreSQL restore point created" \
        || log "WARNING: Could not create PostgreSQL restore point"
      ;;
    neo4j)
      if command -v neo4j-admin &>/dev/null; then
        neo4j-admin database dump --to-path="${restore_point}" "$NEO4J_DATABASE" 2>>"$LOG_FILE" \
          && log "Neo4j restore point created" \
          || log "WARNING: Could not create Neo4j restore point"
      fi
      ;;
    minio)
      if command -v mc &>/dev/null; then
        export MINIO_ROOT_USER="$MINIO_ACCESS_KEY"
        export MINIO_ROOT_PASSWORD="$MINIO_SECRET_KEY"
        mc alias set crimekit_restore "http://${MINIO_ENDPOINT}" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" 2>>"$LOG_FILE"
        mc mirror --overwrite crimekit_restore "${restore_point}/data" 2>>"$LOG_FILE" \
          && log "MinIO restore point created" \
          || log "WARNING: Could not create MinIO restore point"
      fi
      ;;
    configs)
      tar -czf "${restore_point}/configs_pre_restore.tar.gz" \
        -C "$PROJECT_ROOT" \
        --exclude='node_modules' \
        --exclude='.git' \
        docker-compose.yml infrastructure/ .env* 2>>"$LOG_FILE" \
        && log "Config restore point created" \
        || log "WARNING: Could not create config restore point"
      ;;
  esac
}

restore_postgres() {
  log "Starting PostgreSQL restore..."

  local backup_dir
  if [ -n "$BACKUP_FILE" ]; then
    backup_dir="$BACKUP_FILE"
  else
    backup_dir=$(find_latest_backup postgres) || die "No PostgreSQL backup found in $BACKUP_DIR/postgres/"
  fi

  local dump_file
  dump_file=$(find "$backup_dir" -name "*.dump" -type f | head -1)
  if [ -z "$dump_file" ]; then
    die "No .dump file found in $backup_dir"
  fi

  log "Restoring from: $dump_file"
  verify_backup_integrity "$backup_dir"
  create_restore_point postgres

  export PGPASSWORD="$POSTGRES_PASSWORD"

  log "Dropping and recreating database..."
  dropdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB" 2>>"$LOG_FILE" \
    || log "WARNING: dropdb failed (database may not exist)"
  createdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB" 2>>"$LOG_FILE" \
    || log "WARNING: createdb failed (database may already exist)"

  if pg_restore \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    -j 4 \
    "$dump_file" 2>>"$LOG_FILE"; then
    log "PostgreSQL restore completed successfully"
  else
    die "PostgreSQL restore failed"
  fi
}

restore_neo4j() {
  log "Starting Neo4j restore (target database: ${NEO4J_DATABASE})..."

  local backup_dir
  if [ -n "$BACKUP_FILE" ]; then
    backup_dir="$BACKUP_FILE"
  else
    backup_dir=$(find_latest_backup neo4j) || die "No Neo4j backup found in $BACKUP_DIR/neo4j/"
  fi

  verify_backup_integrity "$backup_dir"
  create_restore_point neo4j

  local cypher_file
  cypher_file=$(find "$backup_dir" -name "*.cypher" -type f | head -1)

  local dump_file
  dump_file=$(find "$backup_dir" -name "*.dump" -type f | head -1)

  if [ -n "$cypher_file" ]; then
    log "Restoring Neo4j from Cypher script: $cypher_file"
    if command -v cypher-shell &>/dev/null; then
      if cypher-shell \
        -u "$NEO4J_USER" \
        -p "$NEO4J_PASSWORD" \
        -a "$NEO4J_URI" \
        -d "$NEO4J_DATABASE" \
        -f "$cypher_file" 2>>"$LOG_FILE"; then
        log "Neo4j cypher restore completed successfully"
      else
        die "Neo4j cypher restore failed"
      fi
    else
      die "cypher-shell not found for Cypher restore"
    fi
  elif [ -n "$dump_file" ]; then
    log "Restoring Neo4j from dump archive: $dump_file"
    if command -v neo4j-admin &>/dev/null; then
      if neo4j-admin database load --from-path="$dump_file" --overwrite-destination=true "$NEO4J_DATABASE" 2>>"$LOG_FILE"; then
        log "Neo4j admin restore completed successfully"
      else
        die "Neo4j admin restore failed"
      fi
    else
      die "neo4j-admin not found for dump restore"
    fi
  else
    die "No .cypher or .dump backup file found in $backup_dir"
  fi
}

restore_minio() {
  log "Starting MinIO restore..."

  local backup_dir
  if [ -n "$BACKUP_FILE" ]; then
    backup_dir="$BACKUP_FILE"
  else
    backup_dir=$(find_latest_backup minio) || die "No MinIO backup found in $BACKUP_DIR/minio/"
  fi

  verify_backup_integrity "$backup_dir"
  create_restore_point minio

  export MINIO_ROOT_USER="$MINIO_ACCESS_KEY"
  export MINIO_ROOT_PASSWORD="$MINIO_SECRET_KEY"

  if command -v mc &>/dev/null; then
    local data_dir="${backup_dir}/data"
    if [ -d "$data_dir" ]; then
      mc alias set crimekit_restore "http://${MINIO_ENDPOINT}" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" 2>>"$LOG_FILE"
      if mc mirror --overwrite "$data_dir" crimekit_restore 2>>"$LOG_FILE"; then
        log "MinIO restore completed successfully"
      else
        die "MinIO restore failed"
      fi
    else
      die "No data directory found in $backup_dir"
    fi
  else
    local tar_file
    tar_file=$(find "$backup_dir" -name "*.tar.gz" -type f | head -1)
    if [ -n "$tar_file" ]; then
      if tar -xzf "$tar_file" -C / 2>>"$LOG_FILE"; then
        log "MinIO tar restore completed successfully"
      else
        die "MinIO tar restore failed"
      fi
    else
      die "No backup file found in $backup_dir"
    fi
  fi
}

restore_configs() {
  log "Starting config restore..."

  local backup_dir
  if [ -n "$BACKUP_FILE" ]; then
    backup_dir="$BACKUP_FILE"
  else
    backup_dir=$(find_latest_backup configs) || die "No config backup found in $BACKUP_DIR/configs/"
  fi

  local tar_file
  tar_file=$(find "$backup_dir" -name "*.tar.gz" -type f | head -1)
  if [ -z "$tar_file" ]; then
    die "No .tar.gz file found in $backup_dir"
  fi

  verify_backup_integrity "$backup_dir"

  local target_dest="${CONFIG_DEST:-${RESTORE_CONFIG_DEST:-}}"
  if [ -z "$target_dest" ]; then
    target_dest="${BACKUP_DIR}/restored_configs_$(date -u +%Y%m%d_%H%M%S)"
    log "No destination directory specified. Defaulting to safe isolated destination: $target_dest"
  fi

  # Safety check against production overwrite
  if [ "$target_dest" = "$PROJECT_ROOT" ] || [ "$target_dest" = "${PROJECT_ROOT}/infrastructure" ] || [ "$target_dest" = "/opt/crimekit/app" ]; then
    if [ "$ALLOW_PROD_OVERWRITE" != "true" ]; then
      die "SAFETY REFUSAL: Target directory ($target_dest) is the active production project. Refusing to overwrite live configs without --allow-overwrite-prod"
    fi
    log "WARNING: Live production directory overwrite confirmed via --allow-overwrite-prod"
    create_restore_point configs
  fi

  mkdir -p "$target_dest"
  if tar -xzf "$tar_file" -C "$target_dest" 2>>"$LOG_FILE"; then
    log "Config restore completed successfully into: $target_dest"
  else
    die "Config restore failed"
  fi
}

main() {
  parse_args "$@"

  log "=========================================="
  log "CrimeKit Restore - Starting"
  log "Component: ${COMPONENT}"
  log "=========================================="

  confirm_restore

  mkdir -p "${BACKUP_DIR}/restore_points"

  case "$COMPONENT" in
    postgres)
      restore_postgres
      ;;
    neo4j)
      restore_neo4j
      ;;
    minio)
      restore_minio
      ;;
    configs)
      restore_configs
      ;;
    all)
      restore_postgres
      restore_neo4j
      restore_minio
      restore_configs
      ;;
  esac

  log "=========================================="
  log "CrimeKit Restore - Completed Successfully"
  log "=========================================="
}

trap 'die "Restore interrupted by signal"; exit 1' INT TERM

main "$@"
