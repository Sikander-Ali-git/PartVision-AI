# Milestone 1 Report: Computer-Vision Baseline

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 1 — Baseline Model Development & Pipeline Validation  
**Date**: October 3, 2026  
**Platform**: Apple Silicon Mac (M3, ARM64) | macOS  
**Execution Location**: `/Volumes/Toshiba 1TB/PartVision` (External Dedicated Drive)  

---

## 1. Project Objective

PartVision AI aims to provide accurate identification of automotive spare parts directly from user-supplied imagery. The computer-vision component is designed solely to detect and segment visually recognizable parts in an image. Downstream part compatibility, OEM part numbering, interchangeability, and vehicle fitment will be resolved by querying a structured compatibility database in future milestones rather than relying on model hallucinations.

The primary objective of Milestone 1 is to establish a 100% reproducible, verified computer-vision baseline using the official Ultralytics **Carparts-Seg** dataset and the **YOLO11n-seg** architecture without altering dataset taxonomies or introducing complex custom losses.

---

## 2. Dataset Source & Provenance

The dataset utilized is the official Carparts-Seg dataset distributed by Ultralytics:
- **Source URL**: `https://github.com/ultralytics/assets/releases/download/v0.0.0/carparts-seg.zip`
- **Raw Archive Location**: `data/raw/carparts-seg.zip`
- **Archive Size**: 139,535,504 bytes (133.07 MB)
- **SHA256 Checksum**: `e2eea20030d02366b07174bcdbcc843f63791bdd53962a83e00636d15e78e41f`
- **Extraction Location**: `data/processed/carparts-seg/`
- **Dataset Preservation**: The original dataset archive and extracted directories were preserved in their native structure without modification.

---

## 3. Dataset Statistics

The dataset was parsed, verified, and cataloged across the official three splits:

| Metric | Train Split | Validation Split | Test Split | Total Dataset |
| :--- | :--- | :--- | :--- | :--- |
| **Total Images** | 3,156 | 401 | 276 | **3,833** |
| **Total Label Files** | 3,156 | 401 | 276 | **3,833** |
| **Empty Annotation Files** | 116 (3.68%) | 12 (2.99%) | 7 (2.54%) | **135** (3.52%) |
| **Total Instance Annotations**| 16,733 | 2,042 | 1,599 | **20,374** |
| **Average Annotations / Image**| 5.30 | 5.09 | 5.79 | **5.32** |
| **Image Resolution** | 640 x 640 (100%)| 640 x 640 (100%) | 640 x 640 (100%) | **640 x 640 (100%)** |
| **Number of Classes** | 23 | 23 | 23 | **23** |

---

## 4. Class Distribution

The dataset taxonomy consists of 23 original classes. No classes were renamed or merged in Milestone 1.

| Class ID | Class Name | Train Annotations | Val Annotations | Test Annotations | Total Annotations | Overall % |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 0 | `back_bumper` | 732 | 94 | 44 | 870 | 4.27% |
| 1 | `back_door` | 1,008 | 159 | 85 | 1,252 | 6.15% |
| 2 | `back_glass` | 890 | 115 | 53 | 1,058 | 5.19% |
| 3 | `back_left_door` | 204 | 15 | 36 | 255 | 1.25% |
| 4 | `back_left_light` | 244 | 19 | 28 | 291 | 1.43% |
| 5 | `back_light` | 1,588 | 226 | 88 | 1,902 | 9.34% |
| 6 | `back_right_door` | 184 | 12 | 28 | 224 | 1.10% |
| 7 | `back_right_light` | 204 | 13 | 24 | 241 | 1.18% |
| 8 | `front_bumper` | 1,616 | 208 | 154 | 1,978 | 9.71% |
| 9 | `front_door` | 1,150 | 167 | 92 | 1,409 | 6.92% |
| 10 | `front_glass` | 1,682 | 214 | 166 | 2,062 | 10.12% |
| 11 | `front_left_door` | 224 | 15 | 40 | 279 | 1.37% |
| 12 | `front_left_light` | 412 | 30 | 62 | 504 | 2.47% |
| 13 | `front_light` | 2,520 | 373 | 195 | 3,088 | 15.16% |
| 14 | `front_right_door` | 208 | 12 | 28 | 248 | 1.22% |
| 15 | `front_right_light` | 392 | 26 | 56 | 474 | 2.33% |
| 16 | `hood` | 1,706 | 214 | 160 | 2,080 | 10.21% |
| 17 | `left_mirror` | 404 | 31 | 62 | 497 | 2.44% |
| 18 | `object` | 10 | 1 | 1 | 12 | 0.06% |
| 19 | `right_mirror` | 412 | 31 | 56 | 499 | 2.45% |
| 20 | `tailgate` | 88 | 5 | 8 | 101 | 0.50% |
| 21 | `trunk` | 146 | 9 | 18 | 173 | 0.85% |
| 22 | `wheel` | 709 | 53 | 115 | 877 | 4.30% |
| **Total** | | **16,733** | **2,042** | **1,599** | **20,374** | **100.00%** |

*Note: Visual distribution plots are archived at `reports/class_distribution.png` and tabular figures at `reports/class_distribution.csv`.*

---

## 5. Dataset Quality Checks

The validation script `scripts/validate_dataset.py` performed automated structural checks:
- **File Pairing**: 100% match between image files and `.txt` label files (3,833 / 3,833).
- **Missing Label Files**: 0.
- **Orphan Label Files**: 0.
- **Corrupt / Unreadable Images**: 0 across all splits.
- **Malformed Polygon Lines**: 0. All polygon coordinates conform to normalized floats in `[0.0, 1.0]` with even coordinate counts ($\ge 6$ coordinates per polygon).
- **Empty Background Images**: 135 images total (116 train, 12 val, 7 test) have valid empty label files acting as true negatives / background examples.
- **Ground Truth Visual Inspection**: Executed via `scripts/visualize_dataset.py` and saved to `reports/dataset_sample_grid.png`, verifying tight polygon boundaries around vehicle components.

---

## 6. Model Architecture

- **Architecture**: `YOLO11n-seg` (Ultralytics instance segmentation nano variant).
- **Base Checkpoint**: Pretrained `yolo11n-seg.pt` (COCO-pretrained weights).
- **Summary**:
  - Layers: 113 layers (fused)
  - Parameters: 2,839,053 (~2.84M parameters)
  - Computational Complexity: 9.7 GFLOPs
  - Model Footprint: 5.7 MB (`baseline_yolo11n_seg_best.pt`)

---

## 7. Training Configuration

The baseline was trained using standard Ultralytics hyperparameters without custom loss modifications or aggressive augmentations:
- **Epochs**: 3
- **Image Resolution (`imgsz`)**: 640
- **Batch Size**: 16
- **DataLoader Workers**: 0 (avoiding macOS IPC socket overhead)
- **Hardware Acceleration (`device`)**: `mps` (Apple Silicon Metal Performance Shaders on Apple M3)
- **Optimizer**: Default Ultralytics auto-optimizer (SGD / AdamW with automatic momentum)
- **Output Directory**: `runs/partvision_v1/`
- **Best Weights Export**: `models/baseline_yolo11n_seg_best.pt`

---

## 8. Training Duration & System Resource Utilization

- **Total Training Duration**: **30 minutes 20.5 seconds** (1,820.47 seconds)
- **Per-Epoch Duration**: ~10 minutes per epoch (3,156 training images, 198 batches / epoch)
- **Inference Speed**: ~2.7 ms inference, 0.4 ms preprocess, 37.3 ms postprocess per image on M3 MPS.
- **Storage Profile**:
  - Starting Free Space on External HDD: 919.48 GB
  - Ending Free Space on External HDD: 921.63 GB (Available: ~921 GB, Project footprint: ~1.2 GB including raw zip, extracted dataset, venv, and checkpoints)
  - No storage alerts or low-space warnings were encountered.

---

## 9. Validation Metrics

Evaluated on the 401 images (2,042 part instances) of the validation split:

### Overall Performance

| Evaluation Mode | Precision | Recall | mAP@0.50 | mAP@0.50:0.95 |
| :--- | :---: | :---: | :---: | :---: |
| **Object Detection (Box)** | **0.6536** | **0.4876** | **0.4803** | **0.3721** |
| **Instance Segmentation (Mask)** | **0.6663** | **0.4938** | **0.4935** | **0.3581** |

### Per-Class Performance Breakdown

| Class Name | Box P | Box R | Box mAP50 | Box mAP50-95 | Seg P | Seg R | Seg mAP50 | Seg mAP50-95 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `back_bumper` | 0.6743 | 0.9043 | 0.8510 | 0.6274 | 0.6824 | 0.9043 | 0.8448 | 0.5280 |
| `back_door` | 0.4909 | 0.6352 | 0.5263 | 0.4108 | 0.4930 | 0.6226 | 0.5258 | 0.3809 |
| `back_glass` | 0.7617 | 0.7652 | 0.7879 | 0.6134 | 0.7718 | 0.7645 | 0.7877 | 0.5956 |
| `back_left_door` | 1.0000 | 0.0000 | 0.1329 | 0.1087 | 1.0000 | 0.0000 | 0.1285 | 0.1005 |
| `back_left_light` | 0.3848 | 0.6316 | 0.4501 | 0.3548 | 0.4224 | 0.6842 | 0.5249 | 0.3558 |
| `back_light` | 0.6702 | 0.6814 | 0.6703 | 0.4753 | 0.6844 | 0.6903 | 0.6991 | 0.4614 |
| `back_right_door` | 1.0000 | 0.0000 | 0.0781 | 0.0632 | 1.0000 | 0.0000 | 0.0685 | 0.0497 |
| `back_right_light`| 0.2978 | 0.5385 | 0.4309 | 0.3776 | 0.3006 | 0.5385 | 0.4309 | 0.3762 |
| `front_bumper` | 0.8466 | 0.9821 | 0.9405 | 0.7876 | 0.8463 | 0.9794 | 0.9405 | 0.7524 |
| `front_door` | 0.4869 | 0.6591 | 0.5842 | 0.4576 | 0.4880 | 0.6507 | 0.5805 | 0.4446 |
| `front_glass` | 0.8670 | 0.9486 | 0.9456 | 0.8385 | 0.8690 | 0.9486 | 0.9456 | 0.8470 |
| `front_left_door` | 0.6915 | 0.0667 | 0.3271 | 0.2512 | 0.7090 | 0.0667 | 0.3174 | 0.2112 |
| `front_left_light`| 0.4002 | 0.4003 | 0.3602 | 0.2666 | 0.4174 | 0.4000 | 0.3696 | 0.2639 |
| `front_light` | 0.7354 | 0.7989 | 0.7814 | 0.5708 | 0.7426 | 0.7968 | 0.7847 | 0.5374 |
| `front_right_door`| 0.3518 | 0.2283 | 0.2985 | 0.2404 | 0.3381 | 0.2156 | 0.2985 | 0.2097 |
| `front_right_light`| 0.4420 | 0.5000 | 0.5132 | 0.4139 | 0.4451 | 0.5000 | 0.5132 | 0.4114 |
| `hood` | 0.8876 | 0.9486 | 0.9248 | 0.7773 | 0.8861 | 0.9439 | 0.9247 | 0.7582 |
| `left_mirror` | 0.2856 | 0.5161 | 0.2768 | 0.1711 | 0.3044 | 0.5161 | 0.2737 | 0.1773 |
| `object` | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| `right_mirror` | 0.3157 | 0.6129 | 0.4497 | 0.2764 | 0.3196 | 0.6129 | 0.4497 | 0.2905 |
| `tailgate` | 1.0000 | 0.0000 | 0.1354 | 0.0873 | 1.0000 | 0.0000 | 0.1354 | 0.0959 |
| `trunk` | 1.0000 | 0.0000 | 0.2131 | 0.1449 | 1.0000 | 0.0000 | 0.2131 | 0.1442 |
| `wheel` | 0.4424 | 0.3962 | 0.3693 | 0.2439 | 0.6055 | 0.5213 | 0.5945 | 0.2443 |

---

## 10. Test Prediction Examples

Inference was run via `scripts/predict_test.py` on unseen images from the test set with a confidence threshold of `0.25`:
- **Summary File**: `reports/test_predictions/prediction_summary.json`
- **Visual Overview Grid**: `reports/test_predictions/test_prediction_grid.png`
- **Key Qualitative Findings**:
  1. **Primary Structural Parts**: The model reliably identifies and segments large panels (`front_glass`, `hood`, `front_bumper`, `back_bumper`) with high confidence (> 85–96%).
  2. **Boundary Quality**: The segmentation polygon masks adhere tightly to contours of windshields, headlights, and bumpers.
  3. **Door Ambiguity**: Side door detections often show competition between generic `front_door`/`back_door` labels and specific `front_left_door`/`back_left_door` labels.
  4. **Small Parts**: Mirror detection produces lower confidence (~0.30–0.52) due to smaller relative pixel scale.

---

## 11. Observed Limitations & Risk Analysis

1. **Not Production-Ready**: A 3-epoch baseline model is strictly an initial proof of concept to validate the end-to-end training and inference pipeline. It is not ready for deployment.
2. **Exterior / Body Panel Scope**: The Carparts-Seg dataset covers **only exterior vehicle body parts**. It does not possess any ability to identify internal mechanical parts (engines, alternators, transmissions, radiators, spark plugs, filters, brake pads) or interior cabin components.
3. **Severe Class Imbalance**: High-frequency classes (`front_light` with 3,088 annotations) vastly outperform underrepresented classes (`object` with 12 annotations, `tailgate` with 101 annotations).
4. **Taxonomy Duplication & Sidedness**: The dataset possesses overlapping classes (e.g. `front_light` vs `front_left_light` and `front_right_light`; `front_door` vs `front_left_door`). In Milestone 1, preserving the official taxonomy as instructed meant accepting this split in prediction confidence.
5. **Separation of Vision and Compatibility**: The vision model output must never be used directly to declare mechanical compatibility between vehicles. Part fitment depends on engine codes, model years, chassis numbers, and VIN specifications, which must be cross-referenced against a structured database.

---

## 12. Recommended Next Steps (Milestone 2 & Beyond)

1. **Longer Training Schedule**: Train YOLO11n-seg or YOLO11s-seg for 50–100 epochs with early stopping to allow mask boundaries and underrepresented classes to converge.
2. **Taxonomy Rationalization (Future Milestone)**: In consultation with domain requirements, explore merging redundant sided classes into unified classes (e.g., merging `front_left_door` + `front_right_door` + `front_door` into `car_door`, and deriving side/orientation via image position or metadata).
3. **Targeted Data Augmentation & Balancing**: Apply class-balanced sampling or focal weighting to improve recall on scarce classes like `tailgate`, `trunk`, and `mirror`.
4. **Mechanical / Spare-Part Dataset Expansion**: Collect and curate datasets representing internal, replacement, and unmounted spare parts (e.g., brake calipers, alternators, oil filters) that mechanics and buyers actually purchase as detached parts.
5. **Compatibility Database Design**: Design the relational database schema linking detected visual part categories to OEM part numbers, vehicle year/make/model hierarchies, and interchange groups.
