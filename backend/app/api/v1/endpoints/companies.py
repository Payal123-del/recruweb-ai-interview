from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.company import CompanyRead, CompanyUpdate, CompanyStats
from app.schemas.user import UserRead, UserCreate
from app.schemas.common import StandardResponse
from app.services.company_service import CompanyService
from app.services.user_service import UserService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user, get_current_active_tenant, require_permission, verify_tenant_access
from app.models.entities import User

router = APIRouter(prefix="/companies", tags=["Tenant Workspace"])


@router.get("/current", response_model=StandardResponse[CompanyRead])
async def get_current_company_details(
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    company = await CompanyService.get_company_by_id(db, tenant_id)
    return StandardResponse(data=CompanyRead.model_validate(company))


@router.get("/current/stats", response_model=StandardResponse[CompanyStats])
async def get_current_company_stats(
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    stats = await CompanyService.get_company_stats(db, tenant_id)
    return StandardResponse(data=stats)


@router.patch("/current", response_model=StandardResponse[CompanyRead])
async def update_current_company(
    request: Request,
    payload: CompanyUpdate,
    current_user: User = Depends(require_permission("company:update")),
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    company = await CompanyService.update_company(db, tenant_id, payload)
    await AuditService.log_action(
        db=db,
        action="UPDATE_COMPANY_PROFILE",
        resource_type="COMPANY",
        resource_id=tenant_id,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Company details updated", data=CompanyRead.model_validate(company))


@router.get("/current/team", response_model=StandardResponse[List[UserRead]])
async def list_team_members(
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    users = await UserService.list_company_users(db, tenant_id=tenant_id)
    return StandardResponse(data=[UserRead.model_validate(u) for u in users])


@router.post("/current/team", response_model=StandardResponse[UserRead])
async def invite_team_member(
    request: Request,
    payload: UserCreate,
    current_user: User = Depends(require_permission("user:create")),
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    payload.tenant_id = tenant_id
    user = await UserService.create_user(db, payload)
    await AuditService.log_action(
        db=db,
        action="INVITE_TEAM_MEMBER",
        resource_type="USER",
        resource_id=user.id,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Team member invited successfully", data=UserRead.model_validate(user))
