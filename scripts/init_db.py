"""
Database initialisation script.

Run this once before starting the server for the first time:
    python scripts/init_db.py

Run with --reset to drop and recreate all tables (WARNING: deletes all data):
    python scripts/init_db.py --reset
"""

import sys
import os

# Make sure project root is on the path when running this script directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import engine, init_db
from database.models import Base


def reset_db() -> None:
    """Drop all tables and recreate them. Deletes all stored data."""
    print("WARNING: Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")
    init_db()
    print("Tables recreated.")


if __name__ == "__main__":
    if "--reset" in sys.argv:
        confirm = input("This will delete ALL data. Type 'yes' to confirm: ")
        if confirm.strip().lower() == "yes":
            reset_db()
        else:
            print("Aborted.")
    else:
        init_db()
        print("Database initialised successfully.")
