from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.entities import QuestionType, DifficultyLevel


class QuestionBase(BaseModel):
    category: str = "Robotics & Controls"
    question_text: str = Field(..., min_length=5)
    question_type: str = QuestionType.TECHNICAL.value
    difficulty: str = DifficultyLevel.MEDIUM.value
    skills: List[str] = []
    expected_topics: List[str] = []
    time_limit_seconds: int = 120
    scoring_rubric: Dict[str, Any] = {}


class QuestionCreate(QuestionBase):
    tenant_id: Optional[str] = None  # None for global question bank


class QuestionUpdate(BaseModel):
    category: Optional[str] = None
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    difficulty: Optional[str] = None
    skills: Optional[List[str]] = None
    expected_topics: Optional[List[str]] = None
    time_limit_seconds: Optional[int] = None
    scoring_rubric: Optional[Dict[str, Any]] = None


class QuestionRead(QuestionBase):
    id: str
    tenant_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
