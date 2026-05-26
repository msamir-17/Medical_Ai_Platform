# TASKS.md
# Development Phases & Task Checklist — AI Medical Record Intelligence Platform

> Use this as your sprint board. Check off items as you complete them.
> Each phase must be fully complete before moving to the next.

---

## Phase 0 — Project Setup (Day 1–2)

### Repository
- [ ] Create GitHub repo: `medical-ai-platform`
- [ ] Add `.gitignore` (Python + Node + secrets)
- [ ] Add `.env.example` with all required keys
- [ ] Create `README.md` with setup instructions
- [ ] Create the full folder structure from ARCHITECTURE.md

### Backend Bootstrap
- [ ] `python -m venv venv` + `pip install fastapi uvicorn sqlalchemy pydantic-settings psycopg2-binary alembic python-jose bcrypt python-multipart`
- [ ] `app/main.py` with CORS + health endpoint
- [ ] `app/config.py` with pydantic-settings
- [ ] `app/database.py` with SQLAlchemy session
- [ ] Alembic initialized: `alembic init alembic`
- [ ] Test: `uvicorn app.main:app --reload` returns `{"status":"ok"}`

### Frontend Bootstrap
- [ ] `npx create-next-app@latest frontend --typescript --tailwind --app`
- [ ] `npm install axios @tanstack/react-query react-dropzone next-auth zustand react-hook-form`
- [ ] `npx shadcn-ui@latest init`
- [ ] CSS custom properties added to `globals.css` from UI_GUIDELINES.md
- [ ] Axios instance created in `lib/api.ts` with interceptors
- [ ] Test: `npm run dev` runs without errors

### Docker Bootstrap
- [ ] `backend/Dockerfile`
- [ ] `frontend/Dockerfile`
- [ ] `docker-compose.yml` with all 3 services (frontend, backend, postgres)
- [ ] Test: `docker-compose up --build` — all services healthy

---

## Phase 1 — Authentication (Day 3–4)

### Backend
- [ ] `models/user.py` — SQLAlchemy User model
- [ ] `schemas/auth.py` — UserCreate, UserResponse, TokenResponse
- [ ] `repositories/user_repository.py` — get_by_email, create, get_by_id
- [ ] `services/auth_service.py` — hash_password, verify_password, create_token, decode_token
- [ ] `routers/auth.py` — POST /auth/register, POST /auth/login, GET /auth/me
- [ ] `middleware/auth_middleware.py` — get_current_user dependency
- [ ] Alembic migration: create users table
- [ ] Tests: `test_auth.py` — register, login, invalid credentials, expired token

### Frontend
- [ ] `types/index.ts` — User, AuthTokens interfaces
- [ ] `features/auth/authService.ts` — register(), login(), getMe()
- [ ] `features/auth/useAuth.ts` — useLogin, useRegister hooks
- [ ] `store/authStore.ts` — Zustand store with user + token
- [ ] `app/(auth)/register/page.tsx` — register form
- [ ] `app/(auth)/login/page.tsx` — login form
- [ ] Protected route middleware in `middleware.ts`
- [ ] Test: register → login → redirect to dashboard → logout

---

## Phase 2 — File Upload & OCR (Day 5–7)

### Backend
- [ ] `pip install pymupdf easyocr`
- [ ] `services/file_service.py` — save_file(), validate_file(), delete_file()
- [ ] `services/ocr_service.py` — extract_text(), extract_from_pdf(), extract_from_image(), clean_text(), extract_medical_values()
- [ ] `models/report.py` — SQLAlchemy Report model (all fields from schema)
- [ ] `schemas/report.py` — ReportCreate, ReportResponse
- [ ] `repositories/report_repository.py` — create, get_by_id, get_by_user_id, delete
- [ ] `routers/reports.py` — POST /reports/upload, GET /reports, GET /reports/{id}, DELETE /reports/{id}
- [ ] Alembic migration: create reports table
- [ ] Test: upload PDF → text extracted → values dict returned

### Frontend
- [ ] `types/index.ts` — Report, ExtractedValues interfaces
- [ ] `features/reports/reportService.ts` — upload(), getAll(), getById(), deleteById()
- [ ] `features/reports/useReports.ts` — useReports, useReport, useUpload hooks
- [ ] `components/upload/UploadZone.tsx` — drag-and-drop with react-dropzone
- [ ] `components/upload/ProcessingSteps.tsx` — OCR → NLP → Embedding status steps
- [ ] `app/(dashboard)/upload/page.tsx` — full upload page
- [ ] `components/report/ReportCard.tsx` — card with filename, date, status badge
- [ ] `components/report/ReportList.tsx` — grid of report cards
- [ ] `app/(dashboard)/dashboard/page.tsx` — dashboard with report list
- [ ] Test: drag PDF → upload → see report card appear on dashboard

---

## Phase 3 — NLP Entity Extraction (Day 8–9)

### Backend
- [ ] `pip install transformers torch sentence-transformers`
- [ ] `services/nlp_service.py` — load_pipeline() at startup, extract_entities()
- [ ] Integrate NLP into upload pipeline after OCR
- [ ] Store entities JSON in report record
- [ ] Test: upload blood test → diseases/medicines extracted correctly

### Frontend
- [ ] `types/index.ts` — Entities, EntityGroup interfaces
- [ ] `components/report/EntityPills.tsx` — color-coded pills per entity type
- [ ] `app/(dashboard)/reports/[id]/page.tsx` — report detail page (entities section)
- [ ] Test: view report detail → see entity pills for detected terms

---

## Phase 4 — ML Risk Prediction + SHAP (Day 10–13)

### ML Training (Jupyter Notebooks)
- [ ] `notebooks/eda/diabetes_eda.ipynb` — full EDA on Pima dataset
- [ ] `notebooks/model_training/diabetes_model.ipynb` — feature engineering + SMOTE + XGBoost training
- [ ] `notebooks/model_training/heart_model.ipynb` — Cleveland dataset + XGBoost training
- [ ] Save: `ml_models/diabetes_model.pkl`, `ml_models/heart_model.pkl`, `ml_models/scaler.pkl`
- [ ] Document model metrics: accuracy, F1, AUC in `notebooks/MODEL_METRICS.md`

### Backend
- [ ] `pip install scikit-learn xgboost imbalanced-learn shap joblib`
- [ ] `services/predict_service.py` — load_models() at startup, predict_diabetes(), predict_heart(), get_shap_values()
- [ ] `schemas/predict.py` — PredictionRequest, PredictionResponse, ShapEntry
- [ ] `routers/predict.py` — POST /predict/diabetes, POST /predict/heart
- [ ] Integrate prediction into upload pipeline
- [ ] Test: upload diabetes report → risk score + SHAP values returned

### Frontend
- [ ] `types/index.ts` — PredictionResult, ShapEntry interfaces
- [ ] `features/predict/usePrediction.ts` — React Query hook
- [ ] `components/risk/RiskScoreCard.tsx` — large risk percentage + risk level badge
- [ ] `components/risk/ShapBarChart.tsx` — horizontal bar chart of SHAP contributions (Recharts)
- [ ] `components/risk/RiskBadge.tsx` — low/moderate/high colored badge
- [ ] Add risk section to `/reports/[id]` page
- [ ] Test: view report → see risk score with color coding + SHAP chart

---

## Phase 5 — RAG Chatbot (Day 14–17)

### Backend
- [ ] `pip install langchain langchain-community faiss-cpu anthropic`
- [ ] `services/rag_service.py` — index_report(), query_report(), delete_index()
- [ ] Integrate FAISS indexing into upload pipeline (after OCR)
- [ ] `models/chat_history.py` — ChatHistory SQLAlchemy model
- [ ] `repositories/chat_repository.py` — create, get_by_user
- [ ] `routers/chat.py` — POST /chat/query (SSE streaming), GET /chat/history
- [ ] Alembic migration: create chat_history table
- [ ] System prompt: constrain LLM to answer only from retrieved chunks
- [ ] Test: index a report → ask question → grounded answer returned

### Frontend
- [ ] `types/index.ts` — ChatMessage, ChatHistory interfaces
- [ ] `features/chat/chatService.ts` — query() with SSE handling
- [ ] `features/chat/useChat.ts` — message state + streaming hook
- [ ] `components/chat/ChatWindow.tsx` — scrollable message area
- [ ] `components/chat/MessageBubble.tsx` — user (right) and AI (left) styled bubbles
- [ ] `components/chat/ChatInput.tsx` — input + send button
- [ ] `components/chat/ReportSelector.tsx` — dropdown to select report context
- [ ] `app/(dashboard)/chat/page.tsx` — full chat page
- [ ] Test: select report → ask question → see streaming answer

---

## Phase 6 — Dashboard & Report Detail Polish (Day 18–20)

### Frontend
- [ ] `components/layout/Sidebar.tsx` — fixed sidebar with nav links + user avatar
- [ ] `components/layout/TopNav.tsx` — breadcrumb + theme toggle
- [ ] `components/layout/MobileNav.tsx` — bottom nav for mobile
- [ ] `components/ui/Skeleton.tsx` — shimmer skeleton component
- [ ] Add skeleton loading states to: ReportList, ReportCard, RiskScoreCard, ShapBarChart
- [ ] `app/(dashboard)/reports/[id]/page.tsx` — complete report detail:
  - [ ] Hero section (filename + date + overall risk badge)
  - [ ] Lab values grid (2 columns, monospace values)
  - [ ] Risk prediction card with SHAP chart
  - [ ] Entity pills section
  - [ ] Collapsible raw text section
- [ ] Dark mode: CSS custom properties + `data-theme` toggle + localStorage persistence
- [ ] Responsive: test all pages at 375px, 768px, 1280px

---

## Phase 7 — Testing (Day 21–23)

### Backend Tests (pytest)
- [ ] `tests/test_auth.py` — register, login, invalid token
- [ ] `tests/test_ocr.py` — PDF extraction, image extraction, empty file handling
- [ ] `tests/test_predict.py` — valid input, missing fields, model output shape
- [ ] `tests/test_rag.py` — index, query, empty index handling
- [ ] `tests/test_reports.py` — upload, get, delete, unauthorized access
- [ ] Run: `pytest --cov=app tests/` — target >70% coverage

### Frontend Tests
- [ ] `ReportCard.test.tsx` — renders correctly, calls onDelete
- [ ] `UploadZone.test.tsx` — accepts valid files, rejects invalid types
- [ ] `ShapBarChart.test.tsx` — renders bars from SHAP data
- [ ] `useChat.test.ts` — message state updates correctly

---

## Phase 8 — CI/CD & Deployment (Day 24–25)

- [ ] `.github/workflows/ci.yml` — pytest + Next.js build on every PR
- [ ] `.github/workflows/deploy.yml` — Docker build + push to Docker Hub on main
- [ ] Deploy backend to Render (free tier) or Railway
- [ ] Deploy frontend to Vercel
- [ ] Deploy PostgreSQL to Supabase (free tier)
- [ ] Set all environment variables in deployment platform
- [ ] Test: full user flow on production URL

---

## Phase 9 — Portfolio Polish (Day 26–27)

- [ ] `README.md` — complete with: overview, demo GIF, tech stack table, setup steps, API table, model metrics
- [ ] Record Loom walkthrough video (5–7 min): upload → OCR → risk → chat
- [ ] Add live demo link to GitHub repo description
- [ ] Add project to LinkedIn with 3-bullet description
- [ ] Prepare SHAP explanation for FAANG interviews (memorize from PROJECT_CONTEXT.md)

---

## Optimization Tasks (Post-MVP)

- [ ] Background task queue: move OCR+NLP to Celery + Redis (async processing)
- [ ] File storage: migrate from local disk to AWS S3 or Cloudflare R2
- [ ] Vector DB: migrate from FAISS to Pinecone for scalability
- [ ] Caching: add Redis cache for repeated predictions on same report
- [ ] Rate limiting: add `slowapi` to FastAPI for all endpoints
- [ ] Monitoring: add Sentry error tracking (frontend + backend)
- [ ] Logging: structured JSON logging with `loguru`
- [ ] Database: add read replica for GET endpoints

---

## Future Enhancement Ideas (Recommended — Not in Current Spec)

- [ ] Health timeline chart: glucose/BMI trends across multiple reports
- [ ] Report comparison: old vs new values side by side
- [ ] Medicine recommendation: suggest generic alternatives
- [ ] Doctor share mode: read-only report link with expiry
- [ ] Multi-language OCR: Hindi, Arabic, French medical reports
- [ ] Email alerts: notify user when abnormal value detected
- [ ] Mobile app: React Native with Expo
- [ ] Voice Q&A: Web Speech API for chat input

---

## Milestone Summary

| Milestone | Target Day | Deliverable |
|---|---|---|
| Project boots locally | Day 2 | `docker-compose up` works |
| Auth works end-to-end | Day 4 | Register → Login → Dashboard |
| Upload + OCR works | Day 7 | PDF upload → values extracted |
| NLP entities work | Day 9 | Diseases/medicines detected |
| Risk + SHAP works | Day 13 | Risk score with explanation |
| RAG chatbot works | Day 17 | Q&A over own reports |
| Full UI polished | Day 20 | Dark mode, responsive, skeletons |
| Tests passing | Day 23 | >70% coverage |
| Deployed live | Day 25 | Production URL working |
| Portfolio ready | Day 27 | README + video + LinkedIn |
