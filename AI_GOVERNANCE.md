# CrimeKit — AI Governance, RAG Architecture & Safety Principles

## 1. Absolute Boundaries of AI in Forensics
In CrimeKit, artificial intelligence is strictly an **investigative aid**, never the authoritative source of forensic truth:
- **Zero Evidence Modification**: AI agents and LLM inferences have no write permissions to evidence files, custody records, or metadata.
- **No Guilt Claims or Certainty Fabrication**: AI query responses must never assert guilt, liability, or definitive identity. Outputs must use measured evidentiary language such as:
  - *"Potential match identified"*
  - *"Candidate requiring human examiner verification"*
  - *"Discrepancy detected in timeline logs"*
- **Grounding and Citation**: Every claim made by the AI Agent must reference specific document chunks, evidence IDs, and line/page offsets.

---

## 2. Case-Scoped RAG Pipeline

```
Evidence File / Artifact
           ↓
Text Extraction (OCR, metadata, EVTX, strings)
           ↓
Chunking & Normalization
           ↓
Embedding Generation (Deterministic SHA-256 fallback / OpenAI)
           ↓
Vector Storage (Scattered with case_id and evidence_id tags)
           ↓
Case-Filtered Vector Search (Enforcing case_id == current_case)
           ↓
Relevance Re-Ranking & Context Assembly
           ↓
LLM Investigative Reasoning & Citation Attachment
```

### Case Isolation Guarantee
Every query submitted to `/ai/agent/query` requires an authenticated investigator context. The vector retrieval engine strictly rejects cross-case document retrieval, ensuring that evidence from Case A is completely invisible to queries within Case B.
