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
        result = rag_service.query_report(request.question, request.user_id)
        
        # Safe check: In industry, we always check the type of our result
        if not isinstance(result, dict):
             return {"answer": str(result), "evidence": "Raw format detected"}
        
        return {
            "answer": result.get("answer", "No response"),
            "evidence": result.get("sources", "")
        }
    except Exception as e:
        print(f"❌ Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")