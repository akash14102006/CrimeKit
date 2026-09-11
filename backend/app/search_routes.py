"""Search API routes for the enterprise search platform."""

import asyncio
from typing import Any, Dict, List, Optional

import dataclasses
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import database
from .auth import get_current_user
from .search import get_search_engine, SearchEngine, SearchMode, SearchTier


router = APIRouter(prefix="/api/v1/search", tags=["search"])


# --- Request Bodies ---


class GeneralSearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class EvidenceSearchRequest(BaseModel):
    sha256: Optional[str] = None
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    content_type: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class CaseSearchRequest(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TimelineSearchRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    event_type: Optional[str] = None
    entity_ids: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class EntitySearchRequest(BaseModel):
    query: str
    entity_type: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class RelationshipSearchRequest(BaseModel):
    entity_id: str
    max_depth: int = Field(default=2, ge=1, le=5)
    relationship_types: Optional[List[str]] = None


class HybridSearchRequest(BaseModel):
    query: str
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SemanticSearchRequest(BaseModel):
    query: str
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class CrossCorrelationRequest(BaseModel):
    query: str
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# --- Helper ---


async def _run_search(func, *args, **kwargs):
    """Execute a sync search function in a thread executor."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


def _serialize_results(results: Any) -> Any:
    """Convert search result objects to JSON-serializable dicts."""
    if hasattr(results, "to_dict"):
        return {"results": [results.to_dict()], "total": 1}
    if dataclasses.is_dataclass(results) and not isinstance(results, type):
        return {"results": [dataclasses.asdict(results)], "total": 1}
    if isinstance(results, list):
        items = [
            r.to_dict() if hasattr(r, "to_dict")
            else dataclasses.asdict(r) if dataclasses.is_dataclass(r) and not isinstance(r, type)
            else r
            for r in results
        ]
        return {"results": items, "total": len(items)}
    if isinstance(results, dict):
        return results
    return {"results": results, "total": 0}


# --- Routes ---


@router.get("")
@router.get("/")
async def general_search_get(
    q: str = Query(..., min_length=1),
    mode: str = Query("hybrid"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    try:
        smode = SearchMode(mode)
    except ValueError:
        smode = SearchMode.HYBRID

    results = await _run_search(
        engine.search,
        q,
        mode=smode,
        page=page,
        page_size=page_size,
    )
    if hasattr(results, "to_dict"):
        content = results.to_dict()
    elif dataclasses.is_dataclass(results):
        content = dataclasses.asdict(results)
    else:
        content = results
    return JSONResponse(content=content)


@router.post("")
@router.post("/")
async def general_search(
    body: GeneralSearchRequest,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    try:
        mode = SearchMode(body.mode)
    except ValueError:
        mode = SearchMode.HYBRID

    results = await _run_search(
        engine.search,
        query_str=body.query,
        mode=mode,
        filters=body.filters,
        page=body.page,
        page_size=body.page_size,
    )
    return JSONResponse(content=_serialize_results(results))


@router.post("/evidence", response_model=None)
async def search_evidence(
    body: EvidenceSearchRequest,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    results = await _run_search(
        engine.search_evidence,
        sha256=body.sha256,
        filename=body.filename,
        mime_type=body.mime_type,
        page=body.page,
        page_size=body.page_size,
    )
    return JSONResponse(content=_serialize_results(results))


@router.post("/cases", response_model=None)
async def search_cases(
    body: CaseSearchRequest,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    results = await _run_search(
        engine.search_cases,
        query=body.title,
        status=body.status,
        created_by=body.created_by,
        page=body.page,
        page_size=body.page_size,
    )
    return JSONResponse(content=_serialize_results(results))


@router.post("/timeline", response_model=None)
async def search_timeline(
    body: TimelineSearchRequest,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    results = await _run_search(
        engine.search_timeline,
        event_type=body.event_type,
        page=body.page,
        page_size=body.page_size,
    )
    return JSONResponse(content=_serialize_results(results))


@router.post("/entities", response_model=None)
async def search_entities(
    body: EntitySearchRequest,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    results = await _run_search(
        engine.search_entities,
        query=body.query,
        entity_type=body.entity_type,
        page=body.page,
        page_size=body.page_size,
    )
    return JSONResponse(content=_serialize_results(results))


@router.post("/relationships", response_model=None)
async def find_relationships(
    body: RelationshipSearchRequest,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    results = await _run_search(
        engine.find_related,
        entity_value=body.entity_id,
        max_depth=body.max_depth,
        page=1,
        page_size=20,
    )
    return JSONResponse(content=_serialize_results(results))


@router.post("/hybrid", response_model=None)
async def hybrid_search(
    body: HybridSearchRequest,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    results = await _run_search(
        engine.hybrid_search,
        query_str=body.query,
        page=body.page,
        page_size=body.page_size,
    )
    return JSONResponse(content=_serialize_results(results))


@router.post("/semantic", response_model=None)
async def semantic_search(
    body: SemanticSearchRequest,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    results = await _run_search(
        engine.semantic_search,
        query_str=body.query,
        page=body.page,
        page_size=body.page_size,
    )
    return JSONResponse(content=_serialize_results(results))


@router.post("/cross-correlation", response_model=None)
async def cross_correlation(
    body: CrossCorrelationRequest,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    results = await _run_search(
        engine.search_cross_correlation,
        query_str=body.query,
        page=body.page,
        page_size=body.page_size,
    )
    return JSONResponse(content=_serialize_results(results))


@router.post("/reindex", response_model=None)
async def reindex(
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    results = await _run_search(
        engine.reindex_all,
    )
    return JSONResponse(content=_serialize_results(results))


@router.get("/facets/{search_type}", response_model=None)
async def get_facets(
    search_type: str,
    db: Session = Depends(database.get_db_session),
    current_user: Any = Depends(get_current_user),
):
    engine = get_search_engine(db)
    from .search import SearchFacet
    results = await _run_search(
        engine.with_facets,
        query_str=search_type,
        facets=[SearchFacet(name=search_type, field=search_type)],
    )
    return JSONResponse(content=_serialize_results(results))


@router.get("/health", response_model=None)
async def search_health(
    db: Session = Depends(database.get_db_session),
):
    engine = get_search_engine(db)
    results = await _run_search(engine.health_check)
    status_code = 200 if results.get("status") == "healthy" else 503
    return JSONResponse(content=results, status_code=status_code)
