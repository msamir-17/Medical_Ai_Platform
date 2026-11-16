import os
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock easyocr.Reader before importing app.main to avoid sandbox permission errors
with patch("easyocr.Reader", return_value=MagicMock()):
    from app.main import app
    from app.utils.logger import get_user_hash, JSONFormatter
    from app.utils.metrics import (
        SEMANTIC_CACHE_HIT_TOTAL,
        BM25_CACHE_HIT_TOTAL,
        RAG_REQUEST_TOTAL,
        get_metrics_data,
    )


@pytest.fixture
def client():
    return TestClient(app)


def test_x_request_id_injected_in_response(client):
    """
    Test that every response gets an X-Request-ID header for distributed tracing.
    """
    with patch("app.main.engine.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0


def test_metrics_endpoint_public_when_no_token_set(client):
    """
    Test that /metrics returns 200 with Prometheus exposition format when METRICS_TOKEN is unset.
    """
    with patch.dict(os.environ, {}, clear=False):
        if "METRICS_TOKEN" in os.environ:
            del os.environ["METRICS_TOKEN"]
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "rag_request_total" in response.text or "process_resident_memory_bytes" in response.text


def test_metrics_endpoint_token_protection(client):
    """
    Test that /metrics requires valid token when METRICS_TOKEN is configured.
    """
    with patch.dict(os.environ, {"METRICS_TOKEN": "secret_mlops_token_99"}):
        # 1. Without token -> 401
        res_no_token = client.get("/metrics")
        assert res_no_token.status_code == 401

        # 2. With wrong token -> 401
        res_wrong_token = client.get("/metrics", headers={"X-Metrics-Token": "wrong_token"})
        assert res_wrong_token.status_code == 401

        # 3. With correct token in header -> 200
        res_header = client.get("/metrics", headers={"X-Metrics-Token": "secret_mlops_token_99"})
        assert res_header.status_code == 200
        assert "# HELP" in res_header.text

        # 4. With correct token in query param -> 200
        res_query = client.get("/metrics?token=secret_mlops_token_99")
        assert res_query.status_code == 200


def test_structured_json_logger_anonymization():
    """
    Test that JSON logger outputs valid JSON and get_user_hash masks real user IDs.
    """
    # 1. Anonymization test
    h1 = get_user_hash("user_uuid_12345")
    h2 = get_user_hash("user_uuid_12345")
    assert h1 == h2  # Deterministic
    assert "user_uuid_12345" not in h1
    assert len(h1) == 12

    # 2. Anonymous fallback
    assert get_user_hash(None) == "anonymous"

    # 3. Formatter test
    import logging
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="mediai.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="API access",
        args=(),
        exc_info=None,
    )
    record.request_id = "req_123"
    record.method = "POST"
    record.path = "/chat/query"
    record.status_code = 200
    record.latency_ms = 45.2
    record.user_hash = h1

    output = formatter.format(record)
    parsed = json.loads(output)
    assert parsed["level"] == "INFO"
    assert parsed["request_id"] == "req_123"
    assert parsed["path"] == "/chat/query"
    assert parsed["user_hash"] == h1
    assert parsed["latency_ms"] == 45.2


def test_prometheus_custom_metrics_increment():
    """
    Test that custom counters increment and appear in /metrics text output.
    """
    initial_sem_hits = SEMANTIC_CACHE_HIT_TOTAL._value.get()
    SEMANTIC_CACHE_HIT_TOTAL.inc()
    assert SEMANTIC_CACHE_HIT_TOTAL._value.get() == initial_sem_hits + 1

    initial_bm25_hits = BM25_CACHE_HIT_TOTAL._value.get()
    BM25_CACHE_HIT_TOTAL.inc()
    assert BM25_CACHE_HIT_TOTAL._value.get() == initial_bm25_hits + 1

    RAG_REQUEST_TOTAL.labels(status="success").inc()

    metrics_text = get_metrics_data().decode("utf-8")
    assert "semantic_cache_hit_total" in metrics_text
    assert "bm25_cache_hit_total" in metrics_text
    assert "rag_request_total" in metrics_text

