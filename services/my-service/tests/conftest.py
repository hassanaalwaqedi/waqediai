"""Pytest configuration for service tests."""

import pytest
from fastapi.testclient import TestClient

from service_name.main import create_app
from service_name.config import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        service_name="test-service",
        environment="testing",
        debug=True,
    )


@pytest.fixture
def app(test_settings: Settings):
    """Create test application."""
    return create_app(test_settings)


@pytest.fixture
def client(app) -> TestClient:
    """Create test client."""
    return TestClient(app)
