# PartVision V3: Data Provenance and Open Licensing Documentation

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 5A — Unified Automotive Dataset Construction  
**Date**: October 6, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  

---

## 1. Executive Summary & Legal Framework

PartVision V3 represents a composite computer-vision dataset combining two distinct open-access automotive repositories:
1. **Ultralytics Carparts-Seg** (processed via PartVision V2 taxonomy consolidation).
2. **Humans in the Loop Car Parts and Damages Dataset** (acquired via official open distribution).

Because these datasets originate from independent organizations with different licensing terms, **PartVision does NOT claim a single uniform license across the entire merged collection**. Instead, each image and polygon annotation retains its individual legal provenance and licensing terms, tracked on a per-file basis in `reports/v3_image_provenance.csv`.

---

## 2. Constituent Datasets & Exact Licensing Terms

### Source Dataset 1: Carparts-V2 (Derived from Ultralytics Carparts-Seg)

- **Source Asset URL**: [github.com/ultralytics/assets/releases/download/v0.0.0/carparts-seg.zip](https://github.com/ultralytics/assets/releases/download/v0.0.0/carparts-seg.zip)
- **Archive Checksum (SHA256)**: `e2eea20030d02366b07174bcdbcc843f63791bdd53962a83e00636d15e78e41f`
- **Original Publisher**: Ultralytics / Open Source Computer Vision Assets
- **Original Scale**: 3,833 images, 20,374 annotations across 23 classes.
- **V2 Derivative Processing**: Consolidated into 13 classes (removing class 18 `object`, eliminating left/right lateral competition across doors, lights, and mirrors). Retained 3,833 images and 20,362 annotations.
- **Governing License**: **AGPL-3.0 / Ultralytics Open License**
- **Commercial Use Rights**: Permitted under open-source compliance (or enterprise commercial licensing if bundled into closed-source commercial distributions).
- **Attribution Obligation**: Mandatory citation of Ultralytics Carparts-Seg.
- **Redistribution Rights**: Permitted under compatible open licenses with attribution.
- **V3 Contribution**:
  - **3,833 images** (Train: 3,156, Val: 442, Test: 235)
  - **20,362 polygon annotations** across 13 core exterior classes.

---

### Source Dataset 2: Humans in the Loop (HITL) — Car Parts and Damages

- **Official Web Portal**: [humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/](https://humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/)
- **Distribution Mirror**: [huggingface.co/datasets/yusufnull/car-parts-and-damage-dataset](https://huggingface.co/datasets/yusufnull/car-parts-and-damage-dataset)
- **Git Commit SHA**: `e4870360afe5e0516e7567cea550d8718482611b`
- **Original Publisher / Owner**: Humans in the Loop (Social Enterprise for Data Annotation)
- **Labeling Attribution**: GhazalehHITL / Humans in the Loop Annotation Team
- **Governing License**: **Creative Commons Zero 1.0 Universal (CC0 1.0) Public Domain Dedication**
- **Commercial Use Rights**: **UNRESTRICTED (Public Domain)**. CC0 explicitly waives all copyright, database rights, and associated claims worldwide.
- **Attribution Obligation**: None legally required under CC0 (scholarly/professional engineering attribution maintained).
- **Redistribution Rights**: Unrestricted copying, modification, and redistribution.
- **Damage Class Handling**:
  - The HITL raw corpus contains 8 vehicle damage classes (`Scratch`, `Dent`, `Broken part`, `Paint chip`, `Missing part`, `Flaking`, `Corrosion`, `Cracked` - totaling 9,084 annotations).
  - **All damage classes are strictly excluded from PartVision V3** and preserved untouched in `data/external/humans_in_the_loop/` for future damage assessment modules.
- **License-Plate Handling**:
  - `License-plate` (370 polygon instances) was excluded to maintain pure automotive structural part focus.
- **V3 Contribution**:
  - **998 images** (Train: 798, Val: 100, Test: 100)
  - **15,397 polygon annotations** across 18 exterior classes (introducing 6 brand new structural classes: `fender`, `grille`, `quarter_panel`, `rocker_panel`, `roof`, `side_window`).

---

## 3. Data Provenance Architecture

To guarantee complete traceability:
1. **Filename Namespacing**:
   - Images originating from Carparts-V2 retain their original identifiers (e.g. `car10_jpg.rf....jpg`).
   - Images originating from Humans in the Loop are deterministically prefixed with `hitl_` and Unix-sanitized (e.g. `hitl_Car_damages_100.png`).
2. **Provenance Metadata Catalog**:
   - Every single image in `data/processed/partvision-v3/` is indexed in `reports/v3_image_provenance.csv` with fields:
     `image_filename`, `source_dataset`, `source_split`, `original_filename`, `source_identifier_if_available`.
3. **Data Leakage & Duplicate Protection**:
   - SHA256 content hashes confirm **zero cross-dataset duplicates** between Carparts-V2 and HITL.
   - HITL's 998 images were partitioned using a fixed pseudo-random split (`seed=42`) ensuring zero overlap across train, validation, and test partitions.
   - All duplicate relationships are tracked in `reports/v3_duplicate_analysis.csv`.

---

## 4. Summary Matrix

| Metric / Attribute | Carparts-V2 Component | Humans in the Loop Component | Combined V3 Dataset |
|---|---|---|---|
| **Images Contributed** | 3,833 | 998 | **4,831** |
| **Annotations Contributed**| 20,362 | 15,397 | **35,759** |
| **Classes Covered** | 13 | 18 | **19** |
| **Primary License** | AGPL-3.0 / Open Source | CC0 1.0 (Public Domain) | **Dual-Attributed Multi-Source** |
| **Commercial Exploitation**| Permitted with Open Compliance| Unrestricted (Public Domain) | Permitted |
| **Attribution Requirement**| Mandatory (Ultralytics) | None (Maintained for courtesy)| Mandatory per-source citation |
| **Storage Location** | `data/processed/carparts-v2/` | `data/external/humans_in_the_loop/` | `data/processed/partvision-v3/` |
