from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, HttpUrl, Field


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100)
    logo: Optional[str] = None
    industry: Optional[str] = "Robotics & Automation"
    website: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    country: Optional[str] = "United States"
    timezone: Optional[str] = "UTC"
    subscription_plan: Optional[str] = "ENTERPRISE"


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    logo: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = None
    subscription_plan: Optional[str] = None


class CompanyRead(CompanyBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyStats(BaseModel):
    total_jobs: int
    active_jobs: int
    total_candidates: int
    scheduled_interviews: int
    completed_interviews: int
    average_score: float
    shortlisted_count: int
    rejected_count: int
