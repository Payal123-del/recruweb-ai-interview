import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rbac_super_admin_protection(client: AsyncClient):
    """
    CRITICAL TEST: Ensures regular company admins/recruiters cannot access Super Admin endpoints.
    """
    # Login as Company Recruiter
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "recruiter@apexrobotics.io",
        "password": "ApexSecurePass2026!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to access Super Admin analytics
    admin_resp = await client.get("/api/v1/admin/analytics", headers=headers)
    assert admin_resp.status_code == 403

    # Attempt to list all platform companies
    comp_resp = await client.get("/api/v1/admin/companies", headers=headers)
    assert comp_resp.status_code == 403


@pytest.mark.asyncio
async def test_super_admin_access(client: AsyncClient):
    """
    Verifies Super Admin can access platform-wide analytics and company lists.
    """
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "admin@ardhnarishwar.ai",
        "password": "AdminSecurePassword123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    analytics_resp = await client.get("/api/v1/admin/analytics", headers=headers)
    assert analytics_resp.status_code == 200
    assert "total_companies" in analytics_resp.json()["data"]
