
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
from app.services.diabetes_service import diabetes_service
from app.routers.auth_routes import get_current_user
from app.services.heart_service import heart_service




router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db), 
    current_user_id: str = Depends(get_current_user)
   ):

    # 1. Basic Validation
    if not file.filename.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload PDF or Image.")

 # 1. Unique Filename banana (Conflict se bachne ke liye)
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # 2. Save file locally
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    final_risk_score = None
    final_shap_values = []
    report_type = "General"
    patient_metadata = {"name": "Unknown", "age": "N/A"}

    try:

        # 3. AI Pipeline (OCR -> NLP -> RAG)
        raw_text = ocr_service.extract_text(file_path)
        extracted_values = ocr_service.extract_medical_values(raw_text)

        print("\n🧪 DEBUG: Extracted Values from OCR:")
        for k, v in extracted_values.items():
            print(f"   {k} -> {v}")
        print("-" * 30)

        medical_entities = nlp_service.extract_entities(raw_text)

        # 2. METADATA & INTERPRETATION (The Smart Logic)
        patient_metadata = rag_service.extract_patient_metadata(raw_text)
        # Pass the DICTIONARY of numbers, not the raw text!
        interpreted_list = ocr_service.interpret_markers(extracted_values)

        # 1. REPORT CLASSIFICATION
        report_type = "General"
        # 3. CLASSIFICATION
        if "ph" in extracted_values:
            report_type = "ABG (Arterial Blood Gas)"
        elif "glucose" in extracted_values:
            report_type = "Diabetes Screening"
        elif "cholesterol" in extracted_values:
            report_type = "Lipid Profile (Cardiac)"
        elif "haemoglobin" in extracted_values or "wbc" in extracted_values:
            report_type = "Complete Blood Count (CBC)"
        

        if "glucose" in extracted_values and report_type == "Diabetes Profile":
            print(f"🔍 DEBUG: Glucose found ({extracted_values['glucose']}). Starting prediction...")
            try:
                # IMPORTANT: 'diabetes_service' (Small 'd') use karna hai, jo instance hai
                result = diabetes_service.predict_diabetes({
                    "Pregnancies": 0, 
                    "Glucose": float(extracted_values["glucose"]),
                    "BloodPressure": 70, 
                    "SkinThickness": 20, 
                    "Insulin": 79,
                    "BMI": 25, 
                    "DiabetesPedigreeFunction": 0.5, 
                    "Age": 30
                })
                final_risk_score = result["risk_score"]
                final_shap_values = result["shap_explanation"]
                # print(f"✅ DEBUG: Prediction Success! Score: {final_risk_score}")

            except Exception as e:
                # Yeh line aapko terminal mein batayegi ki asli problem kya hai
                print(f"❌ DEBUG: Prediction Failed! Error: {str(e)}")
                # final_risk_score = None

        elif "cholesterol" in extracted_values and report_type == "Lipid Profile":
            report_type = "Lipid Profile (Cardiac)"           
            try:
                # We fill missing values with averages for the Cleveland model
                heart_input = {
                    "age": float(patient_metadata.get("age", 45) if str(patient_metadata.get("age")).isdigit() else 45),
                    "sex": 1 if patient_metadata.get("gender") == "Male" else 0,
                    "cp": 1, "trestbps": 120, "chol": float(extracted_values["cholesterol"]),
                    "fbs": 0, "restecg": 0, "thalach": 150, "exang": 0,
                    "oldpeak": 1.0, "slope": 1, "ca": 0, "thal": 2
                }
                res = heart_service.predict_heart_risk(heart_input)
                final_risk_score = res["risk_score"]
                final_shap_values = res["shap_explanation"]
            except Exception as e: print(f"Cardiac Prediction Error: {e}")

        else:
            print("⚠️ DEBUG: No 'glucose' key found in extracted_values. Skipping prediction.") 

        patient_metadata = rag_service.extract_patient_metadata(raw_text)

        # Right before rag_service.index_report:
        print(f"📁 UPLOAD DEBUG: Saving report to folder of user: {current_user_id}")
        # Chatbot memory mein dalna
        rag_service.index_report(raw_text, user_id=current_user_id,report_id=file_id) 

        # 4. DATABASE MEIN SAVE KARNA (The Professional Way)
        new_report = Report(
            id=file_id,
            user_id=current_user_id, # Abhi ke liye hardcoded
            filename=file.filename,
            extracted_text=raw_text,
            detected_entities=medical_entities,
            extracted_values=interpreted_list,
            risk_score=final_risk_score, # Baad mein ML model se aayega
            patient_info=patient_metadata,
            shap_values=final_shap_values,
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
async def get_report_stats(db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)):  
    """Provides summary statistics for the dashboard."""
    # For now, we still use '123'. 
    # (In the next session, I'll show you how to use the JWT token to get the REAL user ID).
    user_id = current_user_id
    
    total_reports = db.query(Report).filter(Report.user_id == user_id).count()
    
    # Get the latest report to show 'Recent Activity'
    latest_report = db.query(Report).filter(Report.user_id == user_id).order_by(Report.created_at.desc()).first()
    
    return {
        "total_reports": total_reports,
        "last_upload": latest_report.created_at if latest_report else None,
        "latest_filename": latest_report.filename if latest_report else "No reports yet"
    }    

@router.get("/") # Ya phr @router.get("/") 
async def get_all_reports(db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)):
    """Fetches the full list of reports for the gallery."""
    user_id = current_user_id # Matching your stats logic
    
    # Supabase se saari reports uthao
    reports = db.query(Report).filter(Report.user_id == user_id).all()
    
    return reports

@router.get("/{report_id}")
async def get_report_details(report_id: str, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)):

    print(f"🔍 DEBUG: Searching for Report ID: {report_id}")

    """Fetches full details of a specific medical report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: str, 
    db: Session = Depends(get_db), 
    current_user_id: str = Depends(get_current_user)
):
    """Securely deletes a report only if it belongs to the current user."""
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or unauthorized")

    try:
        db.delete(report)
        db.commit()
        return {"message": "Report deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
    
