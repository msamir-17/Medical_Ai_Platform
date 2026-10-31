import sys
import os
import time
import json
import csv
import statistics
from typing import List, Dict, Any

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath("backend"))

from app.services.rag_service import rag_service

# Ensure vector store path points to existing backend vector_stores
rag_service.vector_db_path = os.path.abspath(os.path.join("backend", "vector_stores"))


TEST_QUERIES = [
    "What are the abnormal findings in the lab report?",
    "What is the patient's glucose level and is it high?",
    "Are there any indicators of kidney or electrolyte dysfunction?",
    "What is the serum potassium level and what are the clinical risks?",
    "Can you summarize the arterial blood gas (ABG) analysis?"
]

TEST_USER_ID = "test_user"
TEST_REPORT_IDS = ["rep_kanta"]
TEST_REPORT_DATA = [{
    "id": "rep_kanta",
    "patient_info": {"name": "MR. KANTA YADAV", "age": "74", "gender": "Male"},
    "extracted_values": [
        {"marker": "GLUCOSE", "value": "185.2", "unit": "mg/dL", "status": "HIGH", "ref_range": "70-100"},
        {"marker": "POTASSIUM", "value": "6.03", "unit": "mEq/lit", "status": "HIGH", "ref_range": "3.5-5.0"},
        {"marker": "SODIUM", "value": "147.60", "unit": "mEq/lit", "status": "HIGH", "ref_range": "135-145"}
    ],
    "report_type": "Blood Test & Biochemistry",
    "date": "2026-03-23"
}]

def run_baseline_benchmark(iterations: int = 2, warmup: int = 1):
    print("=" * 60, flush=True)
    print("RUNNING BASELINE RAG PERFORMANCE BENCHMARK", flush=True)
    print(f"Iterations: {iterations} per query | Warm-up: {warmup} queries", flush=True)
    print("=" * 60, flush=True)

    # 1. Warm-up
    print("\n[Warmup Phase] Warming up embeddings and LLM connection...", flush=True)
    for i in range(warmup):
        _ = rag_service.embeddings.embed_query("warmup query")
        _ = rag_service.query_report(
            question="Quick summary of report",
            user_id=TEST_USER_ID,
            mode="single",
            report_ids=TEST_REPORT_IDS,
            all_report_data=TEST_REPORT_DATA
        )
    print("[Warmup Phase] Complete.\n", flush=True)

    results: List[Dict[str, Any]] = []
    errors = 0
    total_calls = 0

    benchmark_start_time = time.perf_counter()

    for q_idx, query in enumerate(TEST_QUERIES, 1):
        print(f"\nEvaluating Query {q_idx}/{len(TEST_QUERIES)}: \"{query}\"", flush=True)
        for it in range(1, iterations + 1):
            total_calls += 1
            call_start = time.perf_counter()
            try:
                # 1. Query Embedding Latency
                t_emb_start = time.perf_counter()
                query_vector = rag_service.embeddings.embed_query(query)
                emb_latency = (time.perf_counter() - t_emb_start) * 1000  # ms

                # 2. Retrieval Latency (Vector + BM25 Hybrid)
                t_ret_start = time.perf_counter()
                path = os.path.join(rag_service.vector_db_path, f"user_{TEST_USER_ID}", f"report_{TEST_REPORT_IDS[0]}")
                if path in rag_service._index_cache:
                    db = rag_service._index_cache[path]
                else:
                    from langchain_community.vectorstores import FAISS
                    db = FAISS.load_local(path, rag_service.embeddings, allow_dangerous_deserialization=True)
                    rag_service._index_cache[path] = db

                from app.services.rag_service import filter_by_l2_threshold, format_abnormal_findings
                from langchain_community.retrievers import BM25Retriever

                faiss_results = db.similarity_search_with_score(query, k=6)
                faiss_docs = filter_by_l2_threshold(faiss_results, threshold=1.3, query=query)

                all_chunks = [doc for doc in db.docstore._dict.values()] if hasattr(db, 'docstore') else faiss_docs
                bm25 = BM25Retriever.from_documents(all_chunks)
                bm25.k = 4
                bm25_docs = bm25.invoke(query)

                seen_content = set()
                combined_docs = []
                for doc in bm25_docs + faiss_docs:
                    if doc.page_content not in seen_content:
                        seen_content.add(doc.page_content)
                        combined_docs.append(doc)

                ret_latency = (time.perf_counter() - t_ret_start) * 1000  # ms

                # 3. Prompt Construction
                struct_summary = format_abnormal_findings(TEST_REPORT_DATA[0]["extracted_values"])
                report_text_block = "\n".join([d.page_content for d in combined_docs])
                context = f"\n=== SOURCE REPORT: {TEST_REPORT_IDS[0]} ===\n{struct_summary}\n--- EXTRACTED REPORT CONTEXT ---\n" + report_text_block

                # 4. LLM Generation Latency (Baseline Synchronous Call)
                from langchain_core.prompts import ChatPromptTemplate
                prompt = ChatPromptTemplate.from_template("""
        You are a Clinical Data Specialist. Answer based ONLY on the context below.
        
        CONTEXT:
        {context}
        
        QUESTION:
        {question}

        STRICT CLINICAL PROTOCOL:
        1. Never compare different markers (e.g. Glucose vs Hemoglobin).
        2. Analyze ALL lab sections provided (CBC, KFT/Renal, Urine, ABG).
        3. Clearly highlight critical abnormalities (e.g. Severe Anemia, High Creatinine/BUN, Hyperkalemia).
        4. Answer in professional English.
        """)
                chain = prompt | rag_service.llm

                t_gen_start = time.perf_counter()
                response = chain.invoke({"context": context, "question": query})
                t_gen_end = time.perf_counter()
                gen_latency = (t_gen_end - t_gen_start) * 1000  # ms
                
                # In non-streaming baseline, the client receives zero tokens until the entire response completes
                # So client-perceived TTFT in non-streaming baseline equals total generation latency
                ttft_latency = gen_latency

                total_e2e_latency = (time.perf_counter() - call_start) * 1000  # ms

                rec = {
                    "query_id": q_idx,
                    "iteration": it,
                    "query": query,
                    "embedding_latency_ms": round(emb_latency, 2),
                    "retrieval_latency_ms": round(ret_latency, 2),
                    "llm_ttft_ms": round(ttft_latency, 2),
                    "generation_latency_ms": round(gen_latency, 2),
                    "total_e2e_latency_ms": round(total_e2e_latency, 2),
                    "response_length_chars": len(response.content),
                    "status": "SUCCESS"
                }
                results.append(rec)
                print(f"  [Iter {it}] E2E: {rec['total_e2e_latency_ms']}ms | Emb: {rec['embedding_latency_ms']}ms | Ret: {rec['retrieval_latency_ms']}ms | TTFT: {rec['llm_ttft_ms']}ms | Gen: {rec['generation_latency_ms']}ms", flush=True)

            except Exception as e:
                errors += 1
                rec = {
                    "query_id": q_idx,
                    "iteration": it,
                    "query": query,
                    "status": f"FAILED: {str(e)}"
                }
                results.append(rec)
                print(f"  [Iter {it}] FAILED: {e}", flush=True)

    total_duration = time.perf_counter() - benchmark_start_time
    successful_results = [r for r in results if r["status"] == "SUCCESS"]

    emb_latencies = [r["embedding_latency_ms"] for r in successful_results]
    ret_latencies = [r["retrieval_latency_ms"] for r in successful_results]
    ttft_latencies = [r["llm_ttft_ms"] for r in successful_results]
    gen_latencies = [r["generation_latency_ms"] for r in successful_results]
    e2e_latencies = [r["total_e2e_latency_ms"] for r in successful_results]

    def p95(data):
        if not data:
            return 0.0
        sorted_d = sorted(data)
        idx = int(0.95 * len(sorted_d))
        return sorted_d[min(idx, len(sorted_d) - 1)]

    summary = {
        "benchmark_type": "BASELINE_UNOPTIMIZED",
        "total_requests": total_calls,
        "successful_requests": len(successful_results),
        "failed_requests": errors,
        "error_rate_pct": round((errors / total_calls) * 100, 2) if total_calls > 0 else 0.0,
        "total_duration_sec": round(total_duration, 2),
        "throughput_req_per_sec": round(len(successful_results) / total_duration, 2) if total_duration > 0 else 0.0,
        "metrics_ms": {
            "query_embedding": {
                "mean": round(statistics.mean(emb_latencies), 2),
                "median": round(statistics.median(emb_latencies), 2),
                "p95": round(p95(emb_latencies), 2)
            },
            "vector_retrieval": {
                "mean": round(statistics.mean(ret_latencies), 2),
                "median": round(statistics.median(ret_latencies), 2),
                "p95": round(p95(ret_latencies), 2)
            },
            "llm_ttft": {
                "mean": round(statistics.mean(ttft_latencies), 2),
                "median": round(statistics.median(ttft_latencies), 2),
                "p95": round(p95(ttft_latencies), 2)
            },
            "generation": {
                "mean": round(statistics.mean(gen_latencies), 2),
                "median": round(statistics.median(gen_latencies), 2),
                "p95": round(p95(gen_latencies), 2)
            },
            "total_e2e": {
                "mean": round(statistics.mean(e2e_latencies), 2),
                "median": round(statistics.median(e2e_latencies), 2),
                "p95": round(p95(e2e_latencies), 2)
            }
        }
    }

    # Save to JSON
    os.makedirs("benchmarks", exist_ok=True)
    with open("benchmarks/baseline_benchmark.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "detailed_runs": results}, f, indent=2)

    # Save to CSV
    csv_file = "benchmarks/baseline_benchmark.csv"
    keys = ["query_id", "iteration", "query", "embedding_latency_ms", "retrieval_latency_ms", "llm_ttft_ms", "generation_latency_ms", "total_e2e_latency_ms", "response_length_chars", "status"]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k, "") for k in keys})

    print("\n" + "=" * 60)
    print("BASELINE BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Total Requests: {total_calls} | Success: {len(successful_results)} | Errors: {errors} ({summary['error_rate_pct']}%)")
    print(f"Throughput: {summary['throughput_req_per_sec']} req/sec")
    print(f"Query Embedding Latency: Mean={summary['metrics_ms']['query_embedding']['mean']}ms, Median={summary['metrics_ms']['query_embedding']['median']}ms, P95={summary['metrics_ms']['query_embedding']['p95']}ms")
    print(f"Vector Retrieval Latency: Mean={summary['metrics_ms']['vector_retrieval']['mean']}ms, Median={summary['metrics_ms']['vector_retrieval']['median']}ms, P95={summary['metrics_ms']['vector_retrieval']['p95']}ms")
    print(f"LLM TTFT Latency:        Mean={summary['metrics_ms']['llm_ttft']['mean']}ms, Median={summary['metrics_ms']['llm_ttft']['median']}ms, P95={summary['metrics_ms']['llm_ttft']['p95']}ms")
    print(f"LLM Generation Latency:  Mean={summary['metrics_ms']['generation']['mean']}ms, Median={summary['metrics_ms']['generation']['median']}ms, P95={summary['metrics_ms']['generation']['p95']}ms")
    print(f"Total E2E Latency:       Mean={summary['metrics_ms']['total_e2e']['mean']}ms, Median={summary['metrics_ms']['total_e2e']['median']}ms, P95={summary['metrics_ms']['total_e2e']['p95']}ms")
    print(f"\nFiles generated: benchmarks/baseline_benchmark.json, benchmarks/baseline_benchmark.csv")
    print("=" * 60)

if __name__ == "__main__":
    run_baseline_benchmark(iterations=3, warmup=1)
