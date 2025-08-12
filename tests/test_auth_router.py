import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from app.main import app
from app.database import db

async def drop_collections():

    await db['User'].drop()
    await db['InvestmentFund'].drop()
    await db['Transaction'].drop()
    await db['UserInvestmentFund'].drop()
    
    print("Collections dropped for testing.")


# --- REGISTER ENDPOINT TESTS ---
@pytest.mark.asyncio(scope="session")
async def test_register_user_success():

    await drop_collections()

    payload = {
        "email": "simpleuser@example.com",
        "password": "simpleuser",
        "name": "Simple User"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "User registered successfully"


@pytest.mark.asyncio(scope="session")
async def test_register_existing_user():

    await drop_collections()

    payload = {
        "email": "simpleuser@example.com",
        "password": "simpleuser",
        "name": "Simple User"
    }   
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        await ac.post("/auth/register", json=payload)

        response = await ac.post("/auth/register", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already exists"


@pytest.mark.asyncio(scope="session")
async def test_register_admin_success():

    await drop_collections()

    payload = {
        "email": "admin@example.com",
        "password": "adminpassword",
        "name": "Admin User",
        "roles": ["Admin"]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "User registered successfully"


# --- LOGIN ENDPOINT TESTS ---
@pytest.mark.asyncio(scope="session")
async def test_login_success():

    await drop_collections()

    payload = {
        "email": "simpleuser@example.com",
        "password": "simpleuser",
        "name": "Simple User"
    }   

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        await ac.post("/auth/register", json=payload)
        
        response = await ac.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio(scope="session")
async def test_login_invalid_password():

    await drop_collections()

    payload = {
        "email": "simpleuser@example.com",
        "password": "simpleuser",
        "name": "Simple User"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        await ac.post("/auth/register", json=payload)

        response = await ac.post("/auth/login", data={"username": payload["email"], "password": "wrongpassword"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.asyncio(scope="session")
async def test_login_admin_success():

    await drop_collections()

    payload = {
        "email": "admin@example.com",
        "password": "adminpassword",
        "name": "Admin User",
        "roles": ["Admin"]
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        await ac.post("/auth/register", json=payload)

        response = await ac.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["token_type"] == "bearer"
