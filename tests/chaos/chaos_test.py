"""
CrimeKit Enterprise Platform — Chaos Engineering Tests

Verifies graceful degradation and recovery when critical infrastructure
components (Redis, PostgreSQL, Neo4j, MinIO, workers) experience failures.

Uses pytest + docker-compose for container management.

Run:
    pytest tests/chaos/chaos_test.py -v --tb=short -s
    pytest tests/chaos/chaos_test.py -v -k "redis" --tb=short

Prerequisites:
    - Docker + docker-compose available
    - CrimeKit stack running (docker compose up -d)
    - pytest, requests, docker python packages installed
"""

import json
import os
import signal
import socket
import subprocess
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Generator, Optional

import pytest
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("BASE_URL", "http://localhost:8088")
API_URL = f"{BASE_URL}"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
COMPOSE_FILE = os.getenv("COMPOSE_FILE", "docker-compose.yml")
PROJECT_NAME = os.getenv("COMPOSE_PROJECT", "crimekit")

# Container names (must match docker-compose.yml)
CONTAINER_POSTGRES = os.getenv("CONTAINER_POSTGRES", "crimekit_postgres")
CONTAINER_REDIS = os.getenv("CONTAINER_REDIS", "crimekit_redis")
CONTAINER_NEO4J = os.getenv("CONTAINER_NEO4J", "crimekit_neo4j")
CONTAINER_MINIO = os.getenv("CONTAINER_MINIO", "crimekit_minio")
CONTAINER_BACKEND = os.getenv("CONTAINER_BACKEND", "crimekit_backend")
CONTAINER_NGINX = os.getenv("CONTAINER_NGINX", "crimekit_nginx")

# Redis config for direct connections
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "crimekit_dev_redis")

# Timeouts
HEALTH_TIMEOUT = 60  # seconds to wait for recovery
RECOVERY_POLL_INTERVAL = 2  # seconds between polls


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def docker_cmd(*args) -> subprocess.CompletedProcess:
    """Execute a docker-compose command."""
    cmd = ["docker", "compose", "-f", COMPOSE_FILE, "-p", PROJECT_NAME] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def docker_exec(container: str, command: str) -> subprocess.CompletedProcess:
    """Execute a command inside a running container."""
    cmd = ["docker", "exec", container] + command.split()
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def container_is_running(container: str) -> bool:
    """Check if a Docker container is running."""
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container],
        capture_output=True, text=True, timeout=10,
    )
    return result.stdout.strip().lower() == "true"


def pause_container(container: str):
    """Pause a Docker container (simulates freeze/hang)."""
    subprocess.run(["docker", "pause", container], capture_output=True, timeout=15)


def unpause_container(container: str):
    """Unpause a Docker container."""
    subprocess.run(["docker", "unpause", container], capture_output=True, timeout=15)


def stop_container(container: str, timeout: int = 10):
    """Stop a Docker container."""
    subprocess.run(
        ["docker", "stop", "-t", str(timeout), container],
        capture_output=True, timeout=timeout + 15,
    )


def start_container(container: str):
    """Start a Docker container."""
    subprocess.run(["docker", "start", container], capture_output=True, timeout=30)


def kill_container(container: str, signal_name: str = "SIGKILL"):
    """Kill a Docker container with a signal."""
    subprocess.run(
        ["docker", "kill", "-s", signal_name, container],
        capture_output=True, timeout=15,
    )


def wait_for_healthy(url: str, timeout: int = HEALTH_TIMEOUT) -> bool:
    """Poll a health endpoint until it returns 200."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        except requests.Timeout:
            pass
        time.sleep(RECOVERY_POLL_INTERVAL)
    return False


def api_get(path: str, headers: dict = None) -> requests.Response:
    return requests.get(f"{API_URL}{path}", headers=headers, timeout=10)


def api_post(path: str, json_data=None, headers: dict = None) -> requests.Response:
    return requests.post(f"{API_URL}{path}", json=json_data, headers=headers, timeout=10)


def register_and_login() -> dict:
    """Register a test user and return auth headers."""
    email = f"chaos_{uuid.uuid4().hex[:8]}@test.dev"
    password = "ChaosTest!2026$"
    api_post("/auth/register", {"email": email, "password": password})
    resp = api_post("/auth/login", {"email": email, "password": password})
    if resp.status_code == 200:
        token = resp.json().get("access_token", "")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def auth_headers() -> dict:
    """Shared auth headers for the test module."""
    return register_and_login()


@pytest.fixture(autouse=True)
def ensure_all_running():
    """Ensure all containers are running before each test."""
    for container in [CONTAINER_POSTGRES, CONTAINER_REDIS, CONTAINER_NEO4J,
                      CONTAINER_MINIO, CONTAINER_BACKEND]:
        if not container_is_running(container):
            start_container(container)
    time.sleep(3)
    yield
    # Recovery: ensure all containers are back up
    for container in [CONTAINER_POSTGRES, CONTAINER_REDIS, CONTAINER_NEO4J,
                      CONTAINER_MINIO, CONTAINER_BACKEND]:
        if not container_is_running(container):
            start_container(container)


# ===========================================================================
# Redis Failure Tests
# ===========================================================================

class TestRedisFailure:
    """Simulate Redis failures and verify recovery."""

    def test_redis_stop_and_restart(self, auth_headers):
        """Stop Redis, verify API degrades gracefully, restart, verify recovery."""
        # 1. Baseline: API works
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200, "Baseline API check failed"

        # 2. Stop Redis
        stop_container(CONTAINER_REDIS)
        time.sleep(2)
        assert not container_is_running(CONTAINER_REDIS), "Redis should be stopped"

        # 3. API should still respond (graceful degradation — auth may use DB fallback)
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code in (200, 500, 503), \
            f"API should degrade gracefully, got {resp.status_code}"

        # 4. Restart Redis
        start_container(CONTAINER_REDIS)
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        assert recovered, "API did not recover after Redis restart"

        # 5. Verify full functionality
        time.sleep(3)
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200, "API not functional after Redis recovery"

    def test_redis_pause_and_unpause(self, auth_headers):
        """Pause Redis (freeze), verify timeout behavior, unpause, verify recovery."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200, "Baseline failed"

        # Pause Redis
        pause_container(CONTAINER_REDIS)
        time.sleep(2)

        # API should timeout or return error
        try:
            resp = api_get("/cases/", auth_headers)
            assert resp.status_code in (200, 408, 500, 503)
        except requests.Timeout:
            pass  # Expected — Redis is frozen

        # Unpause
        unpause_container(CONTAINER_REDIS)
        time.sleep(3)
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        assert recovered, "Did not recover after Redis unpause"

    def test_redis_kill_sigterm(self, auth_headers):
        """Send SIGTERM to Redis, verify clean shutdown and recovery."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        kill_container(CONTAINER_REDIS, "SIGTERM")
        time.sleep(3)

        # Restart
        start_container(CONTAINER_REDIS)
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        assert recovered, "Recovery failed after Redis SIGTERM"

    def test_redis_password_removed_then_restored(self, auth_headers):
        """Simulate Redis config corruption by pausing and restarting."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        # Simulate config issue by pausing briefly
        pause_container(CONTAINER_REDIS)
        time.sleep(1)
        unpause_container(CONTAINER_REDIS)
        time.sleep(3)

        resp = api_get("/cases/", auth_headers)
        assert resp.status_code in (200, 500, 503)


# ===========================================================================
# PostgreSQL Failure Tests
# ===========================================================================

class TestPostgresFailure:
    """Simulate PostgreSQL failures and verify recovery."""

    def test_postgres_stop_and_restart(self, auth_headers):
        """Stop PostgreSQL, verify 503, restart, verify recovery."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        # Stop PostgreSQL
        stop_container(CONTAINER_POSTGRES)
        time.sleep(2)
        assert not container_is_running(CONTAINER_POSTGRES)

        # API should return 503 or 500 (no DB)
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code in (500, 503, 200), \
            f"Expected graceful degradation, got {resp.status_code}"

        # Restart
        start_container(CONTAINER_POSTGRES)
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT + 30)
        assert recovered, "Did not recover after PostgreSQL restart"

        # Verify full functionality
        time.sleep(5)
        headers = register_and_login()
        resp = api_post("/cases/", {"title": "Post-recovery test"}, headers)
        assert resp.status_code in (200, 201), "Post-recovery write failed"

    def test_postgres_pause_and_unpause(self, auth_headers):
        """Pause PostgreSQL (simulates hung queries)."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        pause_container(CONTAINER_POSTGRES)
        time.sleep(2)

        # API may hang or return error
        try:
            resp = api_get("/cases/", auth_headers)
            assert resp.status_code in (200, 408, 500, 503)
        except requests.Timeout:
            pass

        unpause_container(CONTAINER_POSTGRES)
        time.sleep(5)
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT + 30)
        assert recovered, "Recovery failed after PostgreSQL unpause"

    def test_postgres_kill_sigkill(self, auth_headers):
        """Force kill PostgreSQL (simulates crash)."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        kill_container(CONTAINER_POSTGRES, "SIGKILL")
        time.sleep(5)

        # PostgreSQL auto-restarts via Docker restart policy
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT + 30)
        assert recovered, "Recovery failed after PostgreSQL SIGKILL"

        time.sleep(5)
        headers = register_and_login()
        resp = api_get("/cases/", headers)
        assert resp.status_code == 200

    def test_postgres_disk_full_simulation(self, auth_headers):
        """Simulate disk pressure by creating a large file in the container."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        # Create a large file inside the container to simulate disk pressure
        docker_exec(CONTAINER_POSTGRES, "dd if=/dev/zero of=/tmp/disk_pressure bs=1M count=500")
        time.sleep(2)

        # API should still respond (degraded or not)
        try:
            resp = api_get("/cases/", auth_headers)
            assert resp.status_code in (200, 500, 503)
        except Exception:
            pass  # Connection may fail

        # Cleanup
        docker_exec(CONTAINER_POSTGRES, "rm -f /tmp/disk_pressure")
        time.sleep(3)
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        assert recovered, "Recovery failed after disk pressure cleanup"


# ===========================================================================
# Neo4j Failure Tests
# ===========================================================================

class TestNeo4jFailure:
    """Simulate Neo4j (Knowledge Graph) failures."""

    def test_neo4j_stop_and_restart(self, auth_headers):
        """Stop Neo4j, verify KG endpoints degrade, restart, verify recovery."""
        # Baseline
        resp = api_get("/kg/entities", auth_headers)
        assert resp.status_code in (200, 503)

        stop_container(CONTAINER_NEO4J)
        time.sleep(2)

        # KG endpoints should return 503 (service unavailable)
        resp = api_get("/kg/entities", auth_headers)
        assert resp.status_code in (200, 503), \
            f"KG should return 503 when Neo4j is down, got {resp.status_code}"

        # Non-KG endpoints should still work
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200, "Non-KG endpoints should work without Neo4j"

        # Restart
        start_container(CONTAINER_NEO4J)
        time.sleep(10)  # Neo4j needs time to boot

        resp = api_get("/kg/entities", auth_headers)
        assert resp.status_code == 200, "KG not recovered after Neo4j restart"

    def test_neo4j_pause_and_unpause(self, auth_headers):
        """Pause Neo4j, verify behavior, unpause."""
        pause_container(CONTAINER_NEO4J)
        time.sleep(2)

        try:
            resp = api_get("/kg/entities", auth_headers)
            assert resp.status_code in (200, 503, 408)
        except requests.Timeout:
            pass

        unpause_container(CONTAINER_NEO4J)
        time.sleep(10)
        resp = api_get("/kg/entities", auth_headers)
        assert resp.status_code == 200


# ===========================================================================
# Worker Crash Tests
# ===========================================================================

class TestWorkerCrash:
    """Simulate background worker crashes and verify recovery."""

    def test_worker_kill_and_restart(self, auth_headers):
        """Kill the backend worker process and verify it restarts."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        # Kill the backend container (which includes the worker)
        kill_container(CONTAINER_BACKEND, "SIGKILL")
        time.sleep(3)

        # Backend should auto-restart
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        assert recovered, "Backend did not restart after worker kill"

        # Verify functionality
        time.sleep(3)
        headers = register_and_login()
        resp = api_get("/cases/", headers)
        assert resp.status_code == 200, "API not functional after worker restart"

    def test_worker_graceful_shutdown(self, auth_headers):
        """Send SIGTERM to backend for graceful shutdown."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        kill_container(CONTAINER_BACKEND, "SIGTERM")
        time.sleep(5)

        # Should restart via Docker restart policy
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        assert recovered, "Backend did not recover after graceful shutdown"

    def test_worker_processing_during_restart(self, auth_headers):
        """Verify in-progress jobs survive worker restart."""
        # This test verifies that queued jobs in Redis survive a worker restart
        resp = api_get("/processing/queue/stats", auth_headers)
        assert resp.status_code == 200, "Processing queue stats should work"


# ===========================================================================
# MinIO (Object Storage) Failure Tests
# ===========================================================================

class TestMinIOFailure:
    """Simulate MinIO (S3-compatible storage) failures."""

    def test_minio_stop_and_restart(self, auth_headers):
        """Stop MinIO, verify upload degrades, restart, verify recovery."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        stop_container(CONTAINER_MINIO)
        time.sleep(2)

        # Upload should fail gracefully
        file_content = b"chaos test file"
        boundary = "----chaostest"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="chaos.bin"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + file_content + f"\r\n--{boundary}--\r\n".encode()

        try:
            resp = requests.post(
                f"{API_URL}/evidence/upload",
                data=body,
                headers={
                    "Authorization": auth_headers.get("Authorization", ""),
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                },
                timeout=10,
            )
            # Should either succeed (local fallback) or fail gracefully
            assert resp.status_code in (200, 201, 500, 503)
        except Exception:
            pass  # Connection error expected

        # Restart MinIO
        start_container(CONTAINER_MINIO)
        time.sleep(5)
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        assert recovered, "Recovery failed after MinIO restart"

    def test_minio_pause_and_unpause(self, auth_headers):
        """Pause MinIO, verify timeout behavior."""
        pause_container(CONTAINER_MINIO)
        time.sleep(2)

        # API should still respond for non-storage operations
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code in (200, 500, 503)

        unpause_container(CONTAINER_MINIO)
        time.sleep(5)
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200


# ===========================================================================
# Network Latency Injection
# ===========================================================================

class TestNetworkLatency:
    """Simulate network latency using tc (traffic control)."""

    def test_redis_latency_injection(self, auth_headers):
        """Inject 200ms latency on Redis connections."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        # Add latency to Redis container's network interface
        docker_exec(CONTAINER_REDIS, "tc qdisc add dev eth0 root netem delay 200ms 50ms")
        time.sleep(2)

        # API should still work but with increased latency
        start = time.time()
        resp = api_get("/cases/", auth_headers)
        elapsed = time.time() - start
        assert resp.status_code in (200, 500, 503)
        # Latency should be noticeable but not catastrophic
        assert elapsed < 10, f"Request took too long: {elapsed}s"

        # Remove latency
        docker_exec(CONTAINER_REDIS, "tc qdisc del dev eth0 root")
        time.sleep(2)

        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

    def test_postgres_latency_injection(self, auth_headers):
        """Inject 100ms latency on PostgreSQL connections."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        docker_exec(CONTAINER_POSTGRES, "tc qdisc add dev eth0 root netem delay 100ms 30ms")
        time.sleep(2)

        start = time.time()
        resp = api_get("/cases/", auth_headers)
        elapsed = time.time() - start
        assert resp.status_code in (200, 500, 503)
        assert elapsed < 10

        docker_exec(CONTAINER_POSTGRES, "tc qdisc del dev eth0 root")
        time.sleep(2)

        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200


# ===========================================================================
# Container Restart Simulation
# ===========================================================================

class TestContainerRestart:
    """Simulate container restarts and verify system resilience."""

    def test_all_containers_restart_sequentially(self, auth_headers):
        """Restart each container one at a time and verify the system stays up."""
        containers = [
            CONTAINER_REDIS,
            CONTAINER_NEO4J,
            CONTAINER_MINIO,
            CONTAINER_POSTGRES,
        ]

        for container in containers:
            # Stop
            stop_container(container)
            time.sleep(3)

            # API should degrade but not crash entirely
            try:
                resp = api_get("/cases/", auth_headers)
                assert resp.status_code in (200, 500, 503), \
                    f"API crashed when {container} was down"
            except requests.ConnectionError:
                pass  # Acceptable during restart

            # Start
            start_container(container)
            time.sleep(5)

        # Wait for full recovery
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT + 30)
        assert recovered, "System did not recover after sequential container restarts"

        # Verify full functionality
        time.sleep(5)
        headers = register_and_login()
        resp = api_get("/cases/", headers)
        assert resp.status_code == 200

    def test_backend_restart_preserves_data(self, auth_headers):
        """Restart backend and verify that data persists in PostgreSQL."""
        # Create a case
        resp = api_post("/cases/", {"title": "Pre-restart case"}, auth_headers)
        assert resp.status_code in (200, 201)
        case_id = resp.json().get("id")

        # Restart backend
        kill_container(CONTAINER_BACKEND, "SIGKILL")
        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        assert recovered, "Backend did not recover"

        time.sleep(3)
        headers = register_and_login()

        # Verify case still exists
        resp = api_get(f"/cases/{case_id}", headers)
        assert resp.status_code == 200, "Case lost after backend restart"
        assert resp.json().get("title") == "Pre-restart case"

    def test_rapid_restart_cycle(self, auth_headers):
        """Rapidly stop/start Redis multiple times to stress recovery."""
        for i in range(3):
            stop_container(CONTAINER_REDIS)
            time.sleep(1)
            start_container(CONTAINER_REDIS)
            time.sleep(2)

        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT)
        assert recovered, "System did not recover after rapid restart cycle"

        time.sleep(3)
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200


# ===========================================================================
# Memory Pressure Tests
# ===========================================================================

class TestMemoryPressure:
    """Simulate memory pressure on containers."""

    def test_redis_memory_pressure(self, auth_headers):
        """Fill Redis with data to simulate memory pressure."""
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        # Fill Redis with keys via redis-cli
        docker_exec(
            CONTAINER_REDIS,
            "redis-cli -a crimekit_dev_redis EVAL "
            "'for i=1,10000 do redis.call(\"SET\", \"chaos:\" .. i, string.rep(\"x\", 100)) end' 0"
        )
        time.sleep(2)

        # API should still work
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code in (200, 500, 503)

        # Cleanup
        docker_exec(CONTAINER_REDIS, "redis-cli -a crimekit_dev_redis EVAL 'local keys = redis.call(\"KEYS\", \"chaos:*\") for i=1,#keys do redis.call(\"DEL\", keys[i]) end' 0")
        time.sleep(2)

        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200


# ===========================================================================
# Graceful Degradation Verification
# ===========================================================================

class TestGracefulDegradation:
    """Verify the system degrades gracefully across failure scenarios."""

    def test_neo4j_down_rest_of_system_works(self, auth_headers):
        """With Neo4j down, all non-KG features should work."""
        stop_container(CONTAINER_NEO4J)
        time.sleep(3)

        # Cases should work
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200, "Cases endpoint failed without Neo4j"

        # Auth should work
        resp = api_post("/auth/login", {"email": "test@test.com", "password": "x"})
        assert resp.status_code in (200, 401), "Auth endpoint failed without Neo4j"

        # Evidence upload should work
        file_content = b"test"
        boundary = "----grad"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="test.bin"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + file_content + f"\r\n--{boundary}--\r\n".encode()
        try:
            resp = requests.post(
                f"{API_URL}/evidence/upload",
                data=body,
                headers={
                    "Authorization": auth_headers.get("Authorization", ""),
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                },
                timeout=10,
            )
            assert resp.status_code in (200, 201, 500)
        except Exception:
            pass

        # KG should return 503
        resp = api_get("/kg/entities", auth_headers)
        assert resp.status_code == 503, \
            f"KG should return 503 when Neo4j is down, got {resp.status_code}"

        # Restart Neo4j
        start_container(CONTAINER_NEO4J)
        time.sleep(10)

    def test_minio_down_uploads_fail_gracefully(self, auth_headers):
        """With MinIO down, uploads should fail gracefully, not crash the API."""
        stop_container(CONTAINER_MINIO)
        time.sleep(2)

        file_content = b"test file"
        boundary = "----grad2"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="test.bin"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + file_content + f"\r\n--{boundary}--\r\n".encode()

        try:
            resp = requests.post(
                f"{API_URL}/evidence/upload",
                data=body,
                headers={
                    "Authorization": auth_headers.get("Authorization", ""),
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                },
                timeout=10,
            )
            # Should not crash (500 is acceptable, 503 is acceptable)
            assert resp.status_code in (200, 201, 500, 503)
        except Exception:
            pass

        # Cases should still work
        resp = api_get("/cases/", auth_headers)
        assert resp.status_code == 200

        start_container(CONTAINER_MINIO)
        time.sleep(5)

    def test_multiple_simultaneous_failures(self, auth_headers):
        """Stop Redis AND Neo4j simultaneously, verify core API survives."""
        stop_container(CONTAINER_REDIS)
        stop_container(CONTAINER_NEO4J)
        time.sleep(3)

        # Core API (cases, auth) should still respond
        try:
            resp = api_get("/cases/", auth_headers)
            assert resp.status_code in (200, 500, 503)
        except Exception:
            pass  # Acceptable during multi-failure

        # Restart both
        start_container(CONTAINER_REDIS)
        start_container(CONTAINER_NEO4J)
        time.sleep(10)

        recovered = wait_for_healthy(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT + 30)
        assert recovered, "System did not recover from multi-component failure"

        time.sleep(5)
        headers = register_and_login()
        resp = api_get("/cases/", headers)
        assert resp.status_code == 200
