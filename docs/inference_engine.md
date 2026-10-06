# PartVision AI — Production Inference Engine Developer Guide

## Overview

The `src/inference` module provides a production-grade, typed Python interface to the frozen **PartVision V3 YOLO11n-seg** model. Designed as the core computer-vision service for future backend integration (e.g., FastAPI), the engine encapsulates model loading, device selection, bounding box extraction, polygon mask extraction, and output normalization into deterministic Pydantic schemas.

---

## Architecture

```
[Input: Image Path / NumPy Array]
              │
              ▼
   ┌──────────────────────────────────────────────┐
   │         PartVisionInferenceEngine            │
   │  • Loads YOLO11n-seg checkpoint ONCE         │
   │  • Resolves optimal compute device (MPS/CUDA)│
   │  • Applies Ultralytics pre-processing        │
   └──────────────────────────────────────────────┘
              │
              ▼
      [Inference Pass]
  (YOLO11n-seg Segmentation Head)
              │
              ▼
   ┌──────────────────────────────────────────────┐
   │          Extraction & Normalization          │
   │  • Bounding boxes -> [x1, y1, x2, y2]        │
   │  • Masks -> 2D polygon vertices [x, y]       │
   │  • Sorted descending by confidence           │
   │  • Preserves distinct physical instances     │
   └──────────────────────────────────────────────┘
              │
              ▼
   [Output: Typed InferenceResult (Pydantic)]
        ├── model: ModelMetadata
        ├── image: ImageMetadata
        ├── inference: InferenceConfig
        ├── detections: list[Detection]
        └── summary: InferenceSummary
```

---

## Quickstart

### 1. Basic Python Usage

```python
from pathlib import Path
from src.inference import PartVisionInferenceEngine

# 1. Initialize engine (model loaded once into memory)
engine = PartVisionInferenceEngine(
    model_path="models/partvision_v3_yolo11n_seg_best.pt",
    device="auto"  # 'auto', 'mps', 'cuda', or 'cpu'
)

# 2. Run inference on an image
result = engine.predict(
    image="data/processed/partvision-v3/images/test/hitl_Car_damages_1033.png",
    conf=0.25,     # Confidence cutoff threshold
    iou=0.7,       # NMS IoU threshold
    imgsz=512      # Square resolution
)

# 3. Access typed detection fields
print(f"Total parts detected: {result.summary.detection_count}")
for det in result.detections:
    print(f"- {det.class_name} ({det.confidence * 100:.1f}%)")
    print(f"  BBox: [{det.bbox.x1}, {det.bbox.y1}, {det.bbox.x2}, {det.bbox.y2}]")
    if det.mask:
        print(f"  Mask vertices count: {det.mask.point_count}")

# 4. Serialize to JSON for API response
json_output = result.to_json(indent=2)
```

### 2. Predict and Generate Visual Overlay

```python
from src.inference import PartVisionInferenceEngine

engine = PartVisionInferenceEngine()

# Predict and render overlay in a single pass
result, annotated_img = engine.predict_and_visualize(
    image="path/to/car.jpg",
    output_path="reports/inference/car_annotated.jpg",
    conf=0.25
)
```

---

## Command-Line Interface (CLI)

The CLI tool allows batch or single-image inference directly from the terminal:

```bash
# Minimal invocation
.venv/bin/python scripts/predict.py --source path/to/image.jpg

# Full parameter customization
.venv/bin/python scripts/predict.py \
    --source path/to/car.jpg \
    --model models/partvision_v3_yolo11n_seg_best.pt \
    --conf 0.25 \
    --iou 0.7 \
    --imgsz 512 \
    --output reports/inference/ \
    --device auto
```

### Sample CLI Output:
```text
PartVision AI
Model: PartVision YOLO11n-seg V3
Device: mps
Latency: 181.5 ms

Detected parts:
1. wheel — 95.4%
2. wheel — 93.8%
3. front_glass — 93.5%
4. front_light — 93.4%
5. hood — 93.2%
6. fender — 92.9%
7. grille — 92.2%
8. mirror — 88.7%
9. front_door — 88.7%
10. front_bumper — 86.1%
11. rocker_panel — 81.7%
12. side_window — 76.5%
13. quarter_panel — 71.5%

Total detections: 13
JSON saved:      reports/inference/car_result.json
Annotated image: reports/inference/car_annotated.jpg
```

---

## Output Schema Reference

All coordinate conventions use **original image pixel coordinates**:
- `(0, 0)` is the top-left pixel.
- Horizontal axes span `[0, image.width]`.
- Vertical axes span `[0, image.height]`.

### JSON Structure:
```json
{
  "model": {
    "name": "PartVision YOLO11n-seg",
    "version": "v3",
    "checkpoint": "partvision_v3_yolo11n_seg_best.pt",
    "num_classes": 19
  },
  "image": {
    "width": 699,
    "height": 527,
    "channels": 3,
    "filename": "hitl_Car_damages_1033.png"
  },
  "inference": {
    "device": "mps",
    "confidence_threshold": 0.25,
    "iou_threshold": 0.7,
    "image_size": 512
  },
  "detections": [
    {
      "class_id": 18,
      "class_name": "wheel",
      "confidence": 0.9536,
      "bbox": {
        "x1": 49.47,
        "y1": 161.24,
        "x2": 93.71,
        "y2": 249.86
      },
      "mask": {
        "format": "polygon",
        "points": [
          [51.2, 162.4],
          [92.1, 163.5],
          [93.7, 248.9],
          [50.1, 247.3]
        ]
      }
    }
  ],
  "summary": {
    "detection_count": 1,
    "detected_classes": [
      "wheel"
    ]
  },
  "latency_ms": 181.54
}
```

---

## Device Handling & Fallback

The engine automatically selects the fastest available compute device:

1. **`mps`**: Apple Silicon GPU (M-series processors via Metal Performance Shaders).
2. **`cuda`**: NVIDIA GPU via CUDA.
3. **`cpu`**: Universal fallback.

You can explicitly lock the device:
```python
engine = PartVisionInferenceEngine(device="cpu")
```

---

## Frozen 19-Class Taxonomy

| ID | Class Name | Description |
|---|---|---|
| **0** | `back_bumper` | Rear vehicle bumper assembly |
| **1** | `back_door` | Rear passenger side door |
| **2** | `back_glass` | Rear windshield and rear fixed glass |
| **3** | `back_light` | Tail light and rear brake light cluster |
| **4** | `fender` | Front quarter panel over front wheel arch |
| **5** | `front_bumper` | Front bumper fascia |
| **6** | `front_door` | Front passenger/driver door |
| **7** | `front_glass` | Front windshield glass |
| **8** | `front_light` | Headlight and front turn signal cluster |
| **9** | `grille` | Front radiator airflow grille |
| **10** | `hood` | Engine bonnet / hood cover |
| **11** | `mirror` | Side view mirror assembly |
| **12** | `quarter_panel` | Rear quarter panel over rear wheel arch |
| **13** | `rocker_panel` | Lower side sill between wheel arches |
| **14** | `roof` | Vehicle exterior roof sheet metal |
| **15** | `side_window` | Side passenger door window glass |
| **16** | `tailgate` | Rear hatch / liftgate on hatchbacks/SUVs |
| **17** | `trunk` | Rear decklid on sedans and coupes |
| **18** | `wheel` | Road wheel (rim and tire assembly) |

---

## Testing

Run the full automated test suite:

```bash
.venv/bin/pytest -v tests/
```

Test coverage includes:
- Non-existent model and image paths (validation and error handling).
- Metadata initialization.
- Coordinate boundaries for bounding boxes and polygon masks.
- Deterministic descending confidence sorting.
- Zero detections on blank images or ultra-high confidence thresholds.
- Instance segregation for multiple instances of identical classes (e.g. 4 wheels).
- Immutability of input image buffers during visualization.
