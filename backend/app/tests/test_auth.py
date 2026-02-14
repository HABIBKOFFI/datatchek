import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@datatchek.com",
                "password": "StrongPass123",
                "full_name": "New User",
                "company_name": "TestCorp",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@datatchek.com"
        assert data["full_name"] == "New User"
        assert "hashed_password" not in data
        assert "id" in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@datatchek.com",
                "password": "StrongPass123",
                "full_name": "Duplicate User",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    async def test_register_short_password(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@datatchek.com",
                "password": "short",
                "full_name": "Short Pass User",
            },
        )
        assert response.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "StrongPass123",
                "full_name": "Bad Email User",
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@datatchek.com",
                "password": "TestPassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@datatchek.com",
                "password": "WrongPassword",
            },
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    async def test_login_nonexistent_email(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nobody@datatchek.com",
                "password": "SomePassword123",
            },
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetMe:
    async def test_get_me_authenticated(
        self, client: AsyncClient, test_user, auth_headers
    ):
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@datatchek.com"
        assert data["full_name"] == "Test User"

    async def test_get_me_no_token(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token"},
        )
        assert response.status_code == 401
