# Developer Guide

Practical workflows for working on FirAI: debugging, testing, profiling, and
the common ways to extend the system. Read `ARCHITECTURE.md` first for the
mental model and `SETUP_LOCAL.md` to get running.

---

## Debugging

### Backend
- Run with reload and verbose logs:
  ```bash
  uvicorn main:app --reload --port 8000
  ```
- Logging is structured JSON via `logging_config.py`. Use the named loggers
  (`logger`, `auth_logger`, `audit_logger`) rather than `print()`.
- Inspect requests live at `/docs` (Swagger) — every endpoint is callable there
  with an "Authorize" button for the JWT.
- For a failing request, check `/api/metrics/errors` (admin) — `ErrorCatchingMiddleware`
  records exceptions with traceback + request context.
- Set a breakpoint with `import pdb; pdb.set_trace()` or use your IDE's attach-to
  -process against the uvicorn worker.

### Frontend
- `npm run dev` gives HMR. The axios client (`src/api/client.js`) auto-attaches
  the JWT and retries network errors while the backend warms up.
- A 401 clears the token and redirects to `/login` — if you're being bounced,
  your token expired (24h TTL).
- Use the browser Network tab; API base is `/api` (proxied) or `VITE_API_URL`.

---

## Testing

Tests live in `backend/tests/` (pytest, configured by `backend/pytest.ini`).

```bash
cd backend
pytest                      # run all
pytest -k auth              # filter by name
pytest --cov=. --cov-report=term-missing   # coverage
```

Write tests alongside the area you touch — API tests hit routers through an
async client; service tests exercise logic directly. See `TESTING_GUIDE.md`
for fixtures and patterns.

---

## Profiling

- **Slow endpoints:** `PerformanceMonitoringMiddleware` records latency to
  `performance_metrics`; query `/api/metrics/latency?component=api&operation=...`
  (admin). Anything over 5s is flagged as a performance warning in logs.
- **Slow queries:** set `echo=True` on the engine in `database.py` temporarily
  to see emitted SQL, then add an index in `migrations/add_database_indexes.py`.
- **Slow inference:** the AI engine logs timing; the first call to any model is
  slow (lazy load/warmup) — measure the second call.

---

## Common Extensions

### Add a new API endpoint
1. Add the route to the relevant file in `routers/` (or create a new router).
2. Define request/response shapes in `schemas/`.
3. Put logic in a `services/` module; keep the router thin.
4. If it's a new router, mount it in `main.py` and add a matching method to
   `frontend/src/api/client.js`.
5. Attach `Depends(require_officer)` (or `require_admin`) for protected routes.

### Add a new database table / column
- **New table:** define the model under `models/`, import it in
  `models/__init__.py` and in `main.py` (so `create_all` picks it up).
- **New column on an existing table:** add it to the model *and* write an
  `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` step in a migration script under
  `migrations/` (create_all does not alter existing tables). Pattern:
  `migrations/add_case_features.py`.

### Add a new AI model
1. Drop trained artifacts under `ai_engine/trained_models/` (see
   `LOCAL_MODEL_DIR` in `config.py`).
2. Wrap it in a service under `services/` exposing a clean async API and a
   `warmup()` function.
3. Warm it up in the `lifespan` handler in `main.py`.
4. Provide a graceful fallback (cf. `firai_engine._fallback_analysis`) so a
   model failure degrades instead of 500-ing.
5. Add tests covering the happy path and the fallback.

### Add a legal section to the corpus
- Legal data is served by `legal_kb.py` / `legal_rag.py`. Add the section to the
  underlying corpus/seed and re-run the RAG warmup so it gets re-encoded.

---

## Conventions

- **Async everywhere** in the backend — routers, services, and DB access use
  `async`/`await` with `AsyncSession`.
- **Services own logic, routers own HTTP.** Don't put DB queries with business
  rules directly in routers when a service is the right home.
- **No secrets in code.** Configuration flows through `config.py` / env vars.
- **Match the surrounding style** — section-comment banners, type hints,
  docstrings on public functions, and structured logging over prints.
- **Frontend:** functional components + hooks, the shared axios client for all
  calls, CSS variables (`var(--...)`) for theming so dark/light mode keeps
  working.

See `CONTRIBUTING.md` for the PR checklist and review process.
