"""
FirAI Backend — FastAPI Application
------------------------------------
Kerala Police AI Investigation Assistant

Main entry point for the backend API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from seed import seed_database
from routers import firs, dashboard, legal, mo_patterns, translate
from services.embedding_engine import embedding_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    print("[FirAI] Initializing database...")
    await init_db()

    print("[FirAI] Seeding database with existing FIRs...")
    await seed_database()

    print("[FirAI] Warming up embedding model (pre-loading to avoid first-request delay)...")
    import asyncio
    await asyncio.to_thread(embedding_engine.warmup)
    print("[FirAI] Embedding model ready.")

    print("[FirAI] Backend ready!")
    yield

    # Shutdown
    print("[FirAI] Shutting down...")


app = FastAPI(
    title="FirAI — Kerala Police AI Investigation Assistant",
    description="AI-powered FIR analysis, case intelligence, and legal guidance for Kerala Police",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(firs.router)
app.include_router(dashboard.router)
app.include_router(legal.router)
app.include_router(mo_patterns.router)
app.include_router(translate.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "FirAI Backend"}
