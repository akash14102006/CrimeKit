# CRIMEKIT EVIDENCE PROOF FABRIC — ARCHITECTURE DOCUMENT
## Protocol Version: CRIMEKIT-EIP-001 v1.0

---

## 1. EXECUTIVE SUMMARY

CrimeKit's Evidence Proof Fabric provides **cryptographically verifiable evidence integrity** through
an external blockchain trust anchor. The system stores **proof of evidence state** on-chain, never
raw evidence or sensitive metadata.

### Core Design Principle
> "STORE EVIDENCE OFF-CHAIN. STORE PROOF OF EVIDENCE STATE ON-CHAIN."

### What Blockchain Proves
- A specific digital artifact existed in a specific state at a specific time
- The forensic lineage from original evidence to derived artifacts has not been tampered with
- Chain-of-custody checkpoints are externally verifiable
- An independent party can verify evidence without trusting CrimeKit's database

### What Blockchain Does NOT Prove
- The truthfulness of the underlying real-world event
- That the forensic software produced correct results
- That the original evidence was accurately captured

---

## 2. EVIDENCE PROOF FABRIC — LAYERED TRUST MODEL

```
LAYER 8: INDEPENDENT VERIFICATION
  ↕
LAYER 7: BLOCKCHAIN TRUST ANCHOR (Polygon/ Base Sepolia testnet)
  ↕
LAYER 6: CRYPTOGRAPHIC COMMITMENT (Merkle tree batch)
  ↕
LAYER 5: FORENSIC PROVENANCE (parent → operation → derived)
  ↕
LAYER 4: CHAIN OF CUSTODY (custodian + timestamp + operation)
  ↕
LAYER 3: APPLICATION AUDIT (PostgreSQL audit logs)
  ↕
LAYER 2: STORAGE INTEGRITY (Object Lock / retention / legal hold)
  ↕
LAYER 1: FILE INTEGRITY (SHA-256 / SHA-512)
```

---

## 3. BLOCKCHAIN SELECTION

### Recommended: Polygon Amoy Testnet (SIH Prototype) → Polygon Mainnet (Production)

| Criterion | Polygon Amoy | Base Sepolia | Ethereum Sepolia | Hyperledger |
|-----------|-------------|-------------|-----------------|-------------|
| Tx Cost | ~$0.001 | ~$0.005 | ~$0.50 | Free |
| Finality | ~2s | ~2s | ~15min | Immediate |
| EVM | Yes | Yes | Yes | Yes (Besu) |
| SDK | web3.py/ethers | web3.py/ethers | web3.py/ethers | Fabric SDK |
| Testnet | Amoy (80002) | Sepolia (84532) | Sepolia (11155111) | Local |
| Production | Mainnet (137) | Mainnet (8453) | Mainnet (1) | Self-hosted |

**Decision**: Polygon Amoy for prototype, Polygon mainnet for production.
**Migration path**: Contract is EVM-compatible — deploy to any EVM chain.

---

## 4. SMART CONTRACT: EvidenceAnchor.sol

### Minimal On-Chain Record
```solidity
struct AnchorRecord {
    bytes32 proofId;           // Unique proof identifier
    bytes32 caseCommitment;    // Hash of case metadata (no PII)
    bytes32 evidenceCommitment;// Hash of evidence metadata bundle
    bytes32 merkleRoot;        // Merkle root of batched evidence
    uint8   anchorType;        // 0=evidence, 1=custody, 2=provenance
    uint256 timestamp;         // Block timestamp
    bytes32 issuerId;          // Pseudonymous institution hash
    uint16  protocolVersion;   // CRIMEKIT-EIP-001 version
    bytes32 metadataHash;      // Hash of additional metadata
    bool    active;            // Soft delete flag
}
```

### Events (for verifiable state transitions)
```solidity
event EvidenceAnchored(
    bytes32 indexed proofId,
    bytes32 indexed caseCommitment,
    bytes32 commitment,
    bytes32 merkleRoot,
    uint16  protocolVersion,
    uint256 timestamp
);

event AnchorRevoked(
    bytes32 indexed proofId,
    bytes32 indexed reason
);
```

### Key Functions
- `anchorProof(...)` — Store a new evidence proof
- `revokeProof(bytes32 proofId, bytes32 reason)` — Soft-revoke a proof
- `verifyProof(bytes32 proofId)` — Check if proof exists and is active
- `getAnchor(bytes32 proofId)` — Retrieve anchor record
- `getAnchorCount()` — Total anchored proofs
- `batchAnchor(bytes32[] proofIds, bytes32[] commitments)` — Batch anchoring

### Privacy Guarantees
- **NO** case names, evidence filenames, suspect names, PII
- **NO** raw evidence hashes (only commitment hashes)
- **NO** biometric data, passwords, API keys
- Only pseudonymous institution identifiers (SHA-256 of org_id + salt)

---

## 5. MERKLE TREE & BATCH ANCHORING

### Batch Flow
```
Evidence E1 (SHA-256)
Evidence E2 (SHA-256)
Evidence E3 (SHA-256)
Evidence E4 (SHA-256)
Evidence E5 (SHA-256)
Evidence E6 (SHA-256)
Evidence E7 (SHA-256)
Evidence E8 (SHA-256)
         ↓
    COMMITMENT HASH = SHA-256(evidence_sha256 + evidence_metadata_hash + version)
         ↓
    MERKLE TREE (8 leaves → 3 levels → 1 root)
         ↓
    MERKLE ROOT
         ↓
    ONE BLOCKCHAIN TRANSACTION
```

### Batch Size Strategy
- Default batch size: 128 evidence items per Merkle tree
- Anchoring frequency: Every 5 minutes (configurable) or when batch is full
- Maximum pending batch age: 1 hour (force anchor even if not full)
- Queue backpressure: Max 10,000 pending items before rate limiting

### Merkle Proof Generation
For evidence E5:
```
E5 hash → sibling hash → parent hash → grandparent hash → ROOT
```
Verification: Reconstruct root from E5 hash + proof path → compare with anchored root.

---

## 6. FORENSIC LINEAGE — PROVENANCE GRAPH

### ArtifactNode Model
```
ORIGINAL EVIDENCE (SHA-256)
    ↓
    ├── ACQUISITION EVENT (timestamp, actor, method)
    │      ↓
    │   Original Hash
    │
    ├── FORENSIC PROCESSING (engine, version, config)
    │      ↓
    │   ├── Artifact A (filesystem, SHA-256)
    │   ├── Artifact B (OCR text, SHA-256)
    │   ├── Artifact C (entity extraction, SHA-256)
    │   └── Artifact D (knowledge graph, SHA-256)
    │
    ├── DERIVED HASHES (each with parent_artifact_id)
    │      ↓
    │   Provenance Commitment
    │
    ├── MERKLE BATCH COMMITMENT
    │      ↓
    │   Merkle Root
    │
    └── BLOCKCHAIN ANCHOR
           ↓
        Transaction Hash
```

### Versioned Commitments
```
EVIDENCE v1
  ├── COMMITMENT_1 (hash + metadata + version)
  ├── MERKLE BATCH → ROOT_1
  └── BLOCKCHAIN ANCHOR_1

EVIDENCE v2 (reprocessed)
  ├── COMMITMENT_2 (hash + metadata + version)
  ├── MERKLE BATCH → ROOT_2
  └── BLOCKCHAIN ANCHOR_2

DERIVED ARTIFACTS (from v1 or v2)
  ├── Parent: EVIDENCE
  ├── Operation: forensic processing
  ├── Tool: TSK v5.16
  ├── Input hash, Output hash
  └── Own commitment → batch → anchor
```

---

## 7. DATABASE SCHEMA ADDITIONS

### New Tables (PostgreSQL)

```sql
-- Blockchain anchor records
CREATE TABLE blockchain_anchors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proof_id VARCHAR(64) UNIQUE NOT NULL,        -- bytes32 hex
    case_id UUID REFERENCES cases(id),
    evidence_id UUID REFERENCES evidence(id),
    anchor_type VARCHAR(20) NOT NULL,            -- 'evidence', 'custody', 'provenance'
    merkle_root VARCHAR(64) NOT NULL,            -- bytes32 hex
    case_commitment VARCHAR(64),
    evidence_commitment VARCHAR(64),
    metadata_hash VARCHAR(64),
    protocol_version INTEGER DEFAULT 1,
    issuer_id VARCHAR(64),                       -- pseudonymous institution hash
    tx_hash VARCHAR(66),                         -- 0x + 64 hex
    block_number BIGINT,
    chain_id INTEGER,
    network VARCHAR(50),                         -- 'polygon-amoy', 'polygon-mainnet'
    contract_address VARCHAR(42),
    status VARCHAR(20) DEFAULT 'pending',        -- pending, anchoring, anchored, failed, revoked
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 5,
    anchored_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Evidence commitments (per-evidence cryptographic identity)
CREATE TABLE evidence_commitments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id UUID REFERENCES evidence(id),
    commitment_hash VARCHAR(64) NOT NULL,        -- SHA-256(evidence_sha256 + metadata_hash + version)
    evidence_sha256 VARCHAR(64) NOT NULL,
    metadata_hash VARCHAR(64) NOT NULL,          -- SHA-256 of normalized metadata
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending',        -- pending, batched, anchored
    batch_id UUID,                               -- FK to merkle_batches
    anchor_id UUID,                              -- FK to blockchain_anchors
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Merkle batch tracking
CREATE TABLE merkle_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merkle_root VARCHAR(64) NOT NULL,            -- bytes32 hex
    leaf_count INTEGER NOT NULL,
    tree_depth INTEGER NOT NULL,
    batch_size INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',        -- pending, anchoring, anchored, failed
    anchor_id UUID,                              -- FK to blockchain_anchors
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    anchored_at TIMESTAMP WITH TIME ZONE
);

-- Merkle leaves (individual evidence commitments in the tree)
CREATE TABLE merkle_leaves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES merkle_batches(id),
    leaf_index INTEGER NOT NULL,
    commitment_hash VARCHAR(64) NOT NULL,
    evidence_id UUID REFERENCES evidence(id),
    commitment_id UUID REFERENCES evidence_commitments(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Artifact provenance (forensic lineage)
CREATE TABLE artifact_commitments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artifact_id VARCHAR(64) NOT NULL,            -- unique artifact identifier
    parent_artifact_id VARCHAR(64),              -- parent in provenance chain
    root_evidence_id UUID REFERENCES evidence(id),
    artifact_hash VARCHAR(64) NOT NULL,          -- SHA-256 of derived artifact
    operation_type VARCHAR(50) NOT NULL,         -- 'ocr', 'entity_extraction', etc.
    tool_name VARCHAR(100),
    tool_version VARCHAR(50),
    input_hash VARCHAR(64),                      -- hash of input to this operation
    processing_timestamp TIMESTAMP WITH TIME ZONE,
    processor_identity VARCHAR(64),              -- pseudonymous processor ID
    protocol_version INTEGER DEFAULT 1,
    provenance_commitment VARCHAR(64),           -- commitment for this artifact
    batch_id UUID,
    anchor_id UUID,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chain-of-custody commitment checkpoints
CREATE TABLE custody_commitments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    custody_id UUID REFERENCES chain_of_custody(id),
    evidence_id UUID REFERENCES evidence(id),
    custody_hash VARCHAR(64) NOT NULL,           -- SHA-256 of custody entry
    sequence_number INTEGER NOT NULL,            -- ordering in custody chain
    previous_hash VARCHAR(64),                   -- hash of previous custody commitment
    batch_id UUID,
    anchor_id UUID,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Verification requests and results
CREATE TABLE verification_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id UUID REFERENCES evidence(id),
    requested_by UUID REFERENCES users(id),
    verification_type VARCHAR(20),               -- 'full', 'hash_only', 'merkle_only', 'blockchain_only'
    result VARCHAR(20),                          -- 'verified', 'failed', 'partial', 'pending'
    details JSONB,                               -- full verification report
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Protocol version registry
CREATE TABLE blockchain_protocols (
    version INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    hash_algorithm VARCHAR(20) DEFAULT 'sha256',
    commitment_encoding VARCHAR(20) DEFAULT 'abi',
    merkle_schema VARCHAR(20) DEFAULT 'standard',
    contract_version VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deprecated_at TIMESTAMP WITH TIME ZONE
);
```

---

## 8. BLOCKCHAIN ADAPTER ARCHITECTURE

```
Evidence Integrity Layer
        ↓
Commitment Service
        ↓
Anchor Provider Interface
        ↓
┌───────────────────────────────────┐
│  EthereumAdapter (EVM chains)     │
│  ├── PolygonAdapter               │
│  ├── BaseAdapter                  │
│  └── PrivateEVMAdapter            │
├───────────────────────────────────┤
│  HyperledgerAdapter (future)      │
└───────────────────────────────────┘
```

### Interface (Python ABC)
```python
class AnchorProvider(ABC):
    @abstractmethod
    async def create_commitment(self, evidence_sha256, metadata) -> CommitmentResult
    
    @abstractmethod
    async def build_merkle_tree(self, commitments: list) -> MerkleTree
    
    @abstractmethod
    async def generate_proof(self, commitment, merkle_tree) -> MerkleProof
    
    @abstractmethod
    async def anchor_root(self, merkle_root, batch_id) -> AnchorResult
    
    @abstractmethod
    async def get_anchor(self, proof_id) -> AnchorRecord
    
    @abstractmethod
    async def verify_anchor(self, proof_id, expected_root) -> VerificationResult
```

---

## 9. VERIFICATION SERVICE — ONE-CLICK COURT VERIFICATION

### Verification Flow
```
INPUT: evidence file OR evidence ID + proof bundle
         ↓
STEP 1: LOCAL CRYPTOGRAPHIC VERIFICATION
  ├── Compute current SHA-256 of evidence file
  ├── Compare with recorded hash → MATCH / MISMATCH
  ├── Reconstruct commitment from evidence hash + metadata
  └── Verify Merkle proof → VALID / INVALID
         ↓
STEP 2: BLOCKCHAIN FINALITY VERIFICATION
  ├── Query on-chain anchor record
  ├── Compare Merkle root → MATCH / MISMATCH
  ├── Check block timestamp → CONFIRMED / PENDING
  └── Verify contract state → ACTIVE / REVOKED
         ↓
OUTPUT: VERIFICATION REPORT
  ✓/✗ File Integrity
  ✓/✗ Commitment Validity
  ✓/✗ Merkle Proof
  ✓/✗ Blockchain Anchor
  ✓/✗ Timestamp
  FINAL: VERIFIED / FAILED
```

### Proof Bundle (Portable)
```json
{
    "protocol": "CRIMEKIT-EIP-001",
    "version": 1,
    "evidence_id": "EV-004821",
    "evidence_sha256": "abc123...",
    "commitment_hash": "def456...",
    "merkle_proof": {
        "leaf_index": 5,
        "siblings": ["hash1", "hash2", "hash3"],
        "root": "ghi789..."
    },
    "blockchain": {
        "network": "polygon-amoy",
        "chain_id": 80002,
        "contract_address": "0x...",
        "tx_hash": "0x...",
        "block_number": 12345,
        "timestamp": "2026-09-07T12:00:00Z"
    },
    "provenance": {
        "root_evidence_id": "EV-004821",
        "derived_artifacts": 3,
        "lineage_depth": 2
    },
    "verification_instructions": "..."
}
```

---

## 10. SECURITY THREAT MODEL

| # | Threat | Impact | Likelihood | Mitigation | Residual |
|---|--------|--------|------------|------------|----------|
| 1 | Malicious investigator modifies evidence | HIGH | MEDIUM | SHA-256 + blockchain anchor + Merkle proof | Low — hash mismatch detected |
| 2 | Compromised backend database | HIGH | LOW | External blockchain anchor independent of DB | Low — on-chain proof persists |
| 3 | Stolen blockchain private key | HIGH | LOW | HSM/Vault for prod; env vars for dev; key rotation | Medium — attacker can anchor false proofs |
| 4 | RPC provider outage | MEDIUM | MEDIUM | Multiple RPC endpoints, retry queue, async anchoring | Low — evidence still usable, anchoring delayed |
| 5 | Blockchain reorganization | LOW | VERY LOW | Wait for confirmations (12 blocks), re-verify | Very low |
| 6 | Replay attack | LOW | LOW | Nonce management, unique proofIds, idempotency checks | Very low |
| 7 | Hash enumeration | MEDIUM | LOW | Commitments use metadata+version+salt, not raw hashes | Low |
| 8 | Correlation attack | MEDIUM | LOW | No PII on-chain, pseudonymous identifiers | Low |
| 9 | Unauthorized anchoring | HIGH | LOW | RBAC on anchor endpoints, signer isolation | Low |
| 10 | Proof forgery | HIGH | VERY LOW | Cryptographic Merkle proof validation, on-chain verification | Very low |

---

## 11. API SPECIFICATION

### Blockchain Routes (`/api/v1/blockchain/`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/anchor/evidence/{evidence_id}` | Anchor evidence to blockchain |
| POST | `/anchor/batch` | Force-anchor current pending batch |
| GET | `/anchor/{proof_id}` | Get anchor record |
| GET | `/anchor/{proof_id}/status` | Get anchoring status |
| GET | `/evidence/{evidence_id}/proof` | Generate proof bundle |
| POST | `/verify/evidence/{evidence_id}` | Full verification |
| POST | `/verify/proof-bundle` | Verify from proof bundle |
| GET | `/merkle/batches` | List Merkle batches |
| GET | `/merkle/batch/{batch_id}` | Get batch details |
| GET | `/provenance/{evidence_id}` | Get forensic lineage |
| GET | `/stats` | Blockchain statistics |
| GET | `/protocol` | Get protocol version info |

### Frontend Evidence Page Additions
- **Integrity Badge**: ✓ Hash verified / ✗ Mismatch
- **Blockchain Status**: ✓ Anchored / ⏳ Pending / ✗ Failed
- **View Proof Button**: Opens proof bundle modal
- **Verify Button**: Triggers independent verification
- **Provenance Graph**: Shows forensic lineage with blockchain anchors

---

## 12. IMPLEMENTATION PLAN

### Phase 6.1: Smart Contract (Solidity)
- EvidenceAnchor.sol
- Deployment script
- ABI export

### Phase 6.2: Blockchain Core (Python)
- `backend/app/blockchain/` package
- Config, models, adapter interface
- Ethereum adapter with web3.py

### Phase 6.3: Merkle Engine (Python)
- Standard Merkle tree implementation
- Proof generation and validation
- Batch management

### Phase 6.4: Commitment Service (Python)
- Evidence commitment creation
- Versioned commitments
- Provenance commitment

### Phase 6.5: Provenance Engine (Python)
- Forensic lineage tracking
- Artifact commitment creation
- Parent-child relationship management

### Phase 6.6: Anchor Queue (Python)
- Redis-based async anchoring queue
- Retry logic with exponential backoff
- Batch composition and finalization

### Phase 6.7: Verification Service (Python)
- Independent verification flow
- Merkle proof verification
- Blockchain anchor verification
- Proof bundle generation

### Phase 6.8: Database Schema (SQLAlchemy + Alembic)
- New models for blockchain tables
- Migration scripts

### Phase 6.9: API Routes (FastAPI)
- Blockchain router endpoints
- Integration with existing evidence flow

### Phase 6.10: Frontend (Next.js/React)
- Blockchain status components
- Proof viewer modal
- Verification UI
- Provenance graph visualization

### Phase 6.11: Tests
- Merkle tree tests
- Commitment tests
- Verification tests
- Adapter tests
- Integration tests
- Adversarial tests (tamper detection)

### Phase 6.12: Docker Integration
- web3.py in requirements.txt
- Environment variables
- Docker Compose additions

---

## 13. COST MODEL

| Scenario | Transactions | Cost/Transaction | Total Cost |
|----------|-------------|-----------------|------------|
| 100 evidence items | 1 (batched) | $0.001 | $0.001 |
| 1,000 evidence items | 8 | $0.001 | $0.008 |
| 10,000 evidence items | 79 | $0.001 | $0.079 |
| 100,000 evidence items | 782 | $0.001 | $0.782 |
| 1,000,000 evidence items | 7,813 | $0.001 | $7.813 |

**Merkle batching reduces cost by 99.9%** vs. one-transaction-per-evidence.

---

## 14. PRODUCTION MIGRATION PATH

1. **SIH Prototype**: Polygon Amoy testnet → free
2. **Demo/Competition**: Polygon Amoy testnet → ~$0.01 total
3. **Pilot Deployment**: Polygon mainnet → ~$0.01 per batch
4. **Enterprise Production**: 
   - Option A: Polygon mainnet (public, verifiable)
   - Option B: Hyperledger Fabric (permissioned, self-hosted)
   - Option C: Private EVM (Besu/Geth, air-gapped)
5. **Government/Law Enforcement**: Hyperledger Fabric with multi-institution consensus

---

## 15. AI/BLOCKCHAIN SEPARATION OF CONCERNS

| Component | Responsibility | NOT Responsible For |
|-----------|---------------|-------------------|
| **AI Pipeline** | Classification, extraction, summarization, entity recognition, correlation | Integrity verification, provenance anchoring |
| **Blockchain** | Integrity, provenance, commitment, timestamp anchoring, auditability | AI decision making, evidence interpretation |
| **Neo4j Graph** | Investigation relationships, entity connections, case links | Cryptographic proof generation |
| **PostgreSQL** | Operational data, chain-of-custody records, audit logs | External trust anchoring |

**Boundary Rule**: AI confidence scores are NEVER placed on blockchain. Blockchain proves the commitment exists, not that the AI result is correct.

---

*Protocol: CRIMEKIT-EIP-001 v1.0*
*Author: CrimeKit Enterprise Architecture Team*
*Date: 2026-09-07*
*Status: APPROVED FOR IMPLEMENTATION*
