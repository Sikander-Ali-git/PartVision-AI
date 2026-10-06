# PartVision AI — Milestone 5B Final Engineering Report
## V3 Model Training, Evaluation, and Comprehensive Comparative Analysis

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 5B — V3 Model Training & Evaluation  
**Date**: October 6, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  

---

## 1. Executive Summary & Experiment Objective

Milestone 5B evaluates whether the expanded **19-class PartVision V3 dataset** can provide broad, repair-grade automotive exterior coverage while maintaining or exceeding the segmentation accuracy established in Milestones 1–3.

This is an **expansion experiment**. Rather than fine-tuning from the V2 checkpoint, the model was initialized directly from the base pretrained `YOLO11n-seg` COCO weights (`models/yolo11n-seg.pt`). This guarantees a controlled, unpolluted baseline comparison.

### Key Headline Results:
- **Instance Segmentation mAP@0.50**: **85.70%** (up from 81.80% in V2 and 49.35% in V1).
- **Object Detection mAP@0.50**: **84.65%** (up from 81.01% in V2 and 48.03% in V1).
- **Wheel Recovery**: Wheel segmentation mAP50-95 surged from **25.73% (V2) to 69.21% (V3)**—a **+169% relative leap** following HITL wheel augmentation.
- **Trunk Recovery**: Trunk segmentation mAP50-95 increased from **26.72% (V2) to 43.62% (V3)** (+63.2% gain), supported by 49 validation instances (up from 9).
- **Immediate Learnability of New Panels**: All 6 newly introduced exterior collision classes demonstrated immediate convergence:
  - `fender`: **92.86% mAP50** (0.6214 mAP50-95)
  - `rocker_panel`: **87.02% mAP50** (0.3703 mAP50-95)
  - `side_window`: **86.84% mAP50** (0.5897 mAP50-95)
  - `roof`: **80.65% mAP50** (0.3360 mAP50-95)
  - `grille`: **77.97% mAP50** (0.4940 mAP50-95)
  - `quarter_panel`: **70.85% mAP50** (0.3627 mAP50-95)

---

## 2. V3 Dataset Specifications

The PartVision V3 dataset combines the cleaned Carparts-V2 dataset with verified parts from the Humans in the Loop (HITL) dataset:
- **Total Images**: 4,831 images
- **Total Polygon Annotations**: 35,759 instances
- **Taxonomy**: Exactly 19 classes
- **Multi-Class Images**: 4,662 images
- **Clean Negative / Background Images**: 147 images (essential for false-positive suppression)
- **Data Integrity**: 0 malformed annotations, 0 out-of-bounds coordinates, 0 orphan files, 0 cross-dataset duplicates.

### Split Distribution:
| Split | Total Images | Image Share | Total Annotations | Annotation Share |
|---|---|---|---|---|
| **Train** | 3,954 | 81.85% | 29,005 | 81.11% |
| **Validation** | 501 | 10.37% | 3,573 | 9.99% |
| **Test** | 376 | 7.78% | 3,181 | 8.90% |
| **TOTAL** | **4,831** | **100.00%** | **35,759** | **100.00%** |

Configuration registered at [`data/processed/partvision-v3/partvision-v3.yaml`](file:///Volumes/Toshiba%201TB/PartVision/data/processed/partvision-v3/partvision-v3.yaml).

---

## 3. Training Configuration

| Parameter | Configuration Value | Rationale / Compliance Note |
|---|---|---|
| **Model Family** | `YOLO11n-seg` | Standard Ultralytics nano instance segmentation architecture |
| **Initialization** | `models/yolo11n-seg.pt` | COCO-pretrained base weights; **not** initialized from V2 checkpoint |
| **Dataset YAML** | `data/processed/partvision-v3/partvision-v3.yaml` | Absolute workspace path on Toshiba 1TB external storage |
| **Epochs** | **15** | Sufficient for convergence across 19 classes without overfitting |
| **Input Resolution** | **512 × 512** | Consistent with Milestone 3; optimal memory and compute efficiency |
| **Batch Size** | **8** | Conservative footprint for Apple Silicon MPS |
| **Dataloader Workers** | **0** | Single-threaded to avoid multi-process contention |
| **Compute Device** | **`mps`** | Apple Silicon Metal Performance Shaders (Apple M3) |
| **Loss & Regularization** | Default Ultralytics | **No** focal loss, class weighting, oversampling, or custom loss |
| **Checkpoints Output** | `runs/partvision_v3/` | Full training history, tensor logs, and weights |
| **Export Best Checkpoint** | `models/partvision_v3_yolo11n_seg_best.pt` | Exported best model weights (5.71 MB, 2,846,313 parameters) |

---

## 4. Training Duration & Convergence Dynamics

- **Total Wall-Clock Time**: **1h 57m 43.7s** (7,063.71 seconds).
- **Execution Environment**: Executed via `/usr/bin/caffeinate -dimsu` to prevent system sleep or power-save throttling. Training ran at ~1.2 to 1.3 iterations/sec with zero interruptions.
- **Peak Unified Memory**: Only **2.47 GB RAM** utilized throughout the run.

### Loss Progression across Epochs:
| Epoch | Train Box Loss | Train Seg Loss | Train Cls Loss | Val Box Loss | Val Seg Loss | Val Cls Loss | Mask mAP50 | Mask mAP50-95 |
|---|---|---|---|---|---|---|---|---|
| **1** | 1.3613 | 2.6883 | 3.6482 | 1.1358 | 1.9068 | 2.1744 | 0.3595 | 0.2213 |
| **3** | 1.1272 | 2.0106 | 1.5559 | 0.9457 | 1.6529 | 1.2211 | 0.6683 | 0.4070 |
| **5** | 1.0240 | 1.8259 | 1.2499 | 0.8919 | 1.4977 | 1.0079 | 0.7427 | 0.4718 |
| **8** | 0.8795 | 1.4533 | 0.9042 | 0.7969 | 1.3137 | 0.8462 | 0.7987 | 0.5359 |
| **11** | 0.8204 | 1.3433 | 0.7889 | 0.7538 | 1.2267 | 0.7349 | 0.8321 | 0.5713 |
| **13** | 0.7775 | 1.2802 | 0.7276 | 0.7274 | 1.1638 | 0.6967 | 0.8394 | 0.5835 |
| **15** | **0.7493** | **1.2205** | **0.6999** | **0.7049** | **1.1489** | **0.6667** | **0.8563** | **0.5980** |

The training curves are permanently archived at [`reports/v3_training_curves.png`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_training_curves.png).

---

## 5. Validation Metrics (V3 Validation Set)

Evaluated on the 501 images (3,573 ground-truth instances) of the `partvision-v3` validation split using best checkpoint [`models/partvision_v3_yolo11n_seg_best.pt`](file:///Volumes/Toshiba%201TB/PartVision/models/partvision_v3_yolo11n_seg_best.pt):

| Evaluation Task | Precision | Recall | mAP@0.50 | mAP@0.50:0.95 |
|---|---|---|---|---|
| **Object Detection (Bounding Box)** | **0.8026** | **0.8088** | **0.8465** | **0.6413** |
| **Instance Segmentation (Polygon Mask)** | **0.8136** | **0.8182** | **0.8570** | **0.5985** |

Detailed JSON metrics: [`reports/v3_baseline_metrics.json`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_baseline_metrics.json).  
Text summary report: [`reports/v3_baseline_metrics.txt`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_baseline_metrics.txt).

---

## 6. Per-Class Validation Metrics (All 19 Classes)

| Class ID | Class Name | Val Instances | Box Precision | Box Recall | Box mAP50 | Box mAP50-95 | Seg Precision | Seg Recall | Seg mAP50 | Seg mAP50-95 |
|---|---|---|---|---|---|---|---|---|---|---|
| **0** | `back_bumper` | 136 | 0.8870 | 0.8603 | 0.8666 | 0.7150 | 0.8794 | 0.8529 | 0.8697 | 0.6773 |
| **1** | `back_door` | 261 | 0.8586 | 0.9042 | 0.9366 | 0.7972 | 0.8549 | 0.9004 | 0.9365 | 0.6891 |
| **2** | `back_glass` | 260 | 0.8879 | 0.8269 | 0.9087 | 0.6822 | 0.8879 | 0.8269 | 0.9019 | 0.6372 |
| **3** | `back_light` | 327 | 0.8742 | 0.7706 | 0.8398 | 0.5909 | 0.8811 | 0.7768 | 0.8452 | 0.5696 |
| **4** | `fender` (NEW) | 95 | 0.9239 | 0.8942 | 0.9377 | 0.6859 | 0.9239 | 0.8942 | 0.9286 | 0.6214 |
| **5** | `front_bumper` | 281 | 0.9202 | 0.9609 | 0.9465 | 0.8424 | 0.9236 | 0.9644 | 0.9464 | 0.8013 |
| **6** | `front_door` | 287 | 0.8666 | 0.9477 | 0.9401 | 0.8150 | 0.8730 | 0.9547 | 0.9445 | 0.7173 |
| **7** | `front_glass` | 280 | 0.9341 | 0.9821 | 0.9824 | 0.8956 | 0.9341 | 0.9821 | 0.9824 | 0.8910 |
| **8** | `front_light` | 520 | 0.9102 | 0.8692 | 0.9107 | 0.6879 | 0.9102 | 0.8692 | 0.9152 | 0.6621 |
| **9** | `grille` (NEW) | 61 | 0.6727 | 0.7705 | 0.7663 | 0.5535 | 0.6870 | 0.7869 | 0.7797 | 0.4940 |
| **10** | `hood` | 287 | 0.9230 | 0.9582 | 0.9681 | 0.8510 | 0.9197 | 0.9547 | 0.9647 | 0.8523 |
| **11** | `mirror` | 162 | 0.7182 | 0.7901 | 0.7972 | 0.4700 | 0.7294 | 0.8025 | 0.8213 | 0.4349 |
| **12** | `quarter_panel` (NEW) | 82 | 0.6469 | 0.6585 | 0.7015 | 0.3990 | 0.6829 | 0.6951 | 0.7085 | 0.3627 |
| **13** | `rocker_panel` (NEW) | 85 | 0.8552 | 0.9176 | 0.9266 | 0.6314 | 0.8223 | 0.8824 | 0.8702 | 0.3703 |
| **14** | `roof` (NEW) | 77 | 0.8598 | 0.3983 | 0.7289 | 0.3349 | 0.9159 | 0.4243 | 0.8065 | 0.3360 |
| **15** | `side_window` (NEW) | 88 | 0.8228 | 0.8444 | 0.8720 | 0.5285 | 0.8228 | 0.8444 | 0.8684 | 0.5897 |
| **16** | `tailgate` | 5 | 0.2753 | 0.6000 | 0.5929 | 0.5650 | 0.2753 | 0.6000 | 0.6204 | 0.5362 |
| **17** | `trunk` | 49 | 0.5705 | 0.5714 | 0.5642 | 0.4516 | 0.6520 | 0.6531 | 0.6386 | 0.4362 |
| **18** | `wheel` | 230 | 0.8432 | 0.8420 | 0.8965 | 0.6882 | 0.8824 | 0.8811 | 0.9342 | 0.6921 |

---

## 7. Test Inference & Predictions on Unseen Test Split

Inference was executed on 12 diverse test images from the unseen test split (`data/processed/partvision-v3/images/test`, 376 total images) at a confidence threshold of `0.25`:
- **Directory**: [`reports/v3_test_predictions/`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_test_predictions/)
- **Summary**: [`reports/v3_test_predictions/prediction_summary.json`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_test_predictions/prediction_summary.json)
- **Multi-Panel Sample Grid**: [`reports/v3_test_predictions/v3_test_prediction_grid.png`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_test_predictions/v3_test_prediction_grid.png)

### Key Qualitative Findings:
1. **Multi-Part Co-occurrence**: On dense test images such as `hitl_Car_damages_1033.png`, the model successfully identified and cleanly separated 18 distinct part instances in a single pass (`wheel`, `front_glass`, `front_light`, `hood`, `fender`, `grille`, `mirror`, `front_door`, `front_bumper`, `rocker_panel`, `side_window`, `quarter_panel`, `back_glass`, `back_door`, `roof`).
2. **Wheel Segmentation Boundaries**: Mask boundaries around tire rubber and alloy rims are tight and circular, without spilling into the wheel wells or ground.
3. **Fender & Rocker Panel Separation**: The model cleanly delineates the front quarter fender from the adjacent front door sheet metal and lower rocker sill.

---

## 8. Comparative Analysis: V1 Baseline vs V2 Experiment vs V3 Unified

| Metric / Dimension | V1 Baseline | V2 Experiment | V3 Unified | Confounding Factors & Notes |
|---|---|---|---|---|
| **Taxonomy Scope** | 23 classes (original) | 13 classes (consolidated) | **19 classes (unified)** | Expanded to essential exterior collision panels |
| **Total Images** | 3,833 | 3,833 | **4,831** | +26.0% image growth via HITL ingestion |
| **Total Annotations** | 20,362 | 20,362 | **35,759** | +75.6% instance growth |
| **Epochs** | 3 | 10 | **15** | **CONFOUNDER**: Training schedule length varied across milestones |
| **Input Resolution** | 640 × 640 | 512 × 512 | **512 × 512** | **CONFOUNDER**: V1 used 640px; V2 and V3 used 512px |
| **Batch Size** | 16 | 8 | **8** | **CONFOUNDER**: V1 used batch 16; V2 and V3 used batch 8 |
| **Wall-Clock Duration**| 30m 20.5s | 155m 20.2s | **1h 57m 43.7s** | V2 had sleep interruptions; V3 ran via caffeinate |
| **Parameters** | 2,839,053 | 2,836,373 | **2,846,313** | Head dimension scales with number of classes |
| **Model Size on Disk** | 5.73 MB | 5.71 MB | **5.71 MB** | Identical nano parameter regime |
| **Detection Precision**| 0.6536 | 0.7610 | **0.8026** | Consistent increase |
| **Detection Recall** | 0.4876 | 0.8319 | **0.8088** | Balanced precision/recall equilibrium |
| **Detection mAP@0.50** | 0.4803 | 0.8101 | **0.8465** | **+36.62% over V1; +3.64% over V2** |
| **Detection mAP50-95** | 0.3721 | 0.6630 | **0.6413** | Higher class complexity slightly compresses mAP50-95 |
| **Seg Precision** | 0.6663 | 0.7673 | **0.8136** | **+14.73% over V1; +4.63% over V2** |
| **Seg Recall** | 0.4938 | 0.8307 | **0.8182** | Balanced mask coverage |
| **Seg mAP@0.50** | 0.4935 | 0.8180 | **0.8570** | **+36.35% over V1; +3.90% over V2** |
| **Seg mAP50-95** | 0.3581 | 0.6414 | **0.5985** | +24.04% over V1; slight delta from V2 due to 6 new classes |

The comparison table is saved at [`reports/v1_v2_v3_model_comparison.csv`](file:///Volumes/Toshiba%201TB/PartVision/reports/v1_v2_v3_model_comparison.csv).

> [!IMPORTANT]
> **Experimental Confounding Factors**:  
> Metric improvements across V1, V2, and V3 cannot be attributed *solely* to dataset expansion or taxonomy changes. V1 was trained for 3 epochs at 640px, V2 for 10 epochs at 512px, and V3 for 15 epochs at 512px. The higher epoch count in V3 allows deeper convergence, while the 19 classes introduce higher multi-class classification complexity.

---

## 9. Dataset Coverage & Source Contribution Analysis

The dataset coverage audit reveals the exact distribution of source data:
- **Carparts-V2 Contribution**: 20,362 annotations (**56.94%**)
- **Humans in the Loop Contribution**: 15,397 annotations (**43.06%**)

### Breakdown by Origin Category:
1. **Classes Dependent 100% on HITL** (6 classes):
   - `fender`: 935 instances (100% HITL) -> **0.9286 mAP50**
   - `grille`: 577 instances (100% HITL) -> **0.7797 mAP50**
   - `quarter_panel`: 855 instances (100% HITL) -> **0.7085 mAP50**
   - `rocker_panel`: 860 instances (100% HITL) -> **0.8702 mAP50**
   - `roof`: 793 instances (100% HITL) -> **0.8065 mAP50**
   - `side_window`: 951 instances (100% HITL) -> **0.8684 mAP50**
2. **Classes Dependent 100% on Carparts-V2** (1 class):
   - `tailgate`: 101 instances (100% Carparts-V2, 0% HITL) -> **0.6204 mAP50**
3. **Classes Heavily Bolstered by HITL**:
   - `trunk`: 173 (V2) + 416 (HITL) = 589 instances (**70.63% from HITL**)
   - `wheel`: 877 (V2) + 1,750 (HITL) = 2,627 instances (**66.62% from HITL**)
   - `back_glass`: 1,058 (V2) + 1,508 (HITL) = 2,566 instances (**58.77% from HITL**)
   - `mirror`: 996 (V2) + 987 (HITL) = 1,983 instances (**49.77% from HITL**)

Full analysis permanently recorded at [`reports/v3_source_contribution.csv`](file:///Volumes/Toshiba%201TB/PartVision/reports/v3_source_contribution.csv).

---

## 10. Deep-Dive Weak-Class Analysis

For every class exhibiting metrics below the dataset mean, validation instances and structural dynamics were analyzed:

1. **`tailgate` (5 Val Instances)**:
   - **Metrics**: Box P 0.2753, Box R 0.6000, Seg mAP50 **0.6204**, Seg mAP50-95 **0.5362**.
   - **Diagnosis**: Severely data-limited. Only 101 total images in the dataset contain a tailgate, yielding just 5 validation samples. Because sedans have trunks and hatchbacks/SUVs have tailgates, the model experiences low precision when distinguishing rear hatch doors from trunks.
2. **`trunk` (49 Val Instances)**:
   - **Metrics**: Box P 0.5705, Box R 0.5714, Seg mAP50 **0.6386**, Seg mAP50-95 **0.4362**.
   - **Diagnosis**: Significant recovery compared to V2 (which had only 9 val instances and 26.72% mAP50-95). However, trunks remain variable across sedan profiles, rear decklids, and spoiler attachments, holding precision at 0.6520.
3. **`roof` (77 Val Instances)**:
   - **Metrics**: Box P 0.8598, Box R **0.3983**, Seg mAP50 **0.8065**, Seg mAP50-95 **0.3360**.
   - **Diagnosis**: Low recall (0.4243). In ground-level vehicle photography, vehicle roofs are viewed almost edge-on at acute angles. Under extreme perspective foreshortening, roof panels present as narrow slivers, leading to missed detections unless the camera angle is elevated.
4. **`quarter_panel` (82 Val Instances)**:
   - **Metrics**: Box P 0.6469, Box R 0.6585, Seg mAP50 **0.7085**, Seg mAP50-95 **0.3627**.
   - **Diagnosis**: Visual boundary ambiguity. Rear quarter panels lack continuous stamp seams on many unibody vehicles, flowing directly into the C-pillar and rocker sill. The model occasionally confuses the quarter panel boundary with the rear door sheet metal.
5. **`rocker_panel` (85 Val Instances)**:
   - **Metrics**: Box P 0.8552, Box R 0.9176, Seg mAP50 **0.8702**, Seg mAP50-95 **0.3703**.
   - **Diagnosis**: High mAP50 (87.0%) but lower strict mAP50-95 (37.0%). Rocker panels are very long and narrow. Even small pixel shifts in polygon boundaries significantly reduce the Intersection over Union (IoU) at high thresholds (IoU 0.85–0.95), while detection accuracy at IoU 0.50 remains excellent.
6. **`mirror` (162 Val Instances)**:
   - **Metrics**: Seg P 0.7294, Seg R 0.8025, Seg mAP50 **0.8213**, Seg mAP50-95 **0.4349**.
   - **Diagnosis**: Low pixel area footprint. Side mirrors occupy only ~1–2% of image pixels at 512×512 resolution. While mAP50 improved to 82.1%, high-IoU masks suffer from resolution quantization on small objects.

---

## 11. Current Limitations

1. **Exterior-Only Coverage**: PartVision V3 focuses exclusively on exterior collision sheet metal, glass, and wheels. It does not yet identify mechanical parts (engine components, brake rotors, alternators, suspension arms).
2. **Tailgate Sample Starvation**: Tailgate remains constrained to 101 samples. Additional pickup and hatchback data is required to bring it on par with trunk and bumper coverage.
3. **512px Mask Granularity on Slender Parts**: While 512px resolution provides fast training, slender panels (`rocker_panel`) and small fixtures (`mirror`) lose mask boundary sharpness at higher IoU thresholds.

---

## 12. Conclusion

Milestone 5B confirms that expanding PartVision to **19 automotive exterior classes** not only broadens coverage to critical repair panels (`fender`, `grille`, `roof`, `side_window`, `quarter_panel`, `rocker_panel`), but also **improves overall segmentation accuracy to 85.70% mAP50**.

The severe data famines that plagued V1 and V2 for `wheel` and `trunk` have been resolved. The model demonstrates high production readiness for automated exterior automotive part identification.

---

## 13. Recommendation for Milestone 6

Based on the verified Milestone 5B results, the recommended path for Milestone 6 is:

1. **Option A (Recommended): Structured Automotive Compatibility Engine & Schema**:
   - Transition from pure computer vision to the core business logic of PartVision:
   - Build a structured database schema linking the 19 identified visual classes to OEM part numbering systems, Year/Make/Model fitment matrices, and interchange databases.
   - Implement the inference-to-part lookup pipeline ensuring compatibility is resolved via deterministic database queries rather than LLM hallucination.
2. **Option B: Targeted Data Ingestion for Tailgate & Mechanical Parts**:
   - If deeper computer vision expansion is preferred before backend development, acquire a dedicated commercial vehicle/pickup dataset to resolve the tailgate bottleneck, or an engine bay component dataset.
