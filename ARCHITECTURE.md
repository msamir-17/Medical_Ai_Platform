# ARCHITECTURE.md
# System Architecture — AI Medical Record Intelligence Platform

> Reference before creating any new file, route, service, or database model.
> All AI agents must preserve this structure when adding features.

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                      │
│              Next.js 14 — App Router — TypeScript        │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / REST / SSE
┌───────────────────────▼─────────────────────────────────┐
│                 FastAPI Backend (Python 3.11)             │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐  │
│  │  /auth   │ │/reports  │ │ /predict  │ │  /chat   │  │
│  └──────────┘ └──────────┘ └───────────┘ └──────────┘  │
│  ┌──────────────────────────────────────────────────┐   │
│  │               Service Layer                       │   │
│  │  OCR │ NLP │ RAG │ Predict │ Auth │ File         │   │
│  └──────────────────────────────────────────────────┘   │
└──────┬──────────────┬────────────────┬───────────────────┘
       │              │                │
┌──────▼───┐   ┌──────▼──────┐  ┌─────▼──────┐
│PostgreSQL│   │FAISS Indexes│  │ File Store │
│(primary  │   │(vector_     │  │(uploads/)  │
│  DB)     │   │stores/)     │  │            │
└──────────┘   └─────────────┘  └────────────┘
                        │
              ┌──────────▼──────────┐
              │  External LLM API   │
              │  Anthropic / OpenAI │
              └─────────────────────┘
```

---

## 2. Frontend Architecture (Next.js 14)

### Pattern: Feature-based + App Router

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Route group — no layout
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── (dashboard)/              # Route group — with sidebar layout
│   │   ├── layout.tsx            # Sidebar + top nav
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── upload/
│   │   │   └── page.tsx
│   │   ├── reports/
│   │   │   ├── page.tsx          # All reports list
│   │   │   └── [id]/
│   │   │       └── page.tsx      # Single report detail
│   │   └── chat/
│   │       └── page.tsx
│   ├── api/                      # Next.js API routes (auth only)
│   │   └── auth/[...nextauth]/
│   │       └── route.ts
│   ├── layout.tsx                # Root layout (providers)
│   └── globals.css
│
├── components/
│   ├── ui/                       # Primitive reusable components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Input.tsx
│   │   ├── Skeleton.tsx
│   │   ├── Modal.tsx
│   │   ├── Toast.tsx
│   │   └── Spinner.tsx
│   ├── layout/                   # Layout components
│   │   ├── Sidebar.tsx
│   │   ├── TopNav.tsx
│   │   └── MobileNav.tsx
│   ├── report/                   # Feature: Reports
│   │   ├── ReportCard.tsx
│   │   ├── ReportList.tsx
│   │   ├── LabValuesGrid.tsx
│   │   ├── EntityPills.tsx
│   │   └── RawTextCollapse.tsx
│   ├── risk/                     # Feature: Risk Prediction
│   │   ├── RiskScoreCard.tsx
│   │   ├── ShapBarChart.tsx
│   │   └── RiskBadge.tsx
│   ├── upload/                   # Feature: Upload
│   │   ├── UploadZone.tsx
│   │   └── ProcessingSteps.tsx
│   └── chat/                     # Feature: Chatbot
│       ├── ChatWindow.tsx
│       ├── MessageBubble.tsx
│       ├── ChatInput.tsx
│       └── ReportSelector.tsx
│
├── features/                     # Feature-level hooks + logic
│   ├── auth/
│   │   ├── useAuth.ts
│   │   └── authService.ts
│   ├── reports/
│   │   ├── useReports.ts
│   │   ├── useReport.ts
│   │   └── reportService.ts
│   ├── predict/
│   │   └── usePrediction.ts
│   └── chat/
│       ├── useChat.ts
│       └── chatService.ts
│
├── lib/
│   ├── api.ts                    # Axios instance with interceptors
│   ├── auth.ts                   # NextAuth config
│   └── utils.ts                  # Shared utilities
│
├── types/
│   └── index.ts                  # All TypeScript interfaces
│
├── hooks/
│   ├── useDebounce.ts
│   └── useLocalStorage.ts
│
├── store/                        # Zustand global state
│   ├── authStore.ts
│   └── uiStore.ts                # theme, sidebar state
│
└── constants/
    ├── api.ts                    # API endpoint constants
    └── app.ts                    # App-wide constants
```

### State Management Strategy

| State Type | Tool |
|---|---|
| Server state (reports, predictions) | TanStack Query (React Query) |
| Auth state | NextAuth session + Zustand |
| UI state (theme, sidebar) | Zustand |
| Form state | React Hook Form |
| URL state | Next.js searchParams |

### Data Fetching Pattern
```typescript
// Always use React Query for server data
const { data, isLoading, error } = useQuery({
  queryKey: ['report', id],
  queryFn: () => reportService.getById(id),
  staleTime: 5 * 60 * 1000,   // 5 minutes
})
```

---

## 3. Backend Architecture (FastAPI)

### Pattern: Layered — Router → Service → Repository

```
backend/
├── app/
│   ├── main.py                   # App entry, middleware, router inclusion
│   ├── config.py                 # Settings via pydantic-settings
│   ├── database.py               # SQLAlchemy engine + session
│   │
│   ├── routers/                  # HTTP layer — thin, no business logic
│   │   ├── auth.py               # POST /auth/register, /auth/login
│   │   ├── reports.py            # POST /reports/upload, GET /reports, GET /reports/{id}
│   │   ├── predict.py            # POST /predict/diabetes, /predict/heart
│   │   └── chat.py               # POST /chat/query, GET /chat/history
│   │
│   ├── services/                 # Business logic — all AI/ML lives here
│   │   ├── auth_service.py       # JWT creation, bcrypt, token validation
│   │   ├── ocr_service.py        # PyMuPDF + EasyOCR + regex extraction
│   │   ├── nlp_service.py        # BioBERT/SciBERT NER pipeline
│   │   ├── rag_service.py        # LangChain + FAISS indexing + querying
│   │   ├── predict_service.py    # ML model loading + SHAP inference
│   │   └── file_service.py       # File save/delete/path management
│   │
│   ├── repositories/             # Database access — SQLAlchemy queries
│   │   ├── user_repository.py
│   │   ├── report_repository.py
│   │   └── chat_repository.py
│   │
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── report.py
│   │   └── chat_history.py
│   │
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── report.py
│   │   ├── predict.py
│   │   └── chat.py
│   │
│   ├── middleware/
│   │   ├── auth_middleware.py    # JWT validation dependency
│   │   └── error_middleware.py   # Global error handler
│   │
│   └── utils/
│       ├── file_utils.py         # Path helpers, MIME validation
│       └── text_utils.py         # Text cleaning utilities
│
├── ml_models/                    # Serialized models (gitignored, mounted in Docker)
│   ├── diabetes_model.pkl
│   ├── heart_model.pkl
│   └── scaler.pkl
│
├── vector_stores/                # FAISS indexes per user (gitignored)
├── uploads/                      # Temporary file storage (gitignored)
├── tests/
│   ├── test_auth.py
│   ├── test_ocr.py
│   ├── test_predict.py
│   └── test_rag.py
├── Dockerfile
└── requirements.txt
```

---

## 4. Database Schema (PostgreSQL)

### Table: `users`
```sql
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       VARCHAR(255) UNIQUE NOT NULL,
  password    VARCHAR(255) NOT NULL,         -- bcrypt hash
  created_at  TIMESTAMP DEFAULT NOW(),
  updated_at  TIMESTAMP DEFAULT NOW()
);
```

### Table: `reports`
```sql
CREATE TABLE reports (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID REFERENCES users(id) ON DELETE CASCADE,
  filename          VARCHAR(255) NOT NULL,
  file_path         VARCHAR(512) NOT NULL,
  file_type         VARCHAR(10) NOT NULL,     -- pdf | jpg | png
  extracted_text    TEXT,
  extracted_values  JSONB,                    -- {glucose: "240", hba1c: "8.2"}
  entities          JSONB,                    -- {diseases: [], medicines: []}
  diabetes_risk     FLOAT,                    -- 0.0 to 1.0
  heart_risk        FLOAT,
  shap_diabetes     JSONB,                    -- [{feature, value, contribution}]
  shap_heart        JSONB,
  ocr_status        VARCHAR(20) DEFAULT 'pending',  -- pending|done|failed
  created_at        TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_reports_user_id ON reports(user_id);
```

### Table: `chat_history`
```sql
CREATE TABLE chat_history (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
  report_id   UUID REFERENCES reports(id) ON DELETE SET NULL,
  question    TEXT NOT NULL,
  answer      TEXT NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_chat_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_report_id ON chat_history(report_id);
```

---

## 5. API Architecture

### Conventions
- All routes return `application/json`
- All protected routes require `Authorization: Bearer <token>` header
- All error responses follow: `{ "detail": "message", "code": "ERROR_CODE" }`
- Pagination: `?page=1&limit=20`

### Endpoint Map

```
POST   /auth/register           → { access_token, token_type }
POST   /auth/login              → { access_token, token_type }
GET    /auth/me                 → { id, email, created_at }

POST   /reports/upload          → { id, filename, status }       [multipart]
GET    /reports                 → [{ id, filename, risk, date }] [paginated]
GET    /reports/{id}            → Full report object
DELETE /reports/{id}            → { success: true }

POST   /predict/diabetes        → { risk_score, shap_values, explanation }
POST   /predict/heart           → { risk_score, shap_values, explanation }

POST   /chat/query              → SSE stream of answer tokens
GET    /chat/history            → [{ question, answer, report_id, date }]

GET    /health                  → { status: "ok" }
```

---

## 6. Authentication Flow

```
1. User POST /auth/register { email, password }
2. Backend: hash password (bcrypt, rounds=12) → save to users table
3. Backend: create JWT { sub: user_id, exp: now+24h } signed with SECRET_KEY
4. Frontend: store token in memory (Zustand) + httpOnly cookie via NextAuth
5. Every subsequent request: send Authorization: Bearer <token>
6. Backend middleware: decode JWT → get user_id → inject as dependency
7. Token expiry: 401 Unauthorized → frontend redirects to /login
```

FastAPI dependency pattern:
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_jwt(token)
    user = user_repository.get_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=401)
    return user
```

---

## 7. Processing Pipeline Flow

```
File Upload Request
    ↓
file_service.save(file)          → disk: uploads/{user_id}/{uuid}.{ext}
    ↓
ocr_service.extract_text(path)   → raw_text: str
    ↓
ocr_service.extract_values(text) → values: dict
    ↓
nlp_service.extract_entities(text) → entities: dict
    ↓
predict_service.predict(values)  → risk_score + shap_values
    ↓
rag_service.index_report(text, user_id) → FAISS index saved
    ↓
report_repository.save(all_data) → PostgreSQL record created
    ↓
Return report_id to frontend
```

---

## 8. Error Handling Architecture

### Backend
```python
# app/middleware/error_middleware.py
@app.exception_handler(Exception)
async def global_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"}
    )

# Service-level errors — raise HTTPException with specific codes
raise HTTPException(status_code=400, detail="OCR extraction failed — file may be corrupt")
raise HTTPException(status_code=413, detail="File too large — maximum 10MB")
raise HTTPException(status_code=422, detail="Insufficient data for prediction")
```

### Frontend
```typescript
// lib/api.ts — Axios interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authStore.logout()
      router.push('/login')
    }
    toast.error(error.response?.data?.detail ?? 'Something went wrong')
    return Promise.reject(error)
  }
)
```

---

## 9. Performance Optimization

### Frontend
- All images: Next.js `<Image>` with lazy loading
- Routes: automatic code splitting via App Router
- Data fetching: React Query with stale-while-revalidate
- Heavy components (charts, chat): dynamic import with `next/dynamic`
- Bundle analysis: run `ANALYZE=true npm run build` periodically

### Backend
- NLP model: loaded once at startup (module-level singleton), not per-request
- ML models: loaded once at startup via `@app.on_event("startup")`
- FAISS index: cached in memory per user_id in a dict after first load
- Large file processing: consider background tasks for files >2MB
```python
@app.on_event("startup")
async def load_models():
    predict_service.load_models()  # loads .pkl files once
    nlp_service.load_pipeline()    # loads BioBERT once
```
