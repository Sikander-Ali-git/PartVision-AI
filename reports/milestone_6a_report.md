# PartVision AI — Milestone 6A Final Engineering Report
## Production-Oriented Python Inference Engine

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 6A — Production Inference Engine  
**Date**: October 6, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  

---

## 1. Objective

The objective of Milestone 6A is to construct a modular, production-ready Python inference engine wrapping the frozen **PartVision V3 YOLO11n-seg** model. This inference engine forms the foundational computer-vision abstraction layer that will be consumed by future backend services (such as FastAPI).

### Architectural Boundaries Enforced:
- **Model Frozen**: `models/partvision_v3_yolo11n_seg_best.pt` remains 100% frozen. No retraining or fine-tuning occurred.
- **Datasets Untouched**: V1, V2, and V3 datasets remained strictly unmodified.
- **Scope Isolation**: No FastAPI server, React frontend, or database models were constructed in this milestone.

---

## 2. Frozen Model Specifications

The engine binds exclusively to the best trained checkpoint from Milestone 5B:
- **Checkpoint Location**: `models/partvision_v3_yolo11n_seg_best.pt`
- **Architecture**: `YOLO11n-seg` (instance segmentation)
- **Parameters**: 2,846,313
- **File Size**: 5.71 MB
- **Taxonomy**: 19 frozen exterior-part classes:
  `0: back_bumper`, `1: back_door`, `2: back_glass`, `3: back_light`, `4: fender`, `5: front_bumper`, `6: front_door`, `7: front_glass`, `8: front_light`, `9: grille`, `10: hood`, `11: mirror`, `12: quarter_panel`, `13: rocker_panel`, `14: roof`, `15: side_window`, `16: tailgate`, `17: trunk`, `18: wheel`.

---

## 3. Inference Architecture

The inference system is encapsulated inside `src/inference/`:

```
src/
├── __init__.py
└── inference/
    ├── __init__.py      # Public API exports
    ├── engine.py        # PartVisionInferenceEngine core class
    ├── schemas.py       # Typed Pydantic V2 output schemas
    ├── utils.py         # Device selection, image loading, coordinate sanitization
    └── visualize.py     # Clean overlay rendering (polygons, boxes, banners)
```

### Core Design Principles:
1. **Load Once, Predict Many**: The model checkpoint is loaded during engine instantiation (`__init__`) and held in memory. Predictions do not incur redundant disk I/O.
2. **Strict Validation**: The engine validates file paths for both weights and input images, raising clear `FileNotFoundError` exceptions upon failure.
3. **No In-Place Mutation**: Input image arrays are never modified in-place during inference or visualization.
4. **Deterministic Ordering**: Detections are sorted strictly descending by confidence score.
5. **Instance Preservation**: Multiple detected instances of the same class (e.g. 4 wheels) are preserved as distinct physical entities rather than merged.

---

## 4. Output Schemas

All outputs are validated against strict Pydantic V2 schemas defined in [`src/inference/schemas.py`](file:///Volumes/Toshiba%201TB/PartVision/src/inference/schemas.py). All coordinate values are mapped into **original image pixel space** (`[0, width]` and `[0, height]`):

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

## 5. Device Handling & Fallback

The compute device is never hardcoded. Device resolution is managed by `select_optimal_device()` in [`src/inference/utils.py`](file:///Volumes/Toshiba%201TB/PartVision/src/inference/utils.py):

1. **`mps`**: Apple Silicon GPU acceleration via Metal Performance Shaders (active on this Apple M3 machine).
2. **`cuda`**: NVIDIA GPU acceleration if available.
3. **`cpu`**: Portable fallback across any hardware environment.

The active device is explicitly recorded in `result.inference.device`.

---

## 6. Mask Representation

To maintain lightweight, API-friendly responses, raw binary tensor masks are discarded. Instead, masks are converted into **ordered 2D polygon vertex sequences**:
- `points`: List of `[x, y]` pixel coordinates.
- All vertices are strictly clamped to image boundaries `[0, width]` and `[0, height]` and rounded to 2 decimal places.
- Degenerate masks with fewer than 3 vertices are filtered out.

---

## 7. Command-Line Interface (CLI)

The CLI tool [`scripts/predict.py`](file:///Volumes/Toshiba%201TB/PartVision/scripts/predict.py) provides single-command terminal execution:

```bash
python scripts/predict.py --source data/processed/partvision-v3/images/test/hitl_Car_damages_1033.png
```

### Verified Terminal Output:
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
14. back_glass — 71.2%
15. back_door — 69.9%
16. roof — 48.6%
17. quarter_panel — 43.1%
18. roof — 34.2%

Total detections: 18
JSON saved:      reports/inference/hitl_Car_damages_1033_result.json
Annotated image: reports/inference/hitl_Car_damages_1033_annotated.jpg
```

---

## 8. Automated Test Suite Results

A comprehensive test suite was implemented across [`tests/test_inference.py`](file:///Volumes/Toshiba%201TB/PartVision/tests/test_inference.py) and [`tests/test_schemas.py`](file:///Volumes/Toshiba%201TB/PartVision/tests/test_schemas.py). All **17 tests passed with 100% pass rate**:

| Test Name | Test Suite | Result | Verified Capability |
|---|---|:---:|---|
| `test_invalid_model_path_raises` | `test_inference.py` | **PASSED** | Missing weights file raises `FileNotFoundError` |
| `test_invalid_image_path_raises` | `test_inference.py` | **PASSED** | Missing input image raises `FileNotFoundError` |
| `test_engine_initialization_metadata` | `test_inference.py` | **PASSED** | Correct 19-class taxonomy and load duration |
| `test_real_image_inference` | `test_inference.py` | **PASSED** | End-to-end inference on unseen V3 test image |
| `test_confidence_sorting` | `test_inference.py` | **PASSED** | Detections strictly ordered descending by score |
| `test_class_names_and_taxonomy_validity` | `test_inference.py` | **PASSED** | Class IDs map strictly to the 19 frozen classes |
| `test_bbox_and_mask_coordinate_boundaries` | `test_inference.py` | **PASSED** | All coordinates stay within image pixel bounds |
| `test_zero_detections_handling` | `test_inference.py` | **PASSED** | Graceful empty result when cutoff is 0.9999 |
| `test_blank_synthetic_image_handling` | `test_inference.py` | **PASSED** | Graceful handling on black/blank image arrays |
| `test_multiple_instances_not_merged` | `test_inference.py` | **PASSED** | Multiple wheels retain separate bounding boxes |
| `test_predict_and_visualize_no_mutation` | `test_inference.py` | **PASSED** | Original image array buffer is never mutated |
| `test_bbox_properties_and_validation` | `test_schemas.py` | **PASSED** | BBox width, height, area, and coordinates |
| `test_bbox_extra_fields_forbidden` | `test_schemas.py` | **PASSED** | Strict extra field rejection (`extra="forbid"`) |
| `test_polygon_mask_properties` | `test_schemas.py` | **PASSED** | Mask format and vertex count validation |
| `test_detection_confidence_rounding` | `test_schemas.py` | **PASSED** | Confidence values rounded to 4 decimals, [0, 1] range |
| `test_inference_result_serialization` | `test_schemas.py` | **PASSED** | Full dictionary and JSON roundtrip integrity |
| `test_get_detections_by_class` | `test_schemas.py` | **PASSED** | Class filtering helper returns correct instances |

**Summary**: `17 passed in 32.68s`.

---

## 9. Real Image Validation & Performance Measurement

### Measurement Context:
- **Benchmark Label**: **"Local M3 smoke-test performance"**
- **Hardware**: Apple Silicon M3 (MacBook Air, unified memory)
- **Active Device**: `mps` (Metal Performance Shaders)
- **Test Set**: 7 real, unseen test images from `data/processed/partvision-v3/images/test/`

### Performance Metrics:
| Metric | Measurement Value |
|---|---|
| **Model Loading Time** | **46.24 ms** (0.046 seconds) |
| **Minimum Inference Latency** | **181.54 ms** (5.5 FPS) |
| **Maximum Inference Latency** | **800.29 ms** (dense 23-instance image) |
| **Average Inference Latency** | **567.39 ms** (includes decoding, NMS, polygon extraction & visualization) |
| **Estimated Throughput** | **~1.8 FPS** |

*All 7 evaluated image outputs (JSON and annotated images) are archived in [`reports/inference/smoke_test/`](file:///Volumes/Toshiba%201TB/PartVision/reports/inference/smoke_test/). Performance summary saved to [`reports/inference_performance.json`](file:///Volumes/Toshiba%201TB/PartVision/reports/inference_performance.json).*

---

## 10. Limitations

1. **Sequential Single-Image Execution**: The engine operates on single images. Batch inference across large lists of images in a single call will be implemented if required in future milestones.
2. **Polygonal Mask Simplification**: Masks are represented as simple polygons. Complex multi-part objects with internal negative space (holes) are represented by their primary exterior perimeter.
3. **Latency Scaling with Part Density**: On scenes with 20+ overlapping parts, OpenCV polygon contour extraction and rendering adds ~300ms compared to sparse scenes (181ms).

---

## 11. Files Created & Modified

### Source Code:
- [`src/__init__.py`](file:///Volumes/Toshiba%201TB/PartVision/src/__init__.py)
- [`src/inference/__init__.py`](file:///Volumes/Toshiba%201TB/PartVision/src/inference/__init__.py)
- [`src/inference/engine.py`](file:///Volumes/Toshiba%201TB/PartVision/src/inference/engine.py)
- [`src/inference/schemas.py`](file:///Volumes/Toshiba%201TB/PartVision/src/inference/schemas.py)
- [`src/inference/utils.py`](file:///Volumes/Toshiba%201TB/PartVision/src/inference/utils.py)
- [`src/inference/visualize.py`](file:///Volumes/Toshiba%201TB/PartVision/src/inference/visualize.py)

### CLI & Benchmark Scripts:
- [`scripts/predict.py`](file:///Volumes/Toshiba%201TB/PartVision/scripts/predict.py)
- [`scripts/benchmark_inference.py`](file:///Volumes/Toshiba%201TB/PartVision/scripts/benchmark_inference.py)

### Test Suite & Configuration:
- [`tests/test_schemas.py`](file:///Volumes/Toshiba%201TB/PartVision/tests/test_schemas.py)
- [`tests/test_inference.py`](file:///Volumes/Toshiba%201TB/PartVision/tests/test_inference.py)
- [`pytest.ini`](file:///Volumes/Toshiba%201TB/PartVision/pytest.ini)

### Documentation & Reports:
- [`docs/inference_engine.md`](file:///Volumes/Toshiba%201TB/PartVision/docs/inference_engine.md)
- [`reports/milestone_6a_report.md`](file:///Volumes/Toshiba%201TB/PartVision/reports/milestone_6a_report.md)
- [`reports/inference_performance.json`](file:///Volumes/Toshiba%201TB/PartVision/reports/inference_performance.json)

### Modified:
- [`requirements.txt`](file:///Volumes/Toshiba%201TB/PartVision/requirements.txt) (added `pydantic>=2.0.0` and `pytest>=8.0.0`)

---

## 12. Conclusion & Verification

The PartVision V3 model is now cleanly packaged as a production-grade, typed Python library. It decouples the underlying deep learning framework (Ultralytics/PyTorch) from API consumers, returning standardized JSON dictionaries ready for FastAPI integration.

**Milestone 6A is complete.** No frontend, server, or database work was started.
