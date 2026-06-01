from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.diabetes_service import diabetes_service


router = APIRouter()

# Data Validation Schema (Industry Standard)
class DiabetesInput(BaseModel):
    Pregnancies: int
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int

@router.post("/diabetes")
async def predict_diabetes(data: DiabetesInput):
    try:
        # Pydantic data ko dict mein badal kar service ko bhej do
        result = diabetes_service.predict_diabetes(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))