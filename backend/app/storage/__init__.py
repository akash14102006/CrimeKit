"""Enterprise object storage module wrapping MinIO/boto3."""

from __future__ import annotations

import hashlib
import io
import logging
import time
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

__all__ = [
    "StorageError",
    "BucketNotFoundError",
    "QuotaExceededError",
    "ChecksumMismatchError",
    "ObjectLockMode",
    "BucketPolicy",
    "LifecyclePolicy",
    "RetentionPolicy",
    "EnterpriseObjectStore",
]

ObjectLockMode = Literal["COMPLIANCE", "GOVERNANCE"]
SSEType = Literal["S3", "KMS"]
ChecksumAlgorithm = Literal["SHA256", "CRC32"]


class StorageError(Exception):
    def __init__(self, message: str, code: str = "STORAGE_ERROR", status: int = 500):
        super().__init__(message)
        self.code = code
        self.status = status


class BucketNotFoundError(StorageError):
    def __init__(self, bucket: str):
        super().__init__(f"Bucket not found: {bucket}", "BUCKET_NOT_FOUND", 404)


class QuotaExceededError(StorageError):
    def __init__(self, tenant_id: str, quota_bytes: int):
        super().__init__(
            f"Storage quota exceeded for tenant {tenant_id} (limit: {quota_bytes} bytes)",
            "QUOTA_EXCEEDED",
            413,
        )


class ChecksumMismatchError(StorageError):
    def __init__(self, expected: str, actual: str):
        super().__init__(
            f"Checksum mismatch: expected {expected}, got {actual}",
            "CHECKSUM_MISMATCH",
            422,
        )


def _translate_client_error(
    exc: ClientError, default_code: str = "STORAGE_ERROR", default_status: int = 500
) -> StorageError:
    error_info = exc.response.get("Error", {}) if hasattr(exc, "response") else {}
    code = error_info.get("Code", default_code)
    message = error_info.get("Message", str(exc))
    status_code = (
        exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode", default_status)
        if hasattr(exc, "response")
        else default_status
    )
    if code in ("NoSuchBucket", "NotFound") and "bucket" in message.lower():
        return BucketNotFoundError(message)
    if code in ("NoSuchKey", "NotFound"):
        status_code = 404
    elif code in ("AccessDenied", "Forbidden"):
        status_code = 403
    elif code == "BucketAlreadyExists":
        status_code = 409
    return StorageError(message=message, code=code, status=status_code)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BucketPolicy:
    versioning_enabled: bool = False
    object_lock_enabled: bool = False
    object_lock_mode: ObjectLockMode = "COMPLIANCE"
    object_lock_days: int | None = None
    object_lock_years: int | None = None
    immutable: bool = False
    default_encryption: SSEType = "S3"
    kms_key_id: str | None = None
    lifecycle_rules: list[dict[str, Any]] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ObjectVersion:
    version_id: str
    etag: str
    size: int
    last_modified: datetime
    is_latest: bool
    delete_marker: bool = False
    storage_class: str = "STANDARD"


@dataclass(frozen=True)
class LegalHold:
    enabled: bool


@dataclass(frozen=True)
class RetentionPolicy:
    mode: ObjectLockMode
    days: int | None = None
    years: int | None = None
    retain_until: datetime | None = None

    def validate(self) -> None:
        if self.days is None and self.years is None:
            raise StorageError("Retention policy requires days or years", "INVALID_RETENTION", 400)
        if self.days is not None and self.years is not None:
            raise StorageError("Specify either days or years, not both", "INVALID_RETENTION", 400)

    def compute_retain_until(self) -> datetime:
        if self.retain_until is not None:
            return self.retain_until
        now = datetime.now(timezone.utc)
        if self.days is not None:
            return now + timedelta(days=self.days)
        return now + timedelta(days=self.years * 365)  # type: ignore[union-attr]


@dataclass(frozen=True)
class LifecyclePolicy:
    transitions: list[dict[str, Any]] = field(default_factory=list)
    expiration_days: int | None = None
    noncurrent_expiration_days: int | None = None
    abort_incomplete_multipart_days: int | None = None

    def to_rule(self, rule_id: str, prefix: str = "") -> dict[str, Any]:
        rule: dict[str, Any] = {"ID": rule_id, "Status": "Enabled"}
        filter_entry: dict[str, Any] = {}
        if prefix:
            filter_entry["Prefix"] = prefix
        if filter_entry:
            rule["Filter"] = filter_entry
        actions: list[dict[str, Any]] = []
        for t in self.transitions:
            action: dict[str, Any] = {"Transitions": [t]}
            actions.append(action)
        if self.expiration_days is not None:
            actions.append({"Expiration": {"Days": self.expiration_days}})
        if self.noncurrent_expiration_days is not None:
            actions.append(
                {"NoncurrentVersionExpiration": {"NoncurrentDays": self.noncurrent_expiration_days}}
            )
        if self.abort_incomplete_multipart_days is not None:
            actions.append(
                {"AbortIncompleteMultipartUpload": {"DaysAfterInitiation": self.abort_incomplete_multipart_days}}
            )
        rule["AbortIncompleteMultipartUpload"] = (
            {"DaysAfterInitiation": self.abort_incomplete_multipart_days}
            if self.abort_incomplete_multipart_days is not None
            else {}
        )
        if actions:
            rule["Transitions"] = self.transitions
            if self.expiration_days is not None:
                rule["Expiration"] = {"Days": self.expiration_days}
            if self.noncurrent_expiration_days is not None:
                rule["NoncurrentVersionExpiration"] = {"NoncurrentDays": self.noncurrent_expiration_days}
        return rule


@dataclass(frozen=True)
class ChecksumValidator:
    algorithm: ChecksumAlgorithm = "SHA256"

    def compute(self, data: bytes) -> str:
        if self.algorithm == "SHA256":
            return hashlib.sha256(data).hexdigest()
        if self.algorithm == "CRC32":
            import zlib
            return format(zlib.crc32(data) & 0xFFFFFFFF, "08x")
        raise StorageError(f"Unsupported algorithm: {self.algorithm}", "INVALID_ALGORITHM", 400)

    def verify(self, data: bytes, expected: str) -> bool:
        actual = self.compute(data)
        if actual.lower() != expected.lower():
            raise ChecksumMismatchError(expected, actual)
        return True


@dataclass(frozen=True)
class SignedURLGenerator:
    expiry_seconds: int = 3600

    def generate(
        self,
        client: Any,
        bucket: str,
        key: str,
        method: str = "GET",
        expiry: int | None = None,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        expires = expiry or self.expiry_seconds
        params: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if content_type:
            params["ContentType"] = content_type
        if metadata:
            params["Metadata"] = metadata
        return client.generate_presigned_url(
            "get_object" if method.upper() == "GET" else "put_object",
            Params=params,
            ExpiresIn=expires,
        )


# ---------------------------------------------------------------------------
# Tenant quota tracking
# ---------------------------------------------------------------------------

@dataclass
class _TenantQuota:
    tenant_id: str
    max_bytes: int
    used_bytes: int = 0

    def check(self, additional: int) -> None:
        if self.used_bytes + additional > self.max_bytes:
            raise QuotaExceededError(self.tenant_id, self.max_bytes)

    def add(self, size: int) -> None:
        self.used_bytes += size

    def remove(self, size: int) -> None:
        self.used_bytes = max(0, self.used_bytes - size)


# ---------------------------------------------------------------------------
# Main store
# ---------------------------------------------------------------------------

class EnterpriseObjectStore:
    """Thin wrapper around boto3 S3 providing enterprise features."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region: str = "us-east-1",
        default_checksum: ChecksumAlgorithm = "SHA256",
        multipart_threshold: int = 8 * 1024 * 1024,
        multipart_chunksize: int = 8 * 1024 * 1024,
        max_concurrency: int = 10,
        **kwargs: Any,
    ):
        self._config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            retries={"max_attempts": 5, "mode": "adaptive"},
            connect_timeout=10,
            read_timeout=300,
            max_pool_connections=20,
        )
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=self._config,
        )
        self._resource = boto3.resource(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=self._config,
        )
        self._checksum = ChecksumValidator(default_checksum)
        self._multipart_threshold = multipart_threshold
        self._multipart_chunksize = multipart_chunksize
        self._max_concurrency = max_concurrency
        self._quotas: dict[str, _TenantQuota] = {}

    @property
    def client(self) -> Any:
        return self._client

    @property
    def resource(self) -> Any:
        return self._resource

    # ----- quota management -----

    def set_quota(self, tenant_id: str, max_bytes: int) -> None:
        self._quotas[tenant_id] = _TenantQuota(tenant_id=tenant_id, max_bytes=max_bytes)

    def get_quota(self, tenant_id: str) -> _TenantQuota | None:
        return self._quotas.get(tenant_id)

    def remove_quota(self, tenant_id: str) -> None:
        self._quotas.pop(tenant_id, None)

    def _enforce_quota(self, tenant_id: str | None, size: int) -> None:
        if tenant_id and tenant_id in self._quotas:
            self._quotas[tenant_id].check(size)

    def _record_usage(self, tenant_id: str | None, size: int) -> None:
        if tenant_id and tenant_id in self._quotas:
            self._quotas[tenant_id].add(size)

    def _release_usage(self, tenant_id: str | None, size: int) -> None:
        if tenant_id and tenant_id in self._quotas:
            self._quotas[tenant_id].remove(size)

    # ----- bucket operations -----

    def create_bucket(self, bucket: str, policy: BucketPolicy | None = None) -> None:
        creation_args: dict[str, Any] = {"Bucket": bucket}
        if self._client.meta.region_name and self._client.meta.region_name != "us-east-1":
            creation_args["CreateBucketConfiguration"] = {
                "LocationConstraint": self._client.meta.region_name,
            }

        try:
            self._client.create_bucket(**creation_args)
        except ClientError as exc:
            code = exc.response["Error"].get("Code", "")
            if code != "BucketAlreadyOwnedByYou":
                raise StorageError(str(exc), "BUCKET_CREATE_FAILED", 500) from exc
            logger.info("Bucket %s already exists", bucket)

        if policy is not None:
            self._apply_bucket_policy(bucket, policy)
        logger.info("Bucket ready: %s", bucket)

    def _apply_bucket_policy(self, bucket: str, policy: BucketPolicy) -> None:
        if policy.versioning_enabled:
            self._client.put_bucket_versioning(
                Bucket=bucket,
                VersioningConfiguration={"Status": "Enabled"},
            )

        if policy.object_lock_enabled:
            self._client.put_object_lock_configuration(
                Bucket=bucket,
                ObjectLockConfiguration={
                    "ObjectLockEnabled": "Enabled",
                    "Rule": {
                        "DefaultRetention": self._build_default_retention(policy),
                    },
                },
            )

        if policy.immutable and not policy.object_lock_enabled:
            self._client.put_object_lock_configuration(
                Bucket=bucket,
                ObjectLockConfiguration={
                    "ObjectLockEnabled": "Enabled",
                    "Rule": {
                        "DefaultRetention": {
                            "Mode": "COMPLIANCE",
                            "Days": 365,
                        },
                    },
                },
            )

        enc: dict[str, Any]
        if policy.kms_key_id:
            enc = {
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "aws:kms",
                            "KMSMasterKeyID": policy.kms_key_id,
                        },
                        "BucketKeyEnabled": True,
                    }
                ]
            }
        else:
            enc = {
                "Rules": [
                    {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}},
                    {"BucketKeyEnabled": True},
                ]
            }
        self._client.put_bucket_encryption(Bucket=bucket, ServerSideEncryptionConfiguration=enc)

        if policy.lifecycle_rules:
            self._client.put_bucket_lifecycle_configuration(
                Bucket=bucket,
                LifecycleConfiguration={"Rules": policy.lifecycle_rules},
            )

        if policy.tags:
            tag_set = [{"Key": k, "Value": v} for k, v in policy.tags.items()]
            self._client.put_bucket_tagging(
                Bucket=bucket, Tagging={"TagSet": tag_set}
            )

    @staticmethod
    def _build_default_retention(policy: BucketPolicy) -> dict[str, Any]:
        ret: dict[str, Any] = {"Mode": policy.object_lock_mode}
        if policy.object_lock_days is not None:
            ret["Days"] = policy.object_lock_days
        elif policy.object_lock_years is not None:
            ret["Years"] = policy.object_lock_years
        return ret

    def delete_bucket(self, bucket: str) -> None:
        try:
            self._client.delete_bucket(Bucket=bucket)
        except ClientError as exc:
            raise StorageError(str(exc), "BUCKET_DELETE_FAILED", 500) from exc

    def bucket_exists(self, bucket: str) -> bool:
        try:
            self._client.head_bucket(Bucket=bucket)
            return True
        except ClientError:
            return False

    def get_bucket_versioning(self, bucket: str) -> dict[str, Any]:
        resp = self._client.get_bucket_versioning(Bucket=bucket)
        return resp

    def enable_versioning(self, bucket: str) -> None:
        try:
            self._client.put_bucket_versioning(
                Bucket=bucket, VersioningConfiguration={"Status": "Enabled"}
            )
        except ClientError as exc:
            raise _translate_client_error(exc, "ENABLE_VERSIONING_FAILED") from exc

    def suspend_versioning(self, bucket: str) -> None:
        try:
            self._client.put_bucket_versioning(
                Bucket=bucket, VersioningConfiguration={"Status": "Suspended"}
            )
        except ClientError as exc:
            raise _translate_client_error(exc, "SUSPEND_VERSIONING_FAILED") from exc

    # ----- object lock / retention / legal hold -----

    def put_object_retention(
        self,
        bucket: str,
        key: str,
        retention: RetentionPolicy,
        version_id: str | None = None,
    ) -> None:
        retention.validate()
        retain_until = retention.compute_retain_until()
        args: dict[str, Any] = {
            "Bucket": bucket,
            "Key": key,
            "ObjectLockRetainUntilDate": retain_until,
            "ObjectLockMode": retention.mode,
        }
        if version_id:
            args["VersionId"] = version_id
        try:
            self._client.put_object_retention(**args)
        except ClientError as exc:
            raise _translate_client_error(exc, "RETENTION_FAILED") from exc

    def get_object_retention(self, bucket: str, key: str, version_id: str | None = None) -> dict[str, Any]:
        args: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if version_id:
            args["VersionId"] = version_id
        try:
            resp = self._client.get_object_retention(**args)
            return resp.get("Retention", {})
        except ClientError as exc:
            raise _translate_client_error(exc, "GET_RETENTION_FAILED") from exc

    def put_legal_hold(self, bucket: str, key: str, status: Literal["ON", "OFF"], version_id: str | None = None) -> None:
        args: dict[str, Any] = {
            "Bucket": bucket,
            "Key": key,
            "LegalHold": {"Status": status},
        }
        if version_id:
            args["VersionId"] = version_id
        try:
            self._client.put_object_legal_hold(**args)
        except ClientError as exc:
            raise _translate_client_error(exc, "LEGAL_HOLD_FAILED") from exc

    def get_legal_hold(self, bucket: str, key: str, version_id: str | None = None) -> LegalHold:
        args: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if version_id:
            args["VersionId"] = version_id
        try:
            resp = self._client.get_object_legal_hold(**args)
            status = resp.get("LegalHold", {}).get("Status", "OFF")
            return LegalHold(enabled=status == "ON")
        except ClientError as exc:
            raise _translate_client_error(exc, "GET_LEGAL_HOLD_FAILED") from exc

    # ----- versioning queries -----

    def list_object_versions(
        self, bucket: str, prefix: str = "", max_keys: int = 1000
    ) -> list[ObjectVersion]:
        kwargs: dict[str, Any] = {"Bucket": bucket, "MaxKeys": max_keys}
        if prefix:
            kwargs["Prefix"] = prefix
        try:
            resp = self._client.list_object_versions(**kwargs)
        except ClientError as exc:
            raise _translate_client_error(exc, "LIST_VERSIONS_FAILED") from exc
        versions: list[ObjectVersion] = []
        for v in resp.get("Versions", []):
            versions.append(
                ObjectVersion(
                    version_id=v["VersionId"],
                    etag=v["ETag"],
                    size=v["Size"],
                    last_modified=v["LastModified"],
                    is_latest=v["IsLatest"],
                    storage_class=v.get("StorageClass", "STANDARD"),
                )
            )
        for dm in resp.get("DeleteMarkers", []):
            versions.append(
                ObjectVersion(
                    version_id=dm["VersionId"],
                    etag="",
                    size=0,
                    last_modified=dm["LastModified"],
                    is_latest=dm["IsLatest"],
                    delete_marker=True,
                )
            )
        return versions

    def get_current_version(self, bucket: str, key: str) -> ObjectVersion | None:
        versions = self.list_object_versions(bucket, prefix=key)
        for v in versions:
            if v.is_latest:
                return v
        return None

    # ----- upload / download -----

    def upload_object(
        self,
        bucket: str,
        key: str,
        data: bytes | io.IOBase | str,
        tenant_id: str | None = None,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
        encryption: SSEType | None = None,
        kms_key_id: str | None = None,
        checksum: ChecksumAlgorithm | None = None,
        object_lock_mode: ObjectLockMode | None = None,
        object_lock_retain_until: datetime | None = None,
        legal_hold: bool | None = None,
    ) -> dict[str, Any]:
        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(data, bytes):
            size = len(data)
        else:
            data_bytes = data.read()
            size = len(data_bytes)
            data = data_bytes

        self._enforce_quota(tenant_id, size)

        args: dict[str, Any] = {
            "Bucket": bucket,
            "Key": key,
            "Body": data,
            "ContentType": content_type,
        }
        if metadata:
            args["Metadata"] = metadata

        if encryption == "KMS" or kms_key_id:
            args["ServerSideEncryption"] = "aws:kms"
            if kms_key_id:
                args["SSEKMSKeyId"] = kms_key_id
        elif encryption == "S3":
            args["ServerSideEncryption"] = "AES256"

        algo = checksum or self._checksum.algorithm
        if algo == "SHA256":
            args["ChecksumAlgorithm"] = "SHA256"
        elif algo == "CRC32":
            args["ChecksumAlgorithm"] = "CRC32"

        if object_lock_mode and object_lock_retain_until:
            args["ObjectLockMode"] = object_lock_mode
            args["ObjectLockRetainUntilDate"] = object_lock_retain_until
        if legal_hold is not None:
            args["ObjectLockLegalHoldStatus"] = "ON" if legal_hold else "OFF"

        try:
            resp = self._client.put_object(**args)
        except ClientError as exc:
            raise StorageError(str(exc), "UPLOAD_FAILED", 500) from exc

        self._record_usage(tenant_id, size)

        return {
            "bucket": bucket,
            "key": key,
            "etag": resp.get("ETag", ""),
            "version_id": resp.get("VersionId"),
            "checksum_sha256": resp.get("ChecksumSHA256"),
            "checksum_crc32": resp.get("ChecksumCRC32"),
            "size": size,
            "encryption": encryption,
            "server_side_encryption": resp.get("ServerSideEncryption"),
        }

    def upload_multipart(
        self,
        bucket: str,
        key: str,
        data: bytes,
        tenant_id: str | None = None,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
        encryption: SSEType | None = None,
        kms_key_id: str | None = None,
        chunk_size: int | None = None,
    ) -> dict[str, Any]:
        chunk = chunk_size or self._multipart_chunksize
        self._enforce_quota(tenant_id, len(data))

        create_args: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if content_type:
            create_args["ContentType"] = content_type
        if metadata:
            create_args["Metadata"] = metadata
        if encryption == "KMS" or kms_key_id:
            create_args["ServerSideEncryption"] = "aws:kms"
            if kms_key_id:
                create_args["SSEKMSKeyId"] = kms_key_id
        elif encryption == "S3":
            create_args["ServerSideEncryption"] = "AES256"

        mpu = self._client.create_multipart_upload(**create_args)
        upload_id = mpu["UploadId"]

        parts: list[dict[str, Any]] = []
        part_number = 1
        offset = 0
        try:
            while offset < len(data):
                end = min(offset + chunk, len(data))
                part_data = data[offset:end]
                resp = self._client.upload_part(
                    Bucket=bucket,
                    Key=key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=part_data,
                )
                parts.append({"PartNumber": part_number, "ETag": resp["ETag"]})
                part_number += 1
                offset = end

            result = self._client.complete_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
        except Exception:
            self._client.abort_multipart_upload(
                Bucket=bucket, Key=key, UploadId=upload_id
            )
            raise

        self._record_usage(tenant_id, len(data))

        return {
            "bucket": bucket,
            "key": key,
            "upload_id": upload_id,
            "etag": result.get("ETag"),
            "version_id": result.get("VersionId"),
            "location": result.get("Location"),
            "size": len(data),
        }

    def abort_multipart(self, bucket: str, key: str, upload_id: str) -> None:
        self._client.abort_multipart_upload(Bucket=bucket, Key=key, UploadId=upload_id)

    def list_multipart_uploads(self, bucket: str) -> list[dict[str, Any]]:
        resp = self._client.list_multipart_uploads(Bucket=bucket)
        return resp.get("Uploads", [])

    def download_object(
        self,
        bucket: str,
        key: str,
        version_id: str | None = None,
        range_header: str | None = None,
    ) -> bytes:
        args: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if version_id:
            args["VersionId"] = version_id
        if range_header:
            args["Range"] = range_header
        try:
            resp = self._client.get_object(**args)
            body = resp["Body"].read()
            return body
        except ClientError as exc:
            raise _translate_client_error(exc, "DOWNLOAD_FAILED") from exc

    def download_to_file(
        self,
        bucket: str,
        key: str,
        file_path: str,
        version_id: str | None = None,
    ) -> dict[str, Any]:
        args: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if version_id:
            args["VersionId"] = version_id
        self._client.download_fileobj(bucket, key, open(file_path, "wb"), Config=self._config)
        return {"bucket": bucket, "key": key, "file_path": file_path}

    def upload_file(
        self,
        bucket: str,
        key: str,
        file_path: str,
        tenant_id: str | None = None,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        import os
        size = os.path.getsize(file_path)
        self._enforce_quota(tenant_id, size)

        extra_args: dict[str, Any] = {"ContentType": content_type}
        if metadata:
            extra_args["Metadata"] = metadata

        self._client.upload_file(file_path, bucket, key, ExtraArgs=extra_args)
        self._record_usage(tenant_id, size)

        return {"bucket": bucket, "key": key, "size": size}

    # ----- object metadata -----

    def head_object(self, bucket: str, key: str, version_id: str | None = None) -> dict[str, Any]:
        args: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if version_id:
            args["VersionId"] = version_id
        try:
            resp = self._client.head_object(**args)
        except ClientError as exc:
            raise _translate_client_error(exc, "HEAD_OBJECT_FAILED") from exc
        return {
            "content_length": resp.get("ContentLength"),
            "content_type": resp.get("ContentType"),
            "etag": resp.get("ETag"),
            "last_modified": resp.get("LastModified"),
            "metadata": resp.get("Metadata", {}),
            "version_id": resp.get("VersionId"),
            "server_side_encryption": resp.get("ServerSideEncryption"),
            "storage_class": resp.get("StorageClass"),
            "object_lock_mode": resp.get("ObjectLockMode"),
            "object_lock_retain_until_date": resp.get("ObjectLockRetainUntilDate"),
            "object_lock_legal_hold_status": resp.get("ObjectLockLegalHoldStatus"),
            "checksum_sha256": resp.get("ChecksumSHA256"),
            "checksum_crc32": resp.get("ChecksumCRC32"),
        }

    def object_exists(self, bucket: str, key: str) -> bool:
        try:
            self._client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False

    # ----- listing / deletion -----

    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000,
        continuation_token: str | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "Bucket": bucket,
            "MaxKeys": max_keys,
        }
        if prefix:
            kwargs["Prefix"] = prefix
        if continuation_token:
            kwargs["ContinuationToken"] = continuation_token
        resp = self._client.list_objects_v2(**kwargs)
        contents = [
            {
                "key": o["Key"],
                "size": o["Size"],
                "etag": o["ETag"],
                "last_modified": o["LastModified"],
                "storage_class": o.get("StorageClass", "STANDARD"),
            }
            for o in resp.get("Contents", [])
        ]
        return {
            "objects": contents,
            "is_truncated": resp.get("IsTruncated", False),
            "continuation_token": resp.get("NextContinuationToken"),
            "key_count": resp.get("KeyCount", 0),
        }

    def delete_object(self, bucket: str, key: str, version_id: str | None = None) -> None:
        args: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if version_id:
            args["VersionId"] = version_id
        try:
            self._client.delete_object(**args)
        except ClientError as exc:
            raise _translate_client_error(exc, "DELETE_OBJECT_FAILED") from exc

    def delete_objects(self, bucket: str, keys: list[tuple[str, str | None]]) -> dict[str, Any]:
        delete_list: list[dict[str, Any]] = []
        for key, version_id in keys:
            entry: dict[str, Any] = {"Key": key}
            if version_id:
                entry["VersionId"] = version_id
            delete_list.append(entry)

        resp = self._client.delete_objects(
            Bucket=bucket,
            Delete={"Objects": delete_list, "Quiet": True},
        )
        errors = resp.get("Errors", [])
        return {"deleted": len(delete_list) - len(errors), "errors": errors}

    def restore_object(
        self,
        bucket: str,
        key: str,
        days: int = 1,
        tier: str = "STANDARD",
    ) -> dict[str, Any]:
        resp = self._client.restore_object(
            Bucket=bucket,
            Key=key,
            RestoreRequest={
                "Days": days,
                "GlacierJobParameters": {"Tier": tier},
            },
        )
        return {"status": resp.get("ResponseMetadata", {}).get("HTTPStatusCode")}

    def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
        source_version_id: str | None = None,
    ) -> dict[str, Any]:
        copy_source = f"/{source_bucket}/{source_key}"
        if source_version_id:
            copy_source += f"?versionId={source_version_id}"
        resp = self._client.copy_object(
            Bucket=dest_bucket,
            Key=dest_key,
            CopySource=urllib.parse.quote(copy_source, safe="/?="),
        )
        return {
            "etag": resp.get("CopyObjectResult", {}).get("ETag"),
            "version_id": resp.get("VersionId"),
        }

    # ----- signed URLs -----

    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        method: str = "GET",
        expires_in: int = 3600,
        content_type: str | None = None,
        version_id: str | None = None,
    ) -> str:
        generator = SignedURLGenerator(expiry_seconds=expires_in)
        params: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if content_type:
            params["ContentType"] = content_type
        if version_id:
            params["VersionId"] = version_id

        op = "get_object" if method.upper() == "GET" else "put_object"
        try:
            return self._client.generate_presigned_url(
                op, Params=params, ExpiresIn=expires_in
            )
        except ClientError as exc:
            raise _translate_client_error(exc, "PRESIGNED_URL_FAILED") from exc

    def generate_presigned_upload(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> dict[str, str]:
        params: dict[str, Any] = {
            "Bucket": bucket,
            "Key": key,
            "ContentType": content_type,
        }
        if metadata:
            params["Metadata"] = metadata
        url = self._client.generate_presigned_url(
            "put_object", Params=params, ExpiresIn=expires_in
        )
        return {"url": url, "method": "PUT", "content_type": content_type}

    def generate_presigned_download(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        version_id: str | None = None,
    ) -> str:
        params: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if version_id:
            params["VersionId"] = version_id
        return self._client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=expires_in
        )

    # ----- lifecycle management -----

    def put_lifecycle_policy(self, bucket: str, policy: LifecyclePolicy, rule_id: str = "default", prefix: str = "") -> None:
        rule = policy.to_rule(rule_id, prefix)
        try:
            resp = self._client.get_bucket_lifecycle_configuration(Bucket=bucket)
            rules = resp.get("Rules", [])
        except ClientError:
            rules = []

        rules = [r for r in rules if r.get("ID") != rule_id]
        rules.append(rule)
        self._client.put_bucket_lifecycle_configuration(
            Bucket=bucket, LifecycleConfiguration={"Rules": rules}
        )

    def get_lifecycle_policy(self, bucket: str) -> list[dict[str, Any]]:
        try:
            resp = self._client.get_bucket_lifecycle_configuration(Bucket=bucket)
            return resp.get("Rules", [])
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchLifecycleConfiguration":
                return []
            raise

    def delete_lifecycle_policy(self, bucket: str) -> None:
        self._client.delete_bucket_lifecycle_configuration(Bucket=bucket)

    # ----- encryption config -----

    def put_encryption(self, bucket: str, sse_type: SSEType = "S3", kms_key_id: str | None = None) -> None:
        enc: dict[str, Any]
        if sse_type == "KMS" or kms_key_id:
            enc = {
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "aws:kms",
                            **({"KMSMasterKeyID": kms_key_id} if kms_key_id else {}),
                        },
                        "BucketKeyEnabled": True,
                    }
                ]
            }
        else:
            enc = {
                "Rules": [
                    {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}},
                    {"BucketKeyEnabled": True},
                ]
            }
        self._client.put_bucket_encryption(
            Bucket=bucket, ServerSideEncryptionConfiguration=enc
        )

    # ----- tags -----

    def put_object_tags(self, bucket: str, key: str, tags: dict[str, str], version_id: str | None = None) -> None:
        tag_str = "&".join(f"{k}={v}" for k, v in tags.items())
        args: dict[str, Any] = {"Bucket": bucket, "Key": key, "Tagging": {"TagSet": [{"Key": k, "Value": v} for k, v in tags.items()]}}
        if version_id:
            args["VersionId"] = version_id
        self._client.put_object_tagging(**args)

    def get_object_tags(self, bucket: str, key: str, version_id: str | None = None) -> dict[str, str]:
        args: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if version_id:
            args["VersionId"] = version_id
        resp = self._client.get_object_tagging(**args)
        return {t["Key"]: t["Value"] for t in resp.get("TagSet", [])}

    # ----- bucket tags -----

    def put_bucket_tags(self, bucket: str, tags: dict[str, str]) -> None:
        tag_set = [{"Key": k, "Value": v} for k, v in tags.items()]
        self._client.put_bucket_tagging(
            Bucket=bucket, Tagging={"TagSet": tag_set}
        )

    def get_bucket_tags(self, bucket: str) -> dict[str, str]:
        try:
            resp = self._client.get_bucket_tagging(Bucket=bucket)
            return {t["Key"]: t["Value"] for t in resp.get("TagSet", [])}
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchTagSet":
                return {}
            raise

    # ----- presigned policy upload (browser) -----

    def generate_presigned_post(
        self,
        bucket: str,
        key: str,
        content_type: str = "application/octet-stream",
        expires_in: int = 3600,
        max_size_bytes: int = 100 * 1024 * 1024,
    ) -> dict[str, Any]:
        fields = {"Content-Type": content_type}
        conditions = [
            {"Content-Type": content_type},
            ["content-length-range", 1, max_size_bytes],
        ]
        resp = self._client.generate_presigned_post(
            Bucket=bucket,
            Key=key,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expires_in,
        )
        return {"url": resp["url"], "fields": resp["fields"]}

    # ----- presigned URL for evidence sharing -----

    def generate_evidence_share_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        download_filename: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"Bucket": bucket, "Key": key}
        if download_filename:
            params["ResponseContentDisposition"] = f'attachment; filename="{download_filename}"'
        url = self._client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=expires_in
        )
        return {
            "url": url,
            "expires_in": expires_in,
            "key": key,
            "bucket": bucket,
            "download_filename": download_filename,
        }

    # ----- server-side copy / move -----

    def move_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
    ) -> dict[str, Any]:
        result = self.copy_object(source_bucket, source_key, dest_bucket, dest_key)
        self.delete_object(source_bucket, source_key)
        return result
