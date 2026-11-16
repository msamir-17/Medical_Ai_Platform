# MLOPS_PLAN.md — Medical AI Platform

> Isme: (1) project context, (2) agent ke rules, (3) mere suggestions vs tumhara original plan, (4) phase-wise tasks aur ready-to-paste prompts.
> **Ek time par sirf ek phase karwao.** Har phase ke end me "Done Checklist" verify karo, phir agla phase.

---

## 0. Agent ke liye RULES (har prompt ke saath ye follow karna hai)

1. **Existing logic mat todo.** RAG pipeline, auth, diabetes/heart prediction ka behaviour change nahi hona chahiye. Sirf additive changes (naye files, naye middleware, naye endpoints).
2. **Chhote commits.** Ek phase = ek branch (`mlops/phase-1-...`) = ek PR. Direct `main` pe push nahi.
3. **Secrets kabhi hardcode nahi.** Sab kuch environment variables se (HF Space Secrets / GitHub Secrets). `.env.example` update karo, real `.env` commit mat karo.
4. **Patient data = sensitive.** Logs, Sentry, metrics, GitHub repo me kisi bhi jagah patient ka naam, ID, phone, report text, ya lab values **user se link karke** store/send nahi karne. (Detail: Section 3.)
5. **Har change ke saath test.** Naya code likho to minimum 1 pytest likho.
6. **Pehle plan batao, phir code.** Agent har phase shuru karne se pehle files ki list + changes ka short plan de, tab hi code likhe.
7. **Library versions check karo.** Evidently, MLflow, Sentry ki API versions ke saath badalti hai. Installed version ke docs ke hisaab se code likho, memory se nahi.

---

## 1. Project Context (current status)

| Part | Detail |
|---|---|
| Frontend | Next.js 16 (App Router, TS, Tailwind v4, Zustand, React Query, Axios) — Vercel: `https://medical-ai-platform-iota.vercel.app` |
| Backend | FastAPI + uvicorn, 4 routers: `auth_routes`, `diabetes_routes`, `report_routes`, `chat_routes` — Hugging Face Space `samirk10/medical-ai-backend` (Docker SDK, port 7860, CPU Basic: 2 vCPU, 16 GB RAM) |
| DB | Supabase PostgreSQL (SQLAlchemy + psycopg) |
| File/Vector storage | Container disk: `uploads/`, `vector_stores/user_<id>/` (FAISS + in-memory BM25 + semantic cache). **Ephemeral**: Space restart = data gone |
| Models | `diabetes_model.pkl`, `scaler.pkl`, `heart_model.pkl`, `scaler_heart.pkl` + SHAP. Pretrained: EasyOCR, BioBERT, all-MiniLM-L6-v2, ChatGroq |
| Model registry | HF Hub `samirk10/medical-ai-models` via `model_loader.py` |
| Training | Sirf 4 notebooks, koi `train.py` / MLflow / DVC nahi |
| CI/CD | `.github/workflows/deploy-hf.yml` — `backend/` ko HF Space pe sync karta hai, **bina test gate ke** |
| Cloud | AWS pe kuch nahi |

---

## 2. Mere suggestions vs tumhara original plan

Tumhara plan achha hai, tools bhi sahi choose kiye hain. Lekin tum MLOps seekh rahe ho aur ye tumhare scale (free tier, low traffic, 2 small tabular models) ke liye thoda **zyada heavy** hai. Meri honest raay:

| Tumhara plan | Meri raay | Kyun |
|---|---|---|
| Prometheus + Grafana Cloud (Must-Have) | **Baad me (Phase 6, optional)** | Free HF Space public hai aur Grafana Cloud ko tumhare `/metrics` ko scrape karne ke liye alag agent/auth chahiye. Pehle Sentry + UptimeRobot + `/metrics` endpoint + structured logs se 80% value mil jati hai. |
| DVC for data versioning | **Abhi skip** | Pima (768 rows) aur Cleveland (303 rows) bahut chhote public datasets hain. Seedha `data/` me git me daal do (license/source README me likh do). DVC tab lo jab data badi ho ya private ho. |
| MLflow (DagsHub) | **Haan, lo** | Seekhne ke liye best. Lekin pehle `train.py` banao, tabhi MLflow ka matlab hai. |
| Evidently drift | **Haan, lekin batch me** | Low traffic me real-time drift meaningless hai. Hafte me ek baar report, minimum ~100 predictions hone par. |
| "Real-time model accuracy" | **Possible nahi (abhi)** | Ground truth label nahi milta. Isliye proxy metrics lo: prediction distribution, confidence, aur doctor/user ka thumbs up/down feedback. |
| Sirf ML monitoring pe focus | **RAG quality monitoring add karo** | Tumhara asli problem (lamba answer, galat scope) RAG ka hai. Isliye **golden test set** (Phase 4) sabse zyada kaam ka hai. |
| Ephemeral disk par FAISS/uploads | **Ye sabse bada risk hai** | Space restart/sleep = sab users ke vector stores aur PDFs gayab. Phase 5 me fix: Supabase Storage (PDF) + pgvector ya HF persistent storage. |
| Alerting | **Telegram Bot lo** | Free, 10 minute me setup, phone pe instant. |

### Meri recommended order (priority se)

1. **Phase 1** — Safety net: Sentry + UptimeRobot + `/health` (1 din)
2. **Phase 2** — Structured logging + `/metrics` + RAG metrics (1–2 din)
3. **Phase 3** — CI gate: pytest ke baad hi deploy (1 din)
4. **Phase 4** — RAG golden test set (yahi tumhara asli pain-point hai) (1–2 din)
5. **Phase 5** — Persistence fix (FAISS/uploads ephemeral problem) (2–3 din)
6. **Phase 6** — `train.py` + MLflow + model quality gate + HF Hub versioning
7. **Phase 7** — Prediction logging + Evidently weekly drift
8. **Phase 8 (optional)** — Grafana Cloud dashboards

Tum order change karna chaho to karo, bas Phase 1 aur 3 pehle rakho.

---

## 3. Medical data privacy rules (non-negotiable)

Ye project medical reports handle karta hai, isliye:

- **Logs / Sentry / metrics me ye kabhi nahi jana chahiye:** patient name, ID, phone, address, report text, extracted lab values with user identity, JWT tokens, API keys.
- Sentry: `send_default_pii=False` + `before_send` hook jo request body aur headers scrub kare.
- Logs me sirf **ids/hash** (`user_hash = sha256(user_id + SALT)[:12]`), latency, status code, error type.
- Prediction logging (Phase 7): sirf model features + prediction, **user identifier ke bina**.
- **Real patient reports GitHub repo me commit mat karo.** Tests ke liye synthetic/fake report banao (fake naam, fake values).
- Ye project public deploy hai to ek "Disclaimer: educational tool, not medical advice" frontend aur chat response me rakho.

---

## 4. Phases

### PHASE 1 — Safety net (Sentry + UptimeRobot + Health)

**Goal:** Crash ya downtime ho to tumhe pata chale.

**Tasks**
1. `backend/` me `GET /health` endpoint: `{"status":"ok","version": <git sha/env>, "db": true/false}` (DB check ek simple `SELECT 1`, 2 sec timeout).
2. `GET /ready`: models loaded hain ya nahi (diabetes, heart, vector store init) — `true/false`.
3. Sentry integration (`sentry-sdk[fastapi]`):
   - `SENTRY_DSN` env se.
   - `traces_sample_rate=0.1`, `send_default_pii=False`.
   - `before_send` me request body/headers/cookies remove karo.
   - `environment` = `production` / `local`.
4. Frontend (Next.js) me bhi Sentry (`@sentry/nextjs`) optional.
5. README me UptimeRobot setup steps likho (agent ye khud nahi kar sakta, manual hai):
   - UptimeRobot (free) → HTTP monitor → `https://samirk10-medical-ai-backend.hf.space/health` → 5 min interval.
   - Ye HF free Space ko sleep hone se bhi bachata hai (48h inactivity pe sleep hota hai).

**Done Checklist**
- [ ] `/health` aur `/ready` local me chal rahe hain
- [ ] Jaan-bujhkar error raise karke Sentry dashboard me dikha
- [ ] Sentry event me koi patient data/headers nahi hain
- [ ] UptimeRobot monitor green

**Antigravity prompt**
```
MLOPS_PLAN.md ke Phase 1 ko implement karo. Section 0 ke rules aur Section 3 ke privacy rules follow karo.
Pehle plan batao (kaunsi files change hongi), phir code likho.
Existing routers ka behaviour mat badlo. Naya branch: mlops/phase-1-safety-net.
Tests bhi likho: /health aur /ready ke liye pytest.
```

---

### PHASE 2 — Structured logging + `/metrics` + RAG metrics

**Goal:** System ke andar kya ho raha hai wo number me dikhe.

**Tasks**
1. JSON structured logging (`structlog` ya standard `logging` + JSON formatter). Har request ka log: `request_id`, `path`, `method`, `status`, `latency_ms`, `user_hash` (user_id nahi).
2. Middleware: har response me `X-Request-ID` header.
3. `prometheus-fastapi-instrumentator` se `/metrics` endpoint (default HTTP latency/status metrics).
   - `/metrics` ko secret header ya token se protect karo (`METRICS_TOKEN` env), warna public ho jayega.
4. Custom metrics (`prometheus_client`) — sirf **counts/latency**, content nahi:
   - `rag_request_total{status}`
   - `rag_retrieval_latency_seconds`
   - `rag_llm_latency_seconds` aur `rag_ttft_seconds` (first token time, agar streaming ho)
   - `groq_rate_limit_total` (429 count)
   - `semantic_cache_hit_total` / `semantic_cache_miss_total`
   - `bm25_cache_hit_total` / `bm25_cache_miss_total`
   - `rag_fallback_total` (jab fallback answer gaya)
   - `ocr_latency_seconds`, `model_predict_latency_seconds{model}`
   - `process_resident_memory_bytes` (default aata hai) — **RAM watch karo**, EasyOCR + PyTorch + FAISS heavy hain.
5. Heavy models (EasyOCR, BioBERT) **lazy load** karo ya startup pe ek baar, aur memory log karo. 16 GB me bhi leak ho sakta hai.

**Done Checklist**
- [ ] `curl -H "X-Metrics-Token: ..." /metrics` me custom metrics dikh rahe hain
- [ ] Logs JSON format me hain, kisi me patient data nahi
- [ ] Cache hit/miss counters sahi increment ho rahe hain (manual test)

**Antigravity prompt**
```
MLOPS_PLAN.md ke Phase 2 ko implement karo. Section 0 aur 3 follow karo.
RAG pipeline ke andar sirf timing/counter hooks add karo (decorator ya context manager), logic mat badlo.
Metrics me kabhi question text, answer text ya report content label/value ke roop me mat daalo.
Branch: mlops/phase-2-metrics.
```

---

### PHASE 3 — CI gate (test pass ho tabhi deploy)

**Goal:** Kharab code seedha production (HF Space) na jaye.

**Tasks**
1. `.github/workflows/ci.yml` (PR + push pe): Python setup → deps install (cache ke saath) → `ruff` (lint) → `pytest`.
2. Existing `deploy-hf.yml` ko **modify** karo (naya mat banao): sirf `main` pe, aur CI pass hone ke baad (`needs: test` ya `workflow_run`).
3. Secrets: `HF_TOKEN` GitHub Secrets me, workflow me hardcode nahi.
4. Tests ki basic list (`backend/tests/`):
   - `/health` 200
   - auth: signup/login flow (test DB ya mock)
   - diabetes predict: known input → valid output shape
   - model loading: `.pkl` files load hote hain
   - **LLM/Groq ko mock karo.** CI me real API call nahi (rate limit + cost + flaky).
5. `model_loader.py`: HF Hub se model load karte waqt **`revision=` pin karo** (tag ya commit hash), `main` nahi. Isse deploy reproducible hoga.
6. Branch protection (GitHub settings, manual): `main` pe CI pass hona mandatory.

**Done Checklist**
- [ ] Failing test wala PR merge nahi ho pa raha
- [ ] Deploy sirf CI green hone par chalta hai
- [ ] `model_loader.py` pinned revision use karta hai

**Antigravity prompt**
```
MLOPS_PLAN.md ke Phase 3 ko implement karo.
Existing .github/workflows/deploy-hf.yml ko modify karo, naya duplicate mat banao.
CI me koi real Groq/LLM call nahi honi chahiye, sab mock.
Branch: mlops/phase-3-ci-gate.
```

---

### PHASE 4 — RAG Golden Test Set (tumhara asli problem fix)

**Goal:** Jo issue tumne face kiya ("Dr kaun hai" pe poora clinical summary de diya), wo dobara aaye to **test fail ho**.

**Tasks**
1. `backend/tests/rag_golden/` banao:
   - `fake_report.pdf` ya `fake_report.txt` — **synthetic** report (fake naam jaise "Mr. Test Patient", fake doctors, fake values). Real patient data nahi.
   - `golden.json`:
```json
[
  {
    "question": "Patient ka naam kya hai?",
    "must_contain": ["Test Patient"],
    "max_words": 25
  },
  {
    "question": "Doctor kaun hai?",
    "must_contain": ["Dr."],
    "must_not_contain": ["anemia", "creatinine", "Clinical Summary"],
    "max_words": 40
  },
  {
    "question": "Hemoglobin kitna hai?",
    "must_contain": ["g/dL"],
    "max_words": 30
  },
  {
    "question": "Report ka detail me summary do",
    "min_words": 40
  },
  {
    "question": "Patient ko kaunsi bimari hai?",
    "must_contain_any": ["diagnos", "doctor"],
    "max_words": 60
  },
  {
    "question": "Patient ka blood group kya hai?",
    "must_contain_any": ["available nahi", "not available"],
    "max_words": 20
  }
]
```
2. `tests/test_rag_golden.py` ek runner jo har question RAG pipeline se chalaye aur checks kare: `must_contain`, `must_not_contain`, `max_words`, `min_words`.
3. Ye test **real LLM** use karta hai, isliye normal CI gate me nahi. Alag workflow `rag-eval.yml`: `workflow_dispatch` (manual) + weekly schedule. Rate limit se bachne ke liye questions ke beech 2–3 sec sleep.
4. Har run ka result (pass rate, average answer length) MLflow ya JSON artifact me save karo. System prompt badalne ke baad ye run karo, tabhi pata chalega prompt behter hua ya nahi.
5. System prompt ko code se alag file me rakho (`backend/prompts/rag_system_prompt.md`) aur usme version number likho (`PROMPT_VERSION = "v2"`), taki prompt change bhi "versioned" ho.

**Done Checklist**
- [ ] Golden test local me chalta hai, aur purana (lamba jawab dene wala) prompt pe fail hota hai
- [ ] Naya prompt pe pass rate >= 90%
- [ ] Prompt alag file me versioned hai

**Antigravity prompt**
```
MLOPS_PLAN.md ke Phase 4 ko implement karo.
Sirf synthetic/fake report use karo, koi real patient data repo me nahi aana chahiye.
Golden test runner banao jo RAG pipeline ko directly call kare. Ye test normal CI gate me nahi, alag manual+weekly workflow me chalega.
Branch: mlops/phase-4-rag-golden.
```

---

### PHASE 5 — Persistence fix (ephemeral disk problem)

**Goal:** Space restart hone par user ki uploaded reports aur vector index gayab na ho.

**Options (kam se zyada effort)**

| Option | Kaise | Pros | Cons |
|---|---|---|---|
| A. **Supabase Storage + pgvector** (meri recommendation) | PDFs → Supabase Storage bucket (private). Embeddings → Postgres `pgvector` extension. FAISS ki jagah SQL similarity search. | Pehle se Supabase use kar rahe ho, free tier, restart-proof, backups | FAISS → pgvector migration ka kaam, BM25 alag handle karna padega |
| B. Supabase Storage me FAISS index file save/load | Index banne ke baad `.faiss` file bucket me upload, startup/first-use pe download | Code kam badlega | Concurrency/sync issues, startup slow |
| C. HF Space persistent storage | Paid add-on | Sabse aasan | Free tier nahi |
| D. Rebuild on demand | PDF Supabase Storage me, index restart ke baad lazily rebuild | Simple | First query slow, CPU cost |

**Agent ko pehle ye karna hai:** Option A aur B/D ka comparison likhe (tumhare code ko dekh ke), tum choose karo, phir implement.

**Done Checklist**
- [ ] Space restart ke baad user apni purani report pe chat kar pa raha hai
- [ ] PDFs private bucket me hain (signed URL ya backend proxy se), public link nahi
- [ ] Per-user isolation test: user A user B ki report access nahi kar sakta

**Antigravity prompt**
```
MLOPS_PLAN.md ke Phase 5 ko pehle sirf ANALYSIS ke roop me karo: mere codebase (report_routes, chat_routes, vector store code) dekh ke Option A/B/D ka comparison do aur recommend karo. Abhi code mat likho. Mere approval ke baad hi implement karna.
```

---

### PHASE 6 — `train.py` + MLflow + Model Quality Gate

**Goal:** Notebook se reproducible training pipeline.

**Tasks**
1. Notebooks se logic nikaal ke `ml/train_diabetes.py` aur `ml/train_heart.py` (ya ek `train.py --model diabetes|heart`).
2. Config file (`ml/config.yaml`): data path, test_size, random_state, hyperparameters, threshold.
3. Datasets `data/` me (chhote public datasets, source/licence `data/README.md` me). DVC abhi nahi.
4. MLflow (DagsHub free tracking server):
   - env: `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, `MLFLOW_TRACKING_PASSWORD`
   - log: params, metrics (accuracy, **recall**, precision, ROC-AUC, F1), confusion matrix, model artifact, scaler, SHAP summary plot.
   - Medical screening me **recall (sensitivity)** ko priority do, sirf accuracy mat dekho.
5. **Quality gate:** naya model tabhi "promote" ho jab metrics threshold se upar ho aur current production model se kharab na ho (e.g. `recall >= 0.70` aur `roc_auc >= prod_roc_auc - 0.01`).
6. Promote = HF Hub (`samirk10/medical-ai-models`) pe push **with tag/version** (`diabetes-v1.1`). `model_loader.py` me us tag ko pin karo (Phase 3 se link).
7. Model card (`MODEL_CARD.md`): dataset, limitations (Pima = ek specific population), intended use, "not for diagnosis".
8. Manual workflow `train.yml` (`workflow_dispatch`).

**Done Checklist**
- [ ] `python ml/train.py --model diabetes` MLflow me run dikhata hai
- [ ] Quality gate fail hone par model HF Hub pe push nahi hota
- [ ] Production backend naye version tag se load hota hai

**Antigravity prompt**
```
MLOPS_PLAN.md ke Phase 6 ko implement karo. notebooks/ se existing preprocessing aur model logic ko faithfully train script me convert karo (same features, same scaler), warna prediction behaviour badal jayega.
Pehle verify karo ki naya script purane .pkl jaisi hi performance deta hai.
Branch: mlops/phase-6-training.
```

---

### PHASE 7 — Prediction logging + Evidently drift (weekly)

**Goal:** Pata chale ki real users ka data training data se alag to nahi ho raha.

**Tasks**
1. Supabase me table `prediction_logs`:
   `id, created_at, model_name, model_version, features (jsonb), prediction, probability, latency_ms`
   **user_id / naam / report content nahi.**
2. Predict endpoints me ek non-blocking log write (background task). Fail ho to user request fail na ho.
3. `ml/drift_report.py`:
   - Reference = training dataset, Current = last 7 din ke `prediction_logs`.
   - Evidently `DataDriftPreset` se HTML report + JSON summary.
   - Agar `current rows < 100` to "insufficient data" likh ke skip (low traffic me drift reliable nahi).
4. GitHub Actions weekly schedule (`drift.yml`): report generate → artifact upload → drift detect hua to Telegram alert.
5. User feedback (thumbs up/down on prediction/answer) ke liye `feedback` table — ye tumhara "ground truth ka substitute" hai.

**Done Checklist**
- [ ] Predict karne par `prediction_logs` me row aati hai (PII ke bina)
- [ ] `drift_report.py` local me HTML report banata hai
- [ ] <100 rows par graceful skip

**Antigravity prompt**
```
MLOPS_PLAN.md ke Phase 7 ko implement karo. prediction_logs me kisi bhi tarah ka user identifier ya patient data nahi jayega.
Evidently ki installed version ka documentation check karke API use karo.
Logging fail hone par predict endpoint fail nahi hona chahiye.
```

---

### PHASE 8 (Optional) — Grafana Cloud dashboards

Sirf tab karo jab Phase 1–7 stable ho. Grafana Cloud free + Grafana Alloy (ya remote_write) se `/metrics` push/scrape. Dashboards: request rate, p95 latency, error rate, RAM usage, cache hit ratio, Groq 429 count, RAG fallback rate.
HF Space pe extra agent RAM/CPU kha sakta hai, isliye pehle measure karo.

---

## 5. Alerting (Telegram Bot)

Setup (manual, 10 min): `@BotFather` se bot banao → token lo → bot ko message bhejo → chat_id nikalo.
Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

`backend/utils/alerts.py` me ek `send_alert(text)` helper (timeout 5 sec, fail ho to silently log).

| Alert | Source | Trigger |
|---|---|---|
| Space down / 503 | UptimeRobot (Telegram integration built-in) | 2 consecutive failed checks |
| Error spike | Sentry alert rule | >10 errors / 10 min |
| Groq rate limit | App metric | `groq_rate_limit_total` >5 / 10 min |
| High RAM | App check (background task) | RSS > 13 GB |
| Drift | `drift.yml` | Evidently drift detected |
| Golden RAG eval fail | `rag-eval.yml` | pass rate < 90% |
| Deploy failed | GitHub Actions | workflow failure |

Alerts me **koi patient data nahi**, sirf type + count + time.

---

## 6. Secrets / Env variables list

| Variable | Kahan set karna hai |
|---|---|
| `GROQ_API_KEY`, `DATABASE_URL`, `JWT_SECRET` | HF Space Secrets |
| `SENTRY_DSN`, `METRICS_TOKEN`, `USER_HASH_SALT` | HF Space Secrets |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | HF Space Secrets + GitHub Secrets |
| `HF_TOKEN` | GitHub Secrets (deploy + model push) |
| `MLFLOW_TRACKING_URI/USERNAME/PASSWORD` | GitHub Secrets (train workflow) |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | HF Space Secrets (service key **frontend me kabhi nahi**) |

`.env.example` me sirf variable names, values khali.

---

## 7. Cheat-sheet: Kya kya seekh rahe ho (MLOps ke terms)

- **Observability** = logs + metrics + traces. "System andar se kaisa hai?"
- **CI** = har push pe auto test. **CD** = test pass hone par auto deploy.
- **Model registry** = models ka versioned store (tumhare liye HF Hub + MLflow).
- **Data drift** = production input ka distribution training se alag ho gaya.
- **Quality gate** = metric threshold jo model/code ko promote hone se rokta hai.
- **Golden set** = fixed questions + expected behaviour, regression pakadne ke liye.
- **Prompt versioning** = system prompt ko bhi code ki tarah version karna.

---

## 8. Final Definition of Done

- [ ] Downtime ya error par 1–2 min me Telegram alert
- [ ] Kharab code deploy nahi ho sakta (CI gate)
- [ ] RAG ke "short answer" behaviour ka automated test hai
- [ ] Restart ke baad user data safe hai
- [ ] Model retrain → evaluate → gate → versioned push, ek command me
- [ ] Weekly drift report
- [ ] Koi patient data logs/Sentry/repo me leak nahi hota
