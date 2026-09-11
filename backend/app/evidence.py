from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import FileResponse, RedirectResponse, Response
from sqlalchemy.orm import Session
from . import database
from . import models
from .auth import get_current_user, role_required
import hashlib
import os
import shutil
import mimetypes
from datetime import datetime, timezone
import json
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/evidence', tags=['evidence'])


def _public_metadata(value: dict | None) -> dict:
    metadata = dict(value or {})
    engine = metadata.get("forensic_engine") or {}
    engine_metadata = engine.get("metadata") or {}
    forensic_image = engine_metadata.get("forensic_image") or metadata.get("forensic_image")
    if forensic_image:
        metadata.setdefault("evidence_type", forensic_image.get("evidence_type"))
        metadata.setdefault("image_format", forensic_image.get("image_format"))
        metadata.setdefault("processor", forensic_image.get("processor"))
        metadata.setdefault("capability", forensic_image.get("capability"))
        metadata.setdefault("capability_reason", forensic_image.get("reason"))
        metadata.setdefault("forensic_image", forensic_image)
    return metadata


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_storage_dir() -> str:
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


@router.post('/upload')
def upload_evidence(case_id: str | None = Form(None), file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Save file to storage and compute SHA-256
    storage_dir = get_storage_dir()
    filename = file.filename
    temp_path = os.path.join(storage_dir, f"tmp-{datetime.now(timezone.utc).timestamp()}-{filename}")
    sha256 = hashlib.sha256()
    size = 0
    try:
        with open(temp_path, 'wb') as out:
            while True:
                chunk = file.file.read(1024 * 64)
                if not chunk:
                    break
                out.write(chunk)
                sha256.update(chunk)
                size += len(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'failed to save file: {e}')

    digest = sha256.hexdigest()
    # final storage path
    storage_path = os.path.join(storage_dir, digest)
    # move/rename
    shutil.move(temp_path, storage_path)
    mime_type = file.content_type or mimetypes.guess_type(filename)[0]

    # gather file timestamps
    try:
        stat = os.stat(storage_path)
        created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
    except Exception:
        created_at = None
        modified_at = None

    evidence = models.Evidence(
        case_id=case_id,
        filename=filename,
        storage_path=storage_path,
        sha256=digest,
        size=size,
        mime_type=mime_type,
        metadata_json={"original_filename": filename, "created_at": created_at, "modified_at": modified_at},
        uploaded_by=current_user.id,
    )
    db.add(evidence)
    db.flush()
    db.commit()

    coc = models.ChainOfCustody(evidence_id=evidence.id, action='ingest', actor_id=current_user.id, notes='Initial ingest')
    db.add(coc)
    db.commit()

    audit = models.AuditLog(actor_id=current_user.id, action='evidence.upload', target_type='evidence', target_id=evidence.id, detail={'sha256': digest, 'size': size})
    db.add(audit)
    db.commit()

    # Auto-enqueue forensic processing (same as multipart upload path)
    try:
        from .processors import list_processors as _list_procs
        from .processing import start_worker as _start_worker
        fj = models.ForensicJob(evidence_id=evidence.id, processors=_list_procs(), status='queued')
        db.add(fj)
        db.commit()
        _start_worker()
    except Exception as exc:
        logger.warning(f"Failed to auto-enqueue forensic job: {exc}")

    return {"id": evidence.id, "sha256": digest, "size": size, "mime_type": mime_type}


@router.get('/')
def get_all_evidence(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    mime_type: Optional[str] = Query(None),
    case_id: Optional[str] = Query(None),
    sort_by: str = Query("uploaded_at"),
    sort_order: str = Query("desc"),
):
    q = db.query(models.Evidence)

    if search:
        term = f"%{search}%"
        q = q.filter(
            (models.Evidence.filename.ilike(term))
            | (models.Evidence.id.ilike(term))
            | (models.Evidence.sha256.ilike(term))
        )
    if mime_type:
        q = q.filter(models.Evidence.mime_type.ilike(f"%{mime_type}%"))
    if case_id:
        q = q.filter(models.Evidence.case_id == case_id)

    total = q.count()

    sort_col = getattr(models.Evidence, sort_by, models.Evidence.uploaded_at)
    if sort_order == "asc":
        q = q.order_by(sort_col.asc())
    else:
        q = q.order_by(sort_col.desc())

    offset = (page - 1) * limit
    items = q.offset(offset).limit(limit).all()

    return {
        'items': [
            {
                'id': ev.id,
                'case_id': ev.case_id,
                'filename': ev.filename,
                'sha256': ev.sha256,
                'mime_type': ev.mime_type,
                'size': ev.size,
                'metadata': _public_metadata(ev.metadata_json),
                'uploaded_at': ev.uploaded_at.isoformat() if ev.uploaded_at else None,
            } for ev in items
        ],
        'total': total,
        'page': page,
        'limit': limit,
        'offset': offset,
    }


@router.get('/{evidence_id}')
def get_evidence(evidence_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail='evidence not found')
    # audit access
    audit = models.AuditLog(actor_id=current_user.id, action='evidence.view', target_type='evidence', target_id=ev.id, detail={})
    db.add(audit)
    db.commit()
    return {
        'id': ev.id,
        'case_id': ev.case_id,
        'filename': ev.filename,
        'sha256': ev.sha256,
        'size': ev.size,
        'mime_type': ev.mime_type,
        'metadata': _public_metadata(ev.metadata_json),
        'uploaded_by': ev.uploaded_by,
        'uploaded_at': ev.uploaded_at.isoformat() if ev.uploaded_at else None,
    }


@router.get('/{evidence_id}/ocr')
def get_evidence_ocr(evidence_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Return OCR / extracted text for an evidence item.

    Serves the persisted OCR text produced by forensic processing. Text is
    sourced from the Document table (created by the forensic pipeline) and
    falls back to evidence metadata. Returns ``source: "none"`` when no text
    has been extracted yet.
    """
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail='evidence not found')

    text: str | None = None
    source = 'none'
    created_at: str | None = None
    meta: dict = {}

    doc = (
        db.query(models.Document)
        .filter(models.Document.evidence_id == evidence_id)
        .order_by(models.Document.created_at.desc())
        .first()
    )
    if doc and doc.text and doc.text.strip():
        text = doc.text
        source = 'document'
        created_at = doc.created_at.isoformat() if doc.created_at else None
    else:
        ev_meta = ev.metadata_json or {}
        ocr_text = ev_meta.get('ocr_text') or ev_meta.get('extracted_text')
        if ocr_text and str(ocr_text).strip():
            text = str(ocr_text)
            source = 'metadata'

    if ev.metadata_json:
        meta = dict(ev.metadata_json)

    return {
        'evidence_id': evidence_id,
        'text': text,
        'source': source,
        'metadata': meta,
        'created_at': created_at,
    }


@router.get('/case/{case_id}')
def list_case_evidence(case_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    items = db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()
    # audit list action
    audit = models.AuditLog(actor_id=current_user.id, action='evidence.list', target_type='case', target_id=case_id, detail={'count': len(items)})
    db.add(audit)
    db.commit()
    return [
        {
            'id': e.id,
            'filename': e.filename,
            'sha256': e.sha256,
            'size': e.size,
            'mime_type': e.mime_type,
            'case_id': e.case_id,
            'metadata': _public_metadata(e.metadata_json),
            'uploaded_at': e.uploaded_at.isoformat() if e.uploaded_at else None,
        }
        for e in items
    ]


@router.post('/{evidence_id}/custody')
def append_custody(evidence_id: str, payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # RBAC: only admin or investigator can append
    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles:
        raise HTTPException(status_code=403, detail='forbidden')

    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail='evidence not found')

    # verify integrity before logging custody action
    integrity_ok = True
    try:
        sha256 = hashlib.sha256()
        with open(ev.storage_path, 'rb') as f:
            while True:
                chunk = f.read(1024 * 64)
                if not chunk:
                    break
                sha256.update(chunk)
        integrity_ok = (sha256.hexdigest() == ev.sha256)
    except Exception:
        integrity_ok = False

    # compose notes as JSON to preserve structured fields
    details = {
        'previous_owner': payload.get('previous_owner'),
        'new_owner': payload.get('new_owner'),
        'location': payload.get('location'),
        'notes': payload.get('notes'),
        'signature': payload.get('signature'),
    }

    coc = models.ChainOfCustody(evidence_id=evidence_id, action=payload.get('action', 'update'), actor_id=current_user.id, notes=json.dumps(details))
    db.add(coc)
    db.commit()

    audit = models.AuditLog(actor_id=current_user.id, action='evidence.custody.append', target_type='evidence', target_id=evidence_id, detail={'action': payload.get('action'), 'integrity_ok': integrity_ok, 'details': details})
    db.add(audit)
    db.commit()

    return {'custody_id': coc.id, 'integrity_ok': integrity_ok}


@router.get('/{evidence_id}/custody')
def get_custody(evidence_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail='evidence not found')

    # read permission: admin, investigator, or uploader
    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != ev.uploaded_by:
        raise HTTPException(status_code=403, detail='forbidden')

    items = db.query(models.ChainOfCustody).filter(models.ChainOfCustody.evidence_id == evidence_id).order_by(models.ChainOfCustody.timestamp.asc()).all()

    # compute integrity
    integrity_ok = True
    try:
        sha256 = hashlib.sha256()
        with open(ev.storage_path, 'rb') as f:
            while True:
                chunk = f.read(1024 * 64)
                if not chunk:
                    break
                sha256.update(chunk)
        integrity_ok = (sha256.hexdigest() == ev.sha256)
    except Exception:
        integrity_ok = False

    # audit the read
    audit = models.AuditLog(actor_id=current_user.id, action='evidence.custody.view', target_type='evidence', target_id=evidence_id, detail={'count': len(items), 'integrity_ok': integrity_ok})
    db.add(audit)
    db.commit()

    result = []
    for c in items:
        try:
            notes = json.loads(c.notes) if c.notes else {}
        except Exception:
            notes = {'notes': c.notes}
        result.append({
            'id': c.id,
            'action': c.action,
            'actor_id': c.actor_id,
            'timestamp': c.timestamp.isoformat() if c.timestamp else None,
            'details': notes,
        })

    return {'evidence_id': evidence_id, 'integrity_ok': integrity_ok, 'history': result}

@router.patch('/{evidence_id}/reassign')
def reassign_evidence(evidence_id: str, payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(role_required(['investigator', 'admin']))):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail='evidence not found')

    new_case_id = payload.get('case_id')
    old_case_id = ev.case_id

    if new_case_id and new_case_id != old_case_id:
        case = db.query(models.Case).filter(models.Case.id == new_case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail='target case not found')

    ev.case_id = new_case_id
    db.add(ev)
    db.commit()

    coc = models.ChainOfCustody(
        evidence_id=evidence_id,
        action='reassign',
        actor_id=current_user.id,
        notes=f'Reassigned from case {old_case_id or "None"} to case {new_case_id or "None"}',
    )
    db.add(coc)

    audit = models.AuditLog(
        actor_id=current_user.id,
        action='evidence.reassign',
        target_type='evidence',
        target_id=evidence_id,
        detail={'old_case_id': old_case_id, 'new_case_id': new_case_id},
    )
    db.add(audit)
    db.commit()

    return {'evidence_id': evidence_id, 'case_id': new_case_id, 'old_case_id': old_case_id}


@router.get('/{evidence_id}/download')
def download_evidence(evidence_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail='evidence not found')
    audit = models.AuditLog(actor_id=current_user.id, action='evidence.download', target_type='evidence', target_id=ev.id, detail={})
    db.add(audit)
    db.commit()

    if ev.bucket and ev.object_key:
        try:
            from .storage import EnterpriseObjectStore
            import os as _os
            endpoint = _os.getenv("MINIO_ENDPOINT")
            if endpoint:
                if not endpoint.startswith("http"):
                    scheme = "https" if _os.getenv("MINIO_USE_SSL", "false").lower() == "true" else "http"
                    endpoint = f"{scheme}://{endpoint}"
                store = EnterpriseObjectStore(
                    endpoint_url=endpoint,
                    access_key=_os.getenv("MINIO_ACCESS_KEY"),
                    secret_key=_os.getenv("MINIO_SECRET_KEY"),
                )
                from fastapi.responses import StreamingResponse
                obj = store.client.get_object(Bucket=ev.bucket, Key=ev.object_key)
                body = obj["Body"]
                def iter_chunks():
                    try:
                        while True:
                            data = body.read(1024 * 1024)
                            if not data:
                                break
                            yield data
                    finally:
                        body.close()
                return StreamingResponse(
                    iter_chunks(),
                    media_type=ev.mime_type or 'application/octet-stream',
                    headers={"Content-Disposition": f'attachment; filename="{ev.filename}"'},
                )
        except Exception:
            pass

    if not os.path.exists(ev.storage_path):
        raise HTTPException(status_code=404, detail='file not found on disk')
    return FileResponse(
        path=ev.storage_path,
        filename=ev.filename,
        media_type=ev.mime_type or 'application/octet-stream',
    )


@router.delete('/{evidence_id}', status_code=204)
def delete_evidence(evidence_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(role_required(['investigator', 'admin']))):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail='evidence not found')

    # Check legal hold protection
    try:
        from .compliance import DataRetentionService
        if DataRetentionService.is_under_legal_hold(db, evidence_id=evidence_id):
            raise HTTPException(status_code=409, detail='Evidence cannot be deleted: it is under an active legal hold')
    except HTTPException:
        raise
    except Exception:
        pass  # If compliance module unavailable, proceed with delete

    # Check immutable integrity lock (hard lock prevents deletion)
    try:
        from .compliance import ImmutableEvidenceLock
        if db.query(ImmutableEvidenceLock).filter(ImmutableEvidenceLock.evidence_id == evidence_id).first():
            raise HTTPException(
                status_code=409,
                detail='Evidence cannot be deleted: it is protected by an immutable integrity lock',
            )
    except HTTPException:
        raise
    except Exception:
        pass  # If compliance module unavailable, proceed with delete

    filename = ev.filename
    bucket = ev.bucket
    object_key = ev.object_key
    storage_path = ev.storage_path
    sha256_hash = ev.sha256

    # 1. Preserve Chain of Custody history before deleting evidence row
    coc = models.ChainOfCustody(
        evidence_id=evidence_id,
        action='deleted',
        actor_id=current_user.id,
        notes=f'Evidence "{filename}" (SHA256: {sha256_hash}) permanently deleted by {current_user.email or current_user.id}. Audit trail preserved.'
    )
    db.add(coc)
    db.commit()

    # 2. Remove object from MinIO if present
    if bucket and object_key:
        try:
            from .storage import EnterpriseObjectStore
            import os as _os
            endpoint = _os.getenv("MINIO_ENDPOINT")
            if endpoint:
                if not endpoint.startswith("http"):
                    scheme = "https" if _os.getenv("MINIO_USE_SSL", "false").lower() == "true" else "http"
                    endpoint = f"{scheme}://{endpoint}"
                store = EnterpriseObjectStore(
                    endpoint_url=endpoint,
                    access_key=_os.getenv("MINIO_ACCESS_KEY"),
                    secret_key=_os.getenv("MINIO_SECRET_KEY"),
                )
                store.client.delete_object(Bucket=bucket, Key=object_key)
        except Exception as e:
            logger.warning(f"MinIO delete error for {bucket}/{object_key}: {e}")

    # 3. Remove from local disk and preview files
    try:
        if storage_path and os.path.exists(storage_path):
            os.remove(storage_path)
    except Exception as e:
        logger.warning(f"Local storage delete error for {storage_path}: {e}")

    # 4. Remove related upload sessions and chunk files
    upload_sessions = db.query(models.UploadSession).filter(models.UploadSession.evidence_id == evidence_id).all()
    session_ids = [s.id for s in upload_sessions]
    for sess in upload_sessions:
        chunk_dir = os.path.join(os.getenv("STORAGE_DIR", "storage"), "chunks", sess.id)
        if os.path.exists(chunk_dir):
            try:
                import shutil
                shutil.rmtree(chunk_dir)
            except Exception:
                pass
    # Delete child chunks before sessions (FK: upload_chunks_session_id_fkey)
    if session_ids:
        db.query(models.UploadChunk).filter(models.UploadChunk.session_id.in_(session_ids)).delete()
    db.query(models.UploadSession).filter(models.UploadSession.evidence_id == evidence_id).delete()
    db.flush()

    # 5. Remove documents and embeddings
    docs = db.query(models.Document).filter(models.Document.evidence_id == evidence_id).all()
    for doc in docs:
        db.query(models.Embedding).filter(models.Embedding.document_id == doc.id).delete()
        db.delete(doc)

    # 6. Remove forensic jobs and results
    db.query(models.ForensicResult).filter(models.ForensicResult.evidence_id == evidence_id).delete()
    db.query(models.ForensicJob).filter(models.ForensicJob.evidence_id == evidence_id).delete()

    # 6b. Remove related evidence exports
    try:
        from .compliance import EvidenceExport
        db.query(EvidenceExport).filter(EvidenceExport.evidence_id == evidence_id).delete()
    except Exception:
        pass

    # 7. Delete evidence record
    db.delete(ev)

    # 8. Create AuditLog entry
    audit = models.AuditLog(
        actor_id=current_user.id,
        action='evidence.delete',
        target_type='evidence',
        target_id=evidence_id,
        detail={'filename': filename, 'sha256': sha256_hash}
    )
    db.add(audit)
    db.commit()
    return Response(status_code=204)
