from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class QuestionEvaluationRead(BaseModel):
    id: Optional[str] = None
    question_id: str
    question_text: Optional[str] = None
    category: Optional[str] = None
    candidate_answer: Optional[str] = None
    score: float
    relevance_score: float
    technical_score: float
    completeness_score: float
    communication_score: float
    problem_solving_score: float
    behavioral_score: float
    detected_topics: List[str] = []
    missing_topics: List[str] = []
    positive_indicators: List[str] = []
    negative_indicators: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    explanation: str = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EvaluationRead(BaseModel):
    id: str
    tenant_id: str
    interview_id: str
    evaluation_status: str = "COMPLETED"
    relevance_score: float
    technical_score: float
    communication_score: float
    completeness_score: float
    problem_solving_score: float
    behavioral_score: float
    overall_score: float
    confidence_indicator: float
    strengths: List[str] = []
    weaknesses: List[str] = []
    missing_topics: List[str] = []
    question_breakdown: List[Dict[str, Any]] = []
    recommendation: str
    engine_version: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DetailedEvaluationRead(BaseModel):
    interview_id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    job_id: str
    job_title: str
    interview_title: str
    interview_type: str
    status: str
    evaluation: Optional[EvaluationRead] = None
    question_evaluations: List[QuestionEvaluationRead] = []
    scoring_weights: Dict[str, float] = {}
    pdf_download_url: Optional[str] = None
    recruiter_decision: Optional[str] = None
    recruiter_notes: Optional[str] = None
