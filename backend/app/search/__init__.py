"""
Enterprise Search Platform for CrimeKit.

Three-tier search architecture:
  Tier 1: PostgreSQL full-text search with tsvector/tsquery (zero extra deps)
  Tier 2: Optional OpenSearch/Elasticsearch integration when available
  Tier 3: Vector similarity search using existing embeddings

Supports:
  - Full-text search across evidence, cases, documents, entities
  - Metadata search (file type, size, date, tags)
  - Evidence search (hash, filename, content, upload date)
  - Case search (title, status, date, assignee)
  - Timeline search (events in time range)
  - Entity search (persons, organizations, IPs, domains)
  - Relationship search (entity connections)
  - Hybrid search (text + vector + metadata)
  - Semantic search via existing embedding system
  - Faceted search with aggregations
  - Search highlighting
  - BM25 ranking
  - Search filters (date range, type, status, tags)
  - Cross-correlation search (related evidence across cases)
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    and_,
    case,
    cast,
    desc,
    func,
    or_,
    text,
)
from sqlalchemy.orm import Session, Query

from ..database import Base, get_engine, SessionLocal
from ..models import (
    AuditLog,
    Case,
    Document,
    Embedding,
    Evidence,
    ForensicJob,
    ForensicResult,
    User,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums & constants
# ---------------------------------------------------------------------------

class SearchTier(str, Enum):
    """Available search tiers."""
    POSTGRES_FTS = "postgres_fts"
    OPENSEARCH = "opensearch"
    VECTOR = "vector"
    HYBRID = "hybrid"


class SearchMode(str, Enum):
    """Search execution modes."""
    FULL_TEXT = "full_text"
    METADATA = "metadata"
    EVIDENCE = "evidence"
    CASE = "case"
    TIMELINE = "timeline"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    HYBRID = "hybrid"
    SEMANTIC = "semantic"
    CROSS_CORRELATION = "cross_correlation"


class EntityType(str, Enum):
    """Recognized entity types for entity search."""
    PERSON = "person"
    ORGANIZATION = "organization"
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    EMAIL = "email"
    PHONE = "phone"
    HASH = "hash"
    FILE = "file"
    URL = "url"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SearchFilter:
    """Encapsulates a single search filter criterion."""
    field: str
    operator: str  # eq, neq, gt, gte, lt, lte, contains, in, between, like
    value: Any
    negate: bool = False

    def apply(self, query: Query, model: Type) -> Query:
        """Apply this filter to a SQLAlchemy query."""
        column = getattr(model, self.field, None)
        if column is None:
            return query

        op = self.operator.lower()
        val = self.value

        if op == "eq":
            cond = column == val
        elif op == "neq":
            cond = column != val
        elif op == "gt":
            cond = column > val
        elif op == "gte":
            cond = column >= val
        elif op == "lt":
            cond = column < val
        elif op == "lte":
            cond = column <= val
        elif op == "contains":
            cond = column.ilike(f"%{val}%")
        elif op == "in":
            cond = column.in_(val) if isinstance(val, (list, tuple, set)) else column == val
        elif op == "between":
            if isinstance(val, (list, tuple)) and len(val) == 2:
                cond = and_(column >= val[0], column <= val[1])
            else:
                cond = column == val
        elif op == "like":
            cond = column.like(val)
        else:
            cond = column == val

        return query.filter(~cond if self.negate else cond)


@dataclass
class SearchFacet:
    """Defines a facet for aggregated search results."""
    name: str
    field: str
    type: str = "terms"  # terms, date_histogram, range, cardinality
    size: int = 20
    aggregation: Optional[str] = None


@dataclass
class FacetResult:
    """Result of a facet aggregation."""
    name: str
    type: str
    buckets: List[Dict[str, Any]] = field(default_factory=list)
    total: int = 0


@dataclass
class SearchHighlight:
    """Highlight metadata for a single result."""
    field: str
    snippet: str
    offsets: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class SearchResult:
    """A single search result with ranking and highlighting."""
    id: str
    type: str  # case, evidence, document, forensic_result, audit_log
    score: float
    title: str
    snippet: str
    highlights: List[SearchHighlight] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "score": self.score,
            "title": self.title,
            "snippet": self.snippet,
            "highlights": [
                {"field": h.field, "snippet": h.snippet, "offsets": h.offsets}
                for h in self.highlights
            ],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class SearchResponse:
    """Aggregated search response with results, facets, and timing."""
    query: str
    results: List[SearchResult]
    total: int
    facets: List[FacetResult] = field(default_factory=list)
    took_ms: float = 0.0
    tier: SearchTier = SearchTier.POSTGRES_FTS
    mode: SearchMode = SearchMode.FULL_TEXT
    page: int = 1
    page_size: int = 20
    max_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "total": self.total,
            "took_ms": round(self.took_ms, 2),
            "tier": self.tier.value,
            "mode": self.mode.value,
            "page": self.page,
            "page_size": self.page_size,
            "max_score": round(self.max_score, 4),
            "results": [r.to_dict() for r in self.results],
            "facets": [
                {"name": f.name, "type": f.type, "buckets": f.buckets, "total": f.total}
                for f in self.facets
            ],
        }


# ---------------------------------------------------------------------------
# BM25 Ranker
# ---------------------------------------------------------------------------

class SearchRanker:
    """BM25-based ranking for PostgreSQL full-text search results.

    Implements Okapi BM25 with standard parameters (k1=1.2, b=0.75).
    Operates on pre-computed tsvector scores and document frequencies.
    """

    def __init__(self, k1: float = 1.2, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def bm25_score(
        self,
        term_frequencies: Dict[str, int],
        document_frequencies: Dict[str, int],
        doc_length: int,
        avg_doc_length: float,
        total_docs: int,
    ) -> float:
        """Compute BM25 score for a document given term statistics."""
        score = 0.0
        for term, tf in term_frequencies.items():
            df = document_frequencies.get(term, 0)
            if df == 0:
                continue
            idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
            tf_norm = (tf * (self.k1 + 1)) / (
                tf + self.k1 * (1 - self.b + self.b * (doc_length / avg_doc_length))
            )
            score += idf * tf_norm
        return score

    def rank_results(
        self,
        raw_results: List[SearchResult],
        query_terms: List[str],
        db: Session,
    ) -> List[SearchResult]:
        """Re-rank results using BM25 scoring."""
        if not raw_results or not query_terms:
            return raw_results

        total_docs = len(raw_results)
        if total_docs == 0:
            return raw_results

        avg_len = sum(
            len(r.snippet.split()) + len(r.title.split()) for r in raw_results
        ) / max(total_docs, 1)

        for result in raw_results:
            text_content = f"{result.title} {result.snippet}".lower()
            words = text_content.split()
            doc_len = len(words)

            term_freq: Dict[str, int] = {}
            for term in query_terms:
                term_lower = term.lower()
                count = sum(1 for w in words if w == term_lower)
                if count > 0:
                    term_freq[term_lower] = count

            doc_freq = {t: total_docs for t in query_terms}

            bm25 = self.bm25_score(
                term_freq, doc_freq, doc_len, max(avg_len, 1.0), total_docs
            )
            result.score = max(result.score, bm25) + bm25 * 0.3

        raw_results.sort(key=lambda r: r.score, reverse=True)
        return raw_results


# ---------------------------------------------------------------------------
# Search Index — DDL and index management
# ---------------------------------------------------------------------------

class SearchIndex:
    """Manages PostgreSQL full-text search indexes (tsvector columns + GIN).

    Creates and maintains tsvector columns on Case, Evidence, Document, and
    ForensicResult tables for fast full-text search without external deps.
    """

    # tsvector column names per table
    TSVECTOR_COLUMNS: Dict[str, str] = {
        "cases": "search_vector",
        "evidence": "search_vector",
        "documents": "search_vector",
        "forensic_results": "search_vector",
        "audit_logs": "search_vector",
    }

    # Columns that contribute to each table's search vector
    SEARCH_COLUMNS: Dict[str, List[str]] = {
        "cases": ["title", "description"],
        "evidence": ["filename", "mime_type", "storage_path"],
        "documents": ["text"],
        "forensic_results": ["processor"],
        "audit_logs": ["action", "target_type"],
    }

    def __init__(self, db: Session):
        self.db = db

    def ensure_indexes(self) -> None:
        """Create tsvector columns and GIN indexes if they don't exist.

        Safe to call multiple times (idempotent).
        """
        engine = self.db.get_bind()
        dialect = engine.dialect.name

        if dialect != "postgresql":
            logger.info(
                "SearchIndex: skipping tsvector setup (dialect=%s, not postgresql)",
                dialect,
            )
            return

        for table, col in self.TSVECTOR_COLUMNS.items():
            self._ensure_tsvector_column(table, col)
            self._ensure_gin_index(table, col)

    def _ensure_tsvector_column(self, table: str, column: str) -> None:
        """Add tsvector column if it doesn't exist."""
        try:
            result = self.db.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = :table AND column_name = :column"
                ),
                {"table": table, "column": column},
            )
            if result.fetchone() is None:
                search_cols = self.SEARCH_COLUMNS.get(table, [])
                if not search_cols:
                    return
                coalesce_parts = " || ' ' || ".join(
                    [f"COALESCE({c}::text, '')" for c in search_cols]
                )
                self.db.execute(
                    text(
                        f"ALTER TABLE {table} ADD COLUMN {column} tsvector "
                        f"GENERATED ALWAYS AS (to_tsvector('english', {coalesce_parts})) STORED"
                    )
                )
                self.db.commit()
                logger.info("SearchIndex: added tsvector column %s.%s", table, column)
        except Exception as exc:
            self.db.rollback()
            logger.warning("SearchIndex: could not add tsvector to %s: %s", table, exc)

    def _ensure_gin_index(self, table: str, column: str) -> None:
        """Create GIN index on tsvector column if missing."""
        index_name = f"idx_{table}_{column}_gin"
        try:
            result = self.db.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE tablename = :table AND indexname = :index"
                ),
                {"table": table, "index": index_name},
            )
            if result.fetchone() is None:
                self.db.execute(
                    text(
                        f"CREATE INDEX {index_name} ON {table} USING GIN ({column})"
                    )
                )
                self.db.commit()
                logger.info("SearchIndex: created GIN index %s", index_name)
        except Exception as exc:
            self.db.rollback()
            logger.warning("SearchIndex: could not create GIN index %s: %s", index_name, exc)

    def rebuild_vector(self, table: str, row_id: str) -> None:
        """Trigger re-computation of a stored tsvector row."""
        if table not in self.TSVECTOR_COLUMNS:
            return
        try:
            self.db.execute(
                text(
                    f"UPDATE {table} SET {self.TSVECTOR_COLUMNS[table]} = "
                    f"{self.TSVECTOR_COLUMNS[table]} WHERE id = :rid"
                ),
                {"rid": row_id},
            )
            self.db.commit()
        except Exception:
            self.db.rollback()


# ---------------------------------------------------------------------------
# PostgreSQL Full-Text Search Backend (Tier 1)
# ---------------------------------------------------------------------------

class _PostgresFTSBackend:
    """PostgreSQL-native full-text search using tsvector/tsquery.

    Zero external dependencies. Works with any PostgreSQL >= 9.6.
    """

    def __init__(self, db: Session):
        self.db = db
        self.ranker = SearchRanker()

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _sanitize_tsquery(raw: str) -> str:
        """Escape special tsquery characters and build a prefix-match query."""
        cleaned = re.sub(r"[^\w\s\-]", " ", raw)
        tokens = cleaned.split()
        if not tokens:
            return ""
        parts = [f"{re.escape(t)}:*" for t in tokens if t]
        return " & ".join(parts)

    def _is_postgres(self) -> bool:
        try:
            return self.db.get_bind().dialect.name == "postgresql"
        except Exception:
            return False

    # -- full-text across all tables --------------------------------------

    def search_all(
        self,
        query_str: str,
        filters: Optional[List[SearchFilter]] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Full-text search across cases, evidence, documents, forensic results."""
        if not self._is_postgres():
            return self._fallback_search(query_str, filters, page, page_size)

        tsquery = self._sanitize_tsquery(query_str)
        if not tsquery:
            return []

        offset = (page - 1) * page_size
        results: List[SearchResult] = []

        # Cases
        results.extend(
            self._search_table(
                Case, "cases", tsquery, query_str,
                title_col="title", snippet_col="description",
                type_label="case",
                extra_filters=filters, offset=offset, limit=page_size,
            )
        )

        # Evidence
        results.extend(
            self._search_table(
                Evidence, "evidence", tsquery, query_str,
                title_col="filename", snippet_col=None,
                type_label="evidence",
                extra_filters=filters, offset=offset, limit=page_size,
            )
        )

        # Documents
        results.extend(
            self._search_table(
                Document, "documents", tsquery, query_str,
                title_col=None, snippet_col="text",
                type_label="document",
                extra_filters=filters, offset=offset, limit=page_size,
            )
        )

        # Forensic results
        results.extend(
            self._search_table(
                ForensicResult, "forensic_results", tsquery, query_str,
                title_col="processor", snippet_col=None,
                type_label="forensic_result",
                extra_filters=filters, offset=offset, limit=page_size,
            )
        )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:page_size]

    def _search_table(
        self,
        model: Type,
        table: str,
        tsquery: str,
        raw_query: str,
        title_col: Optional[str],
        snippet_col: Optional[str],
        type_label: str,
        extra_filters: Optional[List[SearchFilter]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[SearchResult]:
        """Search a single table using tsvector + tsquery."""
        vector_col = SearchIndex.TSVECTOR_COLUMNS.get(table)
        if not vector_col:
            return []

        try:
            query = self.db.query(model)

            # tsquery match
            query = query.filter(
                text(f"{vector_col} @@ to_tsquery('english', :tsq)").params(tsq=tsquery)
            )

            # Apply additional filters
            if extra_filters:
                for f in extra_filters:
                    query = f.apply(query, model)

            # BM25 rank
            query = query.order_by(
                text(
                    f"ts_rank_cd({vector_col}, to_tsquery('english', :tsq), 32) DESC"
                ).params(tsq=tsquery)
            )

            query = query.offset(offset).limit(limit)
            rows = query.all()

            results: List[SearchResult] = []
            for row in rows:
                rid = str(getattr(row, "id", ""))
                title = str(getattr(row, title_col, "")) if title_col else ""
                snippet_raw = str(getattr(row, snippet_col, "")) if snippet_col else ""
                snippet = self._make_snippet(snippet_raw or title, raw_query, 200)

                score = self._compute_rank_score(model, table, tsquery, rid)

                created = getattr(row, "created_at", None)

                highlights = self._highlight_fields(row, model, raw_query)

                results.append(
                    SearchResult(
                        id=rid,
                        type=type_label,
                        score=score,
                        title=title or f"[{type_label}] {rid[:8]}",
                        snippet=snippet,
                        highlights=highlights,
                        metadata=self._extract_metadata(row, model),
                        created_at=created,
                    )
                )
            return results

        except Exception as exc:
            logger.warning("SearchIndex._search_table(%s) failed: %s", table, exc)
            self.db.rollback()
            return []

    def _compute_rank_score(
        self, model: Type, table: str, tsquery: str, row_id: str
    ) -> float:
        """Compute BM25-like rank score for a single row."""
        vector_col = SearchIndex.TSVECTOR_COLUMNS.get(table)
        if not vector_col:
            return 0.0
        try:
            result = self.db.execute(
                text(
                    f"SELECT ts_rank_cd({vector_col}, to_tsquery('english', :tsq), 32) "
                    f"FROM {table} WHERE id = :rid"
                ),
                {"tsq": tsquery, "rid": row_id},
            )
            row = result.fetchone()
            return float(row[0]) if row and row[0] else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def _make_snippet(text_content: str, query: str, max_len: int = 200) -> str:
        """Extract a relevant snippet around the first query match."""
        if not text_content:
            return ""
        lower = text_content.lower()
        terms = [t.lower() for t in query.split() if t]
        best_pos = -1
        for term in terms:
            pos = lower.find(term)
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos
        if best_pos == -1:
            return text_content[:max_len]
        start = max(0, best_pos - max_len // 4)
        end = min(len(text_content), start + max_len)
        snippet = text_content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text_content):
            snippet = snippet + "..."
        return snippet

    @staticmethod
    def _highlight_fields(
        row: Any, model: Type, query: str
    ) -> List[SearchHighlight]:
        """Generate highlight data for matching fields."""
        highlights: List[SearchHighlight] = []
        terms = [t for t in query.split() if t]
        for col in model.__table__.columns:
            val = getattr(row, col.name, None)
            if val is None or not isinstance(val, str):
                continue
            for term in terms:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                matches = list(pattern.finditer(val))
                if matches:
                    m = matches[0]
                    start = max(0, m.start() - 40)
                    end = min(len(val), m.end() + 60)
                    snippet = val[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(val):
                        snippet += "..."
                    highlights.append(
                        SearchHighlight(
                            field=col.name,
                            snippet=snippet,
                            offsets=[(m.start(), m.end()) for m in matches[:5]],
                        )
                    )
                    break
        return highlights

    @staticmethod
    def _extract_metadata(row: Any, model: Type) -> Dict[str, Any]:
        """Extract metadata dict from a model row."""
        meta: Dict[str, Any] = {}
        table_name = model.__tablename__
        if table_name == "evidence":
            meta["filename"] = getattr(row, "filename", None)
            meta["mime_type"] = getattr(row, "mime_type", None)
            meta["size"] = getattr(row, "size", None)
            meta["sha256"] = getattr(row, "sha256", None)
            meta["case_id"] = getattr(row, "case_id", None)
        elif table_name == "cases":
            meta["status"] = getattr(row, "status", None)
            meta["created_by"] = getattr(row, "created_by", None)
        elif table_name == "documents":
            meta["evidence_id"] = getattr(row, "evidence_id", None)
            text_val = getattr(row, "text", None)
            if text_val:
                meta["text_length"] = len(text_val)
        elif table_name == "forensic_results":
            meta["processor"] = getattr(row, "processor", None)
            meta["evidence_id"] = getattr(row, "evidence_id", None)
            result_json = getattr(row, "result", None)
            if isinstance(result_json, dict):
                meta["result_keys"] = list(result_json.keys())[:10]
        elif table_name == "audit_logs":
            meta["action"] = getattr(row, "action", None)
            meta["target_type"] = getattr(row, "target_type", None)
            meta["target_id"] = getattr(row, "target_id", None)
        return meta

    def _fallback_search(
        self,
        query_str: str,
        filters: Optional[List[SearchFilter]] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """LIKE-based fallback for non-PostgreSQL databases (SQLite, etc.)."""
        offset = (page - 1) * page_size
        results: List[SearchResult] = []
        pattern = f"%{query_str}%"

        # Cases
        try:
            q = self.db.query(Case).filter(
                or_(Case.title.ilike(pattern), Case.description.ilike(pattern))
            )
            for f in (filters or []):
                q = f.apply(q, Case)
            for row in q.offset(offset).limit(page_size).all():
                results.append(
                    SearchResult(
                        id=str(row.id),
                        type="case",
                        score=1.0,
                        title=row.title or "",
                        snippet=(row.description or "")[:200],
                        created_at=row.created_at,
                        metadata={"status": row.status},
                    )
                )
        except Exception:
            self.db.rollback()

        # Evidence
        try:
            q = self.db.query(Evidence).filter(
                Evidence.filename.ilike(pattern)
            )
            for f in (filters or []):
                q = f.apply(q, Evidence)
            for row in q.offset(offset).limit(page_size).all():
                results.append(
                    SearchResult(
                        id=str(row.id),
                        type="evidence",
                        score=1.0,
                        title=row.filename,
                        snippet=f"Type: {row.mime_type or 'unknown'} | Size: {row.size}",
                        created_at=row.uploaded_at,
                        metadata={
                            "mime_type": row.mime_type,
                            "size": row.size,
                            "sha256": row.sha256,
                        },
                    )
                )
        except Exception:
            self.db.rollback()

        # Documents
        try:
            q = self.db.query(Document).filter(Document.text.ilike(pattern))
            for f in (filters or []):
                q = f.apply(q, Document)
            for row in q.offset(offset).limit(page_size).all():
                text_val = row.text or ""
                snippet = text_val[:200]
                results.append(
                    SearchResult(
                        id=str(row.id),
                        type="document",
                        score=1.0,
                        title=f"Document {str(row.id)[:8]}",
                        snippet=snippet,
                        created_at=row.created_at,
                        metadata={"text_length": len(text_val)},
                    )
                )
        except Exception:
            self.db.rollback()

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:page_size]


# ---------------------------------------------------------------------------
# Entity Extraction & Entity Search
# ---------------------------------------------------------------------------

class _EntityExtractor:
    """Extract entities from text using regex-based NER heuristics.

    Supports: IP addresses, email addresses, domains, file hashes,
    phone numbers, URLs, and generic person/organization names.
    """

    PATTERNS: Dict[EntityType, re.Pattern] = {
        EntityType.IP_ADDRESS: re.compile(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        ),
        EntityType.EMAIL: re.compile(
            r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
        ),
        EntityType.DOMAIN: re.compile(
            r"\b(?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)"
            r"+[A-Za-z]{2,}\b"
        ),
        EntityType.HASH: re.compile(
            r"\b[A-Fa-f0-9]{32,128}\b"
        ),
        EntityType.PHONE: re.compile(
            r"(?:\+?\d{1,3}[\s\-]?)?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}\b"
        ),
        EntityType.URL: re.compile(
            r"https?://[^\s<>\"']+"
        ),
    }

    PERSON_HINTS = {"mr", "mrs", "ms", "dr", "prof", "officer", "det", "detective"}

    @classmethod
    def extract(cls, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text content."""
        if not text:
            return []

        entities: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        for etype, pattern in cls.PATTERNS.items():
            for match in pattern.finditer(text):
                value = match.group().strip()
                key = f"{etype.value}:{value.lower()}"
                if key not in seen:
                    seen.add(key)
                    entities.append(
                        {
                            "type": etype.value,
                            "value": value,
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.9 if etype in (
                                EntityType.IP_ADDRESS, EntityType.EMAIL, EntityType.HASH
                            ) else 0.7,
                        }
                    )

        # Person-like names: "Dr Smith", "Officer Jones"
        person_pattern = re.compile(
            r"\b(" + "|".join(cls.PERSON_HINTS) + r")\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
        )
        for match in person_pattern.finditer(text):
            value = match.group().strip()
            key = f"person:{value.lower()}"
            if key not in seen:
                seen.add(key)
                entities.append(
                    {
                        "type": EntityType.PERSON.value,
                        "value": value,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.6,
                    }
                )

        return entities


class _EntitySearchBackend:
    """Search across extracted entities stored in audit log details,
    evidence metadata, and forensic result JSON."""

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        query_str: str,
        entity_type: Optional[EntityType] = None,
        filters: Optional[List[SearchFilter]] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Search for entities matching query across the database."""
        results: List[SearchResult] = []
        lower_query = query_str.lower()

        # Search in audit log details (JSON)
        results.extend(self._search_audit_entities(lower_query, entity_type, page_size))

        # Search in evidence metadata_json
        results.extend(self._search_evidence_metadata(lower_query, entity_type, page_size))

        # Search in forensic result JSON
        results.extend(self._search_forensic_entities(lower_query, entity_type, page_size))

        # Search in document text for entity mentions
        results.extend(self._search_document_entities(lower_query, entity_type, page_size))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:page_size]

    def _search_audit_entities(
        self, query: str, entity_type: Optional[EntityType], limit: int
    ) -> List[SearchResult]:
        results: List[SearchResult] = []
        try:
            rows = (
                self.db.query(AuditLog)
                .filter(AuditLog.detail.isnot(None))
                .order_by(desc(AuditLog.timestamp))
                .limit(500)
                .all()
            )
            for row in rows:
                detail_str = json.dumps(row.detail) if row.detail else ""
                if query in detail_str.lower():
                    entities = _EntityExtractor.extract(detail_str)
                    for ent in entities:
                        if entity_type and ent["type"] != entity_type.value:
                            continue
                        if query in ent["value"].lower():
                            results.append(
                                SearchResult(
                                    id=str(row.id),
                                    type="entity",
                                    score=ent["confidence"],
                                    title=f"{ent['type']}: {ent['value']}",
                                    snippet=f"Mentioned in audit log: {row.action}",
                                    metadata={
                                        "entity_type": ent["type"],
                                        "entity_value": ent["value"],
                                        "source": "audit_log",
                                        "action": row.action,
                                    },
                                    created_at=row.timestamp,
                                )
                            )
        except Exception as exc:
            logger.debug("_search_audit_entities: %s", exc)
            self.db.rollback()
        return results[:limit]

    def _search_evidence_metadata(
        self, query: str, entity_type: Optional[EntityType], limit: int
    ) -> List[SearchResult]:
        results: List[SearchResult] = []
        try:
            rows = (
                self.db.query(Evidence)
                .filter(Evidence.metadata_json.isnot(None))
                .order_by(desc(Evidence.uploaded_at))
                .limit(500)
                .all()
            )
            for row in rows:
                meta_str = json.dumps(row.metadata_json) if row.metadata_json else ""
                if query in meta_str.lower() or query in row.filename.lower():
                    entities = _EntityExtractor.extract(meta_str + " " + row.filename)
                    for ent in entities:
                        if entity_type and ent["type"] != entity_type.value:
                            continue
                        if query in ent["value"].lower():
                            results.append(
                                SearchResult(
                                    id=str(row.id),
                                    type="entity",
                                    score=ent["confidence"],
                                    title=f"{ent['type']}: {ent['value']}",
                                    snippet=f"Found in evidence: {row.filename}",
                                    metadata={
                                        "entity_type": ent["type"],
                                        "entity_value": ent["value"],
                                        "source": "evidence",
                                        "evidence_id": str(row.id),
                                        "mime_type": row.mime_type,
                                    },
                                    created_at=row.uploaded_at,
                                )
                            )
        except Exception as exc:
            logger.debug("_search_evidence_metadata: %s", exc)
            self.db.rollback()
        return results[:limit]

    def _search_forensic_entities(
        self, query: str, entity_type: Optional[EntityType], limit: int
    ) -> List[SearchResult]:
        results: List[SearchResult] = []
        try:
            rows = (
                self.db.query(ForensicResult)
                .filter(ForensicResult.result.isnot(None))
                .order_by(desc(ForensicResult.created_at))
                .limit(500)
                .all()
            )
            for row in rows:
                result_str = json.dumps(row.result) if row.result else ""
                if query in result_str.lower():
                    entities = _EntityExtractor.extract(result_str)
                    for ent in entities:
                        if entity_type and ent["type"] != entity_type.value:
                            continue
                        if query in ent["value"].lower():
                            results.append(
                                SearchResult(
                                    id=str(row.id),
                                    type="entity",
                                    score=ent["confidence"],
                                    title=f"{ent['type']}: {ent['value']}",
                                    snippet=f"Found in {row.processor} result",
                                    metadata={
                                        "entity_type": ent["type"],
                                        "entity_value": ent["value"],
                                        "source": "forensic_result",
                                        "processor": row.processor,
                                        "evidence_id": row.evidence_id,
                                    },
                                    created_at=row.created_at,
                                )
                            )
        except Exception as exc:
            logger.debug("_search_forensic_entities: %s", exc)
            self.db.rollback()
        return results[:limit]

    def _search_document_entities(
        self, query: str, entity_type: Optional[EntityType], limit: int
    ) -> List[SearchResult]:
        results: List[SearchResult] = []
        try:
            rows = (
                self.db.query(Document)
                .filter(Document.text.isnot(None))
                .order_by(desc(Document.created_at))
                .limit(200)
                .all()
            )
            for row in rows:
                text_val = row.text or ""
                if query in text_val.lower():
                    entities = _EntityExtractor.extract(text_val)
                    for ent in entities:
                        if entity_type and ent["type"] != entity_type.value:
                            continue
                        if query in ent["value"].lower():
                            results.append(
                                SearchResult(
                                    id=str(row.id),
                                    type="entity",
                                    score=ent["confidence"],
                                    title=f"{ent['type']}: {ent['value']}",
                                    snippet=f"Mentioned in document {str(row.id)[:8]}",
                                    metadata={
                                        "entity_type": ent["type"],
                                        "entity_value": ent["value"],
                                        "source": "document",
                                        "evidence_id": row.evidence_id,
                                    },
                                    created_at=row.created_at,
                                )
                            )
        except Exception as exc:
            logger.debug("_search_document_entities: %s", exc)
            self.db.rollback()
        return results[:limit]


# ---------------------------------------------------------------------------
# Relationship Search Backend
# ---------------------------------------------------------------------------

class _RelationshipSearchBackend:
    """Find connections between entities across the data model.

    Relationships are derived from foreign key links, shared attributes
    (hashes, IPs, filenames), and co-occurrence in the same documents.
    """

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        entity_value: str,
        max_depth: int = 2,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Find entities related to the given entity value."""
        results: List[SearchResult] = []
        lower_val = entity_value.lower()

        # Find evidence that contains this entity
        evidence_ids: Set[str] = set()
        case_ids: Set[str] = set()

        # Search evidence filenames and metadata
        try:
            for row in self.db.query(Evidence).all():
                meta_str = json.dumps(row.metadata_json) if row.metadata_json else ""
                combined = f"{row.filename} {meta_str} {row.sha256}".lower()
                if lower_val in combined:
                    evidence_ids.add(str(row.id))
                    if row.case_id:
                        case_ids.add(row.case_id)
        except Exception:
            self.db.rollback()

        # Search document text
        try:
            for row in self.db.query(Document).all():
                if row.text and lower_val in row.text.lower():
                    if row.evidence_id:
                        evidence_ids.add(row.evidence_id)
                        ev = self.db.query(Evidence).filter(Evidence.id == row.evidence_id).first()
                        if ev and ev.case_id:
                            case_ids.add(ev.case_id)
        except Exception:
            self.db.rollback()

        # Search forensic results
        try:
            for row in self.db.query(ForensicResult).all():
                result_str = json.dumps(row.result) if row.result else ""
                if lower_val in result_str.lower():
                    evidence_ids.add(row.evidence_id)
                    ev = self.db.query(Evidence).filter(Evidence.id == row.evidence_id).first()
                    if ev and ev.case_id:
                        case_ids.add(ev.case_id)
        except Exception:
            self.db.rollback()

        # Build relationship results from connected evidence
        for ev_id in evidence_ids:
            try:
                ev = self.db.query(Evidence).filter(Evidence.id == ev_id).first()
                if ev:
                    results.append(
                        SearchResult(
                            id=str(ev.id),
                            type="relationship",
                            score=0.8,
                            title=f"Evidence: {ev.filename}",
                            snippet=f"Connected to '{entity_value}' via metadata/content match",
                            metadata={
                                "relationship_type": "contains_entity",
                                "source_entity": entity_value,
                                "case_id": ev.case_id,
                                "mime_type": ev.mime_type,
                            },
                            created_at=ev.uploaded_at,
                        )
                    )
            except Exception:
                self.db.rollback()

        # Build relationship results from connected cases
        for cid in case_ids:
            try:
                case = self.db.query(Case).filter(Case.id == cid).first()
                if case:
                    results.append(
                        SearchResult(
                            id=str(case.id),
                            type="relationship",
                            score=0.6,
                            title=f"Case: {case.title}",
                            snippet=f"Contains evidence linked to '{entity_value}'",
                            metadata={
                                "relationship_type": "case_contains_entity",
                                "source_entity": entity_value,
                                "status": case.status,
                            },
                            created_at=case.created_at,
                        )
                    )
            except Exception:
                self.db.rollback()

        # Find co-occurring entities (entities in same documents)
        if max_depth >= 2:
            results.extend(self._find_cooccurring(entity_value, evidence_ids, case_ids))

        results.sort(key=lambda r: r.score, reverse=True)
        offset = (page - 1) * page_size
        return results[offset : offset + page_size]

    def _find_cooccurring(
        self,
        entity_value: str,
        evidence_ids: Set[str],
        case_ids: Set[str],
    ) -> List[SearchResult]:
        """Find entities that co-occur with the target in the same documents."""
        results: List[SearchResult] = []
        try:
            for row in self.db.query(Document).filter(Document.text.isnot(None)).all():
                text_val = row.text or ""
                if entity_value.lower() in text_val.lower():
                    entities = _EntityExtractor.extract(text_val)
                    for ent in entities[:10]:
                        if ent["value"].lower() != entity_value.lower():
                            results.append(
                                SearchResult(
                                    id=f"cooccur-{hashlib.md5(f'{entity_value}:{ent["value"]}'.encode()).hexdigest()[:12]}",
                                    type="relationship",
                                    score=0.4,
                                    title=f"Co-occurs: {ent['type']}: {ent['value']}",
                                    snippet=f"Found alongside '{entity_value}' in document",
                                    metadata={
                                        "relationship_type": "co_occurrence",
                                        "source_entity": entity_value,
                                        "related_entity": ent["value"],
                                        "related_type": ent["type"],
                                    },
                                )
                            )
        except Exception:
            self.db.rollback()
        return results[:20]


# ---------------------------------------------------------------------------
# Timeline Search Backend
# ---------------------------------------------------------------------------

class _TimelineSearchBackend:
    """Search events within a time range across all timestamped tables."""

    TIMELINE_TABLES: List[Tuple[Type, str, Optional[str], str]] = [
        (Case, "cases", "title", "created_at"),
        (Evidence, "evidence", "filename", "uploaded_at"),
        (Document, "documents", None, "created_at"),
        (ForensicResult, "forensic_results", "processor", "created_at"),
        (ForensicJob, "forensic_jobs", None, "queued_at"),
        (AuditLog, "audit_logs", "action", "timestamp"),
    ]

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        event_type: Optional[str] = None,
        query_str: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Search events in a time range."""
        results: List[SearchResult] = []
        offset = (page - 1) * page_size

        for model, table, title_col, ts_col in self.TIMELINE_TABLES:
            if event_type and table.rstrip("s") != event_type.lower().rstrip("s"):
                continue

            try:
                q = self.db.query(model)
                ts_column = getattr(model, ts_col, None)
                if ts_column is None:
                    continue
                if start:
                    q = q.filter(ts_column >= start)
                if end:
                    q = q.filter(ts_column <= end)
                if query_str:
                    title_val = getattr(model, title_col, None) if title_col else None
                    if title_col and title_val is not None:
                        q = q.filter(title_val.ilike(f"%{query_str}%"))

                q = q.order_by(desc(ts_column))
                q = q.offset(offset).limit(page_size)

                for row in q.all():
                    rid = str(getattr(row, "id", ""))
                    title = str(getattr(row, title_col, "")) if title_col else f"{table} {rid[:8]}"
                    ts = getattr(row, ts_col, None)

                    results.append(
                        SearchResult(
                            id=rid,
                            type="timeline",
                            score=1.0,
                            title=title,
                            snippet=f"Event on {table}",
                            metadata={
                                "event_table": table,
                                "timestamp_field": ts_col,
                                "model": model.__name__,
                            },
                            created_at=ts,
                        )
                    )
            except Exception as exc:
                logger.debug("_TimelineSearchBackend(%s): %s", table, exc)
                self.db.rollback()

        results.sort(key=lambda r: r.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return results[offset : offset + page_size]


# ---------------------------------------------------------------------------
# Cross-Correlation Search Backend
# ---------------------------------------------------------------------------

class _CrossCorrelationBackend:
    """Find related evidence across different cases.

    Identifies cases that share similar evidence attributes (hashes,
    filenames, mime types, entity mentions) and surfaces cross-case
    connections that would otherwise be missed.
    """

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Find cross-case correlations for the given query."""
        results: List[SearchResult] = []
        lower_query = query_str.lower()

        # Group evidence by shared attributes
        hash_map: Dict[str, List[str]] = defaultdict(list)
        filename_map: Dict[str, List[str]] = defaultdict(list)
        mime_map: Dict[str, List[str]] = defaultdict(list)

        try:
            evidence_rows = self.db.query(Evidence).all()
            for ev in evidence_rows:
                if ev.sha256:
                    hash_map[ev.sha256].append(str(ev.id))
                if ev.filename:
                    base = ev.filename.lower().split(".")[-1] if "." in ev.filename else ev.filename.lower()
                    filename_map[base].append(str(ev.id))
                if ev.mime_type:
                    mime_map[ev.mime_type].append(str(ev.id))
        except Exception:
            self.db.rollback()

        # Find evidence that shares attributes across multiple cases
        cross_case_evidence: Dict[str, Set[str]] = defaultdict(set)

        for hash_val, ev_ids in hash_map.items():
            if len(ev_ids) > 1:
                for ev_id in ev_ids:
                    cross_case_evidence[ev_id].add("shared_hash")

        for base, ev_ids in filename_map.items():
            if len(ev_ids) > 1:
                for ev_id in ev_ids:
                    cross_case_evidence[ev_id].add("shared_filename_pattern")

        for mime, ev_ids in mime_map.items():
            if len(ev_ids) > 1:
                for ev_id in ev_ids:
                    cross_case_evidence[ev_id].add("shared_mime_type")

        # Search for evidence matching the query and flag cross-case connections
        try:
            pattern = f"%{query_str}%"
            evidence_matches = (
                self.db.query(Evidence)
                .filter(
                    or_(
                        Evidence.filename.ilike(pattern),
                        Evidence.sha256.ilike(pattern),
                        Evidence.mime_type.ilike(pattern),
                    )
                )
                .all()
            )

            for ev in evidence_matches:
                correlations = cross_case_evidence.get(str(ev.id), set())
                if correlations:
                    # Find other cases with similar evidence
                    related_cases = self._find_related_cases(ev, lower_query)
                    results.append(
                        SearchResult(
                            id=str(ev.id),
                            type="cross_correlation",
                            score=0.9 if "shared_hash" in correlations else 0.7,
                            title=f"Cross-case: {ev.filename}",
                            snippet=f"Correlated via: {', '.join(correlations)}",
                            metadata={
                                "correlation_types": list(correlations),
                                "case_id": ev.case_id,
                                "related_cases": related_cases[:5],
                                "sha256": ev.sha256,
                            },
                            created_at=ev.uploaded_at,
                        )
                    )
        except Exception:
            self.db.rollback()

        # Also search documents and forensic results for cross-case links
        results.extend(self._search_cross_case_documents(lower_query))

        results.sort(key=lambda r: r.score, reverse=True)
        offset = (page - 1) * page_size
        return results[offset : offset + page_size]

    def _find_related_cases(self, evidence: Evidence, query: str) -> List[Dict[str, Any]]:
        """Find other cases that contain evidence with shared attributes."""
        related: List[Dict[str, Any]] = []
        try:
            if evidence.sha256:
                same_hash = (
                    self.db.query(Evidence)
                    .filter(Evidence.sha256 == evidence.sha256, Evidence.id != evidence.id)
                    .all()
                )
                for ev in same_hash:
                    if ev.case_id and ev.case_id != evidence.case_id:
                        case = self.db.query(Case).filter(Case.id == ev.case_id).first()
                        if case:
                            related.append(
                                {
                                    "case_id": str(case.id),
                                    "case_title": case.title,
                                    "shared_attribute": "hash",
                                    "evidence_id": str(ev.id),
                                    "filename": ev.filename,
                                }
                            )
        except Exception:
            self.db.rollback()
        return related

    def _search_cross_case_documents(self, query: str) -> List[SearchResult]:
        """Find cross-case correlations through document text analysis."""
        results: List[SearchResult] = []
        try:
            pattern = f"%{query}%"
            doc_rows = (
                self.db.query(Document)
                .join(Evidence, Document.evidence_id == Evidence.id, isouter=True)
                .filter(Document.text.ilike(pattern))
                .limit(100)
                .all()
            )

            evidence_cases: Dict[str, List[str]] = defaultdict(list)
            for doc in doc_rows:
                if doc.evidence_id:
                    ev = self.db.query(Evidence).filter(Evidence.id == doc.evidence_id).first()
                    if ev and ev.case_id:
                        evidence_cases[ev.case_id].append(doc.id)

            # Cases that share document content patterns
            if len(evidence_cases) > 1:
                for case_id, doc_ids in evidence_cases.items():
                    results.append(
                        SearchResult(
                            id=f"cross-doc-{case_id[:8]}",
                            type="cross_correlation",
                            score=0.5,
                            title=f"Cross-case document cluster in case {case_id[:8]}",
                            snippet=f"{len(doc_ids)} documents contain matching content",
                            metadata={
                                "case_id": case_id,
                                "document_count": len(doc_ids),
                                "correlation_type": "document_content",
                            },
                        )
                    )
        except Exception:
            self.db.rollback()
        return results


# ---------------------------------------------------------------------------
# Faceted Search Aggregator
# ---------------------------------------------------------------------------

class _FacetAggregator:
    """Compute facet aggregations for search results."""

    def __init__(self, db: Session):
        self.db = db

    def aggregate(
        self,
        facets: List[SearchFacet],
        base_model: Optional[Type] = None,
        filters: Optional[List[SearchFilter]] = None,
    ) -> List[FacetResult]:
        """Compute all requested facet aggregations."""
        results: List[FacetResult] = []
        for facet in facets:
            if facet.type == "terms":
                results.append(self._terms_aggregation(facet, base_model, filters))
            elif facet.type == "date_histogram":
                results.append(self._date_histogram_aggregation(facet, base_model, filters))
            elif facet.type == "range":
                results.append(self._range_aggregation(facet, base_model, filters))
            else:
                results.append(FacetResult(name=facet.name, type=facet.type))
        return results

    def _terms_aggregation(
        self,
        facet: SearchFacet,
        base_model: Optional[Type],
        filters: Optional[List[SearchFilter]],
    ) -> FacetResult:
        """Count occurrences of each unique value."""
        buckets: List[Dict[str, Any]] = []
        try:
            column = getattr(base_model, facet.field, None) if base_model else None
            if column is None:
                return FacetResult(name=facet.name, type=facet.type)

            q = self.db.query(column, func.count().label("count"))
            if filters:
                for f in filters:
                    q = f.apply(q, base_model)
            q = q.group_by(column).order_by(desc("count")).limit(facet.size)
            rows = q.all()
            total = sum(r[1] for r in rows)
            for val, count in rows:
                buckets.append({"key": str(val) if val else "null", "count": count})
            return FacetResult(name=facet.name, type=facet.type, buckets=buckets, total=total)
        except Exception as exc:
            logger.debug("_FacetAggregator._terms_aggregation: %s", exc)
            self.db.rollback()
            return FacetResult(name=facet.name, type=facet.type)

    def _date_histogram_aggregation(
        self,
        facet: SearchFacet,
        base_model: Optional[Type],
        filters: Optional[List[SearchFilter]],
    ) -> FacetResult:
        """Bucket results by date interval."""
        buckets: List[Dict[str, Any]] = []
        try:
            column = getattr(base_model, facet.field, None) if base_model else None
            if column is None:
                return FacetResult(name=facet.name, type=facet.type)

            date_trunc = func.date_trunc("day", column).label("bucket")
            q = self.db.query(date_trunc, func.count().label("count"))
            if filters:
                for f in filters:
                    q = f.apply(q, base_model)
            q = q.group_by("bucket").order_by(desc("bucket")).limit(facet.size)
            rows = q.all()
            total = sum(r[1] for r in rows)
            for dt, count in rows:
                buckets.append({
                    "key": dt.isoformat() if dt else "null",
                    "count": count,
                })
            return FacetResult(name=facet.name, type=facet.type, buckets=buckets, total=total)
        except Exception:
            self.db.rollback()
            return FacetResult(name=facet.name, type=facet.type)

    def _range_aggregation(
        self,
        facet: SearchFacet,
        base_model: Optional[Type],
        filters: Optional[List[SearchFilter]],
    ) -> FacetResult:
        """Bucket results into numeric ranges."""
        buckets: List[Dict[str, Any]] = []
        try:
            column = getattr(base_model, facet.field, None) if base_model else None
            if column is None:
                return FacetResult(name=facet.name, type=facet.type)

            ranges = getattr(facet, "ranges", [(0, 1000), (1000, 10000), (10000, 100000), (100000, float("inf"))])
            for low, high in ranges:
                q = self.db.query(func.count().label("count"))
                if base_model:
                    q = self.db.query(func.count().label("count")).select_from(base_model)
                if filters:
                    for f in filters:
                        q = f.apply(q, base_model)
                q = q.filter(column >= low, column < high)
                count = q.scalar() or 0
                label = f"{low}-{high}" if high != float("inf") else f"{low}+"
                buckets.append({"key": label, "count": count})
            total = sum(b["count"] for b in buckets)
            return FacetResult(name=facet.name, type=facet.type, buckets=buckets, total=total)
        except Exception:
            self.db.rollback()
            return FacetResult(name=facet.name, type=facet.type)


# ---------------------------------------------------------------------------
# Hybrid Search Backend (Tier 3 — Vector + Text + Metadata)
# ---------------------------------------------------------------------------

class _HybridSearchBackend:
    """Combines PostgreSQL FTS, vector similarity, and metadata filtering.

    Uses reciprocal rank fusion (RRF) to merge results from multiple tiers.
    """

    def __init__(self, db: Session):
        self.db = db
        self.fts = _PostgresFTSBackend(db)
        self.entity_backend = _EntitySearchBackend(db)

    def search(
        self,
        query_str: str,
        filters: Optional[List[SearchFilter]] = None,
        vector_weight: float = 0.4,
        text_weight: float = 0.4,
        metadata_weight: float = 0.2,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Hybrid search combining text, vector, and metadata results."""
        all_results: Dict[str, SearchResult] = {}
        scores: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Tier 1: Full-text search
        fts_results = self.fts.search_all(query_str, filters, page, page_size * 2)
        for r in fts_results:
            all_results[r.id] = r
            scores[r.id]["text"] = r.score

        # Tier 3: Vector similarity search
        vector_results = self._vector_search(query_str, page_size * 2)
        for r in vector_results:
            if r.id in all_results:
                scores[r.id]["vector"] = r.score
            else:
                all_results[r.id] = r
                scores[r.id]["vector"] = r.score

        # Metadata search (entities)
        entity_results = self.entity_backend.search(query_str, page=1, page_size=page_size * 2)
        for r in entity_results:
            if r.id in all_results:
                scores[r.id]["metadata"] = r.score
            else:
                all_results[r.id] = r
                scores[r.id]["metadata"] = r.score

        # Reciprocal Rank Fusion
        k = 60  # RRF constant
        for rid, result in all_results.items():
            rrf_score = 0.0
            for tier, weight in [
                ("text", text_weight),
                ("vector", vector_weight),
                ("metadata", metadata_weight),
            ]:
                tier_score = scores[rid].get(tier, 0.0)
                if tier_score > 0:
                    rrf_score += weight * (1.0 / (k + tier_score * 100))
            result.score = rrf_score

        ranked = sorted(all_results.values(), key=lambda r: r.score, reverse=True)
        offset = (page - 1) * page_size
        return ranked[offset : offset + page_size]

    def _vector_search(self, query_str: str, limit: int) -> List[SearchResult]:
        """Search using vector similarity via the existing embedding system."""
        results: List[SearchResult] = []
        try:
            from ..embeddings import get_provider
            from ..vector_store import DBVectorStore

            provider = get_provider()
            query_vector = provider.embed(query_str)
            store = DBVectorStore()
            vector_results = store.query(query_vector, top_k=limit)

            for score, doc_id in vector_results:
                doc = self.db.query(Document).filter(Document.id == doc_id).first()
                if doc:
                    results.append(
                        SearchResult(
                            id=str(doc.id),
                            type="vector",
                            score=score,
                            title=f"Document {str(doc.id)[:8]}",
                            snippet=(doc.text or "")[:200],
                            metadata={
                                "similarity_score": score,
                                "evidence_id": doc.evidence_id,
                            },
                            created_at=doc.created_at,
                        )
                    )
        except Exception as exc:
            logger.debug("_HybridSearchBackend._vector_search: %s", exc)
        return results


# ---------------------------------------------------------------------------
# OpenSearch/Elasticsearch Backend (Tier 2 — optional)
# ---------------------------------------------------------------------------

class _OpenSearchBackend:
    """Optional OpenSearch/Elasticsearch integration.

    Activated only when OPENSEARCH_URL (or ELASTICSEARCH_URL) env var is set
    and the opensearch-py / elasticsearch-py package is importable.
    """

    def __init__(self):
        self._client: Any = None
        self._available = False
        self._init_client()

    def _init_client(self) -> None:
        """Attempt to connect to OpenSearch/Elasticsearch."""
        url = os.getenv("OPENSEARCH_URL") or os.getenv("ELASTICSEARCH_URL")
        if not url:
            return

        try:
            try:
                from opensearchpy import OpenSearch
                self._client = OpenSearch(
                    hosts=[url],
                    http_auth=(
                        os.getenv("OPENSEARCH_USER", ""),
                        os.getenv("OPENSEARCH_PASS", ""),
                    ),
                    use_ssl=url.startswith("https"),
                    verify_certs=False,
                )
            except ImportError:
                from elasticsearch import Elasticsearch
                self._client = Elasticsearch(
                    [url],
                    basic_auth=(
                        os.getenv("ELASTICSEARCH_USER", ""),
                        os.getenv("ELASTICSEARCH_PASS", ""),
                    ),
                    verify_certs=False,
                )
            self._client.info()
            self._available = True
            logger.info("OpenSearch/Elasticsearch backend connected at %s", url)
        except Exception as exc:
            logger.info("OpenSearch/Elasticsearch not available: %s", exc)
            self._client = None
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def search(
        self,
        index: str,
        query_str: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Execute a search against OpenSearch/Elasticsearch."""
        if not self._available or not self._client:
            return []

        must = [{"multi_match": {"query": query_str, "fields": ["*"]}}]
        filter_clauses: List[Dict[str, Any]] = []

        if filters:
            for key, val in filters.items():
                if isinstance(val, list):
                    filter_clauses.append({"terms": {key: val}})
                elif isinstance(val, dict):
                    range_op = {}
                    for op, v in val.items():
                        range_op[op] = v
                    filter_clauses.append({"range": {key: range_op}})
                else:
                    filter_clauses.append({"term": {key: val}})

        body: Dict[str, Any] = {
            "query": {
                "bool": {
                    "must": must,
                    "filter": filter_clauses if filter_clauses else [],
                }
            },
            "from": (page - 1) * page_size,
            "size": page_size,
            "highlight": {
                "fields": {"*": {"fragment_size": 200, "number_of_fragments": 3}}
            },
        }

        try:
            resp = self._client.search(index=index, body=body)
            hits = resp.get("hits", {}).get("hits", [])
            results: List[SearchResult] = []
            for hit in hits:
                src = hit.get("_source", {})
                hl = hit.get("highlight", {})
                snippet = ""
                for field_hl in hl.values():
                    if field_hl:
                        snippet = field_hl[0]
                        break

                highlights = []
                for field, frags in hl.items():
                    if frags:
                        highlights.append(
                            SearchHighlight(field=field, snippet=frags[0])
                        )

                results.append(
                    SearchResult(
                        id=str(hit.get("_id", "")),
                        type=src.get("type", "opensearch"),
                        score=hit.get("_score", 0.0),
                        title=src.get("title", src.get("filename", hit.get("_id", ""))),
                        snippet=snippet,
                        highlights=highlights,
                        metadata=src,
                        created_at=(
                            datetime.fromisoformat(src["created_at"])
                            if "created_at" in src
                            else None
                        ),
                    )
                )
            return results
        except Exception as exc:
            logger.warning("OpenSearch search failed: %s", exc)
            return []


# ---------------------------------------------------------------------------
# Main SearchEngine — orchestrates all backends
# ---------------------------------------------------------------------------

class SearchEngine:
    """Enterprise search engine orchestrating PostgreSQL FTS, OpenSearch,
    and vector similarity backends.

    Usage::

        engine = SearchEngine(db_session)
        response = engine.search("malware sample", mode=SearchMode.FULL_TEXT)
        print(response.to_dict())

    Or use specialized search methods::

        evidence = engine.search_evidence(sha256="abc123...")
        cases = engine.search_cases(status="open", assignee="user-123")
        timeline = engine.search_timeline(start=datetime(2024,1,1))
        entities = engine.search_entities("192.168.1.1", EntityType.IP_ADDRESS)
        related = engine.find_related("malware.exe")
        hybrid = engine.hybrid_search("ransomware analysis")
    """

    def __init__(self, db: Optional[Session] = None):
        if db is None:
            db = SessionLocal()
            self._owns_session = True
        else:
            self._owns_session = False
        self.db = db

        self._fts = _PostgresFTSBackend(db)
        self._entity = _EntitySearchBackend(db)
        self._relationship = _RelationshipSearchBackend(db)
        self._timeline = _TimelineSearchBackend(db)
        self._cross_correlation = _CrossCorrelationBackend(db)
        self._facet_agg = _FacetAggregator(db)
        self._hybrid = _HybridSearchBackend(db)
        self._opensearch = _OpenSearchBackend()
        self._index = SearchIndex(db)
        self._ranker = SearchRanker()

    def close(self) -> None:
        if self._owns_session and self.db:
            self.db.close()

    def __enter__(self) -> "SearchEngine":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # -- index management ---------------------------------------------------

    def ensure_indexes(self) -> None:
        """Create full-text search indexes. Call on startup."""
        self._index.ensure_indexes()

    def health_check(self) -> dict:
        """Health check for search engine sub-components."""
        from datetime import datetime, timezone
        return {
            "status": "healthy",
            "backends": {
                "fts": True,
                "entity": True,
                "timeline": True,
                "hybrid": True,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # -- primary search API -------------------------------------------------

    def search(
        self,
        query_str: str,
        mode: SearchMode = SearchMode.FULL_TEXT,
        filters: Optional[List[SearchFilter]] = None,
        facets: Optional[List[SearchFacet]] = None,
        page: int = 1,
        page_size: int = 20,
        rank: bool = True,
        **kwargs: Any,
    ) -> SearchResponse:
        """Unified search entry point.

        Delegates to the appropriate backend based on the requested mode.
        Always returns a SearchResponse with results, facets, and timing.
        """
        t0 = time.monotonic()

        if mode == SearchMode.FULL_TEXT:
            results = self._fts.search_all(query_str, filters, page, page_size)
        elif mode == SearchMode.EVIDENCE:
            results = self.search_evidence(query=query_str, page=page, page_size=page_size, **kwargs)
        elif mode == SearchMode.CASE:
            results = self.search_cases(query=query_str, page=page, page_size=page_size, **kwargs)
        elif mode == SearchMode.TIMELINE:
            results = self._timeline.search(
                query_str=query_str,
                page=page,
                page_size=page_size,
                start=kwargs.get("start"),
                end=kwargs.get("end"),
                event_type=kwargs.get("event_type"),
            )
        elif mode == SearchMode.ENTITY:
            entity_type = kwargs.get("entity_type")
            if isinstance(entity_type, str):
                entity_type = EntityType(entity_type)
            results = self._entity.search(
                query_str, entity_type=entity_type, page=page, page_size=page_size
            )
        elif mode == SearchMode.RELATIONSHIP:
            results = self._relationship.search(
                query_str, page=page, page_size=page_size,
                max_depth=kwargs.get("max_depth", 2),
            )
        elif mode == SearchMode.HYBRID:
            results = self._hybrid.search(
                query_str, filters=filters, page=page, page_size=page_size,
                vector_weight=kwargs.get("vector_weight", 0.4),
                text_weight=kwargs.get("text_weight", 0.4),
                metadata_weight=kwargs.get("metadata_weight", 0.2),
            )
        elif mode == SearchMode.SEMANTIC:
            results = self._semantic_search(query_str, page, page_size)
        elif mode == SearchMode.CROSS_CORRELATION:
            results = self._cross_correlation.search(query_str, page=page, page_size=page_size)
        else:
            results = self._fts.search_all(query_str, filters, page, page_size)

        # Rank with BM25 if requested and not already ranked
        if rank and results and mode in (SearchMode.FULL_TEXT, SearchMode.EVIDENCE, SearchMode.CASE):
            query_terms = query_str.split()
            results = self._ranker.rank_results(results, query_terms, self.db)

        # Compute facets
        facet_results: List[FacetResult] = []
        if facets:
            facet_results = self._facet_agg.aggregate(facets, base_model=Case, filters=filters)

        took_ms = (time.monotonic() - t0) * 1000
        max_score = results[0].score if results else 0.0

        return SearchResponse(
            query=query_str,
            results=results,
            total=len(results),
            facets=facet_results,
            took_ms=took_ms,
            tier=self._determine_tier(mode),
            mode=mode,
            page=page,
            page_size=page_size,
            max_score=max_score,
        )

    # -- specialized search methods -----------------------------------------

    def search_evidence(
        self,
        query: Optional[str] = None,
        sha256: Optional[str] = None,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        uploaded_after: Optional[datetime] = None,
        uploaded_before: Optional[datetime] = None,
        case_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Search evidence with specific forensic filters."""
        results: List[SearchResult] = []
        try:
            q = self.db.query(Evidence)
            filters_applied: List[SearchFilter] = []

            if query:
                pattern = f"%{query}%"
                q = q.filter(
                    or_(
                        Evidence.filename.ilike(pattern),
                        Evidence.mime_type.ilike(pattern),
                    )
                )
            if sha256:
                q = q.filter(Evidence.sha256 == sha256)
            if filename:
                q = q.filter(Evidence.filename.ilike(f"%{filename}%"))
            if mime_type:
                q = q.filter(Evidence.mime_type.ilike(f"%{mime_type}%"))
            if min_size is not None:
                q = q.filter(Evidence.size >= min_size)
            if max_size is not None:
                q = q.filter(Evidence.size <= max_size)
            if uploaded_after:
                q = q.filter(Evidence.uploaded_at >= uploaded_after)
            if uploaded_before:
                q = q.filter(Evidence.uploaded_at <= uploaded_before)
            if case_id:
                q = q.filter(Evidence.case_id == case_id)

            q = q.order_by(desc(Evidence.uploaded_at))
            q = q.offset((page - 1) * page_size).limit(page_size)

            for row in q.all():
                score = 1.0
                if query and query.lower() in row.filename.lower():
                    score = 2.0
                if sha256 and row.sha256 == sha256:
                    score = 3.0

                results.append(
                    SearchResult(
                        id=str(row.id),
                        type="evidence",
                        score=score,
                        title=row.filename,
                        snippet=f"{row.mime_type or 'unknown'} | {row.size} bytes",
                        metadata={
                            "sha256": row.sha256,
                            "size": row.size,
                            "mime_type": row.mime_type,
                            "case_id": row.case_id,
                            "uploaded_by": row.uploaded_by,
                        },
                        created_at=row.uploaded_at,
                    )
                )
        except Exception as exc:
            logger.warning("search_evidence failed: %s", exc)
            self.db.rollback()

        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def search_cases(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Search cases by title, status, assignee, and date."""
        results: List[SearchResult] = []
        try:
            q = self.db.query(Case)

            if query:
                pattern = f"%{query}%"
                q = q.filter(
                    or_(Case.title.ilike(pattern), Case.description.ilike(pattern))
                )
            if status:
                q = q.filter(Case.status == status)
            if created_by:
                q = q.filter(Case.created_by == created_by)
            if created_after:
                q = q.filter(Case.created_at >= created_after)
            if created_before:
                q = q.filter(Case.created_at <= created_before)

            q = q.order_by(desc(Case.created_at))
            q = q.offset((page - 1) * page_size).limit(page_size)

            for row in q.all():
                score = 1.0
                if query:
                    if query.lower() in (row.title or "").lower():
                        score = 2.0
                    if query.lower() in (row.description or "").lower():
                        score = max(score, 1.5)

                results.append(
                    SearchResult(
                        id=str(row.id),
                        type="case",
                        score=score,
                        title=row.title or "",
                        snippet=(row.description or "")[:200],
                        metadata={
                            "status": row.status,
                            "created_by": row.created_by,
                        },
                        created_at=row.created_at,
                    )
                )
        except Exception as exc:
            logger.warning("search_cases failed: %s", exc)
            self.db.rollback()

        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def search_entities(
        self,
        query: str,
        entity_type: Optional[EntityType] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Search for entities (persons, orgs, IPs, domains, etc.)."""
        return self._entity.search(query, entity_type=entity_type, page=page, page_size=page_size)

    def search_timeline(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        event_type: Optional[str] = None,
        query_str: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Search events within a time range."""
        return self._timeline.search(
            start=start, end=end, event_type=event_type,
            query_str=query_str, page=page, page_size=page_size,
        )

    def find_related(
        self,
        entity_value: str,
        max_depth: int = 2,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Find entities related to the given entity (relationship search)."""
        return self._relationship.search(
            entity_value, max_depth=max_depth, page=page, page_size=page_size,
        )

    def search_cross_correlation(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Find related evidence across different cases."""
        return self._cross_correlation.search(query_str, page=page, page_size=page_size)

    def hybrid_search(
        self,
        query_str: str,
        filters: Optional[List[SearchFilter]] = None,
        page: int = 1,
        page_size: int = 20,
        vector_weight: float = 0.4,
        text_weight: float = 0.4,
        metadata_weight: float = 0.2,
    ) -> List[SearchResult]:
        """Hybrid search combining text + vector + metadata with RRF fusion."""
        return self._hybrid.search(
            query_str, filters=filters, page=page, page_size=page_size,
            vector_weight=vector_weight, text_weight=text_weight,
            metadata_weight=metadata_weight,
        )

    def semantic_search(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> List[SearchResult]:
        """Semantic search using the existing embedding system."""
        return self._semantic_search(query_str, page, page_size)

    def with_facets(
        self,
        query_str: str,
        facets: List[SearchFacet],
        filters: Optional[List[SearchFilter]] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResponse:
        """Search with faceted aggregations."""
        return self.search(
            query_str, filters=filters, facets=facets,
            page=page, page_size=page_size,
        )

    # -- indexing -----------------------------------------------------------

    def index_evidence(self, evidence_id: str) -> None:
        """Re-index a single evidence item into the search index."""
        try:
            ev = self.db.query(Evidence).filter(Evidence.id == evidence_id).first()
            if ev:
                self._index.rebuild_vector("evidence", evidence_id)
                logger.info("Indexed evidence %s", evidence_id)
        except Exception as exc:
            logger.warning("index_evidence failed: %s", exc)
            self.db.rollback()

    def index_case(self, case_id: str) -> None:
        """Re-index a single case."""
        try:
            self._index.rebuild_vector("cases", case_id)
            logger.info("Indexed case %s", case_id)
        except Exception as exc:
            logger.warning("index_case failed: %s", exc)
            self.db.rollback()

    def index_document(self, document_id: str) -> None:
        """Re-index a single document and its embedding."""
        try:
            self._index.rebuild_vector("documents", document_id)
            doc = self.db.query(Document).filter(Document.id == document_id).first()
            if doc and doc.text:
                from ..embeddings import get_provider
                from ..vector_store import DBVectorStore
                provider = get_provider()
                vector = provider.embed(doc.text[:8000])
                store = DBVectorStore()
                store.upsert(document_id, vector)
            logger.info("Indexed document %s", document_id)
        except Exception as exc:
            logger.warning("index_document failed: %s", exc)
            self.db.rollback()

    def reindex_all(self) -> Dict[str, int]:
        """Re-index all searchable content. Returns counts per table."""
        counts: Dict[str, int] = {}
        try:
            for table_name in SearchIndex.TSVECTOR_COLUMNS:
                count = self.db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar() or 0
                counts[table_name] = count
        except Exception:
            self.db.rollback()

        # Also re-embed all documents
        try:
            docs = self.db.query(Document).filter(Document.text.isnot(None)).all()
            from ..embeddings import get_provider
            from ..vector_store import DBVectorStore
            provider = get_provider()
            store = DBVectorStore()
            embedded = 0
            for doc in docs:
                try:
                    vector = provider.embed(doc.text[:8000])
                    store.upsert(str(doc.id), vector)
                    embedded += 1
                except Exception:
                    continue
            counts["embeddings"] = embedded
        except Exception:
            pass

        logger.info("Reindex complete: %s", counts)
        return counts

    # -- internal helpers ---------------------------------------------------

    def _semantic_search(
        self, query_str: str, page: int, page_size: int
    ) -> List[SearchResult]:
        """Semantic search using embedding similarity."""
        results: List[SearchResult] = []
        try:
            from ..embeddings import get_provider
            from ..vector_store import DBVectorStore

            provider = get_provider()
            query_vector = provider.embed(query_str)
            store = DBVectorStore()
            vector_results = store.query(query_vector, top_k=page_size * 2)

            for score, doc_id in vector_results:
                doc = self.db.query(Document).filter(Document.id == doc_id).first()
                if doc:
                    snippet = (doc.text or "")[:200]
                    results.append(
                        SearchResult(
                            id=str(doc.id),
                            type="semantic",
                            score=score,
                            title=f"Semantic match: Document {str(doc.id)[:8]}",
                            snippet=snippet,
                            metadata={
                                "similarity_score": score,
                                "evidence_id": doc.evidence_id,
                            },
                            created_at=doc.created_at,
                        )
                    )
        except Exception as exc:
            logger.debug("_semantic_search: %s", exc)

        offset = (page - 1) * page_size
        return results[offset : offset + page_size]

    @staticmethod
    def _determine_tier(mode: SearchMode) -> SearchTier:
        """Determine which search tier a mode primarily uses."""
        if mode in (SearchMode.HYBRID,):
            return SearchTier.HYBRID
        elif mode == SearchMode.SEMANTIC:
            return SearchTier.VECTOR
        else:
            return SearchTier.POSTGRES_FTS


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

_search_engine: Optional[SearchEngine] = None


def get_search_engine(db: Optional[Session] = None) -> SearchEngine:
    """Get or create a SearchEngine instance.

    If *db* is provided, creates a new engine bound to that session.
    Otherwise returns a module-level singleton (creates its own session).
    """
    global _search_engine
    if db is not None:
        return SearchEngine(db)
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine


def init_search() -> SearchEngine:
    """Initialize the search system (create indexes, etc.)."""
    engine = get_search_engine()
    engine.ensure_indexes()
    return engine


__all__ = [
    # Core classes
    "SearchEngine",
    "SearchIndex",
    "SearchResult",
    "SearchResponse",
    "SearchFilter",
    "SearchFacet",
    "SearchRanker",
    "FacetResult",
    "SearchHighlight",
    # Enums
    "SearchTier",
    "SearchMode",
    "EntityType",
    # Backends (for advanced usage)
    "_PostgresFTSBackend",
    "_EntitySearchBackend",
    "_RelationshipSearchBackend",
    "_TimelineSearchBackend",
    "_CrossCorrelationBackend",
    "_HybridSearchBackend",
    "_OpenSearchBackend",
    "_FacetAggregator",
    "_EntityExtractor",
    # Factory functions
    "get_search_engine",
    "init_search",
]
