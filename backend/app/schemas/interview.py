from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.entities import InterviewType, DifficultyLevel, InterviewStatus
from app.schemas.question import QuestionRead


class InterviewCreate(BaseModel):
    job_id: str
    candidate_id: str
    title: str = Field(..., min_length=2)
    interview_type: str = InterviewType.TECHNICAL.value
    difficulty: str = DifficultyLevel.MEDIUM.value
    num_questions: int = 5
    time_limit_minutes: int = 45
    camera_required: bool = True
    mic_required: bool = True
    recording_enabled: bool = True
    allow_candidate_result_view: bool = False
    scoring_weights: Dict[str, float] = {
        "technical": 0.45,
        "problem_solving": 0.25,
        "communication": 0.15,
        "behavioral": 0.15
    }
    candidate_instructions: Optional[str] = "Please ensure your camera and microphone are functional in a quiet environment."
    question_ids: Optional[List[str]] = None


class InterviewUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    candidate_instructions: Optional[str] = None
    allow_candidate_result_view: Optional[bool] = None


class InvitationRead(BaseModel):
    id: str
    secure_token: str
    candidate_email: str
    is_used: bool
    is_revoked: bool
    expires_at: datetime
    invitation_url: Optional[str] = None

    class Config:
        from_attributes = True


class InterviewRead(BaseModel):
    id: str
    tenant_id: str
    job_id: str
    candidate_id: str
    title: str
    interview_type: str
    difficulty: str
    num_questions: int
    time_limit_minutes: int
    camera_required: bool
    mic_required: bool
    recording_enabled: bool
    allow_candidate_result_view: bool
    scoring_weights: Dict[str, float]
    candidate_instructions: Optional[str] = None
    status: str
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    job_title: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    invitation: Optional[InvitationRead] = None
    questions: Optional[List[QuestionRead]] = []

    class Config:
        from_attributes = True


class InterviewVerificationResponse(BaseModel):
    valid: bool
    interview_id: str
    tenant_name: str
    job_title: str
    candidate_name: str
    candidate_email: str
    candidate_skills: Optional[List[str]] = []
    candidate_education: Optional[str] = None
    candidate_experience_years: Optional[float] = 0.0
    field_name: Optional[str] = "Universal"
    target_role: Optional[str] = None
    interview_type: str
    difficulty: str
    is_adaptive: Optional[bool] = False
    focus_skills: Optional[List[str]] = []
    time_limit_minutes: int
    camera_required: bool
    mic_required: bool
    recording_enabled: bool
    candidate_instructions: Optional[str]
    num_questions: int
    questions: List[Dict[str, Any]] = []
    detected_fields: Optional[List[Dict[str, Any]]] = []
    all_fields: Optional[List[Dict[str, Any]]] = []



class AnswerSubmission(BaseModel):
    question_id: str
    answer_text: str
    duration_seconds: float = 0.0
    recording_storage_key: Optional[str] = None
    mime_type: Optional[str] = "video/webm"
    file_size_bytes: Optional[int] = 0
