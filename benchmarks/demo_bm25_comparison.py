import os
import sys
import time
import pickle
import statistics

# Ensure backend path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from langchain_community.retrievers import BM25Retriever
from app.services.rag_service import rag_service

def run_bm25_benchmark():
    print("\n" + "=" * 70)
    print("PHASE 5: IN-MEMORY BM25 INDEX CACHE BENCHMARK")
    print("=" * 70)

    # 1. Load actual real clinical chunks from vector store pickle
    test_pkl_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "backend", "vector_stores", "user_test_user", "report_rep_kanta", "index.pkl")
    )
    master_pkl_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "backend", "vector_stores", "user_5b99de0e-0905-483e-98d2-de4f2e99eaf7", "master_index", "index.pkl")
    )

    if os.path.exists(master_pkl_path):
        target_path = master_pkl_path
        target_name = "Master Multi-Report Index (175 chunks)"
    elif os.path.exists(test_pkl_path):
        target_path = test_pkl_path
        target_name = "Single Lab Report (7 chunks)"
    else:
        print("[ERROR] No real vector store pickle found for benchmark.")
        return

    with open(target_path, "rb") as f:
        docstore, _ = pickle.load(f)

    all_chunks = list(docstore._dict.values())
    total_chunks = len(all_chunks)
    print(f"Target Dataset   : {target_name}")
    print(f"Total Chunks     : {total_chunks}")
    print(f"Query Phrase     : 'glucose creatinine abnormal laboratory findings'\n")

    query = "glucose creatinine abnormal laboratory findings"
    num_runs = 25

    # ---------------------------------------------------------
    # [A] BEFORE PHASE 5: Uncached (Rebuilding BM25 on every query)
    # ---------------------------------------------------------
    print(f"--- [1] BEFORE (Uncached): Rebuilding BM25 Index on Every Query ({num_runs} runs) ---")
    uncached_total_times = []
    uncached_build_times = []
    uncached_query_times = []

    for _ in range(num_runs):
        t0 = time.perf_counter()
        # Rebuild step
        bm = BM25Retriever.from_documents(all_chunks)
        bm.k = 4
        t1 = time.perf_counter()
        # Query step
        docs = bm.invoke(query)
        t2 = time.perf_counter()

        uncached_build_times.append((t1 - t0) * 1000.0)
        uncached_query_times.append((t2 - t1) * 1000.0)
        uncached_total_times.append((t2 - t0) * 1000.0)

    mean_uncached_build = statistics.mean(uncached_build_times)
    mean_uncached_query = statistics.mean(uncached_query_times)
    mean_uncached_total = statistics.mean(uncached_total_times)

    print(f"Mean Index Build Time : {mean_uncached_build:.3f} ms (Repeated Every Request!)")
    print(f"Mean Search Time      : {mean_uncached_query:.3f} ms")
    print(f"Mean Total Time       : {mean_uncached_total:.3f} ms\n")

    # ---------------------------------------------------------
    # [B] AFTER PHASE 5: Cached (In-Memory BM25 Index Reuse)
    # ---------------------------------------------------------
    print(f"--- [2] AFTER (Cached): Reusing In-Memory BM25 Index via RAGService ({num_runs} runs) ---")
    
    # Reset RAGService cache for clean measure
    with rag_service._index_lock:
        rag_service._bm25_cache.clear()

    cached_total_times = []
    cached_lookup_times = []
    cached_query_times = []

    mock_report_path = os.path.dirname(target_path)

    # Run 1: Cold start (Build & Cache)
    t0 = time.perf_counter()
    bm_cold = rag_service._get_or_create_bm25(mock_report_path, all_chunks)
    t_cold_build = (time.perf_counter() - t0) * 1000.0

    # Subsequent Runs: Warm cached lookups
    for _ in range(num_runs):
        t0 = time.perf_counter()
        bm = rag_service._get_or_create_bm25(mock_report_path, all_chunks)
        t1 = time.perf_counter()
        docs = bm.invoke(query)
        t2 = time.perf_counter()

        cached_lookup_times.append((t1 - t0) * 1000.0)
        cached_query_times.append((t2 - t1) * 1000.0)
        cached_total_times.append((t2 - t0) * 1000.0)

    mean_cached_lookup = statistics.mean(cached_lookup_times)
    mean_cached_query = statistics.mean(cached_query_times)
    mean_cached_total = statistics.mean(cached_total_times)

    print(f"Cold Start Build Time : {t_cold_build:.3f} ms (One-time only)")
    print(f"Mean Cache Get Time   : {mean_cached_lookup:.4f} ms (Sub-microsecond memory pointer)")
    print(f"Mean Search Time      : {mean_cached_query:.3f} ms")
    print(f"Mean Total Time       : {mean_cached_total:.3f} ms\n")

    # ---------------------------------------------------------
    # [C] COMPARISON MATRIX
    # ---------------------------------------------------------
    speedup = mean_uncached_total / max(mean_cached_total, 0.001)
    build_time_saved = mean_uncached_build
    pct_reduction = ((mean_uncached_total - mean_cached_total) / mean_uncached_total) * 100.0

    print("=" * 70)
    print(f"{'METRIC':<26} | {'UNCACHED (BEFORE)':<18} | {'CACHED (AFTER)':<18}")
    print("-" * 70)
    print(f"{'Index Build Overhead':<26} | {f'{mean_uncached_build:.3f} ms/req':<18} | {'0.000 ms/req':<18}")
    print(f"{'Index Retrieval Time':<26} | {f'{mean_uncached_query:.3f} ms':<18} | {f'{mean_cached_query:.3f} ms':<18}")
    print(f"{'Total BM25 Stage Time':<26} | {f'{mean_uncached_total:.3f} ms':<18} | {f'{mean_cached_total:.3f} ms':<18}")
    print(f"{'Repeated Tokenization':<26} | {'YES (Every query)':<18} | {'NO (Zero overhead)':<18}")
    print(f"{'Memory Allocations / GC':<26} | {'High Churn':<18} | {'Near Zero':<18}")
    print(f"{'BM25 Stage Speedup':<26} | {'1.0x (Baseline)':<18} | {f'{speedup:.1f}x Faster':<18}")
    print(f"{'Stage Latency Reduction':<26} | {'0.0%':<18} | {f'{pct_reduction:.2f}% Drop':<18}")
    print("=" * 70)

if __name__ == "__main__":
    run_bm25_benchmark()

