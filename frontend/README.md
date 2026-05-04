# FirAI Frontend

> React dashboard for the Kerala Police AI Investigation Assistant.

---

## Overview

A premium, dark-themed single-page application built with React and Vite. Provides 7 investigation pages for Kerala Police officers to analyze FIRs, find similar cases, get legal guidance, and detect crime patterns.

### Design Philosophy

- **Dark navy theme** with electric blue and gold accents (police aesthetic)
- **Glassmorphism** cards with subtle backdrop blur
- **Micro-animations** on page transitions, hover effects, and loading states
- **Narrative-centric** — every page revolves around FIR narrative text
- **Responsive** — works on desktop and tablet for field officers

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **React 19** | UI framework |
| **Vite 8** | Build tool & dev server |
| **React Router** | Client-side routing (6 pages) |
| **Axios** | HTTP API client |
| **Recharts** | Dashboard charts (bar, pie) |
| **Lucide React** | Icon library |

---

## Project Structure

```
frontend/
├── Dockerfile              # Node 20 Alpine + Vite dev server
├── package.json
├── vite.config.js           # API proxy to backend
├── index.html               # Entry HTML with SEO meta
│
└── src/
    ├── main.jsx             # React DOM root
    ├── App.jsx              # Router with all 7 pages + ProtectedRoute
    ├── index.css            # 🎨 Complete design system
    ├── App.css
    │
    ├── api/
    │   └── client.js        # Axios API client (all endpoints)
    │
    ├── components/
    │   └── Layout/
    │       ├── Sidebar.jsx  # Navigation sidebar with icons
    │       ├── Header.jsx   # Top bar with search & title
    │       └── Layout.jsx   # Wrapper with Outlet
    │
    └── pages/
        ├── Dashboard.jsx         # Crime stats, charts, recent FIRs
        ├── FIRAnalyzer.jsx       # Upload/paste/bulk → AI analysis
        ├── CaseIntelligence.jsx  # Browse, search, similar cases, PDF download
        ├── LegalAssistant.jsx    # Local Ollama AI Q&A + IPC ↔ BNS Mapper + Punishment Calculator
        ├── MOPatterns.jsx        # MO pattern detection & alerts
        ├── Translation.jsx       # Malayalam ↔ English translation
        ├── Login.jsx             # JWT Authentication & Registration
        └── Profile.jsx           # Officer profile details
```

---

## Pages

### 0. Authentication (`/login`, `/profile`)
- **Login**: Secure access via Badge Number and Password.
- **Registration**: Request portal for new officers to register station, rank, and details.
- **Profile**: Displays officer identity and allows logout.

### 1. Dashboard (`/`)
- **Stat Cards**: Total FIRs, high severity, critical cases, crime types
- **Bar Chart**: Crime type distribution (from narrative analysis)
- **Pie Chart**: Severity breakdown
- **Recent FIRs Table**: Clickable rows with narrative preview

### 2. FIR Analyzer (`/fir-analyzer`)
Three input modes:
- **Paste Narrative**: Enter Malayalam or English text → AI analysis
- **Upload PDF**: OCR extraction → narrative → analysis
- **Bulk Upload**: Multiple PDFs or JSONs → batch process into database

Results panel shows:
- Crime type, severity, risk score (1–10)
- English summary of narrative
- Applicable IPC/BNS sections
- Recommended investigation steps
- Similar cases with similarity percentage and detailed accused identity comparisons
- **PDF Download**: Retrieve original FIR PDFs directly from results

### 3. Case Intelligence (`/case-intelligence`)
- Browse all FIRs in the database
- Search narratives by keyword
- Filter by crime type
- Click any FIR → detailed view with narrative, acts, accused, and **Download PDF** button
- Similar cases panel (multi-dimensional: narrative embedding + crime type + accused matching)

### 4. Legal Assistant (`/legal-assistant`)
- **Chat Interface**: Ask legal questions to the custom FirAI legal engine
- Pre-built quick questions for common officer queries
- Retains chat history and identifies the requesting officer
- Relevant IPC/BNS sections shown as badges
- **Reference Panel**: Full IPC/BNS section table with bail/cognizable status

### 5. MO Patterns (`/mo-patterns`)
- Click "Run MO Detection" to analyze all narratives
- Pattern cards with description, crime type, and linked FIR IDs
- Uses DBSCAN clustering + FirAI pattern analysis

### 6. Translation (`/translation`)
- Source/target language selectors (Malayalam, English, Hindi)
- Swap languages button
- Copy translated output to clipboard
- Powered by Bhashini API

---

## Design System (`index.css`)

### Color Palette

| Token | Color | Usage |
|---|---|---|
| `--bg-primary` | `#0a1628` | Main background |
| `--bg-card` | `#1a2942` | Card backgrounds |
| `--accent-blue` | `#3b82f6` | Primary accent, active states |
| `--accent-gold` | `#f59e0b` | Warning, MO alerts |
| `--accent-emerald` | `#10b981` | Success, low severity |
| `--accent-red` | `#ef4444` | Danger, critical severity |

### Components

- `.card` / `.card-glass` — Glassmorphism cards with hover glow
- `.stat-card` — Metric cards with colored top border
- `.badge-*` — Severity and type badges
- `.btn-*` — Primary, secondary, ghost, danger buttons
- `.chat-bubble` — User/AI chat bubbles with slide-up animation
- `.upload-zone` — Drag & drop upload area
- `.data-table` — Styled data table with hover rows
- `.similarity-bar` — Visual similarity percentage bar
- `.narrative-box` — Scrollable narrative text display

---

## API Client (`api/client.js`)

All backend endpoints are wrapped in named exports:

```javascript
import { authAPI, firAPI, dashboardAPI, legalAPI, moAPI, translateAPI } from './api/client';

// Examples
await authAPI.login('KERALA-123', 'pass');
await firAPI.list({ crime_type: 'assault' });
await firAPI.analyzeText('narrative text here');
await firAPI.bulkUploadPDF(fileArray);
await dashboardAPI.getStats();
await legalAPI.query('What is IPC 324?');
await translateAPI.translate('text', 'ml', 'en');
```

---

## Running Standalone (without Docker)

```bash
# Install dependencies
npm install

# Development server (proxies /api to backend:8000)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

> **Note**: The Vite dev server proxies `/api` requests to `http://backend:8000`. When running standalone, update `vite.config.js` proxy target to `http://localhost:8000`.

---

## Vite Configuration

```javascript
// vite.config.js
server: {
  host: '0.0.0.0',
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://backend:8000',  // Change to localhost:8000 if running standalone
      changeOrigin: true,
    }
  }
}
```
