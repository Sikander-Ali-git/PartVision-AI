"""
scripts/demo_database.py
Interactive CLI demonstration of PartVision AI Automotive Compatibility Database (Milestone 6B).
Demonstrates visual part mapping, vehicle lookup, body-style validation, aliases, and source verification.
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.repository import PartVisionRepository
from src.database.connection import DEFAULT_DB_PATH


def print_header(title: str):
    print("\n" + "=" * 76)
    print(f" {title.upper()}")
    print("=" * 76)


def print_section(title: str):
    print("\n" + "-" * 76)
    print(f" ► {title}")
    print("-" * 76)


def run_demo():
    print_header("PartVision AI — Milestone 6B: Compatibility Database Demonstration")
    print(f"Database Target: {DEFAULT_DB_PATH}")

    repo = PartVisionRepository()

    # -------------------------------------------------------------------------
    # 1. Database Overview & Taxonomy Summary
    # -------------------------------------------------------------------------
    print_section("1. Canonical Taxonomy & Category Breakdown (19 V3 Classes)")
    parts = repo.get_all_parts()
    categories = {}
    for p in parts:
        categories.setdefault(p.category, []).append(p.part_name)

    for cat, p_list in categories.items():
        print(f"  • {cat:16} ({len(p_list)} parts): {', '.join(p_list)}")
    print(f"\n  Total Indexed Parts: {len(parts)} / 19 canonical V3 classes.")

    # -------------------------------------------------------------------------
    # 2. Flow 1: Detected Part -> Compatible Vehicles
    # -------------------------------------------------------------------------
    print_section("2. Flow 1: Vision Detection -> Compatible Vehicles Lookup")
    detected_part = "front_bumper"
    print(f"Simulating AI Detection: '{detected_part}'")

    start_t = time.perf_counter()
    compat_vehicles = repo.get_compatible_vehicles(detected_part)
    elapsed_ms = (time.perf_counter() - start_t) * 1000

    print(f"Found {len(compat_vehicles)} vehicle fitment records in {elapsed_ms:.2f} ms:\n")
    print(f"  {'Vehicle Make & Model':<32} {'Status':<12} {'Verified':<10} {'Source'}")
    print("  " + "-" * 72)
    for c in compat_vehicles:
        v_title = f"{c.vehicle.make} {c.vehicle.model} ({c.vehicle.generation or 'All'})"
        ver_badge = "OEM" if c.verified else "DEMO"
        print(f"  {v_title:<32} {c.compatibility_status:<12} {ver_badge:<10} {c.source}")

    # -------------------------------------------------------------------------
    # 3. Flow 2: Part Name Normalization & Search Aliases
    # -------------------------------------------------------------------------
    print_section("3. Flow 2: Colloquial Search Aliases -> Canonical Part Mapping")
    test_queries = [
        "windshield",
        "rear windscreen",
        "headlight",
        "bonnet",
        "dicky",
        "side view mirror",
        "alloy wheel",
        "front-bumper",
    ]

    print(f"  {'Input Query':<20} {'→':<3} {'Canonical Taxonomy':<18} {'Category'}")
    print("  " + "-" * 65)
    for q in test_queries:
        canonical = repo.normalize_part_name(q)
        if canonical:
            part_obj = repo.get_part_by_name(canonical)
            cat = part_obj.category if part_obj else "Unknown"
            print(f"  {q:<20} {'→':<3} {canonical:<18} {cat}")
        else:
            print(f"  {q:<20} {'→':<3} {'[UNRECOGNIZED]':<18}")

    # -------------------------------------------------------------------------
    # 4. Flow 3: Body-Style Differentiation (Sedan vs Hatchback)
    # -------------------------------------------------------------------------
    print_section("4. Flow 3: Body-Style Specificity (Tailgate vs Trunk)")
    print("Testing automotive architecture rules:")
    print("  - Hatchbacks/SUVs have tailgates; sedans do NOT have tailgates.")
    print("  - Sedans have trunk lids; hatchbacks do NOT have trunk lids.\n")

    # Vehicle 1: Swift Hatchback
    swift = repo.get_vehicle_by_id(1)
    swift_tailgate = repo.check_compatibility(swift.id, "tailgate")
    swift_trunk = repo.check_compatibility(swift.id, "trunk")

    print(f"Vehicle: {swift.display_name} (Body: {swift.vehicle_type})")
    print(f"  • Part: tailgate → Status: {swift_tailgate.compatibility_status.upper()} ({swift_tailgate.notes})")
    print(f"  • Part: trunk    → Status: {swift_trunk.compatibility_status.upper()} ({swift_trunk.notes})")

    # Vehicle 8: Honda City Sedan
    city = repo.get_vehicle_by_id(8)
    city_tailgate = repo.check_compatibility(city.id, "tailgate")
    city_trunk = repo.check_compatibility(city.id, "trunk")

    print(f"\nVehicle: {city.display_name} (Body: {city.vehicle_type})")
    print(f"  • Part: trunk    → Status: {city_trunk.compatibility_status.upper()} ({city_trunk.notes})")
    print(f"  • Part: tailgate → Status: {city_tailgate.compatibility_status.upper()} ({city_tailgate.notes})")

    # -------------------------------------------------------------------------
    # 5. Flow 4: Generational Incompatibility
    # -------------------------------------------------------------------------
    print_section("5. Flow 4: Generational Facelift & Inter-Generation Fitment")
    swift_3g = repo.get_vehicle_by_id(1)
    swift_4g = repo.get_vehicle_by_id(2)

    comp_3g = repo.check_compatibility(swift_3g.id, "front_bumper")
    comp_4g = repo.check_compatibility(swift_4g.id, "front_bumper")

    print(f"Part: 'front_bumper'")
    print(f"  • {swift_3g.display_name}:")
    print(f"    Fitment: {comp_3g.compatibility_status} | Note: {comp_3g.notes}")
    print(f"  • {swift_4g.display_name}:")
    print(f"    Fitment: {comp_4g.compatibility_status} | Note: {comp_4g.notes}")

    # -------------------------------------------------------------------------
    # 6. Flow 5: Source Attribution & Trust Breakdown
    # -------------------------------------------------------------------------
    print_section("6. Flow 5: Data Provenance & Trust Hierarchy")
    all_compat = repo.get_compatible_parts(1, verified_only=False)
    print(f"Catalog for {swift_3g.display_name}:")
    for item in all_compat:
        status_tag = f"[{item.compatibility_status.upper()}]"
        trust_tag = "[VERIFIED OEM]" if item.verified else "[DEMO RECORD]"
        print(f"  {status_tag:<14} {trust_tag:<16} {item.part.display_name:<20} Source: {item.source}")

    # -------------------------------------------------------------------------
    # 7. Flow 6: Performance Benchmark
    # -------------------------------------------------------------------------
    print_section("7. Performance Benchmark (1,000 Iterations)")
    iterations = 1000
    t0 = time.perf_counter()
    for _ in range(iterations):
        repo.check_compatibility(1, "front_bumper")
    t1 = time.perf_counter()
    avg_us = ((t1 - t0) / iterations) * 1_000_000

    print(f"  Direct Compatibility Check: {avg_us:.2f} µs / query ({iterations / (t1 - t0):,.0f} queries/sec)")
    print(f"  Sub-millisecond latency easily supports high-concurrency API service.")

    print_header("Demonstration Successfully Completed")


if __name__ == "__main__":
    run_demo()
