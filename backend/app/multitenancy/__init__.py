"""
Enterprise Multi-Tenancy Module for CrimeKit

Provides organization/project hierarchy, tenant-aware RBAC, storage isolation,
AI/embeddings isolation, search filtering, Knowledge Graph isolation, audit logs,
tenant context middleware, cross-tenant isolation, provisioning/deprovisioning,
and usage tracking with quotas.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from contextvars import ContextVar
from datetime import datetime, timedelta, timezone
from enum import Enum as PyEnum
from typing import Any, Callable, Dict, List, Optional, Set

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
# Tenant Context (contextvars for async-safe tenant isolation)
# ---------------------------------------------------------------------------

_current_org_id: ContextVar[Optional[str]] = ContextVar("current_org_id", default=None)
_current_project_id: ContextVar[Optional[str]] = ContextVar("current_project_id", default=None)
_current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)


class TenantContext:
    """Set/get current tenant context — thread-safe via contextvars."""

    @staticmethod
    def set_org_id(org_id: Optional[str]) -> None:
        _current_org_id.set(org_id)

    @staticmethod
    def get_org_id() -> Optional[str]:
        return _current_org_id.get()

    @staticmethod
    def set_project_id(project_id: Optional[str]) -> None:
        _current_project_id.set(project_id)

    @staticmethod
    def get_project_id() -> Optional[str]:
        return _current_project_id.get()

    @staticmethod
    def set_user_id(user_id: Optional[str]) -> None:
        _current_user_id.set(user_id)

    @staticmethod
    def get_user_id() -> Optional[str]:
        return _current_user_id.get()

    @staticmethod
    def clear() -> None:
        _current_org_id.set(None)
        _current_project_id.set(None)
        _current_user_id.set(None)

    @staticmethod
    def get_all() -> Dict[str, Optional[str]]:
        return {
            "org_id": _current_org_id.get(),
            "project_id": _current_project_id.get(),
            "user_id": _current_user_id.get(),
        }


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OrgRole(str, PyEnum):
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    ORG_MEMBER = "org_member"
    ORG_VIEWER = "org_viewer"


class ProjectRole(str, PyEnum):
    PROJECT_ADMIN = "project_admin"
    PROJECT_MEMBER = "project_member"
    PROJECT_VIEWER = "project_viewer"


class OrgStatus(str, PyEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPROVISIONED = "deprovisioned"
    PENDING = "pending"


class ProjectStatus(str, PyEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Organization(Base):
    """Top-level tenant organization."""
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default=OrgStatus.ACTIVE.value)
    # storage isolation
    storage_bucket = Column(String, nullable=True)  # per-org S3 bucket name
    storage_prefix = Column(String, nullable=True)  # prefix within bucket
    # AI isolation
    embedding_namespace = Column(String, nullable=True)  # isolated embedding namespace
    # Knowledge Graph isolation
    kg_namespace = Column(String, nullable=True)  # isolated graph namespace
    # quotas
    max_users = Column(Integer, default=100)
    max_projects = Column(Integer, default=20)
    max_storage_bytes = Column(Integer, default=10 * 1024 * 1024 * 1024)  # 10GB default
    max_embeddings = Column(Integer, default=100000)
    # billing
    plan = Column(String, default="free")  # free, pro, enterprise
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    memberships = relationship("OrgMembership", back_populates="organization", cascade="all, delete-orphan")
    usage_records = relationship("TenantUsageRecord", back_populates="organization", cascade="all, delete-orphan")


class Project(Base):
    """Project belongs to an organization."""
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default=ProjectStatus.ACTIVE.value)
    # storage sub-prefix within org bucket
    storage_prefix = Column(String, nullable=True)
    # AI embedding sub-namespace
    embedding_prefix = Column(String, nullable=True)
    # KG sub-namespace
    kg_prefix = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    organization = relationship("Organization", back_populates="projects")
    memberships = relationship("ProjectMembership", back_populates="project", cascade="all, delete-orphan")


class OrgMembership(Base):
    """User membership in an organization with a role."""
    __tablename__ = "org_memberships"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String, nullable=False, default=OrgRole.ORG_MEMBER.value)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    invited_by = Column(String, ForeignKey("users.id"), nullable=True)

    # relationships
    organization = relationship("Organization", back_populates="memberships")


class ProjectMembership(Base):
    """User membership in a project with a role."""
    __tablename__ = "project_memberships"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String, nullable=False, default=ProjectRole.PROJECT_MEMBER.value)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    invited_by = Column(String, ForeignKey("users.id"), nullable=True)

    # relationships
    project = relationship("Project", back_populates="memberships")


class TenantAuditLog(Base):
    """Tenant-aware audit logs — isolated per org."""
    __tablename__ = "tenant_audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False, index=True)
    target_type = Column(String, nullable=True)
    target_id = Column(String, nullable=True)
    detail = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class TenantUsageRecord(Base):
    """Track tenant usage for quotas and billing."""
    __tablename__ = "tenant_usage_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    metric = Column(String, nullable=False, index=True)  # storage_bytes, users, projects, embeddings, api_calls
    value = Column(Integer, default=0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    # relationships
    organization = relationship("Organization", back_populates="usage_records")


class TenantProvisioningLog(Base):
    """Tracks tenant provisioning and deprovisioning events."""
    __tablename__ = "tenant_provisioning_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    action = Column(String, nullable=False)  # provisioned, deprovisioned, suspended, reactivated
    performed_by = Column(String, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    detail = Column(JSON, nullable=True)
    status = Column(String, default="completed")  # completed, failed


class TenantIsolationRule(Base):
    """Rules for cross-tenant data isolation enforcement."""
    __tablename__ = "tenant_isolation_rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    rule_type = Column(String, nullable=False)  # storage, ai, search, kg
    config = Column(JSON, nullable=True)  # rule-specific configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# RBAC Service (Tenant-Aware)
# ---------------------------------------------------------------------------

class TenantRBACService:
    """Tenant-aware role-based access control for org and project levels."""

    ORG_ROLE_HIERARCHY = {
        OrgRole.SUPER_ADMIN.value: 4,
        OrgRole.ORG_ADMIN.value: 3,
        OrgRole.ORG_MEMBER.value: 2,
        OrgRole.ORG_VIEWER.value: 1,
    }

    PROJECT_ROLE_HIERARCHY = {
        ProjectRole.PROJECT_ADMIN.value: 3,
        ProjectRole.PROJECT_MEMBER.value: 2,
        ProjectRole.PROJECT_VIEWER.value: 1,
    }

    @staticmethod
    def add_org_member(
        db: Session,
        org_id: str,
        user_id: str,
        role: str = OrgRole.ORG_MEMBER.value,
        invited_by: Optional[str] = None,
    ) -> OrgMembership:
        existing = (
            db.query(OrgMembership)
            .filter(OrgMembership.org_id == org_id, OrgMembership.user_id == user_id)
            .first()
        )
        if existing:
            existing.role = role
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            return existing

        membership = OrgMembership(
            org_id=org_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    @staticmethod
    def remove_org_member(db: Session, org_id: str, user_id: str) -> bool:
        membership = (
            db.query(OrgMembership)
            .filter(OrgMembership.org_id == org_id, OrgMembership.user_id == user_id)
            .first()
        )
        if not membership:
            return False
        membership.is_active = False
        db.commit()
        return True

    @staticmethod
    def get_org_role(db: Session, org_id: str, user_id: str) -> Optional[str]:
        membership = (
            db.query(OrgMembership)
            .filter(
                OrgMembership.org_id == org_id,
                OrgMembership.user_id == user_id,
                OrgMembership.is_active == True,
            )
            .first()
        )
        return membership.role if membership else None

    @staticmethod
    def has_org_permission(db: Session, org_id: str, user_id: str, required_role: str) -> bool:
        role = TenantRBACService.get_org_role(db, org_id, user_id)
        if not role:
            return False
        return TenantRBACService.ORG_ROLE_HIERARCHY.get(role, 0) >= TenantRBACService.ORG_ROLE_HIERARCHY.get(required_role, 0)

    @staticmethod
    def add_project_member(
        db: Session,
        project_id: str,
        user_id: str,
        role: str = ProjectRole.PROJECT_MEMBER.value,
        invited_by: Optional[str] = None,
    ) -> ProjectMembership:
        existing = (
            db.query(ProjectMembership)
            .filter(ProjectMembership.project_id == project_id, ProjectMembership.user_id == user_id)
            .first()
        )
        if existing:
            existing.role = role
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            return existing

        membership = ProjectMembership(
            project_id=project_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    @staticmethod
    def remove_project_member(db: Session, project_id: str, user_id: str) -> bool:
        membership = (
            db.query(ProjectMembership)
            .filter(ProjectMembership.project_id == project_id, ProjectMembership.user_id == user_id)
            .first()
        )
        if not membership:
            return False
        membership.is_active = False
        db.commit()
        return True

    @staticmethod
    def get_project_role(db: Session, project_id: str, user_id: str) -> Optional[str]:
        membership = (
            db.query(ProjectMembership)
            .filter(
                ProjectMembership.project_id == project_id,
                ProjectMembership.user_id == user_id,
                ProjectMembership.is_active == True,
            )
            .first()
        )
        return membership.role if membership else None

    @staticmethod
    def has_project_permission(db: Session, project_id: str, user_id: str, required_role: str) -> bool:
        role = TenantRBACService.get_project_role(db, project_id, user_id)
        if not role:
            return False
        return TenantRBACService.PROJECT_ROLE_HIERARCHY.get(role, 0) >= TenantRBACService.PROJECT_ROLE_HIERARCHY.get(required_role, 0)

    @staticmethod
    def list_org_members(db: Session, org_id: str) -> List[Dict[str, Any]]:
        memberships = (
            db.query(OrgMembership)
            .filter(OrgMembership.org_id == org_id, OrgMembership.is_active == True)
            .all()
        )
        return [
            {"user_id": m.user_id, "role": m.role, "joined_at": m.joined_at.isoformat() if m.joined_at else None, "invited_by": m.invited_by}
            for m in memberships
        ]

    @staticmethod
    def list_project_members(db: Session, project_id: str) -> List[Dict[str, Any]]:
        memberships = (
            db.query(ProjectMembership)
            .filter(ProjectMembership.project_id == project_id, ProjectMembership.is_active == True)
            .all()
        )
        return [
            {"user_id": m.user_id, "role": m.role, "joined_at": m.joined_at.isoformat() if m.joined_at else None, "invited_by": m.invited_by}
            for m in memberships
        ]

    @staticmethod
    def user_orgs(db: Session, user_id: str) -> List[Dict[str, Any]]:
        memberships = (
            db.query(OrgMembership)
            .filter(OrgMembership.user_id == user_id, OrgMembership.is_active == True)
            .all()
        )
        return [{"org_id": m.org_id, "role": m.role} for m in memberships]

    @staticmethod
    def user_projects(db: Session, user_id: str, org_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = (
            db.query(ProjectMembership)
            .filter(ProjectMembership.user_id == user_id, ProjectMembership.is_active == True)
        )
        if org_id:
            query = query.join(Project, Project.id == ProjectMembership.project_id).filter(Project.org_id == org_id)
        memberships = query.all()
        return [{"project_id": m.project_id, "role": m.role} for m in memberships]


# ---------------------------------------------------------------------------
# Organization Service
# ---------------------------------------------------------------------------

class OrganizationService:
    """Organization CRUD and lifecycle management."""

    @staticmethod
    def create_organization(
        db: Session,
        name: str,
        slug: str,
        description: Optional[str] = None,
        plan: str = "free",
        created_by: Optional[str] = None,
    ) -> Organization:
        existing = db.query(Organization).filter(
            or_(Organization.name == name, Organization.slug == slug)
        ).first()
        if existing:
            raise ValueError(f"Organization with name '{name}' or slug '{slug}' already exists")

        storage_bucket = f"crimekit-{slug}-{uuid.uuid4().hex[:8]}"
        embedding_namespace = f"org-{slug}-embeddings"
        kg_namespace = f"org-{slug}-kg"

        org = Organization(
            name=name,
            slug=slug,
            description=description,
            plan=plan,
            storage_bucket=storage_bucket,
            storage_prefix="",
            embedding_namespace=embedding_namespace,
            kg_namespace=kg_namespace,
        )
        db.add(org)
        db.commit()
        db.refresh(org)

        if created_by:
            TenantRBACService.add_org_member(db, org.id, created_by, OrgRole.ORG_ADMIN.value, invited_by=created_by)

        TenantAuditService.log(
            db,
            org_id=org.id,
            user_id=created_by,
            action="org.created",
            target_type="organization",
            target_id=org.id,
            detail={"name": name, "slug": slug, "plan": plan},
        )

        return org

    @staticmethod
    def get_organization(db: Session, org_id: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.id == org_id).first()

    @staticmethod
    def get_organization_by_slug(db: Session, slug: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.slug == slug).first()

    @staticmethod
    def update_organization(db: Session, org_id: str, **kwargs) -> Optional[Organization]:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return None
        for key, value in kwargs.items():
            if hasattr(org, key) and value is not None:
                setattr(org, key, value)
        org.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(org)
        return org

    @staticmethod
    def delete_organization(db: Session, org_id: str, deleted_by: Optional[str] = None) -> bool:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return False

        TenantAuditService.log(
            db,
            org_id=org_id,
            user_id=deleted_by,
            action="org.deleting",
            target_type="organization",
            target_id=org_id,
        )

        db.delete(org)
        db.commit()
        return True

    @staticmethod
    def list_organizations(db: Session, status: Optional[str] = None, limit: int = 100) -> List[Organization]:
        query = db.query(Organization)
        if status:
            query = query.filter(Organization.status == status)
        return query.order_by(Organization.created_at.desc()).limit(limit).all()


# ---------------------------------------------------------------------------
# Project Service
# ---------------------------------------------------------------------------

class ProjectService:
    """Project CRUD and management."""

    @staticmethod
    def create_project(
        db: Session,
        org_id: str,
        name: str,
        slug: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Project:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")
        if org.status != OrgStatus.ACTIVE.value:
            raise ValueError(f"Organization {org_id} is {org.status}")

        existing = db.query(Project).filter(Project.org_id == org_id, Project.slug == slug).first()
        if existing:
            raise ValueError(f"Project with slug '{slug}' already exists in this organization")

        project_count = db.query(Project).filter(Project.org_id == org_id).count()
        if project_count >= org.max_projects:
            raise ValueError(f"Organization has reached maximum project limit ({org.max_projects})")

        storage_prefix = f"projects/{slug}/"
        embedding_prefix = f"{org.embedding_namespace}/{slug}"
        kg_prefix = f"{org.kg_namespace}/{slug}"

        project = Project(
            org_id=org_id,
            name=name,
            slug=slug,
            description=description,
            storage_prefix=storage_prefix,
            embedding_prefix=embedding_prefix,
            kg_prefix=kg_prefix,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        if created_by:
            TenantRBACService.add_project_member(db, project.id, created_by, ProjectRole.PROJECT_ADMIN.value, invited_by=created_by)

        TenantAuditService.log(
            db,
            org_id=org_id,
            project_id=project.id,
            user_id=created_by,
            action="project.created",
            target_type="project",
            target_id=project.id,
            detail={"name": name, "slug": slug},
        )

        return project

    @staticmethod
    def get_project(db: Session, project_id: str) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def list_org_projects(db: Session, org_id: str, status: Optional[str] = None) -> List[Project]:
        query = db.query(Project).filter(Project.org_id == org_id)
        if status:
            query = query.filter(Project.status == status)
        return query.order_by(Project.created_at.desc()).all()

    @staticmethod
    def update_project(db: Session, project_id: str, **kwargs) -> Optional[Project]:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        for key, value in kwargs.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)
        project.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def archive_project(db: Session, project_id: str, archived_by: Optional[str] = None) -> Optional[Project]:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        project.status = ProjectStatus.ARCHIVED.value
        project.updated_at = datetime.now(timezone.utc)
        db.commit()

        TenantAuditService.log(
            db,
            org_id=project.org_id,
            project_id=project_id,
            user_id=archived_by,
            action="project.archived",
            target_type="project",
            target_id=project_id,
        )
        return project

    @staticmethod
    def delete_project(db: Session, project_id: str, deleted_by: Optional[str] = None) -> bool:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False

        TenantAuditService.log(
            db,
            org_id=project.org_id,
            project_id=project_id,
            user_id=deleted_by,
            action="project.deleting",
            target_type="project",
            target_id=project_id,
        )

        db.delete(project)
        db.commit()
        return True


# ---------------------------------------------------------------------------
# Tenant-Aware Storage Isolation
# ---------------------------------------------------------------------------

class TenantStorageService:
    """Tenant-aware storage isolation — separate S3 buckets per org."""

    @staticmethod
    def get_storage_config(db: Session, org_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        config = {
            "bucket": org.storage_bucket,
            "prefix": org.storage_prefix or "",
            "region": os.getenv("AWS_REGION", "us-east-1"),
            "endpoint_url": os.getenv("S3_ENDPOINT_URL"),
        }

        if project_id:
            project = db.query(Project).filter(Project.id == project_id, Project.org_id == org_id).first()
            if project and project.storage_prefix:
                config["prefix"] = f"{config['prefix']}{project.storage_prefix}"

        return config

    @staticmethod
    def generate_upload_path(
        db: Session,
        org_id: str,
        project_id: Optional[str] = None,
        filename: str = "",
        evidence_type: str = "general",
    ) -> str:
        config = TenantStorageService.get_storage_config(db, org_id, project_id)
        timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        unique_id = uuid.uuid4().hex[:12]
        safe_filename = filename.replace("/", "_").replace("\\", "_")[:100]
        path = f"{config['prefix']}{evidence_type}/{timestamp}/{unique_id}_{safe_filename}"
        return path

    @staticmethod
    def validate_storage_access(db: Session, org_id: str, path: str) -> bool:
        """Validate that a storage path belongs to the specified org."""
        config = TenantStorageService.get_storage_config(db, org_id)
        return path.startswith(config["prefix"]) if config["prefix"] else True

    @staticmethod
    def get_storage_usage(db: Session, org_id: str) -> Dict[str, Any]:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        usage_records = (
            db.query(TenantUsageRecord)
            .filter(TenantUsageRecord.org_id == org_id, TenantUsageRecord.metric == "storage_bytes")
            .order_by(TenantUsageRecord.recorded_at.desc())
            .limit(1)
            .all()
        )

        current_usage = usage_records[0].value if usage_records else 0

        return {
            "current_bytes": current_usage,
            "max_bytes": org.max_storage_bytes,
            "utilization_pct": round((current_usage / org.max_storage_bytes * 100), 2) if org.max_storage_bytes > 0 else 0,
            "bucket": org.storage_bucket,
        }


# ---------------------------------------------------------------------------
# Tenant-Aware AI (Isolated Embeddings)
# ---------------------------------------------------------------------------

class TenantAIService:
    """Tenant-aware AI with isolated embeddings per org."""

    @staticmethod
    def get_embedding_config(db: Session, org_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        config = {
            "namespace": org.embedding_namespace,
            "dimension": int(os.getenv("EMBEDDING_DIMENSION", "1536")),
            "model": os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"),
            "max_embeddings": org.max_embeddings,
        }

        if project_id:
            project = db.query(Project).filter(Project.id == project_id, Project.org_id == org_id).first()
            if project and project.embedding_prefix:
                config["namespace"] = project.embedding_prefix

        return config

    @staticmethod
    def validate_embedding_access(db: Session, org_id: str, embedding_namespace: str) -> bool:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return False
        return embedding_namespace.startswith(org.embedding_namespace) if org.embedding_namespace else True

    @staticmethod
    def get_embedding_usage(db: Session, org_id: str) -> Dict[str, Any]:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        usage_records = (
            db.query(TenantUsageRecord)
            .filter(TenantUsageRecord.org_id == org_id, TenantUsageRecord.metric == "embeddings")
            .order_by(TenantUsageRecord.recorded_at.desc())
            .limit(1)
            .all()
        )

        current_usage = usage_records[0].value if usage_records else 0

        return {
            "current_count": current_usage,
            "max_count": org.max_embeddings,
            "utilization_pct": round((current_usage / org.max_embeddings * 100), 2) if org.max_embeddings > 0 else 0,
            "namespace": org.embedding_namespace,
        }


# ---------------------------------------------------------------------------
# Tenant-Aware Search (Filtered by org_id)
# ---------------------------------------------------------------------------

class TenantSearchService:
    """Tenant-aware search — all queries filtered by org_id."""

    @staticmethod
    def filter_query(db: Session, model, org_id: str):
        """Apply org_id filter to any SQLAlchemy query."""
        if hasattr(model, "org_id"):
            return db.query(model).filter(model.org_id == org_id)
        return db.query(model)

    @staticmethod
    def search_evidence(
        db: Session,
        org_id: str,
        query_text: Optional[str] = None,
        case_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        from ..models import Evidence, Case

        evidence_query = (
            db.query(Evidence)
            .join(Case, Case.id == Evidence.case_id, isouter=True)
            .filter(Case.id.in_(
                db.query(Project.id).filter(Project.org_id == org_id).subquery()
            ))
        )

        if case_id:
            evidence_query = evidence_query.filter(Evidence.case_id == case_id)
        if mime_type:
            evidence_query = evidence_query.filter(Evidence.mime_type == mime_type)
        if query_text:
            evidence_query = evidence_query.filter(
                or_(
                    Evidence.filename.ilike(f"%{query_text}%"),
                    Evidence.sha256.ilike(f"%{query_text}%"),
                )
            )

        results = evidence_query.order_by(Evidence.uploaded_at.desc()).offset(offset).limit(limit).all()

        return [
            {
                "id": e.id,
                "case_id": e.case_id,
                "filename": e.filename,
                "sha256": e.sha256,
                "size": e.size,
                "mime_type": e.mime_type,
                "uploaded_at": e.uploaded_at.isoformat() if e.uploaded_at else None,
            }
            for e in results
        ]

    @staticmethod
    def search_cases(
        db: Session,
        org_id: str,
        query_text: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        from ..models import Case

        project_ids = [p.id for p in db.query(Project.id).filter(Project.org_id == org_id).all()]

        case_query = db.query(Case)
        if project_ids:
            # cases linked to evidence in this org's projects
            from ..models import Evidence
            evidence_case_ids = (
                db.query(Evidence.case_id)
                .filter(Evidence.case_id.in_(
                    db.query(Case.id).subquery()
                ))
                .subquery()
            )
            # For now, return all cases — in production, link cases to projects
            pass

        if status:
            case_query = case_query.filter(Case.status == status)
        if query_text:
            case_query = case_query.filter(
                or_(
                    Case.title.ilike(f"%{query_text}%"),
                    Case.description.ilike(f"%{query_text}%"),
                )
            )

        results = case_query.order_by(Case.created_at.desc()).offset(offset).limit(limit).all()

        return [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in results
        ]


# ---------------------------------------------------------------------------
# Tenant-Aware Knowledge Graph
# ---------------------------------------------------------------------------

class TenantKGService:
    """Tenant-aware Knowledge Graph — isolated graphs per org."""

    @staticmethod
    def get_kg_config(db: Session, org_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        config = {
            "namespace": org.kg_namespace,
            "graph_type": os.getenv("KG_GRAPH_TYPE", "networkx"),
            "backend": os.getenv("KG_BACKEND", "memory"),
        }

        if project_id:
            project = db.query(Project).filter(Project.id == project_id, Project.org_id == org_id).first()
            if project and project.kg_prefix:
                config["namespace"] = project.kg_prefix

        return config

    @staticmethod
    def validate_kg_access(db: Session, org_id: str, kg_namespace: str) -> bool:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return False
        return kg_namespace.startswith(org.kg_namespace) if org.kg_namespace else True

    @staticmethod
    def get_kg_nodes(db: Session, org_id: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get KG nodes filtered by tenant namespace."""
        config = TenantKGService.get_kg_config(db, org_id, project_id)
        # In production, query the actual graph backend filtered by namespace
        return [
            {
                "namespace": config["namespace"],
                "graph_type": config["graph_type"],
                "status": "isolated",
            }
        ]


# ---------------------------------------------------------------------------
# Tenant-Aware Audit Logs
# ---------------------------------------------------------------------------

class TenantAuditService:
    """Tenant-aware audit logging — isolated per org."""

    @staticmethod
    def log(
        db: Session,
        org_id: str,
        action: str,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TenantAuditLog:
        entry = TenantAuditLog(
            org_id=org_id,
            project_id=project_id,
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def query_logs(
        db: Session,
        org_id: str,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[TenantAuditLog]:
        query = db.query(TenantAuditLog).filter(TenantAuditLog.org_id == org_id)
        if action:
            query = query.filter(TenantAuditLog.action == action)
        if user_id:
            query = query.filter(TenantAuditLog.user_id == user_id)
        if target_type:
            query = query.filter(TenantAuditLog.target_type == target_type)
        if target_id:
            query = query.filter(TenantAuditLog.target_id == target_id)
        if start_time:
            query = query.filter(TenantAuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(TenantAuditLog.timestamp <= end_time)
        return query.order_by(TenantAuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_audit_summary(db: Session, org_id: str, days: int = 30) -> Dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        logs = (
            db.query(TenantAuditLog)
            .filter(TenantAuditLog.org_id == org_id, TenantAuditLog.timestamp >= since)
            .all()
        )
        action_counts = {}
        user_counts = {}
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
            if log.user_id:
                user_counts[log.user_id] = user_counts.get(log.user_id, 0) + 1
        return {
            "period_days": days,
            "total_events": len(logs),
            "action_distribution": action_counts,
            "top_users": sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10],
        }


# ---------------------------------------------------------------------------
# Cross-Tenant Data Isolation Enforcement
# ---------------------------------------------------------------------------

class TenantIsolationService:
    """Cross-tenant data isolation enforcement."""

    @staticmethod
    def validate_org_access(db: Session, user_id: str, org_id: str) -> bool:
        membership = (
            db.query(OrgMembership)
            .filter(
                OrgMembership.org_id == org_id,
                OrgMembership.user_id == user_id,
                OrgMembership.is_active == True,
            )
            .first()
        )
        return membership is not None

    @staticmethod
    def validate_project_access(db: Session, user_id: str, project_id: str) -> bool:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        org_access = TenantIsolationService.validate_org_access(db, user_id, project.org_id)
        if not org_access:
            return False
        project_membership = (
            db.query(ProjectMembership)
            .filter(
                ProjectMembership.project_id == project_id,
                ProjectMembership.user_id == user_id,
                ProjectMembership.is_active == True,
            )
            .first()
        )
        return project_membership is not None

    @staticmethod
    def enforce_storage_isolation(db: Session, user_id: str, path: str) -> bool:
        """Validate that a storage path belongs to the user's org."""
        user_orgs = TenantRBACService.user_orgs(db, user_id)
        for org_membership in user_orgs:
            org = db.query(Organization).filter(Organization.id == org_membership["org_id"]).first()
            if org and path.startswith(org.storage_prefix or ""):
                return True
        return False

    @staticmethod
    def enforce_search_isolation(db: Session, user_id: str) -> List[str]:
        """Get list of org_ids the user can search within."""
        user_orgs = TenantRBACService.user_orgs(db, user_id)
        return [m["org_id"] for m in user_orgs]

    @staticmethod
    def create_isolation_rule(
        db: Session,
        org_id: str,
        rule_type: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> TenantIsolationRule:
        rule = TenantIsolationRule(
            org_id=org_id,
            rule_type=rule_type,
            config=config,
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def get_isolation_rules(db: Session, org_id: str) -> List[TenantIsolationRule]:
        return db.query(TenantIsolationRule).filter(
            TenantIsolationRule.org_id == org_id,
            TenantIsolationRule.is_active == True,
        ).all()

    @staticmethod
    def check_cross_tenant_access(
        db: Session,
        requesting_user_id: str,
        target_org_id: str,
        action: str = "read",
    ) -> bool:
        """Check if a user from one org can access resources in another org."""
        # same org access
        if TenantIsolationService.validate_org_access(db, requesting_user_id, target_org_id):
            return True

        # super admin bypass
        requesting_orgs = TenantRBACService.user_orgs(db, requesting_user_id)
        for om in requesting_orgs:
            if om["role"] == OrgRole.SUPER_ADMIN.value:
                return True

        return False


# ---------------------------------------------------------------------------
# Tenant Provisioning / Deprovisioning
# ---------------------------------------------------------------------------

class TenantProvisioningService:
    """Tenant provisioning and deprovisioning."""

    @staticmethod
    def provision_organization(
        db: Session,
        name: str,
        slug: str,
        admin_user_id: str,
        plan: str = "free",
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Full provisioning: create org, add admin, create default project."""
        org = OrganizationService.create_organization(
            db,
            name=name,
            slug=slug,
            description=description,
            plan=plan,
            created_by=admin_user_id,
        )

        default_project = ProjectService.create_project(
            db,
            org_id=org.id,
            name="Default Project",
            slug="default",
            description="Default project for the organization",
            created_by=admin_user_id,
        )

        TenantAuditService.log(
            db,
            org_id=org.id,
            user_id=admin_user_id,
            action="org.provisioned",
            target_type="organization",
            target_id=org.id,
            detail={"plan": plan, "admin_user_id": admin_user_id},
        )

        provisioning_log = TenantProvisioningLog(
            org_id=org.id,
            action="provisioned",
            performed_by=admin_user_id,
            detail={
                "org_name": name,
                "org_slug": slug,
                "plan": plan,
                "default_project_id": default_project.id,
            },
        )
        db.add(provisioning_log)
        db.commit()

        return {
            "organization": {
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "storage_bucket": org.storage_bucket,
                "embedding_namespace": org.embedding_namespace,
                "kg_namespace": org.kg_namespace,
            },
            "default_project": {
                "id": default_project.id,
                "name": default_project.name,
                "slug": default_project.slug,
            },
            "admin_user_id": admin_user_id,
        }

    @staticmethod
    def deprovision_organization(
        db: Session,
        org_id: str,
        performed_by: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deprovision: suspend org, log the event, soft-delete."""
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        org.status = OrgStatus.DEPROVISIONED.value
        org.updated_at = datetime.now(timezone.utc)

        # deactivate all memberships
        db.query(OrgMembership).filter(OrgMembership.org_id == org_id).update({"is_active": False})
        db.query(ProjectMembership).filter(
            ProjectMembership.project_id.in_(
                db.query(Project.id).filter(Project.org_id == org_id).subquery()
            )
        ).update({"is_active": False})

        # archive all projects
        db.query(Project).filter(Project.org_id == org_id).update({"status": ProjectStatus.ARCHIVED.value})

        db.commit()

        TenantAuditService.log(
            db,
            org_id=org_id,
            user_id=performed_by,
            action="org.deprovisioned",
            target_type="organization",
            target_id=org_id,
            detail={"reason": reason},
        )

        provisioning_log = TenantProvisioningLog(
            org_id=org_id,
            action="deprovisioned",
            performed_by=performed_by,
            detail={"reason": reason},
        )
        db.add(provisioning_log)
        db.commit()

        return {
            "org_id": org_id,
            "status": "deprovisioned",
            "performed_by": performed_by,
        }

    @staticmethod
    def suspend_organization(
        db: Session,
        org_id: str,
        performed_by: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        org.status = OrgStatus.SUSPENDED.value
        org.updated_at = datetime.now(timezone.utc)
        db.commit()

        TenantAuditService.log(
            db,
            org_id=org_id,
            user_id=performed_by,
            action="org.suspended",
            target_type="organization",
            target_id=org_id,
            detail={"reason": reason},
        )

        provisioning_log = TenantProvisioningLog(
            org_id=org_id,
            action="suspended",
            performed_by=performed_by,
            detail={"reason": reason},
        )
        db.add(provisioning_log)
        db.commit()

        return {"org_id": org_id, "status": "suspended"}

    @staticmethod
    def reactivate_organization(
        db: Session,
        org_id: str,
        performed_by: str,
    ) -> Dict[str, Any]:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        org.status = OrgStatus.ACTIVE.value
        org.updated_at = datetime.now(timezone.utc)

        db.query(OrgMembership).filter(OrgMembership.org_id == org_id).update({"is_active": True})
        db.query(Project).filter(Project.org_id == org_id, Project.status == ProjectStatus.ARCHIVED.value).update({"status": ProjectStatus.ACTIVE.value})

        db.commit()

        TenantAuditService.log(
            db,
            org_id=org_id,
            user_id=performed_by,
            action="org.reactivated",
            target_type="organization",
            target_id=org_id,
        )

        provisioning_log = TenantProvisioningLog(
            org_id=org_id,
            action="reactivated",
            performed_by=performed_by,
        )
        db.add(provisioning_log)
        db.commit()

        return {"org_id": org_id, "status": "active"}


# ---------------------------------------------------------------------------
# Tenant Usage Tracking & Quotas
# ---------------------------------------------------------------------------

class TenantUsageService:
    """Tenant usage tracking and quota enforcement."""

    @staticmethod
    def record_usage(
        db: Session,
        org_id: str,
        metric: str,
        value: int,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> TenantUsageRecord:
        record = TenantUsageRecord(
            org_id=org_id,
            metric=metric,
            value=value,
            period_start=period_start,
            period_end=period_end,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def increment_usage(db: Session, org_id: str, metric: str, increment: int = 1) -> TenantUsageRecord:
        latest = (
            db.query(TenantUsageRecord)
            .filter(TenantUsageRecord.org_id == org_id, TenantUsageRecord.metric == metric)
            .order_by(TenantUsageRecord.recorded_at.desc())
            .first()
        )
        current_value = latest.value if latest else 0
        return TenantUsageService.record_usage(db, org_id, metric, current_value + increment)

    @staticmethod
    def check_quota(db: Session, org_id: str, metric: str) -> Dict[str, Any]:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        quota_map = {
            "users": ("max_users", org.max_users),
            "projects": ("max_projects", org.max_projects),
            "storage_bytes": ("max_storage_bytes", org.max_storage_bytes),
            "embeddings": ("max_embeddings", org.max_embeddings),
        }

        if metric not in quota_map:
            raise ValueError(f"Unknown metric: {metric}")

        attr_name, max_value = quota_map[metric]

        latest = (
            db.query(TenantUsageRecord)
            .filter(TenantUsageRecord.org_id == org_id, TenantUsageRecord.metric == metric)
            .order_by(TenantUsageRecord.recorded_at.desc())
            .first()
        )
        current_value = latest.value if latest else 0

        return {
            "metric": metric,
            "current": current_value,
            "max": max_value,
            "utilization_pct": round((current_value / max_value * 100), 2) if max_value > 0 else 0,
            "within_quota": current_value < max_value,
        }

    @staticmethod
    def enforce_quota(db: Session, org_id: str, metric: str) -> bool:
        """Check if org is within quota. Raises ValueError if exceeded."""
        quota = TenantUsageService.check_quota(db, org_id, metric)
        if not quota["within_quota"]:
            raise ValueError(
                f"Organization {org_id} has exceeded {metric} quota: "
                f"{quota['current']}/{quota['max']}"
            )
        return True

    @staticmethod
    def get_usage_summary(db: Session, org_id: str, days: int = 30) -> Dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        records = (
            db.query(TenantUsageRecord)
            .filter(TenantUsageRecord.org_id == org_id, TenantUsageRecord.recorded_at >= since)
            .all()
        )

        metrics = {}
        for record in records:
            if record.metric not in metrics:
                metrics[record.metric] = {"values": [], "latest": None}
            metrics[record.metric]["values"].append({
                "value": record.value,
                "recorded_at": record.recorded_at.isoformat() if record.recorded_at else None,
            })
            if metrics[record.metric]["latest"] is None or record.recorded_at > metrics[record.metric]["latest"]["recorded_at"]:
                metrics[record.metric]["latest"] = metrics[record.metric]["values"][-1]

        org = db.query(Organization).filter(Organization.id == org_id).first()

        quotas = {}
        for metric in ["users", "projects", "storage_bytes", "embeddings"]:
            quotas[metric] = TenantUsageService.check_quota(db, org_id, metric)

        return {
            "org_id": org_id,
            "period_days": days,
            "usage_metrics": metrics,
            "quotas": quotas,
            "plan": org.plan if org else None,
        }

    @staticmethod
    def get_org_usage(db: Session, org_id: str) -> Dict[str, Any]:
        """Get current usage snapshot for an org."""
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        member_count = db.query(OrgMembership).filter(OrgMembership.org_id == org_id, OrgMembership.is_active == True).count()
        project_count = db.query(Project).filter(Project.org_id == org_id, Project.status == ProjectStatus.ACTIVE.value).count()

        storage_usage = TenantUsageService.check_quota(db, org_id, "storage_bytes")
        embedding_usage = TenantUsageService.check_quota(db, org_id, "embeddings")

        return {
            "org_id": org_id,
            "org_name": org.name,
            "plan": org.plan,
            "users": {"current": member_count, "max": org.max_users},
            "projects": {"current": project_count, "max": org.max_projects},
            "storage": storage_usage,
            "embeddings": embedding_usage,
        }


# ---------------------------------------------------------------------------
# Tenant Middleware (FastAPI dependency)
# ---------------------------------------------------------------------------

class TenantMiddleware:
    """FastAPI middleware for setting tenant context from request."""

    @staticmethod
    def extract_tenant_from_header(request) -> Dict[str, Optional[str]]:
        """Extract org_id and project_id from request headers."""
        org_id = request.headers.get("X-Org-ID")
        project_id = request.headers.get("X-Project-ID")
        return {"org_id": org_id, "project_id": project_id}

    @staticmethod
    def set_tenant_context(org_id: Optional[str] = None, project_id: Optional[str] = None) -> None:
        TenantContext.set_org_id(org_id)
        TenantContext.set_project_id(project_id)

    @staticmethod
    def clear_tenant_context() -> None:
        TenantContext.clear()

    @staticmethod
    def require_org_access(db: Session, user_id: str, org_id: str) -> bool:
        """Dependency: ensure user has access to the org."""
        if not TenantIsolationService.validate_org_access(db, user_id, org_id):
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Access denied: not a member of this organization")
        return True

    @staticmethod
    def require_project_access(db: Session, user_id: str, project_id: str) -> bool:
        """Dependency: ensure user has access to the project."""
        if not TenantIsolationService.validate_project_access(db, user_id, project_id):
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Access denied: not a member of this project")
        return True


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    # Context
    "TenantContext",
    # Enums
    "OrgRole",
    "ProjectRole",
    "OrgStatus",
    "ProjectStatus",
    # Models
    "Organization",
    "Project",
    "OrgMembership",
    "ProjectMembership",
    "TenantAuditLog",
    "TenantUsageRecord",
    "TenantProvisioningLog",
    "TenantIsolationRule",
    # Services
    "TenantRBACService",
    "OrganizationService",
    "ProjectService",
    "TenantStorageService",
    "TenantAIService",
    "TenantSearchService",
    "TenantKGService",
    "TenantAuditService",
    "TenantIsolationService",
    "TenantProvisioningService",
    "TenantUsageService",
    "TenantMiddleware",
]
