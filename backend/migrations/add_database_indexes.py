"""
Database Migration: Add Performance Indexes
-------------------------------------------
Adds indexes to frequently-queried columns to improve performance.

Run with: python migrations/add_database_indexes.py
"""

import asyncio
from sqlalchemy import text
from database import engine


async def add_indexes():
    """Add indexes to improve query performance."""

    indexes = [
        # FIR table indexes
        {
            "name": "idx_fir_crime_type",
            "table": "firs",
            "columns": ["crime_type"],
            "description": "Speed up filtering by crime type",
        },
        {
            "name": "idx_fir_police_station",
            "table": "firs",
            "columns": ["police_station"],
            "description": "Speed up filtering by police station",
        },
        {
            "name": "idx_fir_number",
            "table": "firs",
            "columns": ["fir_number"],
            "description": "Speed up FIR number lookup",
        },
        {
            "name": "idx_fir_severity",
            "table": "firs",
            "columns": ["severity"],
            "description": "Speed up filtering by severity",
        },
        {
            "name": "idx_fir_created_at",
            "table": "firs",
            "columns": ["created_at"],
            "description": "Speed up date-based queries and sorting",
        },
        # Accused table indexes
        {
            "name": "idx_accused_fir_id",
            "table": "accused",
            "columns": ["fir_id"],
            "description": "Speed up FIR → Accused relationship queries",
        },
        {
            "name": "idx_accused_name",
            "table": "accused",
            "columns": ["name"],
            "description": "Speed up search by accused name",
        },
        # Officer table indexes
        {
            "name": "idx_officer_badge_number",
            "table": "officers",
            "columns": ["badge_number"],
            "description": "Speed up officer login lookup",
        },
        # Audit log indexes
        {
            "name": "idx_audit_officer_id",
            "table": "audit_logs",
            "columns": ["officer_id"],
            "description": "Speed up audit history for officers",
        },
        {
            "name": "idx_audit_resource",
            "table": "audit_logs",
            "columns": ["resource_type", "resource_id"],
            "description": "Speed up access history lookup",
        },
        {
            "name": "idx_audit_created_at",
            "table": "audit_logs",
            "columns": ["created_at"],
            "description": "Speed up date-range audit queries",
        },
        # Error log indexes
        {
            "name": "idx_error_component",
            "table": "error_logs",
            "columns": ["component"],
            "description": "Speed up error lookup by component",
        },
        {
            "name": "idx_error_created_at",
            "table": "error_logs",
            "columns": ["created_at"],
            "description": "Speed up recent error queries",
        },
        # Performance metric indexes
        {
            "name": "idx_metric_component_operation",
            "table": "performance_metrics",
            "columns": ["component", "operation"],
            "description": "Speed up performance metric aggregation",
        },
        {
            "name": "idx_metric_created_at",
            "table": "performance_metrics",
            "columns": ["created_at"],
            "description": "Speed up time-range metric queries",
        },
        # Security event indexes
        {
            "name": "idx_security_event_type",
            "table": "security_events",
            "columns": ["event_type"],
            "description": "Speed up security event filtering",
        },
        {
            "name": "idx_security_severity",
            "table": "security_events",
            "columns": ["severity"],
            "description": "Speed up critical event detection",
        },
        {
            "name": "idx_security_created_at",
            "table": "security_events",
            "columns": ["created_at"],
            "description": "Speed up recent security event queries",
        },
    ]

    async with engine.begin() as conn:
        for idx in indexes:
            try:
                # Build CREATE INDEX statement
                if len(idx["columns"]) == 1:
                    sql = f"""
                    CREATE INDEX IF NOT EXISTS {idx['name']}
                    ON {idx['table']} ({', '.join(idx['columns'])})
                    """
                else:
                    sql = f"""
                    CREATE INDEX IF NOT EXISTS {idx['name']}
                    ON {idx['table']} ({', '.join(idx['columns'])})
                    """

                await conn.execute(text(sql))
                print(f"✓ Created index: {idx['name']} — {idx['description']}")
            except Exception as e:
                print(f"✗ Failed to create index {idx['name']}: {e}")

    print("\n✅ Database indexes created successfully!")


async def drop_indexes():
    """Drop all created indexes (for cleanup)."""

    index_names = [
        "idx_fir_crime_type",
        "idx_fir_police_station",
        "idx_fir_number",
        "idx_fir_severity",
        "idx_fir_created_at",
        "idx_accused_fir_id",
        "idx_accused_name",
        "idx_officer_badge_number",
        "idx_audit_officer_id",
        "idx_audit_resource",
        "idx_audit_created_at",
        "idx_error_component",
        "idx_error_created_at",
        "idx_metric_component_operation",
        "idx_metric_created_at",
        "idx_security_event_type",
        "idx_security_severity",
        "idx_security_created_at",
    ]

    async with engine.begin() as conn:
        for idx_name in index_names:
            try:
                sql = f"DROP INDEX IF EXISTS {idx_name}"
                await conn.execute(text(sql))
                print(f"✓ Dropped index: {idx_name}")
            except Exception as e:
                print(f"✗ Failed to drop index {idx_name}: {e}")

    print("\n✅ Indexes dropped!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        asyncio.run(drop_indexes())
    else:
        asyncio.run(add_indexes())
