import sys
import os
import time
import asyncio
import json
import urllib.request
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("backend"))
from app.services.rag_service import rag_service

rag_service.vector_db_path = os.path.abspath(os.path.join("backend", "vector_stores"))
load_dotenv()

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

QUERY = "What are the abnormal findings across all lab panels?"

async def get_groq_quota_status():
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    data = json.dumps({"model": model, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 5}).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "User-Agent": "curl/7.68.0"}
    )
    def _fetch():
        try:
            with urllib.request.urlopen(req) as resp:
                headers = dict(resp.headers)
                return {
                    "status": resp.status,
                    "limit_tokens": headers.get("x-ratelimit-limit-tokens", "N/A"),
                    "remaining_tokens": headers.get("x-ratelimit-remaining-tokens", "N/A"),
                    "reset_tokens_sec": headers.get("x-ratelimit-reset-tokens", "N/A"),
                    "limit_requests": headers.get("x-ratelimit-limit-requests", "N/A"),
                    "remaining_requests": headers.get("x-ratelimit-remaining-requests", "N/A")
                }
        except urllib.error.HTTPError as he:
            headers = dict(he.headers)
            return {
                "status": he.code,
                "error": str(he),
                "retry_after": headers.get("retry-after", "N/A"),
                "remaining_tokens": headers.get("x-ratelimit-remaining-tokens", "0"),
                "reset_tokens_sec": headers.get("x-ratelimit-reset-tokens", "N/A")
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}

    return await asyncio.to_thread(_fetch)

async def instrumented_single_query(req_id: int):
    t_start = time.perf_counter()
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{TEST_USER_ID}")

    # Stage 1: Embedding Latency
    t_emb_0 = time.perf_counter()
    _ = await asyncio.to_thread(rag_service.embeddings.embed_query, QUERY)
    emb_ms = (time.perf_counter() - t_emb_0) * 1000

    # Stage 2: Retrieval Latency (FAISS + BM25)
    t_ret_0 = time.perf_counter()
    context = await rag_service._parallel_retrieve_contexts(TEST_REPORT_IDS, user_folder, QUERY, TEST_REPORT_DATA)
    ret_ms = (time.perf_counter() - t_ret_0) * 1000

    # Stage 3: LLM Execution
    from langchain_core.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_template("""
    You are a Clinical Data Specialist. Answer based ONLY on the context below.
    CONTEXT: {context}
    QUESTION: {question}
    STRICT CLINICAL PROTOCOL: Answer in professional English.
    """)
    chain = prompt | rag_service.llm

    t_llm_0 = time.perf_counter()
    retries = 0
    try:
        res = await chain.ainvoke({"context": context, "question": QUERY})
        llm_status = "200 OK"
    except Exception as e:
        llm_status = f"ERR: {str(e)[:20]}"

    llm_ms = (time.perf_counter() - t_llm_0) * 1000
    total_ms = (time.perf_counter() - t_start) * 1000

    return {
        "id": req_id,
        "emb_ms": round(emb_ms, 2),
        "ret_ms": round(ret_ms, 2),
        "llm_ms": round(llm_ms, 2),
        "total_ms": round(total_ms, 2),
        "status": llm_status
    }

async def run_detailed_diagnostic(num_requests: int = 5):
    print("=" * 72)
    print("    ROOT-CAUSE DIAGNOSTIC: PER-STAGE BREAKDOWN & GROQ RATE LIMITS")
    print("=" * 72)

    # 1. Inspect live Groq Quota
    print("Checking live Groq API Gateway quota headers...", flush=True)
    quota = await get_groq_quota_status()
    print("-" * 72)
    print(f"Groq Model Quota      : limit_tokens = {quota.get('limit_tokens')} TPM | limit_requests = {quota.get('limit_requests')} RPM")
    print(f"Current Available     : remaining_tokens = {quota.get('remaining_tokens')} | reset_in = {quota.get('reset_tokens_sec')}")
    print("-" * 72)

    print(f"\nDispatching {num_requests} concurrent requests to measure exact per-stage latency...", flush=True)
    tasks = [instrumented_single_query(i + 1) for i in range(num_requests)]
    results = await asyncio.gather(*tasks)

    print("\n" + "=" * 72)
    print(f"{'Req #':<6} | {'Embedding':<10} | {'Retrieval':<10} | {'Groq LLM Wait':<16} | {'Total E2E':<12} | {'Status'}")
    print("-" * 72)
    for r in results:
        print(f"Req {r['id']:<2} | {r['emb_ms']:>6.1f} ms  | {r['ret_ms']:>6.1f} ms  | {r['llm_ms']:>10.1f} ms     | {r['total_ms']:>8.1f} ms  | {r['status']}")
    print("=" * 72)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    asyncio.run(run_detailed_diagnostic(n))

