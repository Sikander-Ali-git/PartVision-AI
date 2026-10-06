# PartVision AI — Milestone 5A Final Engineering Report
## Construction of the PartVision V3 Unified Automotive Dataset

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 5A — Unified Automotive Dataset Construction  
**Date**: October 6, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  

---

## 1. Executive Summary & Why V3 Was Created

In Milestones 1–3, PartVision established a high-performing baseline (`YOLO11n-seg`) on the 13-class consolidated Carparts-V2 dataset, reaching **81.80% mAP50** and **64.14% mAP50-95** on instance segmentation.

However, comprehensive evaluation revealed three major operational and architectural limitations:
1. **Severe Tail-Class Starvation**:
   - `trunk`: Only 173 total instances in Carparts-Seg (26.72% mAP50-95, only 9 validation instances).
   - `tailgate`: Only 101 total instances in Carparts-Seg (45.41% mAP50-95, only 5 validation instances).
   - `wheel`: Suffered from extreme occlusion and rim/tire angle variations (25.73% mAP50-95).
   - `mirror`: Low pixel resolution footprint (49.71% mAP50-95).
2. **Missing Essential Exterior Collision Panels**:
   - Primary replacement panels in automotive collision repair—including `fender`, `grille`, `rocker_panel`, `quarter_panel`, and `roof`—did not exist anywhere in Carparts-Seg.
3. **Glazing & Window Inconsistency**:
   - Passenger door window glass was unsegmented or absorbed directly into door sheet metal.

**Milestone 5A constructs PartVision V3**: a unified 19-class automotive instance-segmentation dataset combining the cleaned Carparts-V2 corpus with the newly verified Humans in the Loop (HITL) car parts dataset.

---

## 2. Target 19-Class Taxonomy

PartVision V3 defines exactly 19 automotive exterior-part classes (Option A architecture):

```yaml
names:
  0: back_bumper
  1: back_door
  2: back_glass
  3: back_light
  4: fender          # NEW (Front wheel arch panel)
  5: front_bumper
  6: front_door
  7: front_glass
  8: front_light
  9: grille          # NEW (Front radiator intake grille)
  10: hood
  11: mirror
  12: quarter_panel  # NEW (Rear wheel arch quarter panel)
  13: rocker_panel   # NEW (Lower sill / rocker panel)
  14: roof           # NEW (Vehicle roof panel)
  15: side_window    # NEW (Side passenger door glass)
  16: tailgate
  17: trunk          # BOLSTERED (+240% increase in training data)
  18: wheel          # BOLSTERED (+101% increase in training data)
```

The configuration is permanently recorded in [`data/processed/partvision-v3/partvision-v3.yaml`](file:///Volumes/Toshiba%201TB/PartVision/data/processed/partvision-v3/partvision-v3.yaml).

---

## 3. Source Datasets & Exact Ground-Truth Mappings

### Source A: Carparts-V2 (`data/processed/carparts-v2/`)
- **Origin**: Ultralytics Carparts-Seg asset release.
- **Images**: 3,833 images.
- **Annotations**: 20,362 annotations across 13 classes.
- **Mapping to V3**:
  - `back_bumper` (0) -> `back_bumper` (0)
  - `back_door` (1) -> `back_door` (1)
  - `back_glass` (2) -> `back_glass` (2)
  - `back_light` (3) -> `back_light` (3)
  - `front_bumper` (4) -> `front_bumper` (5) [remapped ID]
  - `front_door` (5) -> `front_door` (6) [remapped ID]
  - `front_glass` (6) -> `front_glass` (7) [remapped ID]
  - `front_light` (7) -> `front_light` (8) [remapped ID]
  - `hood` (8) -> `hood` (10) [remapped ID]
  - `mirror` (9) -> `mirror` (11) [remapped ID]
  - `tailgate` (10) -> `tailgate` (16) [remapped ID]
  - `trunk` (11) -> `trunk` (17) [remapped ID]
  - `wheel` (12) -> `wheel` (18) [remapped ID]

### Source B: Humans in the Loop (`data/external/humans_in_the_loop/`)
- **Origin**: Humans in the Loop (Data labeling organization), CC0 1.0 Public Domain.
- **Images**: 998 images (from Car damages dataset/File1/img).
- **Annotations**: 15,397 valid part polygon annotations across 20 source classes.
- **Mapping to V3**:
  - `Back-bumper` (443) -> `back_bumper` (0)
  - `Back-door` (721) -> `back_door` (1)
  - `Back-window` (1,237) -> `back_glass` (2)
  - `Back-windshield` (271) -> `back_glass` (2)
  - `Tail-light` (721) -> `back_light` (3)
  - `Fender` (935) -> `fender` (4) [NEW]
  - `Front-bumper` (705) -> `front_bumper` (5)
  - `Front-door` (917) -> `front_door` (6)
  - `Windshield` (632) -> `front_glass` (7)
  - `Headlight` (914) -> `front_light` (8)
  - `Grille` (577) -> `grille` (9) [NEW]
  - `Hood` (712) -> `hood` (10)
  - `Mirror` (987) -> `mirror` (11)
  - `Quarter-panel` (855) -> `quarter_panel` (12) [NEW]
  - `Rocker-panel` (860) -> `rocker_panel` (13) [NEW]
  - `Roof` (793) -> `roof` (14) [NEW]
  - `Front-window` (951) -> `side_window` (15) [NEW]
  - `Trunk` (416) -> `trunk` (17)
  - `Front-wheel` (885) -> `wheel` (18)
  - `Back-wheel` (865) -> `wheel` (18)
  - `License-plate` (370) -> **EXCLUDED** from part taxonomy.
  - All 8 Damage classes (9,084 instances) -> **EXCLUDED** from part taxonomy.

All mapping decisions are audited in [`reports/v3_label_mapping_audit.csv`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_label_mapping_audit.csv).

---

## 4. Dataset Scale & Combined Class Distribution

| Class ID | Class Name | Carparts-V2 | HITL | V3 Total Annotations | Share of Total | Primary Effect in V3 |
|---|---|---|---|---|---|---|
| **0** | `back_bumper` | 870 | 443 | **1,313** | 3.67% | Bolstered (+50.9%) |
| **1** | `back_door` | 1,731 | 721 | **2,452** | 6.86% | Bolstered (+41.7%) |
| **2** | `back_glass` | 1,058 | 1,508 | **2,566** | 7.18% | Bolstered (Rear windshield & rear glazing, +142.5%) |
| **3** | `back_light` | 2,434 | 721 | **3,155** | 8.82% | Bolstered (+29.6%) |
| **4** | `fender` | 0 | 935 | **935** | 2.61% | **NEW STRUCTURAL PANEL** |
| **5** | `front_bumper` | 1,978 | 705 | **2,683** | 7.50% | Bolstered (+35.6%) |
| **6** | `front_door` | 1,936 | 917 | **2,853** | 7.98% | Bolstered (+47.4%) |
| **7** | `front_glass` | 2,062 | 632 | **2,694** | 7.53% | Bolstered (Front windshield, +30.6%) |
| **8** | `front_light` | 4,066 | 914 | **4,980** | 13.93% | Bolstered (+22.5%) |
| **9** | `grille` | 0 | 577 | **577** | 1.61% | **NEW STRUCTURAL PANEL** |
| **10** | `hood` | 2,080 | 712 | **2,792** | 7.81% | Bolstered (+34.2%) |
| **11** | `mirror` | 996 | 987 | **1,983** | 5.55% | Bolstered (+99.1%) |
| **12** | `quarter_panel` | 0 | 855 | **855** | 2.39% | **NEW STRUCTURAL PANEL** |
| **13** | `rocker_panel` | 0 | 860 | **860** | 2.40% | **NEW STRUCTURAL PANEL** |
| **14** | `roof` | 0 | 793 | **793** | 2.22% | **NEW STRUCTURAL PANEL** |
| **15** | `side_window` | 0 | 951 | **951** | 2.66% | **NEW GLAZING CLASS** |
| **16** | `tailgate` | 101 | 0 | **101** | 0.28% | Retained (Exclusive to hatchbacks/pickups) |
| **17** | `trunk` | 173 | 416 | **589** | 1.65% | **CURED DATA FAMINE (+240.5%)** |
| **18** | `wheel` | 877 | 1,750 | **2,627** | 7.35% | **DOUBLED REPRESENTATION (+199.5%)** |
| **TOTAL** | **19 Classes** | **20,362** | **15,397** | **35,759** | **100.00%** | **75.6% Growth in Annotations** |

---

## 5. Train / Val / Test Partition Strategy

To prevent data contamination, Carparts-V2 splits were strictly maintained, while the 998 HITL images were partitioned with a fixed pseudorandom seed:
- **HITL Partition**: `random.seed(42)`
  - **Train (80%)**: 798 images
  - **Validation (10%)**: 100 images
  - **Test (10%)**: 100 images

### Combined Partition Breakdown:
| Split | Carparts-V2 Images | HITL Images | Total V3 Images | Share | Total Annotations | Annotation Share |
|---|---|---|---|---|---|---|
| **Train** | 3,156 | 798 | **3,954** | 81.85% | **29,005** | 81.11% |
| **Validation** | 401 | 100 | **501** | 10.37% | **3,573** | 9.99% |
| **Test** | 276 | 100 | **376** | 7.78% | **3,181** | 8.90% |
| **TOTAL** | **3,833** | **998** | **4,831** | **100.00%** | **35,759** | **100.00%** |

---

## 6. Duplicate Analysis & Data Leakage Protection

- **Cryptographic Hashing**: Every image was hashed with SHA256.
- **Cross-Dataset Leakage**: Exactly **0 cross-dataset duplicate images** exist between Carparts-V2 and HITL.
- **Within-HITL Part Duplicates**: Exactly **0 duplicate images** exist within the 998 HITL parts images.
- **HITL Damage Subset Handling**: The 441 images that overlap between HITL's part and damage subsets were never introduced because the damage subset was completely excluded from V3.
- Full details documented in [`reports/v3_duplicate_analysis.csv`](file:///Volumes/Toshiba 1TB/PartVision/reports/v3_duplicate_analysis.csv).

---

## 7. Data Provenance & Legal Licensing Record

Every image is tracked in [`reports/v3_image_provenance.csv`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_image_provenance.csv).  
Legal terms are recorded in [`reports/v3_data_provenance_and_licenses.md`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_data_provenance_and_licenses.md):
- **Carparts-V2 component**: AGPL-3.0 / Open Source.
- **HITL component**: CC0 1.0 Universal (Public Domain).
- Commercial and derivative use is fully permitted under open compliance.

---

## 8. Dataset Quality & Integrity Validation

Automated validation via [`scripts/validate_dataset_v3.py`](file:///Volumes/Toshiba%201TB/PartVision/scripts/validate_dataset_v3.py):
- **Total Images**: 4,831
- **Total Annotations**: 35,759
- **Malformed Annotations**: 0
- **Invalid Coordinates (<0 or >1)**: 0
- **Orphan Image Files**: 0
- **Orphan Label Files**: 0
- **Empty Image Files**: 147 (Background negative images inherited from V2 object removal, essential for false-positive suppression)

---

## 9. Remaining Class Imbalance & Analysis

While V3 vastly improves taxonomy coverage and cures the trunk/wheel bottlenecks:
1. `tailgate` remains the smallest class (101 instances, 0.28% of dataset). Tailgates are specific to hatchbacks/SUVs, whereas sedans have trunks.
2. `grille` (577 instances) and `trunk` (589 instances) have lower representation than doors or lights, but are now sufficiently populated (>500 instances) for effective deep learning convergence with YOLO11.
3. Newly added structural panels (`fender`, `quarter_panel`, `rocker_panel`, `roof`, `side_window`) each possess between 790 and 950 high-quality polygon instances, providing balanced representation.

---

## 10. Recommended Next Training Experiment (Milestone 5B)

For Milestone 5B model training:
- **Architecture**: `YOLO11n-seg` pretrained checkpoint.
- **Image Resolution**: 512x512 (consistent with Milestone 3) or 640x640.
- **Epochs**: 15–20 epochs on Apple Silicon MPS.
- **Batch Size**: 8 or 16.
- **Objective**: Establish the 19-class segmentation benchmark, verifying that the new classes (`fender`, `grille`, `roof`, `side_window`, `quarter_panel`, `rocker_panel`) achieve strong mAP50 (>75%) while weak classes (`trunk`, `wheel`) show substantial recovery.

---

### Milestone 5A Status: COMPLETE
No model training has been conducted. Working tree is clean and ready for user inspection.
