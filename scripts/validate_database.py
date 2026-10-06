#!/usr/bin/env python3
"""
scripts/validate_database.py
Comprehensive integrity and validation suite for the PartVision SQLite database.

Verifies:
- Database existence and SQLite connectivity
- WAL mode and foreign-key enforcement
- 19 canonical parts completeness and uniqueness
- Absence of orphan compatibility records
- Uniqueness of (vehicle_id, part_id) pairs
- Non-null source attribution and valid verification flags
- Sensible chronological year spans
- Non-null required fields
"""

import sys
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_db_connection, DEFAULT_DB_PATH
from src.inference.utils import FROZEN_V3_CLASSES


def validate_database(db_path: Path = DEFAULT_DB_PATH) -> bool:
    print("=" * 70)
    print("PartVision AI — Milestone 6B: Database Integrity Validation")
    print(f"Target Database: {db_path}")
    print("=" * 70)

    checks_passed = 0
    checks_total = 12
    all_ok = True

    def record_check(name: str, passed: bool, detail: str = ""):
        nonlocal checks_passed, all_ok
        status = "PASS" if passed else "FAIL"
        if passed:
            checks_passed += 1
        else:
            all_ok = False
        print(f"[{status}] {name:<42} : {detail}")

    # Check 1: File Existence
    if not db_path.exists():
        record_check("Database File Existence", False, f"File missing at {db_path}")
        return False
    size_kb = db_path.stat().st_size / 1024
    record_check("Database File Existence", True, f"{size_kb:.2f} KB on disk")

    # Check 2: SQLite Connection
    try:
        conn = get_db_connection(db_path)
        record_check("SQLite Connectivity", True, f"SQLite {sqlite3.sqlite_version}")
    except Exception as e:
        record_check("SQLite Connectivity", False, str(e))
        return False

    try:
        # Check 3: WAL Mode
        mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        record_check("WAL Mode Active", mode.lower() == "wal", f"journal_mode = {mode}")

        # Check 4: Foreign Keys Enforcement
        fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        record_check("Foreign Keys Enforced", fk == 1, f"foreign_keys = {fk}")

        # Check 5: 19 Canonical Parts Present
        rows = conn.execute("SELECT part_name FROM parts ORDER BY id ASC;").fetchall()
        part_names = [r["part_name"] for r in rows]
        parts_match = (set(part_names) == set(FROZEN_V3_CLASSES)) and (len(part_names) == 19)
        record_check("19 Canonical Parts Present", parts_match, f"{len(part_names)} / 19 verified")

        # Check 6: Duplicate Part Names
        dup_parts = conn.execute(
            "SELECT part_name, COUNT(*) FROM parts GROUP BY part_name HAVING COUNT(*) > 1;"
        ).fetchall()
        record_check("Part Name Uniqueness", len(dup_parts) == 0, f"{len(dup_parts)} duplicate names")

        # Check 7: No Orphan Compatibility Records
        orphan_v = conn.execute(
            """
            SELECT COUNT(*) FROM compatibility c 
            LEFT JOIN vehicles v ON c.vehicle_id = v.id 
            WHERE v.id IS NULL;
            """
        ).fetchone()[0]
        orphan_p = conn.execute(
            """
            SELECT COUNT(*) FROM compatibility c 
            LEFT JOIN parts p ON c.part_id = p.id 
            WHERE p.id IS NULL;
            """
        ).fetchone()[0]
        record_check("Orphan Record Check", (orphan_v == 0 and orphan_p == 0), f"Orphan vehicles: {orphan_v}, Orphan parts: {orphan_p}")

        # Check 8: Duplicate Compatibility Relationships
        dup_compat = conn.execute(
            """
            SELECT vehicle_id, part_id, COUNT(*) 
            FROM compatibility 
            GROUP BY vehicle_id, part_id 
            HAVING COUNT(*) > 1;
            """
        ).fetchall()
        record_check("Compatibility Uniqueness", len(dup_compat) == 0, f"{len(dup_compat)} duplicate relationships")

        # Check 9: Source Attribution Integrity
        empty_src = conn.execute(
            "SELECT COUNT(*) FROM compatibility WHERE source IS NULL OR TRIM(source) = '';"
        ).fetchone()[0]
        record_check("Source Attribution Complete", empty_src == 0, f"{empty_src} missing sources")

        # Check 10: Verification Flag Integrity (strictly 0 or 1)
        invalid_ver = conn.execute(
            "SELECT COUNT(*) FROM compatibility WHERE verified NOT IN (0, 1);"
        ).fetchone()[0]
        v_count = conn.execute("SELECT COUNT(*) FROM compatibility WHERE verified = 1;").fetchone()[0]
        u_count = conn.execute("SELECT COUNT(*) FROM compatibility WHERE verified = 0;").fetchone()[0]
        record_check("Verification Flags Valid", invalid_ver == 0, f"Verified: {v_count}, Demo/Unverified: {u_count}")

        # Check 11: Sensible Vehicle Year Ranges
        bad_years = conn.execute(
            """
            SELECT COUNT(*) FROM vehicles 
            WHERE year_start IS NOT NULL AND (year_start < 1950 OR (year_end IS NOT NULL AND year_end < year_start));
            """
        ).fetchone()[0]
        record_check("Vehicle Year Ranges Sensible", bad_years == 0, f"{bad_years} invalid ranges")

        # Check 12: Non-Null Required Fields
        bad_req = conn.execute(
            """
            SELECT 
                (SELECT COUNT(*) FROM vehicles WHERE make IS NULL OR model IS NULL) +
                (SELECT COUNT(*) FROM parts WHERE part_name IS NULL OR display_name IS NULL OR category IS NULL) +
                (SELECT COUNT(*) FROM compatibility WHERE compatibility_status IS NULL);
            """
        ).fetchone()[0]
        record_check("Required Fields Non-Null", bad_req == 0, f"{bad_req} null required values")

    finally:
        conn.close()

    print("-" * 70)
    print(f"VALIDATION SUMMARY: {checks_passed} / {checks_total} Checks Passed")
    print("STATUS: " + ("ALL CHECKS PASSED — DATABASE HEALTHY" if all_ok else "INTEGRITY ISSUES DETECTED"))
    print("=" * 70)

    return all_ok


if __name__ == "__main__":
    success = validate_database()
    sys.exit(0 if success else 1)
