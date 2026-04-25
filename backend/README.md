# FirAI Backend

> FastAPI backend for the Kerala Police AI Investigation Assistant.

---

## Overview

The backend provides all API endpoints for FIR management, AI analysis, legal guidance, and translation. It connects to PostgreSQL for data storage and integrates with Google Gemini and Bhashini APIs.

### Key Responsibilities

- **Authentication**: JWT-based secure routing, officer models, and registration requests
- **FIR Processing**: OCR extraction from PDFs → narrative extraction → structured data
- **Original PDF Storage**: Saves actual PDF files mapped to FIR records
- **AI Analysis**: Crime classification, risk scoring, IPC/BNS mapping (via Gemini)
- **Smart Similarity Search**: Multi-dimensional scoring (Narrative embeddings + accused matching + crime types)
- **MO Detection**: Cross-narrative pattern detection using DBSCAN clustering + Gemini
- **Legal Knowledge**: Built-in IPC/BNS section database + Gemini-powered Q&A
- **Translation**: Malayalam ↔ English via Bhashini API
- **Database Seeding**: Auto-imports 36 existing FIR JSONs and creates initial Admin users on first boot

---

## Project Structure

```
backend/
├── Dockerfile              # Python 3.11 + Tesseract OCR
├── requirements.txt        # Python dependencies
├── main.py                 # FastAPI app entry point
├── config.py               # Environment settings (Pydantic)
├── database.py             # SQLAlchemy async engine + session
├── seed.py                 # Seeds existing FIRs into PostgreSQL
│
├── models/                 # SQLAlchemy ORM Models
│   ├── __init__.py
│   └── fir.py              # FIR, Accused, MOPattern, LegalSection
│
├── schemas/                # Pydantic Request/Response Schemas
│   ├── __init__.py
│   └── fir.py              # All API schemas
│
├── routers/                # API Route Modules
│   ├── __init__.py
│   ├── auth.py             # JWT Login, registration requests, officer profiles
│   ├── firs.py             # FIR CRUD, upload, PDF download, analyze, similar cases
│   ├── dashboard.py        # Dashboard statistics
│   ├── legal.py            # Legal assistant (Gemini + KB)
│   ├── mo_patterns.py      # MO pattern detection
│   └── translate.py        # Bhashini translation
│
├── services/               # Business Logic Services
│   ├── __init__.py
│   ├── fir_processor.py    # PDF OCR → narrative extraction → structuring
│   ├── embedding_engine.py # Sentence-transformer embeddings + similarity
│   ├── gemini_service.py   # Google Gemini LLM integration
│   ├── legal_kb.py         # IPC/BNS section reference database
│   ├── mo_detector.py      # MO pattern detection (clustering + Gemini)
│   └── bhashini_service.py # Bhashini API translation
│
├── data/                   # FIR Data Files
│   ├── raw_pdfs/           # 36 original FIR PDF files
│   └── structured/         # 36 pre-processed FIR JSON files
│
└── storage/                # Pre-computed Data
    ├── embeddings.npy      # Narrative embeddings (NumPy)
    └── metadata.json       # Embedding metadata
```

---

## Database Models

### Officer & RegistrationRequest
Manages police officer identities, roles (admin vs standard), badge numbers, stations, and JWT authentication.

### FIR (Primary Table)

| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-increment ID |
| `narrative` | Text | **Core field** — FIR narrative (Malayalam or English) |
| `narrative_en` | Text | English translation of narrative |
| `narrative_ml` | Text | Malayalam original (if narrative is English) |
| `full_text` | Text | Full OCR-extracted text |
| `crime_type` | String | AI-classified crime type |
| `severity` | String | low / medium / high / critical |
| `risk_score` | Float | 1–10 risk score from AI |
| `summary_en` | Text | AI-generated English summary |
| `recommended_steps` | JSON | Investigation next steps |
| `key_entities` | JSON | Extracted entities (victims, accused, locations) |
| `acts` | JSON | [{act, sections}] |
| `complainant` | JSON | {name, father_name, dob} |
| `embedding_vector` | Binary | Narrative embedding for similarity search |

### Accused

Linked to FIR via `fir_id` foreign key. Stores name, father_name, dob, address.

### MOPattern

Stores detected MO patterns with linked FIR IDs and occurrence counts.

### LegalSection

Reference table for IPC/BNS sections with descriptions, bail/cognizable status.

---

## Services

### `fir_processor.py`
Refactored from the original `extract_text.py`, `clean_text.py`, and `structure_fir.py`. Provides:
- `extract_text_from_pdf(path)` — OCR extraction (Malayalam + English)
- `clean_text(text)` — Normalize whitespace, remove noise
- `extract_narrative(text)` — Extract Section 12 narrative
- `process_fir_pdf(path)` — Full pipeline: PDF → structured dict
- `process_fir_text(text)` — Process pasted text

### `embedding_engine.py`
Singleton `EmbeddingEngine` class with lazy model loading:
- `encode_narrative(text)` — Single narrative → embedding vector
- `find_similar(narrative, top_k)` — Find similar FIRs from storage
- `rebuild_store(fir_list)` — Rebuild embedding store

### `gemini_service.py`
Google Gemini 2.5 Flash integration with fallback:
- `analyze_narrative(text)` — Full AI analysis → crime type, severity, IPC sections, etc.
- `legal_query(question, context)` — Legal Q&A
- `detect_mo_patterns(narratives)` — Cross-narrative pattern detection
- `_fallback_analysis(text)` — Keyword-based fallback when API unavailable

### `legal_kb.py`
Built-in IPC (20+ sections) and BNS (15+ sections) reference:
- `lookup_section(act, section)` — Single section lookup
- `get_all_sections(act_filter)` — List all sections

### `bhashini_service.py`
- `translate_text(text, source_lang, target_lang)` — Bhashini API call

---

## Running Standalone (without Docker)

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set environment variables
set DATABASE_URL=postgresql+asyncpg://firai:firai_secret@localhost:5432/firai_db
set GEMINI_API_KEY=your_key

# Run
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> **Note**: Requires PostgreSQL running locally and Tesseract OCR installed.

---

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
