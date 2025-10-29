#!/usr/bin/env python3
"""
GOOSE Setup Script
Initializes the database and collects initial data
"""

import sys
from database import init_db
from collectors.snapshot import collect_snapshot_data
from collectors.safe import collect_safe_data


def main():
    print("=" * 60)
    print("🪿 GOOSE Setup")
    print("Governance Oversight & Operational Speed Evaluator")
    print("=" * 60)
    print()

    # Step 1: Initialize database
    print("[1/4] Initializing database...")
    try:
        init_db()
        print("✓ Database initialized successfully\n")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        sys.exit(1)

    # Step 2: Collect Snapshot data
    print("[2/4] Collecting Snapshot data...")
    print("This may take a few minutes depending on the number of proposals...")
    try:
        collect_snapshot_data()
        print("✓ Snapshot data collected successfully\n")
    except Exception as e:
        print(f"✗ Snapshot data collection failed: {e}")
        print("You can try running: python collectors/snapshot.py")
        print()

    # Step 3: Collect Safe data
    print("[3/4] Collecting Safe multisig data...")
    try:
        collect_safe_data()
        print("✓ Safe data collected successfully\n")
    except Exception as e:
        print(f"✗ Safe data collection failed: {e}")
        print("You can try running: python collectors/safe.py")
        print()

    # Step 4: Update member names from CSV
    print("[4/4] Updating council member names...")
    try:
        from database import update_member_names
        count = update_member_names()
        print(f"✓ Updated {count} member names from CSV\n")
    except Exception as e:
        print(f"✗ Member name update failed: {e}")
        print()

    # Done
    print("=" * 60)
    print("✓ Setup complete!")
    print()
    print("To start the dashboard, run:")
    print("  python app.py")
    print()
    print("Then open your browser to:")
    print("  http://localhost:8080")
    print("=" * 60)


if __name__ == "__main__":
    main()
