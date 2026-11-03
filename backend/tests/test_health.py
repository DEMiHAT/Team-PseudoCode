"""
Unit tests for system health and discovery endpoints.
"""


def test_root_discovery(client):
    """Test that the root endpoint returns 200 with service information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "IT22301" in data["course"]
    assert data["status"] == "online"


def test_api_health_check(client):
    """Test the /api/v1/health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["database_connected"] is True
    assert "services" in payload["data"]
