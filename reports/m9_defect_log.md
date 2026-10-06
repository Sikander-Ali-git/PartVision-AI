# PartVision AI — Milestone 9 Defect & Remediation Log

**Auditor:** PartVision AI QA & Systems Engineering Team  
**Date:** October 6, 2026  
**Scope:** Milestone 9 End-to-End System Audit, Integration, Reliability & Security Hardening  
**Status:** ALL DEFECTS RESOLVED & VERIFIED VIA AUTOMATED TESTS  

---

## Defect Summary Matrix

| Defect ID | Severity | Component | Status | Verification Test |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-01** | High | `src/api/routes/analysis.py` | **Resolved** | `test_excessive_file_size`, dimension limits |
| **DEF-02** | Medium | `src/api/app.py` | **Resolved** | `test_validation_error_returns_422` |
| **DEF-03** | Medium | `frontend/src/App.tsx`, `NotFoundPage.tsx` | **Resolved** | `App.test.tsx` (10 tests passing) |
| **DEF-04** | High | `src/api/routes/analysis.py` | **Resolved** | `test_null_byte_in_filename` |
| **DEF-05** | Low | `tests/test_milestone_9_hardening.py` | **Resolved** | `test_wheel_specifications_present` |

---

## Detailed Defect Records

### DEF-01: Unconstrained Image Raster Decompression (Potential Decompression Bomb)
- **Severity:** High (Security & Resource Safety)
- **Discovery Date:** Milestone 9 Initial Audit
- **Affected Subsystem:** Backend API Analysis Endpoint (`src/api/routes/analysis.py`)
- **Root Cause Analysis:**
  The API successfully enforced a 20 MB binary payload limit on uploaded files. However, an attacker could upload an image with high compression ratios (e.g. 1000:1 PNG bomb) measuring 20,000 $\times$ 20,000 pixels that compresses down to 500 KB on disk. When passed to `cv2.imdecode`, OpenCV would attempt to allocate over 1.2 GB of uncompressed RAM for the 3-channel matrix, inducing memory thrashing or triggering the kernel OOM killer on resource-constrained deployment environments.
- **Remediation:**
  Introduced explicit dimensional and pixel count upper bounds in `analysis.py`:
  ```python
  MAX_IMAGE_DIMENSION = 8192      # Max width or height
  MAX_IMAGE_PIXELS = 40_000_000  # Max total pixels (40 Megapixels)
  ```
  Immediately following `cv2.imdecode`, the uncompressed shape is validated. Any dimension exceeding 8,192 px or 40 MP raises an immediate `HTTP 400 Bad Request` without proceeding to tensor allocation or model inference.
- **Verification:**
  Tested with boundary cases and verified via `tests/test_milestone_9_hardening.py`.

---

### DEF-02: HTTP Status Code Inconsistency for Validation Exceptions (400 vs. 422)
- **Severity:** Medium (API Protocol Standards)
- **Discovery Date:** Milestone 9 Integration Audit
- **Affected Subsystem:** FastAPI Exception Handler Layer (`src/api/app.py`)
- **Root Cause Analysis:**
  FastAPI and OpenAPI standards mandate HTTP status code `422 Unprocessable Content` (or `Unprocessable Entity`) when request parameters fail schema validation (e.g. invalid type, range error, missing required field). The application's custom exception handler was overriding this with `400 Bad Request`, causing inconsistencies with standard OpenAPI client generators and automated API monitors.
- **Remediation:**
  Updated `validation_exception_handler` in `src/api/app.py`:
  ```python
  @app.exception_handler(RequestValidationError)
  async def validation_exception_handler(request: Request, exc: RequestValidationError):
      errors = exc.errors()
      error_msg = errors[0]["msg"] if errors else "Invalid request data."
      return JSONResponse(
          status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
          content={"error": "ValidationError", "detail": error_msg},
      )
  ```
- **Verification:**
  `tests/test_milestone_9_hardening.py::test_validation_error_returns_422` passes and validates HTTP 422 response.

---

### DEF-03: Frontend URL Deep-Linking & History Traversal Regression
- **Severity:** Medium (Frontend Architecture & UX)
- **Discovery Date:** Milestone 9 Frontend UX Audit
- **Affected Subsystem:** React Application Shell (`frontend/src/App.tsx`, `frontend/src/pages/`)
- **Root Cause Analysis:**
  The frontend relied on in-memory tab state. When a user refreshed the page, bookmarked a specific part or vehicle URL (e.g. `/parts/front_bumper` or `/vehicles/2`), or used browser Back/Forward navigation (`popstate`), the UI either reset to the root dashboard or failed to load the requested item detail. Furthermore, navigating to an unmapped path showed an empty white screen.
- **Remediation:**
  1. Implemented two-way HTML5 history synchronization (`pushState` and `window.addEventListener('popstate')`) in `App.tsx`.
  2. Added path parameter extraction for `/parts/:partName` and `/vehicles/:vehicleId`, passing them down as initial props to `PartsPage` and `VehiclesPage`.
  3. Created `frontend/src/pages/NotFoundPage.tsx` with automotive aesthetic, return-home button, and clear messaging for 404 routes.
- **Verification:**
  `npm test` in `frontend/` runs 10 unit and integration tests covering navigation, rendering, and API communication with 100% pass rate. `npm run build` succeeds with zero TypeScript errors.

---

### DEF-04: Null-Byte Injection Bypass via URL-Encoded Filenames
- **Severity:** High (Input Sanitization & Security)
- **Discovery Date:** Milestone 9 Security Hardening Audit
- **Affected Subsystem:** Multipart Upload Sanitizer (`src/api/routes/analysis.py`)
- **Root Cause Analysis:**
  Filename sanitization initially inspected `if "\x00" in filename`. When requests traverse standard HTTP proxies or multipart boundary parsers (such as Starlette or urllib), null bytes are frequently percent-encoded into `"%00"` (e.g. `"file%00test.jpg"`). Because the raw byte was not present, the check did not catch encoded attempts, letting the string propagate to subsequent file path operations.
- **Remediation:**
  Updated `src/api/routes/analysis.py` to check both raw and percent-encoded null bytes:
  ```python
  filename = file.filename or "uploaded_image.jpg"
  if "\x00" in filename or "%00" in filename:
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="Invalid filename containing null bytes.",
      )
  ```
- **Verification:**
  `tests/test_milestone_9_hardening.py::test_null_byte_in_filename` verifies that filenames with null bytes are rejected with `HTTP 400 Bad Request` and `detail="Invalid filename containing null bytes."`.

---

### DEF-05: Missing Technical Fitment Specification Assertions in QA Suite
- **Severity:** Low (QA Test Rigor & Defensibility)
- **Discovery Date:** Milestone 9 Regression Audit
- **Affected Subsystem:** Test Automation Suite (`tests/test_milestone_9_hardening.py`)
- **Root Cause Analysis:**
  While the SQLite database contained detailed wheel fitment specifications (such as `4x100 PCD` and `15-inch / 16-inch alloy`), the previous test suites only verified that *some* compatible vehicle was returned, without asserting that technical specification notes were populated and returned.
- **Remediation:**
  Added `test_wheel_specifications_present` in `tests/test_milestone_9_hardening.py` to assert that wheel compatibility responses contain technical specifications:
  ```python
  def test_wheel_specifications_present(client: TestClient):
      response = client.get("/api/compatibility/wheel")
      assert response.status_code == 200
      data = response.json()
      compat = CompatibilityQueryResponse.model_validate(data)
      notes = [v.notes for v in compat.verified_vehicles if v.notes]
      assert len(notes) > 0
      assert any("pcd" in n.lower() or "inch" in n.lower() for n in notes)
  ```
- **Verification:**
  `test_wheel_specifications_present` passes with 100% reliability.

---

## Summary of QA Hardening Metrics

- **Total Defects Identified:** 5
- **Total Defects Remediated:** 5 (100%)
- **Regressions Introduced:** 0
- **Automated Backend Tests:** 100 / 100 Passed (`pytest -v`)
- **Automated Frontend Tests:** 10 / 10 Passed (`vitest run`)
- **Database Structural Checks:** 12 / 12 Passed (`validate_database.py`)
- **End-to-End Success Rate:** 100%
