"""Basic health check test stub."""
from __future__ import annotations

from ai_instructions_app.app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/v1/health/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
