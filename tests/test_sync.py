import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_sync_push_empty(client, test_user, auth_headers):
    """Test sync push with empty data."""
    response = client.post(
        "/api/v1/sync/push",
        headers=auth_headers,
        json={
            "users": [],
            "budgets": [],
            "transactions": [],
            "recurring_transactions": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "processed" in data
    assert "conflicts" in data
    assert "timestamp" in data

def test_sync_pull_all_data(client, test_user, auth_headers):
    """Test sync pull without timestamp (all data)."""
    response = client.get("/api/v1/sync/pull", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "budgets" in data
    assert "transactions" in data
    assert "recurring_transactions" in data
    assert "timestamp" in data

def test_sync_pull_with_timestamp(client, test_user, auth_headers):
    """Test sync pull with timestamp."""
    since = datetime.utcnow() - timedelta(hours=1)
    
    response = client.get(
        "/api/v1/sync/pull",
        headers=auth_headers,
        params={"since": since.isoformat()}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "budgets" in data
    assert "transactions" in data
    assert "recurring_transactions" in data

def test_get_sync_conflicts(client, test_user, auth_headers):
    """Test getting sync conflicts."""
    response = client.get("/api/v1/sync/conflicts", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "conflicts" in data
    assert "resolved" in data
    assert isinstance(data["conflicts"], list)

def test_resolve_sync_conflicts(client, test_user, auth_headers):
    """Test resolving sync conflicts."""
    response = client.post(
        "/api/v1/sync/conflicts/resolve",
        headers=auth_headers,
        json={
            "conflict_1": "server_wins",
            "conflict_2": "client_wins"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "resolved_count" in data
    assert "remaining_conflicts" in data

def test_get_sync_status(client, test_user, auth_headers):
    """Test getting sync status."""
    response = client.get("/api/v1/sync/status", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "last_sync" in data
    assert "pending_changes" in data
    assert "conflicts_count" in data
    assert "sync_health" in data
    assert "timestamp" in data