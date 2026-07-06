# Local Setup Guide (Without Docker)

This guide walks through running FirAI on your own machine without Docker —
useful for debugging the backend, the AI engine, or the frontend in isolation.

> For the quickest path, `docker compose up --build` from the repo root runs
> everything. Use this guide when you need to step through a service directly.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.10–3.12 | Backend + AI engine |
| Node.js | 18+ | Frontend (Vite) |
| PostgreSQL | 14+ | Primary datastore |
| Redis | 6+ | Caching layer (optional in dev) |
| Tesseract OCR | 5+ | Required for image/PDF FIR ingestion |

Platform notes:
- **Windows:** Install Tesseract from the UB-Mannheim build and add it to `PATH`.
  Install PostgreSQL via the EDB installer.
- **macOS:** `brew install tesseract postgresql redis`
- **Linux:** `sudo apt install tesseract-ocr libpq-dev postgresql redis-server`

---

## 1. Database

Create the database and user (match the defaults in `backend/config.py`):

```sql
CREATE USER firai WITH PASSWORD 'firai_secret';
CREATE DATABASE firai_db OWNER firai;
```

The app uses the async driver `postgresql+asyncpg`. Tables are created
automatically on first startup via `init_db()`; you do not run DDL by hand.

---

## 2. Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env` (all keys optional except the DB URL if you change it):

```env
DATABASE_URL=postgresql+asyncpg://firai:firai_secret@localhost:5432/firai_db
BHASHINI_API_KEY=
BHASHINI_USER_ID=
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Run the migrations (indexes + case-collaboration columns), then start the server:

```bash
python migrations/add_database_indexes.py
python migrations/add_case_features.py
uvicorn main:app --reload --port 8000
```

First boot is slow: it seeds demo officers + FIRs and warms up the embedding
model, the custom AI engine, the legal RAG index, and the legal LLM
(see the `lifespan` handler in `main.py`). Wait for `[FirAI] Backend ready!`.

API docs: <http://localhost:8000/docs>

### Demo login
Demo officers are seeded by `seed_officers.py`. Check that file for the seeded
badge numbers and passwords.

---

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

By default Vite serves on <http://localhost:3000> and proxies `/api` to the
backend. Override the API base with `VITE_API_URL` if your backend runs
elsewhere (see `frontend/src/api/client.js`).

---

## 4. Redis (optional in dev)

Caching degrades gracefully when Redis is absent (`services/cache_service.py`),
so you can skip it locally. To enable it, start Redis on its default port:

```bash
redis-server
```

---

## Troubleshooting

| Symptom | Cause / Fix |
|---------|-------------|
| `asyncpg` connection refused | PostgreSQL not running, or wrong `DATABASE_URL` |
| OCR returns empty narrative | Tesseract not installed or not on `PATH` |
| Backend hangs on startup | Model warmup — first run downloads model weights; wait it out |
| Frontend 401 loops to /login | Token expired/cleared; log in again |
| `vite: not recognized` | `node_modules` missing — run `npm install` in `frontend/` |
| Slow first AI inference | Model lazy-loads on first call; subsequent calls are fast |

See `DEVELOPER_GUIDE.md` for debugging workflows and `ARCHITECTURE.md` for how
the pieces fit together.
