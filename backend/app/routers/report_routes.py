
from fastapi import APIRouter, UploadFile, File, HTTPException ,Depends
import shutil
import os
from app.services.ocr_service import ocr_service
from app.services.nlp_service import nlp_service
from app.services.rag_service import rag_service
from sqlalchemy.orm import Session
import uuid
from app.database import get_db
from app.models.report import Report
# from app.services.diabetes_service import DiabetesService 
from app.services.diabetes_service import diabetes_service



router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db) # <--- DB connection mangwaya
   ):

    # 1. Basic Validation
    if not file.filename.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload PDF or Image.")

 # 1. Unique Filename banana (Conflict se bachne ke liye)
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)



    try:
        # 2. Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. AI Pipeline (OCR -> NLP -> RAG)
        raw_text = ocr_service.extract_text(file_path)
        extracted_values = ocr_service.extract_medical_values(raw_text)
        medical_entities = nlp_service.extract_entities(raw_text)

                # 1. REPORT CLASSIFICATION
        report_type = "General"
        if "ph" in extracted_values or "pco2" in extracted_values:
            report_type = "ABG (Arterial Blood Gas)"
        elif "glucose" in extracted_values:
            report_type = "Diabetes Screening"

         # 2. CONDITIONAL RISK (Feature Completeness Check)
        calculated_risk = None
        if "glucose" in extracted_values:
            try:
                # We use predict_service (the instance we exported)
                result = diabetes_service.predict_diabetes({
                    "Pregnancies": 0, "Glucose": float(extracted_values["glucose"]),
                    "BloodPressure": 70, "SkinThickness": 20, "Insulin": 79,
                    "BMI": 25, "DiabetesPedigreeFunction": 0.5, "Age": 30
                })
                calculated_risk = result["risk_score"]
            except:
                calculated_risk = None

        
        # Chatbot memory mein dalna
        rag_service.index_report(raw_text, user_id="123") 

        # 4. DATABASE MEIN SAVE KARNA (The Professional Way)
        new_report = Report(
            id=file_id,
            user_id="123", # Abhi ke liye hardcoded
            filename=file.filename,
            extracted_text=raw_text,
            detected_entities=medical_entities,
            extracted_values=extracted_values,
            risk_score=calculated_risk, # Baad mein ML model se aayega
            report_type=report_type 
        )
        
        db.add(new_report)   # Data ko queue mein dalo
        db.commit()          # Supabase mein "Save" button dabao
        db.refresh(new_report) # Naya data wapas read karo (IDs confirm karne ke liye)

        

        return {
            "id": new_report.id,
            "filename": new_report.filename,
            "message": "Report saved successfully to Supabase!"
        }
    
    except Exception as e:
        db.rollback() # Agar error aaye toh database ko purane state pe le jao
        print(f"❌ Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR Processing failed: {str(e)}")
    
@router.get("/stats")
async def get_report_stats(db: Session = Depends(get_db)):  
    """Provides summary statistics for the dashboard."""
    # For now, we still use '123'. 
    # (In the next session, I'll show you how to use the JWT token to get the REAL user ID).
    user_id = "123"
    
    total_reports = db.query(Report).filter(Report.user_id == user_id).count()
    
    # Get the latest report to show 'Recent Activity'
    latest_report = db.query(Report).filter(Report.user_id == user_id).order_by(Report.created_at.desc()).first()
    
    return {
        "total_reports": total_reports,
        "last_upload": latest_report.created_at if latest_report else None,
        "latest_filename": latest_report.filename if latest_report else "No reports yet"
    }    

@router.get("/") # Ya phr @router.get("/") 
async def get_all_reports(db: Session = Depends(get_db)):
    """Fetches the full list of reports for the gallery."""
    user_id = "123" # Matching your stats logic
    
    # Supabase se saari reports uthao
    reports = db.query(Report).filter(Report.user_id == user_id).all()
    
    return reports

@router.get("/{report_id}")
async def get_report_details(report_id: str, db: Session = Depends(get_db)):

    print(f"🔍 DEBUG: Searching for Report ID: {report_id}")

    """Fetches full details of a specific medical report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return report