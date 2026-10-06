"""
src/database/repository.py
Repository access layer providing typed, parameterized queries for vehicles,
parts, aliases, and compatibility lookups.
"""

import sqlite3
import re
from pathlib import Path
from typing import List, Optional, Union

from src.database.connection import get_db_connection, DEFAULT_DB_PATH
from src.database.models import (
    Vehicle,
    Part,
    PartAlias,
    Compatibility,
    CompatibilityDetail,
)


class PartVisionRepository:
    """
    Data Access Object (DAO) providing clean, parameterized access
    to the PartVision automotive compatibility database.
    """

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = Path(db_path or DEFAULT_DB_PATH).expanduser().resolve()

    def _get_conn(self) -> sqlite3.Connection:
        return get_db_connection(self.db_path)

    # -------------------------------------------------------------------------
    # Part Normalization
    # -------------------------------------------------------------------------
    def normalize_part_name(self, raw_name: str) -> Optional[str]:
        """
        Normalizes arbitrary user/AI input into a canonical V3 part taxonomy name.
        
        Examples:
            'Front Bumper' -> 'front_bumper'
            'front-bumper' -> 'front_bumper'
            'FRONT BUMPER' -> 'front_bumper'
            'windshield'   -> 'front_glass' (via alias)
            'headlight'    -> 'front_light' (via alias)

        Returns:
            Canonical snake_case part_name if found, else None.
        """
        if not raw_name or not isinstance(raw_name, str):
            return None

        # Clean string: lowercase, replace hyphens and multiple spaces with single underscore
        cleaned = raw_name.strip().lower()
        cleaned = re.sub(r"[\s\-]+", "_", cleaned)
        cleaned = re.sub(r"[^a-z0-9_]", "", cleaned)

        with self._get_conn() as conn:
            # 1. Direct canonical match
            row = conn.execute(
                "SELECT part_name FROM parts WHERE part_name = ?", (cleaned,)
            ).fetchone()
            if row:
                return str(row["part_name"])

            # 2. Check aliases table (case-insensitive)
            # Try raw input and cleaned input
            row = conn.execute(
                """
                SELECT p.part_name 
                FROM part_aliases a
                JOIN parts p ON a.part_id = p.id
                WHERE LOWER(a.alias) = LOWER(?) OR LOWER(a.alias) = LOWER(?)
                LIMIT 1
                """,
                (raw_name.strip(), cleaned),
            ).fetchone()
            if row:
                return str(row["part_name"])

        return None

    # -------------------------------------------------------------------------
    # Parts Operations
    # -------------------------------------------------------------------------
    def get_all_parts(self) -> List[Part]:
        """Returns all 19 canonical parts ordered by ID."""
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM parts ORDER BY id ASC")
            return [Part.model_validate(dict(r)) for r in cursor.fetchall()]

    def get_part_by_name(self, part_name: str) -> Optional[Part]:
        """
        Looks up a part by its canonical name or alias.
        """
        canonical = self.normalize_part_name(part_name)
        if not canonical:
            return None

        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM parts WHERE part_name = ?", (canonical,)
            ).fetchone()
            if row:
                return Part.model_validate(dict(row))
        return None

    def get_part_by_id(self, part_id: int) -> Optional[Part]:
        """Fetches a part record by its primary key."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM parts WHERE id = ?", (part_id,)).fetchone()
            if row:
                return Part.model_validate(dict(row))
        return None

    # -------------------------------------------------------------------------
    # Vehicles Operations
    # -------------------------------------------------------------------------
    def get_all_vehicles(self) -> List[Vehicle]:
        """Returns all vehicles in the catalog ordered by make and model."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM vehicles ORDER BY make ASC, model ASC, year_start ASC"
            )
            return [Vehicle.model_validate(dict(r)) for r in cursor.fetchall()]

    def get_vehicle_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        """Fetches a vehicle record by its primary key."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)
            ).fetchone()
            if row:
                return Vehicle.model_validate(dict(row))
        return None

    def get_vehicle_by_make_model(self, make: str, model: str) -> List[Vehicle]:
        """
        Finds vehicles matching make and model (case-insensitive substring/prefix).
        """
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM vehicles 
                WHERE LOWER(make) = LOWER(?) AND LOWER(model) = LOWER(?)
                ORDER BY year_start ASC
                """,
                (make.strip(), model.strip()),
            )
            return [Vehicle.model_validate(dict(r)) for r in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Compatibility Queries
    # -------------------------------------------------------------------------
    def get_compatible_vehicles(
        self,
        part_name: str,
        verified_only: bool = False
    ) -> List[CompatibilityDetail]:
        """
        Returns all vehicles compatible with a given part name (or alias).

        Args:
            part_name: Canonical part name or known alias.
            verified_only: If True, filters strictly for verified records (verified == 1).

        Returns:
            List of CompatibilityDetail records.
        """
        canonical = self.normalize_part_name(part_name)
        if not canonical:
            return []

        query = """
            SELECT 
                c.id AS compatibility_id,
                c.compatibility_status,
                c.notes AS compatibility_notes,
                c.source,
                c.verified,
                v.id AS v_id, v.make AS v_make, v.model AS v_model, v.generation AS v_gen,
                v.year_start AS v_ystart, v.year_end AS v_yend, v.variant AS v_var,
                v.vehicle_type AS v_type, v.notes AS v_notes,
                p.id AS p_id, p.part_name AS p_name, p.display_name AS p_dname,
                p.category AS p_cat, p.description AS p_desc
            FROM compatibility c
            JOIN vehicles v ON c.vehicle_id = v.id
            JOIN parts p ON c.part_id = p.id
            WHERE p.part_name = ?
        """
        params = [canonical]

        if verified_only:
            query += " AND c.verified = 1"

        query += " ORDER BY c.verified DESC, v.make ASC, v.model ASC, v.year_start ASC"

        with self._get_conn() as conn:
            cursor = conn.execute(query, params)
            results = []
            for r in cursor.fetchall():
                v = Vehicle(
                    id=r["v_id"],
                    make=r["v_make"],
                    model=r["v_model"],
                    generation=r["v_gen"],
                    year_start=r["v_ystart"],
                    year_end=r["v_yend"],
                    variant=r["v_var"],
                    vehicle_type=r["v_type"],
                    notes=r["v_notes"],
                )
                p = Part(
                    id=r["p_id"],
                    part_name=r["p_name"],
                    display_name=r["p_dname"],
                    category=r["p_cat"],
                    description=r["p_desc"],
                )
                detail = CompatibilityDetail(
                    compatibility_id=r["compatibility_id"],
                    vehicle=v,
                    part=p,
                    compatibility_status=r["compatibility_status"],
                    notes=r["compatibility_notes"],
                    source=r["source"],
                    verified=bool(r["verified"]),
                )
                results.append(detail)
            return results

    def get_compatible_parts(
        self,
        vehicle_id: int,
        verified_only: bool = False
    ) -> List[CompatibilityDetail]:
        """
        Returns all parts mapped to a specific vehicle.

        Args:
            vehicle_id: Target vehicle ID.
            verified_only: If True, returns only verified records.
        """
        query = """
            SELECT 
                c.id AS compatibility_id,
                c.compatibility_status,
                c.notes AS compatibility_notes,
                c.source,
                c.verified,
                v.id AS v_id, v.make AS v_make, v.model AS v_model, v.generation AS v_gen,
                v.year_start AS v_ystart, v.year_end AS v_yend, v.variant AS v_var,
                v.vehicle_type AS v_type, v.notes AS v_notes,
                p.id AS p_id, p.part_name AS p_name, p.display_name AS p_dname,
                p.category AS p_cat, p.description AS p_desc
            FROM compatibility c
            JOIN vehicles v ON c.vehicle_id = v.id
            JOIN parts p ON c.part_id = p.id
            WHERE c.vehicle_id = ?
        """
        params = [vehicle_id]

        if verified_only:
            query += " AND c.verified = 1"

        query += " ORDER BY p.category ASC, p.display_name ASC"

        with self._get_conn() as conn:
            cursor = conn.execute(query, params)
            results = []
            for r in cursor.fetchall():
                v = Vehicle(
                    id=r["v_id"],
                    make=r["v_make"],
                    model=r["v_model"],
                    generation=r["v_gen"],
                    year_start=r["v_ystart"],
                    year_end=r["v_yend"],
                    variant=r["v_var"],
                    vehicle_type=r["v_type"],
                    notes=r["v_notes"],
                )
                p = Part(
                    id=r["p_id"],
                    part_name=r["p_name"],
                    display_name=r["p_dname"],
                    category=r["p_cat"],
                    description=r["p_desc"],
                )
                detail = CompatibilityDetail(
                    compatibility_id=r["compatibility_id"],
                    vehicle=v,
                    part=p,
                    compatibility_status=r["compatibility_status"],
                    notes=r["compatibility_notes"],
                    source=r["source"],
                    verified=bool(r["verified"]),
                )
                results.append(detail)
            return results

    def check_compatibility(
        self,
        vehicle_id: int,
        part_name: str
    ) -> Optional[CompatibilityDetail]:
        """
        Determines whether a specific vehicle and part are compatible.

        Returns:
            CompatibilityDetail if a relationship exists, else None.
        """
        canonical = self.normalize_part_name(part_name)
        if not canonical:
            return None

        query = """
            SELECT 
                c.id AS compatibility_id,
                c.compatibility_status,
                c.notes AS compatibility_notes,
                c.source,
                c.verified,
                v.id AS v_id, v.make AS v_make, v.model AS v_model, v.generation AS v_gen,
                v.year_start AS v_ystart, v.year_end AS v_yend, v.variant AS v_var,
                v.vehicle_type AS v_type, v.notes AS v_notes,
                p.id AS p_id, p.part_name AS p_name, p.display_name AS p_dname,
                p.category AS p_cat, p.description AS p_desc
            FROM compatibility c
            JOIN vehicles v ON c.vehicle_id = v.id
            JOIN parts p ON c.part_id = p.id
            WHERE c.vehicle_id = ? AND p.part_name = ?
            LIMIT 1
        """
        with self._get_conn() as conn:
            r = conn.execute(query, (vehicle_id, canonical)).fetchone()
            if not r:
                return None

            v = Vehicle(
                id=r["v_id"],
                make=r["v_make"],
                model=r["v_model"],
                generation=r["v_gen"],
                year_start=r["v_ystart"],
                year_end=r["v_yend"],
                variant=r["v_var"],
                vehicle_type=r["v_type"],
                notes=r["v_notes"],
            )
            p = Part(
                id=r["p_id"],
                part_name=r["p_name"],
                display_name=r["p_dname"],
                category=r["p_cat"],
                description=r["p_desc"],
            )
            return CompatibilityDetail(
                compatibility_id=r["compatibility_id"],
                vehicle=v,
                part=p,
                compatibility_status=r["compatibility_status"],
                notes=r["compatibility_notes"],
                source=r["source"],
                verified=bool(r["verified"]),
            )
