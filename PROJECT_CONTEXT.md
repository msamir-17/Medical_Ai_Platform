# PROJECT_CONTEXT.md
# AI Medical Record Intelligence Platform

> Drop this file into any AI coding agent (Claude, Gemini, Cursor, Windsurf, Copilot)
> as persistent project memory. Reference it at the start of every session.

---

## 1. Product Overview

A full-stack AI-powered medical record platform where patients upload medical
documents (PDFs, scanned images) and the system automatically:
- Extracts raw text via OCR
- Identifies medical entities via NLP (BioBERT)
- Predicts disease risk via ML models with SHAP explainability
- Enables conversational Q&A over the user's own reports via RAG + LLM

Target users: individual patients managing personal health records.
Target audience for evaluation: FAANG/MAANG internship and fresher interviews.

---

## 2. Core Features

### Confirmed Features (from project spec)

| Feature | Description |
|---|---|
| Report Upload | PDF and image upload via drag-and-drop |
| OCR Extraction | Text extraction using EasyOCR (images) and PyMuPDF (PDFs) |
| Medical Value Parsing | Regex extraction of glucose, HbA1c, blood pressure etc. |
| NLP Entity Extraction | Disease, medicine, symptom detection via BioBERT/SciBERT |
| Diabetes Risk Prediction | XGBoost model trained on Pima Indians dataset |
| Heart Disease Risk | XGBoost model trained on Cleveland Heart Disease dataset |
| SHAP Explainability | Per-prediction feature contribution breakdown |
| RAG Chatbot | LangChain + FAISS + LLM Q&A over uploaded reports |
| Health Dashboard | Risk scores, extracted values, entity cards, health timeline |
| Authentication | JWT-based login and registration |
| Report History | Per-user report list with metadata |
| Chat History | Stored conversation turns per report |
| Docker Deployment | Full docker-compose orchestration |

### Recommended Future Features (not in current spec — mark clearly in code)

- Medicine alternative recommendation engine
- Report comparison (old vs new values over time)
- Health timeline chart (glucose/BMI trends across reports)
- Generic medicine suggestion system
- Multi-language report support
- Email/notification alerts on abnormal values
- Doctor sharing mode (read-only report link)
- Mobile app (React Native)

---

## 3. User Flows

### Flow 1 — New User Registration
```
Land on homepage → click Register → fill email + password
→ POST /auth/register → JWT returned → redirect to dashboard
```

### Flow 2 — Report Upload
```
Dashboard → click Upload → drag PDF/image into UploadZone
→ POST /reports/upload (multipart) → backend saves file
→ OCR extracts text → NLP extracts entities
→ ML predicts risk → FAISS indexes embeddings
→ redirect to /reports/{id} with extracted data displayed
```

### Flow 3 — Risk Prediction View
```
/reports/{id} → view extracted lab values
→ see risk score (diabetes / heart) with percentage
→ see SHAP chart showing which features drove the risk
→ see plain-language explanation ("High glucose contributed 42%")
```

### Flow 4 — RAG Chatbot
```
/chat → select a report from dropdown
→ type question: "Is my glucose dangerous?"
→ POST /chat/query → FAISS retrieves top-4 chunks
→ chunks + question sent to LLM → answer streamed back
→ conversation stored in chat_history table
```

### Flow 5 — Report History
```
Dashboard → view all uploaded reports as cards
→ each card shows: filename, upload date, top risk score, entity count
→ click card → navigate to /reports/{id}
```

---

## 4. Functional Requirements

### Authentication
- [x] User registration with email + password
- [x] Password hashed with bcrypt (never stored plain)
- [x] JWT token issued on login, validated on every protected route
- [x] Token expiry: 24 hours (configurable via env)

### File Upload
- [x] Accept: PDF, PNG, JPG, JPEG
- [x] Max file size: 10MB (enforce on both frontend and backend)
- [x] Save file to `uploads/{user_id}/{uuid_filename}`
- [x] Return file metadata on success

### OCR
- [x] PDF: use PyMuPDF text layer extraction
- [x] Image / scanned PDF: use EasyOCR
- [x] Clean output: strip extra whitespace, normalize line breaks
- [x] Extract structured values via regex patterns

### NLP
- [x] Run BioBERT/SciBERT NER on cleaned text
- [x] Output: `{diseases: [], medicines: [], symptoms: [], values: []}`
- [x] Store result as JSON in PostgreSQL reports table

### ML Prediction
- [x] Diabetes model: XGBoost, trained on Pima Indians dataset
- [x] Heart model: XGBoost, trained on Cleveland dataset
- [x] Input: structured values extracted from report
- [x] Output: risk score (0.0–1.0) + SHAP feature contributions
- [x] Handle missing values gracefully (use model's median imputation)

### RAG Chatbot
- [x] Chunk report text (500 tokens, 50 overlap)
- [x] Embed using `sentence-transformers/all-MiniLM-L6-v2`
- [x] Store FAISS index per user at `vector_stores/{user_id}/`
- [x] Retrieve top-4 similar chunks per query
- [x] Pass chunks + question to LLM (Claude or OpenAI)
- [x] Stream response back to frontend via SSE or WebSocket
- [x] Store Q&A in chat_history table

---

## 5. Business Logic Rules

1. One FAISS index per user — all their reports are merged into one index
2. Risk prediction only runs if minimum required fields are extracted (e.g. glucose for diabetes)
3. If OCR fails to extract enough text (< 50 chars), return error and ask user to re-upload
4. SHAP output is always returned alongside any risk prediction — never prediction without explanation
5. Chat answers must only reference retrieved chunks — never general knowledge (enforced via system prompt)
6. All uploaded files are namespaced per user_id to prevent cross-user access
7. JWT must be validated before any file or prediction endpoint is accessed

---

## 6. Technical Goals

- OCR accuracy: >90% on standard printed medical documents
- ML model AUC: >0.80 on held-out test set
- RAG answer relevance: grounded in retrieved chunks only
- API response time: <2s for OCR+NLP pipeline, <500ms for predictions
- Chat first-token latency: <1s with streaming enabled

---

## 7. Scalability Goals (for interview discussion)

| Current (MVP) | Scaled Version |
|---|---|
| FAISS (local disk) | Pinecone (distributed vector DB) |
| Local file storage | AWS S3 / Cloudflare R2 |
| Synchronous OCR | Celery + Redis async job queue |
| Single FastAPI instance | Horizontal scaling behind load balancer |
| PostgreSQL single instance | PostgreSQL with read replicas |
| Local ML inference | Dedicated ML microservice |

---

## 8. Environment Variables

```env
# backend/.env
DATABASE_URL=postgresql://user:password@postgres:5432/medicaldb
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...        # fallback
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=uploads
VECTOR_STORE_DIR=vector_stores
MODEL_DIR=ml_models

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```
