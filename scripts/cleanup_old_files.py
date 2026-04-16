"""
Cleanup script — deletes uploaded files and thumbnails older than N days.
Database records are kept; only the files on disk are removed.

Usage:
    python scripts/cleanup_old_files.py           # default: 30 days
    python scripts/cleanup_old_files.py --days 7  # custom threshold
    python scripts/cleanup_old_files.py --dry-run # preview without deleting
"""

import sys
import os
import argparse
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import SessionLocal
from database.models import DetectionResult


def cleanup(days: int = 30, dry_run: bool = False) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    db = SessionLocal()

    try:
        old_records = (
            db.query(DetectionResult)
            .filter(DetectionResult.created_at < cutoff)
            .all()
        )

        if not old_records:
            print(f"No records older than {days} days found.")
            return

        print(f"Found {len(old_records)} record(s) older than {days} days.")

        deleted_files = 0
        missing_files = 0

        for record in old_records:
            for path in [record.file_path, record.thumbnail_path]:
                if not path:
                    continue
                if os.path.exists(path):
                    if not dry_run:
                        os.remove(path)
                    print(f"  {'[DRY RUN] Would delete' if dry_run else 'Deleted'}: {path}")
                    deleted_files += 1
                else:
                    missing_files += 1

        print(
            f"\nSummary: {deleted_files} file(s) "
            f"{'would be ' if dry_run else ''}deleted, "
            f"{missing_files} already missing."
        )

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up old uploaded files.")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Delete files older than this many days (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be deleted without actually deleting",
    )
    args = parser.parse_args()
    cleanup(days=args.days, dry_run=args.dry_run)
