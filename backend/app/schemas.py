from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CaseStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"
    PENDING = "pending"


class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[CaseStatus] = CaseStatus.ACTIVE
    priority: Optional[str] = "medium"


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CaseStatus] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None


class CaseOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: Optional[CaseStatus]
    priority: Optional[str]
    assigned_to: Optional[str]
    created_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        orm_mode = True


class CaseListResponse(BaseModel):
    items: list[CaseOut]
    total: int
    limit: int
    offset: int
    page: int

    class Config:
        from_attributes = True
        orm_mode = True


# ── Upload schemas ──────────────────────────────────────────────

class UploadStartRequest(BaseModel):
    filename: str
    file_size: int
    chunk_size: int = 104857600
    case_id: Optional[str] = None
    mime_type: Optional[str] = None
    sha256: Optional[str] = None


class UploadStartResponse(BaseModel):
    upload_id: str
    session_id: str
    chunk_size: int
    total_chunks: int
    bucket: str
    object_key: str
    status: str

    class Config:
        from_attributes = True
        orm_mode = True


class UploadChunkResponse(BaseModel):
    session_id: str
    chunk_number: int
    etag: str
    status: str
    completed_chunks: int
    total_chunks: int

    class Config:
        from_attributes = True
        orm_mode = True


class UploadCompleteRequest(BaseModel):
    parts: List[dict]


class UploadCompleteResponse(BaseModel):
    session_id: str
    evidence_id: str
    sha256: str
    md5: Optional[str]
    size: int
    status: str

    class Config:
        from_attributes = True
        orm_mode = True


class UploadSessionOut(BaseModel):
    id: str
    filename: str
    file_size: int
    chunk_size: int
    total_chunks: int
    completed_chunks: int
    status: str
    upload_id: Optional[str]
    bucket: str
    object_key: str
    sha256: Optional[str]
    md5: Optional[str]
    mime_type: Optional[str]
    evidence_id: Optional[str]
    error_message: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    parts: Optional[List[dict]] = None

    class Config:
        from_attributes = True
        orm_mode = True

