from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from app.models.entities import CandidateStatus


class CandidateBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[float] = 0.0
    education: Optional[str] = "B.S. in Robotics / Computer Science"
    status: str = CandidateStatus.INVITED.value


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[str] = None
    status: Optional[str] = None


class CandidateRead(CandidateBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
