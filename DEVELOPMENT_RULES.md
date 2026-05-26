# DEVELOPMENT_RULES.md
# Development Rules & Standards — AI Medical Record Intelligence Platform

> Every developer and AI agent must follow these rules without exception.
> These rules exist to keep the codebase clean, scalable, and maintainable.

---

## 1. Naming Conventions

### TypeScript / React
```
Components:    PascalCase       → ReportCard.tsx, ShapBarChart.tsx
Hooks:         camelCase + use  → useReport.ts, useChat.ts
Services:      camelCase        → reportService.ts, authService.ts
Types:         PascalCase       → ReportType, PredictionResult
Interfaces:    PascalCase + I   → IReport, IUser (optional but consistent)
Constants:     UPPER_SNAKE_CASE → MAX_FILE_SIZE, API_BASE_URL
CSS classes:   kebab-case       → risk-badge, upload-zone
```

### Python / FastAPI
```
Files:         snake_case       → ocr_service.py, report_repository.py
Functions:     snake_case       → extract_text(), get_current_user()
Classes:       PascalCase       → UserRepository, OcrService
Constants:     UPPER_SNAKE_CASE → MAX_UPLOAD_SIZE, JWT_ALGORITHM
Pydantic models: PascalCase    → ReportCreate, UserResponse
SQLAlchemy models: PascalCase  → User, Report, ChatHistory
```

---

## 2. File Organization Rules

- One component per file — never combine two components in one file
- File name must match the default export name exactly
- Group by feature, not by file type (see ARCHITECTURE.md folder structure)
- Test files live next to the file they test: `ReportCard.test.tsx`
- Never put business logic in components — extract to hooks or services
- Never put API calls in components — all calls go through service files

---

## 3. Component Design Rules

### React Components
```typescript
// ✅ Correct pattern
interface ReportCardProps {
  report: ReportType
  onDelete?: (id: string) => void
  className?: string
}

export function ReportCard({ report, onDelete, className }: ReportCardProps) {
  // Logic extracted to hook if complex
  // Return JSX only
}

// ❌ Never do this
export default function Card(props: any) { ... }  // no any
export function ReportCard({ report, onDelete, x, y, z, a, b }) { ... }  // too many props — extract object
```

### Rules
- Max props: 6. More than 6 → create a sub-component or pass an object
- Always define prop types with TypeScript interface — never `any`
- Components must be pure (same input → same output) unless stateful by design
- Side effects only in `useEffect` with proper dependency arrays
- Never call React Query hooks conditionally
- All async operations must handle loading and error states

---

## 4. TypeScript Rules

```typescript
// ✅ Strict types always
interface PredictionResult {
  riskScore: number          // 0.0 to 1.0
  shapValues: ShapEntry[]
  explanation: string
}

// ✅ Use union types for fixed sets
type RiskLevel = 'low' | 'moderate' | 'high'
type FileType = 'pdf' | 'jpg' | 'jpeg' | 'png'

// ✅ Never suppress TypeScript errors
// ❌ @ts-ignore — forbidden
// ❌ as any — forbidden
// ❌ ! non-null assertion — use optional chaining (?.) instead
```

- `tsconfig.json` must have `"strict": true` — never disable
- All API response types must be defined in `types/index.ts`
- Use `unknown` instead of `any` when type is genuinely uncertain

---

## 5. API Handling Rules

```typescript
// All API calls go through the service layer
// reportService.ts
export const reportService = {
  getAll: (): Promise<ReportType[]> =>
    api.get('/reports').then(r => r.data),

  getById: (id: string): Promise<ReportType> =>
    api.get(`/reports/${id}`).then(r => r.data),

  upload: (file: File): Promise<{ id: string }> => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/reports/upload', form).then(r => r.data)
  }
}

// Components always consume via React Query — never call service directly
const { data } = useQuery({ queryKey: ['reports'], queryFn: reportService.getAll })
```

- Never use `fetch` directly — always use the configured Axios instance in `lib/api.ts`
- API base URL must come from `process.env.NEXT_PUBLIC_API_URL` — never hardcoded
- All endpoints defined as constants in `constants/api.ts`

---

## 6. Python / FastAPI Rules

```python
# ✅ Routers are thin — only HTTP concerns
@router.post("/upload", response_model=ReportResponse)
async def upload_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await report_service.process_upload(file, current_user.id, db)

# ✅ Services contain all business logic
# ✅ Repositories contain all database queries
# ❌ Never write SQL or DB queries inside a router
# ❌ Never write business logic inside a model
```

- All route handlers must be `async`
- Use `Depends()` for dependency injection — never instantiate services inside handlers
- All Pydantic models must use `model_config = ConfigDict(from_attributes=True)`
- Every endpoint must have a `response_model` declared

---

## 7. Security Rules

### Frontend
- Never store JWT in localStorage — use httpOnly cookies via NextAuth
- Never expose API keys in frontend code — all keys are server-side only
- Sanitize all user input before display (use `DOMPurify` if rendering HTML)
- Validate file type on frontend before upload (don't trust MIME type alone)

### Backend
- All file uploads: validate extension AND magic bytes (file header)
- Sanitize filenames: `secure_filename()` — strip path traversal characters
- Rate limit auth endpoints: max 10 attempts/minute per IP
- Never log passwords, tokens, or PHI (personally identifiable health info)
- Environment variables only via `pydantic-settings` — never `os.environ.get()` raw
- SQL queries only through SQLAlchemy ORM — never raw string interpolation

```python
# ✅ Safe
user = db.query(User).filter(User.email == email).first()

# ❌ Never — SQL injection risk
db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

---

## 8. Performance Rules

### Frontend
- Images: always use `<Image>` from `next/image`, never `<img>`
- Charts (Recharts): wrap in `dynamic(() => import(...), { ssr: false })`
- Avoid `useEffect` for derived state — use `useMemo` instead
- Avoid `useState` for server data — that's what React Query is for
- Re-renders: use `React.memo` on list item components (ReportCard, MessageBubble)
- Event handlers in lists: use event delegation or `useCallback`

### Backend
- ML models: singleton pattern — load once, reuse forever
- FAISS indexes: cache in module-level dict keyed by user_id
- Large text processing: use generators, not loading full file to memory
- Database queries: always filter by user_id first (index-backed)
- Avoid N+1 queries: use SQLAlchemy `joinedload()` for related data

---

## 9. Responsive Development Rules

- Start with mobile layout, add desktop via `md:` and `lg:` Tailwind prefixes
- Test on: 375px (iPhone SE), 768px (iPad), 1280px (desktop), 1920px (wide)
- No fixed pixel widths for containers — use `max-w-*` with `w-full`
- Touch targets: minimum `h-11 w-11` (44px) for all interactive elements
- Font sizes: never below `text-xs` (12px) on any screen

---

## 10. Animation Performance Rules

- Only animate: `transform`, `opacity` — never `width`, `height`, `margin`, `padding`
- Use Framer Motion for entrance animations — not raw CSS keyframes in components
- Framer Motion layout animations: only when layout shifts are intentional
- `AnimatePresence` required for exit animations
- Every animation: test with Chrome DevTools Performance tab — no janky frames

---

## 11. Git & Commit Rules

```
feat:     new feature
fix:      bug fix
chore:    dependency update, config change
refactor: code change without behavior change
test:     adding or updating tests
docs:     documentation only

Examples:
feat: add SHAP visualization to report detail page
fix: handle empty OCR output gracefully
refactor: extract chat logic into useChat hook
```

- One feature per branch: `feature/shap-chart`, `fix/ocr-empty-text`
- Never commit directly to `main`
- Never commit `.env` files — use `.env.example` with placeholder values
- Never commit `ml_models/`, `vector_stores/`, `uploads/` — all gitignored
