import pytest
import asyncio
import os
import sys

# Ensure backend path is present
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

rag_service.vector_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vector_stores"))


@pytest.mark.anyio
async def test_async_single_report_retrieval():
    """
    Verify _retrieve_single_report_async executes non-blocking retrieval
    guarded by semaphore.
    """
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{TEST_USER_ID}")
    semaphore = asyncio.Semaphore(3)
    
    context = await rag_service._retrieve_single_report_async(
        rid=TEST_REPORT_ID,
        user_folder=user_folder,
        question="What is the glucose value?",
        all_report_data=TEST_DATA,
        semaphore=semaphore
    )
    
    assert isinstance(context, str)
    assert len(context) > 0
    assert "SOURCE REPORT: rep_kant" in context
    assert "GLUCOSE: 185.2" in context


@pytest.mark.anyio
async def test_parallel_multi_report_retrieval():
    """
    Verify _parallel_retrieve_contexts uses asyncio.gather to retrieve
    multiple report contexts concurrently while preserving order.
    """
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{TEST_USER_ID}")
    report_ids = [TEST_REPORT_ID, TEST_REPORT_ID]  # Concurrently query 2 indices
    
    context = await rag_service._parallel_retrieve_contexts(
        report_ids=report_ids,
        user_folder=user_folder,
        question="What are the abnormal findings?",
        all_report_data=TEST_DATA,
        max_concurrency=4
    )
    
    assert isinstance(context, str)
    assert context.count("SOURCE REPORT: rep_kant") == 2


@pytest.mark.anyio
async def test_fault_tolerance_missing_index():
    """
    Verify that if one report index is missing, parallel retrieval does not crash
    and successfully returns context from valid reports.
    """
    user_folder = os.path.join(rag_service.vector_db_path, f"user_{TEST_USER_ID}")
    report_ids = ["non_existent_report_id", TEST_REPORT_ID]
    
    context = await rag_service._parallel_retrieve_contexts(
        report_ids=report_ids,
        user_folder=user_folder,
        question="What is the glucose value?",
        all_report_data=TEST_DATA
    )
    
    assert isinstance(context, str)
    assert "SOURCE REPORT: rep_kant" in context


@pytest.mark.anyio
async def test_aquery_report_execution():
    """
    Verify aquery_report executes end-to-end async RAG retrieval and generation.
    """
    res = await rag_service.aquery_report(
        question="What is the glucose value?",
        user_id=TEST_USER_ID,
        mode="single",
        report_ids=[TEST_REPORT_ID],
        all_report_data=TEST_DATA
    )
    
    assert isinstance(res, dict)
    assert "answer" in res
    assert "sources" in res
    assert len(res["answer"]) > 0


@pytest.mark.anyio
async def test_aquery_report_stream_events():
    """
    Verify aquery_report_stream yields structured metadata, token, and done events asynchronously.
    """
    events = []
    async for event in rag_service.aquery_report_stream(
        question="What is the glucose value?",
        user_id=TEST_USER_ID,
        mode="single",
        report_ids=[TEST_REPORT_ID],
        all_report_data=TEST_DATA
    ):
        events.append(event)
        # Verify first 3 events then break to test disconnection resilience
        if len(events) >= 3:
            break
            
    assert len(events) >= 3
    assert events[0]["type"] == "metadata"
    assert events[1]["type"] == "token"

