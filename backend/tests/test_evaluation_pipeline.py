import pytest
import os
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.entities import (
    Company, User, Job, Candidate, Question, Interview, Invitation,
    Answer, Evaluation, QuestionEvaluation, Report, InterviewStatus
)
from app.core.security import get_password_hash, create_access_token
from app.ai.engine import AIInterviewEngine
from app.ai.base import QuestionContext, AnswerContext


@pytest.mark.asyncio
async def test_internal_ai_engine_question_evaluation():
    engine = AIInterviewEngine(version="internal-v1")

    q = QuestionContext(
        question_id="test-q1",
        question_text="Explain Inverse Kinematics and how singularities are handled using Jacobian matrix.",
        category="Kinematics",
        question_type="TECHNICAL",
        difficulty="HARD",
        skills=["Kinematics", "C++"],
        expected_topics=["Inverse Kinematics", "Jacobian", "Singularities", "Damped Least Squares"]
    )

    ans = AnswerContext(
        question_id="test-q1",
        answer_text="Inverse Kinematics maps desired end-effector poses back to joint angles. Near singularities where the Jacobian matrix loses rank, we use damped least squares regularization to avoid infinite joint velocities.",
        duration_seconds=40.0
    )

    result = engine.evaluate_question(q, ans)

    assert result.score > 70.0
    assert result.technical_score > 70.0
    assert "Inverse Kinematics" in result.detected_topics
    assert "Jacobian" in result.detected_topics
    assert "Damped Least Squares" in result.detected_topics
    assert len(result.positive_indicators) >= 2
    assert len(result.explanation) > 10


@pytest.mark.asyncio
async def test_full_submission_and_detailed_evaluation_pipeline(client: AsyncClient, db_session: AsyncSession):
    # 1. Setup Tenant & Job
    company = Company(name="Cybernetics Corp", slug="cyber-corp", email="talent@cyber-corp.com")
    db_session.add(company)
    await db_session.flush()

    user = User(
        email="recruiter@cyber-corp.com",
        hashed_password=get_password_hash("Password123!"),
        full_name="Alex Recruiter",
        role="COMPANY_ADMIN",
        tenant_id=company.id,
        is_active=True
    )
    db_session.add(user)

    job = Job(
        tenant_id=company.id,
        title="Senior Robotics Manipulation Lead",
        department="Robotics",
        description="Lead robotics manipulation and trajectory planning.",
        required_skills=["C++", "ROS2", "Kinematics"]
    )
    db_session.add(job)
    await db_session.flush()

    cand = Candidate(
        tenant_id=company.id,
        name="Elena Rostova",
        email="elena.rostova@robotics.io",
        skills=["ROS2", "MoveIt", "Kinematics"]
    )
    db_session.add(cand)
    await db_session.flush()

    q1 = Question(
        category="Kinematics",
        question_text="Explain Jacobian singularities in robot arms.",
        question_type="TECHNICAL",
        difficulty="HARD",
        skills=["Kinematics"],
        expected_topics=["Jacobian", "Singularities", "Damped Least Squares"]
    )
    q2 = Question(
        category="Behavioral",
        question_text="Describe a time you solved a critical hardware failure on deadline.",
        question_type="BEHAVIORAL",
        difficulty="MEDIUM",
        skills=["Problem Solving"],
        expected_topics=["Situation", "Task", "Action", "Result"]
    )
    db_session.add_all([q1, q2])
    await db_session.flush()

    interview = Interview(
        tenant_id=company.id,
        job_id=job.id,
        candidate_id=cand.id,
        title="Elena Rostova Technical Assessment",
        interview_type="TECHNICAL",
        difficulty="HARD",
        status=InterviewStatus.SCHEDULED.value,
        scoring_weights={"technical": 0.5, "problem_solving": 0.25, "communication": 0.15, "behavioral": 0.1}
    )
    db_session.add(interview)
    await db_session.flush()

    token = "secure-elena-interview-token-2026"
    invitation = Invitation(
        tenant_id=company.id,
        interview_id=interview.id,
        candidate_email=cand.email,
        secure_token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db_session.add(invitation)
    await db_session.commit()

    # 2. Candidate verifies token
    v_res = await client.get(f"/api/v1/interviews/verify/{token}")
    assert v_res.status_code == 200
    assert v_res.json()["data"]["candidate_name"] == "Elena Rostova"

    # 3. Candidate submits answers
    payload = [
        {
            "question_id": q1.id,
            "answer_text": "In robotic arms, the Jacobian matrix relates joint velocities to Cartesian velocities. Near kinematic singularities, the Jacobian determinant vanishes, causing numerical instability. We implement damped least squares (Levenberg-Marquardt) to maintain bounded velocities.",
            "duration_seconds": 65.0
        },
        {
            "question_id": q2.id,
            "answer_text": "During our warehouse deployment, an optical encoder failed under severe vibration. Tasked with restoring navigation, I analyzed the sensor telemetry, deployed a Kalman filter noise rejection threshold in ROS2, and successfully restored 99.9% uptime before the operational deadline.",
            "duration_seconds": 70.0
        }
    ]

    sub_res = await client.post(f"/api/v1/interviews/submit/{token}", json=payload)
    assert sub_res.status_code == 200
    sub_data = sub_res.json()["data"]
    assert sub_data["status"] == "REPORT_GENERATED"
    assert sub_data["overall_score"] > 40.0
    assert sub_data["recommendation"] in ["STRONG_HIRE", "HIRE", "CONSIDER", "REJECT", "STRONG_REJECT"]

    # 4. Verify Database Persistence of Answers and Question Evaluations
    answers = (await db_session.execute(select(Answer).where(Answer.interview_id == interview.id))).scalars().all()
    assert len(answers) == 2

    evaluation = (await db_session.execute(select(Evaluation).where(Evaluation.interview_id == interview.id))).scalars().first()
    assert evaluation is not None
    assert evaluation.evaluation_status == "COMPLETED"
    assert evaluation.overall_score > 50.0

    q_evals = (await db_session.execute(select(QuestionEvaluation).where(QuestionEvaluation.evaluation_id == evaluation.id))).scalars().all()
    assert len(q_evals) == 2

    q1_eval = next(qe for qe in q_evals if qe.question_id == q1.id)
    assert "Jacobian" in q1_eval.detected_topics
    assert "Damped Least Squares" in q1_eval.detected_topics
    assert len(q1_eval.explanation) > 10

    q2_eval = next(qe for qe in q_evals if qe.question_id == q2.id)
    assert q2_eval.behavioral_score > 50.0

    # 5. Verify PDF Report Existence
    report = (await db_session.execute(select(Report).where(Report.interview_id == interview.id))).scalars().first()
    assert report is not None
    assert report.pdf_storage_key is not None
    assert os.path.exists(f"./storage_data/{report.pdf_storage_key}")

    # 6. Recruiter fetches detailed evaluation with question breakdown
    recruiter_token = create_access_token(
        subject=user.id,
        tenant_id=company.id,
        role="COMPANY_ADMIN",
        permissions=["report:view", "interview:view"]
    )
    headers = {"Authorization": f"Bearer {recruiter_token}"}

    det_res = await client.get(f"/api/v1/evaluations/{interview.id}/detailed", headers=headers)
    assert det_res.status_code == 200
    det_data = det_res.json()["data"]
    assert det_data["candidate_name"] == "Elena Rostova"
    assert det_data["job_title"] == "Senior Robotics Manipulation Lead"
    assert len(det_data["question_evaluations"]) == 2
    assert det_data["question_evaluations"][0]["score"] > 60.0
    assert len(det_data["question_evaluations"][0]["detected_topics"]) >= 2
