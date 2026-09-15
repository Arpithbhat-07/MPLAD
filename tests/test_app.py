"""Basic application smoke tests."""

from backend.app import create_app


def test_health_endpoint():

    app = create_app()

    client = app.test_client()

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["status"] == "healthy"


def test_project_api():

    app = create_app()

    client = app.test_client()

    response = client.get(
        "/api/projects"
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["success"] is True