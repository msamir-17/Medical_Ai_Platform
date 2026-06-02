import joblib
import os
import pandas as pd
import shap

# Paths following ARCHITECTURE.md
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Note: Ensure you have these files in your ml_models folder from your training phase
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "heart_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "ml_models", "scaler_heart.pkl")

class HeartService:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            print("Loading Heart Risk Models...")
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            self.explainer = shap.TreeExplainer(self.model)
        else:
            print("⚠️ Heart model files not found. Cardiac prediction disabled.")

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