/**
 * CrimeKit Enterprise Platform — k6 Load Test Suite
 *
 * Targets:
 *   - Throughput: 1000 RPS sustained
 *   - Latency:    p95 < 200 ms, p99 < 500 ms
 *   - Errors:     < 0.1 %
 *
 * Run:
 *   k6 run --out json=results.json tests/load/k6_benchmark.js
 *   k6 run --vus 50 --duration 5m tests/load/k6_benchmark.js
 *
 * Stages:
 *   1. Ramp-up:      0 → 100 VUs over 60 s
 *   2. Steady state: 100 VUs for 5 min
 *   3. Spike:        100 → 300 VUs for 30 s, back to 100
 *   4. Ramp-down:    100 → 0 VUs over 30 s
 */

import http from "k6/http";
import { check, group, sleep, fail } from "k6";
import { Counter, Rate, Trend } from "k6/metrics";
import { randomIntBetween } from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

// ---------------------------------------------------------------------------
// Custom metrics
// ---------------------------------------------------------------------------
const authRequests       = new Counter("auth_requests");
const caseRequests       = new Counter("case_requests");
const evidenceRequests   = new Counter("evidence_requests");
const processingRequests = new Counter("processing_requests");
const searchRequests     = new Counter("search_requests");
const kgRequests         = new Counter("kg_requests");

const errorRate          = new Rate("errors");
const authLatency        = new Trend("auth_latency", true);
const caseLatency        = new Trend("case_latency", true);
const evidenceLatency    = new Trend("evidence_latency", true);
const processingLatency  = new Trend("processing_latency", true);
const searchLatency      = new Trend("search_latency", true);
const kgLatency          = new Trend("kg_latency", true);

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const BASE_URL = __ENV.TARGET_URL || "http://localhost:8088";
const API_PREFIX = `${BASE_URL}`;

const TEST_USER_EMAIL = `loadtest_${Date.now()}@crimekit.dev`;
const TEST_USER_PASSWORD = "LoadTest!2026$ecure";

// Small file payload (10 KB)
const PAYLOAD_10KB = "A".repeat(10 * 1024);
// Medium file payload (1 MB)
const PAYLOAD_1MB = "B".repeat(1 * 1024 * 1024);

// ---------------------------------------------------------------------------
// Options — staged load profile
// ---------------------------------------------------------------------------
export const options = {
  scenarios: {
    staged_load: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "60s", target: 100 },   // ramp-up
        { duration: "5m",  target: 100 },   // steady state
        { duration: "30s", target: 300 },   // spike
        { duration: "1m",  target: 100 },   // recover from spike
        { duration: "30s", target: 0 },     // ramp-down
      ],
      gracefulRampDown: "30s",
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<200", "p(99)<500"],
    errors: ["rate<0.01"],
    auth_latency: ["p(95)<200"],
    case_latency: ["p(95)<200"],
    evidence_latency: ["p(95)<200"],
    search_latency: ["p(95)<200"],
    kg_latency: ["p(95)<200"],
  },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
let _accessToken = "";
let _refreshToken = "";
let _registeredCaseId = "";

function jsonHeaders(token) {
  const h = { "Content-Type": "application/json" };
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

function registerUser() {
  const payload = JSON.stringify({
    email: TEST_USER_EMAIL,
    password: TEST_USER_PASSWORD,
  });
  const res = http.post(`${API_PREFIX}/auth/register`, payload, {
    headers: jsonHeaders(),
    tags: { endpoint: "auth_register" },
  });
  authRequests.add(1);
  authLatency.add(res.timings.duration);

  const ok = check(res, {
    "register: 201 or 400 (exists)": (r) => r.status === 201 || r.status === 400,
  });
  errorRate.add(!ok);

  if (res.status === 201) {
    const body = res.json();
    _accessToken = body.access_token || "";
    _refreshToken = body.refresh_token || "";
  }
  return res;
}

function loginUser() {
  const payload = JSON.stringify({
    email: TEST_USER_EMAIL,
    password: TEST_USER_PASSWORD,
  });
  const res = http.post(`${API_PREFIX}/auth/login`, payload, {
    headers: jsonHeaders(),
    tags: { endpoint: "auth_login" },
  });
  authRequests.add(1);
  authLatency.add(res.timings.duration);

  const ok = check(res, { "login: 200": (r) => r.status === 200 });
  errorRate.add(!ok);

  if (res.status === 200) {
    const body = res.json();
    _accessToken = body.access_token || "";
    _refreshToken = body.refresh_token || "";
  }
  return res;
}

function refreshToken() {
  if (!_refreshToken) return null;
  const res = http.post(
    `${API_PREFIX}/auth/refresh`,
    JSON.stringify(_refreshToken),
    {
      headers: jsonHeaders(),
      tags: { endpoint: "auth_refresh" },
    }
  );
  authRequests.add(1);
  authLatency.add(res.timings.duration);

  const ok = check(res, { "refresh: 200": (r) => r.status === 200 });
  errorRate.add(!ok);

  if (res.status === 200) {
    const body = res.json();
    _accessToken = body.access_token || "";
    _refreshToken = body.refresh_token || "";
  }
  return res;
}

// ---------------------------------------------------------------------------
// Auth Group
// ---------------------------------------------------------------------------
function authGroup() {
  group("Authentication", () => {
    registerUser();
    sleep(0.5);
    loginUser();
    sleep(0.5);
    refreshToken();
    sleep(0.3);
  });
}

// ---------------------------------------------------------------------------
// Evidence Upload Group
// ---------------------------------------------------------------------------
function evidenceUploadGroup() {
  group("Evidence Upload", () => {
    if (!_accessToken) return;

    const fileSizes = [
      { name: "small_10KB.bin", data: PAYLOAD_10KB },
      { name: "medium_1MB.bin", data: PAYLOAD_1MB },
    ];
    // Pick a random size each iteration
    const pick = fileSizes[randomIntBetween(0, fileSizes.length - 1)];

    const boundary = `----k6boundary${Date.now()}`;
    const body = [
      `--${boundary}`,
      `Content-Disposition: form-data; name="file"; filename="${pick.name}"`,
      "Content-Type: application/octet-stream",
      "",
      pick.data,
      `--${boundary}--`,
    ].join("\r\n");

    const res = http.post(`${API_PREFIX}/evidence/upload`, body, {
      headers: {
        Authorization: `Bearer ${_accessToken}`,
        "Content-Type": `multipart/form-data; boundary=${boundary}`,
      },
      tags: { endpoint: "evidence_upload" },
      timeout: "30s",
    });
    evidenceRequests.add(1);
    evidenceLatency.add(res.timings.duration);

    const ok = check(res, {
      "upload: 200 or 201": (r) => r.status === 200 || r.status === 201,
    });
    errorRate.add(!ok);
  });
}

// ---------------------------------------------------------------------------
// Case CRUD Group
// ---------------------------------------------------------------------------
function caseCrudGroup() {
  group("Case CRUD", () => {
    if (!_accessToken) return;
    const hdrs = jsonHeaders(_accessToken);

    // Create
    const createRes = http.post(
      `${API_PREFIX}/cases/`,
      JSON.stringify({
        title: `Load-Case-${Date.now()}-${randomIntBetween(0, 9999)}`,
        description: "Automated load test case",
      }),
      { headers: hdrs, tags: { endpoint: "case_create" } }
    );
    caseRequests.add(1);
    caseLatency.add(createRes.timings.duration);
    errorRate.add(createRes.status !== 200 && createRes.status !== 201);

    if (createRes.status === 200 || createRes.status === 201) {
      _registeredCaseId = createRes.json().id || "";
    }

    sleep(0.2);

    // List
    const listRes = http.get(`${API_PREFIX}/cases/`, {
      headers: hdrs,
      tags: { endpoint: "case_list" },
    });
    caseRequests.add(1);
    caseLatency.add(listRes.timings.duration);
    errorRate.add(listRes.status !== 200);

    sleep(0.2);

    // Get by ID
    if (_registeredCaseId) {
      const getRes = http.get(`${API_PREFIX}/cases/${_registeredCaseId}`, {
        headers: hdrs,
        tags: { endpoint: "case_get" },
      });
      caseRequests.add(1);
      caseLatency.add(getRes.timings.duration);
      errorRate.add(getRes.status !== 200 && getRes.status !== 404);

      sleep(0.2);

      // Update
      const updateRes = http.put(
        `${API_PREFIX}/cases/${_registeredCaseId}`,
        JSON.stringify({
          title: `Updated-${Date.now()}`,
          description: "Updated via load test",
          status: "under_review",
        }),
        { headers: hdrs, tags: { endpoint: "case_update" } }
      );
      caseRequests.add(1);
      caseLatency.add(updateRes.timings.duration);
      errorRate.add(updateRes.status !== 200 && updateRes.status !== 403);
    }
  });
}

// ---------------------------------------------------------------------------
// Forensic Processing Queue Group
// ---------------------------------------------------------------------------
function processingGroup() {
  group("Processing Queue", () => {
    if (!_accessToken) return;
    const hdrs = jsonHeaders(_accessToken);

    // Enqueue a processing job (uses any existing evidence if available)
    const enqueueRes = http.post(
      `${API_PREFIX}/processing/forensic/test-evidence-id`,
      JSON.stringify({ enabled_processors: ["hashes", "metadata"] }),
      { headers: hdrs, tags: { endpoint: "processing_forensic" } }
    );
    processingRequests.add(1);
    processingLatency.add(enqueueRes.timings.duration);
    // 404 is acceptable (no evidence), we're measuring API availability
    errorRate.add(enqueueRes.status >= 500);

    sleep(0.3);

    // Queue stats
    const statsRes = http.get(`${API_PREFIX}/processing/queue/stats`, {
      headers: hdrs,
      tags: { endpoint: "queue_stats" },
    });
    processingRequests.add(1);
    processingLatency.add(statsRes.timings.duration);
    errorRate.add(statsRes.status !== 200);

    sleep(0.2);

    // List processors
    const procRes = http.get(`${API_PREFIX}/processing/forensic/processors`, {
      headers: hdrs,
      tags: { endpoint: "list_processors" },
    });
    processingRequests.add(1);
    processingLatency.add(procRes.timings.duration);
    errorRate.add(procRes.status !== 200);
  });
}

// ---------------------------------------------------------------------------
// Search Queries Group
// ---------------------------------------------------------------------------
function searchGroup() {
  group("Search Queries", () => {
    const queries = [
      "forensic",
      "evidence",
      "crime",
      "investigation",
      "test",
      "binary",
      "metadata",
    ];
    const q = queries[randomIntBetween(0, queries.length - 1)];

    // Health/search endpoint (POST /search is enterprise module, fallback: cases list)
    const searchRes = http.get(`${API_PREFIX}/cases/?search=${q}`, {
      headers: jsonHeaders(_accessToken),
      tags: { endpoint: "search" },
    });
    searchRequests.add(1);
    searchLatency.add(searchRes.timings.duration);
    errorRate.add(searchRes.status >= 500);

    sleep(0.3);

    // Evidence listing search
    const evSearch = http.get(`${API_PREFIX}/evidence/case/test-id`, {
      headers: jsonHeaders(_accessToken),
      tags: { endpoint: "evidence_search" },
    });
    searchRequests.add(1);
    searchLatency.add(evSearch.timings.duration);
    // 404 acceptable
    errorRate.add(evSearch.status >= 500);
  });
}

// ---------------------------------------------------------------------------
// Knowledge Graph Queries Group
// ---------------------------------------------------------------------------
function kgGroup() {
  group("Knowledge Graph", () => {
    const hdrs = jsonHeaders(_accessToken);

    // List entities
    const entitiesRes = http.get(`${API_PREFIX}/kg/entities`, {
      headers: hdrs,
      tags: { endpoint: "kg_entities" },
    });
    kgRequests.add(1);
    kgLatency.add(entitiesRes.timings.duration);
    errorRate.add(entitiesRes.status !== 200 && entitiesRes.status !== 503);

    sleep(0.3);

    // Cypher query (safe read)
    const cypherRes = http.post(
      `${API_PREFIX}/kg/query`,
      JSON.stringify({
        cypher: "MATCH (n:Entity) RETURN n.name AS name, n.type AS type LIMIT 10",
        params: {},
      }),
      { headers: hdrs, tags: { endpoint: "kg_query" } }
    );
    kgRequests.add(1);
    kgLatency.add(cypherRes.timings.duration);
    errorRate.add(cypherRes.status !== 200 && cypherRes.status !== 503);

    sleep(0.3);

    // Case graph
    if (_registeredCaseId) {
      const graphRes = http.get(
        `${API_PREFIX}/kg/case/${_registeredCaseId}/graph`,
        { headers: hdrs, tags: { endpoint: "kg_case_graph" } }
      );
      kgRequests.add(1);
      kgLatency.add(graphRes.timings.duration);
      errorRate.add(graphRes.status !== 200 && graphRes.status !== 503);
    }
  });
}

// ---------------------------------------------------------------------------
// Main VU loop
// ---------------------------------------------------------------------------
export default function () {
  // Weighted random selection of scenario groups
  const roll = Math.random();

  if (roll < 0.15) {
    authGroup();
  } else if (roll < 0.45) {
    caseCrudGroup();
  } else if (roll < 0.65) {
    evidenceUploadGroup();
  } else if (roll < 0.80) {
    processingGroup();
  } else if (roll < 0.92) {
    searchGroup();
  } else {
    kgGroup();
  }

  sleep(randomIntBetween(1, 3) / 10); // 0.1 – 0.3 s think time
}

// ---------------------------------------------------------------------------
// Lifecycle hooks
// ---------------------------------------------------------------------------
export function setup() {
  // Ensure the user exists before the test begins
  registerUser();
  if (!_accessToken) {
    loginUser();
  }
  return { startTime: new Date().toISOString() };
}

export function teardown(data) {
  // Optionally log summary
  console.log(
    `Load test completed. Start: ${data.startTime}, End: ${new Date().toISOString()}`
  );
}
