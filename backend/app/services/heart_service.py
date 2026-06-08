import joblib
import os
import pandas as pd
import shap
from app.utils.model_loader import load_model_from_hub
# Paths following ARCHITECTURE.md


class HeartService:
    def __init__(self):
        print("Loading ML Models & SHAP Explainer...")
        self.model = load_model_from_hub("heart_model.pkl")
        self.scaler = load_model_from_hub("scaler_heart.pkl")
        self.explainer = shap.TreeExplainer(self.model)

    def predict_heart_risk(self, data: dict):
        """
        Takes raw cardiac markers and returns probability + SHAP impact.
        Cleveland Features: Age, Sex, CP, Trestbps, Chol, Fbs, Restecg, Thalach, Exang, Oldpeak, Slope, Ca, Thal
        """
        df = pd.DataFrame([data])
        scaled_data = self.scaler.transform(df)
        
        # 1. Risk Score
        prob = self.model.predict_proba(scaled_data)[0][1]
        risk_score = round(float(prob) * 100, 2)

        # 2. SHAP (The 'Why')
        shap_values = self.explainer.shap_values(scaled_data)
        contributions = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]

        explanation = []
        for i, feat in enumerate(df.columns):
            explanation.append({
                "feature": feat,
                "contribution": round(float(contributions[i]) * 100, 2)
            })

        return {
            "risk_score": risk_score,
            "shap_explanation": explanation
        }

# Singleton Instance
heart_service = HeartService()