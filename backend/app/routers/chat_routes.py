from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    question: str

@router.post("/query")
async def ask_question(request: ChatRequest):
    try:
        # Search the report memory
        answer_context = rag_service.query_report(request.question, request.user_id)
        return {"answer_context": answer_context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))