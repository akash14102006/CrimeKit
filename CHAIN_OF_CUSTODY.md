# CrimeKit — Cryptographic Chain of Custody & Blockchain Verification

## 1. Legal Requirements & Integrity Guarantees
In judicial proceedings, evidence is only admissible if its provenance and chain of custody remain unbroken and demonstrably untampered with.

CrimeKit implements a dual-layer custody verification model:
1. **Application Event Ledger**: Every evidence lifecycle event (`upload`, `download`, `transfer`, `inspect`, `process`, `legal_hold`) generates an immutable audit record with user ID, timestamp, and before/after SHA-256 hashes.
2. **Blockchain Merkle Tree Anchoring**: Batch commitments of custody events and evidence hashes are structured into cryptographic Merkle trees.

---

## 2. Merkle Root Validation & Tamper Detection
- **Deterministic Leaf Generation**: `Leaf = SHA-256(evidence_id + sha256_hash + timestamp + actor_id)`
- **Proof of Existence**: Anyone with the Merkle proof path can mathematically verify evidence integrity against the anchored root without exposing confidential case details.
- **Single-Bit Tamper Rejection**: Any modification of an evidence file or metadata entry causes immediate recalculation failure, flagging the evidence as compromised.

---

## 3. Court-Ready Export
Court reports generated via `/compliance/export/court-admissible` package:
- Complete custody timeline with cryptographic signatures.
- Forensic tool versions and parameters.
- Examiner digital signatures and audit references.
