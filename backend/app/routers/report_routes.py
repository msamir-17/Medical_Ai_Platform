
from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from app.services.ocr_service import ocr_service
from app.services.nlp_service import nlp_service
from app.services.rag_service import rag_service

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_report(file: UploadFile = File(...)):
    # 1. Basic Validation
    if not file.filename.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload PDF or Image.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        # 2. Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Process with OCR (The Reader)
        raw_text = ocr_service.extract_text(file_path)
        

        print(f"\n🔍 DEBUG: AI saw this text in the file: {raw_text}\n")


        # 4. Process with Regex (The Strict Detective)
        structured_data = ocr_service.extract_medical_values(raw_text)

        # 5. Process with NLP (The Smart Doctor) - NEW STEP
        medical_entities = nlp_service.extract_entities(raw_text)

        # 5. Process with NLP
        medical_entities = nlp_service.extract_entities(raw_text)

        # 6. Index for Chatbot (Memory) - NEW STEP
        # For now, we use a dummy user_id "123"
        rag_service.index_report(raw_text, user_id="123") 

        return {
            "filename": file.filename,
            "extracted_values": structured_data,
            "detected_entities": medical_entities, # NEW DATA
            "message": "Report analyzed and added to chatbot memory!"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Processing failed: {str(e)}")
    

    