# PartVision AI — REST API Developer Documentation

## 1. Overview & Running the Server

The PartVision AI REST API provides a high-performance backend connecting the frozen **PartVision V3 YOLO11n-seg** computer-vision model with the **SQLite compatibility database**.

### Starting the Server

Launch the Uvicorn server using the standard CLI script:

```bash
# Standard launch (default: 127.0.0.1:8000)
python scripts/run_server.py

# Custom host and port
python scripts/run_server.py --host 0.0.0.0 --port 8000

# Development mode with hot-reloading
python scripts/run_server.py --reload
```

Interactive documentation is automatically generated and hosted:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 2. API Architecture & Pipeline

```
  ┌─────────────────────────────────────────────────────────────┐
  │                 Client HTTP Request                         │
  │      POST /api/analyze (multipart/form-data image)          │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                 FastAPI Validation Layer                    │
  │  • Size limit (20MB)    • Extension check (.jpg,.png,.webp) │
  │  • MIME validation      • OpenCV byte decode verification   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │            M6A Inference Engine (Singleton)                 │
  │  • Loaded once at startup into memory (MPS/CUDA/CPU)        │
  │  • YOLO11n-seg instance segmentation pass                   │
  │  • Bounding boxes, polygon masks, confidence scores         │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ (Canonical part taxonomy strings)
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │          M6B Compatibility Repository (SQLite WAL)          │
  │  • Parameterized queries against data/partvision.db         │
  │  • Verified OEM vs demonstration records segregated         │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                 Structured API Response                     │
  │  • UUID request_id  • Image dimensions  • Latencies         │
  │  • Detections + Polygon Masks + Vehicle Compatibility       │
  └─────────────────────────────────────────────────────────────┘
```

> **CORE RULE**: The API never hallucinates compatibility using an LLM. Visual parts are identified by YOLO; vehicle fitment is determined by SQLite.

---

## 3. Endpoints Specification

### 3.1 Health & Diagnostics

#### `GET /health`
Returns system status, model readiness, and database connectivity.

**Response Example (200 OK):**
```json
{
  "status": "healthy",
  "service": "PartVision AI API",
  "version": "0.4.0",
  "model": "partvision_v3_yolo11n_seg",
  "model_loaded": true,
  "database_connected": true
}
```

---

### 3.2 Vision Analysis & Compatibility

#### `POST /api/analyze`
Accepts an automotive photograph, detects spare parts, and resolves vehicle compatibility.

- **Content-Type**: `multipart/form-data`
- **Form Field**: `file` (binary image data)
- **Supported Formats**: JPEG, JPG, PNG, WEBP
- **Maximum File Size**: 20 MB

**cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analyze" \
  -H "Accept: application/json" \
  -F "file=@data/processed/partvision-v3/images/test/hitl_Car_damages_1033.png"
```

**Response Example (200 OK):**
```json
{
  "request_id": "c36fac31-2ba6-46ae-9195-c63c299d150d",
  "model": {
    "name": "PartVision YOLO11n-seg",
    "version": "v3"
  },
  "image": {
    "width": 699,
    "height": 527
  },
  "detections": [
    {
      "class_id": 18,
      "part_name": "wheel",
      "display_name": "Wheel",
      "confidence": 0.954,
      "bbox": {
        "x1": 49.0,
        "y1": 161.0,
        "x2": 94.0,
        "y2": 250.0
      },
      "mask": {
        "format": "polygon",
        "points": [[52.0, 161.0], [94.0, 185.0], [89.0, 250.0], [49.0, 220.0]]
      },
      "compatibility": {
        "verified_vehicles": [
          {
            "id": 8,
            "make": "Honda",
            "model": "City",
            "generation": "5th Gen",
            "year_start": 2020,
            "year_end": null,
            "variant": "V / VX / ZX",
            "vehicle_type": "Sedan",
            "compatibility_status": "compatible",
            "notes": "15-inch or 16-inch multi-spoke diamond-cut alloy wheels (4x100 PCD).",
            "source": "Honda Access Catalog",
            "verified": true
          }
        ],
        "unverified_vehicles": [],
        "total_matches": 1
      }
    }
  ],
  "summary": {
    "detection_count": 1,
    "detected_parts": ["wheel"]
  },
  "inference": {
    "device": "mps",
    "latency_ms": 41.2,
    "total_pipeline_ms": 143.8
  }
}
```

---

### 3.3 Parts Catalog

#### `GET /api/parts`
Returns all 19 canonical taxonomy classes.
- **Query Parameters**:
  - `category` *(string, optional)*: Filter by component category (e.g., `Lighting`, `Exterior Body`).
  - `search` *(string, optional)*: Substring keyword filter.

#### `GET /api/parts/{part_name}`
Returns detailed metadata, search aliases, and full vehicle compatibility for a part.
- **Example**: `GET /api/parts/front_bumper`

---

### 3.4 Vehicle Catalog

#### `GET /api/vehicles`
Returns vehicles in the catalog.
- **Query Parameters**:
  - `make` *(string, optional)*: Filter by manufacturer (e.g., `Hyundai`).
  - `model` *(string, optional)*: Filter by model name (e.g., `Creta`).

#### `GET /api/vehicles/{vehicle_id}`
Returns vehicle information and all compatible parts with fitment statuses.
- **Example**: `GET /api/vehicles/1`

---

### 3.5 Compatibility Lookup

#### `GET /api/compatibility/{part_name}`
Returns vehicle fitment records for a part or known search alias.
- **Query Parameters**:
  - `verified_only` *(bool, default=false)*: When true, filters out unverified demonstration records.

---

## 4. Error Handling & Standard Error Codes

All errors return a consistent JSON payload:

```json
{
  "error": "NotFoundError",
  "detail": "Part 'sunroof' not found in canonical taxonomy."
}
```

| HTTP Code | Error Classification | Scenario |
| :---: | :--- | :--- |
| **400** | `ValidationError` / `ClientError` | Empty upload, invalid form parameters, or unreadable/corrupt image bytes |
| **404** | `NotFoundError` | Unknown part name or vehicle ID |
| **413** | `PayloadTooLarge` | Uploaded image exceeds 20 MB limit |
| **415** | `UnsupportedMediaType` | File format is not JPEG, PNG, or WEBP |
| **500** | `InternalServerError` | Unhandled runtime exception (stack traces suppressed) |

---

## 5. Security & Input Sanitization

1. **Max Upload Size**: Strictly bounded to 20 MB.
2. **Double Image Verification**: Checks filename extension, Content-Type MIME header, and validates that OpenCV can decode the binary payload.
3. **Guaranteed Temp File Cleanup**: Temporary image files written to disk for YOLO processing are deleted inside a `finally` block.
4. **Parameterized Queries**: All database lookups utilize parameterized SQLite statements preventing SQL injection.
5. **No Shell Execution**: No user input is passed to system commands.
6. **CORS Hardening**: Specific allowed origins (`http://localhost:5173`, `http://localhost:3000`) rather than open wildcards.
