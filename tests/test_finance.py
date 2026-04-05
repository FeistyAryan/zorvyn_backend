import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_rbac_and_finance_workflow(client: AsyncClient):
    # 1. Register Admin (First User)
    await client.post("/api/v1/auth/register", json={
        "email": "admin@test.com", "password": "Password123!"
    })
    
    admin_login = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com", "password": "Password123!"
    })
    admin_token = admin_login.json()["access_token"]

    # 2. Register Second User (Defaults to Viewer)
    await client.post("/api/v1/auth/register", json={
        "email": "staff@test.com", "password": "Password123!"
    })
    
    staff_login = await client.post("/api/v1/auth/login", json={
        "email": "staff@test.com", "password": "Password123!"
    })
    staff_token = staff_login.json()["access_token"]

    # 3. Viewer (Staff) should NOT be able to create records
    fail_res = await client.post(
        "/api/v1/finance/create",
        json={"amount": 100, "type": "income", "category": "salary"},
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert fail_res.status_code == 403

    # 4. Admin promotes Staff to Analyst
    promote_res = await client.patch(
        "/api/v1/users/2",
        json={"role": "analyst"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert promote_res.status_code == 200
    assert promote_res.json()["role"] == "analyst"

    # 5. Analyst should now be able to create records
    success_res = await client.post(
        "/api/v1/finance/create",
        json={"amount": 5000, "type": "income", "category": "salary"},
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert success_res.status_code == 201

    # 6. Verify Summary updates
    summary_res = await client.get(
        "/api/v1/finance/summary",
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert summary_res.status_code == 200
    assert summary_res.json()["total_income"] == "5000.00"

@pytest.mark.asyncio
async def test_user_1_protection(client: AsyncClient):
    # 1. First user is Admin
    await client.post("/api/v1/auth/register", json={
        "email": "boss@test.com", "password": "Password123!"
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "boss@test.com", "password": "Password123!"
    })
    token = login.json()["access_token"]

    # 2. Try to downgrade self (User 1) - Should fail
    res = await client.patch(
        "/api/v1/users/1",
        json={"role": "viewer"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403
    assert "restricted" in res.json()["detail"]
