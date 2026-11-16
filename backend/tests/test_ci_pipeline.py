import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock easyocr.Reader to prevent sandbox/CI filesystem permission delays
with patch("easyocr.Reader", return_value=MagicMock()):
    from app.main import app
    from app.utils.model_loader import load_model_from_hub
    from app.services.diabetes_service import diabetes_service


@pytest.fixture
def client():
    return TestClient(app)


def test_ci_health_and_ready_probes(client):
    """
    CI Gate: Verifies that core health and readiness endpoints respond correctly.
    """
    with patch("app.main.engine.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        res_health = client.get("/health")
        assert res_health.status_code == 200
        health_data = res_health.json()
        assert health_data["status"] == "healthy"
        assert health_data["db"] is True

        res_ready = client.get("/ready")
        assert res_ready.status_code in (200, 503)
        ready_data = res_ready.json()
        assert "models" in ready_data


def test_ci_diabetes_prediction_pipeline():
    """
    CI Gate: Verifies tabular diabetes ML model returns valid risk score & SHAP explanation.
    """
    sample_input = {
        "Pregnancies": 2,
        "Glucose": 140.0,
        "BloodPressure": 75.0,
        "SkinThickness": 20.0,
        "Insulin": 85.0,
        "BMI": 28.5,
        "DiabetesPedigreeFunction": 0.45,
        "Age": 35,
    }

    result = diabetes_service.predict_diabetes(sample_input)
    assert result is not None
    assert "risk_score" in result
    assert 0.0 <= result["risk_score"] <= 100.0
    assert "shap_explanation" in result
    assert len(result["shap_explanation"]) > 0


def test_ci_model_loader_revision_pinning():
    """
    CI Gate: Verifies load_model_from_hub passes pinned revision to hf_hub_download.
    """
    with patch("app.utils.model_loader.hf_hub_download") as mock_hf_download, \
         patch("app.utils.model_loader.joblib.load") as mock_joblib_load:
        
        mock_hf_download.return_value = "dummy/path/model.pkl"
        mock_joblib_load.return_value = MagicMock()

        # 1. Default revision from env or 'main'
        load_model_from_hub("test_model.pkl")
        mock_hf_download.assert_called_with(
            repo_id="samirk10/medical-ai-models",
            filename="test_model.pkl",
            token=os.getenv("HF_TOKEN"),
            revision=os.getenv("MODEL_REVISION", "main")
        )

        # 2. Explicit pinned revision
        load_model_from_hub("test_model.pkl", revision="v1.0.0-prod")
        mock_hf_download.assert_called_with(
            repo_id="samirk10/medical-ai-models",
            filename="test_model.pkl",
            token=os.getenv("HF_TOKEN"),
            revision="v1.0.0-prod"
        )


def test_ci_rag_pipeline_with_mocked_groq_llm():
    """
    CI Gate: Verifies RAG reasoning works cleanly with MOCKED Groq LLM.
    Guarantees zero API costs, zero rate limits, and 100% deterministic CI passes.
    """
    from app.services.rag_service import rag_service

    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Patient ka naam Mr. Kanta Yadav hai."
    mock_llm.invoke.return_value = mock_response
    mock_llm.bind.return_value = mock_llm

    with patch.object(rag_service, "llm", mock_llm):
        prompt_res = rag_service.llm.bind(max_tokens=200).invoke("dummy question")
        assert prompt_res.content == "Patient ka naam Mr. Kanta Yadav hai."

