import pytest
from fastapi.testclient import TestClient
import time

def test_rate_limiting(client):
    """Test rate limiting middleware."""
    # Make multiple requests quickly
    responses = []
    for i in range(55):  # Exceed the 50 requests per minute limit
        response = client.get("/health")
        responses.append(response)
        if response.status_code == 429:
            break
    
    # Should get rate limited
    assert any(r.status_code == 429 for r in responses)

def test_rate_limit_headers(client):
    """Test rate limit headers are present."""
    response = client.get("/health")
    
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers

def test_auth_middleware_exempt_routes(client):
    """Test that exempt routes don't require authentication."""
    exempt_routes = ["/", "/health", "/docs", "/redoc"]
    
    for route in exempt_routes:
        response = client.get(route)
        # Should not get 401 Unauthorized
        assert response.status_code != 401

def test_auth_middleware_protected_routes(client):
    """Test that protected routes require authentication."""
    protected_routes = [
        "/api/v1/users/me",
        "/api/v1/budgets/",
        "/api/v1/transactions/"
    ]
    
    for route in protected_routes:
        response = client.get(route)
        assert response.status_code == 401

def test_auth_middleware_invalid_token(client):
    """Test authentication with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/users/me", headers=headers)
    
    assert response.status_code == 401

def test_auth_middleware_missing_bearer(client):
    """Test authentication with missing Bearer scheme."""
    headers = {"Authorization": "invalid_token"}
    response = client.get("/api/v1/users/me", headers=headers)
    
    assert response.status_code == 401