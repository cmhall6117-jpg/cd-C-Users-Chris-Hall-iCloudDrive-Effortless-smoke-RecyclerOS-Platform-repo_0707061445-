from fastapi.testclient import TestClient

from main import create_app


def test_local_flutter_web_cors_preflight():
    with TestClient(create_app()) as client:
        response = client.options(
            "/v1/opportunities",
            headers={
                "Origin": "http://localhost:4242",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": (
                    "content-type,x-organization-id,x-workspace-id"
                ),
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4242"
    assert "POST" in response.headers["access-control-allow-methods"]
    allowed_headers = response.headers["access-control-allow-headers"].lower()
    assert "x-organization-id" in allowed_headers
    assert "x-workspace-id" in allowed_headers


def test_non_local_origin_is_not_allowed_by_default():
    with TestClient(create_app()) as client:
        response = client.options(
            "/v1/opportunities",
            headers={
                "Origin": "https://example.invalid",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
