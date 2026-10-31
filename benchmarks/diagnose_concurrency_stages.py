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

QUERIES = [
    "What is the patient's glucose level and is it elevated?",
    "What is the serum potassium level and what are the clinical risks?",
    "Summarize the arterial blood gas (ABG) findings.",
    "Are there any signs of metabolic acidosis in the report?",
    "What are the abnormal findings across all lab panels?"
]

async def instrumented_worker(client_id: int, query: str):
    t_req_start = time.perf_counter()
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{TEST_USER_ID}")

    # Stage 1: Retrieval (FAISS + BM25)
    t_ret_start = time.perf_counter()
    context = await rag_service._parallel_retrieve_contexts(TEST_REPORT_IDS, user_folder, query, TEST_REPORT_DATA)
    t_ret_end = time.perf_counter()
    ret_duration_ms = (t_ret_end - t_ret_start) * 1000

    # Stage 2: LLM Invocation
    from langchain_core.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_template("""
    You are a Clinical Data Specialist. Answer based ONLY on the context below.
    CONTEXT: {context}
    QUESTION: {question}
    STRICT CLINICAL PROTOCOL: Answer in professional English.
    """)
    chain = prompt | rag_service.llm

    t_llm_start = time.perf_counter()
    res = await chain.ainvoke({"context": context, "question": query})
    t_llm_end = time.perf_counter()
    llm_duration_ms = (t_llm_end - t_llm_start) * 1000

    total_duration_ms = (time.perf_counter() - t_req_start) * 1000

    return {
        "client_id": client_id,
        "query": query[:35] + "...",
        "retrieval_ms": round(ret_duration_ms, 2),
        "llm_ms": round(llm_duration_ms, 2),
        "total_ms": round(total_duration_ms, 2),
        "response_len": len(res.content)
    }

async def run_stage_diagnostic():
    print("=" * 72)
    print("      DEEP LATENCY STAGE DIAGNOSTIC (5 CONCURRENT REQUESTS)")
    print("=" * 72)
    print("Dissecting where time is spent: Retrieval vs Groq LLM API...")
    print("-" * 72)

    tasks = [instrumented_worker(i + 1, q) for i, q in enumerate(QUERIES)]
    results = await asyncio.gather(*tasks)

    print(f"{'Client':<8} | {'Retrieval Latency':<18} | {'Groq LLM Latency':<18} | {'Total Latency'}")
    print("-" * 72)
    for r in results:
        print(f"Client {r['client_id']:<2} | {r['retrieval_ms']:>10.2f} ms     | {r['llm_ms']:>10.2f} ms     | {r['total_ms']:>10.2f} ms")

    print("-" * 72)
    slowest = max(results, key=lambda x: x["total_ms"])
    fastest = min(results, key=lambda x: x["total_ms"])
    print(f"Fastest Client: Client {fastest['client_id']} ({fastest['total_ms']:.2f} ms)")
    print(f"Slowest Client: Client {slowest['client_id']} ({slowest['total_ms']:.2f} ms)")
    print(f"Slowest Retrieval Component : {slowest['retrieval_ms']:.2f} ms ({round(slowest['retrieval_ms']/slowest['total_ms']*100, 2)}% of total)")
    print(f"Slowest Groq LLM Component  : {slowest['llm_ms']:.2f} ms ({round(slowest['llm_ms']/slowest['total_ms']*100, 2)}% of total)")
    print("=" * 72)

if __name__ == "__main__":
    asyncio.run(run_stage_diagnostic())

