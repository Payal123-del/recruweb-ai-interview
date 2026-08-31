from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.entities import Job, Candidate, Interview, JobStatus, CandidateStatus
from app.schemas.job import JobCreate, JobUpdate, JobRead
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateStatusUpdate
from app.core.exceptions import NotFoundException, ConflictException


class JobService:
    @staticmethod
    async def create_job(db: AsyncSession, tenant_id: str, data: JobCreate, user_id: Optional[str] = None) -> Job:
        job = Job(
            tenant_id=tenant_id,
            created_by=user_id,
            **data.model_dump()
        )
        db.add(job)
        await db.flush()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_job(db: AsyncSession, tenant_id: str, job_id: str) -> Job:
        query = select(Job).where(and_(Job.id == job_id, Job.tenant_id == tenant_id))
        result = await db.execute(query)
        job = result.scalars().first()
        if not job:
            raise NotFoundException("Job not found in this company workspace")
        return job

    @staticmethod
    async def list_jobs(
        db: AsyncSession,
        tenant_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Job]:
        query = select(Job).where(Job.tenant_id == tenant_id)
        if status:
            query = query.where(Job.status == status)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_job(db: AsyncSession, tenant_id: str, job_id: str, data: JobUpdate) -> Job:
        job = await JobService.get_job(db, tenant_id, job_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(job, key, value)
        await db.flush()
        await db.refresh(job)
        return job

    @staticmethod
    async def delete_job(db: AsyncSession, tenant_id: str, job_id: str) -> bool:
        job = await JobService.get_job(db, tenant_id, job_id)
        job.status = JobStatus.ARCHIVED.value
        await db.flush()
        return True


class CandidateService:
    @staticmethod
    async def create_candidate(db: AsyncSession, tenant_id: str, data: CandidateCreate) -> Candidate:
        # Check if candidate already exists in this tenant
        query = select(Candidate).where(and_(Candidate.tenant_id == tenant_id, Candidate.email == data.email.lower()))
        existing = (await db.execute(query)).scalars().first()
        if existing:
            raise ConflictException(f"Candidate with email '{data.email}' already exists in your workspace")

        candidate = Candidate(
            tenant_id=tenant_id,
            name=data.name,
            email=data.email.lower(),
            phone=data.phone,
            resume_url=data.resume_url,
            skills=data.skills,
            experience_years=data.experience_years,
            education=data.education,
            status=data.status
        )
        db.add(candidate)
        await db.flush()
        await db.refresh(candidate)
        return candidate

    @staticmethod
    async def get_candidate(db: AsyncSession, tenant_id: str, candidate_id: str) -> Candidate:
        query = select(Candidate).where(and_(Candidate.id == candidate_id, Candidate.tenant_id == tenant_id))
        result = await db.execute(query)
        candidate = result.scalars().first()
        if not candidate:
            raise NotFoundException("Candidate not found in this company workspace")
        return candidate

    @staticmethod
    async def list_candidates(
        db: AsyncSession,
        tenant_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Candidate]:
        query = select(Candidate).where(Candidate.tenant_id == tenant_id)
        if status:
            query = query.where(Candidate.status == status)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_status(db: AsyncSession, tenant_id: str, candidate_id: str, data: CandidateStatusUpdate) -> Candidate:
        candidate = await CandidateService.get_candidate(db, tenant_id, candidate_id)
        candidate.status = data.status
        await db.flush()
        await db.refresh(candidate)
        return candidate
