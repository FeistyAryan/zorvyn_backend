import pytest
from httpx import AsyncClient

async def get_token(client: AsyncClient, email: str, role: str):
    # Helper to register and login a user
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "Password123!", "role": role
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": email, "password": "Password123!"
    })
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_rbac_viewer_cannot_create(client: AsyncClient):
    # 1. Get Viewer Token
    viewer_token = await get_token(client, "viewer@example.com", "viewer")
    
    # 2. Try to create a record (Should fail)
    record_data = {
        "amount": 1000, "type": "income", "category": "salary", "description": "Stealing Access"
    }
    response = await client.post(
        "/api/v1/finance/create", 
        json=record_data,
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    
    # Expected: 403 Forbidden because Viewer can't create
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_analyst_can_create_and_view_summary(client: AsyncClient):
    # 1. Get Analyst Token
    analyst_token = await get_token(client, "analyst@example.com", "analyst")
    
    # 2. Create Record (Should pass)
    record_data = {
        "amount": 5000, "type": "income", "category": "salary", "description": "Legal Job"
    }
    create_res = await client.post(
        "/api/v1/finance/create", 
        json=record_data,
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert create_res.status_code == 201

    # 3. View Summary (Should work)
    summary_res = await client.get(
        "/api/v1/finance/summary",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert summary_res.status_code == 200
    assert summary_res.json()["total_income"] == "5000.00"
