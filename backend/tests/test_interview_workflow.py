import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_interview_lifecycle(client: AsyncClient):
    # 1. Login as Company Recruiter
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "recruiter@apexrobotics.io",
        "password": "ApexSecurePass2026!"
    })
    assert login_resp.status_code == 200
    recruiter_token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {recruiter_token}"}

    # 2. Fetch Job and Candidate
    jobs_resp = await client.get("/api/v1/jobs", headers=headers)
    job_id = jobs_resp.json()["data"][0]["id"]

    cand_resp = await client.post("/api/v1/candidates", headers=headers, json={
        "name": "Dr. Alan Turing",
        "email": "alan.turing@autonomy.ai",
        "skills": ["Algorithms", "State Machines", "Robotics Navigation"],
        "experience_years": 8.0
    })
    assert cand_resp.status_code == 200
    candidate_id = cand_resp.json()["data"]["id"]

    # 3. Create Interview
    interview_payload = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        "title": "Principal Robotics Autonomous Systems Interview",
        "interview_type": "TECHNICAL",
        "difficulty": "HARD",
        "num_questions": 2,
        "time_limit_minutes": 30
    }
    int_resp = await client.post("/api/v1/interviews", headers=headers, json=interview_payload)
    assert int_resp.status_code == 200
    invitation = int_resp.json()["data"]["invitation"]
    assert invitation is not None
    secure_token = invitation["secure_token"]

    # 4. Candidate verifies token (public endpoint)
    verify_resp = await client.get(f"/api/v1/interviews/verify/{secure_token}")
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()["data"]
    assert verify_data["valid"] is True
    questions = verify_data["questions"]
    assert len(questions) > 0

    # 5. Candidate submits answers
    submit_payload = [
        {
            "question_id": q["id"],
            "answer_text": (
                "To optimize autonomous navigation and kinematic trajectory planning in a 6-DOF robotic manipulator, "
                "we formulate Inverse Kinematics with damped least squares to avoid Jacobian singularities and use "
                "an Extended Kalman Filter fusing IMU and LiDAR odometry for robust SLAM state estimation."
            ),
            "duration_seconds": 110.0
        }
        for q in questions
    ]
    submit_resp = await client.post(f"/api/v1/interviews/submit/{secure_token}", json=submit_payload)
    assert submit_resp.status_code == 200
    eval_res = submit_resp.json()["data"]
    assert eval_res["overall_score"] >= 50.0
    assert eval_res["recommendation"] in ["STRONG_HIRE", "HIRE", "CONSIDER"]

    # 6. Verify token cannot be reused
    reuse_resp = await client.get(f"/api/v1/interviews/verify/{secure_token}")
    assert reuse_resp.status_code == 403

    # 7. Recruiter views reports and shortlists candidate
    reports_resp = await client.get("/api/v1/reports", headers=headers)
    assert reports_resp.status_code == 200
    reports = reports_resp.json()["data"]
    matching_report = next((r for r in reports if r["candidate_id"] == candidate_id), None)
    assert matching_report is not None

    decision_resp = await client.patch(
        f"/api/v1/reports/{matching_report['id']}/decision",
        headers=headers,
        json={"decision": "SHORTLISTED", "notes": "Top tier candidate. Excellent SLAM response."}
    )
    assert decision_resp.status_code == 200
    assert decision_resp.json()["data"]["recruiter_decision"] == "SHORTLISTED"
