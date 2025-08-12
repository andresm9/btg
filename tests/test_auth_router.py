import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from app.main import app
from app.database import db

# --- REGISTER ENDPOINT TESTS ---
@pytest.mark.asyncio(scope="session")
async def test_register_user_success():

    # Drop the collection before starting the test
    await db.users.drop()

    payload = {
        "email": "gaticocafe@example.com",
        "password": "gaticocafe",
        "name": "Gatico Cafe"
    }   
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "User registered successfully"


@pytest.mark.asyncio(scope="session")
async def test_register_existing_user():
    payload = {
        "email": "gaticocafe@example.com",
        "password": "gaticocafe",
        "name": "Gatico Cafe"
    }   
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/register", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already exists"

@pytest.mark.asyncio(scope="session")
async def test_register_admin_success():
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

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        response = await ac.post("/auth/login", data={"username": "gaticocafe@example.com", "password": "gaticocafe"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio(scope="session")
async def test_login_invalid_password():

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        response = await ac.post("/auth/login", data={"username": "gaticocafe@example.com", "password": "wrongpassword"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.asyncio(scope="session")
async def test_login_admin_success():

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        response = await ac.post("/auth/login", data={"username": "admin@example.com", "password": "adminpassword"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["token_type"] == "bearer"
