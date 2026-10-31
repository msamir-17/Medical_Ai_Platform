import sys
import os
import time
import asyncio
import statistics

sys.path.insert(0, os.path.abspath("backend"))
from app.services.rag_service import rag_service

rag_service.vector_db_path = os.path.abspath(os.path.join("backend", "vector_stores"))

TEST_USER_ID = "test_user"
TEST_REPORT_IDS = ["rep_kanta"]
TEST_REPORT_DATA = [{
    "id": "rep_kanta",
    "patient_info": {"name": "MR. KANTA YADAV", "age": "74", "gender": "Male"},
    "extracted_values": [
        {"marker": "GLUCOSE", "value": "185.2", "unit": "mg/dL", "status": "HIGH", "ref_range": "70-100"},
        {"marker": "POTASSIUM", "value": "6.03", "unit": "mEq/lit", "status": "HIGH", "ref_range": "3.5-5.0"}
    ],
    "report_type": "Blood Test",
    "date": "2026-03-23"
}]

BENCHMARK_QUERIES = [
    "What is the patient's glucose level and is it elevated?",
    "What is the serum potassium level and what are the clinical risks?",
    "Summarize the arterial blood gas (ABG) findings.",
    "Are there any signs of metabolic acidosis in the report?",
    "What are the abnormal findings across all lab panels?"
]

async def run_single_request(client_id: int, query: str):
    t0 = time.perf_counter()
    try:
        res = await rag_service.aquery_report(
            question=query,
            user_id=TEST_USER_ID,
            mode="single",
            report_ids=TEST_REPORT_IDS,
            all_report_data=TEST_REPORT_DATA
        )
        duration_ms = (time.perf_counter() - t0) * 1000
        return {"id": client_id, "latency_ms": duration_ms, "status": "SUCCESS"}
    except Exception as e:
        duration_ms = (time.perf_counter() - t0) * 1000
        return {"id": client_id, "latency_ms": duration_ms, "status": f"FAILED: {e}"}

def p_val(data, percentile):
    if not data:
        return 0.0
    sorted_d = sorted(data)
    idx = int(percentile * len(sorted_d))
    return sorted_d[min(idx, len(sorted_d) - 1)]

async def run_concurrency_p95_benchmark(concurrent_users: int = 5):
    print("=" * 68)
    print("   CONCURRENT LOAD BENCHMARK (P50 / P95 LATENCY & THROUGHPUT)")
    print("=" * 68)
    print(f"Concurrency Level : {concurrent_users} Simultaneous Users")
    print(f"Workload           : Real Medical Report Query across Groq + FAISS")
    print("-" * 68)
    print("Executing concurrent requests in parallel...", flush=True)

    t_start = time.perf_counter()
    tasks = [
        run_single_request(i + 1, BENCHMARK_QUERIES[i % len(BENCHMARK_QUERIES)])
        for i in range(concurrent_users)
    ]
    results = await asyncio.gather(*tasks)
    total_time_sec = time.perf_counter() - t_start

    successful = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] != "SUCCESS"]

    latencies = [r["latency_ms"] for r in successful]

    mean_lat = round(statistics.mean(latencies), 2) if latencies else 0
    p50_lat = round(statistics.median(latencies), 2) if latencies else 0
    p90_lat = round(p_val(latencies, 0.90), 2) if latencies else 0
    p95_lat = round(p_val(latencies, 0.95), 2) if latencies else 0
    throughput = round(len(successful) / total_time_sec, 2) if total_time_sec > 0 else 0

    print(f"{'Client #':<12} | {'Response Status':<18} | {'Latency (ms)'}")
    print("-" * 68)
    for r in results:
        print(f"Client {r['id']:<5} | {r['status']:<18} | {r['latency_ms']:.2f} ms")

    print("-" * 68)
    print(f"{'Metric':<30} | {'Measurement'}")
    print("-" * 68)
    print(f"{'Mean Latency':<30} | {mean_lat:.2f} ms")
    print(f"{'P50 Latency (Median)':<30} | {p50_lat:.2f} ms")
    print(f"{'P90 Latency':<30} | {p90_lat:.2f} ms")
    print(f"{'P95 Latency':<30} | {p95_lat:.2f} ms")
    print(f"{'Total Execution Time':<30} | {total_time_sec:.2f} s")
    print(f"{'Effective Throughput':<30} | {throughput} req/s")
    print(f"{'Error / Drop Rate':<30} | {len(failed)} ({round(len(failed)/concurrent_users*100, 1)}%)")
    print("=" * 68)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    asyncio.run(run_concurrency_p95_benchmark(n))

