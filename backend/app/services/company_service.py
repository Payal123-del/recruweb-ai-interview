from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.entities import Company, User, Job, Candidate, Interview, InterviewStatus, JobStatus, CandidateStatus
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyStats
from app.core.exceptions import NotFoundException, ConflictException


class CompanyService:
    @staticmethod
    async def create_company(db: AsyncSession, data: CompanyCreate) -> Company:
        # Check uniqueness of slug and email
        existing_slug = await db.execute(select(Company).where(Company.slug == data.slug))
        if existing_slug.scalars().first():
            raise ConflictException(f"Company slug '{data.slug}' already exists")
        
        existing_email = await db.execute(select(Company).where(Company.email == data.email))
        if existing_email.scalars().first():
            raise ConflictException(f"Company email '{data.email}' already registered")

        company = Company(**data.model_dump())
        db.add(company)
        await db.flush()
        await db.refresh(company)
        return company

    @staticmethod
    async def get_company_by_id(db: AsyncSession, company_id: str) -> Company:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalars().first()
        if not company:
            raise NotFoundException("Company not found")
        return company

    @staticmethod
    async def get_company_by_slug(db: AsyncSession, slug: str) -> Optional[Company]:
        result = await db.execute(select(Company).where(Company.slug == slug))
        return result.scalars().first()

    @staticmethod
    async def list_companies(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Company]:
        result = await db.execute(select(Company).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def update_company(db: AsyncSession, company_id: str, data: CompanyUpdate) -> Company:
        company = await CompanyService.get_company_by_id(db, company_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(company, key, value)
        await db.flush()
        await db.refresh(company)
        return company

    @staticmethod
    async def get_company_stats(db: AsyncSession, company_id: str) -> CompanyStats:
        total_jobs = (await db.execute(select(func.count(Job.id)).where(Job.tenant_id == company_id))).scalar_one() or 0
        active_jobs = (await db.execute(select(func.count(Job.id)).where(and_(Job.tenant_id == company_id, Job.status == JobStatus.PUBLISHED.value)))).scalar_one() or 0
        total_candidates = (await db.execute(select(func.count(Candidate.id)).where(Candidate.tenant_id == company_id))).scalar_one() or 0
        
        scheduled = (await db.execute(select(func.count(Interview.id)).where(and_(Interview.tenant_id == company_id, Interview.status.in_([InterviewStatus.PENDING.value, InterviewStatus.SCHEDULED.value]))))).scalar_one() or 0
        completed = (await db.execute(select(func.count(Interview.id)).where(and_(Interview.tenant_id == company_id, Interview.status == InterviewStatus.COMPLETED.value)))).scalar_one() or 0
        
        shortlisted = (await db.execute(select(func.count(Candidate.id)).where(and_(Candidate.tenant_id == company_id, Candidate.status == CandidateStatus.SHORTLISTED.value)))).scalar_one() or 0
        rejected = (await db.execute(select(func.count(Candidate.id)).where(and_(Candidate.tenant_id == company_id, Candidate.status == CandidateStatus.REJECTED.value)))).scalar_one() or 0

        # Average score calculation from evaluations
        from app.models.entities import Evaluation
        avg_score_res = (await db.execute(select(func.avg(Evaluation.overall_score)).where(Evaluation.tenant_id == company_id))).scalar_one()
        average_score = round(float(avg_score_res), 1) if avg_score_res is not None else 0.0

        return CompanyStats(
            total_jobs=total_jobs,
            active_jobs=active_jobs,
            total_candidates=total_candidates,
            scheduled_interviews=scheduled,
            completed_interviews=completed,
            average_score=average_score,
            shortlisted_count=shortlisted,
            rejected_count=rejected
        )
