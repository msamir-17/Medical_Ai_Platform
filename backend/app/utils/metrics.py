import time
from contextlib import contextmanager
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# --- RAG Request Telemetry ---
RAG_REQUEST_TOTAL = Counter(
    "rag_request_total",
    "Total count of RAG requests processed",
    ["status"]  # "success", "error", "fallback"
)

# --- Latency Histograms ---
RAG_RETRIEVAL_LATENCY_SECONDS = Histogram(
    "rag_retrieval_latency_seconds",
    "Latency of FAISS and BM25 retrieval stage in seconds",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

RAG_LLM_LATENCY_SECONDS = Histogram(
    "rag_llm_latency_seconds",
    "Time taken for LLM generation response in seconds",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 3.5, 5.0, 10.0]
)

RAG_TTFT_SECONDS = Histogram(
    "rag_ttft_seconds",
    "Time to First Token (TTFT) in streaming responses",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0]
)

OCR_LATENCY_SECONDS = Histogram(
    "ocr_latency_seconds",
    "Time taken to extract text via EasyOCR pipeline",
    buckets=[0.5, 1.0, 2.0, 4.0, 8.0, 15.0]
)

MODEL_PREDICT_LATENCY_SECONDS = Histogram(
    "model_predict_latency_seconds",
    "Inference latency of tabular ML models",
    ["model"],  # "diabetes", "heart"
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
)

# --- Reliability & Cache Counters ---
GROQ_RATE_LIMIT_TOTAL = Counter(
    "groq_rate_limit_total",
    "Total HTTP 429 rate limit errors encountered from Groq"
)

SEMANTIC_CACHE_HIT_TOTAL = Counter(
    "semantic_cache_hit_total",
    "Total number of semantic query cache hits"
)

SEMANTIC_CACHE_MISS_TOTAL = Counter(
    "semantic_cache_miss_total",
    "Total number of semantic query cache misses"
)

BM25_CACHE_HIT_TOTAL = Counter(
    "bm25_cache_hit_total",
    "Total in-memory BM25 index cache hits"
)

BM25_CACHE_MISS_TOTAL = Counter(
    "bm25_cache_miss_total",
    "Total in-memory BM25 index cache misses"
)

RAG_FALLBACK_TOTAL = Counter(
    "rag_fallback_total",
    "Total fallback responses generated when Groq was unavailable"
)


# --- Non-Invasive Context Managers (Clean Timing Hooks) ---
@contextmanager
def track_retrieval_time():
    """Context manager to record retrieval latency non-invasively."""
    start = time.perf_counter()
    try:
        yield
    finally:
        RAG_RETRIEVAL_LATENCY_SECONDS.observe(time.perf_counter() - start)


@contextmanager
def track_llm_time():
    """Context manager to record LLM response latency non-invasively."""
    start = time.perf_counter()
    try:
        yield
    finally:
        RAG_LLM_LATENCY_SECONDS.observe(time.perf_counter() - start)


@contextmanager
def track_model_predict_time(model_name: str):
    """Context manager to record tabular ML model inference time."""
    start = time.perf_counter()
    try:
        yield
    finally:
        MODEL_PREDICT_LATENCY_SECONDS.labels(model=model_name).observe(time.perf_counter() - start)


def get_metrics_data() -> bytes:
    """Generate Prometheus exposition format bytes for the /metrics endpoint."""
    return generate_latest()

