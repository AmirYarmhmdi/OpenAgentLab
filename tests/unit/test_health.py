from fastapi.testclient import TestClient
from helpers import create_isolated_app


# This checks the official health endpoint response.
def test_health_endpoint_returns_ok(monkeypatch) -> None:
    with TestClient(create_isolated_app(monkeypatch)) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "OpenAgentLab",
        "version": "0.1.0",
        "environment": "development",
    }


# This checks that the optional root endpoint stays simple.
def test_root_endpoint_returns_running_status(monkeypatch) -> None:
    with TestClient(create_isolated_app(monkeypatch)) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "OpenAgentLab",
        "status": "running",
    }


# This checks that the app can be created without external services.
def test_application_can_be_created_without_external_services(monkeypatch) -> None:
    app = create_isolated_app(monkeypatch)

    assert app.title == "OpenAgentLab"
