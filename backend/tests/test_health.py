"""Tests for health endpoints"""
from tests.conftest import client


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/health/")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "service" in response.json()


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    assert "service" in response.json()
    assert "docs" in response.json()


def test_api_info(client):
    """Test API info endpoint"""
    response = client.get("/api")
    
    assert response.status_code == 200
    assert "name" in response.json()
    assert "endpoints" in response.json()
