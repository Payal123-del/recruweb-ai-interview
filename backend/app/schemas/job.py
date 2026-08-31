from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.entities import JobStatus


class JobBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    department: Optional[str] = "Engineering"
    description: str = Field(..., min_length=10)
    location: Optional[str] = "Remote"
    employment_type: str = "Full-time"
    experience_level: str = "Mid-Senior"
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    salary_range: Optional[str] = "$120k - $160k"
    status: str = JobStatus.PUBLISHED.value


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    salary_range: Optional[str] = None
    status: Optional[str] = None


class JobRead(JobBase):
    id: str
    tenant_id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    candidate_count: Optional[int] = 0
    interview_count: Optional[int] = 0

    class Config:
        from_attributes = True
