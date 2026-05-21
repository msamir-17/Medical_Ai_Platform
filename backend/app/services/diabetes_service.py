import joblib
import os
import numpy as np
import pandas as pd

# 1. Path setting (Industry Standard: Use absolute paths to avoid errors)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "diabetes_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "ml_models", "scaler.pkl")

class DiabetesService:
    def __init__(self):
        # Load the models once when the service starts
        print("Loading ML Models...")
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)

    def predict_diabetes(self, data: dict):
        """
        Takes raw input, scales it, and returns prediction + probability
        """
        # Convert dict to DataFrame for the scaler
        input_df = pd.DataFrame([data])
        
        # 1. Scaling (Wahi scale jo humne training mein use kiya tha)
        # Note: Humein wahi column names chahiye jo training mein thay
        scaled_data = self.scaler.transform(input_df)
        
        # 2. Prediction
        prediction = self.model.predict(scaled_data)[0]
        probability = self.model.predict_proba(scaled_data)[0][1]
        
        return {
            "is_diabetic": bool(prediction),
            "risk_score": round(float(probability) * 100, 2)
        }

# Initialize a singleton instance
diabetes_service = DiabetesService()