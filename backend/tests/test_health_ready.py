import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock easyocr.Reader before importing app.main to avoid sandbox permission errors
with patch("easyocr.Reader", return_value=MagicMock()):
    from app.main import app, sentry_scrub_pii


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint_healthy(client):
    """
    Test that /health returns 200 and healthy status when DB probe succeeds.
    """
    with patch("app.main.engine.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["db"] is True
        assert "version" in data
        assert "environment" in data


def test_health_endpoint_degraded_on_db_failure(client):
    """
    Test that /health returns 503 and degraded status when DB connection fails.
    """
    with patch("app.main.engine.connect", side_effect=Exception("Database pool connection timed out")):
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["db"] is False


def test_ready_endpoint_structure(client):
    """
    Test that /ready probe correctly reports readiness status and model dependencies.
    """
    response = client.get("/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "ready" in data
    assert "models" in data
    assert "diabetes_model" in data["models"]
    assert "heart_model" in data["models"]
    assert "vector_store" in data


def test_sentry_pii_scrubber_protects_medical_data():
    """
    Test HIPAA/GDPR Medical Scrubber (MLOPS_PLAN Section 3):
    Ensures patient names, tokens, cookies, headers, and request body are redacted.
    """
    dummy_event = {
        "request": {
            "headers": {
                "Host": "medical-ai-backend.hf.space",
                "User-Agent": "Mozilla/5.0",
                "Authorization": "Bearer super-secret-jwt-token",
                "X-Patient-Id": "PAT-9843-SECRET",
                "Cookie": "session=sensitive_patient_data",
            },
            "cookies": {"session": "patient_private_cookie"},
            "query_string": "patient_name=Kanta+Yadav&mrn=12345",
            "data": '{"patient_name": "Kanta Yadav", "glucose": 185, "diagnosis": "Type-2 Diabetes"}',
        },
        "breadcrumbs": {
            "values": [
                {
                    "category": "sqlalchemy",
                    "data": {"query": "SELECT * FROM reports WHERE patient_name = 'Kanta Yadav'"},
                },
                {
                    "category": "navigation",
                    "data": {"to": "/reports"},
                },
            ]
        },
    }

    scrubbed = sentry_scrub_pii(dummy_event, hint={})
    req = scrubbed["request"]

    # 1. Authorization and sensitive headers MUST be removed
    assert "Authorization" not in req["headers"]
    assert "authorization" not in req["headers"]
    assert "X-Patient-Id" not in req["headers"]
    assert "Cookie" not in req["headers"]
    assert req["headers"].get("Host") == "medical-ai-backend.hf.space"

    # 2. Cookies and query params MUST be completely removed
    assert "cookies" not in req
    assert "query_string" not in req

    # 3. Patient request body data MUST be redacted
    assert req["data"] == "[SCRUBBED_MEDICAL_DATA]"
    assert "Kanta Yadav" not in str(req["data"])
    assert "glucose" not in str(req["data"])

    # 4. SQL breadcrumbs containing query params MUST be redacted
    sql_bc = scrubbed["breadcrumbs"]["values"][0]
    assert "data" not in sql_bc

