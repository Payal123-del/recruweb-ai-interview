from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field as PydanticField


class FieldRoleRead(BaseModel):
    id: str
    field_id: str
    role_name: str
    description: Optional[str] = None
    default_skills: List[str] = []
    experience_levels: List[str] = []

    class Config:
        from_attributes = True


class FieldSkillRead(BaseModel):
    id: str
    field_id: str
    skill_name: str
    category: str
    importance_weight: float

    class Config:
        from_attributes = True


class FieldCompetencyRead(BaseModel):
    id: str
    field_id: str
    competency_name: str
    description: Optional[str] = None
    default_weight: float
    rubric_guidelines: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class FieldRead(BaseModel):
    id: str
    name: str
    slug: str
    category: str
    description: Optional[str] = None
    icon: Optional[str] = "Briefcase"
    is_active: bool = True
    is_custom: bool = False
    created_at: datetime
    roles: List[FieldRoleRead] = []
    skills: List[FieldSkillRead] = []

    class Config:
        from_attributes = True


class FieldCreate(BaseModel):
    name: str
    category: str = "General Engineering"
    description: Optional[str] = None
    icon: Optional[str] = "Briefcase"
    roles: List[str] = []
    skills: List[str] = []


class FieldUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class ProfileAnalysisRequest(BaseModel):
    resume_text: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[float] = 0.0
    education: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None


class DetectedFieldItem(BaseModel):
    field: str
    confidence: float
    matched_skills: List[str] = []
    suggested_roles: List[str] = []
    reasoning: str = ""


class FieldDetectionResponse(BaseModel):
    detected_fields: List[DetectedFieldItem]
    top_recommended_field: str
    skills_extracted: List[str] = []


class CustomInterviewConfigureRequest(BaseModel):
    field_name: str
    target_role: Optional[str] = None
    interview_type: str = "TECHNICAL"
    difficulty: str = "MEDIUM"
    is_adaptive: bool = False
    experience_level: str = "Mid-Level"
    focus_skills: List[str] = []
    num_questions: int = 5
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
