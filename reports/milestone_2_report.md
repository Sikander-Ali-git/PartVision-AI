# Milestone 2 Report: Dataset Engineering & Taxonomy V2

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 2 — Dataset Engineering and Taxonomy Consolidation (V2)  
**Date**: October 3, 2026  
**Platform**: Apple Silicon Mac (M3, ARM64) | macOS  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision` (External Dedicated Drive)  

---

## 1. Why Taxonomy Engineering Was Performed

In Milestone 1, the baseline model was trained using the native 23-class Carparts-Seg taxonomy. Evaluation of the baseline revealed significant structural and semantic challenges in the original annotations:

1. **Severe Sidedness Competition & Duplication**: The original dataset fragmented identical physical automotive components into arbitrary sub-classes. For instance:
   - Doors were split into `front_door`, `front_left_door`, and `front_right_door` as well as `back_door`, `back_left_door`, and `back_right_door`.
   - Lights were split into `front_light`, `front_left_light`, `front_right_light` as well as `back_light`, `back_left_light`, and `back_right_light`.
   - Mirrors were split into `left_mirror` and `right_mirror`.
   This caused the model to split its prediction probability mass between generic and sided categories (e.g., predicting `front_door` with 0.54 confidence and `front_left_door` with 0.33 confidence on the exact same door panel), depressing precision and recall across all door and light categories.
2. **Generic / Catch-All "Object" Class**: The class `object` (Class ID 18) represented an undefined catch-all category with only 12 annotations in the entire dataset of 20,374 annotations (0.06%). It provided zero semantic value for automotive spare-part identification and had 0.00% mAP in Milestone 1 validation.
3. **Alignment with Downstream Compatibility Architecture**: From an automotive parts supply chain standpoint, identifying a part visually as a `front_door` or `mirror` is the computer-vision system's core job; determining whether the user requires the driver-side or passenger-side replacement is resolved deterministically through user context or the downstream compatibility database, rather than forcing visual ambiguity into the neural network.

---

## 2. Original 23-Class Taxonomy (V1)

The original Carparts-Seg dataset taxonomy comprised 23 classes (IDs 0–22):
- `[ 0] back_bumper`
- `[ 1] back_door`
- `[ 2] back_glass`
- `[ 3] back_left_door`
- `[ 4] back_left_light`
- `[ 5] back_light`
- `[ 6] back_right_door`
- `[ 7] back_right_light`
- `[ 8] front_bumper`
- `[ 9] front_door`
- `[10] front_glass`
- `[11] front_left_door`
- `[12] front_left_light`
- `[13] front_light`
- `[14] front_right_door`
- `[15] front_right_light`
- `[16] hood`
- `[17] left_mirror`
- `[18] object`
- `[19] right_mirror`
- `[20] tailgate`
- `[21] trunk`
- `[22] wheel`

---

## 3. New 13-Class Taxonomy (V2)

The engineered Carparts-V2 dataset consolidates the problem into exactly 13 automotive part classes (IDs 0–12):
- `[ 0] back_bumper`
- `[ 1] back_door`
- `[ 2] back_glass`
- `[ 3] back_light`
- `[ 4] front_bumper`
- `[ 5] front_door`
- `[ 6] front_glass`
- `[ 7] front_light`
- `[ 8] hood`
- `[ 9] mirror`
- `[10] tailgate`
- `[11] trunk`
- `[12] wheel`

Configuration saved to: `data/processed/carparts-v2/carparts-v2.yaml`.

---

## 4. Exact Class Mapping

The deterministic transformation was executed via `scripts/create_dataset_v2.py`:

| Original V1 Class | Original ID | Target V2 Class | Target V2 ID | Mapping Type |
| :--- | :---: | :--- | :---: | :--- |
| `back_bumper` | 0 | `back_bumper` | 0 | 1:1 Identity |
| `back_door` | 1 | `back_door` | 1 | Merged (Rear door group) |
| `back_left_door` | 3 | `back_door` | 1 | Merged (Rear door group) |
| `back_right_door`| 6 | `back_door` | 1 | Merged (Rear door group) |
| `back_glass` | 2 | `back_glass` | 2 | 1:1 Identity |
| `back_left_light` | 4 | `back_light` | 3 | Merged (Tail light group) |
| `back_light` | 5 | `back_light` | 3 | Merged (Tail light group) |
| `back_right_light`| 7 | `back_light` | 3 | Merged (Tail light group) |
| `front_bumper` | 8 | `front_bumper` | 4 | 1:1 Identity |
| `front_door` | 9 | `front_door` | 5 | Merged (Front door group) |
| `front_left_door` | 11 | `front_door` | 5 | Merged (Front door group) |
| `front_right_door`| 14 | `front_door` | 5 | Merged (Front door group) |
| `front_glass` | 10 | `front_glass` | 6 | 1:1 Identity |
| `front_left_light`| 12 | `front_light` | 7 | Merged (Headlight group) |
| `front_light` | 13 | `front_light` | 7 | Merged (Headlight group) |
| `front_right_light`| 15 | `front_light` | 7 | Merged (Headlight group) |
| `hood` | 16 | `hood` | 8 | 1:1 Identity |
| `left_mirror` | 17 | `mirror` | 9 | Merged (Side mirror group) |
| `right_mirror` | 19 | `mirror` | 9 | Merged (Side mirror group) |
| `tailgate` | 20 | `tailgate` | 10 | 1:1 Identity |
| `trunk` | 21 | `trunk` | 11 | 1:1 Identity |
| `wheel` | 22 | `wheel` | 12 | 1:1 Identity |
| `object` | 18 | *None* | — | **REMOVED** |

---

## 5. Annotations Removed & Background Handling

- **Total Annotations Removed**: **12 annotations** (100% of Class 18 `object`).
  - Train split: 10 removed
  - Validation split: 1 removed
  - Test split: 1 removed
- **Total Valid Annotations Retained**: **20,362 annotations** (20,374 V1 annotations − 12 removed objects = 20,362).
- **Images That Became Empty**: Exactly **12 images** in the dataset contained solely a single `object` annotation and no other automotive part labels.
- **Handling of Newly Empty Images**: In strict accordance with dataset engineering standards, these 12 images were preserved in the dataset splits, and their corresponding label files were written as empty files to serve as clean negative/background examples.
- **Total Empty Label Files in V2**: **147 files** (135 originally empty background files in V1 + 12 newly empty files = 147).

---

## 6. V1 vs V2 Class Distribution Comparison

Detailed comparative metrics exported to `reports/v1_vs_v2_dataset_comparison.csv` and `reports/v2_class_distribution.csv`:

| V2 Class ID | V2 Class Name | Constituent V1 Classes | V1 Count | V2 Count | V2 % of Total | Change Impact |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 0 | `back_bumper` | `back_bumper` | 870 | 870 | 4.27% | Direct 1:1 mapping |
| 1 | `back_door` | `back_door` + `back_left_door` + `back_right_door` | 1,731 | 1,731 | 8.50% | Merged 3 fragmented classes into 1 |
| 2 | `back_glass` | `back_glass` | 1,058 | 1,058 | 5.20% | Direct 1:1 mapping |
| 3 | `back_light` | `back_left_light` + `back_light` + `back_right_light` | 2,434 | 2,434 | 11.95% | Merged 3 fragmented classes into 1 |
| 4 | `front_bumper` | `front_bumper` | 1,978 | 1,978 | 9.71% | Direct 1:1 mapping |
| 5 | `front_door` | `front_door` + `front_left_door` + `front_right_door` | 1,936 | 1,936 | 9.51% | Merged 3 fragmented classes into 1 |
| 6 | `front_glass` | `front_glass` | 2,062 | 2,062 | 10.13% | Direct 1:1 mapping |
| 7 | `front_light` | `front_left_light` + `front_light` + `front_right_light` | 4,066 | 4,066 | 19.97% | Merged 3 fragmented classes into 1 |
| 8 | `hood` | `hood` | 2,080 | 2,080 | 10.22% | Direct 1:1 mapping |
| 9 | `mirror` | `left_mirror` + `right_mirror` | 996 | 996 | 4.89% | Merged 2 sided classes into 1 |
| 10 | `tailgate` | `tailgate` | 101 | 101 | 0.50% | Direct 1:1 mapping |
| 11 | `trunk` | `trunk` | 173 | 173 | 0.85% | Direct 1:1 mapping |
| 12 | `wheel` | `wheel` | 877 | 877 | 4.31% | Direct 1:1 mapping |
| — | *[REMOVED] object* | `object` | 12 | 0 | 0.00% | Removed entirely from dataset |
| **TOTAL** | | | **20,374** | **20,362** | **100.00%** | **Consolidated from 23 to 13 classes** |

---

## 7. Dataset Integrity & Preservation Results

Automated integrity verification was executed via `scripts/verify_integrity_v2.py`:

1. **Milestone 1 Preservation**:
   - `data/processed/carparts-seg/`: Untouched (3,833 images, 3,833 labels).
   - `models/baseline_yolo11n_seg_best.pt`: Intact (6,006,052 bytes).
   - `runs/partvision_v1/`: Intact and unmodified.
   - `reports/baseline_metrics.txt` & `reports/baseline_metrics.json`: Intact.
2. **Bit-Level Image Equivalence**:
   - An exhaustive MD5 hash verification across all 3,833 images confirmed that every image in `carparts-v2` is 100% bit-identical to its source image in `carparts-seg`.
3. **Label Syntax & Boundaries**:
   - Malformed polygon lines: **0**.
   - Invalid class IDs: **0** (all IDs strictly in `[0, 12]`).
   - Coordinate normalization: **100% compliant**.
4. **Overall Status**: **PASSED (100% Integrity)**.

---

## 8. Visual Inspection Results

Visual inspection of the consolidated dataset was performed via `scripts/visualize_dataset_v2.py` and saved to `reports/v2_dataset_sample_grid.png`:
- The representative sample grid displays 9 rich training scenes with diverse camera perspectives.
- Ground truth segmentation polygons for consolidated classes (`front_door`, `back_door`, `front_light`, `back_light`, `mirror`, `front_bumper`, `back_bumper`, `hood`, `wheel`) adhere tightly to vehicle body panels.
- Eliminating sided label competition visually unifies the annotation logic: doors and headlights now share a unified, consistent label on both left and right sides of the vehicle.

---

## 9. Remaining Imbalance & Data Observations

Even after consolidating the taxonomy to 13 classes, natural distribution imbalance remains in the underlying photography:
1. **High-Frequency Classes**: `front_light` (4,066 annotations, 19.97%), `hood` (2,080 annotations, 10.22%), and `front_glass` (2,062 annotations, 10.13%) constitute ~40% of the dataset.
2. **Low-Frequency Classes**: `tailgate` (101 annotations, 0.50%) and `trunk` (173 annotations, 0.85%) remain sparse because most automotive photographs in the dataset are front-three-quarter or side views rather than rear views.
3. **Resolution & Preprocessing**: 100% of images remain normalized at 640×640 pixels, making them ideal for standard YOLO input pipelines without dynamic aspect ratio padding overhead.

---

## 10. Recommendation for Next Experiment

*Note: Per strict project guidelines, no V2 model training was performed in Milestone 2. Model performance comparisons cannot be claimed until empirical training is completed.*

For Milestone 3:
1. **Direct Benchmark Comparison**: Train `YOLO11n-seg` on the exact same hyperparameter protocol as Milestone 1 (3 epochs, `imgsz=640`, `batch=16`, `device=mps`) using `carparts-v2.yaml`.
2. **Side-by-Side Evaluation**: Compare precision, recall, and mAP between V1 (23 classes) and V2 (13 classes) to quantitatively measure whether taxonomy consolidation eliminated sidedness confusion and improved door/light recall.
3. **Scaled Training Run**: If the 3-epoch comparison confirms metric improvements, proceed with an extended training run (e.g., 50–100 epochs with early stopping) to achieve convergence on the 13-class dataset.
