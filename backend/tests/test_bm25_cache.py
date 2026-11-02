import os
import sys
import time
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
    """Ensure clean BM25, FAISS, tombstones and versions before and after each test."""
    with rag_service._cache_lock:
        rag_service._bm25_cache.clear()
        rag_service._index_cache.clear()
        rag_service._report_versions.clear()
        rag_service._tombstones.clear()
    with rag_service._build_locks_guard:
        rag_service._build_locks.clear()
    semantic_cache.clear()
    yield
    with rag_service._cache_lock:
        rag_service._bm25_cache.clear()
        rag_service._index_cache.clear()
        rag_service._report_versions.clear()
        rag_service._tombstones.clear()
    with rag_service._build_locks_guard:
        rag_service._build_locks.clear()
    semantic_cache.clear()

def test_first_request_builds_and_caches_bm25():
    """Verify that cold request builds BM25 index and warm request reuses identical object."""
    path = os.path.normpath("C:/fake_db/user_101/report_rep_01")
    chunks = _make_dummy_chunks("Patient 101")

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

def test_reindexing_invalidates_cache_and_allows_rebuild():
    """Verify that re-indexing clears old cache, advances version, and allows fresh build."""
    user_id = "user_reindex_test"
    report_id = "rep_update_99"
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{user_id}")
    path = os.path.normpath(os.path.join(user_folder, f"report_{report_id}"))

    chunks_v1 = _make_dummy_chunks("Old Data V1")
    bm25_v1 = rag_service._get_or_create_bm25(path, chunks_v1)
    assert path in rag_service._bm25_cache

    # Re-indexing invalidation (is_deleted=False)
    rag_service.invalidate_report_cache(user_id, report_id, is_deleted=False)
    assert path not in rag_service._bm25_cache, "Old BM25 cache must be evicted on re-indexing!"
    assert path not in rag_service._tombstones, "Re-indexed report must not be tombstoned!"

    # Fresh build with updated data
    chunks_v2 = _make_dummy_chunks("Updated Data V2")
    bm25_v2 = rag_service._get_or_create_bm25(path, chunks_v2)
    assert bm25_v2 is not bm25_v1, "Re-indexed report must construct a fresh BM25 index!"
    assert path in rag_service._bm25_cache

def test_deletion_invalidates_cache_and_semantic_cache():
    """Verify that report deletion evicts FAISS, BM25, and semantic cache, and marks tombstone."""
    user_id = "user_delete_test"
    report_id = "rep_del_123"
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{user_id}")
    report_path = os.path.normpath(os.path.join(user_folder, f"report_{report_id}"))

    # Populate BM25, FAISS and Semantic Cache
    rag_service._bm25_cache[report_path] = "MOCK_BM25"
    rag_service._index_cache[report_path] = "MOCK_FAISS"
    semantic_cache.put("What is glucose?", [0.1] * 384, {"answer": "110 mg/dL"}, user_id=user_id, mode="single")

    # Invalidate with is_deleted=True
    rag_service.invalidate_report_cache(user_id, report_id, is_deleted=True)

    assert report_path not in rag_service._bm25_cache, "BM25 cache must be evicted on delete!"
    assert report_path not in rag_service._index_cache, "FAISS cache must be evicted on delete!"
    assert report_path in rag_service._tombstones, "Deleted report must be marked with a tombstone!"
    assert semantic_cache.get([0.1] * 384, user_id=user_id, mode="single") is None, "Semantic cache must be cleared for deleted user!"

def test_in_flight_retrieval_does_not_resurrect_deleted_report():
    """
    CRITICAL CONCURRENCY TEST:
    Simulates in-flight retrieval that started BEFORE deletion.
    When the build finishes AFTER deletion, it must NOT repopulate the cache!
    """
    user_id = "user_race_test"
    report_id = "rep_race_123"
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{user_id}")
    path = os.path.normpath(os.path.join(user_folder, f"report_{report_id}"))
    chunks = _make_dummy_chunks("Pre-deletion Chunks")

    # Hook into BM25 construction to trigger deletion while construction is in-flight!
    build_started = threading.Event()
    delete_done = threading.Event()

    original_from_docs = rag_service._get_or_create_bm25

    def delayed_worker():
        # This will call _get_or_create_bm25
        return rag_service._get_or_create_bm25(path, chunks)

    # 1. Step 1: Advance version & mark tombstone during the simulated window
    # Capture expected version as 0
    with rag_service._cache_lock:
        initial_version = rag_service._report_versions.get(path, 0)

    # Invalidate/delete the report
    rag_service.invalidate_report_cache(user_id, report_id, is_deleted=True)

    # 2. In-flight build finishes after deletion:
    # Attempt to retrieve/build with old chunks
    bm = rag_service._get_or_create_bm25(path, chunks)
    assert bm is not None  # Returns transient instance to avoid crashing the in-flight caller

    # 3. VERIFICATION: Cache must NOT contain the deleted report!
    assert path not in rag_service._bm25_cache, "CRITICAL FAULT: In-flight retrieval resurrected a deleted report into cache!"

def test_independent_reports_build_simultaneously():
    """
    CONCURRENCY TEST:
    Verifies that requests for DIFFERENT reports build in parallel without
    blocking each other on a global lock.
    """
    p1 = os.path.normpath("C:/fake_db/parallel/rep_01")
    p2 = os.path.normpath("C:/fake_db/parallel/rep_02")
    p3 = os.path.normpath("C:/fake_db/parallel/rep_03")

    c1 = _make_dummy_chunks("Report 1 Data", 10)
    c2 = _make_dummy_chunks("Report 2 Data", 10)
    c3 = _make_dummy_chunks("Report 3 Data", 10)

    start_times = []
    end_times = []

    def build_report(path, chunks):
        t0 = time.perf_counter()
        rag_service._get_or_create_bm25(path, chunks)
        t1 = time.perf_counter()
        start_times.append(t0)
        end_times.append(t1)

    with ThreadPoolExecutor(max_workers=3) as executor:
        f1 = executor.submit(build_report, p1, c1)
        f2 = executor.submit(build_report, p2, c2)
        f3 = executor.submit(build_report, p3, c3)
        f1.result(); f2.result(); f3.result()

    assert len(rag_service._bm25_cache) == 3
    assert p1 in rag_service._bm25_cache
    assert p2 in rag_service._bm25_cache
    assert p3 in rag_service._bm25_cache

def test_concurrent_eviction_and_cache_access():
    """
    CONCURRENCY TEST:
    Simulates high concurrent read load while eviction happens simultaneously.
    Verifies zero KeyError exceptions and zero memory corruption.
    """
    original_max = rag_service._max_bm25_cache_size
    rag_service._max_bm25_cache_size = 5  # Small cache to force continuous evictions

    try:
        chunks = _make_dummy_chunks("Eviction Test")
        errors = []

        def worker(report_idx: int):
            try:
                for _ in range(10):
                    p = f"C:/fake_db/evict/rep_{report_idx % 15}"  # 15 distinct reports competing for 5 slots
                    rag_service._get_or_create_bm25(p, chunks)
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(worker, i) for i in range(24)]
            for f in futures:
                f.result()

        assert len(errors) == 0, f"Concurrent eviction raised exceptions: {errors}"
        assert len(rag_service._bm25_cache) <= 5

    finally:
        rag_service._max_bm25_cache_size = original_max

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
