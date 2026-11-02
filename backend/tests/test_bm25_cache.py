import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
import pytest
from langchain_core.documents import Document

# Ensure backend path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.rag_service import rag_service
from app.services.semantic_cache_service import semantic_cache

def _make_dummy_chunks(prefix: str, count: int = 5):
    """Helper to generate mock clinical report documents."""
    return [
        Document(
            page_content=f"{prefix} Clinical Lab Finding {i}: Glucose is 11{i} mg/dL, Creatinine is 1.{i} mg/dL",
            metadata={"chunk_id": i}
        )
        for i in range(count)
    ]

@pytest.fixture(autouse=True)
def clean_rag_caches():
    """Ensure clean BM25 and FAISS caches before each test."""
    with rag_service._index_lock:
        rag_service._bm25_cache.clear()
        rag_service._index_cache.clear()
    semantic_cache.clear()
    yield
    with rag_service._index_lock:
        rag_service._bm25_cache.clear()
        rag_service._index_cache.clear()
    semantic_cache.clear()

def test_first_request_builds_and_caches_bm25():
    """Verify that cold request builds BM25 index and warm request reuses identical object."""
    path = os.path.normpath("C:/fake_db/user_101/report_rep_01")
    chunks = _make_dummy_chunks("Patient 101")

    # Initial state
    assert path not in rag_service._bm25_cache

    # 1st Call: Cache MISS -> builds index
    bm25_first = rag_service._get_or_create_bm25(path, chunks)
    assert bm25_first is not None
    assert path in rag_service._bm25_cache
    assert len(rag_service._bm25_cache) == 1

    # 2nd Call: Cache HIT -> returns exact same instance from memory
    bm25_second = rag_service._get_or_create_bm25(path, chunks)
    assert bm25_second is bm25_first, "Cache HIT must return the exact same in-memory BM25 instance!"

def test_user_and_report_isolation():
    """Verify that different users and different reports never share BM25 indexes."""
    path_user_a = os.path.normpath("C:/fake_db/user_A/report_rep_01")
    path_user_b = os.path.normpath("C:/fake_db/user_B/report_rep_01")
    path_user_a_rep2 = os.path.normpath("C:/fake_db/user_A/report_rep_02")

    chunks_a = _make_dummy_chunks("User A Data")
    chunks_b = _make_dummy_chunks("User B Data")
    chunks_a2 = _make_dummy_chunks("User A Report 2")

    bm25_a = rag_service._get_or_create_bm25(path_user_a, chunks_a)
    bm25_b = rag_service._get_or_create_bm25(path_user_b, chunks_b)
    bm25_a2 = rag_service._get_or_create_bm25(path_user_a_rep2, chunks_a2)

    assert bm25_a is not bm25_b, "Patient Isolation Violation: Different users cannot share BM25 index!"
    assert bm25_a is not bm25_a2, "Report Isolation Violation: Different reports cannot share BM25 index!"
    assert len(rag_service._bm25_cache) == 3

def test_reindexing_invalidates_cache():
    """Verify that re-indexing or calling invalidate_report_cache evicts the cached index."""
    user_id = "user_reindex_test"
    report_id = "rep_update_99"
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{user_id}")
    path = os.path.normpath(os.path.join(user_folder, f"report_{report_id}"))

    chunks_v1 = _make_dummy_chunks("Old Data V1")
    bm25_v1 = rag_service._get_or_create_bm25(path, chunks_v1)
    assert path in rag_service._bm25_cache

    # Invalidate cache
    rag_service.invalidate_report_cache(user_id, report_id)
    assert path not in rag_service._bm25_cache, "Old BM25 cache must be evicted on invalidation!"

    # Re-create with new content
    chunks_v2 = _make_dummy_chunks("Updated Data V2")
    bm25_v2 = rag_service._get_or_create_bm25(path, chunks_v2)
    assert bm25_v2 is not bm25_v1, "Re-indexed report must construct a fresh BM25 index!"

def test_deletion_invalidates_cache_and_semantic_cache():
    """Verify that report deletion evicts FAISS, BM25, and semantic cache for the user."""
    user_id = "user_delete_test"
    report_id = "rep_del_123"
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{user_id}")
    report_path = os.path.normpath(os.path.join(user_folder, f"report_{report_id}"))

    # Populate BM25, FAISS and Semantic Cache
    rag_service._bm25_cache[report_path] = "MOCK_BM25"
    rag_service._index_cache[report_path] = "MOCK_FAISS"
    semantic_cache.put("What is glucose?", [0.1] * 384, {"answer": "110 mg/dL"}, user_id=user_id, mode="single")

    assert report_path in rag_service._bm25_cache
    assert report_path in rag_service._index_cache
    assert semantic_cache.get([0.1] * 384, user_id=user_id, mode="single") is not None

    # Invalidate (triggered upon report deletion)
    rag_service.invalidate_report_cache(user_id, report_id)

    assert report_path not in rag_service._bm25_cache, "BM25 cache must be evicted on delete!"
    assert report_path not in rag_service._index_cache, "FAISS cache must be evicted on delete!"
    assert semantic_cache.get([0.1] * 384, user_id=user_id, mode="single") is None, "Semantic cache must be cleared for deleted user!"

def test_thread_safe_concurrent_initialization():
    """Verify that 20 concurrent threads accessing the same cold report build only once without race conditions."""
    path = os.path.normpath("C:/fake_db/user_concurrency/report_rep_01")
    chunks = _make_dummy_chunks("Concurrent Clinical Report")

    results = []
    def worker():
        bm = rag_service._get_or_create_bm25(path, chunks)
        results.append(id(bm))

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker) for _ in range(20)]
        for f in futures:
            f.result()

    # All 20 threads must have received the exact same memory object ID
    assert len(results) == 20
    assert len(set(results)) == 1, "Concurrency race condition detected: Multiple BM25 instances created for the same report!"

def test_lru_eviction_bounded_capacity():
    """Verify that cache respects maximum size and evicts oldest items."""
    # Set small test capacity
    original_max = rag_service._max_bm25_cache_size
    rag_service._max_bm25_cache_size = 3

    try:
        p1 = "C:/fake/rep_1"
        p2 = "C:/fake/rep_2"
        p3 = "C:/fake/rep_3"
        p4 = "C:/fake/rep_4"

        c = _make_dummy_chunks("Dummy")

        rag_service._get_or_create_bm25(p1, c)
        rag_service._get_or_create_bm25(p2, c)
        rag_service._get_or_create_bm25(p3, c)

        assert len(rag_service._bm25_cache) == 3
        assert p1 in rag_service._bm25_cache

        # Access p1 to make it recently used
        rag_service._get_or_create_bm25(p1, c)

        # Insert 4th item -> should evict p2 (the least recently used)
        rag_service._get_or_create_bm25(p4, c)

        assert len(rag_service._bm25_cache) == 3
        assert p4 in rag_service._bm25_cache
        assert p1 in rag_service._bm25_cache
        assert p2 not in rag_service._bm25_cache, "LRU Eviction failed: p2 should have been evicted!"

    finally:
        rag_service._max_bm25_cache_size = original_max

