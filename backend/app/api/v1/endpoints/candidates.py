from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateRead, CandidateStatusUpdate
from app.schemas.common import StandardResponse
from app.services.job_candidate_service import CandidateService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user, get_current_active_tenant, require_permission
from app.models.entities import User

router = APIRouter(prefix="/candidates", tags=["Candidate Management"])


@router.get("", response_model=StandardResponse[List[CandidateRead]])
async def list_candidates(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    candidates = await CandidateService.list_candidates(db, tenant_id=tenant_id, status=status, skip=skip, limit=limit)
    return StandardResponse(data=[CandidateRead.model_validate(c) for c in candidates])


@router.post("", response_model=StandardResponse[CandidateRead])
async def create_candidate(
    request: Request,
    payload: CandidateCreate,
    current_user: User = Depends(require_permission("candidate:create")),
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    candidate = await CandidateService.create_candidate(db, tenant_id=tenant_id, data=payload)
    await AuditService.log_action(
        db=db,
        action="ADD_CANDIDATE",
        resource_type="CANDIDATE",
        resource_id=candidate.id,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Candidate added successfully", data=CandidateRead.model_validate(candidate))


@router.get("/{candidate_id}", response_model=StandardResponse[CandidateRead])
async def get_candidate(
    candidate_id: str,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    candidate = await CandidateService.get_candidate(db, tenant_id=tenant_id, candidate_id=candidate_id)
    return StandardResponse(data=CandidateRead.model_validate(candidate))


@router.patch("/{candidate_id}/status", response_model=StandardResponse[CandidateRead])
async def update_candidate_status(
    request: Request,
    candidate_id: str,
    payload: CandidateStatusUpdate,
    current_user: User = Depends(require_permission("candidate:update")),
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    candidate = await CandidateService.update_status(db, tenant_id=tenant_id, candidate_id=candidate_id, data=payload)
    await AuditService.log_action(
        db=db,
        action=f"CANDIDATE_STATUS_{payload.status}",
        resource_type="CANDIDATE",
        resource_id=candidate.id,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        details={"status": payload.status, "notes": payload.notes},
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Candidate status updated", data=CandidateRead.model_validate(candidate))
