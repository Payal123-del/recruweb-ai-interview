import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities import Company, Job


@pytest.mark.asyncio
async def test_tenant_data_isolation(client: AsyncClient, db_session: AsyncSession):
    """
    CRITICAL TEST: Verifies Company A cannot read or mutate Company B's jobs or data.
    """
    # 1. Login as Apex Robotics Recruiter (Company A)
    login_apex = await client.post("/api/v1/auth/login", json={
        "email": "recruiter@apexrobotics.io",
        "password": "ApexSecurePass2026!"
    })
    assert login_apex.status_code == 200
    apex_token = login_apex.json()["data"]["access_token"]
    apex_headers = {"Authorization": f"Bearer {apex_token}"}

    # 2. Fetch Jobs as Company A
    resp_apex = await client.get("/api/v1/jobs", headers=apex_headers)
    assert resp_apex.status_code == 200
    apex_jobs = resp_apex.json()["data"]
    assert len(apex_jobs) >= 1
    apex_job_id = apex_jobs[0]["id"]

    # 3. Login as Boston Cybernetics Recruiter (Company B)
    login_boston = await client.post("/api/v1/auth/login", json={
        "email": "recruiter@bostoncyber.com",
        "password": "BostonSecurePass2026!"
    })
    assert login_boston.status_code == 200
    boston_token = login_boston.json()["data"]["access_token"]
    boston_headers = {"Authorization": f"Bearer {boston_token}"}

    # 4. Boston Cybernetics attempts to directly access Apex Robotics Job via ID (IDOR Attack)
    resp_tamper = await client.get(f"/api/v1/jobs/{apex_job_id}", headers=boston_headers)
    # Must fail with 404 / 403 because it belongs to Company A
    assert resp_tamper.status_code in [403, 404]

    # 5. Boston Cybernetics lists their own jobs -> should NOT include Apex Robotics job
    resp_boston_jobs = await client.get("/api/v1/jobs", headers=boston_headers)
    assert resp_boston_jobs.status_code == 200
    boston_job_ids = [j["id"] for j in resp_boston_jobs.json()["data"]]
    assert apex_job_id not in boston_job_ids
