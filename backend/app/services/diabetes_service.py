import joblib
import os   
import numpy as np
import pandas as pd
import shap


from app.utils.model_loader import load_model_from_hub
# 1. Path setting
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "diabetes_model.pkl")
# SCALER_PATH = os.path.join(BASE_DIR, "ml_models", "scaler.pkl")

class DiabetesService:
    def __init__(self):
        print("Loading ML Models & SHAP Explainer...")
        self.model = load_model_from_hub("diabetes_model.pkl")
        self.scaler = load_model_from_hub("scaler_diabetes.pkl")
        self.explainer = shap.TreeExplainer(self.model)

    def _prepare_features(self, data: dict):
        """
        Recreates the 13 features (8 numeric + 5 dummies) used during training.
        """
        # 1. Start with the basic 8 numeric features
        # IMPORTANT: Use the exact names and order from training
        df = pd.DataFrame([data])
        
        # 2. Scale the numeric parts (Scaler expects 8 columns based on your training)
        scaled_numeric = self.scaler.transform(df)
        scaled_df = pd.DataFrame(scaled_numeric, columns=df.columns)

        # 3. Manually create the One-Hot Encoded columns (The missing 5 features)
        bmi = data.get('BMI', 0)
        age = data.get('Age', 0)

        # BMI Categories (Logic from your Phase 3)
        scaled_df['BMI_Cat_Normal'] = 1 if 18.5 <= bmi <= 24.9 else 0
        scaled_df['BMI_Cat_Overweight'] = 1 if 25.0 <= bmi <= 29.9 else 0
        scaled_df['BMI_Cat_Obese'] = 1 if bmi >= 30.0 else 0
        
        # Age Groups (Logic from your Phase 3)
        scaled_df['Age_Group_Middle'] = 1 if 31 <= age <= 50 else 0
        scaled_df['Age_Group_Senior'] = 1 if age > 50 else 0

        # Ensure the final column order matches the training data exactly
        final_columns = [
            'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 
            'BMI', 'DiabetesPedigreeFunction', 'Age', 
            'BMI_Cat_Normal', 'BMI_Cat_Overweight', 'BMI_Cat_Obese', 
            'Age_Group_Middle', 'Age_Group_Senior'
        ]
        
        return scaled_df[final_columns]

    def predict_diabetes(self, data: dict):
        try:
            # Step 1: Expand 8 features to 13 and Scale them
            final_input = self._prepare_features(data)
            
            # Step 2: Prediction
            prob = self.model.predict_proba(final_input)[0][1]
            risk_score = round(float(prob) * 100, 2)

            # Step 3: SHAP Calculation (The "Why")
            shap_values = self.explainer.shap_values(final_input)
            
            if isinstance(shap_values, list):
                contributions = shap_values[1][0]
            else:
                contributions = shap_values[0, :, 1] if len(shap_values.shape) == 3 else shap_values[0]

            # Step 4: Structure for Frontend
            explanation = []
            features = final_input.columns.tolist()
            for i, feat in enumerate(features):
                explanation.append({
                    "feature": feat,
                    "contribution": round(float(contributions[i]) * 100, 2)
                })

            return {
                "risk_score": risk_score,
                "shap_explanation": explanation
            }
        except Exception as e:
            print(f"Prediction logic error: {e}")
            raise e

# Initialize singleton
diabetes_service = DiabetesService()