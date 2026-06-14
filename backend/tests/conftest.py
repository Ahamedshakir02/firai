import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from faker import Faker

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from database import Base, get_db
from config import settings

fake = Faker()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Create a test database with in-memory SQLite."""
    # Use in-memory SQLite for testing (faster, isolated)
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def client(test_db):
    """Create a test API client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def authenticated_client(client, test_db):
    """Create an authenticated test client with a registered officer."""
    from models.officer import Officer
    from sqlalchemy.orm import Session
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Create a test officer
    async with AsyncSession(test_db) as session:
        test_officer = Officer(
            badge_number="TEST001",
            name="Test Officer",
            password_hash=pwd_context.hash("testpassword123"),
            is_approved=True,
            is_admin=False,
        )
        session.add(test_officer)
        await session.commit()

    # Login and get token
    response = await client.post(
        "/api/auth/login",
        json={"badge_number": "TEST001", "password": "testpassword123"},
    )

    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    return client


@pytest.fixture
def sample_fir_data():
    """Sample FIR data for testing."""
    return {
        "fir_number": "001/2025",
        "year": 2025,
        "police_station": "Kalpakancherry",
        "narrative": "A theft case reported at a local shop. Items worth Rs. 5000 stolen.",
        "crime_type": "theft",
        "severity": "minor",
        "acts": ["IPC:379"],
        "accused_names": ["John Doe"],
    }


@pytest.fixture
def sample_legal_query():
    """Sample legal query for testing."""
    return {
        "query": "What is the punishment for theft under IPC section 379?",
    }


@pytest.fixture
def classifier():
    """Load the FIR classifier model."""
    from ai_engine.inference import FirInference

    inference = FirInference()
    return inference.classifier


@pytest.fixture
def embedding_engine():
    """Load the embedding engine."""
    from services.embedding_engine import EmbeddingEngine

    return EmbeddingEngine()
