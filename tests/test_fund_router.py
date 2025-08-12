import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from app.main import app
from app.database import db

# --- CREATE FUND ENDPOINT TEST ---
@pytest.mark.asyncio(scope="session")
async def test_create_fund_success():

    # Drop the collections before starting the test
    await db.users.drop()
    await db.InvestmentFund.drop()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        payload = {
            "email": "admin@example.com",
            "password": "adminpassword",
            "name": "Admin User",
            "roles": ["Admin"]
        }

        await ac.post("/auth/register", json=payload)
        response = await ac.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
        response_token = response.json().get("access_token")
        
        payload_fund = {
            "name": "Tech Fund",
            "minimumFee": 1000,
            "category": "Technology"
        }

        response = await ac.post("/funds/create", json=payload_fund, headers={"Authorization": f"Bearer {response_token}"})
        assert response.status_code == status.HTTP_201_CREATED

