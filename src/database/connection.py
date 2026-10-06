"""
src/database/connection.py
SQLite connection manager with WAL mode, foreign key enforcement, and transactions.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Union, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "partvision.db"

SCHEMA_SQL = """
-- 1. Vehicles Table
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    generation TEXT,
    year_start INTEGER,
    year_end INTEGER,
    variant TEXT,
    vehicle_type TEXT,
    notes TEXT
);

-- 2. Parts Table
CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT
);

-- 3. Compatibility Table
CREATE TABLE IF NOT EXISTS compatibility (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    part_id INTEGER NOT NULL,
    compatibility_status TEXT NOT NULL,
    notes TEXT,
    source TEXT NOT NULL,
    verified INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE,
    UNIQUE(vehicle_id, part_id)
);

-- 4. Part Aliases Table
CREATE TABLE IF NOT EXISTS part_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id INTEGER NOT NULL,
    alias TEXT UNIQUE NOT NULL,
    FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE
);

-- Indexes for high-frequency queries
CREATE INDEX IF NOT EXISTS idx_vehicles_make_model ON vehicles(make, model);
CREATE INDEX IF NOT EXISTS idx_parts_part_name ON parts(part_name);
CREATE INDEX IF NOT EXISTS idx_compatibility_vehicle_part ON compatibility(vehicle_id, part_id);
CREATE INDEX IF NOT EXISTS idx_compatibility_part_vehicle ON compatibility(part_id, vehicle_id);
CREATE INDEX IF NOT EXISTS idx_part_aliases_alias ON part_aliases(alias);
"""


def get_db_connection(
    db_path: Optional[Union[str, Path]] = None
) -> sqlite3.Connection:
    """
    Creates and configures an SQLite database connection.
    Enforces WAL mode and foreign keys.

    Args:
        db_path: Path to SQLite database file. Defaults to data/partvision.db.

    Returns:
        Configured sqlite3.Connection object with Row factory enabled.
    """
    path = Path(db_path or DEFAULT_DB_PATH).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row

    # Enforce SQLite engine configurations
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn


@contextmanager
def db_session(
    db_path: Optional[Union[str, Path]] = None
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager providing an atomic SQLite database session.
    Commits on successful completion, rolls back on exception.
    """
    conn = get_db_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
