import pytest
from fastapi.testclient import TestClient
from app.core.security import get_password_hash

def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["name"] == "New User"

def test_register_user_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Duplicate User",
            "email": test_user.email,
            "password": "password123"
        }
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_valid_credentials(client, test_user):
    """Test login with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_login_nonexistent_user(client):
    """Test login with nonexistent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_google_auth_not_implemented(client):
    """Test Google authentication (not fully implemented)."""
    response = client.post(
        "/api/v1/auth/google",
        json={
            "google_token": "fake_google_token"
        }
    )
    
    assert response.status_code == 401
    assert "Google authentication failed" in response.json()["detail"]

def test_biometric_auth_no_biometric_data(client, test_user):
    """Test biometric authentication without biometric data."""
    response = client.post(
        "/api/v1/auth/biometric",
        json={
            "biometric_data": "fake_biometric_data",
            "user_identifier": test_user.email
        }
    )
    
    assert response.status_code == 401
    assert "Biometric authentication failed" in response.json()["detail"]