import os
import joblib
from huggingface_hub import hf_hub_download

# Define your Model Registry ID
MODEL_REPO = "samirk10/medical-ai-models"

def load_model_from_hub(filename: str):
    """
    Downloads model from HF Hub if not cached, then loads it with joblib.
    """
    token = os.getenv("HF_TOKEN")
    
    print(f"📦 Fetching {filename} from {MODEL_REPO}...")
    
    model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=filename,
        token=token # Required for private repos
    )
    
    return joblib.load(model_path)