# PartVision AI — Milestone 7 Final Engineering Report
## FastAPI Backend Integration

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 7 — FastAPI Backend Integration  
**Date**: October 6, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  
**API Version**: `0.4.0`  

---

## 1. Objective

The objective of Milestone 7 is to construct the central REST API backend connecting the frozen **PartVision V3 YOLO11n-seg** inference engine (`src/inference/`) with the **SQLite compatibility database** (`src/database/` + `data/partvision.db`).

### Key Deliverables Completed:
- Built a modular FastAPI application using lifespan resource management and typed Pydantic V2 schemas.
- Implemented the end-to-end image analysis endpoint (`POST /api/analyze`) resolving visual part detections to vehicle compatibility records.
- Built catalog browsing endpoints for parts (`/api/parts`), vehicles (`/api/vehicles`), and direct compatibility queries (`/api/compatibility`).
- Maintained the architectural rule: **YOLO identifies the visual part; SQLite determines vehicular compatibility**. No generative AI or LLMs are involved in fitment determinations.
- Created server execution script (`scripts/run_server.py`) and live demo script (`scripts/demo_api.py`).
- Implemented comprehensive automated test suite (`tests/test_api.py`) passing all 20 test cases with zero regressions across the codebase.

---

## 2. Architecture

```
                    ┌───────────────────────────────────────────────┐
                    │               Client Application              │
                    └───────────────────────┬───────────────────────┘
                                            │ HTTP / Multipart Upload
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │             FastAPI Application               │
                    │                  (0.4.0)                      │
                    │  • CORS Middleware (localhost:5173 / 3000)    │
                    │  • Upload Validation & OpenCV Image Decode    │
                    │  • Unified JSON Error Handling                │
                    └───────────────┬───────────────────────────────┘
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
┌──────────────────────────────┐          ┌──────────────────────────────┐
│  PartVisionInferenceEngine   │          │     PartVisionRepository     │
│       (src/inference/)       │          │       (src/database/)        │
│  • Frozen YOLO11n-seg Model  │          │  • SQLite Connection (WAL)   │
│  • Loaded ONCE in Lifespan   │          │  • 19 Canonical Classes      │
│  • Segmentation & BBoxes     │          │  • 86 Search Aliases         │
│  • Device: Apple Silicon MPS │          │  • 8 Seed Vehicles           │
│  • Zero LLM Hallucination    │          │  • 51 Fitment Records        │
└──────────────┬───────────────┘          └──────────────┬───────────────┘
               │                                         │
               │ Canonical Part Names                    │ Vehicle Fitment Records
               └────────────────────┬────────────────────┘
                                    ▼
                    ┌───────────────────────────────────────────────┐
                    │          AnalysisResponse JSON Payload        │
                    │  • UUID Request ID                            │
                    │  • Detections + Polygons + Confidence         │
                    │  • Verified vs Unverified Compatible Cars     │
                    │  • Latency & Hardware Metrics                 │
                    └───────────────────────────────────────────────┘
```

---

## 3. Endpoints Implemented

| Endpoint | Method | Purpose | Request Body / Params | Response Schema |
| :--- | :---: | :--- | :--- | :--- |
| `/health` | `GET` | Health check & readiness | None | `HealthResponse` |
| `/api/analyze` | `POST` | Vision detection & fitment lookup | `multipart/form-data` (`file`) | `AnalysisResponse` |
| `/api/parts` | `GET` | Canonical parts taxonomy | `?category=...`, `?search=...` | `List[PartSummary]` |
| `/api/parts/{part_name}` | `GET` | Part details & aliases | `part_name` path param | `PartDetailResponse` |
| `/api/vehicles` | `GET` | Vehicle catalog | `?make=...`, `?model=...` | `List[VehicleSummary]` |
| `/api/vehicles/{vehicle_id}` | `GET` | Vehicle details & parts list | `vehicle_id` path param | `VehicleDetailResponse` |
| `/api/compatibility/{part_name}` | `GET` | Direct compatibility lookup | `?verified_only=true/false` | `CompatibilityQueryResponse` |
| `/docs` | `GET` | Interactive Swagger UI | None | HTML |
| `/redoc` | `GET` | ReDoc API specification | None | HTML |

---

## 4. Inference Engine Integration

- **Lifespan Startup**: The inference engine is initialized during application startup in `src/api/app.py`:
  ```python
  engine = PartVisionInferenceEngine(
      model_path="models/partvision_v3_yolo11n_seg_best.pt",
      device="auto",
  )
  app.state.inference_engine = engine
  ```
- **Single-Load Guarantee**: The model checkpoint (2.85M parameters, 5.71 MB) is loaded into memory exactly once and reused for all subsequent requests.
- **Compute Device**: Automatically resolved to Apple Silicon `mps` GPU acceleration.
- **Output Preservation**: Full bounding box coordinates and 2D polygon segmentation vertices are mapped directly to pixel space and serialized into the API response.

---

## 5. Database Integration

- **Authoritative Data Layer**: Connected to `data/partvision.db` via `PartVisionRepository`.
- **Database Verified on Startup**: Lifespan handler confirms connectivity and checks all 19 canonical taxonomy entries prior to accepting traffic.
- **Dependency Injection**: Route handlers obtain the repository instance cleanly via `Depends(get_repository)`.
- **Segregated Fitment**: In accordance with automotive trust requirements, compatibility records returned for detected parts are cleanly split into:
  - `verified_vehicles` (`verified = 1`, cross-referenced against manufacturer OEM catalogs)
  - `unverified_vehicles` (`verified = 0`, demonstration / aftermarket items)

---

## 6. Security & Hardening Controls

1. **Strict File Upload Validation**:
   - Supported extensions enforced: `.jpg`, `.jpeg`, `.png`, `.webp`.
   - MIME header validation against allowed image types.
   - Decodes bytes with OpenCV (`cv2.imdecode`) to reject corrupted files or disguised scripts.
2. **Payload Size Guardrails**: Maximum upload size capped at 20 MB (`HTTP 413 Content Too Large`).
3. **Guaranteed Temp File Cleanup**: Temporary files created for YOLO inference are immediately removed in a `finally` block.
4. **SQL Injection Prevention**: All queries utilize parameterized SQLite bindings.
5. **Information Leakage Prevention**: Custom exception handlers sanitize stack traces and expose only structured error payloads (`ErrorResponse`).
6. **CORS Whitelisting**: Restricted to local frontend origins (`http://localhost:5173`, `http://localhost:3000`).

---

## 7. Test Results & Verification

The automated test suite in [`tests/test_api.py`](file:///Volumes/Toshiba%201TB/PartVision/tests/test_api.py) validates all 20 required scenarios using FastAPI's `TestClient`:

```
tests/test_api.py::test_app_starts_and_health PASSED
tests/test_api.py::test_swagger_and_redoc_documentation PASSED
tests/test_api.py::test_get_all_parts PASSED
tests/test_api.py::test_parts_category_and_search_filtering PASSED
tests/test_api.py::test_get_part_detail PASSED
tests/test_api.py::test_invalid_part_returns_404 PASSED
tests/test_api.py::test_get_all_vehicles PASSED
tests/test_api.py::test_vehicle_filtering PASSED
tests/test_api.py::test_vehicle_detail PASSED
tests/test_api.py::test_invalid_vehicle_returns_404 PASSED
tests/test_api.py::test_compatibility_lookup PASSED
tests/test_api.py::test_compatibility_verified_only PASSED
tests/test_api.py::test_invalid_compatibility_part_returns_404 PASSED
tests/test_api.py::test_analyze_unsupported_file_extension PASSED
tests/test_api.py::test_analyze_unsupported_image_type PASSED
tests/test_api.py::test_analyze_empty_upload PASSED
tests/test_api.py::test_analyze_corrupt_image_bytes PASSED
tests/test_api.py::test_analyze_real_image_end_to_end PASSED
tests/test_api.py::test_analyze_request_id_uniqueness PASSED
tests/test_api.py::test_analyze_temporary_upload_is_cleaned_up PASSED
```

### Full Project Regression Audit:
```
============================= test session starts ==============================
collected 82 items

tests/test_api.py ....................                                   [ 24%]
tests/test_database.py .............................................    [ 79%]
tests/test_inference.py ...........                                     [ 92%]
tests/test_schemas.py ......                                            [100%]

============================= 82 passed in 11.38s ==============================
```
- **Milestone 6A Tests**: 17 / 17 passed
- **Milestone 6B Tests**: 45 / 45 passed
- **Milestone 7 Tests**: 20 / 20 passed
- **Total Regressions**: **0**

---

## 8. Performance Benchmark

Performance benchmark executed on Apple Silicon M3 (`scripts/benchmark_api.py`):

| Metric | Measured Value | Description |
| :--- | :---: | :--- |
| **Application Startup Time** | **68.17 ms** | Total lifespan initialization |
| **Model Initialization Time** | **48.74 ms** | Checkpoint load and tensor allocation |
| **Model Inference Latency (Min)** | **38.01 ms** | Raw YOLO11n-seg pass on MPS |
| **Model Inference Latency (Avg)** | **41.17 ms** | Average across 5 benchmarked requests |
| **Model Inference Latency (Max)** | **44.21 ms** | Peak inference duration |
| **Full API Latency (Min)** | **136.20 ms** | HTTP receive + decode + YOLO + 18 DB lookups + JSON |
| **Full API Latency (Avg)** | **143.84 ms** | End-to-end user request latency |
| **Full API Latency (Max)** | **156.01 ms** | Peak end-to-end duration |

> **Latency Distinction**: Model inference (~41 ms) represents only the neural network compute. Full API latency (~144 ms) accounts for multipart upload decoding, image resizing/rescaling, database lookups for all detected instances, and Pydantic validation.

---

## 9. End-to-End Demonstration

Executing [`scripts/demo_api.py`](file:///Volumes/Toshiba%201TB/PartVision/scripts/demo_api.py) with test image `hitl_Car_damages_1033.png`:

```
======================================================================
 PartVision AI API — End-to-End Analysis Demonstration
======================================================================
Image: hitl_Car_damages_1033.png (699x527 px)
Request ID: c36fac31-2ba6-46ae-9195-c63c299d150d
Compute Device: mps
Model Latency:  41.20 ms
Total API Time: 143.80 ms
----------------------------------------------------------------------

Detected 18 automotive parts:
  • Wheel              —  95.4% conf | BBox: [49, 161, 94, 250]
  • Wheel              —  93.8% conf | BBox: [175, 268, 274, 452]
  • Front Glass        —  93.5% conf | BBox: [167, 21, 472, 132]
  • Front Light        —  93.4% conf | BBox: [285, 225, 503, 339]
  • Hood               —  93.2% conf | BBox: [156, 119, 662, 267]
  • Fender             —  92.9% conf | BBox: [151, 167, 315, 315]
  • Grille             —  92.2% conf | BBox: [522, 242, 669, 438]
  • Mirror             —  88.7% conf | BBox: [87, 86, 152, 145]
  • Front Door         —  88.7% conf | BBox: [73, 18, 174, 292]
  • Front Bumper       —  86.1% conf | BBox: [238, 275, 673, 480]
  • Rocker Panel       —  81.7% conf | BBox: [76, 210, 177, 330]
  • Side Window        —  76.5% conf | BBox: [98, 24, 169, 117]
  • Quarter Panel      —  71.5% conf | BBox: [43, 89, 83, 211]
  • Back Glass         —  71.2% conf | BBox: [73, 28, 110, 90]
  • Back Door          —  69.9% conf | BBox: [53, 21, 113, 226]
  • Roof               —  48.6% conf | BBox: [142, 6, 329, 24]
  • Quarter Panel      —  43.1% conf | BBox: [43, 92, 73, 187]
  • Roof               —  34.2% conf | BBox: [132, 6, 356, 29]

Compatibility Highlights:
  ► Part: Wheel (wheel)
    Verified OEM Matches:   6
    Example: Honda City (5th Gen) [2020–Present]: compatible
  ► Part: Front Bumper (front_bumper)
    Verified OEM Matches:   8
    Example: Maruti Suzuki Swift (3rd Gen) [2018–2024]: compatible
```

---

## 10. Limitations

1. **Local Authentication**: No OAuth2 / JWT authentication is enforced; suitable for development and trusted private networks.
2. **Synchronous Request Processing**: Image analysis runs synchronously within the request-response lifecycle. For large multi-worker production scale, a background task queue (e.g. Celery / Redis) could be adopted.
3. **Database Scope**: Compatibility records are representative baseline entries (8 vehicles, 51 records); production deployment will scale this catalog.

---

## 11. Conclusion & Readiness

Milestone 7 successfully unifies computer-vision inference and relational compatibility into a robust, high-performance REST API service:
- Model frozen and untouched.
- Datasets untouched.
- Zero regressions across 82 automated tests.
- Sub-150ms total API response time on Apple Silicon M3.

The backend is fully operational and ready for **Milestone 8: React Frontend Integration**.
