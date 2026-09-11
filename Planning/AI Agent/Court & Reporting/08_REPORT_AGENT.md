
# 08_REPORT_AGENT.md

# CrimeKit Enterprise Report Agent

> Specialized AI agent responsible for generating court-ready, evidence-backed investigation reports with complete traceability, citations, approvals, and export support.

---

# 1. Agent Purpose

The Report Agent converts outputs from all investigation agents into structured, explainable, court-ready reports. It preserves evidence references, chain of custody, and reasoning transparency while producing standardized reports for investigators, prosecutors, and reviewers.

---

# 2. Responsibilities

- Generate investigation reports
- Aggregate findings from all agents
- Preserve evidence citations
- Produce executive and technical summaries
- Maintain report versioning
- Validate report completeness
- Support review and approval workflows
- Export reports in multiple formats

---

# 3. Goals

- Court-ready documentation
- Complete traceability
- Deterministic formatting
- Explainable conclusions
- Human-review readiness

---

# 4. Folder Structure

```text
report-agent/
├── prompt.md
├── skills.md
├── instruction.md
├── graph.py
├── tools.py
├── memory.py
├── schemas.py
├── config.yaml
└── tests/
```

---

# 5. Inputs

- Supervisor output
- Detective findings
- Timeline
- Correlation graph
- GeoScope analysis
- Testimony analysis
- Evidence citations
- Case metadata
- RAG context
- Knowledge graph context

---

# 6. Outputs

- Executive summary
- Technical report
- Evidence index
- Timeline appendix
- Entity appendix
- Recommendations
- Confidence summary
- Audit metadata
- Export-ready document

---

# 7. Capabilities

- Multi-agent synthesis
- Citation management
- Report templating
- Section generation
- Executive summarization
- Appendix generation
- Report validation
- Multi-format export preparation

---

# 8. Limitations

- No fabrication of findings
- No unsupported conclusions
- No evidence modification
- No legal judgment

---

# 9. Reasoning Process

1. Validate inputs
2. Retrieve missing context
3. Aggregate agent outputs
4. Verify citations
5. Build report structure
6. Validate completeness
7. Score confidence
8. Produce final report

---

# 10. Decision Tree

Receive request
→ Required agent outputs available?
→ Aggregate findings
→ Validate citations
→ Missing sections?
→ Request completion
→ Human approval required?
→ Generate final report

---

# 11. LangGraph State

- request_id
- investigation_id
- report_sections
- evidence_index
- citations
- confidence
- approvals
- export_targets
- errors

---

# 12. graph.py Design

Nodes

- start
- validate
- retrieve_context
- collect_agent_outputs
- verify_citations
- assemble_report
- validate_report
- human_review
- export
- audit
- end

Conditional branches

- retry
- fallback
- supervisor_review

---

# 13. tools.py Design

Shared tools

- retrieve_rag()
- search_vector()
- query_graph()
- fetch_case()
- build_pdf()
- build_docx()
- build_html()
- build_json()
- citation_validator()
- report_validator()

---

# 14. memory.py Design

Working Memory
- Current report assembly

Session Memory
- Investigation context

Report Memory
- Draft versions

Vector Memory
- Retrieved evidence

Knowledge Memory
- Entity relationships

Audit Memory
- Version history and approvals

---

# 15. prompt.md Structure

- Identity
- Mission
- Report objectives
- Formatting rules
- Citation policy
- Confidence policy
- Output schema
- Safety rules
- Export requirements

---

# 16. skills.md Usage

Skills

- Report Composition
- Executive Summary
- Technical Writing
- Citation Verification
- Evidence Indexing
- Appendix Generation
- Report Validation

---

# 17. instruction.md

Rules

- Never omit supporting citations
- Distinguish evidence from inference
- Preserve original findings
- Do not alter evidence
- Escalate missing information
- Produce schema-compliant output

---

# 18. schemas.py

Models

- ReportRequest
- ReportResponse
- ReportSection
- ExecutiveSummary
- EvidenceIndex
- Appendix
- Citation
- ConfidenceScore
- ApprovalRecord
- ErrorResponse

---

# 19. config.yaml

Configuration

- llm_model
- embedding_model
- report_template
- confidence_threshold
- retry_limit
- timeout
- logging_level
- export_formats
- cache_ttl

---

# 20. RAG Strategy

Retrieve only report-relevant evidence.

Pipeline

Request
→ Hybrid Retrieval
→ Metadata Filter
→ Evidence Validation
→ Context Assembly
→ Report Generation
→ Citation Verification

---

# 21. Knowledge Graph Usage

Use Neo4j to

- validate entity references
- enrich appendices
- cross-reference relationships
- verify investigation consistency

---

# 22. Memory Strategy

Maintain

- report drafts
- accepted revisions
- rejected revisions
- evidence references
- approval history

---

# 23. Retry Logic

Retry

- retrieval failures
- export failures
- temporary service outages

Use exponential backoff.

---

# 24. Fallback Strategy

If report generation fails

- regenerate affected sections
- rebuild citations
- request missing outputs
- escalate to Supervisor
- require human review

---

# 25. Observability

Capture

- report generation latency
- validation latency
- export latency
- token usage
- approval duration

---

# 26. Metrics

- report completeness
- citation coverage
- validation success
- export success
- response latency
- hallucination rate

---

# 27. Logging

Structured logs

- request_id
- investigation_id
- report_version
- sections_generated
- citations
- exports
- latency
- outcome

---

# 28. Security

- JWT validation
- RBAC
- Tool authorization
- Prompt injection protection
- Secret isolation
- Output sanitization

---

# 29. Ethical Constraints

- Preserve evidence integrity
- Respect privacy
- Clearly distinguish facts from inference
- Support human review
- Avoid biased language

---

# 30. Hallucination Prevention

- Retrieval-first workflow
- Mandatory citations
- Cross-agent validation
- Confidence scoring
- Reject unsupported conclusions

---

# 31. Testing

Unit
- report templates
- citation validator
- export builders

Integration
- RAG
- knowledge graph
- export services

End-to-End
- full investigation report
- supervisor workflow
- approval lifecycle

Regression
- schema validation
- formatting stability

---

# 32. Acceptance Criteria

Production ready when

- Reports include complete citations
- Required sections are generated
- Confidence scores exist
- Exports succeed
- Security checks pass
- Tests pass

---

# 33. Developer Checklist

- Implement graph nodes
- Create prompts
- Implement tools
- Configure memory
- Build schemas
- Add retries
- Add observability
- Add security
- Write automated tests
- Validate production readiness

---

# 34. Guiding Principle

The Report Agent is the final documentation engine of CrimeKit. It transforms validated investigation outputs into professional, evidence-backed, auditable reports suitable for review, collaboration, and court presentation while maintaining transparency, traceability, and enterprise-grade quality.
