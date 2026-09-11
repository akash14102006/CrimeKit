# CRIMEKIT WEBSOCKET DEPLOYMENT CHECKLIST
**Endpoint:** `/ws/case/{case_id}`  
**Protocol:** WebSocket (`ws://` in dev, `wss://` in production)  
**Relay Implementation:** `backend/app/realtime_relay.py` + `backend/app/websocket_manager.py`  

---

## 1. Connection Lifecycle & Authentication

1. **Client Connection:**
   Frontend initiates connection via `wss://<api-domain>/ws/case/{case_id}?token=<jwt>`.
2. **Handshake Verification:**
   - [backend/app/ws_routes.py:82](file:///c:/Users/akash/Downloads/Enterprise%20grade%20-%20CrimeKit%20-%20front%20error/backend/app/ws_routes.py#L82) extracts `token` from query parameter.
   - Decodes JWT and validates signature.
   - `_verify_case_access()` checks case assignment: Admin and Investigator roles can access any case; Viewer role can only access assigned cases. Unassigned requests are rejected with close code `4003`.
3. **Registration:**
   Socket is registered in `ConnectionManager` under `case_id`.

---

## 2. Event Relay Flow

```
[ Forensic Worker ]
       |
       | 1. Publish Event (e.g. entity.detected)
       v
[ Redis Pub/Sub ] (`crimekit:events:case:{case_id}`)
       |
       | 2. Redis Message
       v
[ realtime_relay.py ] (Asyncio loop subscribed to pattern)
       |
       | 3. Broadcast to active sockets
       v
[ websocket_manager.py ] (`manager.broadcast_to_case`)
       |
       | 4. WSS Frame
       v
[ Browser Client ] (`useGraphWebSocket.ts` / `useTSKRealtime.ts`)
```

---

## 3. Load Balancer & Proxy Requirements

* **HTTP Version:** Must support HTTP/1.1 with `Upgrade: websocket` and `Connection: upgrade` headers.
* **Idle Timeout:** AWS ALB idle timeout must be configured to **1200 seconds (20 minutes)** to prevent premature disconnection during periods of inactive case analysis.
* **Client Heartbeats:** Frontend sends periodic `"ping"` frames; backend responds with `"pong"` to keep connections alive through intermediary firewalls.
* **Multi-Instance Scaling:** Because the event relay uses Redis Pub/Sub, scaling out FastAPI across multiple ECS Fargate container instances works seamlessly without sticky sessions: each instance receives published case events and delivers them to its locally connected clients.
