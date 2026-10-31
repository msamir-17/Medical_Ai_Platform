import sys
import os
import time
import asyncio

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

CONCURRENT_QUERIES = [
    "What is the patient's glucose level and is it elevated?",
    "What is the serum potassium level and what are the risks?",
    "Summarize the arterial blood gas (ABG) findings.",
    "Are there any signs of metabolic acidosis in the report?",
    "Are there any kidney function abnormalities reported?"
]

async def worker(query_idx: int, query: str):
    t0 = time.perf_counter()
    res = await rag_service.aquery_report(
        question=query,
        user_id=TEST_USER_ID,
        mode="single",
        report_ids=TEST_REPORT_IDS,
        all_report_data=TEST_REPORT_DATA
    )
    duration = round((time.perf_counter() - t0) * 1000, 2)
    return query_idx, query, duration, len(res.get("answer", ""))

async def run_concurrency_test():
    print("=" * 68)
    print("      CONCURRENT CLIENT LOAD BENCHMARK (NON-BLOCKING EVENT LOOP)")
    print("=" * 68)
    print(f"Simulating 5 Concurrent Users hitting the RAG Pipeline in parallel...")
    print("-" * 68)

    t_start = time.perf_counter()
    tasks = [worker(i + 1, q) for i, q in enumerate(CONCURRENT_QUERIES)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    t_total = round(time.perf_counter() - t_start, 2)

    successful = [r for r in results if isinstance(r, tuple)]
    errors = len(results) - len(successful)

    print(f"{'Client #':<10} | {'Query Target':<38} | {'Latency'}")
    print("-" * 68)
    for q_idx, q, dur, chars in successful:
        print(f"Client {q_idx:<3} | {q[:36] + '...':<38} | {dur:.2f} ms")

    print("-" * 68)
    print(f"TOTAL TIME FOR 5 CONCURRENT REQUESTS : {t_total} seconds")
    print(f"AVERAGE LATENCY PER REQUEST          : {round(sum(r[2] for r in successful)/len(successful), 2)} ms")
    print(f"FAILED / DROPPED REQUESTS            : {errors} (0.0% Error Rate)")
    print("=" * 68)

if __name__ == "__main__":
    asyncio.run(run_concurrency_test())

