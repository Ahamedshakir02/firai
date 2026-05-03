"""
Seed Script
-----------
Migrates existing 36 structured FIR JSON files into PostgreSQL.
Run on first startup to populate the database.
"""

import os
import json
import asyncio
from datetime import datetime
from sqlalchemy import select, func
from database import engine, async_session, Base
from models.fir import FIR, Accused
from services.embedding_engine import embedding_engine
from services import firai_engine
from services.fir_processor import extract_fir_number, generate_fir_filename
from services.fir_processor import extract_district_and_station
from config import get_settings

settings = get_settings()


async def seed_database():
    """Seed the database with existing structured FIR JSON files."""

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Check if already seeded
    async with async_session() as db:
        result = await db.execute(select(func.count(FIR.id)))
        count = result.scalar()
        if count > 0:
            print(f"[Seed] Database already has {count} FIRs. Skipping seed.")
            return

    # Load structured JSONs
    structured_dir = settings.STRUCTURED_DIR
    if not os.path.exists(structured_dir):
        print(f"[Seed] Structured data directory not found: {structured_dir}")
        return

    json_files = sorted([f for f in os.listdir(structured_dir) if f.endswith(".json")])
    print(f"[Seed] Found {len(json_files)} JSON files to seed.")

    async with async_session() as db:
        for filename in json_files:
            filepath = os.path.join(structured_dir, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                narrative = data.get("narrative", "").strip()
                if not narrative:
                    print(f"[Seed] Skipping {filename}: no narrative")
                    continue

                # Parse date
                fir_date = None
                date_str = data.get("date")
                if date_str:
                    for fmt in ["%d/%m/%Y", "%d-%m-%Y"]:
                        try:
                            fir_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue

                # Use custom FirAI Engine for analysis
                analysis = firai_engine._fallback_analysis(narrative)

                # Extract FIR number and station from full_text if available
                fir_num = None
                district = None
                station = None
                full_text = data.get("full_text", "")
                if full_text:
                    fir_num = extract_fir_number(full_text)
                    district, station = extract_district_and_station(full_text)

                # Generate proper FIR-based filename
                proper_filename = generate_fir_filename(
                    fir_number=fir_num,
                    police_station=station,
                    fallback_name=data.get("file", filename),
                    extension=os.path.splitext(filename)[1],
                )

                # Create FIR record
                fir = FIR(
                    file_name=proper_filename,
                    fir_number=fir_num,
                    narrative=narrative,
                    full_text=full_text,
                    fir_date=fir_date,
                    district=district,
                    police_station=station,
                    place=data.get("place"),
                    acts=data.get("acts"),
                    complainant=data.get("complainant"),
                    crime_type=analysis.get("crime_type"),
                    severity=analysis.get("severity"),
                    summary_en=analysis.get("summary_en"),
                    recommended_steps=analysis.get("recommended_steps"),
                    key_entities=analysis.get("key_entities"),
                )

                # Generate embedding
                embedding = embedding_engine.encode_narrative(narrative)
                fir.embedding_vector = embedding.tobytes()

                db.add(fir)
                await db.flush()

                # Add accused
                for acc in data.get("accused", []):
                    if acc.get("name"):
                        accused = Accused(
                            fir_id=fir.id,
                            name=acc.get("name"),
                            father_name=acc.get("father_name"),
                            dob=acc.get("dob"),
                            address=acc.get("address")
                        )
                        db.add(accused)

                print(f"[Seed] ✓ {filename} → FIR #{fir.id} ({analysis.get('crime_type')})")

            except Exception as e:
                print(f"[Seed] ✗ Error processing {filename}: {e}")

        await db.commit()
        print(f"[Seed] Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
