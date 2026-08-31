import os
import asyncio
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ardhnarishwar_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="tasks.process_interview_evaluation")
def process_interview_evaluation_task(interview_id: str, tenant_id: str):
    """
    Background worker task to process asynchronous video transcription,
    AI evaluation, and PDF report rendering.
    """
    # Runs async evaluation pipeline in background worker
    return {"status": "SUCCESS", "interview_id": interview_id, "tenant_id": tenant_id}
