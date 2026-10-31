import pytest
import json
import os
import sys

# Ensure backend path is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.rag_service import rag_service

TEST_USER_ID = "test_user"
TEST_REPORT_ID = "rep_kanta"
TEST_DATA = [{
    "id": "rep_kanta",
    "patient_info": {"name": "MR. KANTA YADAV", "age": "74", "gender": "Male"},
    "extracted_values": [
        {"marker": "GLUCOSE", "value": "185.2", "unit": "mg/dL", "status": "HIGH", "ref_range": "70-100"}
    ],
    "report_type": "Blood Test",
    "date": "2026-03-23"
}]

# Point to backend vector_stores if run from repository root
rag_service.vector_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vector_stores"))


def test_regression_existing_query_report():
    """
    REGRESSION TEST: Verify existing query_report method works 100% intact
    and returns expected dictionary with 'answer' and 'sources'.
    """
    result = rag_service.query_report(
        question="What is the glucose value?",
        user_id=TEST_USER_ID,
        mode="single",
        report_ids=[TEST_REPORT_ID],
        all_report_data=TEST_DATA
    )
    assert isinstance(result, dict)
    assert "answer" in result
    assert "sources" in result
    assert len(result["answer"]) > 0
    assert "Analyzed 1 active documents" in result["sources"]


def test_streaming_generator_events_and_sources():
    """
    STREAMING TEST: Verify query_report_stream yields:
    1. Initial 'metadata' event with sources and context length
    2. 'token' chunks
    3. Final 'done' event with sources attribution
    """
    generator = rag_service.query_report_stream(
        question="What is the glucose value?",
        user_id=TEST_USER_ID,
        mode="single",
        report_ids=[TEST_REPORT_ID],
        all_report_data=TEST_DATA
    )

    events = []
    tokens = []
    for item in generator:
        events.append(item)
        if item.get("type") == "token":
            tokens.append(item.get("content", ""))

    assert len(events) >= 3, "Stream must emit metadata, token, and done events"
    
    # 1. First event must be metadata containing sources
    metadata_event = events[0]
    assert metadata_event["type"] == "metadata"
    assert "sources" in metadata_event
    assert "Analyzed 1 active documents" in metadata_event["sources"]
    assert metadata_event.get("context_length", 0) > 0

    # 2. Token chunks must be present and assemble the clinical response
    assert len(tokens) > 0
    full_text = "".join(tokens)
    assert len(full_text) > 0

    # 3. Final event must be 'done' with sources
    last_event = events[-1]
    assert last_event["type"] == "done"
    assert "sources" in last_event


def test_streaming_client_disconnection_handling():
    """
    DISCONNECTION TEST: Verify generator can be terminated prematurely
    without hanging or leaking underlying resources (simulating client abort).
    """
    generator = rag_service.query_report_stream(
        question="Summarize the full report findings",
        user_id=TEST_USER_ID,
        mode="single",
        report_ids=[TEST_REPORT_ID],
        all_report_data=TEST_DATA
    )

    received_chunks = 0
    for chunk in generator:
        received_chunks += 1
        # Client disconnects after receiving first 2 chunks
        if received_chunks >= 2:
            generator.close()
            break

    assert received_chunks == 2
    # Verify generator is closed
    with pytest.raises(StopIteration):
        next(generator)


def test_streaming_safety_gate_mismatch():
    """
    SAFETY GATE TEST: Compare mode with mismatched identities must emit safety block.
    """
    mismatched_data = [
        {"patient_info": {"name": "KANTA YADAV"}},
        {"patient_info": {"name": "BASHIR SHAIKH"}}
    ]
    generator = rag_service.query_report_stream(
        question="Compare patient trends",
        user_id=TEST_USER_ID,
        mode="compare",
        report_ids=["rep1", "rep2"],
        all_report_data=mismatched_data
    )

    events = list(generator)
    assert any("Safety Block" in e.get("content", "") for e in events)
    assert any(e.get("sources") == "Safety Engine" for e in events)

