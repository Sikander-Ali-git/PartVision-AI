"""
tests/test_database.py
Comprehensive test suite for PartVision AI SQLite Compatibility Database (Milestone 6B).
Tests schema, foreign keys, constraints, normalization, repository operations, and domain logic.
"""

import sqlite3
import pytest
import tempfile
from pathlib import Path

from src.database.connection import get_db_connection, db_session, SCHEMA_SQL
from src.database.models import (
    Vehicle,
    Part,
    PartAlias,
    Compatibility,
    CompatibilityDetail,
)
from src.database.repository import PartVisionRepository
from scripts.init_database import init_database


@pytest.fixture(scope="session")
def temp_db_path():
    """Creates a temporary SQLite database initialized with full schema and seed data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_file = Path(f.name)

    # Initialize schema and seed data using reproducible script
    init_database(db_file)

    yield db_file

    # Cleanup temporary database and any WAL/SHM companion files
    for ext in ["", "-wal", "-shm"]:
        p = Path(str(db_file) + ext)
        if p.exists():
            try:
                p.unlink()
            except OSError:
                pass


@pytest.fixture
def repo(temp_db_path):
    """Provides a PartVisionRepository bound to the isolated temporary test database."""
    return PartVisionRepository(db_path=temp_db_path)


# =============================================================================
# 1. Database Connection & Schema Configuration Tests
# =============================================================================

def test_sqlite_pragmas(temp_db_path):
    """Verifies that foreign keys and WAL mode are enforced."""
    conn = get_db_connection(temp_db_path)
    try:
        fk_val = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk_val == 1, "Foreign keys must be enabled (PRAGMA foreign_keys = ON)"

        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        assert journal_mode.lower() == "wal", "WAL mode must be active"
    finally:
        conn.close()


def test_schema_tables_and_indexes_exist(temp_db_path):
    """Verifies that all 4 required tables and expected indexes exist."""
    conn = get_db_connection(temp_db_path)
    try:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            ).fetchall()
        ]
        assert "vehicles" in tables
        assert "parts" in tables
        assert "compatibility" in tables
        assert "part_aliases" in tables

        indexes = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name;"
            ).fetchall()
        ]
        assert "idx_vehicles_make_model" in indexes
        assert "idx_parts_part_name" in indexes
        assert "idx_compatibility_vehicle_part" in indexes
        assert "idx_compatibility_part_vehicle" in indexes
        assert "idx_part_aliases_alias" in indexes
    finally:
        conn.close()


# =============================================================================
# 2. Schema Constraints & Foreign Key Enforcement Tests
# =============================================================================

def test_foreign_key_constraint_enforcement(temp_db_path):
    """Verifies that inserting a compatibility record with a nonexistent vehicle/part fails."""
    conn = get_db_connection(temp_db_path)
    try:
        # Nonexistent vehicle_id
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO compatibility (vehicle_id, part_id, compatibility_status, source, verified)
                VALUES (999999, 1, 'compatible', 'Test', 1)
                """
            )

        # Nonexistent part_id
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO compatibility (vehicle_id, part_id, compatibility_status, source, verified)
                VALUES (1, 999999, 'compatible', 'Test', 1)
                """
            )
    finally:
        conn.close()


def test_unique_compatibility_constraint(temp_db_path):
    """Verifies that duplicate (vehicle_id, part_id) pairings are rejected."""
    conn = get_db_connection(temp_db_path)
    try:
        # Swift 3rd Gen (1) and front_bumper (6) is already seeded
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO compatibility (vehicle_id, part_id, compatibility_status, source, verified)
                VALUES (1, 6, 'duplicate_entry', 'Duplicate Test', 0)
                """
            )
    finally:
        conn.close()


def test_unique_part_name_constraint(temp_db_path):
    """Verifies that duplicate canonical part_name cannot be inserted."""
    conn = get_db_connection(temp_db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO parts (part_name, display_name, category)
                VALUES ('front_bumper', 'Duplicate Front Bumper', 'Exterior Body')
                """
            )
    finally:
        conn.close()


def test_cascade_delete_enforcement(temp_db_path):
    """Verifies that cascading deletion operates properly on foreign keys."""
    conn = get_db_connection(temp_db_path)
    try:
        # Create a dummy vehicle and part, link them, then delete the vehicle
        conn.execute(
            "INSERT INTO vehicles (make, model, year_start) VALUES ('TestMake', 'TestModel', 2025)"
        )
        test_v_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            """
            INSERT INTO compatibility (vehicle_id, part_id, compatibility_status, source, verified)
            VALUES (?, 1, 'compatible', 'Test Cascade', 0)
            """,
            (test_v_id,),
        )
        conn.commit()

        # Verify entry exists
        row = conn.execute(
            "SELECT COUNT(*) FROM compatibility WHERE vehicle_id = ?", (test_v_id,)
        ).fetchone()[0]
        assert row == 1

        # Delete dummy vehicle
        conn.execute("DELETE FROM vehicles WHERE id = ?", (test_v_id,))
        conn.commit()

        # Compatibility row should cascade delete
        row_after = conn.execute(
            "SELECT COUNT(*) FROM compatibility WHERE vehicle_id = ?", (test_v_id,)
        ).fetchone()[0]
        assert row_after == 0
    finally:
        conn.close()


# =============================================================================
# 3. Pydantic Models & Domain Logic Tests
# =============================================================================

def test_vehicle_model_display_name():
    """Tests Vehicle display_name property generation."""
    v1 = Vehicle(
        id=1,
        make="Maruti Suzuki",
        model="Swift",
        generation="3rd Gen",
        year_start=2018,
        year_end=2024,
    )
    assert v1.display_name == "Maruti Suzuki Swift (3rd Gen) [2018–2024]"

    v2 = Vehicle(
        id=2,
        make="Mahindra",
        model="Scorpio-N",
        generation="Z8",
        year_start=2022,
        year_end=None,
    )
    assert v2.display_name == "Mahindra Scorpio-N (Z8) [2022–Present]"


def test_part_model_attributes():
    """Tests Part model structure."""
    part = Part(
        id=5,
        part_name="fender",
        display_name="Front Fender / Wing",
        category="Exterior Body",
        description="Side quarter panel over the wheel.",
    )
    assert part.part_name == "fender"
    assert part.category == "Exterior Body"


def test_compatibility_detail_model():
    """Tests CompatibilityDetail nested representation."""
    v = Vehicle(id=1, make="Hyundai", model="Creta")
    p = Part(id=1, part_name="hood", display_name="Hood", category="Exterior Body")
    detail = CompatibilityDetail(
        compatibility_id=10,
        vehicle=v,
        part=p,
        compatibility_status="direct_fit",
        notes="OEM replacement",
        source="Hyundai WPC",
        verified=True,
    )
    assert detail.is_verified is True
    assert detail.vehicle.make == "Hyundai"
    assert detail.part.part_name == "hood"


# =============================================================================
# 4. Taxonomy & Normalization Tests
# =============================================================================

def test_taxonomy_all_19_classes_present(repo):
    """Verifies all 19 PartVision V3 classes are present in the database."""
    parts = repo.get_all_parts()
    assert len(parts) == 19
    names = {p.part_name for p in parts}

    expected_v3_classes = {
        "back_bumper", "back_door", "back_glass", "back_light", "fender",
        "front_bumper", "front_door", "front_glass", "front_light", "grille",
        "hood", "mirror", "quarter_panel", "rocker_panel", "roof",
        "side_window", "tailgate", "trunk", "wheel"
    }
    assert names == expected_v3_classes


@pytest.mark.parametrize(
    "raw_input,expected_canonical",
    [
        # Exact canonical
        ("front_bumper", "front_bumper"),
        ("hood", "hood"),
        ("wheel", "wheel"),
        # Title case and spaces
        ("Front Bumper", "front_bumper"),
        ("Back Door", "back_door"),
        ("Quarter Panel", "quarter_panel"),
        # Hyphens and uppercase
        ("FRONT-BUMPER", "front_bumper"),
        ("rocker-panel", "rocker_panel"),
        # Colloquial synonyms and search aliases
        ("headlight", "front_light"),
        ("headlamp", "front_light"),
        ("taillight", "back_light"),
        ("tail lamp", "back_light"),
        ("windshield", "front_glass"),
        ("front windscreen", "front_glass"),
        ("rear windscreen", "back_glass"),
        ("bonnet", "hood"),
        ("engine cover", "hood"),
        ("boot", "trunk"),
        ("dicky", "trunk"),
        ("boot lid", "trunk"),
        ("rear hatch", "tailgate"),
        ("hatchback door", "tailgate"),
        ("side view mirror", "mirror"),
        ("wing mirror", "mirror"),
        ("rim", "wheel"),
        ("alloy wheel", "wheel"),
    ],
)
def test_part_name_normalization(repo, raw_input, expected_canonical):
    """Tests normalization of canonical names, casing, and aliases."""
    normalized = repo.normalize_part_name(raw_input)
    assert normalized == expected_canonical


def test_normalization_invalid_inputs(repo):
    """Tests normalization handling of nonexistent or empty inputs."""
    assert repo.normalize_part_name("") is None
    assert repo.normalize_part_name("   ") is None
    assert repo.normalize_part_name("nonexistent_unknown_gadget_xyz") is None
    assert repo.normalize_part_name(None) is None  # type: ignore


# =============================================================================
# 5. Vehicle Operations Tests
# =============================================================================

def test_get_all_vehicles(repo):
    """Verifies all 8 seeded vehicles are returned."""
    vehicles = repo.get_all_vehicles()
    assert len(vehicles) == 8
    makes = {v.make for v in vehicles}
    assert "Maruti Suzuki" in makes
    assert "Hyundai" in makes
    assert "Tata" in makes
    assert "Mahindra" in makes
    assert "Toyota" in makes
    assert "Honda" in makes


def test_get_vehicle_by_id(repo):
    """Verifies retrieval of vehicle by ID."""
    v = repo.get_vehicle_by_id(1)
    assert v is not None
    assert v.make == "Maruti Suzuki"
    assert v.model == "Swift"
    assert "3rd Gen" in v.generation

    assert repo.get_vehicle_by_id(9999) is None


def test_get_vehicle_by_make_model(repo):
    """Verifies retrieval of vehicles by make and model."""
    results = repo.get_vehicle_by_make_model("maruti suzuki", "swift")
    assert len(results) == 2  # 3rd Gen and 4th Gen
    gens = {r.generation for r in results}
    assert any("3rd Gen" in g for g in gens)
    assert any("4th Gen" in g for g in gens)

    # Nonexistent vehicle
    assert len(repo.get_vehicle_by_make_model("Ferrari", "Enzo")) == 0


# =============================================================================
# 6. Automotive Compatibility Query Tests
# =============================================================================

def test_get_compatible_vehicles_for_part(repo):
    """Verifies vehicle lookup for a canonical part."""
    # Front bumper should be compatible with multiple vehicles
    results = repo.get_compatible_vehicles("front_bumper")
    assert len(results) >= 5

    # Check that alias works as well
    results_alias = repo.get_compatible_vehicles("front bumper")
    assert len(results_alias) == len(results)

    # Check verified_only filter
    verified_only = repo.get_compatible_vehicles("front_bumper", verified_only=True)
    assert all(r.verified is True for r in verified_only)


def test_body_style_differentiation_trunk_vs_tailgate(repo):
    """
    CRITICAL AUTOMOTIVE RULE:
    - Sedans (Honda City) have a 'trunk' (compatible) and 'tailgate' (incompatible).
    - Hatchbacks/SUVs (Swift, Creta, Nexon) have a 'tailgate' (compatible) and 'trunk' (incompatible).
    """
    # 1. Honda City Sedan (id=8)
    city_vehicles = repo.get_vehicle_by_make_model("Honda", "City")
    assert len(city_vehicles) == 1
    city_id = city_vehicles[0].id

    city_trunk = repo.check_compatibility(city_id, "trunk")
    assert city_trunk is not None
    assert city_trunk.compatibility_status == "compatible"

    city_tailgate = repo.check_compatibility(city_id, "tailgate")
    assert city_tailgate is not None
    assert city_tailgate.compatibility_status == "incompatible"

    # 2. Maruti Suzuki Swift 3rd Gen (id=1)
    swift_vehicles = repo.get_vehicle_by_make_model("Maruti Suzuki", "Swift")
    swift_3g = next(v for v in swift_vehicles if "3rd Gen" in v.generation)

    swift_tailgate = repo.check_compatibility(swift_3g.id, "tailgate")
    assert swift_tailgate is not None
    assert swift_tailgate.compatibility_status == "compatible"

    swift_trunk = repo.check_compatibility(swift_3g.id, "trunk")
    assert swift_trunk is not None
    assert swift_trunk.compatibility_status == "incompatible"


def test_generational_incompatibility(repo):
    """
    Verifies that generational incompatibilities are preserved:
    Swift 3rd Gen bumper vs Swift 4th Gen.
    """
    # Swift 3rd Gen has compatible front_bumper
    swift_3g = repo.get_vehicle_by_id(1)
    comp_3g = repo.check_compatibility(swift_3g.id, "front_bumper")
    assert comp_3g is not None
    assert comp_3g.compatibility_status == "compatible"

    # Swift 4th Gen front bumper has distinct fitment note
    swift_4g = repo.get_vehicle_by_id(2)
    comp_4g = repo.check_compatibility(swift_4g.id, "front_bumper")
    assert comp_4g is not None
    assert "4th Gen" in comp_4g.notes or "Redesigned" in comp_4g.notes


def test_get_compatible_parts_for_vehicle(repo):
    """Verifies querying all parts for a specific vehicle."""
    parts_for_swift = repo.get_compatible_parts(1)
    assert len(parts_for_swift) >= 6

    compatible_names = {
        d.part.part_name for d in parts_for_swift if d.compatibility_status == "compatible"
    }
    incompatible_names = {
        d.part.part_name for d in parts_for_swift if d.compatibility_status == "incompatible"
    }

    assert "front_bumper" in compatible_names
    assert "hood" in compatible_names
    assert "tailgate" in compatible_names
    assert "trunk" in incompatible_names


def test_verified_vs_demonstration_status(repo):
    """Verifies that verified and demonstration/unverified records are tracked accurately."""
    all_swift_3g = repo.get_compatible_parts(1, verified_only=False)
    verified_swift_3g = repo.get_compatible_parts(1, verified_only=True)

    # Rocker panel on Swift 3rd Gen is an unverified demonstration record
    has_unverified = any(not d.verified for d in all_swift_3g)
    assert has_unverified is True, "Should contain at least one demonstration record"
    assert len(verified_swift_3g) < len(all_swift_3g)
