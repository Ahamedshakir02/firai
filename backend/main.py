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
from routers import firs, dashboard, legal, mo_patterns, translate, monitoring, cases
from routers import auth
from middleware import LoggingMiddleware, ErrorCatchingMiddleware, PerformanceMonitoringMiddleware
from services.embedding_engine import embedding_engine
from services.firai_engine import warmup as warmup_ai_engine
from config import get_settings
from logging_config import logger

# Ensure Officer/RegistrationRequest tables are created
import models.officer  # noqa: F401
import models.audit  # noqa: F401
import models.case  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("[FirAI] Initializing database...")
    await init_db()

    logger.info("[FirAI] Seeding demo officers...")
    await seed_officers()

    logger.info("[FirAI] Seeding database with existing FIRs...")
    await seed_database()

    logger.info("[FirAI] Warming up embedding model...")
    import asyncio
    await asyncio.to_thread(embedding_engine.warmup)
    logger.info("[FirAI] Embedding model ready.")

    logger.info("[FirAI] Loading custom AI engine...")
    await asyncio.to_thread(warmup_ai_engine)
    logger.info("[FirAI] Custom AI engine ready.")

    logger.info("[FirAI] Encoding legal sections for RAG search...")
    from services import legal_rag
    await asyncio.to_thread(legal_rag.warmup)
    logger.info("[FirAI] Legal RAG ready.")

    logger.info("[FirAI] Loading Generative Legal Assistant LLM...")
    from ai_engine.models import legal_llm
    await asyncio.to_thread(legal_llm.warmup)

    logger.info("[FirAI] Backend ready!")
    yield

    # Shutdown
    logger.info("[FirAI] Shutting down...")


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

# Add logging and monitoring middleware
app.add_middleware(PerformanceMonitoringMiddleware)
app.add_middleware(ErrorCatchingMiddleware)
app.add_middleware(LoggingMiddleware)

# Mount routers
app.include_router(auth.router)       # Auth must be first (public login/register routes)
app.include_router(firs.router)
app.include_router(dashboard.router)
app.include_router(legal.router)
app.include_router(mo_patterns.router)
app.include_router(translate.router)
app.include_router(monitoring.router)  # Metrics, audit trails, and monitoring endpoints
app.include_router(cases.router)       # Notes, bulk actions, timeline, notifications


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
