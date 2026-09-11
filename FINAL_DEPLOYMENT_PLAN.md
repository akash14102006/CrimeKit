# CRIMEKIT FINAL PRODUCTION DEPLOYMENT PLAN
**Document Version:** 1.0.0  
**Status:** READY FOR STAGED EXECUTION (Pending User Approval)  
**Execution Mode:** DO NOT EXECUTE AUTOMATICALLY — AWAIT EXPLICIT APPROVAL  

---

## Master 19-Step Deployment Sequence

```
[ Step 1: Frontend Build ]
  Status: COMPLETED
  - npm run build executed successfully.
  - Output directory frontend/out populated with 30 pre-rendered HTML routes and assets.

[ Step 2: Catalyst Project Verification ]
  Status: VERIFIED & READY
  - Catalyst CLI 1.27.0 authenticated as akashanitha2005@gmail.com.
  - Client source mapped to frontend/out in catalyst.json.
  - Pending user confirmation of project target (CodeMafiaweb3 vs new CrimeKit project).

[ Step 3: Cloud Network Provisioning ]
  Target: AWS VPC (Region: ap-south-1 Mumbai)
  - 1x VPC (10.0.0.0/16) across 2 Availability Zones.
  - 2x Public Subnets (for ALB and NAT Gateways).
  - 2x Private Application Subnets (for ECS Fargate Backend Tasks).
  - 2x Private Data Subnets (isolated, for RDS PostgreSQL, ElastiCache Redis, and Neo4j).
  - Security groups enforcing least-privilege ingress.

[ Step 4: Object Storage Provisioning ]
  Target: AWS S3
  - Create bucket crimekit-evidence-prod with S3 Object Lock enabled in COMPLIANCE mode.
  - Create bucket crimekit-documents-prod with versioning enabled.
  - Create bucket crimekit-court-reports-prod with S3 Object Lock enabled.
  - Configure VPC Gateway Endpoint (com.amazonaws.ap-south-1.s3).

[ Step 5: PostgreSQL Database Provisioning ]
  Target: AWS RDS for PostgreSQL 16 (Multi-AZ)
  - Instance Class: db.m6g.xlarge (or db.t4g.medium for cost-conscious staging).
  - Execute infrastructure/postgres/init.sql to create extensions (uuid-ossp, pgcrypto, pg_trgm, btree_gist).
  - Execute CREATE EXTENSION vector; for pgvector support.

[ Step 6: Redis In-Memory Store Provisioning ]
  Target: AWS ElastiCache for Redis 7
  - Node Type: cache.m6g.large Multi-AZ with automatic failover.
  - Configure AOF persistence and volatile-lru eviction policy to protect task streams.

[ Step 7: Neo4j Knowledge Graph Provisioning ]
  Target: Neo4j AuraDB Professional (or EC2 r6g.xlarge)
  - Execute schema constraints and uniqueness indexes from NEO4J_DEPLOYMENT_CHECKLIST.md.

[ Step 8: Production Secret Injection ]
  Target: AWS Secrets Manager (KMS CMK Encrypted)
  - Store JWT_SECRET_KEY (64-char CSPRNG string).
  - Store database passwords, Redis tokens, Neo4j passwords, and Descope Management Key.

[ Step 9: Backend Container Registry & Build ]
  Target: Amazon ECR (Elastic Container Registry)
  - Build OCI image from backend/Dockerfile via Docker Buildx.
  - Push image crimekit-backend:v1.0.0 to Amazon ECR.

[ Step 10: Database Migration Execution ]
  Target: RDS PostgreSQL Database
  - Run ECS one-off task: alembic upgrade head.
  - Verify all tables created without errors.

[ Step 11: FastAPI Backend API Deployment ]
  Target: AWS ECS Fargate
  - Deploy backend tasks (minimum 2 tasks for HA) behind AWS Application Load Balancer.
  - Configure ALB listeners for HTTP/HTTPS with ACM SSL certificate.

[ Step 12: Forensic Worker Pool Deployment ]
  Target: AWS ECS Fargate (Compute-Optimized)
  - Deploy worker tasks consuming from Redis Streams consumer group crimekit-workers.
  - Configure autoscaling policy based on stream depth.

[ Step 13: Authentication Configuration ]
  Target: Descope Console & Backend
  - Verify production redirect URIs match the Catalyst frontend domain.
  - Confirm Descope JWT public keys and webhook endpoints.

[ Step 14: Face Trace Deployment ]
  Target: AWS EC2 g4dn.xlarge (NVIDIA T4) or ECS CPU Mode
  - For staging/demo: run in CPU mode via ONNX Runtime.
  - For real-time production video: launch GPU worker node with buffalo_l ONNX weights.

[ Step 15: WebSocket Validation ]
  Target: /ws/case/{case_id}
  - Configure ALB idle timeout to 1200 seconds (20 minutes).
  - Verify TLS handshake and message delivery over wss://.

[ Step 16: Catalyst Frontend Deployment ]
  Target: Zoho Catalyst Web Client
  - Execute catalyst deploy --only client from project root.
  - Verify static assets and SPA fallback from global CDN.

[ Step 17: DNS & TLS Finalization ]
  Target: AWS Route 53 & Zoho Custom Domains
  - Point api.crimekit.yourdomain.com to ALB via CNAME/Alias.
  - Point crimekit.yourdomain.com to Zoho Catalyst Web Client CDN.

[ Step 18: End-to-End Production Validation ]
  - Verify user login through Descope OIDC.
  - Upload synthetic test evidence and verify S3 Object Lock.
  - Verify automated OCR, GLiNER entity extraction, and Neo4j graph population.
  - Verify real-time event streaming in browser via WebSocket.

[ Step 19: Production Hardening ]
  - Enable AWS WAF on Application Load Balancer.
  - Enable CloudWatch alarms and Prometheus alerting for dead-letter queues.
  - Finalize backup schedules and automated recovery runbooks.
```
