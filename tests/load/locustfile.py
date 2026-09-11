"""
CrimeKit Enterprise Platform — Locust Load Test Suite

Features:
  - HttpUser classes per endpoint group (auth, cases, evidence, processing, search, kg)
  - Weighted task sets matching realistic traffic patterns
  - Custom shape: ramp → steady → spike → steady → cool-down
  - Metrics collection and JSON report generation
  - Automatic token management and evidence upload with generated payloads

Run:
  locust -f tests/load/locustfile.py --host http://localhost:8088
  locust -f tests/load/locustfile.py --host http://localhost:8088 --headless -u 100 -r 10 --run-time 5m

Requirements:
  pip install locust
"""

import io
import json
import os
import random
import string
import time
from datetime import datetime, timezone
from pathlib import Path

from locust import (
    HttpUser,
    between,
    events,
    tag,
    task,
    LoadTestShape,
)
from locust.runners import MasterRunner


# ---------------------------------------------------------------------------
# Global state shared across users
# ---------------------------------------------------------------------------
_state = {
    "tokens": {},          # user_id -> {access, refresh}
    "cases": [],           # created case IDs
    "evidence_ids": [],    # uploaded evidence IDs
    "job_ids": [],         # processing job IDs
    "test_user_email": None,
}

_REPORT = {
    "start_time": None,
    "end_time": None,
    "total_requests": 0,
    "total_failures": 0,
    "endpoint_stats": {},
    "percentiles": {},
}

# ---------------------------------------------------------------------------
# Custom load shape: ramp → steady → spike → steady → cool-down
# ---------------------------------------------------------------------------

class CrimeKitLoadShape(LoadTestShape):
    """
    Stages:
      1. Ramp-up:        0 → 100 users over 60 s
      2. Steady state:   100 users for 5 min
      3. Spike:          100 → 300 users over 15 s, hold 30 s, ramp back
      4. Cool-down:      100 → 0 users over 30 s
    """

    stages = [
        {"duration": 60,  "users": 100, "spawn_rate": 5},     # ramp-up
        {"duration": 360, "users": 100, "spawn_rate": 10},    # steady
        {"duration": 375, "users": 300, "spawn_rate": 20},    # spike up
        {"duration": 405, "users": 300, "spawn_rate": 10},    # spike hold
        {"duration": 420, "users": 100, "spawn_rate": 10},    # recover
        {"duration": 450, "users": 0,   "spawn_rate": 5},     # cool-down
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _random_email():
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"locust_{suffix}@crimekit.test"


def _random_string(n=12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def _generate_filePayload(size_bytes):
    """Generate a random binary payload of the given size."""
    return "".join(random.choices(string.printable, k=size_bytes))


# ---------------------------------------------------------------------------
# Auth User
# ---------------------------------------------------------------------------

class AuthUser(HttpUser):
    """Handles registration, login, and token refresh."""
    weight = 2
    wait_time = between(0.5, 2)

    def on_start(self):
        self.email = _random_email()
        self.password = "Locust!2026$ec"
        self.access_token = None
        self.refresh_token = None
        self._register()

    def _register(self):
        with self.client.post(
            "/auth/register",
            json={"email": self.email, "password": self.password},
            name="/auth/register",
            catch_response=True,
        ) as resp:
            if resp.status_code in (201, 400):
                resp.success()
                if resp.status_code == 201:
                    body = resp.json()
                    self.access_token = body.get("access_token")
                    self.refresh_token = body.get("refresh_token")
                    _state["tokens"][self.email] = {
                        "access": self.access_token,
                        "refresh": self.refresh_token,
                    }
            else:
                resp.failure(f"Register failed: {resp.status_code}")

    def _auth_headers(self):
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    @tag("auth")
    @task(3)
    def login(self):
        self.client.post(
            "/auth/login",
            json={"email": self.email, "password": self.password},
            name="/auth/login",
            headers={"Content-Type": "application/json"},
        )

    @tag("auth")
    @task(1)
    def refresh(self):
        if not self.refresh_token:
            return
        with self.client.post(
            "/auth/refresh",
            json=self.refresh_token,
            name="/auth/refresh",
            headers={"Content-Type": "application/json"},
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                body = resp.json()
                self.access_token = body.get("access_token")
                self.refresh_token = body.get("refresh_token")
                resp.success()
            else:
                resp.failure(f"Refresh failed: {resp.status_code}")

    @tag("auth")
    @task(1)
    def logout(self):
        if not self.refresh_token:
            return
        self.client.post(
            "/auth/logout",
            json=self.refresh_token,
            name="/auth/logout",
            headers={"Content-Type": "application/json"},
        )


# ---------------------------------------------------------------------------
# Cases User
# ---------------------------------------------------------------------------

class CasesUser(HttpUser):
    """Case CRUD operations."""
    weight = 3
    wait_time = between(0.3, 1.5)

    def on_start(self):
        self.email = _random_email()
        self.password = "Locust!2026$ec"
        self.access_token = None
        self._register()
        self.cases = []

    def _register(self):
        resp = self.client.post(
            "/auth/register",
            json={"email": self.email, "password": self.password},
            name="/auth/register",
        )
        if resp.status_code in (201, 400) and resp.status_code == 201:
            body = resp.json()
            self.access_token = body.get("access_token")

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    @tag("cases")
    @task(4)
    def create_case(self):
        title = f"Case-{_random_string(6)}-{int(time.time())}"
        with self.client.post(
            "/cases/",
            json={"title": title, "description": "Locust load test"},
            headers=self._headers(),
            name="/cases/ [POST]",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201):
                case_id = resp.json().get("id", "")
                self.cases.append(case_id)
                _state["cases"].append(case_id)
                resp.success()
            else:
                resp.failure(f"Create case: {resp.status_code}")

    @tag("cases")
    @task(6)
    def list_cases(self):
        self.client.get(
            "/cases/",
            headers=self._headers(),
            name="/cases/ [GET]",
        )

    @tag("cases")
    @task(5)
    def get_case(self):
        if not self.cases:
            return
        case_id = random.choice(self.cases)
        self.client.get(
            f"/cases/{case_id}",
            headers=self._headers(),
            name="/cases/{id} [GET]",
        )

    @tag("cases")
    @task(2)
    def update_case(self):
        if not self.cases:
            return
        case_id = random.choice(self.cases)
        self.client.put(
            f"/cases/{case_id}",
            json={"title": f"Updated-{_random_string(4)}", "status": "under_review"},
            headers=self._headers(),
            name="/cases/{id} [PUT]",
        )


# ---------------------------------------------------------------------------
# Evidence User
# ---------------------------------------------------------------------------

class EvidenceUser(HttpUser):
    """Evidence upload and retrieval."""
    weight = 3
    wait_time = between(0.5, 2)

    def on_start(self):
        self.email = _random_email()
        self.password = "Locust!2026$ec"
        self.access_token = None
        self.evidence_ids = []
        self._register()

    def _register(self):
        resp = self.client.post(
            "/auth/register",
            json={"email": self.email, "password": self.password},
            name="/auth/register",
        )
        if resp.status_code == 201:
            body = resp.json()
            self.access_token = body.get("access_token")

    def _headers(self):
        h = {}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    @tag("evidence")
    @task(3)
    def upload_evidence_small(self):
        self._upload("small.bin", 10 * 1024)

    @tag("evidence")
    @task(1)
    def upload_evidence_medium(self):
        self._upload("medium.bin", 1024 * 1024)

    def _upload(self, filename, size):
        payload = _generate_filePayload(size)
        boundary = f"----locust{int(time.time())}"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
            f"{payload}\r\n"
            f"--{boundary}--\r\n"
        )
        headers = self._headers()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        with self.client.post(
            "/evidence/upload",
            data=body,
            headers=headers,
            name=f"/evidence/upload [{filename}]",
            catch_response=True,
            timeout=30,
        ) as resp:
            if resp.status_code in (200, 201):
                ev_id = resp.json().get("id", "")
                self.evidence_ids.append(ev_id)
                _state["evidence_ids"].append(ev_id)
                resp.success()
            else:
                resp.failure(f"Upload failed: {resp.status_code}")

    @tag("evidence")
    @task(5)
    def get_evidence(self):
        if not self.evidence_ids:
            return
        ev_id = random.choice(self.evidence_ids)
        self.client.get(
            f"/evidence/{ev_id}",
            headers=self._headers(),
            name="/evidence/{id} [GET]",
        )

    @tag("evidence")
    @task(4)
    def list_case_evidence(self):
        if _state["cases"]:
            case_id = random.choice(_state["cases"])
            self.client.get(
                f"/evidence/case/{case_id}",
                headers=self._headers(),
                name="/evidence/case/{id} [GET]",
            )

    @tag("evidence")
    @task(2)
    def get_custody(self):
        if not self.evidence_ids:
            return
        ev_id = random.choice(self.evidence_ids)
        self.client.get(
            f"/evidence/{ev_id}/custody",
            headers=self._headers(),
            name="/evidence/{id}/custody [GET]",
        )


# ---------------------------------------------------------------------------
# Processing User
# ---------------------------------------------------------------------------

class ProcessingUser(HttpUser):
    """Forensic processing queue operations."""
    weight = 2
    wait_time = between(0.5, 2)

    def on_start(self):
        self.email = _random_email()
        self.password = "Locust!2026$ec"
        self.access_token = None
        self.job_ids = []
        self._register()

    def _register(self):
        resp = self.client.post(
            "/auth/register",
            json={"email": self.email, "password": self.password},
            name="/auth/register",
        )
        if resp.status_code == 201:
            body = resp.json()
            self.access_token = body.get("access_token")

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    @tag("processing")
    @task(2)
    def enqueue_processing(self):
        if not _state["evidence_ids"]:
            return
        ev_id = random.choice(_state["evidence_ids"])
        with self.client.post(
            f"/processing/evidence/{ev_id}/enqueue",
            json={"processors": ["hashes", "metadata"]},
            headers=self._headers(),
            name="/processing/evidence/{id}/enqueue",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201):
                job_id = resp.json().get("job_id", "")
                self.job_ids.append(job_id)
                _state["job_ids"].append(job_id)
                resp.success()
            elif resp.status_code in (403, 404):
                resp.success()  # expected
            else:
                resp.failure(f"Enqueue failed: {resp.status_code}")

    @tag("processing")
    @task(3)
    def get_job(self):
        if not self.job_ids:
            return
        job_id = random.choice(self.job_ids)
        self.client.get(
            f"/processing/jobs/{job_id}",
            headers=self._headers(),
            name="/processing/jobs/{id} [GET]",
        )

    @tag("processing")
    @task(2)
    def get_queue_stats(self):
        self.client.get(
            "/processing/queue/stats",
            headers=self._headers(),
            name="/processing/queue/stats",
        )

    @tag("processing")
    @task(1)
    def list_processors(self):
        self.client.get(
            "/processing/forensic/processors",
            headers=self._headers(),
            name="/processing/forensic/processors",
        )


# ---------------------------------------------------------------------------
# Search User
# ---------------------------------------------------------------------------

class SearchUser(HttpUser):
    """Search queries across the platform."""
    weight = 2
    wait_time = between(0.3, 1)

    QUERIES = ["forensic", "evidence", "crime", "binary", "metadata", "test", "hash"]

    def on_start(self):
        self.email = _random_email()
        self.password = "Locust!2026$ec"
        self.access_token = None
        self._register()

    def _register(self):
        resp = self.client.post(
            "/auth/register",
            json={"email": self.email, "password": self.password},
            name="/auth/register",
        )
        if resp.status_code == 201:
            body = resp.json()
            self.access_token = body.get("access_token")

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    @tag("search")
    @task(5)
    def search_cases(self):
        q = random.choice(self.QUERIES)
        self.client.get(
            f"/cases/?search={q}",
            headers=self._headers(),
            name="/cases/?search={q}",
        )

    @tag("search")
    @task(3)
    def search_evidence(self):
        q = random.choice(self.QUERIES)
        self.client.get(
            f"/evidence/case/{q}",
            headers=self._headers(),
            name="/evidence/case/{q}",
        )


# ---------------------------------------------------------------------------
# Knowledge Graph User
# ---------------------------------------------------------------------------

class KGUser(HttpUser):
    """Knowledge graph queries."""
    weight = 1
    wait_time = between(0.5, 2)

    def on_start(self):
        self.email = _random_email()
        self.password = "Locust!2026$ec"
        self.access_token = None
        self._register()

    def _register(self):
        resp = self.client.post(
            "/auth/register",
            json={"email": self.email, "password": self.password},
            name="/auth/register",
        )
        if resp.status_code == 201:
            body = resp.json()
            self.access_token = body.get("access_token")

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    @tag("kg")
    @task(3)
    def list_entities(self):
        self.client.get(
            "/kg/entities",
            headers=self._headers(),
            name="/kg/entities",
        )

    @tag("kg")
    @task(2)
    def cypher_query(self):
        self.client.post(
            "/kg/query",
            json={
                "cypher": "MATCH (n:Entity) RETURN n.name AS name, n.type AS type LIMIT 10",
                "params": {},
            },
            headers=self._headers(),
            name="/kg/query",
        )

    @tag("kg")
    @task(1)
    def case_graph(self):
        if _state["cases"]:
            case_id = random.choice(_state["cases"])
            self.client.get(
                f"/kg/case/{case_id}/graph",
                headers=self._headers(),
                name="/kg/case/{id}/graph",
            )


# ---------------------------------------------------------------------------
# Lifecycle: collect and persist stats
# ---------------------------------------------------------------------------

@events.init.add_listener
def on_init(environment, **kwargs):
    _REPORT["start_time"] = datetime.now(timezone.utc).isoformat()
    _REPORT["endpoint_stats"] = {}


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    _REPORT["total_requests"] += 1
    if exception:
        _REPORT["total_failures"] += 1

    if name not in _REPORT["endpoint_stats"]:
        _REPORT["endpoint_stats"][name] = {
            "count": 0,
            "failures": 0,
            "total_time_ms": 0,
            "min_ms": float("inf"),
            "max_ms": 0,
        }
    stat = _REPORT["endpoint_stats"][name]
    stat["count"] += 1
    if exception:
        stat["failures"] += 1
    stat["total_time_ms"] += response_time
    stat["min_ms"] = min(stat["min_ms"], response_time)
    stat["max_ms"] = max(stat["max_ms"], response_time)


@events.quitting.add_listener
def on_quit(environment, **kwargs):
    _REPORT["end_time"] = datetime.now(timezone.utc).isoformat()

    # Compute averages
    for name, stat in _REPORT["endpoint_stats"].items():
        if stat["count"] > 0:
            stat["avg_ms"] = round(stat["total_time_ms"] / stat["count"], 2)
        else:
            stat["avg_ms"] = 0

    # Percentiles from runner stats
    if environment.runner:
        stats = environment.runner.stats
        if stats.total:
            _REPORT["percentiles"] = {
                f"p{p}": round(stats.total.get_response_time_percentile(p / 100), 2)
                for p in [50, 75, 90, 95, 99]
            }

    # Write report
    report_path = Path("tests/load/locust_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(_REPORT, f, indent=2, default=str)
    print(f"\n[Locust] Report written to {report_path}")

    # Summary
    total = _REPORT["total_requests"]
    failures = _REPORT["total_failures"]
    error_pct = (failures / total * 100) if total else 0
    print(f"[Locust] Total requests: {total}")
    print(f"[Locust] Total failures: {failures} ({error_pct:.2f}%)")
    print(f"[Locust] Unique endpoints: {len(_REPORT['endpoint_stats'])}")
    if _REPORT["percentiles"]:
        print(f"[Locust] Percentiles: {_REPORT['percentiles']}")
