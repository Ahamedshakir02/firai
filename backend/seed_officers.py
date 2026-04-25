"""
Seed Demo Officers
------------------
Pre-seeds demo officer accounts for testing.
Runs during application startup.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from database import async_session
from models.officer import Officer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_OFFICERS = [
    {
        "badge_number": "KP-1001",
        "name": "Inspector Arun Kumar",
        "rank": "Sub Inspector (SI)",
        "police_station": "Thiruvananthapuram Central",
        "district": "Thiruvananthapuram",
        "phone": "+91 9876543210",
        "email": "arun.kumar@keralapolice.gov.in",
        "password": "firai123",
        "is_admin": True,
    },
    {
        "badge_number": "KP-1002",
        "name": "ASI Priya Nair",
        "rank": "Assistant Sub Inspector (ASI)",
        "police_station": "Ernakulam South",
        "district": "Ernakulam",
        "phone": "+91 9876543211",
        "email": "priya.nair@keralapolice.gov.in",
        "password": "firai123",
        "is_admin": False,
    },
    {
        "badge_number": "KP-1003",
        "name": "CI Rajesh Menon",
        "rank": "Circle Inspector (CI)",
        "police_station": "Kozhikode City",
        "district": "Kozhikode",
        "phone": "+91 9876543212",
        "email": "rajesh.menon@keralapolice.gov.in",
        "password": "firai123",
        "is_admin": True,
    },
]


async def seed_officers():
    """Seed demo officers if they don't already exist."""
    async with async_session() as db:
        for data in DEMO_OFFICERS:
            result = await db.execute(
                select(Officer).where(Officer.badge_number == data["badge_number"])
            )
            if result.scalar_one_or_none():
                continue

            officer = Officer(
                badge_number=data["badge_number"],
                name=data["name"],
                rank=data["rank"],
                police_station=data["police_station"],
                district=data["district"],
                phone=data["phone"],
                email=data["email"],
                password_hash=pwd_context.hash(data["password"]),
                is_admin=data["is_admin"],
            )
            db.add(officer)
            print(f"  [Seed] Created officer: {data['name']} ({data['badge_number']})")

        await db.commit()
    print(f"[FirAI] Officer seeding complete ({len(DEMO_OFFICERS)} demo accounts)")
