from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionRead
from app.schemas.common import StandardResponse
from app.services.interview_service import QuestionService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user, get_current_active_tenant, require_permission
from app.models.entities import User

router = APIRouter(prefix="/questions", tags=["Question Bank"])


@router.get("", response_model=StandardResponse[List[QuestionRead]])
async def list_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    questions = await QuestionService.list_questions(
        db, tenant_id=tenant_id, category=category, difficulty=difficulty, skip=skip, limit=limit
    )
    return StandardResponse(data=[QuestionRead.model_validate(q) for q in questions])


@router.post("", response_model=StandardResponse[QuestionRead])
async def create_question(
    request: Request,
    payload: QuestionCreate,
    current_user: User = Depends(require_permission("question:create")),
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.is_superuser:
        payload.tenant_id = tenant_id  # Force tenant scoping for regular company users

    question = await QuestionService.create_question(db, data=payload, user_id=current_user.id)
    await AuditService.log_action(
        db=db,
        action="CREATE_QUESTION",
        resource_type="QUESTION",
        resource_id=question.id,
        tenant_id=payload.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None
    )
    return StandardResponse(message="Question created successfully", data=QuestionRead.model_validate(question))


@router.get("/{question_id}", response_model=StandardResponse[QuestionRead])
async def get_question(
    question_id: str,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    question = await QuestionService.get_question(db, question_id=question_id, tenant_id=tenant_id)
    return StandardResponse(data=QuestionRead.model_validate(question))
