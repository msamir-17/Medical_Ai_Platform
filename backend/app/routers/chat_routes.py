from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.database import get_db # 2. ADD THIS
from app.models.report import Report # 3. ADD THIS
from typing import Optional ,List
from sqlalchemy.orm import Session
from app.services.classifier_service import classifier

from app.routers.auth_routes import get_current_user
router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    mode: str = "single"
    report_id: Optional[str] = None
    report_ids: Optional[List[str]] = [] # Ab hum list bhejenge


@router.post("/query")
async def ask_question(
    request: ChatRequest, 
    db: Session = Depends(get_db), 
    current_user_id: str = Depends(get_current_user)
):
    # 1. DATABASE IS THE SOURCE OF TRUTH
    # Agar user ne 'All Reports' (overview/compare) चुना है, तो DB से सारी active IDs निकालो
    if request.mode in ["overview", "compare"] and (not request.report_ids):
        active_reports = db.query(Report).filter(Report.user_id == current_user_id).all()
        target_ids = [r.id for r in active_reports]
    else:
        # Single report ya specific selected reports
        target_ids = request.report_ids if request.report_ids else [request.report_id]
        active_reports = db.query(Report).filter(Report.id.in_(target_ids), Report.user_id == current_user_id).all()

    # 2. Pack data for the service (No more guessing)
    all_report_data = [{
        "id": r.id,
        "patient_info": r.patient_info,
        "extracted_values": r.extracted_values,
        "report_type": r.report_type,
        "date": r.created_at
    } for r in active_reports]

    # 3. Call Service
    result = rag_service.query_report(
        question=request.question,
        user_id=current_user_id,
        mode=request.mode,
        report_ids=target_ids, # Sirf wahi IDs jo DB mein hain
        all_report_data=all_report_data
    )
    return result

@router.post("/stream")
async def ask_question_stream(
    chat_request: ChatRequest, 
    raw_request: Request,
    db: Session = Depends(get_db), 
    current_user_id: str = Depends(get_current_user)
):
    # 1. DATABASE IS THE SOURCE OF TRUTH
    if chat_request.mode in ["overview", "compare"] and (not chat_request.report_ids):
        active_reports = db.query(Report).filter(Report.user_id == current_user_id).all()
        target_ids = [r.id for r in active_reports]
    else:
        target_ids = chat_request.report_ids if chat_request.report_ids else [chat_request.report_id]
        active_reports = db.query(Report).filter(Report.id.in_(target_ids), Report.user_id == current_user_id).all()

    all_report_data = [{
        "id": r.id,
        "patient_info": r.patient_info,
        "extracted_values": r.extracted_values,
        "report_type": r.report_type,
        "date": r.created_at
    } for r in active_reports]

    # 2. SSE Generator with Disconnection Safety
    async def sse_event_generator():
        try:
            stream_gen = rag_service.query_report_stream(
                question=chat_request.question,
                user_id=current_user_id,
                mode=chat_request.mode,
                report_ids=target_ids,
                all_report_data=all_report_data
            )
            for chunk in stream_gen:
                if await raw_request.is_disconnected():
                    print(f"[STREAM DISCONNECT] Client disconnected for user {current_user_id}.")
                    break
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as exc:
            err_event = {"type": "error", "message": f"Streaming pipeline error: {str(exc)}"}
            yield f"data: {json.dumps(err_event)}\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
