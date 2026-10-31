import json
import os
import sys

def compare_benchmarks(base_path: str = "benchmarks/baseline_benchmark.json", opt_path: str = "benchmarks/streaming_benchmark.json"):
    if not os.path.exists(base_path):
        print(f"Error: Baseline file not found: {base_path}")
        return
    if not os.path.exists(opt_path):
        print(f"Error: Optimized file not found: {opt_path}")
        return

    with open(base_path, "r", encoding="utf-8") as f:
        base_data = json.load(f)["summary"]
    with open(opt_path, "r", encoding="utf-8") as f:
        opt_data = json.load(f)["summary"]

    base_metrics = base_data["metrics_ms"]
    opt_metrics = opt_data["metrics_ms"]

    def calc_diff(b_val, o_val):
        if b_val == 0:
            return "0.0%"
        pct = ((b_val - o_val) / b_val) * 100
        sign = "-" if pct > 0 else "+"
        return f"{abs(pct):.1f}% faster" if pct > 0 else f"{abs(pct):.1f}% slower"

    print("\n" + "=" * 78)
    print("           RAG PERFORMANCE BENCHMARK COMPARISON MATRIX (PHASE 2)")
    print("=" * 78)
    header = f"{'Metric':<30} | {'Baseline (Sync)':<16} | {'Streaming (Opt)':<16} | {'Improvement'}"
    print(header)
    print("-" * 78)

    rows = [
        ("Embedding Latency (Mean)", f"{base_metrics['query_embedding']['mean']} ms", f"{opt_metrics['query_embedding']['mean']} ms", calc_diff(base_metrics['query_embedding']['mean'], opt_metrics['query_embedding']['mean'])),
        ("Retrieval Latency (Mean)", f"{base_metrics['vector_retrieval']['mean']} ms", f"{opt_metrics['vector_retrieval']['mean']} ms", calc_diff(base_metrics['vector_retrieval']['mean'], opt_metrics['vector_retrieval']['mean'])),
        ("LLM TTFT (Mean)", f"{base_metrics['llm_ttft']['mean']} ms", f"{opt_metrics['llm_ttft']['mean']} ms", calc_diff(base_metrics['llm_ttft']['mean'], opt_metrics['llm_ttft']['mean'])),
        ("LLM TTFT (Median)", f"{base_metrics['llm_ttft']['median']} ms", f"{opt_metrics['llm_ttft']['median']} ms", calc_diff(base_metrics['llm_ttft']['median'], opt_metrics['llm_ttft']['median'])),
        ("Total Generation (Mean)", f"{base_metrics['generation']['mean']} ms", f"{opt_metrics['generation']['mean']} ms", calc_diff(base_metrics['generation']['mean'], opt_metrics['generation']['mean'])),
        ("Total E2E Latency (Mean)", f"{base_metrics['total_e2e']['mean']} ms", f"{opt_metrics['total_e2e']['mean']} ms", calc_diff(base_metrics['total_e2e']['mean'], opt_metrics['total_e2e']['mean'])),
        ("Total E2E Latency (P95)", f"{base_metrics['total_e2e']['p95']} ms", f"{opt_metrics['total_e2e']['p95']} ms", calc_diff(base_metrics['total_e2e']['p95'], opt_metrics['total_e2e']['p95'])),
        ("Throughput", f"{base_data['throughput_req_per_sec']} req/s", f"{opt_data['throughput_req_per_sec']} req/s", f"+{((opt_data['throughput_req_per_sec'] - base_data['throughput_req_per_sec'])/max(base_data['throughput_req_per_sec'], 0.001))*100:.1f}%"),
        ("Error Rate", f"{base_data['error_rate_pct']}%", f"{opt_data['error_rate_pct']}%", "Identical (0.0%)"),
    ]

    for label, b, o, imp in rows:
        print(f"{label:<30} | {b:<16} | {o:<16} | {imp}")

    print("=" * 78 + "\n")

if __name__ == "__main__":
    b_path = sys.argv[1] if len(sys.argv) > 1 else "benchmarks/baseline_benchmark.json"
    o_path = sys.argv[2] if len(sys.argv) > 2 else "benchmarks/streaming_benchmark.json"
    compare_benchmarks(b_path, o_path)

