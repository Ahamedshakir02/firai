# FirAI Backend

> FastAPI backend for the Kerala Police AI Investigation Assistant.

---

## Overview

The backend provides all API endpoints for FIR management, AI analysis, legal guidance, and translation. It connects to PostgreSQL for data storage and uses a **100% custom-built AI engine** (FirAI Engine) — no external AI APIs.

### Key Responsibilities

- **Authentication**: JWT-based secure routing, officer models, and registration requests
- **FIR Processing**: OCR extraction from PDFs → narrative extraction → structured data
- **Auto File Naming**: Uploaded PDFs are automatically renamed to `FIR_{number}_{year}_{station}.pdf`
- **Duplicate Detection**: File-hash and FIR-number based deduplication on upload
- **Original PDF Storage**: Saves actual PDF files mapped to FIR records with proper names
- **AI Analysis**: Crime classification, risk scoring, IPC/BNS mapping (via custom FirAI Engine)
- **Smart Similarity Search**: Multi-dimensional scoring (Narrative embeddings + accused matching + crime types)
- **MO Detection**: Cross-narrative pattern detection using DBSCAN clustering
- **Legal Knowledge**: Built-in IPC/BNS section database + AI-powered Q&A
- **Translation**: Malayalam ↔ English via Bhashini API
- **Database Seeding**: Auto-imports 90+ existing FIR JSONs and creates initial Admin users on first boot

---

## Project Structure

```
backend/
├── Dockerfile              # Python 3.11 + Tesseract OCR (mal+eng)
├── requirements.txt        # Python dependencies
├── main.py                 # FastAPI app entry point
├── config.py               # Environment settings (Pydantic)
├── database.py             # SQLAlchemy async engine + session
├── seed.py                 # Seeds existing FIRs into PostgreSQL (auto-names)
├── seed_officers.py        # Seeds demo officer accounts
│
├── scripts/                # 🔧 Data Management Utilities
│   ├── rename_firs.py      # Rename existing JSONs/PDFs to FIR_XXXX_YYYY_STATION
│   └── reprocess_all_firs.py  # Wipe & re-OCR all PDFs (dedup + auto-name)
│
├── models/                 # SQLAlchemy ORM Models
│   ├── fir.py              # FIR, Accused, MOPattern, LegalSection
│   └── officer.py          # Officer, RegistrationRequest
│
├── schemas/                # Pydantic Request/Response Schemas
│   └── fir.py              # All API schemas
│
├── routers/                # API Route Modules
│   ├── auth.py             # JWT Login, registration requests, officer profiles
│   ├── firs.py             # FIR CRUD, upload (auto-name), PDF download, analyze, similar cases
│   ├── dashboard.py        # Dashboard statistics
│   ├── legal.py            # Legal assistant (custom AI + KB)
│   ├── mo_patterns.py      # MO pattern detection
│   └── translate.py        # Bhashini translation
│
├── services/               # Business Logic Services
│   ├── firai_engine.py     # 🧠 Custom AI engine (crime classification, legal mapping)
│   ├── fir_processor.py    # PDF OCR → extraction → auto-naming (generate_fir_filename)
│   ├── embedding_engine.py # Sentence-transformer embeddings + similarity
│   ├── legal_kb.py         # IPC/BNS section reference database
│   ├── mo_detector.py      # MO pattern detection (DBSCAN clustering)
│   └── bhashini_service.py # Bhashini API translation
│
├── ai_engine/              # 🧠 Custom AI System
│   ├── data/
│   │   ├── label_generator.py   # Auto-derives labels from IPC/BNS
│   │   ├── legal_corpus.py      # Indian law text (IPC, BNS, CrPC)
│   │   └── datasets/            # Generated training data
│   ├── models/
│   │   └── classifier.py        # BiLSTM neural network architecture
│   ├── inference/               # Model loading & prediction
│   └── trained_models/          # Saved model weights
│       ├── classifier.pt        # Trained neural network (3.3 MB)
│       └── classifier_vocab.pkl # Vocabulary (32 KB)
│
├── training/
│   └── train_classifier.py      # Training script (Colab/local)
│
├── data/                   # FIR Data Files
│   ├── raw_pdfs/           # 90+ FIR PDF files (auto-named: FIR_XXXX_YYYY_STATION.pdf)
│   └── structured/         # 90+ structured FIR JSON files (auto-named)
│
└── storage/                # Pre-computed Data
    ├── embeddings.npy      # Narrative embeddings (NumPy)
    └── metadata.json       # Embedding metadata
```

---

## FIR File Naming Convention

All FIR files are automatically named using the format: `FIR_{number}_{year}_{station}`

### Examples

| Original Upload Name | Auto-Generated Name |
|---|---|
| `2lSpMsBKiu1d3sNkoB_20260405134040..pdf` | `FIR_0314_2026_CHITTOOR.pdf` |
| `scan_page1.pdf` | `FIR_0517_2024_KALPAKANCHERRY.pdf` |
| `FIR_unknown.pdf` (if extraction fails) | `FIR_unknown.pdf` (fallback) |

### How It Works

The `generate_fir_filename()` function in `fir_processor.py` extracts the FIR number and police station from the OCR'd text and generates the filename. This runs automatically:
- During **PDF upload** (single and bulk)
- During **database seeding** (first boot)
- Via **`scripts/rename_firs.py`** (batch rename existing files)
- Via **`scripts/reprocess_all_firs.py`** (full re-OCR from scratch)

---

## Database Models

### Officer & RegistrationRequest
Manages police officer identities, roles (admin vs standard), badge numbers, stations, and JWT authentication.

### FIR (Primary Table)

| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-increment ID |
| `file_name` | String | Auto-generated filename (e.g. `FIR_0517_2024_KALPAKANCHERRY.pdf`) |
| `fir_number` | String | Extracted FIR number (e.g. `0517/2024`) |
| `narrative` | Text | **Core field** — FIR narrative (Malayalam or English) |
| `narrative_en` | Text | English translation of narrative |
| `narrative_ml` | Text | Malayalam original (if narrative is English) |
| `full_text` | Text | Full OCR-extracted text |
| `district` | String | District name (e.g. `MALAPPURAM`) |
| `police_station` | String | Police station (e.g. `KOTTAKKAL`) |
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
Complete FIR processing pipeline with auto-naming:
- `extract_text_from_pdf(path)` — OCR extraction (Malayalam + English)
- `clean_text(text)` — Normalize whitespace, remove noise
- `extract_narrative(text)` — Extract Section 12 narrative
- `extract_fir_number(text)` — Extract FIR number (e.g. `0517/2024`)
- `extract_district_and_station(text)` — Extract district and police station
- `extract_acts(text)` — Extract legal acts and sections
- `extract_complainant(text)` — Extract complainant details
- `extract_accused(text)` — Extract accused persons
- `generate_fir_filename(...)` — **Generate standardized filename from extracted metadata**
- `process_fir_pdf(path)` — Full pipeline: PDF → structured dict
- `process_fir_text(text)` — Process pasted text

### `firai_engine.py`
Custom AI engine (100% offline, no external APIs):
- `analyze_narrative(text)` — Full AI analysis → crime type, severity, IPC sections, etc.
- `legal_query(question, context)` — Legal Q&A from Indian law corpus
- `detect_mo_patterns(narratives)` — Cross-narrative pattern detection
- `_fallback_analysis(text)` — Keyword-based analysis

### `embedding_engine.py`
Singleton `EmbeddingEngine` class with lazy model loading:
- `encode_narrative(text)` — Single narrative → embedding vector
- `find_similar(narrative, top_k)` — Find similar FIRs from storage
- `rebuild_store(fir_list)` — Rebuild embedding store

### `legal_kb.py`
Built-in IPC (20+ sections) and BNS (15+ sections) reference:
- `lookup_section(act, section)` — Single section lookup
- `get_all_sections(act_filter)` — List all sections

### `bhashini_service.py`
- `translate_text(text, source_lang, target_lang)` — Bhashini API call

---

## Data Management Scripts

### `scripts/rename_firs.py`
Renames existing JSON/PDF files to standardized FIR names based on content:
```bash
python scripts/rename_firs.py           # Dry run (preview)
python scripts/rename_firs.py --apply   # Apply renames
```

### `scripts/reprocess_all_firs.py`
Nuclear option — deletes all structured JSONs, removes duplicate PDFs, and re-processes every PDF from scratch:
```bash
python scripts/reprocess_all_firs.py           # Dry run (preview)
python scripts/reprocess_all_firs.py --apply   # Full reprocess
```

Features:
- MD5 hash-based duplicate PDF detection
- FIR number-based content duplicate detection
- Auto-renames PDFs to proper FIR names after processing
- Collision handling for same FIR number edge cases

> **Requires**: Tesseract OCR with Malayalam language data (`mal.traineddata`)

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

# Run
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> **Note**: Requires PostgreSQL running locally and Tesseract OCR installed with Malayalam language data.

---

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
