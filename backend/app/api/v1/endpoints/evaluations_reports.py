import os
from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.schemas.evaluation import EvaluationRead, DetailedEvaluationRead
from app.schemas.report import ReportRead, RecruiterDecisionUpdate
from app.schemas.candidate import CandidateRead
from app.schemas.job import JobRead
from app.schemas.common import StandardResponse, MessageResponse
from app.services.audit_service import AuditService
from app.services.interview_service import InterviewService
from app.api.deps import get_current_user, get_current_active_tenant, require_permission
from app.models.entities import User, Evaluation, Report, Interview, Candidate, Job
from app.core.exceptions import NotFoundException, ForbiddenException

router = APIRouter(tags=["Evaluations & Reports"])


@router.get("/evaluations/{interview_id}", response_model=StandardResponse[EvaluationRead])
async def get_interview_evaluation(
    interview_id: str,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    query = select(Evaluation).where(and_(Evaluation.interview_id == interview_id, Evaluation.tenant_id == tenant_id))
    result = await db.execute(query)
    eval_record = result.scalars().first()
    if not eval_record:
        raise NotFoundException("Evaluation not yet generated for this interview")
    return StandardResponse(data=EvaluationRead.model_validate(eval_record))


@router.get("/evaluations/{interview_id}/detailed", response_model=StandardResponse[DetailedEvaluationRead])
async def get_detailed_interview_evaluation(
    interview_id: str,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    detailed_data = await InterviewService.get_detailed_interview_evaluation(db, interview_id=interview_id, tenant_id=tenant_id)
    return StandardResponse(data=DetailedEvaluationRead(**detailed_data))


@router.get("/reports", response_model=StandardResponse[List[ReportRead]])
async def list_reports(
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    query = select(Report).where(Report.tenant_id == tenant_id).order_by(Report.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    reports = list(result.scalars().all())

    items = []
    for r in reports:
        cand = await db.get(Candidate, r.candidate_id)
        it = await db.get(Interview, r.interview_id)
        job = await db.get(Job, it.job_id) if it else None
        ev = (await db.execute(select(Evaluation).where(Evaluation.interview_id == r.interview_id))).scalars().first()

        items.append(ReportRead(
            id=r.id,
            tenant_id=r.tenant_id,
            interview_id=r.interview_id,
            candidate_id=r.candidate_id,
            pdf_storage_key=r.pdf_storage_key,
            pdf_download_url=f"/api/v1/reports/{r.id}/download" if r.pdf_storage_key else None,
            recruiter_decision=r.recruiter_decision,
            recruiter_notes=r.recruiter_notes,
            is_published_to_candidate=r.is_published_to_candidate,
            created_at=r.created_at,
            updated_at=r.updated_at,
            candidate=CandidateRead.model_validate(cand) if cand else None,
            job=JobRead.model_validate(job) if job else None,
            evaluation=EvaluationRead.model_validate(ev) if ev else None
        ))

    return StandardResponse(data=items)


@router.get("/reports/{report_id}", response_model=StandardResponse[ReportRead])
async def get_report_details(
    report_id: str,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    query = select(Report).where(and_(Report.id == report_id, Report.tenant_id == tenant_id))
    report = (await db.execute(query)).scalars().first()
    if not report:
        raise NotFoundException("Report not found")

    cand = await db.get(Candidate, report.candidate_id)
    it = await db.get(Interview, report.interview_id)
    job = await db.get(Job, it.job_id) if it else None
    ev = (await db.execute(select(Evaluation).where(Evaluation.interview_id == report.interview_id))).scalars().first()

    return StandardResponse(data=ReportRead(
        id=report.id,
        tenant_id=report.tenant_id,
        interview_id=report.interview_id,
        candidate_id=report.candidate_id,
        pdf_storage_key=report.pdf_storage_key,
        pdf_download_url=f"/api/v1/reports/{report.id}/download" if report.pdf_storage_key else None,
        recruiter_decision=report.recruiter_decision,
        recruiter_notes=report.recruiter_notes,
        is_published_to_candidate=report.is_published_to_candidate,
        created_at=report.created_at,
        updated_at=report.updated_at,
        candidate=CandidateRead.model_validate(cand) if cand else None,
        job=JobRead.model_validate(job) if job else None,
        evaluation=EvaluationRead.model_validate(ev) if ev else None
    ))


@router.patch("/reports/{report_id}/decision", response_model=StandardResponse[ReportRead])
async def update_recruiter_decision(
    request: Request,
    report_id: str,
    payload: RecruiterDecisionUpdate,
    current_user: User = Depends(require_permission("report:view")),
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    query = select(Report).where(and_(Report.id == report_id, Report.tenant_id == tenant_id))
    report = (await db.execute(query)).scalars().first()
    if not report:
        raise NotFoundException("Report not found")

    report.recruiter_decision = payload.decision
    if payload.notes is not None:
        report.recruiter_notes = payload.notes
    if payload.is_published_to_candidate is not None:
        report.is_published_to_candidate = payload.is_published_to_candidate

    # Update candidate status as well
    candidate = await db.get(Candidate, report.candidate_id)
    if candidate:
        if payload.decision == "SHORTLISTED":
            candidate.status = "SHORTLISTED"
        elif payload.decision == "REJECTED":
            candidate.status = "REJECTED"
        elif payload.decision == "UNDER_REVIEW":
            candidate.status = "UNDER_REVIEW"

    await db.flush()
    await db.refresh(report)

    await AuditService.log_action(
        db=db,
        action=f"RECRUITER_DECISION_{payload.decision}",
        resource_type="REPORT",
        resource_id=report.id,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        details={"decision": payload.decision, "notes": payload.notes},
        ip_address=request.client.host if request.client else None
    )

    return StandardResponse(message="Recruiter decision recorded", data=ReportRead.model_validate(report))


@router.get("/reports/{report_id}/download")
async def download_report_pdf(
    report_id: str,
    tenant_id: str = Depends(get_current_active_tenant),
    db: AsyncSession = Depends(get_db)
):
    query = select(Report).where(and_(Report.id == report_id, Report.tenant_id == tenant_id))
    report = (await db.execute(query)).scalars().first()
    if not report or not report.pdf_storage_key:
        raise NotFoundException("PDF report is not available for this interview")

    file_path = os.path.join(os.path.abspath(settings.STORAGE_LOCAL_DIR), report.pdf_storage_key.replace("..", "").lstrip("/\\"))
    if not os.path.exists(file_path):
        raise NotFoundException("Report file missing on storage")

    return FileResponse(file_path, media_type="application/pdf", filename=f"interview_report_{report_id}.pdf")
