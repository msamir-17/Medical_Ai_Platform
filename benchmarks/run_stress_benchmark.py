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

QUERIES = [
    "What is the patient's glucose level and is it elevated?",
    "What is the serum potassium level and what are the clinical risks?",
    "Summarize the arterial blood gas (ABG) findings.",
    "Are there any signs of metabolic acidosis in the report?",
    "What are the abnormal findings across all lab panels?"
]

async def execute_request(req_id: int, query: str):
    t0 = time.perf_counter()
    try:
        res = await rag_service.aquery_report(
            question=query,
            user_id=TEST_USER_ID,
            mode="single",
            report_ids=TEST_REPORT_IDS,
            all_report_data=TEST_REPORT_DATA
        )
        latency = (time.perf_counter() - t0) * 1000
        return {"id": req_id, "latency_ms": latency, "status": "SUCCESS"}
    except Exception as e:
        latency = (time.perf_counter() - t0) * 1000
        return {"id": req_id, "latency_ms": latency, "status": f"FAILED: {e}"}

def p_val(data, percentile):
    if not data:
        return 0.0
    s = sorted(data)
    idx = int(percentile * len(s))
    return s[min(idx, len(s) - 1)]

async def run_stress_test(total_requests: int = 30, concurrency: int = 5):
    print("=" * 68)
    print("    RAG PIPELINE HIGH-VOLUME STRESS BENCHMARK (30-50 RUNS)")
    print("=" * 68)
    print(f"Total Requests : {total_requests}")
    print(f"Concurrency    : {concurrency} requests per batch/wave")
    print(f"Batches        : {total_requests // concurrency} waves")
    print("-" * 68)

    all_results = []
    t_start = time.perf_counter()

    for batch_idx in range(0, total_requests, concurrency):
        batch_num = (batch_idx // concurrency) + 1
        print(f"Executing Batch {batch_num}/{(total_requests + concurrency - 1)//concurrency} ({concurrency} concurrent requests)...", flush=True)
        batch_tasks = [
            execute_request(batch_idx + i + 1, QUERIES[(batch_idx + i) % len(QUERIES)])
            for i in range(min(concurrency, total_requests - batch_idx))
        ]
        batch_res = await asyncio.gather(*batch_tasks)
        all_results.extend(batch_res)
        # Small metering gap between waves to allow Groq token replenishment
        await asyncio.sleep(0.5)

    total_time = time.perf_counter() - t_start
    successful = [r for r in all_results if r["status"] == "SUCCESS"]
    failed = [r for r in all_results if r["status"] != "SUCCESS"]

    latencies = [r["latency_ms"] for r in successful]

    mean_lat = statistics.mean(latencies) if latencies else 0.0
    p50_lat = statistics.median(latencies) if latencies else 0.0
    p90_lat = p_val(latencies, 0.90)
    p95_lat = p_val(latencies, 0.95)
    max_lat = max(latencies) if latencies else 0.0
    throughput = len(successful) / total_time if total_time > 0 else 0.0

    print("\n" + "=" * 68)
    print("                 STRESS BENCHMARK RESULTS")
    print("=" * 68)
    print(f"{'Metric':<30} | {'Measurement'}")
    print("-" * 68)
    print(f"{'Total Executions':<30} | {total_requests}")
    print(f"{'Successful Executions':<30} | {len(successful)} ({round(len(successful)/total_requests*100, 1)}%)")
    print(f"{'Failed Executions':<30} | {len(failed)}")
    print(f"{'Mean Latency':<30} | {mean_lat:.2f} ms")
    print(f"{'P50 Latency (Median)':<30} | {p50_lat:.2f} ms")
    print(f"{'P90 Latency':<30} | {p90_lat:.2f} ms")
    print(f"{'P95 Latency':<30} | {p95_lat:.2f} ms")
    print(f"{'Max Latency (Outlier)':<30} | {max_lat:.2f} ms")
    print(f"{'Total Duration':<30} | {total_time:.2f} s")
    print(f"{'Sustained Throughput':<30} | {throughput:.2f} req/s")
    print("=" * 68)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    c = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    asyncio.run(run_stress_test(n, c))

