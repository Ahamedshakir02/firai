# FirAI Architecture

FirAI is an AI investigation assistant for the Kerala Police: it ingests FIR
documents (PDF / scanned images, Malayalam or English), extracts and analyzes
the narrative, and surfaces case intelligence — crime classification, similar
cases, legal guidance, and modus-operandi patterns.

---

## High-Level Components

```
                    ┌───────────────────────────────────────────┐
                    │                Frontend (React + Vite)     │
                    │  Dashboard · FIR Analyzer · Case Intel ·    │
                    │  Legal Assistant · MO Patterns · Translation│
                    └───────────────────────┬─────────────────────┘
                                             │  REST (/api/*), JWT bearer
                                             ▼
                    ┌───────────────────────────────────────────┐
                    │            Backend (FastAPI, async)         │
                    │  routers/  →  services/  →  models/ (ORM)    │
                    │  middleware: logging · errors · perf        │
                    └───────┬───────────────────────┬─────────────┘
                            │                       │
                ┌───────────▼─────────┐   ┌─────────▼──────────┐
                │   PostgreSQL         │   │   Redis (cache)     │
                │  (asyncpg, SQLAlc.)  │   │  legal/embeddings   │
                └──────────────────────┘   └────────────────────┘
                            │
                ┌───────────▼───────────────────────────────────┐
                │              AI Engine (in-process)             │
                │  embedding_engine · firai_engine · legal_rag ·  │
                │  legal_llm · mo_detector · fir_processor (OCR)  │
                └─────────────────────────────────────────────────┘
```

Everything runs in-process: the AI models load into the FastAPI worker at
startup (`main.py` `lifespan`), so there is no separate model-serving tier.

---

## Backend Layout (`backend/`)

| Layer | Path | Responsibility |
|-------|------|----------------|
| Entrypoint | `main.py` | App wiring, CORS, middleware, model warmup, router mounting |
| Routers | `routers/` | HTTP endpoints (thin; delegate to services) |
| Services | `services/` | Business logic, AI orchestration, caching, audit |
| Models | `models/` | SQLAlchemy ORM tables |
| Schemas | `schemas/` | Pydantic request/response contracts |
| AI engine | `ai_engine/` | Trained models + generative legal LLM |
| Config | `config.py` | Settings via env vars (pydantic-settings) |
| Middleware | `middleware.py` | Structured logging, error catching, perf metrics |

### Routers
- `auth.py` — JWT login, registration requests, admin approval. Exposes
  `require_officer` / `require_admin` dependencies used across the app.
- `firs.py` — upload (PDF/image), analyze, similarity search, bulk import,
  download, export.
- `dashboard.py` — aggregate crime statistics.
- `legal.py` — IPC/BNS section lookup, RAG-backed legal Q&A, punishment calc.
- `mo_patterns.py` — modus-operandi detection across narratives.
- `translate.py` — Malayalam ↔ English (Bhashini, optional).
- `monitoring.py` — metrics, error tracking, audit trails, security events.
- `cases.py` — notes/annotations, bulk actions, case timeline, notifications.

### Key services
- `embedding_engine.py` — multilingual sentence embeddings (384-dim) for
  narrative similarity; vectors stored as `LargeBinary` on the FIR row.
- `firai_engine.py` — custom classifier: crime type, severity, summary,
  recommended steps, key entities (with a `_fallback_analysis` path).
- `fir_processor.py` — document → narrative + metadata (OCR for images/PDF).
- `legal_rag.py` / `legal_kb.py` — semantic search over the legal corpus.
- `mo_detector.py` — clusters narratives into recurring MO patterns.
- `cache_service.py` — Redis caching with graceful fallback.
- `audit_service.py` / `advanced_audit.py` — compliance + audit logging.
- `case_service.py` — timeline events + officer notifications.
- `rate_limiter.py` — per-IP login/registration throttling.

---

## Data Model

```
officers ──< audit_logs                 firs ──< accused
   │                                      │
   │                                      ├──< fir_notes        (annotations)
   ├──< notifications >── firs            ├──< case_events      (timeline)
   │                                      └─ status, tags       (workflow)
registration_requests

mo_patterns        legal_sections
error_logs · performance_metrics · security_events   (observability)
```

- **FIR** is the core entity: narrative (original + translations), AI-derived
  fields (crime type, severity, summary, entities, acts), an embedding vector,
  plus workflow `status` and `tags`.
- **Accused** rows hang off a FIR (cascade delete) and drive repeat-offender
  matching in similarity search.
- **FIRNote / CaseEvent / Notification** power collaboration: annotations, the
  per-case timeline, and the in-app alert bell.
- **AuditLog / ErrorLog / PerformanceMetric / SecurityEvent** are the
  observability tables fed by middleware and services.

Tables are created by `Base.metadata.create_all` at startup. Columns added to
pre-existing tables (e.g. `firs.status`, `firs.tags`) need the migration script
`migrations/add_case_features.py`.

---

## Request Lifecycle (upload → intelligence)

```
1. Officer uploads a FIR (PDF/image)        POST /api/firs/upload-pdf
2. fir_processor OCRs + extracts narrative, metadata, accused
3. firai_engine analyzes → crime type, severity, summary, steps, entities
4. _find_duplicate guards against re-ingesting the same FIR
5. embedding_engine encodes the narrative → stored on the row
6. FIR + Accused persisted; a `created` case_event is logged
7. _find_similar_in_db returns multi-dimensional matches
   (narrative cosine 60% + crime-type 20% + accused match 20%)
8. Response → frontend renders analysis + similar cases
```

Subsequent collaboration (notes, status changes, tags) appends `case_events`,
and MO pattern detection raises `notifications` for the officer.

---

## Cross-Cutting Concerns

- **Auth:** JWT bearer tokens (`routers/auth.py`); most routers attach
  `Depends(require_officer)` at the router level.
- **Caching:** hot reads (legal sections, embeddings, similarity, stats) are
  cached in Redis with TTLs; misses fall through to PostgreSQL.
- **Observability:** middleware logs every request as structured JSON, records
  latency, and captures errors; surfaced via `/api/metrics/*`.
- **Security:** rate limiting, input validation (`validators.py`), CSRF tokens
  (`csrf_protection.py`), and audit trails.

See `DEVELOPER_GUIDE.md` for how to extend each layer.
