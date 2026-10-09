# CrimeKit — 3-Minute Hackathon Demo Script

> **Nebius × NVIDIA Global AI Hackathon (Best Apps & Agents)**  
> Case: `CASE-2026-001` (State v. Rahul Kumar / Evening Incident)

---

### [0:00 - 0:25] The Problem & Introduction
- **Presenter:** "Digital investigations today are crippled by fragmentation. An investigator must juggle call records, tower pings, GPS coordinates, and witness statements. LLM wrappers hallucinate and claim to 'detect lies,' which has zero forensic validity."
- **Action:** Open CrimeKit dashboard, navigate to `CASE-2026-001`, and enter the **AI Investigation Workspace**.
- **Presenter:** "CrimeKit is an evidence-grounded multi-agent platform powered by **NVIDIA Nemotron** on **Nebius Token Factory**."

---

### [0:25 - 0:50] The Orchestrated Query
- **Presenter:** "Watch what happens when an investigator submits an overarching question:"
- **Query:** 
  > *"Determine whether Rahul Kumar was associated with the phone number, what happened around the relevant call, whether the device was near the incident location, and whether witness testimony is consistent with the digital evidence."*
- **Action:** Submit query in ChatPanel.
- **Visual:** The **Case Orchestrator** planning pipeline activates.
- **Presenter:** "Notice the multi-agent dispatch: Orchestrator delegates entity resolution to **Detective**, chronology to **Timeline**, cell sectors to **GeoScope**, and deposition decomposition to **Testimony**."

---

### [0:50 - 1:25] Specialist Tools & Evidence Grounding
- **Action:** Scroll through the **Tool Execution Feed**.
- **Showcase:**
  - `evidence_search` and `entity_search` resolve Rahul Kumar and map phone records.
  - `timeline_search` correlates outgoing call at 21:14:00 UTC.
  - `movement_trace` identifies cell tower ping at Sector 4.
  - `extract_claims` extracts Claim CLM-001: *"Rahul called me at 21:00"* and Claim CLM-002: *"I was at the railway station."*
- **Presenter:** "Every finding strictly cites its evidence artifact (`EV-104`, `EV-119`). No hallucinated evidence IDs."

---

### [1:25 - 1:55] Interactive Contradiction Matrix
- **Action:** Switch to the **Matrix** tab in the workspace panel.
- **Visual:** The Contradiction Matrix displays rows of claims versus digital evidence.
- **Highlight:**
  - **Temporal Conflict (Severity: High):** Witness asserts call at 21:00:00; CDR record `EV-104` proves incoming call occurred at 21:14:00 (14-minute delta).
  - **Spatial Conflict (Severity: Medium):** Witness places device at Railway Station; tower sector `EV-119` registers 3.4 km away.
- **Presenter:** "CrimeKit does NOT say 'the witness is lying.' It calculates the deterministic 14-minute delta and flags it for human review."
- **Action:** Investigator adds note: *"Confirmed discrepancy against carrier CDR record"* and clicks **[Confirm Contradiction]**.

---

### [1:55 - 2:20] Forensic Report Synthesis
- **Action:** Switch to the Report Preview.
- **Visual:** The Report Agent has synthesized court-reviewable markdown/PDF exhibits, linking:
  - Cryptographic SHA-256 Hash Ledger
  - Chain of Custody Log
  - Investigator-Confirmed Contradiction Exhibits
- **Presenter:** "Notice the human review boundary notice: AI correlation assists analysis, but judicial determination remains with human counsel."

---

### [2:20 - 2:45] Tamper-Evident Case Sealing & Offline Archive
- **Action:** Switch to the **Seal/Archive** tab.
- **Visual:** Pre-seal validation checklist passes (evidence hashes intact, report generated).
- **Action:** Click **[Seal Case State]**.
- **Visual:** Master **Case Root Hash** is calculated:
  $$\text{CASE ROOT HASH: } \texttt{7f83b1657ff1fc53b92dc18148a1d65...}$$
- **Presenter:** "We've computed an 8-dimensional Merkle-style root across evidence, timeline, claims, reviews, and reports. Now we export the offline archive."
- **Action:** Click **[Download Archive]** to download `crimekit-case-archive-CASE-2026-001-v1.zip`.

---

### [2:45 - 3:00] Zero-Dependency Offline Verifier & Conclusion
- **Action:** Extract the ZIP and open `archive/verification.html` in an offline browser tab.
- **Visual:**
  - `✓ ARCHIVE INTEGRITY VERIFIED`
  - All subtree roots and evidence hashes are displayed and verified locally without internet or backend servers.
- **Presenter:** "CrimeKit demonstrates the full power of NVIDIA Nemotron on Nebius: autonomous multi-agent planning, rigorous tool calling, deterministic discrepancy detection, human decision-making, and verifiable offline archives. Thank you."
