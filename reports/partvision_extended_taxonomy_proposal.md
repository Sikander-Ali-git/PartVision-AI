# Milestone 4B: PartVision Extended Automotive Taxonomy Proposal

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 4B — Multi-Dataset Acquisition & Taxonomy Design  
**Date**: October 3, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  

---

## 1. Executive Summary & Design Principles

In Milestone 2, PartVision established **Taxonomy V2** (13 consolidated classes), which resolved severe bilateral competition (e.g. left vs. right doors/lights) and increased instance segmentation mAP50 from 49.35% to 81.80%.

However, Taxonomy V2 left several critical structural gaps:
1. **Severe Class Imbalance / Underrepresentation**:
   - `trunk`: Only 173 total instances in Carparts-Seg (26.72% mAP50-95).
   - `tailgate`: Only 101 total instances in Carparts-Seg (45.41% mAP50-95).
   - `wheel`: Suffered from heavy angular distortion and occlusion (25.73% mAP50-95).
   - `mirror`: Low pixel resolution footprint (49.71% mAP50-95).
2. **Missing Essential Exterior Replacement Panels**:
   - Panels frequently damaged and replaced in collisions—such as `fender`, `grille`, `rocker_panel`, `quarter_panel`, and `roof`—were completely absent from the Ultralytics Carparts-Seg dataset.
3. **Absence of Side Window Differentiation**:
   - Passenger door windows were historically absorbed into the general door panel without distinct glazing localization.

In Milestone 4B, based strictly on the ground-truth annotations discovered across the verified datasets, we propose the **PartVision Extended Taxonomy (V3 Architecture)** for human review.

### Core Design Rules Applied:
- **No Sidedness Competition**: Eliminate left vs. right distinctions (which cause catastrophic spatial confusion when vehicle orientation changes).
- **Consolidation of Wheel Sub-types**: Merge `Front-wheel` and `Back-wheel` into a unified `wheel` class.
- **Glass Glazing Consistency**: Maintain clear separation between frontal windshield (`front_glass`), rear window (`back_glass`), and side windows (`side_window`).
- **Vehicle Domain Separation**: Prefix motorcycle components (e.g., `bike_brake_lever`, `bike_carrier`) to prevent semantic collision with automotive mechanisms.
- **Strict Separation of Damage**: Vehicle damage classes (`dent`, `scratch`, `cracked`, etc.) are preserved in raw storage for future damage assessment, but strictly excluded from part classification.

---

## 2. Source-to-Target Class Mapping Inventory

The proposal synthesizes ground-truth classes from **Carparts-V2 (13 classes)**, **Humans in the Loop (21 part classes)**, and **Fusion-Bike-Parts (5 reported motorcycle classes)** into a cohesive schema.

### Table 1: Complete Mapping Analysis

| Source Dataset | Original Class | Instance Count | Proposed PartVision Class | Vehicle Domain | Taxonomy Action | Design Rationale & Technical Justification |
|---|---|---|---|---|---|---|
| **Carparts-V2** | `back_bumper` | 1,234 | `back_bumper` | Passenger Car | Retained | Core rear exterior bumper; strong performance in V2 (87.8% mAP50). |
| **HITL** | `Back-bumper` | 443 | `back_bumper` | Passenger Car | Consolidated | Merges 1:1 with `back_bumper`, adding 443 new training instances. |
| **Carparts-V2** | `front_bumper` | 1,450 | `front_bumper` | Passenger Car | Retained | Core front exterior bumper; high performance in V2 (92.5% mAP50). |
| **HITL** | `Front-bumper` | 705 | `front_bumper` | Passenger Car | Consolidated | Merges 1:1 with `front_bumper`, expanding lighting and angle diversity. |
| **Carparts-V2** | `front_door` | 3,420 | `front_door` | Passenger Car | Retained | Consolidated front door assembly (93.2% mAP50 in V2). |
| **HITL** | `Front-door` | 917 | `front_door` | Passenger Car | Consolidated | Merges 1:1 with `front_door`. |
| **Carparts-V2** | `back_door` | 3,210 | `back_door` | Passenger Car | Retained | Consolidated rear door assembly (93.4% mAP50 in V2). |
| **HITL** | `Back-door` | 721 | `back_door` | Passenger Car | Consolidated | Merges 1:1 with `back_door`. |
| **Carparts-V2** | `hood` | 1,350 | `hood` | Passenger Car | Retained | Front engine hood panel (88.4% mAP50 in V2). |
| **HITL** | `Hood` | 712 | `hood` | Passenger Car | Consolidated | Merges 1:1 with `hood`. |
| **Carparts-V2** | `front_light` | 2,200 | `front_light` | Passenger Car | Retained | Consolidated headlight cluster (90.9% mAP50 in V2). |
| **HITL** | `Headlight` | 914 | `front_light` | Passenger Car | Consolidated | Standardizes singular "Headlight" to consolidated `front_light`. |
| **Carparts-V2** | `back_light` | 1,850 | `back_light` | Passenger Car | Retained | Consolidated taillight cluster (87.6% mAP50 in V2). |
| **HITL** | `Tail-light` | 721 | `back_light` | Passenger Car | Consolidated | Standardizes "Tail-light" to consolidated `back_light`. |
| **Carparts-V2** | `front_glass` | 1,100 | `front_glass` | Passenger Car | Retained | Front windshield glazing (94.0% mAP50 in V2). |
| **HITL** | `Windshield` | 632 | `front_glass` | Passenger Car | Consolidated | Merges "Windshield" directly into `front_glass`. |
| **Carparts-V2** | `back_glass` | 1,024 | `back_glass` | Passenger Car | Retained | Rear windshield glazing (87.5% mAP50 in V2). |
| **HITL** | `Back-windshield`| 271 | `back_glass` | Passenger Car | Consolidated | Merges "Back-windshield" directly into `back_glass`. |
| **Carparts-V2** | `mirror` | 1,520 | `mirror` | Passenger Car | Retained | Consolidated side mirrors (82.4% mAP50 in V2). |
| **HITL** | `Mirror` | 987 | `mirror` | Passenger Car | Consolidated | Bolsters side mirror representation with 987 new instances. |
| **Carparts-V2** | `wheel` | 1,726 | `wheel` | Passenger Car | Retained | Critical chassis component; weakest V2 class (25.7% mAP50-95). |
| **HITL** | `Front-wheel` | 885 | `wheel` | Passenger Car | Consolidated | Eliminates front/back wheel split; provides massive data boost (+885). |
| **HITL** | `Back-wheel` | 865 | `wheel` | Passenger Car | Consolidated | Eliminates front/back wheel split; provides massive data boost (+865). |
| **Carparts-V2** | `trunk` | 173 | `trunk` | Passenger Car | Retained | Severely starved V2 class (only 9 validation instances). |
| **HITL** | `Trunk` | 416 | `trunk` | Passenger Car | Consolidated | **Increases trunk training instances by 240%** (173 -> 589), solving data famine. |
| **Carparts-V2** | `tailgate` | 101 | `tailgate` | Passenger Car | Retained | Liftgate / rear hatchback door; retained as distinct class. |
| **HITL** | `Front-window` | 951 | `side_window` | Passenger Car | **New Class** | Distinct side door window glass; avoids confusing door sheet metal with glass. |
| **HITL** | `Back-window` | 1,237 | `side_window` | Passenger Car | **New Class** | Merged with front side windows to create unified `side_window` glazing class (2,188 total). |
| **HITL** | `Fender` | 935 | `fender` | Passenger Car | **New Class** | Front quarter body panel over front wheel well; critical collision repair part. |
| **HITL** | `Quarter-panel`| 855 | `quarter_panel`| Passenger Car | **New Class** | Rear body panel surrounding rear wheel well; standard OEM catalog part. |
| **HITL** | `Rocker-panel` | 860 | `rocker_panel` | Passenger Car | **New Class** | Lower structural panel beneath side doors; frequent rust/curb damage part. |
| **HITL** | `Grille` | 577 | `grille` | Passenger Car | **New Class** | Front radiator intake grille assembly; key brand-defining visual component. |
| **HITL** | `Roof` | 793 | `roof` | Passenger Car | **New Class** | Upper roof panel; provides top-down vehicle structural boundary. |
| **HITL** | `License-plate`| 370 | `license_plate`| Passenger Car | Optional/Excluded| Frequently blurred or obscured; recommended as auxiliary/excluded class. |
| **Fusion-Bike** | `Brake_Lever` | ~4,000 | `bike_brake_lever`| Motorcycle | **New Domain** | Handlebar hand brake lever control; distinct from automotive pedal. |
| **Fusion-Bike** | `Brake_Pedal` | ~3,500 | `bike_brake_pedal`| Motorcycle | **New Domain** | Foot brake pedal control mechanism. |
| **Fusion-Bike** | `Carrier` | ~3,000 | `bike_carrier` | Motorcycle | **New Domain** | Rear luggage rack / helmet mounting rack. |
| **Fusion-Bike** | `Center_Cowl` | ~4,200 | `bike_center_cowl`| Motorcycle | **New Domain** | Central aerodynamic body fairing cowl. |
| **Fusion-Bike** | `Chain_Cover` | ~3,800 | `bike_chain_cover`| Motorcycle | **New Domain** | Enclosed secondary drive chain protective shroud. |

---

## 3. Proposed Extended Taxonomy Tiers

We propose structuring the PartVision catalog into **Three Cohesive Architectural Options** for stakeholder selection:

### Option A: The Complete Exterior Automotive Suite (19 Passenger Car Classes)
*Focuses purely on passenger vehicles, eliminating tail-class deficiencies while adding all essential structural body panels.*

```
0:  back_bumper       (Rear bumper assembly)
1:  back_door         (Rear passenger doors)
2:  back_glass        (Rear windshield glass)
3:  back_light        (Taillights / brake lights)
4:  fender            (NEW: Front wheel-well fender panel)
5:  front_bumper      (Front bumper assembly)
6:  front_door        (Front passenger doors)
7:  front_glass       (Front windshield glass)
8:  front_light       (Headlight clusters)
9:  grille            (NEW: Front radiator grille)
10: hood              (Front engine bonnet)
11: mirror            (Side rearview mirrors)
12: quarter_panel     (NEW: Rear wheel-well quarter panel)
13: rocker_panel      (NEW: Lower sill / rocker panel)
14: roof              (NEW: Vehicle roof panel)
15: side_window       (NEW: Side door window glass)
16: tailgate          (Liftgate / hatchback door)
17: trunk             (Sedan trunk lid)
18: wheel             (Tires and road rims)
```

### Option B: The Multi-Modal Automotive & Motorcycle Suite (24 Classes)
*Extends Option A with a dedicated two-wheeler / motorcycle sub-domain, keeping vehicle types cleanly segregated via explicit naming.*

- All 19 classes from **Option A** (Classes 0–18)
- Plus 5 Motorcycle Classes:
```
19: bike_brake_lever  (Motorcycle handlebar brake lever)
20: bike_brake_pedal  (Motorcycle foot brake pedal)
21: bike_carrier      (Motorcycle rear carrier rack)
22: bike_center_cowl  (Motorcycle body center cowl)
23: bike_chain_cover  (Motorcycle protective chain cover)
```

### Option C: The Conservative Deficit-Repair Suite (14 Classes)
*Maintains exact V2 compatibility while adding only the newly available `side_window` and using HITL instances strictly to bolster existing weak classes (`trunk`, `wheel`, `mirror`).*

---

## 4. Key Benefits of Proposed Option A (19 Classes)

1. **Elimination of the V2 "Trunk Famine"**:
   - V2 had only 173 total instances of `trunk`.
   - Adding HITL adds **416 high-resolution polygon instances**, boosting total trunk annotations to **589** (a 3.4x data increase).
2. **Resolution of the "Wheel Occlusion" Bottleneck**:
   - V2 wheel mAP50-95 was 25.73%.
   - Adding 1,750 combined wheel instances from HITL (885 front-wheel + 865 back-wheel) brings total wheel instances to **3,476**, doubling representation across diverse viewing angles and rim designs.
3. **Professional OEM Panel Coverage**:
   - Introducing `fender` (935), `quarter_panel` (855), `grille` (577), and `rocker_panel` (860) transforms PartVision from a basic exterior detector into a genuine collision estimation system capable of distinguishing contiguous body panels.

---

## 5. Next Steps for Implementation (Milestone 5)

1. **Human Alignment & Sign-off**: User/stakeholder confirms preference between Option A (19-class automotive), Option B (24-class multi-modal), or Option C.
2. **Annotation Converter Pipeline**: Construct `scripts/convert_hitl_to_yolo.py` to parse Supervisely JSON polygon coordinates, normalize to YOLO format, filter damage classes, and map class IDs according to the selected option.
3. **Controlled V3 Benchmark**: Re-train YOLO11n-seg under identical standardized conditions to measure quantitative gains.
