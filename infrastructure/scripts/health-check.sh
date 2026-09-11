#!/usr/bin/env bash
set -euo pipefail

VERBOSE=false
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
NEO4J_URL="${NEO4J_URL:-http://localhost:7474}"
MINIO_URL="${MINIO_URL:-http://localhost:9000}"
NGINX_URL="${NGINX_URL:-http://localhost:80}"

TOTAL=0
HEALTHY=0
DEGRADED=0
CRITICAL=0

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --verbose          Show detailed output for each check
  -h, --help         Show this help message

Environment variables:
  BACKEND_URL         (default: http://localhost:8000)
  POSTGRES_HOST/PORT  (default: localhost:5432)
  REDIS_HOST/PORT     (default: localhost:6379)
  NEO4J_URL           (default: http://localhost:7474)
  MINIO_URL           (default: http://localhost:9000)
  NGINX_URL           (default: http://localhost:80)
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --verbose)
        VERBOSE=true
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "Unknown option: $1" >&2
        usage
        exit 1
        ;;
    esac
  done
}

measure_latency() {
  local start_ns end_ns latency_ms
  start_ns=$(date +%s%N 2>/dev/null || echo "0")

  local cmd_result
  cmd_result=$(eval "$1" 2>/dev/null)
  local exit_code=$?

  end_ns=$(date +%s%N 2>/dev/null || echo "0")

  if [ "$start_ns" != "0" ] && [ "$end_ns" != "0" ]; then
    latency_ms=$(( (end_ns - start_ns) / 1000000 ))
  else
    latency_ms=0
  fi

  echo "$exit_code:$latency_ms:$cmd_result"
}

emit_result() {
  local service="$1" status="$2" latency="$3" detail="${4:-}"
  printf '{"service": "%s", "status": "%s", "latency_ms": %s}\n' \
    "$service" "$status" "$latency"
  if [ "$VERBOSE" = true ] && [ -n "$detail" ]; then
    echo "  detail: $detail"
  fi
}

check_backend() {
  local result
  result=$(measure_latency "curl -sf -o /dev/null -w '%{http_code}' ${BACKEND_URL}/health --max-time 5")
  local exit_code latency detail
  IFS=':' read -r exit_code latency detail <<< "$result"

  TOTAL=$((TOTAL + 1))
  if [ "$exit_code" -eq 0 ] && [ "$detail" = "200" ]; then
    HEALTHY=$((HEALTHY + 1))
    emit_result "backend" "healthy" "$latency"
  else
    CRITICAL=$((CRITICAL + 1))
    emit_result "backend" "unhealthy" "$latency" "exit=$exit_code status=$detail"
  fi
}

check_postgres() {
  local result
  result=$(measure_latency "pg_isready -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U postgres")
  local exit_code latency detail
  IFS=':' read -r exit_code latency detail <<< "$result"

  TOTAL=$((TOTAL + 1))
  if [ "$exit_code" -eq 0 ]; then
    HEALTHY=$((HEALTHY + 1))
    emit_result "postgresql" "healthy" "$latency"
  else
    CRITICAL=$((CRITICAL + 1))
    emit_result "postgresql" "unhealthy" "$latency" "pg_isready failed"
  fi
}

check_redis() {
  local result
  result=$(measure_latency "redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} ping")
  local exit_code latency detail
  IFS=':' read -r exit_code latency detail <<< "$result"

  TOTAL=$((TOTAL + 1))
  if [ "$exit_code" -eq 0 ] && echo "$detail" | grep -qi "PONG"; then
    HEALTHY=$((HEALTHY + 1))
    emit_result "redis" "healthy" "$latency"
  else
    DEGRADED=$((DEGRADED + 1))
    emit_result "redis" "unhealthy" "$latency" "ping failed"
  fi
}

check_neo4j() {
  local result
  result=$(measure_latency "curl -sf -o /dev/null -w '%{http_code}' ${NEO4J_URL} --max-time 5")
  local exit_code latency detail
  IFS=':' read -r exit_code latency detail <<< "$result"

  TOTAL=$((TOTAL + 1))
  if [ "$exit_code" -eq 0 ] && [ "$detail" = "200" ]; then
    HEALTHY=$((HEALTHY + 1))
    emit_result "neo4j" "healthy" "$latency"
  else
    CRITICAL=$((CRITICAL + 1))
    emit_result "neo4j" "unhealthy" "$latency" "exit=$exit_code status=$detail"
  fi
}

check_minio() {
  local result
  result=$(measure_latency "curl -sf -o /dev/null -w '%{http_code}' ${MINIO_URL}/minio/health/live --max-time 5")
  local exit_code latency detail
  IFS=':' read -r exit_code latency detail <<< "$result"

  TOTAL=$((TOTAL + 1))
  if [ "$exit_code" -eq 0 ] && [ "$detail" = "200" ]; then
    HEALTHY=$((HEALTHY + 1))
    emit_result "minio" "healthy" "$latency"
  else
    DEGRADED=$((DEGRADED + 1))
    emit_result "minio" "unhealthy" "$latency" "exit=$exit_code status=$detail"
  fi
}

check_nginx() {
  local result
  result=$(measure_latency "curl -sf -o /dev/null -w '%{http_code}' ${NGINX_URL} --max-time 5")
  local exit_code latency detail
  IFS=':' read -r exit_code latency detail <<< "$result"

  TOTAL=$((TOTAL + 1))
  if [ "$exit_code" -eq 0 ] && [[ "$detail" =~ ^(200|301|302|304)$ ]]; then
    HEALTHY=$((HEALTHY + 1))
    emit_result "nginx" "healthy" "$latency"
  else
    DEGRADED=$((DEGRADED + 1))
    emit_result "nginx" "unhealthy" "$latency" "exit=$exit_code status=$detail"
  fi
}

determine_overall_status() {
  if [ "$CRITICAL" -gt 0 ]; then
    echo "critical"
    return 2
  elif [ "$DEGRADED" -gt 0 ]; then
    echo "degraded"
    return 1
  else
    echo "healthy"
    return 0
  fi
}

main() {
  parse_args "$@"

  if [ "$VERBOSE" = true ]; then
    echo "=========================================="
    echo "  CrimeKit Health Check"
    echo "  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "=========================================="
    echo ""
  fi

  check_backend
  check_postgres
  check_redis
  check_neo4j
  check_minio
  check_nginx

  overall_status
  local exit_code=$?

  if [ "$VERBOSE" = true ]; then
    echo ""
    echo "------------------------------------------"
    echo "  Summary"
    echo "  Total:    ${TOTAL}"
    echo "  Healthy:  ${HEALTHY}"
    echo "  Degraded: ${DEGRADED}"
    echo "  Critical: ${CRITICAL}"
    echo "  Overall:  $(echo "$overall_status" | tr '[:lower:]' '[:upper:]')"
    echo "------------------------------------------"
  fi

  exit $exit_code
}

overall_status() {
  determine_overall_status
}

main "$@"
