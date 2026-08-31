from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class QuestionContext(BaseModel):
    question_id: str
    question_text: str
    category: str
    question_type: str
    difficulty: str
    field_name: str = "Universal"
    role_name: Optional[str] = None
    skills: List[str] = []
    expected_topics: List[str] = []
    scoring_rubric: Dict[str, Any] = {}


class AnswerContext(BaseModel):
    question_id: str
    answer_text: str
    duration_seconds: float = 0.0


class QuestionEvaluationResult(BaseModel):
    question_id: str
    score: float
    relevance_score: float
    technical_score: float
    completeness_score: float
    communication_score: float
    problem_solving_score: float
    behavioral_score: float
    domain_score: float = 0.0
    detected_topics: List[str] = []
    missing_topics: List[str] = []
    positive_indicators: List[str] = []
    negative_indicators: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    feedback: str = ""
    explanation: str = ""


class OverallEvaluationResult(BaseModel):
    relevance_score: float
    technical_score: float
    communication_score: float
    completeness_score: float
    problem_solving_score: float
    behavioral_score: float
    domain_score: float = 0.0
    overall_score: float
    confidence_indicator: float
    field_name: str = "Universal"
    target_role: Optional[str] = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    missing_topics: List[str] = []
    improvement_suggestions: List[Dict[str, Any]] = []
    question_breakdown: List[Dict[str, Any]] = []
    recommendation: str
    engine_version: str = "universal-v1.0"


class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, question: QuestionContext, answer: AnswerContext) -> Dict[str, Any]:
        pass

