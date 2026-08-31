from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobRead
from app.schemas.common import StandardResponse, MessageResponse
from app.services.job_candidate_service import JobService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user, get_current_active_tenant, require_permission
from app.models.entities import User

router = APIRouter(prefix="/jobs", tags=["Job Postings"])


@router.get("", response_model=StandardResponse[List[JobRead]])
async def list_jobs(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    jobs = await JobService.list_jobs(db, tenant_id=tenant_id, status=status, skip=skip, limit=limit)
    return StandardResponse(data=[JobRead.model_validate(j) for j in jobs])


@router.post("", response_model=StandardResponse[JobRead])
async def create_job(
    request: Request,
    payload: JobCreate,
    current_user: User = Depends(require_permission("job:create")),
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    job = await JobService.create_job(db, tenant_id=tenant_id, data=payload, user_id=current_user.id)
    await AuditService.log_action(
        db=db,
        action="CREATE_JOB",
        resource_type="JOB",
        resource_id=job.id,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Job posting created", data=JobRead.model_validate(job))


@router.get("/{job_id}", response_model=StandardResponse[JobRead])
async def get_job_details(
    job_id: str,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    job = await JobService.get_job(db, tenant_id=tenant_id, job_id=job_id)
    return StandardResponse(data=JobRead.model_validate(job))


@router.patch("/{job_id}", response_model=StandardResponse[JobRead])
async def update_job(
    request: Request,
    job_id: str,
    payload: JobUpdate,
    current_user: User = Depends(require_permission("job:update")),
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    job = await JobService.update_job(db, tenant_id=tenant_id, job_id=job_id, data=payload)
    await AuditService.log_action(
        db=db,
        action="UPDATE_JOB",
        resource_type="JOB",
        resource_id=job.id,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Job updated successfully", data=JobRead.model_validate(job))


@router.delete("/{job_id}", response_model=StandardResponse[MessageResponse])
async def delete_job(
    request: Request,
    job_id: str,
    current_user: User = Depends(require_permission("job:delete")),
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    await JobService.delete_job(db, tenant_id=tenant_id, job_id=job_id)
    await AuditService.log_action(
        db=db,
        action="ARCHIVE_JOB",
        resource_type="JOB",
        resource_id=job_id,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(data=MessageResponse(message="Job archived successfully"))
