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
        # Get the dictionary from the service
        result = rag_service.query_report(request.question, request.user_id)
        
        # Now this will not crash!
        return {
            "answer": result.get("answer", "No answer generated"),
            "evidence": result.get("sources", "No evidence found")
        }
    except Exception as e:
        # Debugging ke liye terminal mein error print karein
        print(f"❌ Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))