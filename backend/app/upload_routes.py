import hashlib
import logging
import mimetypes
import os
import socket
import tempfile
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from . import database, models
from .auth import get_current_user
from .processing import start_worker
from .processors import list_processors
from .schemas import (
    UploadChunkResponse,
    UploadCompleteRequest,
    UploadCompleteResponse,
    UploadSessionOut,
    UploadStartRequest,
    UploadStartResponse,
)
from .storage import EnterpriseObjectStore

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/uploads", tags=["uploads"])

DEFAULT_CHUNK_SIZE = 100 * 1024 * 1024
MIN_CHUNK_SIZE = 5 * 1024 * 1024
MAX_CHUNK_SIZE = 500 * 1024 * 1024
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(500 * 1024 * 1024 * 1024)))  # 500 GB default


def _adaptive_chunk_size(file_size: int) -> int:
    """Select chunk size based on file size for optimal throughput."""
    if file_size <= 100 * 1024 * 1024:  # <= 100MB: 5MB chunks (fast resume)
        return 5 * 1024 * 1024
    if file_size <= 1 * 1024 * 1024 * 1024:  # <= 1GB: 25MB chunks
        return 25 * 1024 * 1024
    if file_size <= 10 * 1024 * 1024 * 1024:  # <= 10GB: 100MB chunks
        return 100 * 1024 * 1024
    if file_size <= 50 * 1024 * 1024 * 1024:  # <= 50GB: 200MB chunks
        return 200 * 1024 * 1024
    return MAX_CHUNK_SIZE  # > 50GB: 500MB chunks

_store: EnterpriseObjectStore | None = None
_minio_available: bool | None = None


def _check_minio_connectivity(timeout_sec: float = 2.0) -> bool:
    """Quick socket-level check if MinIO is reachable. Returns True if reachable."""
    global _minio_available
    endpoint = os.getenv("MINIO_ENDPOINT", "")
    if not endpoint:
        _minio_available = False
        return False
    try:
        parsed = urlparse(endpoint if "://" in endpoint else f"http://{endpoint}")
        host = parsed.hostname or "localhost"
        port = parsed.port or 9000
        sock = socket.create_connection((host, port), timeout=timeout_sec)
        sock.close()
        _minio_available = True
        return True
    except (socket.timeout, OSError, ConnectionRefusedError) as exc:
        logger.warning("MinIO unreachable at %s: %s", endpoint, exc)
        _minio_available = False
        return False


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _minio_endpoint_url() -> str | None:
    endpoint = os.getenv("MINIO_ENDPOINT")
    if not endpoint:
        return None
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    scheme = "https" if os.getenv("MINIO_USE_SSL", "false").lower() == "true" else "http"
    return f"{scheme}://{endpoint}"


def _get_store() -> EnterpriseObjectStore:
    global _store
    if _store is None:
        _store = EnterpriseObjectStore(
            endpoint_url=_minio_endpoint_url(),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            multipart_chunksize=DEFAULT_CHUNK_SIZE,
        )
    return _store


def _get_tenant_id(current_user: models.User, request: Request) -> str | None:
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        return tenant_id
    return getattr(current_user, "tenant_id", None)


def _storage_dir() -> str:
    env_dir = os.getenv("EVIDENCE_STORAGE_DIR")
    if env_dir:
        os.makedirs(env_dir, mode=0o755, exist_ok=True)
        return env_dir
    base = os.getcwd()
    if os.path.basename(base) == "backend":
        storage_dir = os.path.join(base, "storage", "evidence")
    else:
        storage_dir = os.path.join(base, "backend", "storage", "evidence")
    os.makedirs(storage_dir, mode=0o755, exist_ok=True)
    return storage_dir


def _build_object_key(case_id: str | None, filename: str) -> str:
    safe_name = os.path.basename(filename or "evidence.bin")
    case_segment = case_id or "unassigned"
    return f"cases/{case_segment}/{uuid.uuid4()}-{safe_name}"


def _session_parts(session: models.UploadSession) -> list[dict]:
    parts = session.parts or []
    return sorted(parts, key=lambda part: int(part["PartNumber"]))


def _touch_session(session: models.UploadSession) -> None:
    session.updated_at = datetime.now(timezone.utc)


def _create_processing_job(db: Session, evidence: models.Evidence) -> str:
    job = models.ForensicJob(evidence_id=evidence.id, processors=list_processors(), status="queued")
    db.add(job)
    db.flush()
    return job.id


@router.post("/start", response_model=UploadStartResponse)
def start_upload(
    body: UploadStartRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    database.init_db()

    if body.file_size <= 0:
        raise HTTPException(status_code=400, detail="file_size must be greater than zero")
    if body.file_size > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"file_size {body.file_size} exceeds maximum {MAX_UPLOAD_SIZE_BYTES} bytes "
                   f"({MAX_UPLOAD_SIZE_BYTES / (1024**3):.0f} GB). "
                   f"Set MAX_UPLOAD_SIZE_BYTES environment variable to increase the limit.",
        )

    if _minio_available is None:
        _check_minio_connectivity()
    if not _minio_available:
        raise HTTPException(
            status_code=503,
            detail="Object storage (MinIO) is not available. "
                   "Please ensure MinIO is running (docker-compose up -d).",
        )

    requested_chunk = body.chunk_size or DEFAULT_CHUNK_SIZE
    adaptive = _adaptive_chunk_size(body.file_size)
    chunk_size = min(max(min(requested_chunk, adaptive), MIN_CHUNK_SIZE), MAX_CHUNK_SIZE)
    total_chunks = max(1, (body.file_size + chunk_size - 1) // chunk_size)
    bucket = os.getenv("MINIO_BUCKET_EVIDENCE", "crimekit-evidence")
    object_key = _build_object_key(body.case_id, body.filename)

    content_type = body.mime_type or mimetypes.guess_type(body.filename)[0] or "application/octet-stream"
    metadata = {
        "uploaded_by": current_user.id,
        "original_filename": body.filename,
    }
    if body.case_id:
        metadata["case_id"] = body.case_id

    try:
        response = _get_store().client.create_multipart_upload(
            Bucket=bucket,
            Key=object_key,
            ContentType=content_type,
            Metadata=metadata,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"failed to start multipart upload: {exc}")

    session = models.UploadSession(
        user_id=current_user.id,
        tenant_id=_get_tenant_id(current_user, request),
        case_id=body.case_id,
        filename=body.filename,
        file_size=body.file_size,
        chunk_size=chunk_size,
        total_chunks=total_chunks,
        completed_chunks=0,
        status="in_progress",
        upload_id=response["UploadId"],
        bucket=bucket,
        object_key=object_key,
        sha256=body.sha256,
        mime_type=content_type,
        parts=[],
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    audit = models.AuditLog(
        actor_id=current_user.id,
        action="upload.start",
        target_type="upload_session",
        target_id=session.id,
        detail={
            "filename": body.filename,
            "file_size": body.file_size,
            "chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "bucket": bucket,
            "object_key": object_key,
        },
    )
    db.add(audit)
    db.commit()

    return UploadStartResponse(
        upload_id=session.upload_id,
        session_id=session.id,
        chunk_size=chunk_size,
        total_chunks=total_chunks,
        bucket=bucket,
        object_key=object_key,
        status=session.status,
    )


@router.post("/chunk", response_model=UploadChunkResponse)
def upload_chunk(
    session_id: str = Form(...),
    chunk_number: int = Form(...),
    chunk_sha256: str | None = Form(None),
    chunk: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.UploadSession).filter(models.UploadSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="upload session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    if session.status not in {"in_progress", "paused"}:
        raise HTTPException(status_code=400, detail=f"upload session is {session.status}")
    if chunk_number < 1 or chunk_number > session.total_chunks:
        raise HTTPException(status_code=400, detail="invalid chunk number")

    # Stream the chunk through a SpooledTemporaryFile to avoid holding the
    # entire payload (up to 100 MB) in RAM.  Data is spooled to disk once it
    # exceeds SPOOL_THRESHOLD, keeping memory usage predictable even when
    # multiple chunks upload in parallel.
    SPOOL_THRESHOLD = 10 * 1024 * 1024  # 10 MB
    READ_BLOCK = 262_144  # 256 KB

    spooled = tempfile.SpooledTemporaryFile(max_size=SPOOL_THRESHOLD)
    sha = hashlib.sha256()
    try:
        while True:
            block = chunk.file.read(READ_BLOCK)
            if not block:
                break
            spooled.write(block)
            sha.update(block)
    except Exception as exc:
        spooled.close()
        raise HTTPException(status_code=400, detail=f"failed to read chunk data: {exc}")

    digest = sha.hexdigest()
    chunk_len = spooled.tell()
    if chunk_len == 0:
        spooled.close()
        raise HTTPException(status_code=400, detail="empty chunk")

    if chunk_sha256 and digest != chunk_sha256:
        spooled.close()
        raise HTTPException(status_code=400, detail="chunk checksum mismatch")

    spooled.seek(0)

    try:
        response = _get_store().client.upload_part(
            Bucket=session.bucket,
            Key=session.object_key,
            PartNumber=chunk_number,
            UploadId=session.upload_id,
            Body=spooled,
            ContentLength=chunk_len,
        )
    except Exception as exc:
        chunk_row = db.query(models.UploadChunk).filter(
            models.UploadChunk.session_id == session.id,
            models.UploadChunk.chunk_number == chunk_number,
        ).first()
        if chunk_row:
            chunk_row.status = "failed"
            chunk_row.retries = (chunk_row.retries or 0) + 1
            chunk_row.error_message = str(exc)
            _touch_session(session)
            db.commit()
        raise HTTPException(status_code=503, detail=f"failed to upload chunk: {exc}")
    finally:
        spooled.close()

    chunk_row = db.query(models.UploadChunk).filter(
        models.UploadChunk.session_id == session.id,
        models.UploadChunk.chunk_number == chunk_number,
    ).first()
    is_new_chunk = chunk_row is None
    if chunk_row is None:
        chunk_row = models.UploadChunk(
            session_id=session.id,
            chunk_number=chunk_number,
            size=chunk_len,
            sha256=digest,
            etag=response["ETag"],
            status="uploaded",
            retries=0,
            uploaded_at=datetime.now(timezone.utc),
        )
        db.add(chunk_row)
    else:
        chunk_row.size = chunk_len
        chunk_row.sha256 = digest
        chunk_row.etag = response["ETag"]
        chunk_row.status = "uploaded"
        chunk_row.uploaded_at = datetime.now(timezone.utc)
        chunk_row.error_message = None

    parts = [part for part in (session.parts or []) if int(part["PartNumber"]) != chunk_number]
    parts.append({"PartNumber": chunk_number, "ETag": response["ETag"]})
    session.parts = sorted(parts, key=lambda part: int(part["PartNumber"]))
    if is_new_chunk:
        session.completed_chunks = min(session.total_chunks, (session.completed_chunks or 0) + 1)
    else:
        session.completed_chunks = len(session.parts or [])
    session.status = "in_progress"
    _touch_session(session)
    db.commit()

    return UploadChunkResponse(
        session_id=session.id,
        chunk_number=chunk_number,
        etag=response["ETag"],
        status="uploaded",
        completed_chunks=session.completed_chunks,
        total_chunks=session.total_chunks,
    )


@router.post("/complete", response_model=UploadCompleteResponse)
def complete_upload(
    session_id: str,
    body: UploadCompleteRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.UploadSession).filter(models.UploadSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="upload session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    if session.status == "completed" and session.evidence_id:
        return UploadCompleteResponse(
            session_id=session.id,
            evidence_id=session.evidence_id,
            sha256=session.sha256 or "",
            md5=session.md5,
            size=session.file_size,
            status=session.status,
        )

    parts = body.parts or _session_parts(session)
    if len(parts) != session.total_chunks:
        raise HTTPException(status_code=400, detail="not all chunks have been uploaded")

    try:
        _get_store().client.complete_multipart_upload(
            Bucket=session.bucket,
            Key=session.object_key,
            UploadId=session.upload_id,
            MultipartUpload={"Parts": parts},
        )
    except Exception as exc:
        session.status = "failed"
        session.error_message = str(exc)
        _touch_session(session)
        db.commit()
        raise HTTPException(status_code=503, detail=f"failed to complete multipart upload: {exc}")

    client_sha256 = session.sha256 or ""
    # Always hash the completed object on the server. A client digest is only
    # an assertion and must never determine integrity or storage routing.
    sha256_digest = ""
    md5_digest = session.md5 or ""

    if not sha256_digest:
        storage_dir = _storage_dir()
        local_path = os.path.join(storage_dir, str(uuid.uuid4()))
        sha256 = hashlib.sha256()
        md5 = hashlib.md5()

        try:
            stream = _get_store().client.get_object(Bucket=session.bucket, Key=session.object_key)
            body_stream = stream["Body"]
            with open(local_path, "wb") as output:
                while True:
                    data = body_stream.read(1024 * 1024)
                    if not data:
                        break
                    output.write(data)
                    sha256.update(data)
                    md5.update(data)
            body_stream.close()
        except Exception as exc:
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception:
                    pass
            session.status = "failed"
            session.error_message = f"failed to materialize evidence locally: {exc}"
            _touch_session(session)
            db.commit()
            raise HTTPException(status_code=500, detail=session.error_message)

        sha256_digest = sha256.hexdigest()
        md5_digest = md5.hexdigest()

        if client_sha256 and client_sha256.lower() != sha256_digest:
            session.status = "failed"
            session.error_message = "uploaded object SHA-256 does not match the declared digest"
            _touch_session(session)
            db.commit()
            if os.path.exists(local_path):
                os.remove(local_path)
            raise HTTPException(status_code=422, detail=session.error_message)

        duplicate = db.query(models.Evidence).filter(models.Evidence.sha256 == sha256_digest).first()
        if duplicate:
            if os.path.exists(local_path):
                os.remove(local_path)
            session.status = "completed"
            session.sha256 = sha256_digest
            session.md5 = md5_digest
            session.evidence_id = duplicate.id
            session.completed_at = datetime.now(timezone.utc)
            session.error_message = "duplicate upload matched existing evidence"
            _touch_session(session)
            db.commit()
            return UploadCompleteResponse(
                session_id=session.id,
                evidence_id=duplicate.id,
                sha256=sha256_digest,
                md5=md5_digest,
                size=session.file_size,
                status="completed",
            )

        final_path = os.path.join(storage_dir, sha256_digest)
        if local_path != final_path:
            if os.path.exists(final_path):
                os.remove(local_path)
            else:
                os.replace(local_path, final_path)
    evidence = models.Evidence(
        case_id=session.case_id,
        filename=session.filename,
        storage_path=final_path or f"minio://{session.bucket}/{session.object_key}",
        bucket=session.bucket,
        object_key=session.object_key,
        sha256=sha256_digest,
        size=os.path.getsize(final_path),
        mime_type=session.mime_type,
        metadata_json={
            "original_filename": session.filename,
            "multipart_upload_id": session.upload_id,
            "chunk_size": session.chunk_size,
            "total_chunks": session.total_chunks,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "source": "multipart_minio",
        },
        uploaded_by=current_user.id,
    )
    db.add(evidence)
    db.flush()

    db.add(
        models.ChainOfCustody(
            evidence_id=evidence.id,
            action="ingest",
            actor_id=current_user.id,
            notes="Initial ingest via multipart upload",
        )
    )
    db.add(
        models.AuditLog(
            actor_id=current_user.id,
            action="evidence.upload.multipart",
            target_type="evidence",
            target_id=evidence.id,
            detail={
                "upload_session_id": session.id,
                "sha256": sha256_digest,
                "md5": md5_digest,
                "size": session.file_size,
                "bucket": session.bucket,
                "object_key": session.object_key,
            },
        )
    )

    job_id = _create_processing_job(db, evidence)
    db.add(
        models.AuditLog(
            actor_id=current_user.id,
            action="processing.enqueue",
            target_type="evidence",
            target_id=evidence.id,
            detail={"job_id": job_id, "processors": None},
        )
    )

    session.status = "completed"
    session.sha256 = sha256_digest
    session.md5 = md5_digest
    session.evidence_id = evidence.id
    session.completed_chunks = session.total_chunks
    session.completed_at = datetime.now(timezone.utc)
    session.error_message = None
    _touch_session(session)
    db.commit()

    if os.getenv("TESTING") != "1":
        start_worker()

    return UploadCompleteResponse(
        session_id=session.id,
        evidence_id=evidence.id,
        sha256=sha256_digest,
        md5=md5_digest,
        size=session.file_size,
        status=session.status,
    )


@router.post("/cancel")
def cancel_upload(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.UploadSession).filter(models.UploadSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="upload session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    if session.status in {"completed", "cancelled"}:
        return {"session_id": session.id, "status": session.status}

    try:
        _get_store().client.abort_multipart_upload(
            Bucket=session.bucket,
            Key=session.object_key,
            UploadId=session.upload_id,
        )
    except Exception:
        pass

    session.status = "cancelled"
    session.error_message = None
    _touch_session(session)
    db.commit()
    return {"session_id": session.id, "status": session.status}


@router.get("/status/{upload_id}")
def get_upload_status(
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.UploadSession).filter(models.UploadSession.id == upload_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="upload session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")

    chunks = db.query(models.UploadChunk).filter(models.UploadChunk.session_id == session.id).all()
    return {
        **UploadSessionOut.from_orm(session).dict(),
        "bucket": session.bucket,
        "object_key": session.object_key,
        "upload_id": session.upload_id,
        "completed_part_numbers": sorted(chunk.chunk_number for chunk in chunks if chunk.status == "uploaded"),
        "parts": _session_parts(session),
        "chunks": [
            {
                "chunk_number": chunk.chunk_number,
                "size": chunk.size,
                "status": chunk.status,
                "retries": chunk.retries,
                "etag": chunk.etag,
                "error_message": chunk.error_message,
            }
            for chunk in sorted(chunks, key=lambda item: item.chunk_number)
        ],
    }


@router.post("/resume")
def resume_upload(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.UploadSession).filter(models.UploadSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="upload session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    if session.status == "cancelled":
        raise HTTPException(status_code=400, detail="cancelled uploads cannot be resumed")

    session.status = "in_progress"
    _touch_session(session)
    db.commit()
    return get_upload_status(session.id, db, current_user)


@router.delete("/{upload_id}")
def delete_upload(
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.UploadSession).filter(models.UploadSession.id == upload_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="upload session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")

    if session.status not in {"completed", "cancelled"}:
        try:
            _get_store().client.abort_multipart_upload(
                Bucket=session.bucket,
                Key=session.object_key,
                UploadId=session.upload_id,
            )
        except Exception:
            pass

    db.query(models.UploadChunk).filter(models.UploadChunk.session_id == session.id).delete()
    db.delete(session)
    db.commit()
    return {"deleted": True, "upload_id": upload_id}
