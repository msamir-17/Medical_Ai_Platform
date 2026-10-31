import pytest
import time
import numpy as np
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.semantic_cache_service import SemanticCacheService, semantic_cache

@pytest.fixture(autouse=True)
def clean_cache():
    """Ensure a fresh cache instance before every test."""
    semantic_cache.clear()
    yield
    semantic_cache.clear()

def test_cache_miss_on_empty():
    """Verify that an initial query results in a cache miss."""
    dummy_vec = [0.1] * 384
    res = semantic_cache.get(dummy_vec, user_id="user_123", mode="single", report_ids=["rep_1"])
    assert res is None
    metrics = semantic_cache.get_metrics()
    assert metrics["total_lookups"] == 1
    assert metrics["cache_misses"] == 1
    assert metrics["cache_hits"] == 0

def test_exact_query_cache_hit():
    """Verify storing and retrieving identical query vector produces a cache hit."""
    dummy_vec = [0.2] * 384
    resp_data = {"answer": "Fasting blood glucose is 115 mg/dL.", "sources": "Lab Report"}
    
    # Store in cache
    semantic_cache.put(
        query_text="What is fasting glucose?",
        query_embedding=dummy_vec,
        response=resp_data,
        user_id="user_123",
        mode="single",
        report_ids=["rep_1"]
    )

    # Retrieve
    hit = semantic_cache.get(dummy_vec, user_id="user_123", mode="single", report_ids=["rep_1"])
    assert hit is not None
    assert hit["cache_hit"] is True
    assert hit["answer"] == resp_data["answer"]
    assert hit["similarity_score"] >= 0.99
    
    metrics = semantic_cache.get_metrics()
    assert metrics["cache_hits"] == 1
    assert metrics["hit_rate_pct"] == 100.0

def test_patient_isolation_guarantee():
    """Verify that User A's cached clinical data cannot be accessed by User B."""
    dummy_vec = [0.5] * 384
    resp_data = {"answer": "Patient A has Stage 2 Hypertension.", "sources": "Cardiology"}

    semantic_cache.put(
        query_text="Check blood pressure findings",
        query_embedding=dummy_vec,
        response=resp_data,
        user_id="user_patient_A",
        mode="single",
        report_ids=["rep_100"]
    )

    # User B queries with identical embedding -> must be None!
    hit_user_b = semantic_cache.get(dummy_vec, user_id="user_patient_B", mode="single", report_ids=["rep_100"])
    assert hit_user_b is None, "CRITICAL FAULT: Cross-patient data leakage detected!"

    # User A queries and gets hit
    hit_user_a = semantic_cache.get(dummy_vec, user_id="user_patient_A", mode="single", report_ids=["rep_100"])
    assert hit_user_a is not None
    assert hit_user_a["answer"] == resp_data["answer"]

def test_report_isolation_guarantee():
    """Verify that caching for Report 1 does not return for Report 2."""
    dummy_vec = [0.3] * 384
    resp_data = {"answer": "Serum Creatinine is 1.4 mg/dL.", "sources": "Renal Panel"}

    semantic_cache.put(
        query_text="What is creatinine?",
        query_embedding=dummy_vec,
        response=resp_data,
        user_id="user_123",
        mode="single",
        report_ids=["rep_1"]
    )

    # Query with report 2
    hit_rep_2 = semantic_cache.get(dummy_vec, user_id="user_123", mode="single", report_ids=["rep_2"])
    assert hit_rep_2 is None

    # Query with both report 1 and report 2
    hit_both = semantic_cache.get(dummy_vec, user_id="user_123", mode="single", report_ids=["rep_1", "rep_2"])
    assert hit_both is None

def test_user_invalidation():
    """Verify cache invalidation upon document deletion or profile update."""
    dummy_vec = [0.4] * 384
    resp_data = {"answer": "Normal ECG findings.", "sources": "Report 1"}

    semantic_cache.put("ECG status", dummy_vec, resp_data, user_id="user_to_clear", mode="single", report_ids=["r1"])
    assert semantic_cache.get(dummy_vec, user_id="user_to_clear", mode="single", report_ids=["r1"]) is not None

    deleted_count = semantic_cache.invalidate_user("user_to_clear")
    assert deleted_count >= 1

    # Should now be a cache miss
    assert semantic_cache.get(dummy_vec, user_id="user_to_clear", mode="single", report_ids=["r1"]) is None

def test_ttl_expiration():
    """Verify that expired cache entries are ignored."""
    service = SemanticCacheService()
    service.ttl_seconds = 0.1  # 100ms TTL for test
    dummy_vec = [0.7] * 384
    resp = {"answer": "Temporary value", "sources": "Lab"}

    service.put("Test", dummy_vec, resp, user_id="u1", mode="single", report_ids=["r1"])
    # Immediate lookup -> hit
    assert service.get(dummy_vec, user_id="u1", mode="single", report_ids=["r1"]) is not None

    # Wait for TTL expiry
    time.sleep(0.15)
    # Post-expiry lookup -> miss
    assert service.get(dummy_vec, user_id="u1", mode="single", report_ids=["r1"]) is None

def test_telemetry_metrics_tracking():
    """Verify metrics calculation accuracy."""
    service = SemanticCacheService()
    dummy_vec = [0.1] * 384
    # Miss
    service.get(dummy_vec, "u1", "single")
    # Put
    service.put("q", dummy_vec, {"answer": "ans"}, "u1", "single")
    # Hit
    service.get(dummy_vec, "u1", "single")
    
    metrics = service.get_metrics()
    assert metrics["total_lookups"] == 2
    assert metrics["cache_hits"] == 1
    assert metrics["cache_misses"] == 1
    assert metrics["hit_rate_pct"] == 50.0
