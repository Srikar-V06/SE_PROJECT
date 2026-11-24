import asyncio
import json

from ledger_api.main import internal_error


def assert_error(response, status, code):
    assert response.status_code == status

    body = response.json()

    assert set(body) == {"code", "message"}
    assert body["code"] == code
    assert isinstance(body["message"], str)


def test_validation_error_format(client):
    response = client.post("/auth/register", json={})

    assert_error(response, 400, "VALIDATION_ERROR")


def test_not_found_error_format(client):
    response = client.get("/nonexistent-route")

    assert_error(response, 404, "NOT_FOUND")


def test_wrong_method_error_format(client):
    response = client.post("/health")

    assert_error(response, 405, "METHOD_NOT_ALLOWED")


def test_internal_error_format():
    response = asyncio.run(
        internal_error(None, RuntimeError("Synthetic test error"))
    )

    body = json.loads(response.body)

    assert response.status_code == 500
    assert set(body) == {"code", "message"}
    assert body["code"] == "INTERNAL_ERROR"