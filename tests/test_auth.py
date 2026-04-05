import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_first_user_becomes_admin(client: AsyncClient):
    # Fresh DB for this test
    register_data = {"email": "first@example.com", "password": "Password123!"}
    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    assert response.json()["role"] == "admin"

@pytest.mark.asyncio
async def test_subsequent_user_becomes_viewer(client: AsyncClient):
    # Fresh DB for this test
    # 1. Register first (becomes admin)
    await client.post("/api/v1/auth/register", json={"email": "admin@example.com", "password": "Password123!"})
    # 2. Register second (should be viewer)
    res = await client.post("/api/v1/auth/register", json={"email": "second@example.com", "password": "Password123!"})
    assert res.status_code == 201
    assert res.json()["role"] == "viewer"

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # Fresh DB for this test
    email = "login@example.com"
    pw = "Password123!"
    await client.post("/api/v1/auth/register", json={"email": email, "password": pw})
    
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": pw})
    assert response.status_code == 200
    assert "access_token" in response.json()
