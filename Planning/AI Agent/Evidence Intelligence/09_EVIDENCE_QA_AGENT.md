
# 09_EVIDENCE_QA_AGENT.md

# CrimeKit Enterprise Evidence QA Agent

> Specialized AI agent responsible for answering investigator questions using only verified case evidence through Retrieval-Augmented Generation (RAG), knowledge graph reasoning, and explainable citations.

---

# 1. Agent Purpose

The Evidence QA Agent serves as the trusted conversational interface for investigators. It retrieves, analyzes, and synthesizes evidence to answer questions while ensuring every answer is traceable to supporting evidence.

It does **not** invent facts, speculate beyond the evidence, or replace investigator judgment.

---

# 2. Responsibilities

- Answer investigation questions
- Retrieve relevant evidence
- Rank evidence by relevance
- Generate evidence-backed answers
- Cite supporting artifacts
- Explain uncertainty
- Recommend follow-up questions
- Escalate unanswered queries

---

# 3. Goals

- Accurate evidence retrieval
- Citation-first responses
- Low hallucination rate
- Explainable reasoning
- Fast investigator assistance

---

# 4. Folder Structure

```text
evidence-qa-agent/
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

- Investigator question
- Case identifier
- Evidence metadata
- Documents
- Images
- Audio transcripts
- Timeline outputs
- Correlation outputs
- Knowledge graph context
- RAG retrieval context

---

# 6. Outputs

- Direct answer
- Supporting evidence
- Evidence citations
- Confidence score
- Related entities
- Suggested follow-up questions
- Escalation recommendation (if required)

---

# 7. Capabilities

- Natural-language question answering
- Hybrid retrieval
- Multi-modal evidence lookup
- Citation generation
- Entity-aware reasoning
- Context summarization
- Follow-up question suggestion

---

# 8. Limitations

- No unsupported answers
- No fabricated citations
- No evidence modification
- No legal conclusions

---

# 9. Reasoning Process

1. Validate question
2. Retrieve relevant evidence
3. Expand context with knowledge graph
4. Rank retrieved evidence
5. Generate answer
6. Verify citations
7. Score confidence
8. Return structured response

---

# 10. Decision Tree

Question
→ Evidence available?
→ Retrieve context
→ Sufficient evidence?
→ Generate answer
→ Verify citations
→ Confidence acceptable?
→ Respond
→ Otherwise request more evidence or escalate

---

# 11. LangGraph State

- request_id
- investigation_id
- user_question
- retrieved_chunks
- graph_context
- answer
- citations
- confidence
- tool_results
- errors

---

# 12. graph.py Design

Nodes

- start
- validate
- retrieve_context
- expand_graph_context
- rank_evidence
- generate_answer
- verify_citations
- confidence_score
- finalize
- audit
- end

Branches

- retry
- fallback
- supervisor_review

---

# 13. tools.py Design

- hybrid_retrieval()
- vector_search()
- keyword_search()
- query_graph()
- rerank_results()
- summarize_context()
- citation_builder()
- fetch_case()

All tools return typed request/response objects.

---

# 14. memory.py Design

- Working Memory
- Session Memory
- QA History
- Vector Memory
- Knowledge Memory
- Audit Memory

---

# 15. prompt.md Structure

- Identity
- Mission
- Allowed evidence
- Available tools
- Retrieval rules
- Citation policy
- Confidence policy
- Output schema
- Safety rules
- Hallucination prevention

---

# 16. skills.md Usage

Skills

- Evidence Retrieval
- Question Understanding
- Context Ranking
- Multi-hop Reasoning
- Citation Generation
- Answer Summarization

Each skill specifies purpose, inputs, outputs, tools, and expected confidence.

---

# 17. instruction.md

Rules

- Retrieve before reasoning
- Never answer without evidence
- Preserve evidence wording where appropriate
- Clearly distinguish evidence from inference
- Always provide citations
- Explain uncertainty

---

# 18. schemas.py

Models

- QARequest
- QAResponse
- EvidenceChunk
- Citation
- ConfidenceScore
- SuggestedQuestion
- ErrorResponse

---

# 19. config.yaml

Configuration

- llm_model
- embedding_model
- reranker_model
- retrieval_top_k
- confidence_threshold
- retry_limit
- timeout
- logging_level
- cache_ttl

---

# 20. RAG Strategy

Pipeline

Question
→ Hybrid Retrieval
→ Metadata Filtering
→ Vector Search
→ Keyword Search
→ Reranking
→ Knowledge Graph Expansion
→ Context Assembly
→ Answer Generation
→ Citation Verification

---

# 21. Knowledge Graph Usage

Use Neo4j to:

- Link entities
- Expand relationships
- Discover connected evidence
- Improve multi-hop retrieval
- Validate context consistency

---

# 22. Memory Strategy

Store

- previous questions
- retrieved evidence
- accepted answers
- rejected answers
- confidence history

Expire temporary reasoning after completion.

---

# 23. Retry Logic

Retry

- retrieval failures
- graph query failures
- timeout events

Use configurable exponential backoff.

---

# 24. Fallback Strategy

If insufficient evidence:

- broaden retrieval
- search metadata
- query knowledge graph
- request clarification
- escalate to Supervisor

---

# 25. Observability

Track

- retrieval latency
- reranking latency
- answer generation latency
- token usage
- citation coverage

---

# 26. Metrics

- Answer accuracy
- Retrieval precision
- Citation coverage
- Hallucination rate
- Average latency
- User satisfaction

---

# 27. Logging

Structured logs

- request_id
- investigation_id
- question
- retrieved_chunks
- citations
- tool_calls
- latency
- outcome

---

# 28. Security

- RBAC
- JWT validation
- Tool authorization
- Prompt injection detection
- Secret isolation
- Output sanitization

---

# 29. Ethical Constraints

- Preserve evidence integrity
- Respect privacy
- Avoid unsupported claims
- Require human review for high-risk decisions
- Clearly separate evidence from inference

---

# 30. Hallucination Prevention

- Retrieval-first workflow
- Mandatory evidence citations
- Confidence scoring
- Cross-check retrieved context
- Reject unsupported answers
- Explain uncertainty

---

# 31. Testing

Unit

- retrieval
- reranking
- citation builder

Integration

- vector database
- knowledge graph
- memory synchronization

End-to-End

- investigator QA workflow
- supervisor integration
- failure recovery

Regression

- prompt stability
- schema validation

---

# 32. Acceptance Criteria

Production-ready when

- Every answer includes supporting evidence
- Citations are valid
- Confidence score is computed
- Schemas validate
- Security checks pass
- Tests succeed

---

# 33. Developer Checklist

- Implement graph nodes
- Define prompts
- Build retrieval tools
- Configure memory
- Create schemas
- Configure retries
- Add observability
- Add security
- Write automated tests
- Validate production readiness

---

# 34. Guiding Principle

The Evidence QA Agent is the trusted evidence interface of CrimeKit. Every answer must be reproducible, evidence-backed, transparent, and fully traceable through citations, ensuring investigators receive reliable assistance while preserving the integrity of the investigation.
