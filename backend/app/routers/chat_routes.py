from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.database import get_db # 2. ADD THIS
from app.models.report import Report # 3. ADD THIS
from typing import Optional
from sqlalchemy.orm import Session

from app.routers.auth_routes import get_current_user
router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    report_id: Optional[str] = None

@router.post("/query")
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
    ):

    # 1. Fetch the report record from Supabase first
    report = db.query(Report).filter(Report.id == request.report_id).first()
    
    # 2. Pass the DB data to the service for "Numeric Routing"
    report_data = {
        "extracted_values": report.extracted_values if report else []
    }

    result = rag_service.query_report(
        request.question, 
        current_user_id, 
        request.report_id, 
        db_report_data=report_data
    )
    return result

