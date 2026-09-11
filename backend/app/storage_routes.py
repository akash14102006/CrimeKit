"""Enterprise Object Storage API routes — buckets, objects, versioning, legal holds, quotas."""

import base64
import logging
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .auth import get_current_user
from .storage import (
    BucketPolicy,
    EnterpriseObjectStore,
    ObjectLockMode,
    RetentionPolicy,
    StorageError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/storage", tags=["storage"])


def _require_admin(current_user):
    roles = [r.name for r in current_user.roles]
    if "admin" not in roles:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="forbidden: admin required")


_store: EnterpriseObjectStore | None = None


def _get_store() -> EnterpriseObjectStore:
    global _store
    if _store is None:
        import os

        endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        if endpoint and not endpoint.startswith("http"):
            secure = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
            endpoint = f"http{'s' if secure else ''}://{endpoint}"
        _store = EnterpriseObjectStore(
            endpoint_url=endpoint,
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            region=os.getenv("AWS_REGION", "us-east-1"),
        )
    return _store


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class BucketPolicyBody(BaseModel):
    versioning_enabled: bool = False
    object_lock_enabled: bool = False
    object_lock_mode: Literal["COMPLIANCE", "GOVERNANCE"] = "COMPLIANCE"
    immutable: bool = False
    default_encryption: Literal["S3", "KMS"] = "S3"
    kms_key_id: Optional[str] = None


class CreateBucketRequest(BaseModel):
    name: str
    policy: BucketPolicyBody = BucketPolicyBody()


class VersioningRequest(BaseModel):
    enabled: bool


class LifecycleRule(BaseModel):
    id: Optional[str] = None
    status: Literal["Enabled", "Disabled"] = "Enabled"
    prefix: str = ""
    transitions: list[dict[str, Any]] = []
    expiration_days: Optional[int] = None
    noncurrent_expiration_days: Optional[int] = None
    abort_incomplete_multipart_days: Optional[int] = None


class LifecycleRequest(BaseModel):
    rules: list[LifecycleRule]


class ObjectLockRequest(BaseModel):
    mode: Literal["COMPLIANCE", "GOVERNANCE"] = "COMPLIANCE"
    days: Optional[int] = None
    years: Optional[int] = None


class UploadRequest(BaseModel):
    bucket: str
    key: str
    content_bytes: str
    content_type: str = "application/octet-stream"
    tags: dict[str, str] = {}


class MultipartInitRequest(BaseModel):
    bucket: str
    key: str
    content_type: str = "application/octet-stream"


class MultipartPartRequest(BaseModel):
    upload_id: str
    bucket: str
    key: str
    part_number: int
    data: str


class MultipartCompleteRequest(BaseModel):
    upload_id: str
    bucket: str
    key: str
    parts: list[dict[str, Any]]


class LegalHoldRequest(BaseModel):
    enabled: bool


class RetentionRequest(BaseModel):
    mode: Literal["COMPLIANCE", "GOVERNANCE"] = "COMPLIANCE"
    days: Optional[int] = None
    years: Optional[int] = None


class PresignedURLRequest(BaseModel):
    expiry_seconds: int = 3600
    method: Literal["GET", "PUT"] = "GET"


class QuotaRequest(BaseModel):
    quota_bytes: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _error_response(exc: StorageError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status,
        content={"error": exc.code, "detail": str(exc)},
    )


def _json(data: Any, status: int = 200) -> JSONResponse:
    return JSONResponse(content=data, status_code=status)


# ---------------------------------------------------------------------------
# 1. POST /buckets — Create bucket
# ---------------------------------------------------------------------------


@router.post("/buckets")
async def create_bucket(body: CreateBucketRequest, current_user=Depends(get_current_user)):
    """Create a new bucket with an optional enterprise policy."""
    _require_admin(current_user)
    policy = BucketPolicy(
        versioning_enabled=body.policy.versioning_enabled,
        object_lock_enabled=body.policy.object_lock_enabled,
        object_lock_mode=body.policy.object_lock_mode,
        immutable=body.policy.immutable,
        default_encryption=body.policy.default_encryption,
        kms_key_id=body.policy.kms_key_id,
    )
    try:
        _get_store().create_bucket(body.name, policy=policy)
    except StorageError as exc:
        return _error_response(exc)
    return _json({"bucket": body.name, "message": "Bucket created"}, status=201)


# ---------------------------------------------------------------------------
# 2. GET /buckets — List all buckets
# ---------------------------------------------------------------------------


@router.get("/buckets")
async def list_buckets(_user=Depends(get_current_user)):
    """List every bucket visible to the calling user."""
    try:
        resp = _get_store().client.list_buckets()
        buckets = [
            {
                "name": b["Name"],
                "creation_date": b["CreationDate"].isoformat(),
            }
            for b in resp.get("Buckets", [])
        ]
    except StorageError as exc:
        return _error_response(exc)
    return _json({"buckets": buckets})


# ---------------------------------------------------------------------------
# 3. DELETE /buckets/{bucket_name} — Delete bucket
# ---------------------------------------------------------------------------


@router.delete("/buckets/{bucket_name}")
async def delete_bucket(bucket_name: str, current_user=Depends(get_current_user)):
    """Delete an empty bucket."""
    _require_admin(current_user)
    try:
        _get_store().delete_bucket(bucket_name)
    except StorageError as exc:
        return _error_response(exc)
    return _json({"bucket": bucket_name, "message": "Bucket deleted"})


# ---------------------------------------------------------------------------
# 4. POST /buckets/{bucket_name}/versioning — Enable/disable versioning
# ---------------------------------------------------------------------------


@router.post("/buckets/{bucket_name}/versioning")
async def set_versioning(bucket_name: str, body: VersioningRequest, current_user=Depends(get_current_user)):
    """Enable or suspend versioning on a bucket."""
    _require_admin(current_user)
    try:
        if body.enabled:
            _get_store().enable_versioning(bucket_name)
        else:
            _get_store().suspend_versioning(bucket_name)
    except StorageError as exc:
        return _error_response(exc)
    return _json({"bucket": bucket_name, "versioning_enabled": body.enabled})


# ---------------------------------------------------------------------------
# 5. POST /buckets/{bucket_name}/lifecycle — Set lifecycle rules
# ---------------------------------------------------------------------------


@router.post("/buckets/{bucket_name}/lifecycle")
async def set_lifecycle(bucket_name: str, body: LifecycleRequest, current_user=Depends(get_current_user)):
    """Replace lifecycle configuration on a bucket."""
    _require_admin(current_user)
    try:
        from .storage import LifecyclePolicy

        rules_raw: list[dict[str, Any]] = []
        for idx, rule in enumerate(body.rules):
            lp = LifecyclePolicy(
                transitions=rule.transitions,
                expiration_days=rule.expiration_days,
                noncurrent_expiration_days=rule.noncurrent_expiration_days,
                abort_incomplete_multipart_days=rule.abort_incomplete_multipart_days,
            )
            rules_raw.append(lp.to_rule(rule.id or f"rule-{idx}", rule.prefix))
        _get_store().client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration={"Rules": rules_raw},
        )
    except StorageError as exc:
        return _error_response(exc)
    return _json({"bucket": bucket_name, "lifecycle_rules_applied": len(body.rules)})


# ---------------------------------------------------------------------------
# 6. POST /buckets/{bucket_name}/locking — Set object lock configuration
# ---------------------------------------------------------------------------


@router.post("/buckets/{bucket_name}/locking")
async def set_object_lock(bucket_name: str, body: ObjectLockRequest, current_user=Depends(get_current_user)):
    """Configure default object lock retention for new objects."""
    _require_admin(current_user)
    if body.days is None and body.years is None:
        return _json({"error": "Provide days or years"}, status=400)
    if body.days is not None and body.years is not None:
        return _json({"error": "Provide either days or years, not both"}, status=400)
    try:
        rule: dict[str, Any] = {"Mode": body.mode}
        if body.days is not None:
            rule["Days"] = body.days
        else:
            rule["Years"] = body.years
        _get_store().client.put_object_lock_configuration(
            Bucket=bucket_name,
            ObjectLockConfiguration={
                "ObjectLockEnabled": "Enabled",
                "Rule": {"DefaultRetention": rule},
            },
        )
    except StorageError as exc:
        return _error_response(exc)
    return _json({"bucket": bucket_name, "lock_mode": body.mode})


# ---------------------------------------------------------------------------
# 7. POST /upload — Upload file to bucket
# ---------------------------------------------------------------------------


@router.post("/upload")
async def upload_object(body: UploadRequest, _user=Depends(get_current_user)):
    """Upload a base64-encoded object to a bucket."""
    try:
        data = base64.b64decode(body.content_bytes)
    except Exception:
        return _json({"error": "Invalid base64 content"}, status=400)
    try:
        result = _get_store().upload_object(
            bucket=body.bucket,
            key=body.key,
            data=data,
            tenant_id=None,
            content_type=body.content_type,
            metadata=body.tags or None,
        )
    except StorageError as exc:
        return _error_response(exc)
    return _json(result, status=201)


# ---------------------------------------------------------------------------
# 8. POST /upload/multipart/init — Init multipart upload
# ---------------------------------------------------------------------------


@router.post("/upload/multipart/init")
async def multipart_init(body: MultipartInitRequest, _user=Depends(get_current_user)):
    """Initiate a new multipart upload and return the upload_id."""
    try:
        resp = _get_store().client.create_multipart_upload(
            Bucket=body.bucket,
            Key=body.key,
            ContentType=body.content_type,
        )
    except StorageError as exc:
        return _error_response(exc)
    return _json(
        {
            "upload_id": resp["UploadId"],
            "bucket": body.bucket,
            "key": body.key,
        },
        status=201,
    )


# ---------------------------------------------------------------------------
# 9. POST /upload/multipart/part — Upload part
# ---------------------------------------------------------------------------


@router.post("/upload/multipart/part")
async def multipart_part(body: MultipartPartRequest, _user=Depends(get_current_user)):
    """Upload a single part to an in-progress multipart upload."""
    try:
        data = base64.b64decode(body.data)
    except Exception:
        return _json({"error": "Invalid base64 data"}, status=400)
    try:
        resp = _get_store().client.upload_part(
            Bucket=body.bucket,
            Key=body.key,
            PartNumber=body.part_number,
            UploadId=body.upload_id,
            Body=data,
        )
    except StorageError as exc:
        return _error_response(exc)
    return _json(
        {
            "part_number": body.part_number,
            "etag": resp["ETag"],
        }
    )


# ---------------------------------------------------------------------------
# 10. POST /upload/multipart/complete — Complete multipart
# ---------------------------------------------------------------------------


@router.post("/upload/multipart/complete")
async def multipart_complete(body: MultipartCompleteRequest, _user=Depends(get_current_user)):
    """Complete a multipart upload by committing all uploaded parts."""
    try:
        resp = _get_store().client.complete_multipart_upload(
            Bucket=body.bucket,
            Key=body.key,
            UploadId=body.upload_id,
            MultipartUpload={"Parts": body.parts},
        )
    except StorageError as exc:
        return _error_response(exc)
    return _json(
        {
            "bucket": body.bucket,
            "key": body.key,
            "upload_id": body.upload_id,
            "etag": resp.get("ETag"),
            "version_id": resp.get("VersionId"),
            "location": resp.get("Location"),
        }
    )


# ---------------------------------------------------------------------------
# 11. GET /objects/{bucket_name}/{key:path} — Download object
# ---------------------------------------------------------------------------


@router.get("/objects/{bucket_name}/{key:path}")
async def download_object(bucket_name: str, key: str, request: Request, _user=Depends(get_current_user)):
    """Stream the raw bytes of an object to the client."""
    version_id = request.query_params.get("version_id")
    range_header = request.headers.get("range")
    try:
        data = _get_store().download_object(
            bucket_name, key, version_id=version_id, range_header=range_header
        )
    except StorageError as exc:
        return _error_response(exc)
    return JSONResponse(content=base64.b64encode(data).decode(), media_type="application/json")


# ---------------------------------------------------------------------------
# 12. HEAD /objects/{bucket_name}/{key:path} — Get object metadata
# ---------------------------------------------------------------------------


@router.head("/objects/{bucket_name}/{key:path}")
async def head_object(bucket_name: str, key: str, request: Request, _user=Depends(get_current_user)):
    """Return object metadata without downloading the body."""
    version_id = request.query_params.get("version_id")
    try:
        meta = _get_store().head_object(bucket_name, key, version_id=version_id)
    except StorageError as exc:
        return _error_response(exc)
    return _json(meta)


# ---------------------------------------------------------------------------
# 13. DELETE /objects/{bucket_name}/{key:path} — Delete object
# ---------------------------------------------------------------------------


@router.delete("/objects/{bucket_name}/{key:path}")
async def delete_object(bucket_name: str, key: str, request: Request, _user=Depends(get_current_user)):
    """Delete an object (or a specific version)."""
    version_id = request.query_params.get("version_id")
    try:
        _get_store().delete_object(bucket_name, key, version_id=version_id)
    except StorageError as exc:
        return _error_response(exc)
    return _json({"bucket": bucket_name, "key": key, "message": "Object deleted"})


# ---------------------------------------------------------------------------
# 14. GET /objects/{bucket_name}/{key:path}/versions — List object versions
# ---------------------------------------------------------------------------


@router.get("/objects/{bucket_name}/{key:path}/versions")
async def list_object_versions(bucket_name: str, key: str, _user=Depends(get_current_user)):
    """List all versions and delete markers for an object."""
    try:
        versions = _get_store().list_object_versions(bucket_name, prefix=key)
    except StorageError as exc:
        return _error_response(exc)
    return _json(
        {
            "bucket": bucket_name,
            "key": key,
            "versions": [
                {
                    "version_id": v.version_id,
                    "etag": v.etag,
                    "size": v.size,
                    "last_modified": v.last_modified.isoformat(),
                    "is_latest": v.is_latest,
                    "delete_marker": v.delete_marker,
                    "storage_class": v.storage_class,
                }
                for v in versions
            ],
        }
    )


# ---------------------------------------------------------------------------
# 15. GET /objects/{bucket_name}/{key:path}/checksum — Validate checksum
# ---------------------------------------------------------------------------


@router.get("/objects/{bucket_name}/{key:path}/checksum")
async def validate_checksum(bucket_name: str, key: str, _user=Depends(get_current_user)):
    """Download the object and compute its SHA-256 checksum for verification."""
    try:
        data = _get_store().download_object(bucket_name, key)
    except StorageError as exc:
        return _error_response(exc)
    import hashlib

    sha256 = hashlib.sha256(data).hexdigest()
    return _json(
        {
            "bucket": bucket_name,
            "key": key,
            "checksum_sha256": sha256,
            "size": len(data),
        }
    )


# ---------------------------------------------------------------------------
# 16. POST /objects/{bucket_name}/{key:path}/legal-hold — Set legal hold
# ---------------------------------------------------------------------------


@router.post("/objects/{bucket_name}/{key:path}/legal-hold")
async def set_legal_hold(bucket_name: str, key: str, body: LegalHoldRequest, current_user=Depends(get_current_user)):
    """Enable or disable a legal hold on an object version."""
    _require_admin(current_user)
    try:
        status_str = "ON" if body.enabled else "OFF"
        _get_store().put_legal_hold(bucket_name, key, status=status_str)
    except StorageError as exc:
        return _error_response(exc)
    return _json({"bucket": bucket_name, "key": key, "legal_hold": body.enabled})


# ---------------------------------------------------------------------------
# 17. POST /objects/{bucket_name}/{key:path}/retention — Set retention
# ---------------------------------------------------------------------------


@router.post("/objects/{bucket_name}/{key:path}/retention")
async def set_retention(bucket_name: str, key: str, body: RetentionRequest, current_user=Depends(get_current_user)):
    """Apply a governance or compliance retention policy to an object."""
    _require_admin(current_user)
    try:
        retention = RetentionPolicy(mode=body.mode, days=body.days, years=body.years)
        _get_store().put_object_retention(bucket_name, key, retention)
    except StorageError as exc:
        return _error_response(exc)
    return _json({"bucket": bucket_name, "key": key, "retention_mode": body.mode})


# ---------------------------------------------------------------------------
# 18. POST /presigned/{bucket_name}/{key:path} — Generate presigned URL
# ---------------------------------------------------------------------------


@router.post("/presigned/{bucket_name}/{key:path}")
async def generate_presigned_url(
    bucket_name: str, key: str, body: PresignedURLRequest, _user=Depends(get_current_user)
):
    """Generate a time-limited presigned URL for GET or PUT access."""
    try:
        url = _get_store().generate_presigned_url(
            bucket_name, key, method=body.method, expires_in=body.expiry_seconds
        )
    except StorageError as exc:
        return _error_response(exc)
    return _json({"url": url, "method": body.method, "expires_in": body.expiry_seconds})


# ---------------------------------------------------------------------------
# 19. GET /quotas/{tenant_id} — Get storage quota
# ---------------------------------------------------------------------------


@router.get("/quotas/{tenant_id}")
async def get_quota(tenant_id: str, _user=Depends(get_current_user)):
    """Return the storage quota and current usage for a tenant."""
    quota = _get_store().get_quota(tenant_id)
    if quota is None:
        return _json({"tenant_id": tenant_id, "quota_bytes": 0, "used_bytes": 0, "configured": False})
    return _json(
        {
            "tenant_id": tenant_id,
            "quota_bytes": quota.max_bytes,
            "used_bytes": quota.used_bytes,
            "available_bytes": quota.max_bytes - quota.used_bytes,
            "configured": True,
        }
    )


# ---------------------------------------------------------------------------
# 20. POST /quotas/{tenant_id} — Set storage quota
# ---------------------------------------------------------------------------


@router.post("/quotas/{tenant_id}")
async def set_quota(tenant_id: str, body: QuotaRequest, current_user=Depends(get_current_user)):
    """Set or update the storage quota for a tenant."""
    _require_admin(current_user)
    _get_store().set_quota(tenant_id, body.quota_bytes)
    return _json(
        {
            "tenant_id": tenant_id,
            "quota_bytes": body.quota_bytes,
            "message": "Quota updated",
        },
        status=201,
    )
