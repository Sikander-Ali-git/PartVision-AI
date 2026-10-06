"""
tests/test_api.py
Automated test suite for PartVision AI FastAPI backend integration (Milestone 7).
Tests all 20 required scenarios including endpoints, validations, errors, and real image inference.
"""

import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.api.app import app
from src.api.schemas import (
    HealthResponse,
    AnalysisResponse,
    PartSummary,
    PartDetailResponse,
    VehicleSummary,
    VehicleDetailResponse,
    CompatibilityQueryResponse,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_IMAGE_PATH = PROJECT_ROOT / "data" / "processed" / "partvision-v3" / "images" / "test" / "hitl_Car_damages_1033.png"


@pytest.fixture(scope="session")
def client():
    """Initializes TestClient triggering application lifespan (loads YOLO model and DB)."""
    with TestClient(app) as test_client:
        yield test_client


# =============================================================================
# 1. Health & Startup Tests
# =============================================================================

def test_app_starts_and_health(client: TestClient):
    """1 & 2: Verifies application starts and GET /health returns ready status."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    health = HealthResponse.model_validate(data)
    assert health.status == "healthy"
    assert health.service == "PartVision AI API"
    assert health.version == "0.4.0"
    assert health.model_loaded is True
    assert health.database_connected is True


def test_swagger_and_redoc_documentation(client: TestClient):
    """Verifies Swagger UI and ReDoc endpoints are exposed and functional."""
    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200
    assert "Swagger UI" in docs_resp.text

    redoc_resp = client.get("/redoc")
    assert redoc_resp.status_code == 200
    assert "redoc" in redoc_resp.text.lower()


# =============================================================================
# 2. Parts Catalog Tests
# =============================================================================

def test_get_all_parts(client: TestClient):
    """3: Verifies GET /api/parts returns all 19 canonical taxonomy classes."""
    response = client.get("/api/parts")
    assert response.status_code == 200

    parts = [PartSummary.model_validate(p) for p in response.json()]
    assert len(parts) == 19
    part_names = {p.part_name for p in parts}
    assert "front_bumper" in part_names
    assert "hood" in part_names
    assert "wheel" in part_names


def test_parts_category_and_search_filtering(client: TestClient):
    """Tests optional filtering on /api/parts by category and search substring."""
    # Filter by category
    resp_cat = client.get("/api/parts?category=Lighting")
    assert resp_cat.status_code == 200
    lighting_parts = resp_cat.json()
    assert len(lighting_parts) == 2
    assert {p["part_name"] for p in lighting_parts} == {"front_light", "back_light"}

    # Search by keyword
    resp_search = client.get("/api/parts?search=bumper")
    assert resp_search.status_code == 200
    bumper_parts = resp_search.json()
    assert len(bumper_parts) == 2
    assert {p["part_name"] for p in bumper_parts} == {"front_bumper", "back_bumper"}


def test_get_part_detail(client: TestClient):
    """4: Verifies GET /api/parts/front_bumper returns full metadata and aliases."""
    response = client.get("/api/parts/front_bumper")
    assert response.status_code == 200

    detail = PartDetailResponse.model_validate(response.json())
    assert detail.part_name == "front_bumper"
    assert detail.display_name == "Front Bumper"
    assert detail.category == "Exterior Body"
    assert len(detail.aliases) > 0
    assert detail.compatibility.total_matches > 0


def test_invalid_part_returns_404(client: TestClient):
    """5: Verifies invalid part name returns HTTP 404 with standard error body."""
    response = client.get("/api/parts/nonexistent_part_xyz")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "NotFoundError"
    assert "not found" in data["detail"]


# =============================================================================
# 3. Vehicle Catalog Tests
# =============================================================================

def test_get_all_vehicles(client: TestClient):
    """6: Verifies GET /api/vehicles returns seeded vehicle catalog."""
    response = client.get("/api/vehicles")
    assert response.status_code == 200

    vehicles = [VehicleSummary.model_validate(v) for v in response.json()]
    assert len(vehicles) == 8
    makes = {v.make for v in vehicles}
    assert "Maruti Suzuki" in makes
    assert "Hyundai" in makes
    assert "Honda" in makes


def test_vehicle_filtering(client: TestClient):
    """7: Verifies vehicle filtering by make and model."""
    response = client.get("/api/vehicles?make=Hyundai&model=Creta")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 2  # Pre-facelift and Facelift
    assert all(r["make"] == "Hyundai" and r["model"] == "Creta" for r in results)


def test_vehicle_detail(client: TestClient):
    """8: Verifies vehicle detail and associated parts fitment."""
    response = client.get("/api/vehicles/1")
    assert response.status_code == 200

    data = response.json()
    detail = VehicleDetailResponse.model_validate(data)
    assert detail.vehicle.id == 1
    assert detail.vehicle.make == "Maruti Suzuki"
    assert detail.vehicle.model == "Swift"
    assert detail.total_parts > 0
    assert len(detail.compatible_parts) == detail.total_parts


def test_invalid_vehicle_returns_404(client: TestClient):
    """Verifies unknown vehicle ID returns HTTP 404."""
    response = client.get("/api/vehicles/999999")
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"


# =============================================================================
# 4. Standalone Compatibility Lookup Tests
# =============================================================================

def test_compatibility_lookup(client: TestClient):
    """9: Verifies GET /api/compatibility/{part_name} returns segregated vehicles."""
    response = client.get("/api/compatibility/front_bumper")
    assert response.status_code == 200

    compat = CompatibilityQueryResponse.model_validate(response.json())
    assert compat.part == "front_bumper"
    assert len(compat.verified_vehicles) > 0
    assert compat.total_matches == len(compat.verified_vehicles) + len(compat.unverified_vehicles)


def test_compatibility_verified_only(client: TestClient):
    """10: Verifies ?verified_only=true returns strictly verified OEM records."""
    response = client.get("/api/compatibility/front_bumper?verified_only=true")
    assert response.status_code == 200

    compat = CompatibilityQueryResponse.model_validate(response.json())
    assert len(compat.verified_vehicles) > 0
    assert len(compat.unverified_vehicles) == 0
    assert all(v.verified is True for v in compat.verified_vehicles)


def test_invalid_compatibility_part_returns_404(client: TestClient):
    """11: Verifies unknown part in compatibility query returns HTTP 404."""
    response = client.get("/api/compatibility/unknown_aftermarket_gadget")
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"


# =============================================================================
# 5. Analysis Endpoint Validation & Error Handling Tests
# =============================================================================

def test_analyze_unsupported_file_extension(client: TestClient):
    """12: Verifies non-image file extension is rejected with HTTP 415."""
    files = {"file": ("document.txt", b"This is a text file", "text/plain")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 415
    assert response.json()["error"] == "UnsupportedMediaType"


def test_analyze_unsupported_image_type(client: TestClient):
    """13: Verifies unsupported image format (e.g. GIF) is rejected with HTTP 415."""
    files = {"file": ("animated.gif", b"GIF89a...", "image/gif")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 415
    assert response.json()["error"] == "UnsupportedMediaType"


def test_analyze_empty_upload(client: TestClient):
    """14: Verifies empty (0-byte) image upload is rejected with HTTP 400."""
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_analyze_corrupt_image_bytes(client: TestClient):
    """Verifies corrupted binary content with image extension is rejected with HTTP 400."""
    files = {"file": ("corrupt.jpg", b"NOT_A_VALID_JPEG_HEADER_BYTES", "image/jpeg")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "corrupted" in response.json()["detail"].lower()


# =============================================================================
# 6. Real Image Inference & Compatibility Attachment Tests
# =============================================================================

def test_analyze_real_image_end_to_end(client: TestClient):
    """
    15, 16, 17, 18, 19, 20: Full end-to-end test on real V3 test image.
    Verifies YOLO segmentation, compatibility resolution, UUID request_id,
    temporary file cleanup, and strict Pydantic response validation.
    """
    assert TEST_IMAGE_PATH.exists(), f"Test image missing at {TEST_IMAGE_PATH}"

    with open(TEST_IMAGE_PATH, "rb") as f:
        img_bytes = f.read()

    files = {"file": ("hitl_Car_damages_1033.png", img_bytes, "image/png")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 200

    data = response.json()

    # 18: Validate Request ID exists and is a valid UUID
    assert "request_id" in data
    parsed_uuid = uuid.UUID(data["request_id"])
    assert str(parsed_uuid) == data["request_id"]

    # 20: Validate against strict Pydantic schema
    result = AnalysisResponse.model_validate(data)
    assert result.model.name == "PartVision YOLO11n-seg"
    assert result.model.version == "v3"
    assert result.image.width > 0
    assert result.image.height > 0
    assert result.inference.latency_ms > 0

    # 16: Analysis returns detections
    assert result.summary.detection_count > 0
    assert len(result.detections) == result.summary.detection_count

    # 17: Compatibility data is attached to detections
    for det in result.detections:
        assert det.part_name in result.summary.detected_parts
        assert det.confidence >= 0.25
        assert det.bbox.width > 0
        assert det.bbox.height > 0

        # Compatibility group attached
        compat = det.compatibility
        assert isinstance(compat.verified_vehicles, list)
        assert isinstance(compat.unverified_vehicles, list)
        assert compat.total_matches == len(compat.verified_vehicles) + len(compat.unverified_vehicles)

        # Check vehicle item fields
        for v in compat.verified_vehicles:
            assert v.verified is True
            assert v.make != ""
            assert v.model != ""
            assert v.source != ""
            assert v.compatibility_status in ("compatible", "incompatible", "direct_fit")

        for v in compat.unverified_vehicles:
            assert v.verified is False
            assert v.source != ""


def test_analyze_request_id_uniqueness(client: TestClient):
    """18: Verifies each analysis request receives a distinct unique UUID."""
    assert TEST_IMAGE_PATH.exists()
    with open(TEST_IMAGE_PATH, "rb") as f:
        img_bytes = f.read()

    files1 = {"file": ("test1.png", img_bytes, "image/png")}
    files2 = {"file": ("test2.png", img_bytes, "image/png")}

    resp1 = client.post("/api/analyze", files=files1)
    resp2 = client.post("/api/analyze", files=files2)

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    id1 = resp1.json()["request_id"]
    id2 = resp2.json()["request_id"]
    assert id1 != id2
    assert uuid.UUID(id1)
    assert uuid.UUID(id2)


def test_analyze_temporary_upload_is_cleaned_up(client: TestClient):
    """19: Verifies temporary files created during analysis are deleted in finally block."""
    import tempfile
    import os

    temp_dir = tempfile.gettempdir()
    files_before = set(os.listdir(temp_dir))

    with open(TEST_IMAGE_PATH, "rb") as f:
        img_bytes = f.read()

    files = {"file": ("cleanup_test.png", img_bytes, "image/png")}
    resp = client.post("/api/analyze", files=files)
    assert resp.status_code == 200

    files_after = set(os.listdir(temp_dir))
    new_files = files_after - files_before
    # Check that no new image temp file remains
    lingering_images = [f for f in new_files if f.endswith((".png", ".jpg", ".jpeg", ".webp"))]
    assert len(lingering_images) == 0, f"Lingering temporary files found: {lingering_images}"
