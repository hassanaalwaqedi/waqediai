"""Unit tests for the service."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_readiness_check(client: TestClient) -> None:
    """Test readiness check endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_example_endpoint(client: TestClient) -> None:
    """Test example API endpoint."""
    response = client.get("/api/v1/example")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
