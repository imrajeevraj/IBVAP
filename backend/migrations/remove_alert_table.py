#!/usr/bin/env python3
"""Migration: Remove unused alerts table

This migration removes the alerts table which is no longer used.
All alert functionality is now handled by the security_events table.

Run with: python backend/migrations/remove_alert_table.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, text, inspect


def get_database_url():
    """Get the database URL from environment or use default."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./ibvap.db")
    return db_url


def migrate():
    """Remove the alerts table."""
    db_url = get_database_url()
    engine = create_engine(db_url)
    
    print(f"Connecting to database: {db_url}")
    
    with engine.connect() as conn:
        # Check if alerts table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if "alerts" in tables:
            print("[INFO] Found alerts table")
            print("  Dropping alerts table...")
            conn.execute(text("DROP TABLE IF EXISTS alerts"))
            conn.commit()
            print("[SUCCESS] Alerts table successfully removed")
        else:
            print("[INFO] Alerts table does not exist (already removed or never created)")
    
    print("\nMigration complete!")
    return True


if __name__ == "__main__":
    try:
        success = migrate()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
