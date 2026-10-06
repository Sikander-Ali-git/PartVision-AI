#!/usr/bin/env python3
"""
scripts/init_database.py
Initializes the PartVision SQLite database (data/partvision.db),
configures WAL mode, foreign keys, indexes, and seeds the 19 canonical parts,
representative vehicles, aliases, and source-tracked compatibility records.

Idempotent: Safe to run repeatedly without creating duplicate records.
"""

import sys
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_db_connection, DEFAULT_DB_PATH, SCHEMA_SQL

# -----------------------------------------------------------------------------
# 1. Canonical 19 Parts Taxonomy (Option A / Milestone 5B)
# -----------------------------------------------------------------------------
PARTS_SEED = [
    {
        "part_name": "back_bumper",
        "display_name": "Back Bumper",
        "category": "Exterior Body",
        "description": "Rear impact bumper cover fascia and reinforcement bar."
    },
    {
        "part_name": "back_door",
        "display_name": "Back Door",
        "category": "Exterior Body",
        "description": "Rear passenger side door shell, window frame, and hinge assembly."
    },
    {
        "part_name": "back_glass",
        "display_name": "Back Glass",
        "category": "Exterior Glass",
        "description": "Rear vehicle windshield, hatch window, or liftgate safety glass."
    },
    {
        "part_name": "back_light",
        "display_name": "Back Light",
        "category": "Lighting",
        "description": "Rear tail lamp, brake light, reverse lamp, and turn signal cluster."
    },
    {
        "part_name": "fender",
        "display_name": "Fender",
        "category": "Exterior Body",
        "description": "Front body side sheet metal panel positioned over the front wheel arch."
    },
    {
        "part_name": "front_bumper",
        "display_name": "Front Bumper",
        "category": "Exterior Body",
        "description": "Front bumper cover fascia, lower air dam, and impact reinforcement."
    },
    {
        "part_name": "front_door",
        "display_name": "Front Door",
        "category": "Exterior Body",
        "description": "Front driver or passenger side door exterior shell and assembly."
    },
    {
        "part_name": "front_glass",
        "display_name": "Front Glass",
        "category": "Exterior Glass",
        "description": "Front laminated automotive safety windshield."
    },
    {
        "part_name": "front_light",
        "display_name": "Front Light",
        "category": "Lighting",
        "description": "Front headlamp assembly containing low/high beams and DRLs."
    },
    {
        "part_name": "grille",
        "display_name": "Grille",
        "category": "Exterior Body",
        "description": "Front radiator airflow intake grille and decorative surround."
    },
    {
        "part_name": "hood",
        "display_name": "Hood",
        "category": "Exterior Body",
        "description": "Engine compartment hood / bonnet exterior sheet metal panel."
    },
    {
        "part_name": "mirror",
        "display_name": "Mirror",
        "category": "Mirrors",
        "description": "Exterior side-view rear mirror housing, glass, and turn indicator."
    },
    {
        "part_name": "quarter_panel",
        "display_name": "Quarter Panel",
        "category": "Exterior Body",
        "description": "Rear body side panel positioned above and around the rear wheel arch."
    },
    {
        "part_name": "rocker_panel",
        "display_name": "Rocker Panel",
        "category": "Exterior Body",
        "description": "Lower exterior body side sill panel beneath doors between wheel arches."
    },
    {
        "part_name": "roof",
        "display_name": "Roof",
        "category": "Exterior Body",
        "description": "Vehicle exterior roof sheet metal panel and structural skin."
    },
    {
        "part_name": "side_window",
        "display_name": "Side Window",
        "category": "Exterior Glass",
        "description": "Side door drop window tempered glass or fixed quarter glass."
    },
    {
        "part_name": "tailgate",
        "display_name": "Tailgate",
        "category": "Exterior Body",
        "description": "Rear upward or side-opening hatch door for hatchback and SUV bodies."
    },
    {
        "part_name": "trunk",
        "display_name": "Trunk",
        "category": "Exterior Body",
        "description": "Rear luggage decklid / boot lid for three-box sedan and coupe bodies."
    },
    {
        "part_name": "wheel",
        "display_name": "Wheel",
        "category": "Wheels",
        "description": "Road wheel assembly including rim, hub mount, and mounted tire."
    },
]

# -----------------------------------------------------------------------------
# 2. Canonical Part Aliases
# -----------------------------------------------------------------------------
ALIASES_SEED = [
    # front_bumper
    ("front_bumper", "front bumper"),
    ("front_bumper", "front-bumper"),
    ("front_bumper", "bumper front"),
    ("front_bumper", "front fascia"),
    # back_bumper
    ("back_bumper", "back bumper"),
    ("back_bumper", "rear bumper"),
    ("back_bumper", "back-bumper"),
    ("back_bumper", "rear-bumper"),
    ("back_bumper", "bumper rear"),
    # front_glass
    ("front_glass", "front glass"),
    ("front_glass", "windshield"),
    ("front_glass", "windscreen"),
    ("front_glass", "front windshield"),
    ("front_glass", "front windscreen"),
    # back_glass
    ("back_glass", "back glass"),
    ("back_glass", "rear glass"),
    ("back_glass", "rear windshield"),
    ("back_glass", "rear windscreen"),
    ("back_glass", "back window"),
    ("back_glass", "rear window"),
    # front_light
    ("front_light", "front light"),
    ("front_light", "headlight"),
    ("front_light", "headlamp"),
    ("front_light", "front headlamp"),
    ("front_light", "head light"),
    # back_light
    ("back_light", "back light"),
    ("back_light", "tail light"),
    ("back_light", "taillight"),
    ("back_light", "tail lamp"),
    ("back_light", "rear lamp"),
    ("back_light", "brake light"),
    # side_window
    ("side_window", "side window"),
    ("side_window", "door glass"),
    ("side_window", "door window"),
    ("side_window", "front window"),
    ("side_window", "quarter glass"),
    # hood
    ("hood", "hood"),
    ("hood", "bonnet"),
    ("hood", "engine hood"),
    ("hood", "engine cover"),
    # trunk
    ("trunk", "trunk"),
    ("trunk", "boot"),
    ("trunk", "dicky"),
    ("trunk", "boot lid"),
    ("trunk", "decklid"),
    ("trunk", "trunk lid"),
    # tailgate
    ("tailgate", "tailgate"),
    ("tailgate", "liftgate"),
    ("tailgate", "rear hatch"),
    ("tailgate", "hatchback door"),
    ("tailgate", "back hatch"),
    # fender
    ("fender", "fender"),
    ("fender", "front fender"),
    ("fender", "wing"),
    ("fender", "front wing"),
    # quarter_panel
    ("quarter_panel", "quarter panel"),
    ("quarter_panel", "quarter-panel"),
    ("quarter_panel", "rear quarter"),
    ("quarter_panel", "rear quarter panel"),
    # rocker_panel
    ("rocker_panel", "rocker panel"),
    ("rocker_panel", "rocker-panel"),
    ("rocker_panel", "side sill"),
    ("rocker_panel", "rocker sill"),
    # grille
    ("grille", "grille"),
    ("grille", "radiator grille"),
    ("grille", "front grille"),
    ("grille", "mesh grille"),
    # mirror
    ("mirror", "mirror"),
    ("mirror", "side mirror"),
    ("mirror", "side view mirror"),
    ("mirror", "wing mirror"),
    ("mirror", "door mirror"),
    ("mirror", "rearview mirror"),
    # wheel
    ("wheel", "wheel"),
    ("wheel", "rim"),
    ("wheel", "tire"),
    ("wheel", "alloy wheel"),
    ("wheel", "tyre"),
    # roof
    ("roof", "roof"),
    ("roof", "roof panel"),
    ("roof", "top"),
    # front_door
    ("front_door", "front door"),
    ("front_door", "front-door"),
    # back_door
    ("back_door", "back door"),
    ("back_door", "rear door"),
    ("back_door", "back-door"),
]

# -----------------------------------------------------------------------------
# 3. Representative Indian-Market Vehicles Seed Data
# -----------------------------------------------------------------------------
VEHICLES_SEED = [
    {
        "id": 1,
        "make": "Maruti Suzuki",
        "model": "Swift",
        "generation": "3rd Gen (A2L)",
        "year_start": 2018,
        "year_end": 2024,
        "variant": "VXi / ZXi / ZXi+",
        "vehicle_type": "Hatchback",
        "notes": "Heartect platform 5-door hatchback with unified C-pillar door handles."
    },
    {
        "id": 2,
        "make": "Maruti Suzuki",
        "model": "Swift",
        "generation": "4th Gen (Z-Series)",
        "year_start": 2024,
        "year_end": None,
        "variant": "LXi / VXi / ZXi / ZXi+",
        "vehicle_type": "Hatchback",
        "notes": "4th generation redesign; features clamshell bonnet and conventional rear door handles."
    },
    {
        "id": 3,
        "make": "Hyundai",
        "model": "Creta",
        "generation": "2nd Gen (SU2i Pre-facelift)",
        "year_start": 2020,
        "year_end": 2023,
        "variant": "EX / S / SX / SX(O)",
        "vehicle_type": "Compact SUV",
        "notes": "Split headlamp design with trio-beam LED and distinctive trapezoidal cascading grille."
    },
    {
        "id": 4,
        "make": "Hyundai",
        "model": "Creta",
        "generation": "2nd Gen (SU2i Facelift)",
        "year_start": 2024,
        "year_end": None,
        "variant": "E / EX / S / SX / SX(O)",
        "vehicle_type": "Compact SUV",
        "notes": "Parametric black chrome grille, quad-beam LED headlamps, and continuous Horizon light bar."
    },
    {
        "id": 5,
        "make": "Tata",
        "model": "Nexon",
        "generation": "1st Gen (Facelift 2)",
        "year_start": 2023,
        "year_end": None,
        "variant": "Smart / Pure / Creative / Fearless",
        "vehicle_type": "Subcompact SUV",
        "notes": "Curvv concept inspired design with bi-functional LED headlamps and X-factor connected tail lamps."
    },
    {
        "id": 6,
        "make": "Mahindra",
        "model": "Scorpio-N",
        "generation": "1st Gen (Z-Series)",
        "year_start": 2022,
        "year_end": None,
        "variant": "Z2 / Z4 / Z6 / Z8 / Z8L",
        "vehicle_type": "Mid-size SUV",
        "notes": "Body-on-frame D-segment SUV with side-opening rear tailgate and vertical chrome grille."
    },
    {
        "id": 7,
        "make": "Toyota",
        "model": "Innova Crysta",
        "generation": "2nd Gen (AN140)",
        "year_start": 2016,
        "year_end": None,
        "variant": "GX / VX / ZX",
        "vehicle_type": "MPV",
        "notes": "IMV ladder-frame platform multi-purpose vehicle with vertical liftgate."
    },
    {
        "id": 8,
        "make": "Honda",
        "model": "City",
        "generation": "5th Gen",
        "year_start": 2020,
        "year_end": None,
        "variant": "V / VX / ZX",
        "vehicle_type": "Sedan",
        "notes": "Traditional 3-box mid-size sedan with conventional rear boot lid / trunk decklid."
    },
]

# -----------------------------------------------------------------------------
# 4. Source-Tracked Compatibility Seed Data
# -----------------------------------------------------------------------------
COMPATIBILITY_SEED = [
    # --- Vehicle 1: Maruti Suzuki Swift (3rd Gen, 2018-2024) ---
    {
        "vehicle_id": 1,
        "part_name": "front_bumper",
        "status": "compatible",
        "notes": "Direct OEM fitment for Swift 3rd Gen (A2L) chassis years 2018–2024.",
        "source": "Maruti Suzuki Genuine Parts (MSGP) Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 1,
        "part_name": "hood",
        "status": "compatible",
        "notes": "Heartect platform stamped steel hood; fits all 2018–2024 variants.",
        "source": "MSGP Body Collision Repair Manual",
        "verified": 1
    },
    {
        "vehicle_id": 1,
        "part_name": "front_light",
        "status": "compatible",
        "notes": "Headlamp housing assembly fits all 3rd Gen Swift models.",
        "source": "MSGP Electrical Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 1,
        "part_name": "tailgate",
        "status": "compatible",
        "notes": "Rear 5-door hatchback liftgate shell.",
        "source": "MSGP Body Collision Repair Manual",
        "verified": 1
    },
    {
        "vehicle_id": 1,
        "part_name": "trunk",
        "status": "incompatible",
        "notes": "Hatchback body architecture utilizes a tailgate; sedan trunk lid is incompatible.",
        "source": "Maruti Suzuki Technical Specification",
        "verified": 1
    },
    {
        "vehicle_id": 1,
        "part_name": "wheel",
        "status": "compatible",
        "notes": "Standard 14-inch steel or 15-inch precision-cut alloy (4x100 PCD).",
        "source": "MSGP Wheel & Tire Specification",
        "verified": 1
    },
    {
        "vehicle_id": 1,
        "part_name": "fender",
        "status": "compatible",
        "notes": "Front quarter panel; interchangeable between 2018–2024 models.",
        "source": "MSGP Collision Repair Manual",
        "verified": 1
    },
    {
        "vehicle_id": 1,
        "part_name": "grille",
        "status": "compatible",
        "notes": "Hexagonal honeycomb front radiator grille assembly.",
        "source": "MSGP Exterior Trim Manual",
        "verified": 1
    },
    {
        "vehicle_id": 1,
        "part_name": "mirror",
        "status": "compatible",
        "notes": "Power-adjust and power-fold side mirror assembly.",
        "source": "MSGP Parts Manual",
        "verified": 1
    },
    {
        "vehicle_id": 1,
        "part_name": "rocker_panel",
        "status": "compatible",
        "notes": "Demonstration: Aftermarket sports aerodynamic side sill skirt.",
        "source": "PartVision Demonstration Aftermarket Catalog",
        "verified": 0
    },

    # --- Vehicle 2: Maruti Suzuki Swift (4th Gen, 2024-Present) ---
    {
        "vehicle_id": 2,
        "part_name": "front_bumper",
        "status": "compatible",
        "notes": "Redesigned 4th Gen front fascia; NOT backward-compatible with 3rd Gen.",
        "source": "Maruti Suzuki 2024 Parts Bulletin",
        "verified": 1
    },
    {
        "vehicle_id": 2,
        "part_name": "hood",
        "status": "compatible",
        "notes": "All-new clamshell hood structure; distinct stamping from 3rd Gen.",
        "source": "Maruti Suzuki 2024 Collision Bulletin",
        "verified": 1
    },
    {
        "vehicle_id": 2,
        "part_name": "front_light",
        "status": "compatible",
        "notes": "Signature L-shaped LED projector lamp unit for 4th Gen.",
        "source": "MSGP 2024 Parts Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 2,
        "part_name": "tailgate",
        "status": "compatible",
        "notes": "Redesigned 4th Gen hatchback liftgate with integrated rear camera housing.",
        "source": "MSGP 2024 Parts Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 2,
        "part_name": "trunk",
        "status": "incompatible",
        "notes": "Hatchback architecture does not utilize a sedan trunk.",
        "source": "Maruti Suzuki Technical Specification",
        "verified": 1
    },
    {
        "vehicle_id": 2,
        "part_name": "wheel",
        "status": "compatible",
        "notes": "15-inch dual-tone alloy wheel (4x100 PCD).",
        "source": "MSGP 2024 Parts Catalog",
        "verified": 1
    },

    # --- Vehicle 3: Hyundai Creta (2nd Gen Pre-facelift, 2020-2023) ---
    {
        "vehicle_id": 3,
        "part_name": "front_bumper",
        "status": "compatible",
        "notes": "OEM pre-facelift front bumper cover (OEM Part: 86511-M1000).",
        "source": "Hyundai Mobis Genuine Parts Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 3,
        "part_name": "grille",
        "status": "compatible",
        "notes": "Trapezoidal cascading grille (OEM Part: 86350-M1000).",
        "source": "Hyundai Mobis Genuine Parts Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 3,
        "part_name": "hood",
        "status": "compatible",
        "notes": "Pre-facelift hood bonnet sheet metal (OEM Part: 66400-M1000).",
        "source": "Hyundai Mobis Collision Manual",
        "verified": 1
    },
    {
        "vehicle_id": 3,
        "part_name": "tailgate",
        "status": "compatible",
        "notes": "SUV rear liftgate shell with high-mount stop lamp cutout.",
        "source": "Hyundai Mobis Parts Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 3,
        "part_name": "trunk",
        "status": "incompatible",
        "notes": "SUV architecture uses an upward tailgate, not a sedan boot lid.",
        "source": "Hyundai Official Vehicle Specifications",
        "verified": 1
    },
    {
        "vehicle_id": 3,
        "part_name": "wheel",
        "status": "compatible",
        "notes": "16-inch steel or 17-inch diamond-cut alloy (5x114.3 PCD).",
        "source": "Hyundai Mobis Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 3,
        "part_name": "fender",
        "status": "compatible",
        "notes": "Demonstration: Flared wheel arch trim extension for off-road aesthetics.",
        "source": "PartVision Demonstration Bodywork Cross-Reference",
        "verified": 0
    },

    # --- Vehicle 4: Hyundai Creta (2nd Gen Facelift, 2024-Present) ---
    {
        "vehicle_id": 4,
        "part_name": "front_bumper",
        "status": "compatible",
        "notes": "Facelift front bumper with integrated skid plate; incompatible with 2020–2023.",
        "source": "Hyundai 2024 Mobis Collision Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 4,
        "part_name": "grille",
        "status": "compatible",
        "notes": "Parametric black chrome grille; incompatible with pre-facelift Creta.",
        "source": "Hyundai 2024 Mobis Collision Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 4,
        "part_name": "front_light",
        "status": "compatible",
        "notes": "Quad-beam LED headlamp assembly.",
        "source": "Hyundai Mobis Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 4,
        "part_name": "tailgate",
        "status": "compatible",
        "notes": "Updated liftgate featuring full-width connected LED Horizon light bar.",
        "source": "Hyundai Mobis Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 4,
        "part_name": "trunk",
        "status": "incompatible",
        "notes": "SUV architecture uses a tailgate liftgate, not a sedan trunk.",
        "source": "Hyundai Official Vehicle Specifications",
        "verified": 1
    },

    # --- Vehicle 5: Tata Nexon (1st Gen Facelift 2, 2023-Present) ---
    {
        "vehicle_id": 5,
        "part_name": "front_bumper",
        "status": "compatible",
        "notes": "Bi-functional split bumper assembly with lower air dam.",
        "source": "Tata Motors Genuine Parts (TMGP) Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 5,
        "part_name": "front_light",
        "status": "compatible",
        "notes": "Sequential LED DRL and low-mounted bi-functional projector headlamp.",
        "source": "TMGP Electrical Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 5,
        "part_name": "tailgate",
        "status": "compatible",
        "notes": "Rear liftgate featuring continuous X-factor LED light bar.",
        "source": "TMGP Body Manual",
        "verified": 1
    },
    {
        "vehicle_id": 5,
        "part_name": "trunk",
        "status": "incompatible",
        "notes": "Subcompact SUV architecture utilizes a rear liftgate, not a trunk lid.",
        "source": "Tata Motors Vehicle Specification",
        "verified": 1
    },
    {
        "vehicle_id": 5,
        "part_name": "roof",
        "status": "compatible",
        "notes": "Dual-tone contrast roof sheet metal panel.",
        "source": "TMGP Collision Repair Manual",
        "verified": 1
    },
    {
        "vehicle_id": 5,
        "part_name": "wheel",
        "status": "compatible",
        "notes": "16-inch alloy wheel with aerodynamic aero-inserts.",
        "source": "TMGP Wheel Specification",
        "verified": 1
    },
    {
        "vehicle_id": 5,
        "part_name": "side_window",
        "status": "compatible",
        "notes": "Demonstration: Solar-control UV cut glass replacement accessory.",
        "source": "PartVision Demonstration Glass Reference",
        "verified": 0
    },

    # --- Vehicle 6: Mahindra Scorpio-N (2022-Present) ---
    {
        "vehicle_id": 6,
        "part_name": "front_bumper",
        "status": "compatible",
        "notes": "D-segment SUV front bumper with fog lamp bezel.",
        "source": "Mahindra Maxicare Genuine Parts Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 6,
        "part_name": "grille",
        "status": "compatible",
        "notes": "Chrome-accented vertical multi-slat front grille with Twin Peaks emblem.",
        "source": "Mahindra Parts Bulletin",
        "verified": 1
    },
    {
        "vehicle_id": 6,
        "part_name": "tailgate",
        "status": "compatible",
        "notes": "Side-hinged rear door with hydraulic assist strut.",
        "source": "Mahindra Body Manual",
        "verified": 1
    },
    {
        "vehicle_id": 6,
        "part_name": "trunk",
        "status": "incompatible",
        "notes": "Mid-size ladder-frame SUV uses a side-opening rear door, not a trunk decklid.",
        "source": "Mahindra Technical Specification",
        "verified": 1
    },
    {
        "vehicle_id": 6,
        "part_name": "wheel",
        "status": "compatible",
        "notes": "17-inch steel or 18-inch dual-tone diamond-cut alloy (5x114.3 PCD).",
        "source": "Mahindra Maxicare Catalog",
        "verified": 1
    },

    # --- Vehicle 7: Toyota Innova Crysta (2016-Present) ---
    {
        "vehicle_id": 7,
        "part_name": "front_bumper",
        "status": "compatible",
        "notes": "IMV platform heavy-duty front bumper cover.",
        "source": "Toyota Genuine Parts (TGP) EPC",
        "verified": 1
    },
    {
        "vehicle_id": 7,
        "part_name": "hood",
        "status": "compatible",
        "notes": "Contoured steel hood bonnet.",
        "source": "Toyota EPC Collision Manual",
        "verified": 1
    },
    {
        "vehicle_id": 7,
        "part_name": "tailgate",
        "status": "compatible",
        "notes": "Rear upward liftgate door shell with integrated wiper motor mount.",
        "source": "Toyota EPC Body Manual",
        "verified": 1
    },
    {
        "vehicle_id": 7,
        "part_name": "trunk",
        "status": "incompatible",
        "notes": "Multi-purpose vehicle (MPV) architecture does not use a sedan trunk.",
        "source": "Toyota Official Vehicle Specification",
        "verified": 1
    },

    # --- Vehicle 8: Honda City (5th Gen, 2020-Present) ---
    {
        "vehicle_id": 8,
        "part_name": "trunk",
        "status": "compatible",
        "notes": "Three-box sedan boot lid / trunk decklid with integrated ducktail spoiler lip.",
        "source": "Honda Access Genuine Parts Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 8,
        "part_name": "tailgate",
        "status": "incompatible",
        "notes": "Three-box sedan body style uses a trunk decklid; hatchback tailgate is incompatible.",
        "source": "Honda Official Vehicle Specifications",
        "verified": 1
    },
    {
        "vehicle_id": 8,
        "part_name": "front_bumper",
        "status": "compatible",
        "notes": "Low-slung sedan front bumper cover with honeycomb lower grille.",
        "source": "Honda Access Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 8,
        "part_name": "hood",
        "status": "compatible",
        "notes": "Aerodynamic sedan bonnet panel.",
        "source": "Honda Collision Repair Manual",
        "verified": 1
    },
    {
        "vehicle_id": 8,
        "part_name": "front_light",
        "status": "compatible",
        "notes": "9-array inline full-LED headlamp cluster.",
        "source": "Honda Access Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 8,
        "part_name": "back_glass",
        "status": "compatible",
        "notes": "Fixed rear sedan windshield safety glass with defogger lines.",
        "source": "Honda Access Catalog",
        "verified": 1
    },
    {
        "vehicle_id": 8,
        "part_name": "wheel",
        "status": "compatible",
        "notes": "15-inch or 16-inch multi-spoke diamond-cut alloy wheels (4x100 PCD).",
        "source": "Honda Access Catalog",
        "verified": 1
    },
]


def init_database(db_path: Path = DEFAULT_DB_PATH):
    print("=" * 70)
    print("PartVision AI — Milestone 6B: Initialize Compatibility Database")
    print(f"Target Database: {db_path}")
    print("=" * 70)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(db_path)

    try:
        with conn:
            # 1. Execute DDL: Tables and Indexes
            print("\n[*] Applying database schema and indexes...")
            conn.executescript(SCHEMA_SQL)

            # 2. Seed 19 Parts Taxonomy
            print("[*] Seeding 19 PartVision V3 canonical parts...")
            parts_inserted = 0
            for p in PARTS_SEED:
                cursor = conn.execute(
                    """
                    INSERT INTO parts (part_name, display_name, category, description)
                    VALUES (:part_name, :display_name, :category, :description)
                    ON CONFLICT(part_name) DO UPDATE SET
                        display_name = excluded.display_name,
                        category = excluded.category,
                        description = excluded.description
                    """,
                    p
                )
                if cursor.rowcount > 0:
                    parts_inserted += 1

            # Fetch part_name -> id mapping
            part_id_map = {
                row["part_name"]: row["id"]
                for row in conn.execute("SELECT id, part_name FROM parts").fetchall()
            }
            print(f"    Indexed {len(part_id_map)} canonical parts.")

            # 3. Seed Part Aliases
            print("[*] Seeding canonical part search aliases...")
            alias_count = 0
            for part_name, alias in ALIASES_SEED:
                pid = part_id_map.get(part_name)
                if pid:
                    cursor = conn.execute(
                        """
                        INSERT INTO part_aliases (part_id, alias)
                        VALUES (?, ?)
                        ON CONFLICT(alias) DO UPDATE SET
                            part_id = excluded.part_id
                        """,
                        (pid, alias)
                    )
                    if cursor.rowcount > 0:
                        alias_count += 1
            print(f"    Seeded {alias_count} search aliases.")

            # 4. Seed Vehicles Catalog
            print("[*] Seeding representative vehicle records...")
            vehicles_seeded = 0
            for v in VEHICLES_SEED:
                conn.execute(
                    """
                    INSERT INTO vehicles (id, make, model, generation, year_start, year_end, variant, vehicle_type, notes)
                    VALUES (:id, :make, :model, :generation, :year_start, :year_end, :variant, :vehicle_type, :notes)
                    ON CONFLICT(id) DO UPDATE SET
                        make = excluded.make,
                        model = excluded.model,
                        generation = excluded.generation,
                        year_start = excluded.year_start,
                        year_end = excluded.year_end,
                        variant = excluded.variant,
                        vehicle_type = excluded.vehicle_type,
                        notes = excluded.notes
                    """,
                    v
                )
                vehicles_seeded += 1
            print(f"    Seeded {vehicles_seeded} vehicle records.")

            # 5. Seed Compatibility Records
            print("[*] Seeding source-tracked compatibility relationships...")
            compat_seeded = 0
            verified_count = 0
            for c in COMPATIBILITY_SEED:
                pid = part_id_map.get(c["part_name"])
                if not pid:
                    print(f"    [!] Warning: Part {c['part_name']} not found for vehicle {c['vehicle_id']}")
                    continue

                conn.execute(
                    """
                    INSERT INTO compatibility (vehicle_id, part_id, compatibility_status, notes, source, verified)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(vehicle_id, part_id) DO UPDATE SET
                        compatibility_status = excluded.compatibility_status,
                        notes = excluded.notes,
                        source = excluded.source,
                        verified = excluded.verified
                    """,
                    (c["vehicle_id"], pid, c["status"], c["notes"], c["source"], c["verified"])
                )
                compat_seeded += 1
                if c["verified"] == 1:
                    verified_count += 1

            unverified_count = compat_seeded - verified_count
            print(f"    Seeded {compat_seeded} compatibility relationships.")
            print(f"    - Verified Records:   {verified_count} (OEM Catalogs & Manuals)")
            print(f"    - Demonstration Data: {unverified_count} (Explicitly marked unverified)")

        print("\n=== Database Initialization Successfully Completed ===")

    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
