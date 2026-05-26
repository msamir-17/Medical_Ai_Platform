# AI_AGENT_RULES.md
# AI Coding Agent Instructions — AI Medical Record Intelligence Platform

> Paste this file at the start of every AI coding session.
> Optimized for: Claude Opus, Gemini Flash, Cursor, Windsurf, VS Code AI agents, Codex.

---

## Identity & Context

You are an AI coding assistant working on the **AI Medical Record Intelligence Platform**.

This is a full-stack application:
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, React Query, Zustand
- **Backend**: FastAPI (Python 3.11), SQLAlchemy, Pydantic, LangChain, FAISS
- **Database**: PostgreSQL
- **AI pipeline**: EasyOCR, PyMuPDF, BioBERT/SciBERT, XGBoost + SHAP, LangChain RAG

The project uses a **feature-based, layered architecture**. Read ARCHITECTURE.md before
modifying any file structure. Read UI_GUIDELINES.md before generating any component.
Read DEVELOPMENT_RULES.md before writing any code.

---

## Core Behavioral Rules

### Before Writing Any Code
1. Identify which layer the change belongs to: Router / Service / Repository / Component / Hook
2. Check if a similar component or service already exists — extend it, don't duplicate
3. Verify the TypeScript interface for any new data shape exists in `types/index.ts`
4. Confirm the change doesn't require a database migration before proceeding

### When Modifying Existing Files
- Read the entire file before making any edit
- Preserve all existing imports, exports, and interfaces
- Do not change function signatures unless explicitly instructed
- Do not add new dependencies without noting them
- Preserve all existing error handling
- Never remove `TODO` or `FIXME` comments — preserve developer notes

### When Creating New Files
- Follow the exact folder structure defined in ARCHITECTURE.md
- Match naming conventions from DEVELOPMENT_RULES.md exactly
- Always include the full file — never partial snippets for new files
- New React components must have: TypeScript interface, default export, loading state
- New FastAPI routes must have: response_model, auth dependency, error handling

---

## Code Generation Rules

### TypeScript / React
```typescript
// Every new component must follow this structure
interface ComponentNameProps {
  // Required props first, optional props last with ?
  requiredProp: string
  optionalProp?: boolean
  className?: string
}

export function ComponentName({ requiredProp, optionalProp, className }: ComponentNameProps) {
  // 1. Hooks first
  // 2. Derived state / memoized values
  // 3. Event handlers
  // 4. Return JSX
}
```

Rules:
- `any` type is forbidden — use `unknown` if type is genuinely dynamic
- Always handle: loading state, error state, empty state — all three
- React Query: `queryKey` arrays must be consistent and documented
- Tailwind classes: follow UI_GUIDELINES.md color and spacing tokens
- Import order: React → Next → third-party → internal (components → lib → types)

### Python / FastAPI
```python
# Every new route must follow this structure
@router.post("/endpoint", response_model=ResponseSchema, status_code=201)
async def create_something(
    request_body: RequestSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResponseSchema:
    """One-line docstring describing the endpoint."""
    result = await service_function(request_body, current_user.id, db)
    return result
```

Rules:
- Type annotations on every function parameter and return value — no exceptions
- Pydantic schemas for all request bodies and responses — never raw dicts
- `HTTPException` with specific status codes and descriptive messages
- No business logic in routers — call service functions only
- No database queries in services — call repository functions only

---

## Preservation Rules (Do Not Break)

### Architecture Boundaries
- ❌ Never put database queries in a router file
- ❌ Never put business logic in a component
- ❌ Never call API endpoints directly in a component (always via service + React Query)
- ❌ Never add global CSS that overrides Tailwind base styles
- ❌ Never mutate Zustand state outside of store action functions
- ❌ Never bypass JWT authentication on any data endpoint

### UI Consistency
- ❌ Never use hardcoded hex colors — always use CSS custom properties
- ❌ Never use inline `style={{}}` for layout — use Tailwind classes
- ❌ Never create a new loading spinner component — use the existing `Spinner` from `components/ui/`
- ❌ Never create a new Button component — use and extend the existing one
- ❌ Never use arbitrary Tailwind values like `w-[317px]` — use scale tokens

### Performance
- ❌ Never import an entire library when only a function is needed
- ❌ Never add a new npm package without checking if existing dependencies cover the need
- ❌ Never put expensive computations inside render — use `useMemo`
- ❌ Never load ML models per-request — they must be singletons loaded at startup

---

## How to Add a New Feature

Follow this exact sequence:

1. **Type first**: Add TypeScript interfaces to `types/index.ts`
2. **API contract**: Add endpoint constants to `constants/api.ts`
3. **Service**: Create or update service file in `features/{feature}/`
4. **Hook**: Create React Query hook in `features/{feature}/use{Feature}.ts`
5. **Backend route**: Add router function (thin — calls service only)
6. **Backend service**: Add business logic function
7. **Backend repository**: Add database query function
8. **Component**: Build UI component consuming the hook
9. **Page**: Wire component into the App Router page

Never skip steps or merge them. This sequence ensures testability and prevents coupling.

---

## Refactoring Rules

- Extract only when: same logic appears in 2+ places OR function exceeds 40 lines
- Renaming: update ALL usages — never leave dead references
- When splitting a component: the parent must remain backward-compatible
- When changing a service function signature: update all callers in the same PR
- Do not refactor and add features in the same commit

---

## AI Response Format for This Project

When generating code, always structure your response as:

```
1. Brief explanation of what you're doing and why (2–3 sentences max)
2. File path header before each code block: `// frontend/components/risk/ShapBarChart.tsx`
3. Complete file content (never partial for new files)
4. List of any new dependencies to install
5. Any database migration required (yes/no, and if yes, the SQL)
6. List of other files that need to be updated as a result
```

When asked to fix a bug:
```
1. State what the bug is and its root cause
2. Show the minimal change to fix it (not a full rewrite)
3. Explain what would happen if this fix is not applied
```

---

## Prohibited Patterns

```typescript
// ❌ Never generate these patterns

// Prohibited: prop drilling more than 2 levels
<A><B><C onAction={handleAction} /></B></A>  // use context or Zustand

// Prohibited: useEffect for data fetching
useEffect(() => { fetchData() }, [])  // use React Query

// Prohibited: console.log in production code
console.log('debug')  // use structured error handling

// Prohibited: hardcoded API URLs
fetch('http://localhost:8000/reports')  // use constants/api.ts

// Prohibited: catching errors silently
try { ... } catch (e) {}  // always handle or rethrow
```

```python
# ❌ Never generate these patterns

# Prohibited: raw SQL with f-strings
f"SELECT * FROM users WHERE id = {user_id}"

# Prohibited: catching broad exceptions silently
except Exception:
    pass

# Prohibited: global mutable state in services
diabetes_model = None  # wrong — use startup event and proper singleton

# Prohibited: loading models per request
def predict(values):
    model = joblib.load('models/diabetes_model.pkl')  # wrong — do this at startup
```

---

## Quick Reference: Where Does Code Go?

| What you're building | Where it goes |
|---|---|
| HTTP endpoint | `backend/app/routers/` |
| Business logic, AI pipeline | `backend/app/services/` |
| Database query | `backend/app/repositories/` |
| ORM table definition | `backend/app/models/` |
| Request/response shape | `backend/app/schemas/` |
| React data fetching | `frontend/features/{name}/use{Name}.ts` |
| HTTP call to backend | `frontend/features/{name}/{name}Service.ts` |
| Reusable UI primitive | `frontend/components/ui/` |
| Feature-specific UI | `frontend/components/{feature}/` |
| Global TypeScript types | `frontend/types/index.ts` |
| Global constants | `frontend/constants/` |
| App page | `frontend/app/(dashboard)/{route}/page.tsx` |
