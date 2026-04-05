import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # 1. Test Registration
    register_data = {
        "email": "testuser@example.com",
        "password": "Password123!",
        "role": "viewer"
    }
    response = await client.post("/api/v1/auth/register", json=register_data)
    
    assert response.status_code == 201
    assert response.json()["email"] == register_data["email"]
    assert response.json()["role"] == "viewer"

    # 2. Test Login
    login_data = {
        "email": "testuser@example.com",
        "password": "Password123!"
    }
    login_response = await client.post("/api/v1/auth/login", json=login_data)
    
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    login_data = {
        "email": "testuser@example.com",
        "password": "WrongPassword"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
