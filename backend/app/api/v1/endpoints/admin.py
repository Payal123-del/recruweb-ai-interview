from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyRead
from app.schemas.user import UserCreate, UserRead
from app.schemas.analytics import SuperAdminAnalytics
from app.schemas.common import StandardResponse, MessageResponse
from app.services.company_service import CompanyService
from app.services.user_service import UserService
from app.services.dataset_analytics_service import AnalyticsService
from app.services.audit_service import AuditService
from app.api.deps import require_super_admin
from app.models.entities import User

router = APIRouter(prefix="/admin", tags=["Super Admin Operations"])


@router.get("/analytics", response_model=StandardResponse[SuperAdminAnalytics])
async def get_super_admin_analytics(
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    analytics = await AnalyticsService.get_super_admin_analytics(db)
    return StandardResponse(data=analytics)


@router.get("/companies", response_model=StandardResponse[List[CompanyRead]])
async def list_all_companies(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    companies = await CompanyService.list_companies(db, skip=skip, limit=limit)
    return StandardResponse(data=[CompanyRead.model_validate(c) for c in companies])


@router.post("/companies", response_model=StandardResponse[CompanyRead])
async def create_company(
    request: Request,
    payload: CompanyCreate,
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    company = await CompanyService.create_company(db, payload)
    await AuditService.log_action(
        db=db,
        action="CREATE_COMPANY",
        resource_type="COMPANY",
        resource_id=company.id,
        user_id=current_admin.id,
        user_email=current_admin.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Company created successfully", data=CompanyRead.model_validate(company))


@router.patch("/companies/{company_id}", response_model=StandardResponse[CompanyRead])
async def update_company(
    request: Request,
    company_id: str,
    payload: CompanyUpdate,
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    company = await CompanyService.update_company(db, company_id, payload)
    await AuditService.log_action(
        db=db,
        action="UPDATE_COMPANY",
        resource_type="COMPANY",
        resource_id=company.id,
        user_id=current_admin.id,
        user_email=current_admin.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Company updated successfully", data=CompanyRead.model_validate(company))


@router.post("/companies/{company_id}/admin", response_model=StandardResponse[UserRead])
async def create_company_administrator(
    request: Request,
    company_id: str,
    payload: UserCreate,
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    payload.tenant_id = company_id
    payload.role = "COMPANY_ADMIN"
    user = await UserService.create_user(db, payload)
    await AuditService.log_action(
        db=db,
        action="CREATE_COMPANY_ADMIN",
        resource_type="USER",
        resource_id=user.id,
        tenant_id=company_id,
        user_id=current_admin.id,
        user_email=current_admin.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Company Administrator created", data=UserRead.model_validate(user))


@router.get("/users", response_model=StandardResponse[List[UserRead]])
async def list_all_platform_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    users = await UserService.list_all_users(db, skip=skip, limit=limit)
    return StandardResponse(data=[UserRead.model_validate(u) for u in users])
