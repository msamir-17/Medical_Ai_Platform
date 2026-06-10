from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.database import get_db # 2. ADD THIS
from app.models.report import Report # 3. ADD THIS
from typing import Optional ,List
from sqlalchemy.orm import Session

from app.routers.auth_routes import get_current_user
router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    mode: str = "single"
    report_id: Optional[str] = None
    report_ids: Optional[List[str]] = [] # Ab hum list bhejenge



@router.post("/query")
async def ask_question(request: ChatRequest, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)):
    
# 1. Decide which reports to fetch metadata for
    target_ids = request.report_ids if request.report_ids else [request.report_id]
    
    # 2. Supabase se un reports ki info nikalo
    reports = db.query(Report).filter(Report.id.in_(target_ids), Report.user_id == current_user_id).all()
    all_info = [r.patient_info for r in reports if r.patient_info]

    # 3. Call the service with the new parameters
    result = rag_service.query_report(
        question=request.question,
        user_id=current_user_id,
        mode=request.mode, # <--- Passing the mode!
        report_ids=target_ids,
        all_patient_info=all_info
    )
    return result