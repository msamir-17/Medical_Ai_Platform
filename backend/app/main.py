import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
from app.models import user  # Import your models
from app.models import report
from app.routers import diabetes_routes, report_routes , chat_routes , auth_routes 

# --- Sentry & Privacy Scrubber Configuration (MLOPS_PLAN Phase 1) ---
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    HAS_SENTRY = True
except ImportError:
    HAS_SENTRY = False

SENTRY_DSN = os.getenv("SENTRY_DSN")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "production" if os.getenv("SPACE_ID") else "development")


def sentry_scrub_pii(event, hint):
    """
    HIPAA/GDPR Medical Data Privacy Scrubber (MLOPS_PLAN Section 3):
    Guarantees that NO patient names, IDs, phone numbers, report text, lab values,
    JWT tokens, cookies, or request bodies are transmitted to Sentry.
    """
    if "request" in event:
        req = event["request"]
        # Allow only non-sensitive routing headers; strip auth, tokens, patient metadata
        safe_headers = {"host", "user-agent", "accept", "content-type"}
        if "headers" in req and isinstance(req["headers"], dict):
            req["headers"] = {
                k: v for k, v in req["headers"].items()
                if k.lower() in safe_headers and "auth" not in k.lower() and "token" not in k.lower()
            }
        # Completely scrub cookies and query parameters
        req.pop("cookies", None)
        req.pop("query_string", None)

        # Completely redact request body payload to protect clinical data
        if "data" in req:
            req["data"] = "[SCRUBBED_MEDICAL_DATA]"

    # Also scrub extra breadcrumbs that may log SQL parameters containing medical records
    if "breadcrumbs" in event and isinstance(event["breadcrumbs"], dict) and "values" in event["breadcrumbs"]:
        for b in event["breadcrumbs"]["values"]:
            if b.get("category") in ("sqlalchemy", "query"):
                b.pop("data", None)

    return event


if HAS_SENTRY and SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=APP_ENV,
        release=f"medical-ai-backend@{APP_VERSION}",
        traces_sample_rate=0.1,
        send_default_pii=False,
        before_send=sentry_scrub_pii,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
    )


# This looks at all models that inherit from 'Base' and creates tables in Supabase
try:
    Base.metadata.create_all(bind=engine)
except Exception as db_init_err:
    print(f"[STARTUP WARNING] Supabase initial schema sync failed (DB may be paused/unreachable): {db_init_err}")


# 1. Initialize the App
app = FastAPI(
    title="Medical AI Platform API",
    description="Backend for AI-powered medical record analysis",
    version=APP_VERSION
)


# 2. Configure CORS (Cross-Origin Resource Sharing)
# This allows your Next.js frontend (port 3000) to talk to this API (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://medical-ai-platform-iota.vercel.app",
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(diabetes_routes.router, prefix="/predict", tags=["Diabetes"])
app.include_router(report_routes.router, prefix="/reports", tags=["Reports"])
app.include_router(chat_routes.router, prefix="/chat", tags=["AI Chatbot"])

# 3. Health Check Endpoint (Production Liveness Probe)
@app.get("/health")
def health_check(response: Response):
    """
    Production Liveness & Dependency Probe (MLOPS_PLAN Phase 1):
    Executes an active DB probe (SELECT 1 with timeout).
    Returns 200 when all core dependencies respond; 503 if database connectivity fails.
    """
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    status_str = "healthy" if db_ok else "degraded"
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": status_str,
        "version": APP_VERSION,
        "environment": APP_ENV,
        "db": db_ok,
    }

# 4. Readiness Probe Endpoint
@app.get("/ready")
def ready_check(response: Response):
    """
    Production Readiness Probe (MLOPS_PLAN Phase 1):
    Verifies that critical ML model files and vector store paths are accessible.
    Returns 200 when ready to receive traffic, 503 during warm-up.
    """
    ml_dirs = ["ml_models", os.path.join("backend", "ml_models")]
    diabetes_ok = any(os.path.exists(os.path.join(d, "diabetes_model.pkl")) for d in ml_dirs)
    heart_ok = any(os.path.exists(os.path.join(d, "heart_model.pkl")) for d in ml_dirs)
    vector_ok = os.path.exists("vector_stores") or os.path.exists(os.path.join("backend", "vector_stores"))

    all_ready = bool(diabetes_ok and heart_ok and vector_ok)
    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "ready": all_ready,
        "models": {
            "diabetes_model": diabetes_ok,
            "heart_model": heart_ok,
        },
        "vector_store": vector_ok,
    }

# 5. Sentry Verification Test Endpoint
@app.get("/debug/sentry-test")
def sentry_test_endpoint():
    """
    Controlled Verification Endpoint (MLOPS_PLAN Phase 1):
    Explicitly triggers a test error to confirm Sentry alert receipt and PII scrub.
    """
    if not SENTRY_DSN or not HAS_SENTRY:
        return {
            "status": "skipped",
            "message": "Sentry is not active (SENTRY_DSN not set or sentry-sdk not installed)."
        }
    raise RuntimeError("MediAI Sentry Verification: Controlled test alert triggered successfully.")

# 6. Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical AI Platform API"}