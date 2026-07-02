import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.auth_log import AuthLog

pytestmark = pytest.mark.asyncio

async def test_register_user_success(client: AsyncClient, db_session: AsyncSession):
    register_data = {
        "email": "testregister@example.com",
        "password": "Password123!",
        "full_name": "Test Register User",
        "terms_accepted": True
    }
    
    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    
    resp_json = response.json()
    assert resp_json["success"] is True
    assert "access_token" in resp_json["data"]
    assert "refresh_token" in resp_json["data"]
    assert resp_json["data"]["user"]["email"] == "testregister@example.com"
    
    # Check in DB
    stmt = select(User).where(User.email == "testregister@example.com")
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.full_name == "Test Register User"
    
    # Check log
    stmt_log = select(AuthLog).where(AuthLog.user_id == user.id)
    res_log = await db_session.execute(stmt_log)
    log = res_log.scalar_one_or_none()
    assert log is not None
    assert log.event_type == "register"
    assert log.success is True

async def test_register_validation_error(client: AsyncClient):
    # Weak password
    register_data = {
        "email": "invalidpassword@example.com",
        "password": "weak",
        "full_name": "Test Weak User",
        "terms_accepted": True
    }
    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"

async def test_login_user_success(client: AsyncClient, db_session: AsyncSession):
    # Register first
    register_data = {
        "email": "testlogin@example.com",
        "password": "Password123!",
        "full_name": "Test Login User",
        "terms_accepted": True
    }
    await client.post("/api/v1/auth/register", json=register_data)
    
    # Login
    login_data = {
        "email": "testlogin@example.com",
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["success"] is True
    assert "access_token" in resp_json["data"]
    assert resp_json["data"]["user"]["email"] == "testlogin@example.com"

async def test_login_incorrect_password_and_lockout(client: AsyncClient, db_session: AsyncSession):
    # Register first
    register_data = {
        "email": "testlockout@example.com",
        "password": "Password123!",
        "full_name": "Test Lockout User",
        "terms_accepted": True
    }
    await client.post("/api/v1/auth/register", json=register_data)
    
    # Try logging in 5 times with incorrect password
    login_data = {
        "email": "testlockout@example.com",
        "password": "WrongPassword!"
    }
    
    for i in range(5):
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
    
    # The 6th attempt should return a lockout error message
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "khóa tạm thời" in response.json()["message"]

async def test_get_me_success(client: AsyncClient):
    # Register and get access token
    register_data = {
        "email": "testme@example.com",
        "password": "Password123!",
        "full_name": "Test Me User",
        "terms_accepted": True
    }
    reg_resp = await client.post("/api/v1/auth/register", json=register_data)
    access_token = reg_resp.json()["data"]["access_token"]
    
    # Call GET /me with token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "testme@example.com"

async def test_token_refresh(client: AsyncClient):
    # Register and get refresh token
    register_data = {
        "email": "testrefresh@example.com",
        "password": "Password123!",
        "full_name": "Test Refresh User",
        "terms_accepted": True
    }
    reg_resp = await client.post("/api/v1/auth/register", json=register_data)
    refresh_token = reg_resp.json()["data"]["refresh_token"]
    
    # Refresh
    refresh_payload = {"refresh_token": refresh_token}
    response = await client.post("/api/v1/auth/refresh", json=refresh_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    assert "refresh_token" in response.json()["data"]

async def test_forgot_reset_password(client: AsyncClient, db_session: AsyncSession):
    # Register first
    register_data = {
        "email": "testreset@example.com",
        "password": "Password123!",
        "full_name": "Test Reset User",
        "terms_accepted": True
    }
    await client.post("/api/v1/auth/register", json=register_data)
    
    # Request reset
    response = await client.post("/api/v1/auth/forgot-password", json={"email": "testreset@example.com"})
    assert response.status_code == 200
    
    # We must find the generated reset token in DB since we can't read terminal output in test
    from app.models.password_reset_token import PasswordResetToken
    stmt = select(PasswordResetToken)
    result = await db_session.execute(stmt)
    reset_record = result.scalars().first()
    assert reset_record is not None
    assert reset_record.used is False
    
    token_hash = reset_record.token_hash
    
    # Commit or rollback the session's transaction to free it for the next endpoint request
    await db_session.rollback()
    
    # Use reset token to change password
    reset_data = {
        "token": token_hash,
        "new_password": "NewPassword123!"
    }
    response_reset = await client.post("/api/v1/auth/reset-password", json=reset_data)
    assert response_reset.status_code == 200
    
    # Try logging in with the old password (should fail)
    response_login_old = await client.post("/api/v1/auth/login", json={
        "email": "testreset@example.com",
        "password": "Password123!"
    })
    assert response_login_old.status_code == 401
    
    # Login with the new password (should succeed)
    response_login_new = await client.post("/api/v1/auth/login", json={
        "email": "testreset@example.com",
        "password": "NewPassword123!"
    })
    assert response_login_new.status_code == 200
