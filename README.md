# FirAI — Kerala Police AI Investigation Assistant

> AI-powered investigation assistant built for Kerala Police officers — providing real-time FIR analysis, case intelligence, legal guidance, and multilingual support using a **100% custom-built AI engine**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Custom AI](https://img.shields.io/badge/AI-Custom%20Built-ff6b6b?logo=pytorch)

---

## Table of Contents

1. [Overview](#-overview)
2. [FirAI Engine — Custom AI](#-firai-engine--custom-ai)
3. [Architecture](#️-architecture)
4. [Prerequisites](#-prerequisites)
5. [Step 1 — Install Docker](#step-1--install-docker)
6. [Step 2 — Clone the Repository](#step-2--clone-the-repository)
7. [Step 3 — Configure Environment](#step-3--configure-environment)
8. [Step 4 — Train the AI Model](#step-4--train-the-ai-model)
9. [Step 5 — Run the Project](#step-5--run-the-project)
10. [Verify Everything Works](#-verify-everything-works)
11. [Features](#-features)
12. [Project Structure](#-project-structure)
13. [Environment Variables](#-environment-variables)
14. [API Endpoints](#️-api-endpoints)
15. [Common Issues & Fixes](#-common-issues--fixes)
16. [Tech Stack](#-tech-stack)

---

## Overview

Kerala Police officers face fragmented processes when accessing FIRs, case updates, and legal procedures. **FirAI** solves this with an AI-powered investigation dashboard that:

- **Parses FIR narratives** (Malayalam & English) and classifies crimes with relevant IPC/BNS sections
- **Finds similar past cases** using multi-dimensional smart similarity (narrative embeddings + accused identity matching + crime type filtering)
- **Detects Modus Operandi (MO) patterns** across FIRs to identify recurring crime methods
- **Provides AI legal guidance** via a built-in Indian legal knowledge base, with optional Claude AI for conversational answers
- **Protects sensitive data** via JWT-based officer authentication and a registration portal with admin approval
- **Centralises all FIR data** with original PDF document storage and retrieval
- **Auto-names and deduplicates** uploaded FIR files using extracted metadata (FIR number, year, police station)
- **Translates narratives** between Malayalam and English via Bhashini API

### Core Principle: Narrative-Centric

The **FIR narrative** (Section 12 — First Information Contents) is the backbone of the entire system. All AI analysis, similarity search, crime classification, and pattern detection flows from the narrative text.

---

## FirAI Engine — Custom AI

FirAI uses a **100% custom-built AI system** called **FirAI Engine**. Every model is designed, trained, and owned by this project. Classification, summarization, entity extraction, and legal mapping all run offline with no external API calls.

### How It Works

The AI learns directly from **Indian law texts** (IPC, BNS, CrPC, BNSS, Kerala Police Act) and real Kerala Police FIR data. Training labels are derived automatically from the IPC/BNS section numbers present in the FIRs themselves — no external AI is used to generate training data.

For conversational legal Q&A, FirAI optionally integrates with **Anthropic's Claude API**. If no API key is configured, all legal questions are answered from the built-in structured knowledge base.

### Custom Models

| # | Model | Architecture | What It Does |
|---|---|---|---|
| 1 | **FirClassifier** | BiLSTM + Attention Neural Network | Crime type + severity classification |
| 2 | **FirNER** | Regex + Custom Extraction Pipeline | Entity extraction (names, locations, vehicles, amounts) |
| 3 | **FirSummarizer** | TextRank + Template Engine | English narrative summarization |
| 4 | **FirLegalMapper** | IPC/BNS Section Lookup + TF-IDF | IPC/BNS section prediction from acts data |
| 5 | **FirLegalLLM** | Claude API (optional) + Knowledge Base | Conversational Legal Q&A with RAG |

### Training Data & Context

- **90+ real Kerala Police FIRs** (Malayalam narratives) from 10+ police stations across Kerala
- **Indian Legal Corpus** — Comprehensive knowledge base with elements, punishments, bail status, and investigation steps for IPC, BNS, NDPS, POCSO, MVA, and Kerala Abkari Act sections
- **IPC to BNS Transition Map** — Accurate cross-referencing between the Indian Penal Code (1860) and Bharatiya Nyaya Sanhita (2023)
- **Section-derived classification** — Crime type and severity are derived deterministically from the actual IPC/BNS sections in each FIR, falling back to the neural classifier when no section data is available

### Performance

| Metric | Score |
|---|---|
| Crime classification accuracy | **98.8%** |
| Severity classification accuracy | **98.8%** |
| Model size | **3.3 MB** |
| Inference time | **< 100ms** on CPU |
| Internet required at runtime | **No** (Claude API is optional) |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Docker Compose                       │
│                                                          │
│  ┌──────────┐    ┌──────────────────┐   ┌─────────────┐  │
│  │ Frontend │    │     Backend      │   │  PostgreSQL │  │
│  │  React   │◄──►│    FastAPI       │◄─►│     16      │  │
│  │  :3000   │    │    :8000         │   │   :5432     │  │
│  └──────────┘    └────────┬─────────┘   └─────────────┘  │
│                           │                              │
│              ┌────────────┼────────────┐                 │
│              ▼            ▼            ▼                 │
│          FirAI         Bhashini    Sentence              │
│          Engine          API      Transformers           │
│       (Custom AI)    (Translate)  (Embeddings)           │
│                           │                              │
│                    ┌──────▼──────┐                       │
│                    │  Claude API │ (optional)            │
│                    │  Legal Q&A  │                       │
│                    └─────────────┘                       │
└──────────────────────────────────────────────────────────┘
```

### AI Pipeline

```
FIR Narrative (Malayalam/English)
        │
        ├──► Section-Derived Labeler ──► Crime Type + Severity (primary)
        ├──► FirClassifier (BiLSTM) ──── Crime Type + Severity (fallback)
        ├──► FirNER (Regex/Patterns) ──► Entities (names, vehicles, amounts)
        ├──► FirSummarizer (TextRank) ── English Summary
        ├──► FirLegalMapper ──────────── Applicable IPC/BNS Sections
        └──► Legal Corpus / Claude API ► Investigation Recommendations + Q&A
```

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Docker Desktop** | Includes Docker Engine + Docker Compose |
| **Git** | To clone the repository |
| **Python 3.11+** | Only needed if training the AI model locally |
| **Anthropic API Key** | Optional — enables AI-powered legal chat (free to start at console.anthropic.com) |
| **Bhashini API Key** | Optional — only needed for Malayalam translation |

> **Minimum system:** 4 GB RAM, 10 GB free disk space (for Docker images + ML models)

---

## Step 1 — Install Docker

Docker Desktop bundles everything you need (Docker Engine + Docker Compose).

### Windows

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Run the installer — accept defaults.
3. When prompted, enable **WSL 2** (recommended).
4. Restart your computer after installation.
5. Open Docker Desktop from the Start menu. Wait for **"Engine running"** (green icon in taskbar).
6. Verify in PowerShell:
   ```powershell
   docker --version
   docker compose version
   ```

### macOS

1. Download Docker Desktop:
   - Apple Silicon (M1/M2/M3): https://desktop.docker.com/mac/main/arm64/Docker.dmg
   - Intel: https://desktop.docker.com/mac/main/amd64/Docker.dmg
2. Open the `.dmg` and drag Docker to Applications.
3. Launch Docker from Applications. Grant permissions if asked.
4. Verify in Terminal:
   ```bash
   docker --version
   docker compose version
   ```

### Linux (Ubuntu / Debian)

```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
sudo systemctl enable --now docker
```

---

## Step 2 — Clone the Repository

```bash
git clone https://github.com/Ahamedshakir02/firai.git
cd firai
```

> **Don't have Git?**
> - Windows: https://git-scm.com/download/win
> - macOS: `xcode-select --install`
> - Linux: `sudo apt-get install git`

---

## Step 3 — Configure Environment

### 3a. Create your `.env` from the template

```bash
# Windows (PowerShell)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

> This step is required. The project will not start without a `.env` file.

### 3b. Edit `.env`

```bash
# Windows
notepad .env

# macOS / Linux
nano .env
```

The default configuration works out of the box. The only value you need to add is an Anthropic API key if you want AI-powered legal chat:

```env
# Database — leave unchanged, Docker handles it
POSTGRES_USER=firai
POSTGRES_PASSWORD=firai_secret
POSTGRES_DB=firai_db
DATABASE_URL=postgresql+asyncpg://firai:firai_secret@db:5432/firai_db

# Claude API — optional, enables AI-powered Legal Assistant
# Get your key at https://console.anthropic.com
ANTHROPIC_API_KEY=
CLAUDE_MODEL=claude-haiku-4-5-20251001

# Translation — optional, for Malayalam ↔ English
BHASHINI_API_KEY=
BHASHINI_USER_ID=
```

> Without `ANTHROPIC_API_KEY`, the Legal Assistant still works — it answers queries from the built-in IPC/BNS knowledge base.

### 3c. Get an Anthropic API Key (optional)

1. Sign up at https://console.anthropic.com
2. Go to **API Keys** and create a new key
3. Paste it as `ANTHROPIC_API_KEY=sk-ant-...` in your `.env`

### 3d. Get a Bhashini API Key (optional, for translation)

1. Register at https://bhashini.gov.in/ulca/user-profile
2. Go to **My Profile → API Keys**
3. Copy your **API Key** and **User ID** into `.env`

---

## Step 4 — Train the AI Model

FirAI includes a custom neural network that needs to be trained on the FIR data. Training takes ~5 minutes on CPU.

### Option A: Train Locally

```bash
cd backend
pip install torch scikit-learn numpy
python training/train_classifier.py --epochs 50
```

### Option B: Train on Google Colab (Free GPU)

1. Upload the `backend/` folder to Colab
2. Run:
   ```python
   !pip install torch scikit-learn numpy
   !python training/train_classifier.py --epochs 50 --data_dir ./data/structured
   ```
3. Download `ai_engine/trained_models/classifier.pt` and `classifier_vocab.pkl`

### What Training Produces

```
ai_engine/trained_models/
├── classifier.pt          # 3.3 MB — trained neural network weights
└── classifier_vocab.pkl   # 32 KB — vocabulary (Malayalam + English tokens)
```

> **Pre-trained model included:** The repository ships with a pre-trained model — you can skip this step and go straight to Step 5.

---

## Step 5 — Run the Project

Make sure Docker Desktop is running, then from the project root:

```bash
docker compose up --build
```

### What happens on first run

| Step | What it does | Time |
|---|---|---|
| Build | Downloads base images, installs Python + npm packages | 3–8 min |
| Database | PostgreSQL initialises with `firai_db` | ~10 sec |
| Backend | FastAPI starts, loads AI models, seeds 90+ FIRs | 1–2 min |
| Frontend | Vite dev server starts | ~15 sec |

> Subsequent runs (without `--build`) start in under 30 seconds.

### Running in detached mode

```bash
docker compose up --build -d
```

View logs:
```bash
docker compose logs -f           # all services
docker compose logs -f backend   # backend only
docker compose logs -f frontend  # frontend only
```

### Stopping

```bash
docker compose down              # stops containers, keeps database
docker compose down -v           # stops containers and deletes database (fresh start)
```

---

## Verify Everything Works

| Service | URL | Expected |
|---|---|---|
| **Dashboard** | http://localhost:3000 | Kerala Police FirAI dashboard |
| **Backend API** | http://localhost:8000/api/health | `{"status": "healthy"}` |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |

You should see **90+ FIRs** already loaded in the Case Intelligence page, sorted by real case numbers (e.g. `Case 0008/2025`).

---

## Features

| Feature | Page | Description |
|---|---|---|
| **Authentication** | `/login` | JWT-protected access with badge number + password login |
| **Officer Profile** | `/profile` | View officer details, admin panel for managing registration requests |
| **Registration Portal** | `/login` (register tab) | New officer registration with admin approval workflow |
| **Dashboard** | `/` | Crime stats, severity breakdown, monthly trends, recent FIRs |
| **FIR Analyzer** | `/fir-analyzer` | Upload PDF or paste narrative — AI classifies crime, extracts sections, suggests investigation steps |
| **Case Intelligence** | `/case-intelligence` | Browse and search FIRs by crime type and police station; multi-dimensional similarity search with PDF downloads |
| **Legal Assistant** | `/legal-assistant` | AI legal chat (Claude API or knowledge-base fallback), IPC ↔ BNS Cross-Mapper, multi-charge Punishment Calculator |
| **MO Patterns** | `/mo-patterns` | Detect recurring modus operandi across all FIR narratives |
| **Translation** | `/translation` | Translate FIR text between Malayalam and English |

---

## Project Structure

```
firai/
├── docker-compose.yml         # Orchestrates all 3 services
├── .env                       # Your config (never commit this)
├── .env.example               # Template for environment variables
│
├── backend/                   # Python / FastAPI
│   ├── Dockerfile
│   ├── main.py                # App entry point, startup hooks
│   ├── config.py              # Settings loaded from .env
│   ├── database.py            # SQLAlchemy async engine + session
│   ├── seed.py                # Seeds existing FIRs on first boot
│   ├── seed_officers.py       # Seeds demo officer accounts
│   ├── requirements.txt
│   ├── scripts/
│   │   ├── extract_rules.py       # Extract IPC/BNS sections from PDF law texts
│   │   ├── rename_firs.py         # Rename JSONs/PDFs to FIR_XXXX_YYYY_STATION format
│   │   └── reprocess_all_firs.py  # Wipe & re-OCR all PDFs (dedup + auto-name)
│   ├── ai_engine/             # Custom AI System
│   │   ├── data/
│   │   │   ├── label_generator.py   # Derives crime labels from IPC/BNS sections
│   │   │   ├── legal_corpus.py      # Indian law knowledge base (IPC, BNS, CrPC)
│   │   │   └── datasets/            # Generated training data
│   │   ├── models/
│   │   │   ├── classifier.py        # BiLSTM neural network architecture
│   │   │   └── legal_llm.py         # Claude API integration + knowledge-base fallback
│   │   ├── inference/               # Model loading & prediction
│   │   └── trained_models/          # Saved model weights
│   │       ├── classifier.pt        # Trained neural network (3.3 MB)
│   │       └── classifier_vocab.pkl # Vocabulary (32 KB)
│   ├── training/
│   │   └── train_classifier.py      # Training script (Colab/local)
│   ├── models/
│   │   ├── fir.py             # FIR, Accused, MOPattern, LegalSection ORM models
│   │   └── officer.py         # Officer, RegistrationRequest ORM models
│   ├── routers/
│   │   ├── auth.py            # JWT auth, registration, admin approval
│   │   ├── firs.py            # FIR upload, analysis, similarity, export
│   │   ├── dashboard.py       # Statistics endpoint
│   │   ├── legal.py           # Legal Q&A, section lookup, IPC↔BNS mapping
│   │   ├── mo_patterns.py     # MO pattern detection
│   │   └── translate.py       # Translation endpoint
│   ├── schemas/
│   │   └── fir.py             # Pydantic request/response schemas
│   ├── services/
│   │   ├── firai_engine.py    # Main AI service — classification, legal Q&A, MO detection
│   │   ├── embedding_engine.py# Sentence-Transformer similarity search
│   │   ├── fir_processor.py   # PDF OCR + field extraction + auto-naming
│   │   ├── bhashini_service.py# Malayalam translation (Bhashini + Google fallback)
│   │   ├── legal_kb.py        # IPC/BNS knowledge base service
│   │   └── mo_detector.py     # MO pattern detection logic
│   ├── storage/               # Runtime file storage
│   └── data/
│       ├── raw_pdfs/          # Original FIR PDF documents
│       ├── structured/        # Structured FIR JSON files
│       └── rules/             # Extracted legal rules (extracted_rules.json)
│
└── frontend/                  # React / Vite
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── main.jsx           # App entry point
        ├── App.jsx            # Router setup + ProtectedRoute
        ├── index.css          # Global design system (dark theme, responsive)
        ├── api/
        │   └── client.js      # Axios API client (all endpoints + JWT interceptor)
        ├── context/
        │   └── AuthContext.jsx # Authentication context provider
        ├── components/
        │   └── Layout/
        │       ├── Layout.jsx  # App shell with mobile sidebar toggle
        │       ├── Sidebar.jsx # Navigation sidebar (slide-in on mobile)
        │       └── Header.jsx  # Top bar with hamburger menu on mobile
        └── pages/
            ├── Login.jsx
            ├── Profile.jsx
            ├── Dashboard.jsx
            ├── FIRAnalyzer.jsx
            ├── CaseIntelligence.jsx
            ├── LegalAssistant.jsx
            ├── MOPatterns.jsx
            └── Translation.jsx
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `POSTGRES_USER` | Yes | `firai` | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | `firai_secret` | PostgreSQL password |
| `POSTGRES_DB` | Yes | `firai_db` | Database name |
| `DATABASE_URL` | Yes | *(see .env)* | Full async connection string |
| `ANTHROPIC_API_KEY` | No | — | Claude API key — enables AI-powered legal chat |
| `CLAUDE_MODEL` | No | `claude-haiku-4-5-20251001` | Claude model to use for legal Q&A |
| `BHASHINI_API_KEY` | No | — | Bhashini API for Malayalam ↔ English translation |
| `BHASHINI_USER_ID` | No | — | Bhashini user ID |
| `GOOGLE_MAPS_API_KEY` | No | — | Reserved for future map integration |

> Without `ANTHROPIC_API_KEY`, legal queries are answered from the built-in IPC/BNS knowledge base — no functionality is lost, only conversational AI responses are unavailable.

---

## API Endpoints

The full interactive API docs are at **http://localhost:8000/docs** when running.

### Authentication (Public)

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | `GET` | Health check with service status |
| `/api/auth/login` | `POST` | Authenticate officer — returns JWT |
| `/api/auth/register-request` | `POST` | Submit officer registration request |

### Authentication (Protected)

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/me` | `GET` | Get current officer profile |
| `/api/auth/registration-requests` | `GET` | Admin: list all registration requests |
| `/api/auth/registration-requests/{id}/approve` | `POST` | Admin: approve a request |
| `/api/auth/registration-requests/{id}/reject` | `POST` | Admin: reject a request |

### FIRs (All protected)

| Endpoint | Method | Description |
|---|---|---|
| `/api/firs` | `GET` | List FIRs — filter by `crime_type`, `police_station`, `severity`, `search` |
| `/api/firs/{id}` | `GET` | Full FIR details with accused |
| `/api/firs/{id}/download` | `GET` | Download FIR PDF (JSON fallback) |
| `/api/firs/{id}/similar` | `GET` | Find similar FIRs (embedding + accused matching) |
| `/api/firs/upload-pdf` | `POST` | Upload and analyse a single FIR PDF |
| `/api/firs/analyze-text` | `POST` | Analyse pasted narrative (no save) |
| `/api/firs/analyze-and-save` | `POST` | Analyse and save narrative as new FIR |
| `/api/firs/bulk-upload` | `POST` | Bulk upload multiple FIR PDFs |
| `/api/firs/bulk-upload-json` | `POST` | Bulk upload pre-processed JSON files |
| `/api/firs/export/all` | `GET` | Export all FIRs as JSON |

### Legal Assistant (All protected)

| Endpoint | Method | Description |
|---|---|---|
| `/api/legal/query` | `POST` | Ask a legal question (Claude API or KB fallback) |
| `/api/legal/sections` | `GET` | Browse IPC/BNS legal sections |
| `/api/legal/sections/{act}/{section}` | `GET` | Look up a specific section |
| `/api/legal/sections/lookup` | `POST` | Batch look up sections for a FIR's acts list |
| `/api/legal/equivalent/{act}/{section}` | `GET` | IPC ↔ BNS cross-mapping |
| `/api/legal/equivalent/batch` | `POST` | Batch IPC ↔ BNS cross-mapping |
| `/api/legal/punishment-calc` | `POST` | Punishment calculator for multiple sections |

### Other (All protected)

| Endpoint | Method | Description |
|---|---|---|
| `/api/dashboard/stats` | `GET` | Aggregated dashboard statistics |
| `/api/mo/patterns` | `GET` | List detected MO patterns |
| `/api/mo/detect` | `POST` | Run MO detection across all FIRs |
| `/api/translate` | `POST` | Translate text (Malayalam ↔ English) |

---

## Common Issues & Fixes

### `database "firai" does not exist`

Stale volume from a previous configuration:
```bash
docker compose down -v
docker compose up --build
```

### `Failed to resolve import "../../api/client"`

Import path is wrong. All page files in `src/pages/` should use one level up:
```js
import { firAPI } from '../api/client';   // correct
```

### `connection is closed` (SQLAlchemy)

Pool holds a stale connection after a DB restart. Handled automatically by `pool_pre_ping=True`. If it persists:
```bash
docker compose restart backend
```

### Frontend shows a blank page or cached errors

Hard-refresh the browser:
- **Windows/Linux:** `Ctrl + Shift + R`
- **macOS:** `Cmd + Shift + R`

Or restart the frontend container:
```bash
docker compose restart frontend
```

### PDF upload is slow

OCR of multi-page FIR PDFs uses Tesseract and takes 15–60 seconds per PDF — this is expected. The backend runs OCR in a background thread so the app stays responsive.

### Docker Desktop — "WSL 2 installation is incomplete" (Windows)

Follow Microsoft's guide: https://aka.ms/wsl2kernel  
Then restart Docker Desktop.

### Legal Assistant returns knowledge-base answers instead of AI chat

The Claude API key is not configured. Add `ANTHROPIC_API_KEY=sk-ant-...` to your `.env` file and restart the backend:
```bash
docker compose restart backend
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 19, Vite, React Router v7, Recharts, Lucide Icons, Axios | Responsive dashboard UI |
| **Backend** | Python 3.11, FastAPI 0.115, SQLAlchemy 2.0 (async), Pydantic v2, python-jose, passlib | REST API + JWT Auth |
| **Database** | PostgreSQL 16 (Alpine) | FIR storage + officer accounts |
| **AI Engine** | Custom BiLSTM + Attention (PyTorch CPU), trained on IPC/BNS legal corpus | Crime classification, entity extraction, legal mapping |
| **Legal Q&A** | Claude API (Anthropic) — optional; built-in IPC/BNS knowledge base as fallback | Conversational legal answers with RAG |
| **Legal KB** | Indian Legal Corpus (IPC, BNS, CrPC, BNSS, NDPS, POCSO, MVA, Kerala Abkari Act) | Section lookup, punishment calculator, investigation steps |
| **Embeddings** | `all-MiniLM-L6-v2` (Sentence-Transformers) | Narrative similarity search |
| **OCR** | PyMuPDF + Tesseract OCR (`mal+eng`) | PDF text extraction |
| **Translation** | Bhashini API (AI4Bharat) + Google Translate fallback (deep-translator) | Malayalam ↔ English |
| **Containerisation** | Docker, Docker Compose | One-command deployment |

---

## FIR File Management

All FIR files follow the naming convention: `FIR_{number}_{year}_{station}`

| Scenario | What Happens |
|---|---|
| **Upload via app** | PDF is OCR'd, FIR number extracted, saved as `FIR_0517_2024_KALPAKANCHERRY.pdf` |
| **Bulk upload** | Each PDF auto-named based on extracted metadata |
| **Database seed** | JSON files auto-named with FIR number + station on first boot |

### Data Management Scripts

```bash
cd backend

# Extract IPC/BNS sections from law PDFs into extracted_rules.json
python scripts/extract_rules.py

# Rename existing files to standardized FIR names (dry run)
python scripts/rename_firs.py

# Apply renames
python scripts/rename_firs.py --apply

# Full reprocess: delete all JSONs, remove duplicates, re-OCR everything (dry run)
python scripts/reprocess_all_firs.py

# Apply reprocessing (requires Tesseract OCR)
python scripts/reprocess_all_firs.py --apply
```

> Reprocessing requires Tesseract OCR with Malayalam language data:
> - **Windows:** `winget install UB-Mannheim.TesseractOCR` + download `mal.traineddata`
> - **Docker:** Already included in the Dockerfile

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

This project is developed for the Kerala Police Department as an AI investigation assistant tool.

---

<p align="center">
  <strong>FirAI</strong> — Custom AI, Smarter Investigations, Safer Kerala
</p>
