from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.analytics import CompanyAnalytics
from app.schemas.dataset import DatasetCreate, DatasetRead, DatasetVersionRead, ModelVersionRead
from app.schemas.audit import AuditLogRead
from app.schemas.common import StandardResponse
from app.services.dataset_analytics_service import AnalyticsService, DatasetService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user, get_current_active_tenant, require_super_admin, require_permission
from app.models.entities import User

router = APIRouter(tags=["Analytics, AI Datasets & Audit"])


# 1. Company Analytics
@router.get("/analytics/overview", response_model=StandardResponse[CompanyAnalytics])
async def get_company_analytics(
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    analytics = await AnalyticsService.get_company_analytics(db, tenant_id=tenant_id)
    return StandardResponse(data=analytics)


# 2. AI Datasets & Model Versions (Super Admin)
@router.get("/datasets", response_model=StandardResponse[List[DatasetRead]])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    datasets = await DatasetService.list_datasets(db, skip=skip, limit=limit)
    return StandardResponse(data=[DatasetRead.model_validate(d) for d in datasets])


@router.post("/datasets", response_model=StandardResponse[DatasetRead])
async def create_dataset(
    request: Request,
    payload: DatasetCreate,
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    ds = await DatasetService.create_dataset(db, payload)
    await AuditService.log_action(
        db=db,
        action="CREATE_AI_DATASET",
        resource_type="DATASET",
        resource_id=ds.id,
        user_id=current_admin.id,
        user_email=current_admin.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="AI Dataset created", data=DatasetRead.model_validate(ds))


@router.post("/datasets/{dataset_id}/upload-version", response_model=StandardResponse[DatasetVersionRead])
async def upload_dataset_version(
    request: Request,
    dataset_id: str,
    version_tag: str = Form(...),
    file: UploadFile = File(...),
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    file_bytes = await file.read()
    version = await DatasetService.validate_and_upload_version(
        db=db,
        dataset_id=dataset_id,
        version_tag=version_tag,
        file_bytes=file_bytes,
        filename=file.filename or "dataset.csv"
    )
    await AuditService.log_action(
        db=db,
        action="UPLOAD_DATASET_VERSION",
        resource_type="DATASET_VERSION",
        resource_id=version.id,
        user_id=current_admin.id,
        user_email=current_admin.email,
        details={"version_tag": version_tag, "records": version.records_count, "status": version.validation_status},
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Dataset version validated and recorded", data=DatasetVersionRead.model_validate(version))


@router.get("/models/versions", response_model=StandardResponse[List[ModelVersionRead]])
async def list_model_versions(
    current_admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    models = await DatasetService.list_model_versions(db)
    return StandardResponse(data=[ModelVersionRead.model_validate(m) for m in models])


# 3. Audit Logs
@router.get("/audit-logs", response_model=StandardResponse[List[AuditLogRead]])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Super Admins see all logs, Company users only see their tenant's logs
    tenant_id = None if current_user.is_superuser else current_user.tenant_id
    logs = await AuditService.get_logs(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return StandardResponse(data=[AuditLogRead.model_validate(l) for l in logs])
