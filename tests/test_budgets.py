import pytest
from fastapi.testclient import TestClient

def test_create_budget(client, test_user, auth_headers):
    """Test creating a new budget."""
    response = client.post(
        "/api/v1/budgets/",
        headers=auth_headers,
        json={
            "name": "New Budget",
            "currency": "EUR"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Budget"
    assert data["currency"] == "EUR"
    assert data["status"] == "active"

def test_list_user_budgets(client, test_user, test_budget, auth_headers):
    """Test listing user's budgets."""
    response = client.get("/api/v1/budgets/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["name"] == test_budget.name

def test_list_budgets_with_search(client, test_user, test_budget, auth_headers):
    """Test listing budgets with search."""
    response = client.get(
        "/api/v1/budgets/",
        headers=auth_headers,
        params={"search": "Test"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1

def test_get_budget_with_users(client, test_user, test_budget, auth_headers):
    """Test getting budget with user information."""
    response = client.get(
        f"/api/v1/budgets/{test_budget.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_budget.id)
    assert data["name"] == test_budget.name
    assert "users" in data
    assert len(data["users"]) >= 1

def test_update_budget(client, test_user, test_budget, auth_headers):
    """Test updating budget information."""
    response = client.put(
        f"/api/v1/budgets/{test_budget.id}",
        headers=auth_headers,
        json={
            "name": "Updated Budget Name",
            "currency": "GBP"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Budget Name"
    assert data["currency"] == "GBP"

def test_delete_budget(client, test_user, test_budget, auth_headers):
    """Test deleting (archiving) budget."""
    response = client.delete(
        f"/api/v1/budgets/{test_budget.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204

def test_access_denied_to_other_budget(client, test_user, auth_headers):
    """Test access denied to budget user doesn't have access to."""
    fake_budget_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(
        f"/api/v1/budgets/{fake_budget_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 403

def test_add_user_to_budget(client, test_user, test_budget, auth_headers, db_session):
    """Test adding user to budget."""
    # Create another user
    from app.models.models import User
    from app.core.security import get_password_hash
    
    new_user = User(
        name="Another User",
        email="another@example.com",
        password_hash=get_password_hash("password123"),
        auth_method="email"
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    
    response = client.post(
        f"/api/v1/budgets/{test_budget.id}/users/{new_user.id}",
        headers=auth_headers,
        params={"role": "editor"}
    )
    
    assert response.status_code == 201

def test_remove_user_from_budget(client, test_user, test_budget, auth_headers, db_session):
    """Test removing user from budget."""
    # Create and add another user first
    from app.models.models import User, UserBudget, UserRole
    from app.core.security import get_password_hash
    
    new_user = User(
        name="Another User",
        email="another@example.com",
        password_hash=get_password_hash("password123"),
        auth_method="email"
    )
    db_session.add(new_user)
    db_session.flush()
    
    user_budget = UserBudget(
        user_id=new_user.id,
        budget_id=test_budget.id,
        role=UserRole.VIEWER
    )
    db_session.add(user_budget)
    db_session.commit()
    
    response = client.delete(
        f"/api/v1/budgets/{test_budget.id}/users/{new_user.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204