import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test user registration
def test_register_user():
    response = client.post('/auth/register', json={
        "email": "simpleuser@example.com",
        "password": "simpleuser",
        "name": "Simple User"
    })
    assert response.status_code == 200
    assert "User registered successfully" in response.json()["message"]

# Test admin user registration
def test_register_admin_user():
    response = client.post('/auth/register', json={
        "email": "admin@example.com",
        "password": "admin",
        "name": "Admin User",
        "roles": ["Admin"]
    })
    assert response.status_code == 200
    assert "User registered successfully" in response.json()["message"]

# Test login and token retrieval
def test_login():
    # Register user first
    
    client.post('/auth/register', json={
        "email": "simpleuser2@example.com",
        "password": "simpleuser2",
        "name": "Simple User 2"
    })

    response = client.post('/auth/login', data={
        "username": "simpleuser2@example.com",
        "password": "simpleuser2"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()