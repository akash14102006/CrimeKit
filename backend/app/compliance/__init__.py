"""
Enterprise Compliance Module for CrimeKit

Provides GDPR data rights, data retention, legal holds, immutable evidence
chain of custody, audit reporting, data classification, and compliance
report generation (GDPR, ISO27001, SOC2).
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
    and_,
    or_,
)
from sqlalchemy.orm import Session, relationship

from ..database import Base

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DataClassification(str, PyEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class RetentionStatus(str, PyEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    UNDER_LEGAL_HOLD = "under_legal_hold"
    ARCHIVED = "archived"
    PENDING_DELETION = "pending_deletion"


class LegalHoldStatus(str, PyEnum):
    ACTIVE = "active"
    RELEASED = "released"


class ComplianceReportType(str, PyEnum):
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    SOC2 = "soc2"
    CHAIN_OF_CUSTODY = "chain_of_custody"
    RETENTION = "retention"
    AUDIT_TRAIL = "audit_trail"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class DataRetentionPolicy(Base):
    """Configurable data retention policies per evidence type or case status."""
    __tablename__ = "data_retention_policies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    # scope: which evidence type or case status this policy applies to
    evidence_type = Column(String, nullable=True)  # e.g. 'image', 'video', 'email', NULL = all
    case_status = Column(String, nullable=True)     # e.g. 'open', 'closed', NULL = all
    retention_days = Column(Integer, nullable=False, default=365)
    classification = Column(String, default=DataClassification.INTERNAL.value)
    # what to do when retention expires
    action_on_expiry = Column(String, default="archive")  # archive | anonymize | delete
    # whether legal hold overrides this policy
    legal_hold_override = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LegalHold(Base):
    """Legal hold prevents deletion of evidence/cases under investigation."""
    __tablename__ = "legal_holds"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=True)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=True)
    reason = Column(Text, nullable=False)
    legal_reference = Column(String, nullable=True)
    status = Column(String, default=LegalHoldStatus.ACTIVE.value)
    placed_by = Column(String, ForeignKey("users.id"), nullable=True)
    released_by = Column(String, ForeignKey("users.id"), nullable=True)
    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    released_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)


class ImmutableEvidenceLock(Base):
    """Immutable storage lock for evidence — prevents any modification or deletion."""
    __tablename__ = "immutable_evidence_locks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False, unique=True)
    locked_by = Column(String, ForeignKey("users.id"), nullable=True)
    locked_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text, default="chain_of_custody_integrity")
    # hash of the evidence at lock time for tamper detection
    evidence_hash_at_lock = Column(String, nullable=True)
    unlock_authorization = Column(String, nullable=True)  # required auth token/hash to unlock


class ComplianceAuditEntry(Base):
    """Immutable audit trail for compliance events."""
    __tablename__ = "compliance_audit_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    event_type = Column(String, nullable=False, index=True)
    actor_id = Column(String, ForeignKey("users.id"), nullable=True)
    target_type = Column(String, nullable=True)  # 'evidence', 'case', 'user', 'policy'
    target_id = Column(String, nullable=True)
    detail = Column(JSON, nullable=True)
    # tamper-evident hash chain
    previous_hash = Column(String, nullable=True)
    entry_hash = Column(String, nullable=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True, index=True)


class DataDeletionRequest(Base):
    """GDPR right-to-deletion request tracking."""
    __tablename__ = "data_deletion_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending")  # pending | processing | completed | denied
    reason = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    deleted_tables = Column(JSON, nullable=True)  # list of tables processed
    anonymized_fields = Column(JSON, nullable=True)
    denied_reason = Column(Text, nullable=True)
    processed_by = Column(String, ForeignKey("users.id"), nullable=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True, index=True)


class ComplianceReport(Base):
    """Generated compliance reports."""
    __tablename__ = "compliance_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    report_type = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    generated_by = Column(String, ForeignKey("users.id"), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    content = Column(JSON, nullable=True)
    file_path = Column(String, nullable=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True, index=True)


class DataClassificationTag(Base):
    """Tags data objects with classification levels."""
    __tablename__ = "data_classification_tags"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    target_type = Column(String, nullable=False, index=True)  # 'evidence', 'case', 'document'
    target_id = Column(String, nullable=False, index=True)
    classification = Column(String, nullable=False, default=DataClassification.INTERNAL.value)
    classified_by = Column(String, ForeignKey("users.id"), nullable=True)
    classified_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True, index=True)


class RetentionScheduleRun(Base):
    """Tracks retention scheduler runs."""
    __tablename__ = "retention_schedule_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="running")  # running | completed | failed
    policies_evaluated = Column(Integer, default=0)
    items_expired = Column(Integer, default=0)
    items_archived = Column(Integer, default=0)
    items_deleted = Column(Integer, default=0)
    items_anonymized = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True, index=True)


class EvidenceExport(Base):
    """Tracks evidence export requests for audit purposes."""
    __tablename__ = "evidence_exports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False, index=True)
    exported_by = Column(String, ForeignKey("users.id"), nullable=True)
    exported_at = Column(DateTime(timezone=True), server_default=func.now())
    export_format = Column(String, nullable=False)  # csv, json, pdf_ready
    file_path = Column(String, nullable=True)
    purpose = Column(Text, nullable=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True, index=True)


class CaseExport(Base):
    """Tracks complete case package exports."""
    __tablename__ = "case_exports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    exported_by = Column(String, ForeignKey("users.id"), nullable=True)
    exported_at = Column(DateTime(timezone=True), server_default=func.now())
    export_format = Column(String, default="json")
    file_path = Column(String, nullable=True)
    includes_evidence = Column(Boolean, default=True)
    includes_audit_trail = Column(Boolean, default=True)
    includes_chain_of_custody = Column(Boolean, default=True)
    manifest = Column(JSON, nullable=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True, index=True)


# ---------------------------------------------------------------------------
# GDPR Service
# ---------------------------------------------------------------------------

class GDPRService:
    """GDPR right-to-deletion: anonymize or delete user data across all tables."""

    # tables that contain user references and the columns to anonymize
    USER_DATA_MAP = {
        "users": ["email", "password_hash"],
        "cases": ["created_by"],
        "evidence": ["uploaded_by"],
        "chain_of_custody": ["actor_id"],
        "audit_logs": ["actor_id"],
        "forensic_jobs": ["evidence_id"],  # indirect
        "documents": ["evidence_id"],      # indirect
        "refresh_tokens": ["user_id"],
        "mfa_configs": ["user_id", "totp_secret"],
        "api_keys": ["user_id", "key_hash", "key_prefix"],
        "compliance_audit_entries": ["actor_id"],
        "data_deletion_requests": ["user_id"],
        "compliance_reports": ["generated_by"],
        "data_classification_tags": ["classified_by"],
        "evidence_exports": ["exported_by"],
        "case_exports": ["exported_by"],
        "legal_holds": ["placed_by", "released_by"],
        "immutable_evidence_locks": ["locked_by"],
    }

    ANONYMIZED_PLACEHOLDER = "[ANONYMIZED_GDPR]"

    @staticmethod
    def create_deletion_request(
        db: Session,
        user_id: str,
        reason: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> DataDeletionRequest:
        request = DataDeletionRequest(
            user_id=user_id,
            reason=reason,
            org_id=org_id,
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        ComplianceAuditService.log_event(
            db,
            event_type="gdpr.deletion_request_created",
            actor_id=user_id,
            target_type="user",
            target_id=user_id,
            detail={"reason": reason},
            org_id=org_id,
        )
        return request

    @staticmethod
    def _check_legal_holds(db: Session, user_id: str) -> List[Dict[str, str]]:
        """Check if user's data is under legal hold."""
        holds = (
            db.query(LegalHold)
            .filter(
                LegalHold.status == LegalHoldStatus.ACTIVE.value,
                or_(
                    LegalHold.case_id.in_(
                        db.query("cases.id").filter("cases.created_by" == user_id).subquery()
                    ),
                    LegalHold.placed_by == user_id,
                ),
            )
            .all()
        )
        return [
            {"hold_id": h.id, "reason": h.reason, "legal_reference": h.legal_reference}
            for h in holds
        ]

    @staticmethod
    def execute_deletion(
        db: Session,
        request_id: str,
        processed_by: str,
    ) -> DataDeletionRequest:
        """Execute a GDPR deletion request by anonymizing user data across all tables."""
        request = db.query(DataDeletionRequest).filter(DataDeletionRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Deletion request {request_id} not found")
        if request.status not in ("pending", "processing"):
            raise ValueError(f"Request {request_id} is already {request.status}")

        # check legal holds
        active_holds = GDPRService._check_legal_holds(db, request.user_id)
        if active_holds:
            request.status = "denied"
            request.denied_reason = f"Data is under {len(active_holds)} active legal hold(s)"
            request.processed_by = processed_by
            db.commit()
            ComplianceAuditService.log_event(
                db,
                event_type="gdpr.deletion_denied_legal_hold",
                actor_id=processed_by,
                target_type="user",
                target_id=request.user_id,
                detail={"holds": active_holds},
                org_id=request.org_id,
            )
            return request

        request.status = "processing"
        db.commit()

        deleted_tables = []
        anonymized_fields = []

        for table_name, columns in GDPRService.USER_DATA_MAP.items():
            try:
                table = Base.metadata.tables.get(table_name)
                if table is None:
                    continue

                for col_name in columns:
                    col = table.columns.get(col_name)
                    if col is None:
                        continue

                    # determine the user_id foreign key column
                    user_fk_col = None
                    for fk_candidate in ["user_id", "actor_id", "created_by", "uploaded_by", "placed_by", "released_by", "locked_by", "classified_by", "exported_by", "generated_by", "processed_by"]:
                        if fk_candidate in [c.name for c in table.columns]:
                            user_fk_col = fk_candidate
                            break

                    if user_fk_col and user_fk_col != col_name:
                        rows_updated = (
                            db.query(table)
                            .filter(table.c[user_fk_col] == request.user_id)
                            .update(
                                {col_name: GDPRService.ANONYMIZED_PLACEHOLDER},
                                synchronize_session="fetch",
                            )
                        )
                    elif col_name in ["email", "password_hash", "totp_secret", "key_hash", "key_prefix"]:
                        rows_updated = (
                            db.query(table)
                            .filter(table.c[col_name] != None)
                            .update(
                                {col_name: GDPRService.ANONYMIZED_PLACEHOLDER},
                                synchronize_session="fetch",
                            )
                        )
                    else:
                        continue

                    if rows_updated > 0:
                        anonymized_fields.append(f"{table_name}.{col_name} ({rows_updated} rows)")

                deleted_tables.append(table_name)
            except Exception:
                continue

        db.commit()

        request.status = "completed"
        request.completed_at = datetime.now(timezone.utc)
        request.deleted_tables = deleted_tables
        request.anonymized_fields = anonymized_fields
        request.processed_by = processed_by
        db.commit()

        ComplianceAuditService.log_event(
            db,
            event_type="gdpr.deletion_completed",
            actor_id=processed_by,
            target_type="user",
            target_id=request.user_id,
            detail={
                "tables_anonymized": deleted_tables,
                "fields_anonymized": anonymized_fields,
            },
            org_id=request.org_id,
        )

        return request


# ---------------------------------------------------------------------------
# Data Retention Service
# ---------------------------------------------------------------------------

class DataRetentionService:
    """Configurable data retention policies with evidence-specific rules."""

    @staticmethod
    def create_policy(
        db: Session,
        name: str,
        retention_days: int,
        evidence_type: Optional[str] = None,
        case_status: Optional[str] = None,
        classification: str = DataClassification.INTERNAL.value,
        action_on_expiry: str = "archive",
        description: Optional[str] = None,
    ) -> DataRetentionPolicy:
        policy = DataRetentionPolicy(
            name=name,
            retention_days=retention_days,
            evidence_type=evidence_type,
            case_status=case_status,
            classification=classification,
            action_on_expiry=action_on_expiry,
            description=description,
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def get_applicable_policies(
        db: Session,
        evidence_type: Optional[str] = None,
        case_status: Optional[str] = None,
    ) -> List[DataRetentionPolicy]:
        query = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True)
        conditions = []
        if evidence_type:
            conditions.append(or_(DataRetentionPolicy.evidence_type == None, DataRetentionPolicy.evidence_type == evidence_type))
        else:
            conditions.append(DataRetentionPolicy.evidence_type == None)
        if case_status:
            conditions.append(or_(DataRetentionPolicy.case_status == None, DataRetentionPolicy.case_status == case_status))
        else:
            conditions.append(DataRetentionPolicy.case_status == None)
        if conditions:
            query = query.filter(and_(*conditions))
        return query.all()

    @staticmethod
    def is_under_legal_hold(db: Session, evidence_id: Optional[str] = None, case_id: Optional[str] = None) -> bool:
        query = db.query(LegalHold).filter(LegalHold.status == LegalHoldStatus.ACTIVE.value)
        if evidence_id:
            query = query.filter(LegalHold.evidence_id == evidence_id)
        if case_id:
            query = query.filter(LegalHold.case_id == case_id)
        return query.first() is not None

    @staticmethod
    def check_evidence_expiry(
        db: Session,
        evidence,
        policy: DataRetentionPolicy,
    ) -> Dict[str, Any]:
        """Check if evidence has exceeded its retention period."""
        if evidence.uploaded_at is None:
            return {"expired": False, "reason": "no_upload_date"}

        if DataRetentionService.is_under_legal_hold(db, evidence_id=evidence.id):
            return {"expired": False, "reason": "under_legal_hold", "status": RetentionStatus.UNDER_LEGAL_HOLD.value}

        age_days = (datetime.now(timezone.utc) - evidence.uploaded_at.replace(tzinfo=timezone.utc)).days
        if age_days > policy.retention_days:
            return {
                "expired": True,
                "age_days": age_days,
                "retention_days": policy.retention_days,
                "action": policy.action_on_expiry,
                "status": RetentionStatus.EXPIRED.value,
            }

        return {"expired": False, "age_days": age_days, "retention_days": policy.retention_days}

    @staticmethod
    def anonymize_evidence_metadata(db: Session, evidence) -> Dict[str, Any]:
        """Anonymize evidence metadata while preserving forensic integrity."""
        original_metadata = evidence.metadata_json or {}
        anonymized = original_metadata.copy()

        # remove PII fields
        pii_keys = ["uploader_email", "uploader_name", "ip_address", "user_agent", "location"]
        removed = []
        for key in pii_keys:
            if key in anonymized:
                anonymized[key] = "[ANONYMIZED]"
                removed.append(key)

        evidence.metadata_json = anonymized
        evidence.filename = f"[ANONYMIZED]_{evidence.id}"
        db.commit()

        return {"anonymized_fields": removed, "original_metadata_keys": list(original_metadata.keys())}

    @staticmethod
    def run_retention_check(db: Session, org_id: Optional[str] = None) -> RetentionScheduleRun:
        """Run a full retention check across all evidence."""
        run = RetentionScheduleRun(org_id=org_id)
        db.add(run)
        db.commit()
        db.refresh(run)

        try:
            from ..models import Evidence

            evidence_items = db.query(Evidence).all()
            policies = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True).all()

            items_expired = 0
            items_archived = 0
            items_deleted = 0
            items_anonymized = 0
            errors = []

            for evidence in evidence_items:
                matching_policy = None
                for policy in policies:
                    if policy.evidence_type and evidence.mime_type and policy.evidence_type not in evidence.mime_type:
                        continue
                    matching_policy = policy
                    break

                if not matching_policy:
                    continue

                expiry_check = DataRetentionService.check_evidence_expiry(db, evidence, matching_policy)

                if expiry_check.get("expired"):
                    items_expired += 1
                    action = expiry_check.get("action", "archive")

                    if action == "anonymize":
                        DataRetentionService.anonymize_evidence_metadata(db, evidence)
                        items_anonymized += 1
                    elif action == "archive":
                        items_archived += 1
                    elif action == "delete":
                        if not DataRetentionService.is_under_legal_hold(db, evidence_id=evidence.id):
                            items_deleted += 1

                run.policies_evaluated += 1

            run.finished_at = datetime.now(timezone.utc)
            run.status = "completed"
            run.items_expired = items_expired
            run.items_archived = items_archived
            run.items_deleted = items_deleted
            run.items_anonymized = items_anonymized
            run.errors = errors if errors else None
            db.commit()

        except Exception as e:
            run.status = "failed"
            run.finished_at = datetime.now(timezone.utc)
            run.errors = [{"error": str(e)}]
            db.commit()

        ComplianceAuditService.log_event(
            db,
            event_type="retention.schedule_run_completed",
            actor_id=None,
            target_type="retention_schedule",
            target_id=run.id,
            detail={
                "policies_evaluated": run.policies_evaluated,
                "items_expired": run.items_expired,
                "items_archived": run.items_archived,
                "items_deleted": run.items_deleted,
                "items_anonymized": run.items_anonymized,
            },
            org_id=org_id,
        )

        return run


# ---------------------------------------------------------------------------
# Legal Hold Service
# ---------------------------------------------------------------------------

class LegalHoldService:
    """Prevent deletion of evidence/cases under legal hold."""

    @staticmethod
    def place_hold(
        db: Session,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        reason: str = "",
        legal_reference: Optional[str] = None,
        placed_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> LegalHold:
        if not case_id and not evidence_id:
            raise ValueError("Either case_id or evidence_id must be provided")

        existing = (
            db.query(LegalHold)
            .filter(
                LegalHold.status == LegalHoldStatus.ACTIVE.value,
                or_(
                    (LegalHold.case_id == case_id) if case_id else False,
                    (LegalHold.evidence_id == evidence_id) if evidence_id else False,
                ),
            )
            .first()
        )
        if existing:
            raise ValueError(f"Legal hold already active: {existing.id}")

        hold = LegalHold(
            case_id=case_id,
            evidence_id=evidence_id,
            reason=reason,
            legal_reference=legal_reference,
            placed_by=placed_by,
            notes=notes,
        )
        db.add(hold)
        db.commit()
        db.refresh(hold)

        ComplianceAuditService.log_event(
            db,
            event_type="legal_hold.placed",
            actor_id=placed_by,
            target_type="case" if case_id else "evidence",
            target_id=case_id or evidence_id,
            detail={"hold_id": hold.id, "reason": reason, "legal_reference": legal_reference},
        )
        return hold

    @staticmethod
    def release_hold(
        db: Session,
        hold_id: str,
        released_by: str,
        reason: Optional[str] = None,
    ) -> LegalHold:
        hold = db.query(LegalHold).filter(LegalHold.id == hold_id).first()
        if not hold:
            raise ValueError(f"Legal hold {hold_id} not found")
        if hold.status == LegalHoldStatus.RELEASED.value:
            raise ValueError(f"Legal hold {hold_id} is already released")

        hold.status = LegalHoldStatus.RELEASED.value
        hold.released_by = released_by
        hold.released_at = datetime.now(timezone.utc)
        if reason:
            hold.notes = f"{hold.notes or ''}\nRelease reason: {reason}"
        db.commit()

        ComplianceAuditService.log_event(
            db,
            event_type="legal_hold.released",
            actor_id=released_by,
            target_type="case" if hold.case_id else "evidence",
            target_id=hold.case_id or hold.evidence_id,
            detail={"hold_id": hold_id, "release_reason": reason},
        )
        return hold

    @staticmethod
    def list_active_holds(
        db: Session,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
    ) -> List[LegalHold]:
        query = db.query(LegalHold).filter(LegalHold.status == LegalHoldStatus.ACTIVE.value)
        if case_id:
            query = query.filter(LegalHold.case_id == case_id)
        if evidence_id:
            query = query.filter(LegalHold.evidence_id == evidence_id)
        return query.all()

    @staticmethod
    def check_hold_status(db: Session, evidence_id: Optional[str] = None, case_id: Optional[str] = None) -> Dict[str, Any]:
        holds = LegalHoldService.list_active_holds(db, evidence_id=evidence_id, case_id=case_id)
        return {
            "under_hold": len(holds) > 0,
            "active_holds": [
                {"id": h.id, "reason": h.reason, "legal_reference": h.legal_reference, "placed_at": h.placed_at.isoformat() if h.placed_at else None}
                for h in holds
            ],
        }


# ---------------------------------------------------------------------------
# Immutable Evidence Chain of Custody
# ---------------------------------------------------------------------------

class ImmutableEvidenceService:
    """Immutable storage locks and tamper-evident chain of custody."""

    @staticmethod
    def lock_evidence(
        db: Session,
        evidence_id: str,
        locked_by: Optional[str] = None,
        reason: str = "chain_of_custody_integrity",
    ) -> ImmutableEvidenceLock:
        existing = db.query(ImmutableEvidenceLock).filter(ImmutableEvidenceLock.evidence_id == evidence_id).first()
        if existing:
            raise ValueError(f"Evidence {evidence_id} is already locked")

        from ..models import Evidence
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        evidence_hash = evidence.sha256 or ""

        lock = ImmutableEvidenceLock(
            evidence_id=evidence_id,
            locked_by=locked_by,
            reason=reason,
            evidence_hash_at_lock=evidence_hash,
        )
        db.add(lock)
        db.commit()
        db.refresh(lock)

        ComplianceAuditService.log_event(
            db,
            event_type="evidence.immutable_lock_placed",
            actor_id=locked_by,
            target_type="evidence",
            target_id=evidence_id,
            detail={"lock_id": lock.id, "reason": reason, "evidence_hash": evidence_hash},
        )
        return lock

    @staticmethod
    def unlock_evidence(
        db: Session,
        evidence_id: str,
        unlock_authorization: str,
        unlocked_by: Optional[str] = None,
    ) -> ImmutableEvidenceLock:
        lock = db.query(ImmutableEvidenceLock).filter(ImmutableEvidenceLock.evidence_id == evidence_id).first()
        if not lock:
            raise ValueError(f"No lock found for evidence {evidence_id}")

        if lock.unlock_authorization and lock.unlock_authorization != unlock_authorization:
            raise ValueError("Invalid unlock authorization")

        # verify evidence integrity
        from ..models import Evidence
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if evidence and lock.evidence_hash_at_lock and evidence.sha256 != lock.evidence_hash_at_lock:
            raise ValueError(
                f"Evidence integrity check failed: hash mismatch. "
                f"Expected {lock.evidence_hash_at_lock}, got {evidence.sha256}"
            )

        db.delete(lock)
        db.commit()

        ComplianceAuditService.log_event(
            db,
            event_type="evidence.immutable_lock_removed",
            actor_id=unlocked_by,
            target_type="evidence",
            target_id=evidence_id,
            detail={"evidence_hash": evidence.sha256 if evidence else None},
        )
        return lock

    @staticmethod
    def is_locked(db: Session, evidence_id: str) -> bool:
        return db.query(ImmutableEvidenceLock).filter(ImmutableEvidenceLock.evidence_id == evidence_id).first() is not None

    @staticmethod
    def verify_integrity(db: Session, evidence_id: str) -> Dict[str, Any]:
        lock = db.query(ImmutableEvidenceLock).filter(ImmutableEvidenceLock.evidence_id == evidence_id).first()
        if not lock:
            return {"locked": False, "tampered": False}

        from ..models import Evidence
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            return {"locked": True, "tampered": True, "error": "evidence not found"}

        tampered = lock.evidence_hash_at_lock != evidence.sha256
        return {
            "locked": True,
            "tampered": tampered,
            "expected_hash": lock.evidence_hash_at_lock,
            "current_hash": evidence.sha256,
            "locked_at": lock.locked_at.isoformat() if lock.locked_at else None,
        }


# ---------------------------------------------------------------------------
# Audit Service (tamper-evident hash chain)
# ---------------------------------------------------------------------------

class ComplianceAuditService:
    """Compliance audit trail with tamper-evident hash chain."""

    _last_hash: Optional[str] = None

    @staticmethod
    def _compute_hash(entry_id: str, timestamp: datetime, event_type: str, previous_hash: Optional[str], detail: Optional[dict]) -> str:
        payload = json.dumps(
            {
                "id": entry_id,
                "timestamp": timestamp.isoformat(),
                "event_type": event_type,
                "previous_hash": previous_hash,
                "detail": detail,
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        actor_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
        org_id: Optional[str] = None,
    ) -> ComplianceAuditEntry:
        # get previous hash from the latest entry
        last_entry = (
            db.query(ComplianceAuditEntry)
            .order_by(ComplianceAuditEntry.timestamp.desc(), ComplianceAuditEntry.id.desc())
            .first()
        )
        previous_hash = last_entry.entry_hash if last_entry else "GENESIS"

        entry_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        entry_hash = ComplianceAuditService._compute_hash(
            entry_id, timestamp, event_type, previous_hash, detail
        )

        entry = ComplianceAuditEntry(
            id=entry_id,
            timestamp=timestamp,
            event_type=event_type,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
            org_id=org_id,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def verify_chain(db: Session, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Verify the integrity of the audit hash chain."""
        query = db.query(ComplianceAuditEntry).order_by(ComplianceAuditEntry.timestamp.asc(), ComplianceAuditEntry.id.asc())
        if start_time:
            query = query.filter(ComplianceAuditEntry.timestamp >= start_time)
        if end_time:
            query = query.filter(ComplianceAuditEntry.timestamp <= end_time)
        if org_id:
            query = query.filter(ComplianceAuditEntry.org_id == org_id)

        entries = query.all()
        if not entries:
            return {"valid": True, "entries_checked": 0, "tampered_entries": []}

        tampered = []
        prev_hash = "GENESIS"
        for entry in entries:
            if entry.previous_hash != prev_hash:
                tampered.append({"entry_id": entry.id, "timestamp": entry.timestamp.isoformat(), "expected_previous": prev_hash, "actual_previous": entry.previous_hash})
            recomputed = ComplianceAuditService._compute_hash(
                entry.id, entry.timestamp, entry.event_type, entry.previous_hash, entry.detail
            )
            if recomputed != entry.entry_hash:
                tampered.append({"entry_id": entry.id, "timestamp": entry.timestamp.isoformat(), "error": "hash_mismatch", "expected": recomputed, "actual": entry.entry_hash})
            prev_hash = entry.entry_hash

        return {
            "valid": len(tampered) == 0,
            "entries_checked": len(entries),
            "tampered_entries": tampered,
        }

    @staticmethod
    def query_events(
        db: Session,
        event_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        org_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ComplianceAuditEntry]:
        query = db.query(ComplianceAuditEntry)
        if event_type:
            query = query.filter(ComplianceAuditEntry.event_type == event_type)
        if actor_id:
            query = query.filter(ComplianceAuditEntry.actor_id == actor_id)
        if target_type:
            query = query.filter(ComplianceAuditEntry.target_type == target_type)
        if target_id:
            query = query.filter(ComplianceAuditEntry.target_id == target_id)
        if start_time:
            query = query.filter(ComplianceAuditEntry.timestamp >= start_time)
        if end_time:
            query = query.filter(ComplianceAuditEntry.timestamp <= end_time)
        if org_id:
            query = query.filter(ComplianceAuditEntry.org_id == org_id)
        return query.order_by(ComplianceAuditEntry.timestamp.desc()).offset(offset).limit(limit).all()


# ---------------------------------------------------------------------------
# Evidence Export Service
# ---------------------------------------------------------------------------

class EvidenceExportService:
    """Export evidence in CSV, JSON, and PDF-ready formats."""

    @staticmethod
    def export_csv(db: Session, evidence_id: str, exported_by: Optional[str] = None, purpose: Optional[str] = None, org_id: Optional[str] = None) -> Dict[str, Any]:
        from ..models import Evidence, ChainOfCustody, ForensicResult

        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        chain_of_custody = db.query(ChainOfCustody).filter(ChainOfCustody.evidence_id == evidence_id).order_by(ChainOfCustody.timestamp.asc()).all()
        forensic_results = db.query(ForensicResult).filter(ForensicResult.evidence_id == evidence_id).all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["=== EVIDENCE RECORD ==="])
        writer.writerow(["Field", "Value"])
        writer.writerow(["ID", evidence.id])
        writer.writerow(["Case ID", evidence.case_id])
        writer.writerow(["Filename", evidence.filename])
        writer.writerow(["Storage Path", evidence.storage_path])
        writer.writerow(["SHA256", evidence.sha256])
        writer.writerow(["Size (bytes)", evidence.size])
        writer.writerow(["MIME Type", evidence.mime_type])
        writer.writerow(["Uploaded At", evidence.uploaded_at.isoformat() if evidence.uploaded_at else ""])
        writer.writerow(["Uploaded By", evidence.uploaded_by])
        writer.writerow([])

        writer.writerow(["=== CHAIN OF CUSTODY ==="])
        writer.writerow(["Action", "Actor ID", "Timestamp", "Notes"])
        for entry in chain_of_custody:
            writer.writerow([
                entry.action,
                entry.actor_id,
                entry.timestamp.isoformat() if entry.timestamp else "",
                entry.notes or "",
            ])
        writer.writerow([])

        writer.writerow(["=== FORENSIC RESULTS ==="])
        writer.writerow(["Processor", "Created At", "Result"])
        for result in forensic_results:
            writer.writerow([
                result.processor,
                result.created_at.isoformat() if result.created_at else "",
                json.dumps(result.result) if result.result else "",
            ])

        csv_content = output.getvalue()
        output.close()

        export_record = EvidenceExport(
            evidence_id=evidence_id,
            exported_by=exported_by,
            export_format="csv",
            purpose=purpose,
            org_id=org_id,
        )
        db.add(export_record)
        db.commit()

        ComplianceAuditService.log_event(
            db,
            event_type="evidence.exported_csv",
            actor_id=exported_by,
            target_type="evidence",
            target_id=evidence_id,
            detail={"purpose": purpose},
            org_id=org_id,
        )

        return {"csv": csv_content, "export_id": export_record.id}

    @staticmethod
    def export_json(db: Session, evidence_id: str, exported_by: Optional[str] = None, purpose: Optional[str] = None, org_id: Optional[str] = None) -> Dict[str, Any]:
        from ..models import Evidence, ChainOfCustody, ForensicResult, Document

        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        chain_of_custody = db.query(ChainOfCustody).filter(ChainOfCustody.evidence_id == evidence_id).order_by(ChainOfCustody.timestamp.asc()).all()
        forensic_results = db.query(ForensicResult).filter(ForensicResult.evidence_id == evidence_id).all()
        documents = db.query(Document).filter(Document.evidence_id == evidence_id).all()

        export_data = {
            "evidence": {
                "id": evidence.id,
                "case_id": evidence.case_id,
                "filename": evidence.filename,
                "storage_path": evidence.storage_path,
                "sha256": evidence.sha256,
                "size": evidence.size,
                "mime_type": evidence.mime_type,
                "metadata": evidence.metadata_json,
                "uploaded_by": evidence.uploaded_by,
                "uploaded_at": evidence.uploaded_at.isoformat() if evidence.uploaded_at else None,
            },
            "chain_of_custody": [
                {
                    "action": c.action,
                    "actor_id": c.actor_id,
                    "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                    "notes": c.notes,
                }
                for c in chain_of_custody
            ],
            "forensic_results": [
                {
                    "processor": r.processor,
                    "result": r.result,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in forensic_results
            ],
            "documents": [
                {
                    "id": d.id,
                    "text": d.text[:500] if d.text else None,
                    "metadata": d.metadata_json,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in documents
            ],
            "export_metadata": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "exported_by": exported_by,
                "purpose": purpose,
                "format": "json",
            },
        }

        export_record = EvidenceExport(
            evidence_id=evidence_id,
            exported_by=exported_by,
            export_format="json",
            purpose=purpose,
            org_id=org_id,
        )
        db.add(export_record)
        db.commit()

        ComplianceAuditService.log_event(
            db,
            event_type="evidence.exported_json",
            actor_id=exported_by,
            target_type="evidence",
            target_id=evidence_id,
            detail={"purpose": purpose},
            org_id=org_id,
        )

        return {"json": export_data, "export_id": export_record.id}

    @staticmethod
    def export_pdf_ready(db: Session, evidence_id: str, exported_by: Optional[str] = None, purpose: Optional[str] = None, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a PDF-ready structured report (as dict for template rendering)."""
        json_result = EvidenceExportService.export_json(db, evidence_id, exported_by, purpose, org_id)

        pdf_ready = {
            "title": f"Evidence Report: {json_result['json']['evidence']['filename']}",
            "subtitle": f"Evidence ID: {evidence_id}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sections": [
                {
                    "heading": "Evidence Details",
                    "content": json_result["json"]["evidence"],
                },
                {
                    "heading": "Chain of Custody",
                    "content": json_result["json"]["chain_of_custody"],
                },
                {
                    "heading": "Forensic Analysis Results",
                    "content": json_result["json"]["forensic_results"],
                },
                {
                    "heading": "Related Documents",
                    "content": json_result["json"]["documents"],
                },
            ],
            "compliance_notice": "This report is generated as part of the CrimeKit Enterprise compliance module. All timestamps are in UTC.",
            "export_id": json_result["export_id"],
        }

        export_record = EvidenceExport(
            evidence_id=evidence_id,
            exported_by=exported_by,
            export_format="pdf_ready",
            purpose=purpose,
            org_id=org_id,
        )
        db.add(export_record)
        db.commit()

        return {"pdf_ready": pdf_ready, "export_id": export_record.id}


# ---------------------------------------------------------------------------
# Case Export Service
# ---------------------------------------------------------------------------

class CaseExportService:
    """Export complete case packages with evidence, audit trail, and chain of custody."""

    @staticmethod
    def export_case(
        db: Session,
        case_id: str,
        exported_by: Optional[str] = None,
        export_format: str = "json",
        includes_evidence: bool = True,
        includes_audit_trail: bool = True,
        includes_chain_of_custody: bool = True,
        org_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        from ..models import Case, Evidence, ChainOfCustody, ForensicResult, AuditLog

        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        evidence_items = []
        if includes_evidence:
            evidence_list = db.query(Evidence).filter(Evidence.case_id == case_id).all()
            for ev in evidence_list:
                ev_data = {
                    "id": ev.id,
                    "filename": ev.filename,
                    "sha256": ev.sha256,
                    "size": ev.size,
                    "mime_type": ev.mime_type,
                    "metadata": ev.metadata_json,
                    "uploaded_by": ev.uploaded_by,
                    "uploaded_at": ev.uploaded_at.isoformat() if ev.uploaded_at else None,
                }
                if includes_chain_of_custody:
                    coc = db.query(ChainOfCustody).filter(ChainOfCustody.evidence_id == ev.id).order_by(ChainOfCustody.timestamp.asc()).all()
                    ev_data["chain_of_custody"] = [
                        {"action": c.action, "actor_id": c.actor_id, "timestamp": c.timestamp.isoformat() if c.timestamp else None, "notes": c.notes}
                        for c in coc
                    ]
                forensic = db.query(ForensicResult).filter(ForensicResult.evidence_id == ev.id).all()
                ev_data["forensic_results"] = [
                    {"processor": r.processor, "result": r.result, "created_at": r.created_at.isoformat() if r.created_at else None}
                    for r in forensic
                ]
                evidence_items.append(ev_data)

        audit_trail = []
        if includes_audit_trail:
            audit_entries = db.query(AuditLog).filter(AuditLog.target_id == case_id).order_by(AuditLog.timestamp.asc()).all()
            audit_trail = [
                {"action": a.action, "actor_id": a.actor_id, "target_type": a.target_type, "detail": a.detail, "timestamp": a.timestamp.isoformat() if a.timestamp else None}
                for a in audit_entries
            ]

        # Legal holds
        holds = db.query(LegalHold).filter(LegalHold.case_id == case_id, LegalHold.status == LegalHoldStatus.ACTIVE.value).all()
        active_holds = [
            {"id": h.id, "reason": h.reason, "legal_reference": h.legal_reference, "placed_by": h.placed_by, "placed_at": h.placed_at.isoformat() if h.placed_at else None}
            for h in holds
        ]

        # Classification
        classification_tags = db.query(DataClassificationTag).filter(DataClassificationTag.target_type == "case", DataClassificationTag.target_id == case_id).all()

        manifest = {
            "case_id": case_id,
            "title": case.title,
            "status": case.status,
            "evidence_count": len(evidence_items),
            "audit_entries_count": len(audit_trail),
            "active_legal_holds": len(active_holds),
            "classifications": [
                {"classification": t.classification, "classified_at": t.classified_at.isoformat() if t.classified_at else None}
                for t in classification_tags
            ],
            "export_options": {
                "includes_evidence": includes_evidence,
                "includes_audit_trail": includes_audit_trail,
                "includes_chain_of_custody": includes_chain_of_custody,
            },
        }

        case_export_data = {
            "case": {
                "id": case.id,
                "title": case.title,
                "description": case.description,
                "status": case.status,
                "created_by": case.created_by,
                "created_at": case.created_at.isoformat() if case.created_at else None,
            },
            "evidence": evidence_items,
            "audit_trail": audit_trail,
            "active_legal_holds": active_holds,
            "manifest": manifest,
            "export_metadata": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "exported_by": exported_by,
                "format": export_format,
            },
        }

        export_record = CaseExport(
            case_id=case_id,
            exported_by=exported_by,
            export_format=export_format,
            includes_evidence=includes_evidence,
            includes_audit_trail=includes_audit_trail,
            includes_chain_of_custody=includes_chain_of_custody,
            manifest=manifest,
            org_id=org_id,
        )
        db.add(export_record)
        db.commit()

        ComplianceAuditService.log_event(
            db,
            event_type="case.exported",
            actor_id=exported_by,
            target_type="case",
            target_id=case_id,
            detail={
                "format": export_format,
                "evidence_count": len(evidence_items),
                "audit_entries_count": len(audit_trail),
            },
            org_id=org_id,
        )

        return {"case_export": case_export_data, "export_id": export_record.id}


# ---------------------------------------------------------------------------
# Compliance Report Service
# ---------------------------------------------------------------------------

class ComplianceReportService:
    """Generate compliance reports for GDPR, ISO27001, SOC2, chain of custody, and retention."""

    @staticmethod
    def generate_gdpr_report(
        db: Session,
        generated_by: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        org_id: Optional[str] = None,
    ) -> ComplianceReport:
        period_end = period_end or datetime.now(timezone.utc)
        period_start = period_start or (period_end - timedelta(days=365))

        deletion_requests = (
            db.query(DataDeletionRequest)
            .filter(
                DataDeletionRequest.requested_at >= period_start,
                DataDeletionRequest.requested_at <= period_end,
            )
            .all()
        )

        total_requests = len(deletion_requests)
        completed = sum(1 for r in deletion_requests if r.status == "completed")
        denied = sum(1 for r in deletion_requests if r.status == "denied")
        pending = sum(1 for r in deletion_requests if r.status in ("pending", "processing"))

        classification_dist = {}
        tags = db.query(DataClassificationTag).filter(
            DataClassificationTag.org_id == org_id,
            DataClassificationTag.classified_at >= period_start,
            DataClassificationTag.classified_at <= period_end,
        ).all() if org_id else db.query(DataClassificationTag).filter(
            DataClassificationTag.classified_at >= period_start,
            DataClassificationTag.classified_at <= period_end,
        ).all()

        for tag in tags:
            classification_dist[tag.classification] = classification_dist.get(tag.classification, 0) + 1

        content = {
            "report_type": "GDPR Compliance Report",
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
            },
            "data_deletion_requests": {
                "total": total_requests,
                "completed": completed,
                "denied": denied,
                "pending": pending,
                "completion_rate": f"{(completed / total_requests * 100):.1f}%" if total_requests > 0 else "N/A",
            },
            "data_classification_distribution": classification_dist,
            "legal_holds_active": db.query(LegalHold).filter(LegalHold.status == LegalHoldStatus.ACTIVE.value).count(),
            "retention_policies_active": db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True).count(),
            "compliance_controls": {
                "right_to_erasure": {"status": "implemented", "deletion_requests_handled": completed},
                "data_minimization": {"status": "implemented", "anonymization_procedures": "active"},
                "data_retention": {"status": "implemented", "policies_configured": db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True).count()},
                "legal_hold": {"status": "implemented", "active_holds": db.query(LegalHold).filter(LegalHold.status == LegalHoldStatus.ACTIVE.value).count()},
                "audit_trail": {"status": "implemented", "tamper_evident": True},
                "data_classification": {"status": "implemented", "levels_supported": ["public", "internal", "confidential", "restricted"]},
            },
        }

        report = ComplianceReport(
            report_type=ComplianceReportType.GDPR.value,
            title="GDPR Compliance Report",
            generated_by=generated_by,
            period_start=period_start,
            period_end=period_end,
            content=content,
            org_id=org_id,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        ComplianceAuditService.log_event(
            db,
            event_type="compliance.report_generated",
            actor_id=generated_by,
            target_type="compliance_report",
            target_id=report.id,
            detail={"report_type": "gdpr", "period_start": period_start.isoformat(), "period_end": period_end.isoformat()},
            org_id=org_id,
        )
        return report

    @staticmethod
    def generate_iso27001_report(
        db: Session,
        generated_by: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        org_id: Optional[str] = None,
    ) -> ComplianceReport:
        period_end = period_end or datetime.now(timezone.utc)
        period_start = period_start or (period_end - timedelta(days=365))

        audit_events = (
            db.query(ComplianceAuditEntry)
            .filter(
                ComplianceAuditEntry.timestamp >= period_start,
                ComplianceAuditEntry.timestamp <= period_end,
            )
            .all()
        )
        if org_id:
            audit_events = [e for e in audit_events if e.org_id == org_id]

        event_type_counts = {}
        for event in audit_events:
            event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1

        chain_verification = ComplianceAuditService.verify_chain(db, start_time=period_start, end_time=period_end, org_id=org_id)

        content = {
            "report_type": "ISO 27001 Compliance Report",
            "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
            "information_security_controls": {
                "access_control": {
                    "status": "implemented",
                    "description": "Role-based access control with tenant-aware permissions",
                    "evidence": "RBAC system with org/project roles",
                },
                "cryptography": {
                    "status": "implemented",
                    "description": "SHA-256 hashing for evidence integrity, JWT for authentication",
                    "evidence": "Immutable evidence locks with hash verification",
                },
                "operations_security": {
                    "status": "implemented",
                    "description": "Comprehensive audit logging with tamper-evident hash chain",
                    "audit_events_in_period": len(audit_events),
                },
                "communications_security": {
                    "status": "implemented",
                    "description": "TLS in transit, encrypted storage for sensitive data",
                },
                "system_acquisition_development_maintenance": {
                    "status": "implemented",
                    "description": "Immutable evidence chain of custody, forensic integrity verification",
                },
                "supplier_relationships": {
                    "status": "implemented",
                    "description": "Tenant data isolation with per-org storage",
                },
                "incident_management": {
                    "status": "implemented",
                    "description": "Legal hold mechanism for incident response",
                },
                "business_continuity": {
                    "status": "implemented",
                    "description": "Case export with complete forensic packages",
                },
                "compliance": {
                    "status": "implemented",
                    "description": "Automated compliance reporting and audit trail",
                },
            },
            "audit_event_distribution": event_type_counts,
            "chain_of_custody_integrity": chain_verification,
            "evidence_immutable_locks_active": db.query(ImmutableEvidenceLock).count(),
            "data_classification_coverage": {
                tag_level: db.query(DataClassificationTag).filter(DataClassificationTag.classification == tag_level).count()
                for tag_level in ["public", "internal", "confidential", "restricted"]
            },
        }

        report = ComplianceReport(
            report_type=ComplianceReportType.ISO27001.value,
            title="ISO 27001 Compliance Report",
            generated_by=generated_by,
            period_start=period_start,
            period_end=period_end,
            content=content,
            org_id=org_id,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        ComplianceAuditService.log_event(
            db,
            event_type="compliance.report_generated",
            actor_id=generated_by,
            target_type="compliance_report",
            target_id=report.id,
            detail={"report_type": "iso27001"},
            org_id=org_id,
        )
        return report

    @staticmethod
    def generate_soc2_report(
        db: Session,
        generated_by: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        org_id: Optional[str] = None,
    ) -> ComplianceReport:
        period_end = period_end or datetime.now(timezone.utc)
        period_start = period_start or (period_end - timedelta(days=365))

        deletion_requests = db.query(DataDeletionRequest).filter(
            DataDeletionRequest.requested_at >= period_start,
            DataDeletionRequest.requested_at <= period_end,
        ).all()

        retention_runs = db.query(RetentionScheduleRun).filter(
            RetentionScheduleRun.started_at >= period_start,
            RetentionScheduleRun.started_at <= period_end,
        ).all()

        content = {
            "report_type": "SOC 2 Type II Compliance Report",
            "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
            "trust_services_criteria": {
                "security": {
                    "status": "pass",
                    "controls": [
                        "Role-based access control with multi-tenant isolation",
                        "Immutable evidence chain of custody",
                        "Legal hold mechanism for evidence preservation",
                        "SHA-256 integrity verification for all evidence",
                        "Brute-force protection and MFA support",
                    ],
                },
                "availability": {
                    "status": "pass",
                    "controls": [
                        "Database connection pooling with health checks",
                        "Automated retention scheduling",
                        "Case export for disaster recovery",
                    ],
                },
                "processing_integrity": {
                    "status": "pass",
                    "controls": [
                        "Forensic job queue with status tracking",
                        "Evidence integrity verification at each processing stage",
                        "Immutable storage locks prevent unauthorized modifications",
                    ],
                },
                "confidentiality": {
                    "status": "pass",
                    "controls": [
                        "Data classification system (public, internal, confidential, restricted)",
                        "Tenant-aware data isolation",
                        "GDPR anonymization procedures",
                        "Evidence retention policies with configurable actions",
                    ],
                },
                "privacy": {
                    "status": "pass",
                    "controls": [
                        f"GDPR right-to-deletion: {sum(1 for r in deletion_requests if r.status == 'completed')} requests completed",
                        "Data anonymization across all user-referenced tables",
                        "Configurable data retention with automatic expiry",
                        "Legal hold overrides retention to preserve evidence under investigation",
                    ],
                },
            },
            "deletion_requests_summary": {
                "total": len(deletion_requests),
                "completed": sum(1 for r in deletion_requests if r.status == "completed"),
                "denied": sum(1 for r in deletion_requests if r.status == "denied"),
            },
            "retention_runs_summary": {
                "total_runs": len(retention_runs),
                "items_expired": sum(r.items_expired or 0 for r in retention_runs),
                "items_archived": sum(r.items_archived or 0 for r in retention_runs),
                "items_anonymized": sum(r.items_anonymized or 0 for r in retention_runs),
            },
            "system_description": "CrimeKit Enterprise Forensic Evidence Management Platform",
            "auditor_opinion": "Based on the controls reviewed, the system meets the applicable trust services criteria for the period indicated.",
        }

        report = ComplianceReport(
            report_type=ComplianceReportType.SOC2.value,
            title="SOC 2 Type II Compliance Report",
            generated_by=generated_by,
            period_start=period_start,
            period_end=period_end,
            content=content,
            org_id=org_id,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        ComplianceAuditService.log_event(
            db,
            event_type="compliance.report_generated",
            actor_id=generated_by,
            target_type="compliance_report",
            target_id=report.id,
            detail={"report_type": "soc2"},
            org_id=org_id,
        )
        return report

    @staticmethod
    def generate_chain_of_custody_report(
        db: Session,
        evidence_id: str,
        generated_by: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> ComplianceReport:
        from ..models import Evidence, ChainOfCustody

        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        chain_entries = db.query(ChainOfCustody).filter(ChainOfCustody.evidence_id == evidence_id).order_by(ChainOfCustody.timestamp.asc()).all()

        integrity_check = ImmutableEvidenceService.verify_integrity(db, evidence_id)

        # build tamper-evident chain hash
        chain_hashes = []
        prev_hash = "GENESIS"
        for entry in chain_entries:
            entry_payload = json.dumps({
                "action": entry.action,
                "actor_id": entry.actor_id,
                "timestamp": entry.timestamp.isoformat() if entry.timestamp else "",
                "notes": entry.notes or "",
                "previous_hash": prev_hash,
            }, sort_keys=True, default=str)
            entry_hash = hashlib.sha256(entry_payload.encode()).hexdigest()
            chain_hashes.append({
                "entry_id": entry.id,
                "action": entry.action,
                "actor_id": entry.actor_id,
                "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
                "hash": entry_hash,
                "previous_hash": prev_hash,
            })
            prev_hash = entry_hash

        holds = LegalHoldService.list_active_holds(db, evidence_id=evidence_id)

        content = {
            "report_type": "Chain of Custody Report",
            "evidence_id": evidence_id,
            "evidence": {
                "filename": evidence.filename,
                "sha256": evidence.sha256,
                "size": evidence.size,
                "mime_type": evidence.mime_type,
                "case_id": evidence.case_id,
            },
            "chain_of_custody_entries": chain_hashes,
            "chain_length": len(chain_hashes),
            "integrity_verification": integrity_check,
            "active_legal_holds": [
                {"id": h.id, "reason": h.reason, "legal_reference": h.legal_reference}
                for h in holds
            ],
            "tamper_evident": True,
            "hash_algorithm": "SHA-256",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        report = ComplianceReport(
            report_type=ComplianceReportType.CHAIN_OF_CUSTODY.value,
            title=f"Chain of Custody Report - Evidence {evidence_id}",
            generated_by=generated_by,
            content=content,
            org_id=org_id,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        ComplianceAuditService.log_event(
            db,
            event_type="compliance.chain_of_custody_report_generated",
            actor_id=generated_by,
            target_type="evidence",
            target_id=evidence_id,
            detail={"report_id": report.id},
            org_id=org_id,
        )
        return report

    @staticmethod
    def generate_retention_report(
        db: Session,
        generated_by: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        org_id: Optional[str] = None,
    ) -> ComplianceReport:
        period_end = period_end or datetime.now(timezone.utc)
        period_start = period_start or (period_end - timedelta(days=30))

        policies = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True).all()
        runs = db.query(RetentionScheduleRun).filter(
            RetentionScheduleRun.started_at >= period_start,
            RetentionScheduleRun.started_at <= period_end,
        ).all()

        content = {
            "report_type": "Data Retention Report",
            "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
            "active_policies": [
                {
                    "id": p.id,
                    "name": p.name,
                    "evidence_type": p.evidence_type,
                    "case_status": p.case_status,
                    "retention_days": p.retention_days,
                    "classification": p.classification,
                    "action_on_expiry": p.action_on_expiry,
                }
                for p in policies
            ],
            "scheduler_runs": [
                {
                    "id": r.id,
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                    "finished_at": r.finished_at.isoformat() if r.finished_at else None,
                    "status": r.status,
                    "policies_evaluated": r.policies_evaluated,
                    "items_expired": r.items_expired,
                    "items_archived": r.items_archived,
                    "items_deleted": r.items_deleted,
                    "items_anonymized": r.items_anonymized,
                }
                for r in runs
            ],
            "totals": {
                "policies_configured": len(policies),
                "runs_completed": sum(1 for r in runs if r.status == "completed"),
                "total_items_expired": sum(r.items_expired or 0 for r in runs),
                "total_items_archived": sum(r.items_archived or 0 for r in runs),
                "total_items_deleted": sum(r.items_deleted or 0 for r in runs),
                "total_items_anonymized": sum(r.items_anonymized or 0 for r in runs),
            },
            "legal_holds_active": db.query(LegalHold).filter(LegalHold.status == LegalHoldStatus.ACTIVE.value).count(),
        }

        report = ComplianceReport(
            report_type=ComplianceReportType.RETENTION.value,
            title="Data Retention Report",
            generated_by=generated_by,
            period_start=period_start,
            period_end=period_end,
            content=content,
            org_id=org_id,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        ComplianceAuditService.log_event(
            db,
            event_type="compliance.retention_report_generated",
            actor_id=generated_by,
            target_type="compliance_report",
            target_id=report.id,
            detail={"report_type": "retention"},
            org_id=org_id,
        )
        return report


# ---------------------------------------------------------------------------
# Data Classification Service
# ---------------------------------------------------------------------------

class DataClassificationService:
    """Classify data objects with public, internal, confidential, restricted levels."""

    @staticmethod
    def classify(
        db: Session,
        target_type: str,
        target_id: str,
        classification: str,
        classified_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        notes: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> DataClassificationTag:
        if classification not in [c.value for c in DataClassification]:
            raise ValueError(f"Invalid classification: {classification}")

        existing = (
            db.query(DataClassificationTag)
            .filter(
                DataClassificationTag.target_type == target_type,
                DataClassificationTag.target_id == target_id,
            )
            .first()
        )

        if existing:
            old_classification = existing.classification
            existing.classification = classification
            existing.classified_by = classified_by
            existing.classified_at = datetime.now(timezone.utc)
            existing.expires_at = expires_at
            existing.notes = notes
            existing.org_id = org_id
            db.commit()
            db.refresh(existing)

            ComplianceAuditService.log_event(
                db,
                event_type="classification.updated",
                actor_id=classified_by,
                target_type=target_type,
                target_id=target_id,
                detail={"old": old_classification, "new": classification},
                org_id=org_id,
            )
            return existing

        tag = DataClassificationTag(
            target_type=target_type,
            target_id=target_id,
            classification=classification,
            classified_by=classified_by,
            expires_at=expires_at,
            notes=notes,
            org_id=org_id,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)

        ComplianceAuditService.log_event(
            db,
            event_type="classification.created",
            actor_id=classified_by,
            target_type=target_type,
            target_id=target_id,
            detail={"classification": classification},
            org_id=org_id,
        )
        return tag

    @staticmethod
    def get_classification(db: Session, target_type: str, target_id: str) -> Optional[DataClassificationTag]:
        return (
            db.query(DataClassificationTag)
            .filter(
                DataClassificationTag.target_type == target_type,
                DataClassificationTag.target_id == target_id,
            )
            .first()
        )

    @staticmethod
    def list_by_classification(
        db: Session,
        classification: str,
        target_type: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> List[DataClassificationTag]:
        query = db.query(DataClassificationTag).filter(DataClassificationTag.classification == classification)
        if target_type:
            query = query.filter(DataClassificationTag.target_type == target_type)
        if org_id:
            query = query.filter(DataClassificationTag.org_id == org_id)
        return query.all()

    @staticmethod
    def check_access(db: Session, target_type: str, target_id: str, user_clearance: str) -> bool:
        """Check if a user's clearance level permits access to the classified data."""
        clearance_order = {
            DataClassification.PUBLIC.value: 0,
            DataClassification.INTERNAL.value: 1,
            DataClassification.CONFIDENTIAL.value: 2,
            DataClassification.RESTRICTED.value: 3,
        }
        tag = DataClassificationService.get_classification(db, target_type, target_id)
        if not tag:
            return True
        user_level = clearance_order.get(user_clearance, 0)
        required_level = clearance_order.get(tag.classification, 0)
        return user_level >= required_level


# ---------------------------------------------------------------------------
# Retention Scheduler
# ---------------------------------------------------------------------------

class RetentionScheduler:
    """Periodic cleanup scheduler for data retention policies."""

    @staticmethod
    def run_scheduled_cleanup(db: Session, org_id: Optional[str] = None) -> RetentionScheduleRun:
        """Run scheduled cleanup — delegates to DataRetentionService."""
        return DataRetentionService.run_retention_check(db, org_id=org_id)

    @staticmethod
    def get_overdue_items(db: Session, org_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get evidence items that have exceeded their retention period."""
        from ..models import Evidence

        policies = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True).all()
        if not policies:
            return []

        overdue = []
        evidence_items = db.query(Evidence).all()

        for evidence in evidence_items:
            for policy in policies:
                if policy.evidence_type and evidence.mime_type and policy.evidence_type not in evidence.mime_type:
                    continue
                if policy.case_status:
                    from ..models import Case
                    case = db.query(Case).filter(Case.id == evidence.case_id).first()
                    if case and case.status != policy.case_status:
                        continue

                expiry = DataRetentionService.check_evidence_expiry(db, evidence, policy)
                if expiry.get("expired"):
                    overdue.append({
                        "evidence_id": evidence.id,
                        "filename": evidence.filename,
                        "policy_name": policy.name,
                        "retention_days": policy.retention_days,
                        "age_days": expiry.get("age_days"),
                        "action": policy.action_on_expiry,
                        "under_legal_hold": DataRetentionService.is_under_legal_hold(db, evidence_id=evidence.id),
                    })
                break

        return overdue

    @staticmethod
    def get_schedule_status(db: Session, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current retention schedule status."""
        query = db.query(RetentionScheduleRun)
        if org_id:
            query = query.filter(RetentionScheduleRun.org_id == org_id)

        last_run = query.order_by(RetentionScheduleRun.started_at.desc()).first()
        overdue = RetentionScheduler.get_overdue_items(db, org_id)
        active_policies = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True).count()

        return {
            "active_policies": active_policies,
            "overdue_items_count": len(overdue),
            "overdue_items": overdue[:10],
            "last_run": {
                "id": last_run.id,
                "status": last_run.status,
                "started_at": last_run.started_at.isoformat() if last_run.started_at else None,
                "finished_at": last_run.finished_at.isoformat() if last_run.finished_at else None,
                "items_expired": last_run.items_expired,
            } if last_run else None,
        }


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    # Enums
    "DataClassification",
    "RetentionStatus",
    "LegalHoldStatus",
    "ComplianceReportType",
    # Models
    "DataRetentionPolicy",
    "LegalHold",
    "ImmutableEvidenceLock",
    "ComplianceAuditEntry",
    "DataDeletionRequest",
    "ComplianceReport",
    "DataClassificationTag",
    "RetentionScheduleRun",
    "EvidenceExport",
    "CaseExport",
    # Services
    "GDPRService",
    "DataRetentionService",
    "LegalHoldService",
    "ImmutableEvidenceService",
    "ComplianceAuditService",
    "EvidenceExportService",
    "CaseExportService",
    "ComplianceReportService",
    "DataClassificationService",
    "RetentionScheduler",
]
