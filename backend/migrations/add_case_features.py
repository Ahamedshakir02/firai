"""
Database Migration: Case Collaboration Features
-----------------------------------------------
Adds the workflow columns required by bulk actions & the timeline:
  - firs.status  (case workflow state)
  - firs.tags    (JSON array of labels)

The fir_notes, case_events, and notifications tables are created
automatically by SQLAlchemy's create_all() on startup; this migration
only handles the columns added to the pre-existing `firs` table, plus
helpful indexes for the new tables.

Run with: python migrations/add_case_features.py
"""

import asyncio
from sqlalchemy import text
from database import engine


async def migrate():
    statements = [
        # New columns on the existing firs table (Postgres supports IF NOT EXISTS)
        "ALTER TABLE firs ADD COLUMN IF NOT EXISTS status VARCHAR(30) DEFAULT 'new'",
        "ALTER TABLE firs ADD COLUMN IF NOT EXISTS tags JSON",
        # Backfill nulls so filtering/ordering is predictable
        "UPDATE firs SET status = 'new' WHERE status IS NULL",
        # Indexes for the collaboration tables
        "CREATE INDEX IF NOT EXISTS idx_fir_notes_fir_id ON fir_notes (fir_id)",
        "CREATE INDEX IF NOT EXISTS idx_case_events_fir_id ON case_events (fir_id)",
        "CREATE INDEX IF NOT EXISTS idx_case_events_created_at ON case_events (created_at)",
        "CREATE INDEX IF NOT EXISTS idx_notifications_officer ON notifications (officer_id, is_read)",
        "CREATE INDEX IF NOT EXISTS idx_fir_status ON firs (status)",
    ]

    async with engine.begin() as conn:
        for sql in statements:
            try:
                await conn.execute(text(sql))
                print(f"✓ {sql.split(chr(10))[0][:70]}")
            except Exception as e:
                print(f"✗ Failed: {sql[:50]}... — {e}")

    print("\n✅ Case features migration complete!")


if __name__ == "__main__":
    asyncio.run(migrate())
