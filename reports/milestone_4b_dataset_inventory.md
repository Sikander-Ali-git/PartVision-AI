# Milestone 4B: External Dataset Inventory & Quality Inspection

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 4B — Multi-Dataset Acquisition & Taxonomy Design  
**Date**: October 3, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  

---

## 1. Acquisition & Verification Overview

In Milestone 4B, the two candidate datasets selected from Group A in Milestone 4A were systematically verified and acquired.

| Dataset | Official Source | Stated License | Acquisition Status | Images | Annotations | Format |
|---|---|---|---|---|---|---|
| **Humans in the Loop (HITL)** | `https://humansintheloop.org` | CC0 1.0 (Public Domain) | **Acquired & Verified** | 1,812 | 24,851 | Supervisely JSON (Polygons) |
| **Fusion-Bike-Parts** | Roboflow Universe (`fgsplbikeparts`) | CC BY 4.0 | **Halted (Platform Access Constraint)** | 6,700 | Estimated ~20,000 | YOLO / COCO Polygons |

---

## 2. Dataset A: Humans in the Loop — Car Parts and Damages

- **Local Storage**: `data/external/humans_in_the_loop/`
- **Verified Commit SHA**: `e4870360afe5e0516e7567cea550d8718482611b`
- **Total Images**: **1,812**
  - Car parts subset: 998 images
  - Car damages subset: 814 images
- **Total Annotations**: **24,851** polygon instances
  - Automotive Part Annotations: **15,767**
  - Vehicle Damage Annotations: **9,084**
- **Total Unique Classes**: **29** (21 Part classes + 8 Damage classes)
- **Resolution Range**: Min `487x280`, Max `1122x690`, Mean `706.7x500.4`
- **Empty Images**: 0
- **Duplicate Images (SHA256 Match)**: 441
- **Malformed Annotations**: 0
- **Annotation Format**: Supervisely JSON with explicit `exterior` polygon vertices `[[x, y], ...]`. Converts losslessly to normalized YOLO segmentation format.

### HITL Class Distribution Breakdown

| Category | Class Name | Instances | Images | Semantic Type |
|---|---|---|---|---|
| DAMAGE | `Scratch` | 3,242 | 517 | Damage Annotation |
| DAMAGE | `Dent` | 1,664 | 629 | Damage Annotation |
| DAMAGE | `Broken part` | 1,500 | 664 | Damage Annotation |
| DAMAGE | `Paint chip` | 1,356 | 279 | Damage Annotation |
| PART | `Back-window` | 1,237 | 812 | Part Annotation |
| PART | `Mirror` | 987 | 839 | Part Annotation |
| PART | `Front-window` | 951 | 826 | Part Annotation |
| PART | `Fender` | 935 | 895 | Part Annotation |
| PART | `Front-door` | 917 | 905 | Part Annotation |
| PART | `Headlight` | 914 | 658 | Part Annotation |
| PART | `Front-wheel` | 885 | 879 | Part Annotation |
| PART | `Back-wheel` | 865 | 856 | Part Annotation |
| PART | `Rocker-panel` | 860 | 858 | Part Annotation |
| PART | `Quarter-panel` | 855 | 838 | Part Annotation |
| PART | `Roof` | 793 | 790 | Part Annotation |
| PART | `Back-door` | 721 | 714 | Part Annotation |
| PART | `Tail-light` | 721 | 470 | Part Annotation |
| PART | `Hood` | 712 | 712 | Part Annotation |
| PART | `Front-bumper` | 705 | 693 | Part Annotation |
| PART | `Windshield` | 632 | 631 | Part Annotation |
| DAMAGE | `Missing part` | 632 | 434 | Damage Annotation |
| PART | `Grille` | 577 | 531 | Part Annotation |
| PART | `Back-bumper` | 443 | 441 | Part Annotation |
| PART | `Trunk` | 416 | 351 | Part Annotation |
| PART | `License-plate` | 370 | 368 | Part Annotation |
| DAMAGE | `Flaking` | 337 | 108 | Damage Annotation |
| DAMAGE | `Corrosion` | 277 | 109 | Damage Annotation |
| PART | `Back-windshield` | 271 | 270 | Part Annotation |
| DAMAGE | `Cracked` | 76 | 67 | Damage Annotation |

---

## 3. Dataset B: Fusion-Bike-Parts Status & Blocker Analysis

- **Official Source**: `https://universe.roboflow.com/fgsplbikeparts/fusion-bike-parts`
- **Creator**: `fgsplbikeparts`
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Published Date**: October 2024
- **Reported Classes**: `Brake_Lever`, `Brake_Pedal`, `Carrier`, `Center_Cowl`, `Chain_Cover`
- **Reported Volume**: 6,700 images with polygon instance segmentation masks.
- **Directory Status**: `data/external/fusion_bike_parts/` initialized and preserved.
- **Access Blocker Details**:
  1. **Cloudflare Anti-Bot Barrier**: Roboflow Universe endpoints return an `HTTP 403 Forbidden (Cloudflare Challenge)` to all automated scripts and non-interactive requests.
  2. **Platform Authentication Requirement**: Roboflow Universe requires an authenticated user account and a private `ROBOFLOW_API_KEY` to generate direct download tokens or export zip archives.
  3. **Milestone Constraint Compliance**: In accordance with Milestone 4B Section 1 (*'If a source or license cannot be verified, STOP that dataset and report the issue'*), acquisition for Fusion-Bike-Parts is stopped and reported without fabricating synthetic data or bypassing platform security.

