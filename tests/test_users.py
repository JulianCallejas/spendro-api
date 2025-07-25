import pytest
from fastapi.testclient import TestClient

def test_get_current_user(client, test_user, auth_headers):
    """Test getting current user information."""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["name"] == test_user.name
    assert data["email"] == test_user.email

def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/users/me")
    
    assert response.status_code == 401

def test_update_current_user(client, test_user, auth_headers):
    """Test updating current user information."""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "name": "Updated Name",
            "phone": "+9876543210"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["phone"] == "+9876543210"

def test_list_users(client, test_user, auth_headers):
    """Test listing users with pagination."""
    response = client.get("/api/v1/users/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert "items" in data
    assert len(data["items"]) >= 1

def test_list_users_with_search(client, test_user, auth_headers):
    """Test listing users with search."""
    response = client.get(
        "/api/v1/users/",
        headers=auth_headers,
        params={"search": "Test"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1

def test_get_user_by_id(client, test_user, auth_headers):
    """Test getting user by ID."""
    response = client.get(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)

def test_get_nonexistent_user(client, auth_headers):
    """Test getting nonexistent user."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(
        f"/api/v1/users/{fake_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404

def test_delete_current_user(client, test_user, auth_headers):
    """Test deleting current user account."""
    response = client.delete("/api/v1/users/me", headers=auth_headers)
    
    assert response.status_code == 204