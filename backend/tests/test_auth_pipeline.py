import pytest
import jwt
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company, User, UserRoleType
from app.core.security import get_password_hash, create_access_token, create_refresh_token
from app.core.config import settings


@pytest.mark.asyncio
async def test_auth_login_success(client: AsyncClient, db_session: AsyncSession):
    # 1. Create company and user
    company = Company(name="Auth Test Corp", slug="auth-test-corp", email="talent@authtest.com")
    db_session.add(company)
    await db_session.flush()

    user = User(
        email="authuser@authtest.com",
        hashed_password=get_password_hash("ValidPassword123!"),
        full_name="Auth Test User",
        role=UserRoleType.COMPANY_ADMIN.value,
        tenant_id=company.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    # 2. Test login
    res = await client.post("/api/v1/auth/login", json={
        "email": "authuser@authtest.com",
        "password": "ValidPassword123!"
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_auth_valid_access_token(client: AsyncClient, db_session: AsyncSession):
    company = Company(name="Valid Corp", slug="valid-corp", email="contact@validcorp.com")
    db_session.add(company)
    await db_session.flush()

    user = User(
        email="valid@validcorp.com",
        hashed_password=get_password_hash("ValidPass123!"),
        full_name="Valid Admin",
        role=UserRoleType.COMPANY_ADMIN.value,
        tenant_id=company.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(subject=user.id, tenant_id=company.id, role=user.role)
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["email"] == "valid@validcorp.com"
    assert res.json()["data"]["company_name"] == "Valid Corp"


@pytest.mark.asyncio
async def test_auth_expired_access_token(client: AsyncClient, db_session: AsyncSession):
    company = Company(name="Expired Corp", slug="expired-corp", email="contact@expiredcorp.com")
    db_session.add(company)
    await db_session.flush()

    user = User(
        email="expired@expiredcorp.com",
        hashed_password=get_password_hash("ExpiredPass123!"),
        full_name="Expired User",
        role=UserRoleType.COMPANY_ADMIN.value,
        tenant_id=company.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    # Create expired token
    token = create_access_token(
        subject=user.id,
        tenant_id=company.id,
        role=user.role,
        expires_delta=timedelta(minutes=-30)
    )
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 401
    assert "Invalid or expired" in res.json()["message"]


@pytest.mark.asyncio
async def test_auth_invalid_and_missing_tokens(client: AsyncClient):
    # Missing token
    res_missing = await client.get("/api/v1/auth/me")
    assert res_missing.status_code == 401
    assert "required" in res_missing.json()["message"].lower()

    # Corrupted / forged token
    res_invalid = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer forged-garbage-token-string"})
    assert res_invalid.status_code == 401


@pytest.mark.asyncio
async def test_auth_refresh_token_rotation(client: AsyncClient, db_session: AsyncSession):
    company = Company(name="Refresh Corp", slug="refresh-corp", email="info@refreshcorp.com")
    db_session.add(company)
    await db_session.flush()

    user = User(
        email="refresher@refreshcorp.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Refresher",
        role=UserRoleType.COMPANY_ADMIN.value,
        tenant_id=company.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    refresh_token = create_refresh_token(subject=user.id, tenant_id=company.id)

    # 1. Attempt to use refresh token directly as access token (should fail)
    res_bad_type = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert res_bad_type.status_code == 401
    assert "expected 'access'" in res_bad_type.json()["message"]

    # 2. Call /api/v1/auth/refresh to rotate tokens
    res_refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res_refresh.status_code == 200
    new_data = res_refresh.json()["data"]
    assert "access_token" in new_data
    assert "refresh_token" in new_data

    # 3. New access token works
    res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {new_data['access_token']}"})
    assert res_me.status_code == 200
    assert res_me.json()["data"]["email"] == "refresher@refreshcorp.com"


@pytest.mark.asyncio
async def test_auth_inactive_user_rejected(client: AsyncClient, db_session: AsyncSession):
    company = Company(name="Inactive Corp", slug="inactive-corp", email="info@inactivecorp.com")
    db_session.add(company)
    await db_session.flush()

    user = User(
        email="inactive@inactivecorp.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Inactive User",
        role=UserRoleType.COMPANY_ADMIN.value,
        tenant_id=company.id,
        is_active=False
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(subject=user.id, tenant_id=company.id, role=user.role)
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 403
    assert "inactive" in res.json()["message"].lower()
