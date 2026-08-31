from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class CompanyAnalytics(BaseModel):
    total_jobs: int
    active_jobs: int
    total_candidates: int
    scheduled_interviews: int
    completed_interviews: int
    average_score: float
    shortlist_rate: float
    rejection_rate: float
    score_distribution: Dict[str, int]
    skill_performance: List[Dict[str, Any]]
    monthly_trends: List[Dict[str, Any]]


class SuperAdminAnalytics(BaseModel):
    total_companies: int
    active_companies: int
    total_users: int
    total_candidates: int
    total_interviews: int
    completed_interviews: int
    platform_avg_score: float
    company_growth: List[Dict[str, Any]]
    platform_activity: List[Dict[str, Any]]
