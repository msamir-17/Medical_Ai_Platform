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
async def ask_question(request: ChatRequest, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)):
    
    # 1. Sabhi reports ka metadata fetch karein comparison ke liye
    if not request.report_id:
        reports = db.query(Report).filter(Report.user_id == current_user_id).all()
        all_info = [r.patient_info for r in reports if r.patient_info]
    else:
        # Single report mode
        report = db.query(Report).filter(Report.id == request.report_id).first()
        all_info = [report.patient_info] if report else []

    # 2. Service ko metadata ke saath call karein
    result = rag_service.query_report(
        question=request.question, 
        user_id=current_user_id, 
        report_id=request.report_id,
        all_patient_info=all_info
    )
    return result