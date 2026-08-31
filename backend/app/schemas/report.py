from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.schemas.evaluation import EvaluationRead
from app.schemas.candidate import CandidateRead
from app.schemas.job import JobRead


class ReportRead(BaseModel):
    id: str
    tenant_id: str
    interview_id: str
    candidate_id: str
    pdf_storage_key: Optional[str] = None
    pdf_download_url: Optional[str] = None
    recruiter_decision: Optional[str] = None
    recruiter_notes: Optional[str] = None
    is_published_to_candidate: bool
    created_at: datetime
    updated_at: datetime

    candidate: Optional[CandidateRead] = None
    job: Optional[JobRead] = None
    evaluation: Optional[EvaluationRead] = None

    class Config:
        from_attributes = True


class RecruiterDecisionUpdate(BaseModel):
    decision: str  # SHORTLISTED, REJECTED, UNDER_REVIEW
    notes: Optional[str] = None
    is_published_to_candidate: Optional[bool] = None
