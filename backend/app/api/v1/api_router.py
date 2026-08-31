from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    admin,
    companies,
    jobs,
    candidates,
    questions,
    interviews,
    recordings,
    evaluations_reports,
    analytics_datasets_audit,
    fields
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(companies.router)
api_router.include_router(jobs.router)
api_router.include_router(candidates.router)
api_router.include_router(questions.router)
api_router.include_router(interviews.router)
api_router.include_router(recordings.router)
api_router.include_router(evaluations_reports.router)
api_router.include_router(analytics_datasets_audit.router)
api_router.include_router(fields.router)

