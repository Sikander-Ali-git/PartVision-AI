# PartVision AI

**Automotive Spare-Part Identification and Compatibility System**

PartVision AI is a computer-vision system designed to identify automotive spare parts directly from vehicle images using instance segmentation. The goal of the AI model is to detect and delineate visually recognizable automotive components, while downstream part compatibility, OEM cross-referencing, and interchange information are resolved through a deterministic structured database rather than being hallucinated by the model.

---

## Milestone 1: Computer-Vision Baseline

Milestone 1 establishes a clean, reproducible computer-vision baseline using the official Ultralytics **Carparts-Seg** dataset and **YOLO11n-seg**.

### Key Milestone 1 Results (Validation Set)

| Task | Precision | Recall | mAP50 | mAP50-95 |
| :--- | :--- | :--- | :--- | :--- |
| **Detection (Box)** | **0.6536** (65.36%) | **0.4876** (48.76%) | **0.4803** (48.03%) | **0.3721** (37.21%) |
| **Segmentation (Mask)** | **0.6663** (66.63%) | **0.4938** (49.38%) | **0.4935** (49.35%) | **0.3581** (35.81%) |

Top performing classes:
- `front_glass`: Mask mAP50 = 0.9456, mAP50-95 = 0.8470
- `front_bumper`: Mask mAP50 = 0.9405, mAP50-95 = 0.7524
- `hood`: Mask mAP50 = 0.9247, mAP50-95 = 0.7582
- `back_bumper`: Mask mAP50 = 0.8448, mAP50-95 = 0.5280
- `front_light`: Mask mAP50 = 0.7847, mAP50-95 = 0.5374

---

## Environment & Hardware

The baseline was developed and trained on Apple Silicon:
- **Processor**: Apple Silicon M3 (ARM64)
- **OS**: macOS
- **Python**: 3.13.2
- **PyTorch**: 2.14.1 (with Apple Silicon Metal Performance Shaders - MPS enabled)
- **Torchvision**: 0.29.1
- **Ultralytics**: 8.4.171
- **OpenCV**: 5.0.0

---

## Dataset

- **Source**: Official Ultralytics Carparts-Seg release ([Download URL](https://github.com/ultralytics/assets/releases/download/v0.0.0/carparts-seg.zip))
- **Archive Size**: 139,535,504 bytes (133.07 MB)
- **SHA256 Checksum**: `e2eea20030d02366b07174bcdbcc843f63791bdd53962a83e00636d15e78e41f`
- **Total Images**: 3,833 images (all normalized 640x640 resolution)
- **Total Annotations**: 20,374 instance polygon annotations across 23 classes
- **Splits**:
  - `train`: 3,156 images (16,733 annotations)
  - `val`: 401 images (2,042 annotations)
  - `test`: 276 images (1,599 annotations)
- **Taxonomy (23 classes)**:
  `back_bumper`, `back_door`, `back_glass`, `back_left_door`, `back_left_light`, `back_light`, `back_right_door`, `back_right_light`, `front_bumper`, `front_door`, `front_glass`, `front_left_door`, `front_left_light`, `front_light`, `front_right_door`, `front_right_light`, `hood`, `left_mirror`, `object`, `right_mirror`, `tailgate`, `trunk`, `wheel`.

---

## Project Structure

```
PartVision/
├── data/
│   ├── raw/                  # Downloaded raw zip archives
│   ├── processed/            # Extracted Carparts-Seg dataset
│   └── dataset.yaml          # Local YOLO dataset specification
├── models/                   # Model checkpoints (pretrained & best trained)
├── notebooks/                # Exploratory notebooks
├── reports/                  # Validation logs, metrics, CSVs, and plots
│   ├── class_distribution.csv
│   ├── class_distribution.png
│   ├── dataset_sample_grid.png
│   ├── dataset_validation.txt
│   ├── baseline_metrics.txt
│   ├── baseline_metrics.json
│   ├── milestone_1_report.md
│   └── test_predictions/
├── scripts/
│   ├── download_dataset.py   # Dataset download & SHA256 checksum verification
│   ├── validate_dataset.py   # Dataset validation and class distribution analysis
│   ├── visualize_dataset.py  # Ground-truth segmentation grid visualizer
│   ├── train_baseline.py     # YOLO11n-seg baseline training & evaluation
│   └── predict_test.py       # Inference on unseen test set images
├── runs/
│   └── partvision_v1/        # Ultralytics training outputs and checkpoint weights
├── backend/                  # Future backend API services
├── frontend/                 # Future frontend application
├── database/                 # Future compatibility database schema & migrations
├── requirements.txt
├── README.md
└── .gitignore
```

---

## How to Reproduce the Baseline

### 1. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Download and Extract Dataset
```bash
python scripts/download_dataset.py
```

### 3. Validate Dataset Integrity
```bash
python scripts/validate_dataset.py
```

### 4. Visualize Ground Truth Annotations
```bash
python scripts/visualize_dataset.py
```

### 5. Train Baseline Model (YOLO11n-seg)
```bash
python scripts/train_baseline.py
```
This trains for 3 epochs with batch size 16 at 640x640 using MPS acceleration and generates `reports/baseline_metrics.txt` and `reports/baseline_metrics.json`.

### 6. Run Test Predictions
```bash
python scripts/predict_test.py
```
This executes inference with confidence threshold 0.25 on unseen test set images, saving annotated outputs and `reports/test_predictions/test_prediction_grid.png`.

---

## Known Limitations

1. **Exterior Body Parts Only**: Carparts-Seg exclusively covers exterior body parts (bumpers, doors, glass, lights, hood, mirrors, wheels). It does **not** contain mechanical, under-the-hood, electrical, drivetrain, or interior parts (such as alternators, brake calipers, spark plugs, radiators, steering wheels).
2. **Class Imbalance**: High-frequency parts (`front_light`: 3,088 annotations, `hood`: 2,080 annotations) perform strongly (~0.92–0.94 mAP50), whereas scarce classes (`object`: 12 annotations, `tailgate`: 101 annotations) achieve significantly lower recall.
3. **Left/Right Ambiguity**: The dataset contains redundant / ambiguous categories (e.g. `back_door` vs `back_left_door` / `back_right_door`; `front_light` vs `front_left_light` / `front_right_light`), which split the model's prediction probability across classes for the same object.
4. **Baseline Epoch Count**: 3 epochs provides a fast baseline to verify the pipeline and prove end-to-end viability, but does not represent maximum model convergence.
5. **No Production Compatibility Guarantee**: The model output is strictly visual part segmentation. Part fitment, OEM cross-compatibility, and vehicle trim compatibility require deterministic database matching scheduled for future milestones.
