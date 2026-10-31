import sys
import os
import time
import asyncio
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

TEST_PAYLOAD = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a Clinical Data Specialist. Analyze lab reports."},
        {"role": "user", "content": "What are the patient abnormal lab findings? Glucose is 185.2 mg/dL, Potassium is 6.03 mEq/L."}
    ],
    "max_tokens": 150
}

def execute_raw_groq_http(request_id: int):
    """
    Direct low-level HTTP call to Groq API capturing exact first-attempt status,
    headers, retry-after, and provider-reported token usage.
    """
    t0 = time.perf_counter()
    data = json.dumps(TEST_PAYLOAD).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "curl/7.68.0"
        }
    )

    attempts = 0
    max_retries = 2
    delay_total = 0.0

    while attempts <= max_retries:
        attempts += 1
        t_attempt_start = time.perf_counter()
        try:
            with urllib.request.urlopen(req) as resp:
                t_resp = time.perf_counter()
                headers = dict(resp.headers)
                body = json.loads(resp.read().decode())
                usage = body.get("usage", {})
                
                return {
                    "request_id": request_id,
                    "first_attempt_status": resp.status if attempts == 1 else "429 -> 200",
                    "final_status": resp.status,
                    "retries": attempts - 1,
                    "retry_delay_sec": round(delay_total, 2),
                    "wall_clock_sec": round(t_resp - t0, 2),
                    "groq_queue_time": usage.get("queue_time", 0.0),
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "remaining_tokens": headers.get("x-ratelimit-remaining-tokens", "N/A"),
                    "reset_tokens_sec": headers.get("x-ratelimit-reset-tokens", "N/A"),
                    "rpd_remaining": headers.get("x-ratelimit-remaining-requests", "N/A")
                }
        except urllib.error.HTTPError as he:
            headers = dict(he.headers)
            retry_after_hdr = headers.get("retry-after")
            reset_sec_hdr = headers.get("x-ratelimit-reset-tokens")
            
            # Extract retry delay
            try:
                wait_sec = float(retry_after_hdr) if retry_after_hdr else 5.0
            except (ValueError, TypeError):
                wait_sec = 5.0

            if attempts <= max_retries and he.code == 429:
                delay_total += wait_sec
                time.sleep(wait_sec)
                continue
            else:
                return {
                    "request_id": request_id,
                    "first_attempt_status": he.code,
                    "final_status": he.code,
                    "retries": attempts - 1,
                    "retry_delay_sec": round(delay_total, 2),
                    "wall_clock_sec": round(time.perf_counter() - t0, 2),
                    "groq_queue_time": 0.0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "remaining_tokens": headers.get("x-ratelimit-remaining-tokens", "0"),
                    "reset_tokens_sec": reset_sec_hdr or "N/A",
                    "rpd_remaining": headers.get("x-ratelimit-remaining-requests", "N/A")
                }
        except Exception as e:
            return {
                "request_id": request_id,
                "first_attempt_status": "ERR",
                "final_status": "ERR",
                "retries": 0,
                "retry_delay_sec": 0.0,
                "wall_clock_sec": round(time.perf_counter() - t0, 2),
                "error": str(e)
            }

async def run_lifecycle_verification(concurrency: int = 4):
    print("=" * 76)
    print("      GROQ HTTP LIFECYCLE, RETRY & TOKEN USAGE AUDIT")
    print("=" * 76)
    print(f"Target Model      : {model}")
    print(f"Concurrent Waves  : {concurrency} Simultaneous HTTP Requests")
    print("-" * 76)
    print("Firing concurrent requests to intercept raw HTTP headers & retry events...\n", flush=True)

    tasks = [asyncio.to_thread(execute_raw_groq_http, i + 1) for i in range(concurrency)]
    results = await asyncio.gather(*tasks)

    print(f"{'Req':<4} | {'1st Status':<11} | {'Final':<6} | {'Retries':<8} | {'Retry Sleep':<12} | {'Tokens':<8} | {'Wall Clock'}")
    print("-" * 76)
    for r in results:
        t_tokens = f"{r.get('prompt_tokens',0)}+{r.get('completion_tokens',0)}"
        print(f"#{r['request_id']:<3} | {str(r.get('first_attempt_status')):<11} | {str(r.get('final_status')):<6} | {str(r.get('retries')):<8} | {str(r.get('retry_delay_sec')) + 's':<12} | {t_tokens:<8} | {r.get('wall_clock_sec')}s")

    print("-" * 76)
    print(f"Live Remaining Quota : {results[-1].get('remaining_tokens')} Tokens (TPM) | Token Reset in: {results[-1].get('reset_tokens_sec')}")
    print(f"Live Daily Quota     : {results[-1].get('rpd_remaining')} Requests Remaining (RPD)")
    print("=" * 76)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    asyncio.run(run_lifecycle_verification(n))

