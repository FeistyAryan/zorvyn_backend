import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_rbac_and_finance_workflow(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "admin@test.com", "password": "Password123!"
    })
    
    admin_login = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com", "password": "Password123!"
    })
    admin_token = admin_login.json()["access_token"]

    await client.post("/api/v1/auth/register", json={
        "email": "staff@test.com", "password": "Password123!"
    })
    
    staff_login = await client.post("/api/v1/auth/login", json={
        "email": "staff@test.com", "password": "Password123!"
    })
    staff_token = staff_login.json()["access_token"]

    fail_res = await client.post(
        "/api/v1/finance/create",
        json={"amount": 100, "type": "income", "category": "salary"},
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert fail_res.status_code == 403

    promote_res = await client.patch(
        "/api/v1/users/2",
        json={"role": "analyst"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert promote_res.status_code == 200
    assert promote_res.json()["role"] == "analyst"

    success_res = await client.post(
        "/api/v1/finance/create",
        json={"amount": 5000, "type": "income", "category": "salary"},
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert success_res.status_code == 201

    summary_res = await client.get(
        "/api/v1/finance/summary",
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert summary_res.status_code == 200
    assert summary_res.json()["total_income"] == "5000.00"

@pytest.mark.asyncio
async def test_user_1_protection(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "boss@test.com", "password": "Password123!"
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "boss@test.com", "password": "Password123!"
    })
    token = login.json()["access_token"]

    res = await client.patch(
        "/api/v1/users/1",
        json={"role": "viewer"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403
    assert "restricted" in res.json()["detail"]
