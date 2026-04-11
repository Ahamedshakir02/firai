# FirAI — Kerala Police AI Investigation Assistant

> AI-powered knowledge and investigation assistant that provides real-time FIR analysis, case intelligence, legal guidance, and multilingual support for Kerala Police officers.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

---

## 🔍 Overview

Kerala Police officers face fragmented processes when accessing FIRs, case updates, and legal procedures. **FirAI** solves this by providing an AI-powered investigation dashboard that:

- **Parses FIR narratives** (Malayalam & English) and classifies crimes with relevant IPC/BNS sections
- **Finds similar past cases** using semantic narrative similarity
- **Detects Modus Operandi patterns** across FIRs to identify recurring crime methods
- **Provides AI legal guidance** powered by Google Gemini
- **Translates narratives** between Malayalam and English via Bhashini API
- **Centralizes all FIR data** in a unified, searchable dashboard

### Core Principle: Narrative-Centric

The **FIR narrative** (Section 12 — First Information Contents) is the backbone of the entire system. All AI analysis, similarity search, crime classification, and pattern detection flows from the narrative text.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                 Docker Compose                   │
│                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Frontend │  │   Backend    │  │ PostgreSQL│  │
│  │ React    │──│   FastAPI    │──│   16      │  │
│  │ Port 3000│  │   Port 8000  │  │ Port 5432 │  │
│  └──────────┘  └──────┬───────┘  └───────────┘  │
│                       │                          │
│              ┌────────┼────────┐                 │
│              │        │        │                 │
│           Gemini  Bhashini  Embeddings           │
│            API      API    (MiniLM)              │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- API Keys: Gemini, Bhashini (optional)

### 1. Clone & Configure

```bash
git clone https://github.com/Ahamedshakir02/firai.git
cd firai
```

### 2. Set API Keys

Edit the `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
BHASHINI_API_KEY=your_bhashini_api_key
BHASHINI_USER_ID=your_bhashini_user_id
```

### 3. Start Everything

```bash
docker-compose up --build
```

This starts:
| Service | URL | Description |
|---|---|---|
| **Frontend** | http://localhost:3000 | React dashboard |
| **Backend** | http://localhost:8000 | FastAPI API |
| **Database** | localhost:5432 | PostgreSQL |

On first boot, the backend automatically **seeds 36 existing FIRs** into the database.

---

## 📱 Features

| Feature | Description |
|---|---|
| **Dashboard** | Crime stats, severity charts, recent FIRs overview |
| **FIR Analyzer** | Upload PDF or paste narrative → AI analysis (crime type, risk, IPC sections) |
| **Case Intelligence** | Browse FIRs, search narratives, find similar cases |
| **Legal Assistant** | Chat with Gemini for IPC/BNS guidance, bail info, procedures |
| **MO Patterns** | Detect recurring crime methods across FIR narratives |
| **Translation** | Malayalam ↔ English narrative translation via Bhashini |
| **Bulk Upload** | Upload multiple historical FIRs (PDF or JSON) for batch processing |

---

## 📁 Project Structure

```
firai/
├── docker-compose.yml       # Orchestrates all 3 services
├── .env                     # API keys and database config
├── backend/                 # FastAPI + Python (see backend/README.md)
│   ├── main.py              # App entry point
│   ├── models/              # SQLAlchemy ORM models
│   ├── routers/             # API route modules
│   ├── services/            # Business logic (Gemini, OCR, embeddings)
│   ├── data/                # Existing FIR PDFs and JSONs
│   └── seed.py              # Database seeding script
└── frontend/                # React + Vite (see frontend/README.md)
    └── src/
        ├── pages/           # 6 dashboard pages
        ├── components/      # Reusable UI components
        └── api/             # API client
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `POSTGRES_USER` | Yes | Database username (default: `firai`) |
| `POSTGRES_PASSWORD` | Yes | Database password (default: `firai_secret`) |
| `POSTGRES_DB` | Yes | Database name (default: `firai_db`) |
| `DATABASE_URL` | Yes | Full PostgreSQL connection string |
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI analysis |
| `BHASHINI_API_KEY` | No | Bhashini API key for Malayalam translation |
| `BHASHINI_USER_ID` | No | Bhashini user ID |
| `GOOGLE_MAPS_API_KEY` | No | Google Maps API key (future use) |

---

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/firs` | GET | List all FIRs (filterable) |
| `/api/firs/{id}` | GET | Get FIR details |
| `/api/firs/upload-pdf` | POST | Upload & analyze single FIR PDF |
| `/api/firs/analyze-text` | POST | Analyze pasted narrative |
| `/api/firs/bulk-upload` | POST | Bulk upload FIR PDFs |
| `/api/firs/bulk-upload-json` | POST | Bulk upload pre-processed JSONs |
| `/api/firs/{id}/similar` | GET | Find similar FIRs by narrative |
| `/api/dashboard/stats` | GET | Dashboard statistics |
| `/api/legal/query` | POST | AI legal Q&A |
| `/api/legal/sections` | GET | IPC/BNS section reference |
| `/api/mo/patterns` | GET | List MO patterns |
| `/api/mo/detect` | POST | Run MO detection |
| `/api/translate` | POST | Translate text |

---

## 📊 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, React Router, Recharts, Lucide Icons |
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), Pydantic |
| Database | PostgreSQL 16 |
| AI/ML | Google Gemini 1.5 Flash, Sentence-Transformers, scikit-learn |
| OCR | PyMuPDF, Tesseract (Malayalam + English) |
| Translation | Bhashini API (AI4Bharat) |
| DevOps | Docker, Docker Compose |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## 📜 License

This project is developed for the Kerala Police Department as an AI investigation assistant.

---

<p align="center">
  <strong>FirAI</strong> — Smarter Investigations, Safer Kerala 🛡️
</p>
