# FirAI — Kerala Police AI Investigation Assistant

> AI-powered investigation assistant providing real-time FIR analysis, case intelligence, legal guidance, and multilingual support for Kerala Police officers.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Architecture](#️-architecture)
3. [Prerequisites](#-prerequisites)
4. [Step 1 — Install Docker](#step-1--install-docker)
5. [Step 2 — Clone the Repository](#step-2--clone-the-repository)
6. [Step 3 — Configure API Keys](#step-3--configure-api-keys)
7. [Step 4 — Run the Project](#step-4--run-the-project)
8. [Verify Everything Works](#-verify-everything-works)
9. [Features](#-features)
10. [Project Structure](#-project-structure)
11. [Environment Variables](#-environment-variables)
12. [API Endpoints](#️-api-endpoints)
13. [Common Issues & Fixes](#-common-issues--fixes)
14. [Tech Stack](#-tech-stack)

---

## 🔍 Overview

Kerala Police officers face fragmented processes when accessing FIRs, case updates, and legal procedures. **FirAI** solves this by providing an AI-powered investigation dashboard that:

- **Parses FIR narratives** (Malayalam & English) and classifies crimes with relevant IPC/BNS sections
- **Finds similar past cases** using semantic narrative similarity (embeddings)
- **Detects Modus Operandi (MO) patterns** across FIRs to identify recurring crime methods
- **Provides AI legal guidance** powered by Google Gemini
- **Translates narratives** between Malayalam and English via Bhashini API
- **Centralises all FIR data** in a unified, searchable dashboard sorted by real case numbers

### Core Principle: Narrative-Centric

The **FIR narrative** (Section 12 — First Information Contents) is the backbone of the entire system. All AI analysis, similarity search, crime classification, and pattern detection flows from the narrative text.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Docker Compose                    │
│                                                     │
│  ┌──────────┐    ┌──────────────┐   ┌─────────────┐ │
│  │ Frontend │    │   Backend    │   │  PostgreSQL │ │
│  │  React   │◄──►│   FastAPI    │◄─►│     16      │ │
│  │ :3000    │    │   :8000      │   │   :5432     │ │
│  └──────────┘    └──────┬───────┘   └─────────────┘ │
│                         │                           │
│              ┌──────────┼──────────┐                │
│              ▼          ▼          ▼                │
│           Gemini    Bhashini   Sentence             │
│            API        API     Transformers          │
│         (Analysis) (Translate) (Embeddings)         │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Prerequisites

Before starting, you need:

| Requirement | Notes |
|---|---|
| **Docker Desktop** | Includes Docker Engine + Docker Compose |
| **Git** | To clone the repository |
| **Google Gemini API Key** | Free tier available — for AI analysis |
| **Bhashini API Key** | Optional — only needed for Malayalam translation |

> **Minimum System:** 4 GB RAM, 10 GB free disk space (for Docker images + ML models)

---

## Step 1 — Install Docker

Docker Desktop bundles everything you need (Docker Engine + Docker Compose). Pick your OS:

### 🪟 Windows

1. **Download** Docker Desktop from the official website:
   👉 https://www.docker.com/products/docker-desktop/

2. **Run the installer** (`Docker Desktop Installer.exe`) — accept defaults.

3. When prompted, enable **WSL 2** (recommended). If WSL 2 is not installed, Docker will guide you through it.

4. **Restart your computer** after installation.

5. Open **Docker Desktop** from the Start menu. Wait for it to say **"Engine running"** (green icon in the taskbar).

6. **Verify** by opening PowerShell or Command Prompt:
   ```powershell
   docker --version
   docker compose version
   ```
   You should see version numbers for both.

---

### 🍎 macOS

1. **Download** Docker Desktop for Mac:
   - Apple Silicon (M1/M2/M3): https://desktop.docker.com/mac/main/arm64/Docker.dmg
   - Intel: https://desktop.docker.com/mac/main/amd64/Docker.dmg

2. Open the `.dmg` file and **drag Docker to Applications**.

3. Launch **Docker** from Applications. Grant permissions if asked.

4. Wait for Docker to start (whale icon in the menu bar turns solid).

5. **Verify** in Terminal:
   ```bash
   docker --version
   docker compose version
   ```

---

### 🐧 Linux (Ubuntu / Debian)

Run these commands in a terminal:

```bash
# Remove any old Docker versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine + Compose plugin
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow running Docker without sudo (log out and back in after this)
sudo usermod -aG docker $USER

# Start service
sudo systemctl enable --now docker
```

**Verify:**
```bash
docker --version
docker compose version
```

---

## Step 2 — Clone the Repository

Open a terminal (PowerShell on Windows, Terminal on macOS/Linux):

```bash
git clone https://github.com/Ahamedshakir02/firai.git
cd firai
```

> **Don't have Git?**
> - Windows: Download from https://git-scm.com/download/win
> - macOS: Run `xcode-select --install` in Terminal
> - Linux: `sudo apt-get install git`

---

## Step 3 — Configure API Keys

The `.env` file is **not included in the repository** (it's gitignored to keep secrets safe). You need to create it from the provided template.

### 3a. Copy the template to create your `.env`

```bash
# Windows (PowerShell)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

> **This step is required.** The project will not start without a `.env` file.

### 3b. Get a Gemini API Key (Required for AI analysis)

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key

### 3c. Edit `.env` and add your keys

Open the file you just created:

```bash
# Windows (PowerShell)
notepad .env

# macOS / Linux
nano .env
```

Fill in your Gemini key (everything else can stay as-is):

```env
# Database — leave these unchanged, Docker handles it
POSTGRES_USER=firai
POSTGRES_PASSWORD=firai_secret
POSTGRES_DB=firai_db
DATABASE_URL=postgresql+asyncpg://firai:firai_secret@db:5432/firai_db

# Required: Add your Gemini API key here
GEMINI_API_KEY=AIza...your_key_here

# Optional: Bhashini for Malayalam ↔ English translation
# Leave blank if you don't need translation features
BHASHINI_API_KEY=
BHASHINI_USER_ID=

# Optional: Google Maps (reserved for future use)
GOOGLE_MAPS_API_KEY=
```

> **Without a Gemini key:** The app still runs and loads FIRs, but AI analysis uses a keyword-based fallback instead of Gemini.

### 3d. Optional — Bhashini API Key (for Translation)

1. Register at https://bhashini.gov.in/ulca/user-profile
2. Navigate to **My Profile → API Keys**
3. Copy your **API Key** and **User ID**
4. Paste them into `.env`

---

## Step 4 — Run the Project

Make sure Docker Desktop is running, then in the project directory:

```bash
docker-compose up --build
```

### What happens on first run

| Step | What it does | Time |
|---|---|---|
| 🔨 **Build** | Downloads base images, installs Python packages, npm packages | 3–8 min |
| 🗄️ **Database** | PostgreSQL initialises with `firai_db` | ~10 sec |
| 🤖 **Backend** | FastAPI starts, ML model downloads (~90 MB), seeds 36 FIRs | 1–2 min |
| ⚛️ **Frontend** | Vite dev server starts | ~15 sec |

> **Subsequent runs** (without `--build`) start in under 30 seconds.

### Running in the background (detached mode)

```bash
docker-compose up --build -d
```

View logs anytime:
```bash
docker-compose logs -f           # all services
docker-compose logs -f backend   # backend only
docker-compose logs -f frontend  # frontend only
```

### Stopping the project

```bash
docker-compose down              # stops containers, keeps data
docker-compose down -v           # stops containers AND deletes database (fresh start)
```

---

## ✅ Verify Everything Works

Once started, check these URLs in your browser:

| Service | URL | Expected |
|---|---|---|
| **Dashboard** | http://localhost:3000 | Kerala Police FirAI dashboard |
| **Backend API** | http://localhost:8000/api/health | `{"status": "healthy"}` |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |

You should see **36 FIRs** already loaded in the Case Intelligence page, sorted by real case numbers (e.g. `Case 0008/2025`).

---

## 📱 Features

| Feature | Page | Description |
|---|---|---|
| **Dashboard** | `/` | Crime stats, severity breakdown, recent FIRs |
| **FIR Analyzer** | `/fir-analyzer` | Upload PDF or paste narrative → AI classifies crime, extracts sections, suggests investigation steps |
| **Case Intelligence** | `/case-intelligence` | Browse & search FIRs by case number, find similar cases using embedding similarity |
| **Legal Assistant** | `/legal` | Chat with Gemini AI for IPC/BNS guidance, bail info, CrPC procedures |
| **MO Patterns** | `/mo-patterns` | Detect recurring modus operandi across all FIR narratives |
| **Translation** | `/translation` | Translate FIR text between Malayalam and English |

---

## 📁 Project Structure

```
firai/
├── docker-compose.yml         # Orchestrates all 3 services
├── .env                       # Your API keys and config (never commit this)
├── .env.example               # Template for environment variables
│
├── backend/                   # Python / FastAPI
│   ├── Dockerfile
│   ├── main.py                # App entry point, startup hooks
│   ├── config.py              # Settings loaded from .env
│   ├── database.py            # SQLAlchemy async engine + session
│   ├── seed.py                # Seeds 36 existing FIRs on first boot
│   ├── requirements.txt
│   ├── models/
│   │   └── fir.py             # FIR, Accused, MOPattern, LegalSection ORM models
│   ├── routers/
│   │   ├── firs.py            # FIR upload, analysis, similarity search
│   │   ├── dashboard.py       # Statistics endpoint
│   │   ├── legal.py           # Legal Q&A
│   │   ├── mo_patterns.py     # MO pattern detection
│   │   └── translate.py       # Translation endpoint
│   ├── schemas/
│   │   └── fir.py             # Pydantic request/response schemas
│   ├── services/
│   │   ├── gemini_service.py  # Google Gemini integration (async)
│   │   ├── embedding_engine.py# Sentence-Transformer similarity search
│   │   ├── fir_processor.py   # PDF OCR + field extraction
│   │   ├── bhashini_service.py# Malayalam translation
│   │   ├── legal_kb.py        # IPC/BNS knowledge base
│   │   └── mo_detector.py     # MO pattern detection logic
│   └── data/
│       └── structured/        # 36 pre-processed FIR JSON files
│
└── frontend/                  # React / Vite
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── main.jsx           # App entry point
        ├── App.jsx            # Router setup
        ├── index.css          # Global design system
        ├── api/
        │   └── client.js      # Axios API client (all endpoints)
        ├── components/
        │   └── Layout/        # Sidebar, Header, Layout wrapper
        └── pages/
            ├── Dashboard.jsx
            ├── FIRAnalyzer.jsx
            ├── CaseIntelligence.jsx
            ├── LegalAssistant.jsx
            ├── MOPatterns.jsx
            └── Translation.jsx
```

---

## 🔐 Environment Variables

All variables are set in the `.env` file in the project root.

| Variable | Required | Default | Description |
|---|---|---|---|
| `POSTGRES_USER` | ✅ | `firai` | PostgreSQL username |
| `POSTGRES_PASSWORD` | ✅ | `firai_secret` | PostgreSQL password |
| `POSTGRES_DB` | ✅ | `firai_db` | Database name |
| `DATABASE_URL` | ✅ | *(see .env)* | Full async connection string — don't change the `@db:5432` part, it refers to the Docker service name |
| `GEMINI_API_KEY` | ✅ | — | Google Gemini API for AI analysis, legal Q&A, MO detection |
| `BHASHINI_API_KEY` | ❌ | — | Bhashini API for Malayalam ↔ English translation |
| `BHASHINI_USER_ID` | ❌ | — | Bhashini user ID |
| `GOOGLE_MAPS_API_KEY` | ❌ | — | Reserved for future map integration |

---

## 🛠️ API Endpoints

The full interactive API docs are available at **http://localhost:8000/docs** when running.

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | `GET` | Health check |
| `/api/firs` | `GET` | List FIRs (filter by crime type, severity, search) |
| `/api/firs/{id}` | `GET` | Get full FIR details |
| `/api/firs/upload-pdf` | `POST` | Upload & analyse a single FIR PDF |
| `/api/firs/analyze-text` | `POST` | Analyse pasted narrative text |
| `/api/firs/analyze-and-save` | `POST` | Analyse and persist narrative as a new FIR |
| `/api/firs/bulk-upload` | `POST` | Bulk upload multiple FIR PDFs |
| `/api/firs/bulk-upload-json` | `POST` | Bulk upload pre-processed JSON files |
| `/api/firs/{id}/similar` | `GET` | Find similar FIRs by narrative embedding |
| `/api/dashboard/stats` | `GET` | Aggregated statistics for dashboard |
| `/api/legal/query` | `POST` | Ask Gemini AI a legal question |
| `/api/legal/sections` | `GET` | Browse IPC/BNS legal sections |
| `/api/mo/patterns` | `GET` | List detected MO patterns |
| `/api/mo/detect` | `POST` | Run MO pattern detection across all FIRs |
| `/api/translate` | `POST` | Translate text (Malayalam ↔ English) |

---

## 🔧 Common Issues & Fixes

### ❌ `database "firai" does not exist`

The database volume has stale data from a previous configuration. Fix:
```bash
docker-compose down -v    # deletes old volume
docker-compose up --build # fresh start with correct DB name
```

---

### ❌ `Failed to resolve import "../../api/client"`

The frontend import paths are wrong. All page files in `src/pages/` should import as:
```js
import { firAPI } from '../api/client';   // ✅ one level up
// NOT
import { firAPI } from '../../api/client'; // ❌ two levels up
```

---

### ❌ `connection is closed` (SQLAlchemy)

The database container was restarted and the connection pool holds stale connections. This is handled automatically by `pool_pre_ping=True` in the latest code. If it persists, restart the backend:
```bash
docker-compose restart backend
```

---

### ❌ Frontend shows a blank page or old cached errors

Vite cached an error. Hard refresh the browser:
- **Windows/Linux:** `Ctrl + Shift + R`
- **macOS:** `Cmd + Shift + R`

Or restart the frontend container:
```bash
docker-compose restart frontend
```

---

### ❌ Gemini analysis returns fallback results

Check your API key is set correctly in `.env`:
```bash
docker exec firai_backend printenv GEMINI_API_KEY
```
If blank, edit `.env` and restart:
```bash
docker-compose restart backend
```

---

### ❌ PDF upload is very slow

OCR of multi-page FIR PDFs uses Tesseract and takes 15–60 seconds per PDF — this is normal. The backend runs the OCR in a background thread so the app stays responsive.

---

### ❌ Docker Desktop says "WSL 2 installation is incomplete" (Windows)

Follow Microsoft's guide: https://aka.ms/wsl2kernel  
Then restart Docker Desktop.

---

## 📊 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 19, Vite, React Router v6, Recharts, Lucide Icons | Dashboard UI |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy (async), Pydantic v2 | REST API |
| **Database** | PostgreSQL 16 | FIR storage |
| **AI Analysis** | Google Gemini 1.5 Flash | Crime classification, legal Q&A, MO detection |
| **Embeddings** | `all-MiniLM-L6-v2` (Sentence-Transformers) | Narrative similarity search |
| **OCR** | PyMuPDF + Tesseract OCR (`mal+eng`) | PDF text extraction |
| **Translation** | Bhashini API (AI4Bharat) | Malayalam ↔ English |
| **Containerisation** | Docker, Docker Compose | One-command deployment |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📜 License

This project is developed for the Kerala Police Department as an AI investigation assistant tool.

---

<p align="center">
  <strong>FirAI</strong> — Smarter Investigations, Safer Kerala 🛡️
</p>
