"""
FirAI Backend — FastAPI Application
------------------------------------
Kerala Police AI Investigation Assistant

Main entry point for the backend API.
"""

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from seed import seed_database
from seed_officers import seed_officers
from routers import firs, dashboard, legal, mo_patterns, translate
from routers import auth
from services.embedding_engine import embedding_engine
from services.firai_engine import warmup as warmup_ai_engine
from config import get_settings

# Ensure Officer/RegistrationRequest tables are created
import models.officer  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    print("[FirAI] Initializing database...")
    await init_db()

    print("[FirAI] Seeding demo officers...")
    await seed_officers()

    print("[FirAI] Seeding database with existing FIRs...")
    await seed_database()

    print("[FirAI] Warming up embedding model (pre-loading to avoid first-request delay)...")
    import asyncio
    await asyncio.to_thread(embedding_engine.warmup)
    print("[FirAI] Embedding model ready.")

    print("[FirAI] Loading custom AI engine...")
    await asyncio.to_thread(warmup_ai_engine)
    print("[FirAI] Custom AI engine ready.")

    print("[FirAI] Encoding legal sections for RAG search...")
    from services import legal_rag
    await asyncio.to_thread(legal_rag.warmup)
    print("[FirAI] Legal RAG ready.")

    print("[FirAI] Backend ready!")
    yield

    # Shutdown
    print("[FirAI] Shutting down...")


app = FastAPI(
    title="FirAI — Kerala Police AI Investigation Assistant",
    description="AI-powered FIR analysis, case intelligence, and legal guidance for Kerala Police",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — configurable via CORS_ORIGINS env var (comma-separated), with sensible defaults
_default_origins = ["http://localhost:3000", "http://frontend:3000", "http://127.0.0.1:3000"]
_cors_origins = os.environ.get("CORS_ORIGINS", "").split(",") if os.environ.get("CORS_ORIGINS") else _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)       # Auth must be first (public login/register routes)
app.include_router(firs.router)
app.include_router(dashboard.router)
app.include_router(legal.router)
app.include_router(mo_patterns.router)
app.include_router(translate.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint with service status (public — no auth required)."""
    settings = get_settings()
    return {
        "status": "healthy",
        "service": "FirAI Backend",
        "ai_engine": "firai-engine-v1 (custom built)",
        "bhashini_configured": bool(settings.BHASHINI_API_KEY),
    }
