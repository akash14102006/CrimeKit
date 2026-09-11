"""Multi-Tenancy API routes for organizations, projects, members, and quotas."""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import database, models
from .auth import get_current_user
from .multitenancy import (
    Organization,
    OrganizationService,
    Project,
    ProjectService,
    ProjectStatus,
    TenantContext,
    TenantIsolationService,
    TenantMiddleware,
    TenantProvisioningService,
    TenantRBACService,
    TenantUsageService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


def _require_admin(current_user: models.User):
    roles = [r.name for r in current_user.roles]
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="forbidden: admin required")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Pydantic request models ──────────────────────────────────────────


class OrganizationCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class OrganizationUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    plan: Optional[str] = None


class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class MemberAddRequest(BaseModel):
    user_id: str
    role: str = "org_member"


class ProjectMemberAddRequest(BaseModel):
    user_id: str
    role: str = "project_member"


class QuotaUpdateRequest(BaseModel):
    quota_bytes: int


# ── Helpers ──────────────────────────────────────────────────────────


def _slugify(name: str) -> str:
    """Generate a URL-safe slug from a name."""
    import re
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


def _require_org_access(db: Session, user_id: str, org_id: str):
    """Validate user has access to the org, raise 403 otherwise."""
    if not TenantIsolationService.validate_org_access(db, user_id, org_id):
        raise HTTPException(status_code=403, detail="Access denied: not a member of this organization")


# ── 1. POST /organizations ───────────────────────────────────────────


@router.post("/organizations")
async def create_organization(
    body: OrganizationCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new organization."""
    _require_admin(current_user)
    try:
        slug = _slugify(body.name)
        org = OrganizationService.create_organization(
            db,
            name=body.name,
            slug=slug,
            description=body.description,
            created_by=current_user.id,
        )
        return JSONResponse(
            status_code=201,
            content={
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "description": org.description,
                "status": org.status,
                "plan": org.plan,
                "storage_bucket": org.storage_bucket,
                "embedding_namespace": org.embedding_namespace,
                "kg_namespace": org.kg_namespace,
                "created_at": org.created_at.isoformat() if org.created_at else None,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create organization: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 2. GET /organizations ────────────────────────────────────────────


@router.get("/organizations")
async def list_organizations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List organizations the current user belongs to."""
    user_orgs = TenantRBACService.user_orgs(db, current_user.id)
    org_ids = [m["org_id"] for m in user_orgs]

    orgs = db.query(Organization).filter(Organization.id.in_(org_ids)).all() if org_ids else []
    return JSONResponse(
        content={
            "organizations": [
                {
                    "id": o.id,
                    "name": o.name,
                    "slug": o.slug,
                    "description": o.description,
                    "status": o.status,
                    "plan": o.plan,
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                }
                for o in orgs
            ],
            "total": len(orgs),
        }
    )


# ── 3. GET /organizations/{org_id} ───────────────────────────────────


@router.get("/organizations/{org_id}")
async def get_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get organization details."""
    _require_org_access(db, current_user.id, org_id)

    org = OrganizationService.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return JSONResponse(
        content={
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "description": org.description,
            "status": org.status,
            "plan": org.plan,
            "storage_bucket": org.storage_bucket,
            "embedding_namespace": org.embedding_namespace,
            "kg_namespace": org.kg_namespace,
            "max_users": org.max_users,
            "max_projects": org.max_projects,
            "max_storage_bytes": org.max_storage_bytes,
            "max_embeddings": org.max_embeddings,
            "created_at": org.created_at.isoformat() if org.created_at else None,
            "updated_at": org.updated_at.isoformat() if org.updated_at else None,
        }
    )


# ── 4. PUT /organizations/{org_id} ───────────────────────────────────


@router.put("/organizations/{org_id}")
async def update_organization(
    org_id: str,
    body: OrganizationUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update an organization."""
    _require_admin(current_user)
    _require_org_access(db, current_user.id, org_id)

    update_fields = body.model_dump(exclude_unset=True)
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    org = OrganizationService.update_organization(db, org_id, **update_fields)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return JSONResponse(
        content={
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "description": org.description,
            "status": org.status,
            "plan": org.plan,
            "updated_at": org.updated_at.isoformat() if org.updated_at else None,
        }
    )


# ── 5. DELETE /organizations/{org_id} ─────────────────────────────────


@router.delete("/organizations/{org_id}")
async def deactivate_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Deactivate (deprovision) an organization."""
    _require_admin(current_user)
    _require_org_access(db, current_user.id, org_id)

    try:
        result = TenantProvisioningService.deprovision_organization(
            db, org_id, performed_by=current_user.id
        )
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── 6. POST /organizations/{org_id}/projects ─────────────────────────


@router.post("/organizations/{org_id}/projects")
async def create_project(
    org_id: str,
    body: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new project within an organization."""
    _require_admin(current_user)
    _require_org_access(db, current_user.id, org_id)

    try:
        slug = _slugify(body.name)
        project = ProjectService.create_project(
            db,
            org_id=org_id,
            name=body.name,
            slug=slug,
            description=body.description,
            created_by=current_user.id,
        )
        return JSONResponse(
            status_code=201,
            content={
                "id": project.id,
                "org_id": project.org_id,
                "name": project.name,
                "slug": project.slug,
                "description": project.description,
                "status": project.status,
                "storage_prefix": project.storage_prefix,
                "embedding_prefix": project.embedding_prefix,
                "kg_prefix": project.kg_prefix,
                "created_at": project.created_at.isoformat() if project.created_at else None,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create project: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 7. GET /organizations/{org_id}/projects ──────────────────────────


@router.get("/organizations/{org_id}/projects")
async def list_projects(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all projects in an organization."""
    _require_org_access(db, current_user.id, org_id)

    projects = ProjectService.list_org_projects(db, org_id)
    return JSONResponse(
        content={
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "description": p.description,
                    "status": p.status,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in projects
            ],
            "total": len(projects),
        }
    )


# ── 8. GET /organizations/{org_id}/projects/{project_id} ─────────────


@router.get("/organizations/{org_id}/projects/{project_id}")
async def get_project(
    org_id: str,
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get project details."""
    _require_org_access(db, current_user.id, org_id)

    project = ProjectService.get_project(db, project_id)
    if not project or project.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")

    return JSONResponse(
        content={
            "id": project.id,
            "org_id": project.org_id,
            "name": project.name,
            "slug": project.slug,
            "description": project.description,
            "status": project.status,
            "storage_prefix": project.storage_prefix,
            "embedding_prefix": project.embedding_prefix,
            "kg_prefix": project.kg_prefix,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        }
    )


# ── 9. PUT /organizations/{org_id}/projects/{project_id} ─────────────


@router.put("/organizations/{org_id}/projects/{project_id}")
async def update_project(
    org_id: str,
    project_id: str,
    body: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update a project."""
    _require_admin(current_user)
    _require_org_access(db, current_user.id, org_id)

    project = ProjectService.get_project(db, project_id)
    if not project or project.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")

    update_fields = body.model_dump(exclude_unset=True)
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = ProjectService.update_project(db, project_id, **update_fields)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")

    return JSONResponse(
        content={
            "id": updated.id,
            "org_id": updated.org_id,
            "name": updated.name,
            "slug": updated.slug,
            "description": updated.description,
            "status": updated.status,
            "updated_at": updated.updated_at.isoformat() if updated.updated_at else None,
        }
    )


# ── 10. DELETE /organizations/{org_id}/projects/{project_id} ──────────


@router.delete("/organizations/{org_id}/projects/{project_id}")
async def deactivate_project(
    org_id: str,
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Deactivate (archive) a project."""
    _require_admin(current_user)
    _require_org_access(db, current_user.id, org_id)

    project = ProjectService.get_project(db, project_id)
    if not project or project.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")

    archived = ProjectService.archive_project(db, project_id, archived_by=current_user.id)
    if not archived:
        raise HTTPException(status_code=404, detail="Project not found")

    return JSONResponse(
        content={"detail": "Project archived", "id": project_id, "status": archived.status}
    )


# ── 11. POST /organizations/{org_id}/members ─────────────────────────


@router.post("/organizations/{org_id}/members")
async def add_organization_member(
    org_id: str,
    body: MemberAddRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Add a member to an organization."""
    _require_admin(current_user)
    _require_org_access(db, current_user.id, org_id)

    try:
        membership = TenantRBACService.add_org_member(
            db,
            org_id=org_id,
            user_id=body.user_id,
            role=body.role,
            invited_by=current_user.id,
        )
        return JSONResponse(
            status_code=201,
            content={
                "id": membership.id,
                "org_id": membership.org_id,
                "user_id": membership.user_id,
                "role": membership.role,
                "is_active": membership.is_active,
                "joined_at": membership.joined_at.isoformat() if membership.joined_at else None,
            },
        )
    except Exception as e:
        logger.error("Failed to add member: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 12. GET /organizations/{org_id}/members ──────────────────────────


@router.get("/organizations/{org_id}/members")
async def list_organization_members(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all members of an organization."""
    _require_org_access(db, current_user.id, org_id)

    members = TenantRBACService.list_org_members(db, org_id)
    return JSONResponse(content={"members": members, "total": len(members)})


# ── 13. DELETE /organizations/{org_id}/members/{user_id} ─────────────


@router.delete("/organizations/{org_id}/members/{user_id}")
async def remove_organization_member(
    org_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Remove a member from an organization."""
    _require_admin(current_user)
    _require_org_access(db, current_user.id, org_id)

    removed = TenantRBACService.remove_org_member(db, org_id, user_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Member not found")

    return JSONResponse(content={"detail": "Member removed", "org_id": org_id, "user_id": user_id})


# ── 14. POST /organizations/{org_id}/projects/{project_id}/members ───


@router.post("/organizations/{org_id}/projects/{project_id}/members")
async def add_project_member(
    org_id: str,
    project_id: str,
    body: ProjectMemberAddRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Add a member to a project."""
    _require_admin(current_user)
    _require_org_access(db, current_user.id, org_id)

    project = ProjectService.get_project(db, project_id)
    if not project or project.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        membership = TenantRBACService.add_project_member(
            db,
            project_id=project_id,
            user_id=body.user_id,
            role=body.role,
            invited_by=current_user.id,
        )
        return JSONResponse(
            status_code=201,
            content={
                "id": membership.id,
                "project_id": membership.project_id,
                "user_id": membership.user_id,
                "role": membership.role,
                "is_active": membership.is_active,
                "joined_at": membership.joined_at.isoformat() if membership.joined_at else None,
            },
        )
    except Exception as e:
        logger.error("Failed to add project member: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 15. GET /organizations/{org_id}/projects/{project_id}/members ─────


@router.get("/organizations/{org_id}/projects/{project_id}/members")
async def list_project_members(
    org_id: str,
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all members of a project."""
    _require_org_access(db, current_user.id, org_id)

    project = ProjectService.get_project(db, project_id)
    if not project or project.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")

    members = TenantRBACService.list_project_members(db, project_id)
    return JSONResponse(content={"members": members, "total": len(members)})


# ── 16. GET /organizations/{org_id}/usage ─────────────────────────────


@router.get("/organizations/{org_id}/usage")
async def get_usage_statistics(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get usage statistics for an organization."""
    _require_org_access(db, current_user.id, org_id)

    try:
        usage = TenantUsageService.get_org_usage(db, org_id)
        return JSONResponse(content=usage)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── 17. POST /organizations/{org_id}/quota ───────────────────────────


@router.post("/organizations/{org_id}/quota")
async def update_storage_quota(
    org_id: str,
    body: QuotaUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update storage quota for an organization."""
    _require_admin(current_user)
    _require_org_access(db, current_user.id, org_id)

    org = OrganizationService.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    org.max_storage_bytes = body.quota_bytes
    org.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(org)

    return JSONResponse(
        content={
            "id": org.id,
            "max_storage_bytes": org.max_storage_bytes,
            "updated_at": org.updated_at.isoformat() if org.updated_at else None,
        }
    )


# ── 18. GET /context ─────────────────────────────────────────────────


@router.get("/context")
async def get_tenant_context(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get current tenant context from request headers."""
    tenant_info = TenantMiddleware.extract_tenant_from_header(request)
    org_id = tenant_info.get("org_id")
    project_id = tenant_info.get("project_id")

    result = {
        "user_id": current_user.id,
        "org_id": org_id,
        "project_id": project_id,
        "org_access": False,
        "project_access": False,
    }

    if org_id:
        result["org_access"] = TenantIsolationService.validate_org_access(db, current_user.id, org_id)
        org = OrganizationService.get_organization(db, org_id)
        if org:
            result["org_name"] = org.name
            result["org_status"] = org.status
            result["org_plan"] = org.plan

    if project_id:
        result["project_access"] = TenantIsolationService.validate_project_access(db, current_user.id, project_id)
        project = ProjectService.get_project(db, project_id)
        if project:
            result["project_name"] = project.name
            result["project_status"] = project.status

    result["user_orgs"] = TenantRBACService.user_orgs(db, current_user.id)

    return JSONResponse(content=result)
