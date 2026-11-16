import os
import joblib
from huggingface_hub import hf_hub_download

# Define your Model Registry ID and default pinned revision
MODEL_REPO = "samirk10/medical-ai-models"
MODEL_REVISION = os.getenv("MODEL_REVISION", "main")

def load_model_from_hub(filename: str, revision: str = None):
    """
    Downloads model from HF Hub if not cached, then loads it with joblib.
    Supports pinned revisions/tags/commits for reproducible deployments (MLOPS_PLAN Phase 3).
    Checks local ml_models directory first for fast zero-network loading in CI.
    """
    # 1. Fast local load if file exists in repository
    candidates = [
        os.path.join("ml_models", filename),
        os.path.join("backend", "ml_models", filename),
    ]
    if filename == "scaler_diabetes.pkl":
        candidates.extend([os.path.join("ml_models", "scaler.pkl"), os.path.join("backend", "ml_models", "scaler.pkl")])

    for path in candidates:
        if os.path.exists(path):
            print(f"[Model Loader] Loading local artifact: {path}")
            return joblib.load(path)

    # 2. Download from HF Hub
    token = os.getenv("HF_TOKEN")
    rev = revision or MODEL_REVISION
    
    print(f"[Model Loader] Fetching {filename} from {MODEL_REPO} (revision: {rev})...")
    
    model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=filename,
        token=token, # Required for private repos
        revision=rev
    )
    
    return joblib.load(model_path)