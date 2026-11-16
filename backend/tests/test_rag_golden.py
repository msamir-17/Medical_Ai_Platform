import os
import json
import time
import pytest
from datetime import datetime
from dotenv import load_dotenv

# Load local .env credentials for evaluation
load_dotenv()

# Real LLM Golden Evaluation Suite (MLOPS_PLAN Phase 4)
# Run locally or via manual/weekly workflow .github/workflows/rag-eval.yml

GOLDEN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "rag_golden"))
REPORT_PATH = os.path.join(GOLDEN_DIR, "fake_report.txt")
GOLDEN_PATH = os.path.join(GOLDEN_DIR, "golden.json")
RESULT_PATH = os.path.join(GOLDEN_DIR, "last_eval_result.json")


@pytest.fixture(scope="module")
def setup_rag_golden():
    """
    Initializes RAG service, indexes synthetic fake report, and yields test context.
    Skips if real GROQ_API_KEY is not provided.
    """
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key or "mock" in groq_key or len(groq_key) < 15:
        pytest.skip("Real GROQ_API_KEY is required to run Phase 4 RAG Golden LLM Evaluation.")

    from app.services.rag_service import rag_service, PROMPT_VERSION

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        fake_report_text = f.read()

    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        golden_cases = json.load(f)

    user_id = "test_golden_eval_user"
    report_id = "synth_report_001"

    print(f"\n[Golden Eval Setup] Indexing synthetic report into test namespace ({user_id})...")
    rag_service.index_report(
        text=fake_report_text,
        user_id=user_id,
        report_id=report_id,
        extracted_metadata={"date": "2026-11-15"}
    )

    yield {
        "rag_service": rag_service,
        "prompt_version": PROMPT_VERSION,
        "user_id": user_id,
        "report_id": report_id,
        "golden_cases": golden_cases,
    }

    # Teardown
    print(f"\n[Golden Eval Teardown] Cleaning up test namespace {user_id}...")
    rag_service.invalidate_report_cache(user_id, report_id, is_deleted=True)


def test_rag_golden_suite(setup_rag_golden):
    """
    Executes the golden QA test suite against real RAG reasoning.
    Validates anti-hallucination, strict length bounds, and correct concise answers.
    """
    rag_service = setup_rag_golden["rag_service"]
    prompt_version = setup_rag_golden["prompt_version"]
    user_id = setup_rag_golden["user_id"]
    report_id = setup_rag_golden["report_id"]
    golden_cases = setup_rag_golden["golden_cases"]

    eval_results = []
    passed_count = 0

    print(f"\n=======================================================")
    print(f"  RAG Golden Evaluation Suite - Prompt Version: {prompt_version}")
    print(f"=======================================================")

    for idx, case in enumerate(golden_cases, 1):
        q_id = case.get("id", f"q{idx}")
        question = case["question"]
        print(f"\n[{idx}/{len(golden_cases)}] Question: '{question}'")

        start_time = time.time()
        response_data = rag_service.query_report(
            question=question,
            user_id=user_id,
            mode="single",
            report_ids=[report_id]
        )
        latency = round(time.time() - start_time, 2)

        answer = response_data.get("answer", "") if isinstance(response_data, dict) else str(response_data)
        word_count = len(answer.strip().split())

        print(f"       Answer ({word_count} words): {answer}")

        # Assertions check
        errors = []
        lower_ans = answer.lower()

        # 1. max_words check
        if "max_words" in case and word_count > case["max_words"]:
            errors.append(f"Answer exceeded max_words ({word_count} > {case['max_words']})")

        # 2. min_words check
        if "min_words" in case and word_count < case["min_words"]:
            errors.append(f"Answer fell below min_words ({word_count} < {case['min_words']})")

        # 3. must_contain check
        if "must_contain" in case:
            for token in case["must_contain"]:
                if token.lower() not in lower_ans:
                    errors.append(f"Missing required token '{token}'")

        # 4. must_not_contain check
        if "must_not_contain" in case:
            for forbidden in case["must_not_contain"]:
                if forbidden.lower() in lower_ans:
                    errors.append(f"Found forbidden token '{forbidden}' (unsolicited content/hallucination)")

        # 5. must_contain_any check
        if "must_contain_any" in case:
            matched = any(token.lower() in lower_ans for token in case["must_contain_any"])
            if not matched:
                errors.append(f"None of required tokens found from {case['must_contain_any']}")

        is_passed = len(errors) == 0
        if is_passed:
            passed_count += 1
            print(f"       Status: PASS (in {latency}s)")
        else:
            print(f"       Status: FAIL -> {'; '.join(errors)}")

        eval_results.append({
            "id": q_id,
            "question": question,
            "answer": answer,
            "word_count": word_count,
            "passed": is_passed,
            "errors": errors,
            "latency_seconds": latency,
        })

        # Rate-limit guard: 2.5s sleep between calls to respect Groq free tier (30 RPM)
        if idx < len(golden_cases):
            time.sleep(2.5)

    pass_rate = round((passed_count / len(golden_cases)) * 100, 1)
    print(f"\n-------------------------------------------------------")
    print(f"  Summary: {passed_count}/{len(golden_cases)} Passed ({pass_rate}%)")
    print(f"-------------------------------------------------------")

    # Save artifact for tracking across prompt revisions
    artifact = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "prompt_version": prompt_version,
        "total_cases": len(golden_cases),
        "passed_cases": passed_count,
        "pass_rate_percentage": pass_rate,
        "results": eval_results,
    }
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    print(f"[Golden Eval] Evaluation report saved to: {RESULT_PATH}")

    # CI assertion: At least 80% of golden queries must pass
    assert pass_rate >= 80.0, f"RAG Golden Evaluation pass rate ({pass_rate}%) is below 80% threshold!"

