import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from app.main import app
from app.database import db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def drop_collections():

    await db.users.drop()
    await db.InvestmentFund.drop()
    await db.Transaction.drop()


# --- CREATE FUND ENDPOINT TEST ---
@pytest.mark.asyncio
async def test_create_fund_success():

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


@pytest.mark.asyncio
async def test_create_fund_unauthorized():

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        payload = {
            "email": "simpleuser@example.com",
            "password": "simpleuser",
            "name": "Simple User"
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
        assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_subscribe_fund_success():
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
            "minimumFee": 50,
            "category": "Technology"
        }

        response = await ac.post("/funds/create", json=payload_fund, headers={"Authorization": f"Bearer {response_token}"})
        assert response.status_code == status.HTTP_201_CREATED

        fund_id = response.json().get("id")
        print(f"Created fund with ID: {fund_id}")
        assert fund_id is not None
        

        payload = {
            "email": "simpleuser@example.com",
            "password": "simpleuser",
            "name": "Simple User"
        }

        await ac.post("/auth/register", json=payload)
        response = await ac.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
        response_token = response.json().get("access_token")

        response = await ac.post(f"/funds/subscribe/{fund_id}", headers={"Authorization": f"Bearer {response_token}"})
        assert response.status_code == status.HTTP_201_CREATED