
import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from app.main import app
from app.database import db

@pytest.fixture(scope="session", autouse=True)
def event_loop():
    
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()



async def drop_collections():
    await db['User'].drop()
    await db['InvestmentFund'].drop()
    await db['Transaction'].drop()
    await db['UserInvestmentFund'].drop()
    print("Collections dropped for testing.")


async def register_and_login(ac, email, password, name, roles=None):

    payload = {"email": email, "password": password, "name": name}
    if roles:
        payload["roles"] = roles
    
    await ac.post("/auth/register", json=payload)
    response = await ac.post("/auth/login", data={"username": email, "password": password})
    
    return response.json().get("access_token")


async def create_fund(ac, token, name="Tech Fund", minimumFee=1000, category="Technology"):
    
    payload_fund = {"name": name, "minimumFee": minimumFee, "category": category}
    response = await ac.post("/funds/create", json=payload_fund, headers={"Authorization": f"Bearer {token}"})
    
    return response


# --- CREATE FUND ENDPOINT TEST ---

@pytest.mark.asyncio
async def test_create_fund_success():

    await drop_collections()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        admin_token = await register_and_login(ac, "admin@example.com", "adminpassword", "Admin User", roles=["Admin"])
        response = await create_fund(ac, admin_token, name="Tech Fund", minimumFee=1000, category="Technology")
        assert response.status_code == status.HTTP_201_CREATED



@pytest.mark.asyncio
async def test_create_fund_unauthorized():
    """Test create a fund from a customer profile"""

    await drop_collections()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        user_token = await register_and_login(ac, "simpleuser@example.com", "simpleuser", "Simple User")
        response = await create_fund(ac, user_token, name="Tech Fund", minimumFee=1000, category="Technology")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_subscribe_fund_success():
    
    await drop_collections()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
    
        admin_token = await register_and_login(ac, "admin@example.com", "adminpassword", "Admin User", roles=["Admin"])
        response = await create_fund(ac, admin_token, name="Tech Fund", minimumFee=50, category="Technology")
    
        fund_id = response.json().get("id")
    
        user_token = await register_and_login(ac, "simpleuser@example.com", "simpleuser", "Simple User")
        response = await ac.post(f"/funds/subscribe/{fund_id}", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == status.HTTP_201_CREATED




@pytest.mark.asyncio
async def test_cancel_fund_success():

    await drop_collections()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        admin_token = await register_and_login(ac, "admin@example.com", "adminpassword", "Admin User", roles=["Admin"])
        response = await create_fund(ac, admin_token, name="Tech Fund", minimumFee=50, category="Technology")
        
        fund_id = response.json().get("id")
        
        user_token = await register_and_login(ac, "simpleuser@example.com", "simpleuser", "Simple User")
        await ac.post(f"/funds/subscribe/{fund_id}", headers={"Authorization": f"Bearer {user_token}"})
        
        response = await ac.post(f"/funds/cancel/{fund_id}", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == status.HTTP_200_OK