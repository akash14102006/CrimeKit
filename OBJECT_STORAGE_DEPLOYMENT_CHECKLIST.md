# CRIMEKIT OBJECT STORAGE DEPLOYMENT CHECKLIST
**Document Version:** 1.0.0  
**Target Storage Engine:** AWS S3 (or S3-compatible MinIO for development)  
**Client Library:** `boto3` 1.34.0 / `botocore` 1.34.0  

---

## 1. Required Production S3 Buckets

CrimeKit divides its evidentiary and generated assets across 5 dedicated buckets:

| Bucket Name | Purpose | Retention / WORM Mode | Encryption |
|---|---|---|---|
| `crimekit-evidence-prod` | Raw disk images (E01/RAW), CCTV videos, mobile dumps | S3 Object Lock: **COMPLIANCE (7 Years)** | SSE-KMS |
| `crimekit-documents-prod`| Extracted documents, OCR text streams, PDFs | S3 Versioning Enabled | SSE-KMS |
| `crimekit-court-reports-prod`| Generated court-ready PDF audit reports | S3 Object Lock: **COMPLIANCE (7 Years)** | SSE-KMS |
| `crimekit-ai-outputs-prod`| Extracted face crops, thumbnails, vector buffers | Standard Lifecycle (90 days transition) | SSE-S3 |
| `crimekit-backups-prod` | Database dumps and system state snapshots | Standard Lifecycle (30 days purge) | SSE-KMS |

---

## 2. Forensic Integrity & S3 Object Lock (WORM)

* **Object Lock Mode:** `COMPLIANCE` (preventing even the AWS root account from deleting or altering evidence until retention expires).
* **Legal Hold Capability:** Handled via `backend/app/storage/__init__.py:87` (`LegalHold(enabled=True)`).
* **Integrity Validation:** SHA-256 is computed client-side or during streaming upload; compared against `s3_client.head_object()` metadata and recorded in the immutable `chain_of_custody` database table.

---

## 3. Presigned URLs & Security

* **Uploads:** Multi-part presigned URLs generated via `storage.generate_presigned_upload_url()` with a default TTL of 3600 seconds.
* **Downloads:** Presigned download URLs generated via `storage.generate_presigned_download_url()` with a default TTL of 900 seconds.
* **Network Isolation:** Public access strictly blocked (`BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets` set to `True`). Access allowed ONLY via IAM Roles from backend tasks and VPC Gateway Endpoints (`com.amazonaws.ap-south-1.s3`).
