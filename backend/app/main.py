from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import diabetes_routes, report_routes , chat_routes
# 1. Initialize the App
app = FastAPI(
    title="Medical AI Platform API",
    description="Backend for AI-powered medical record analysis",
    version="1.0.0"
)

# 2. Configure CORS (Cross-Origin Resource Sharing)
# This allows your Next.js frontend (port 3000) to talk to this API (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(diabetes_routes.router, prefix="/predict", tags=["Diabetes"])
app.include_router(report_routes.router, prefix="/reports", tags=["Reports"])
app.include_router(chat_routes.router, prefix="/chat", tags=["AI Chatbot"])

# 3. Health Check Endpoint (Industry Standard)
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Medical AI Platform is online"}

# 4. Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical AI Platform API"}