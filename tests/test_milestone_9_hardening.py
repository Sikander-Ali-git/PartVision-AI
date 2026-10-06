"""
tests/test_milestone_9_hardening.py
Milestone 9 - Full System Integration, Quality Assurance & Hardening Test Suite.

Audits and verifies:
1. Real Image Verification Suite (3 diverse test images from V3 test split)
2. Detection & Segmentation Geometry Invariants
3. Compatibility Query Invariants (front_bumper, wheel, hood, mirror, verified_only)
4. Upload Edge Cases & Security Invariants (null bytes, path traversal, corrupt bytes, empty file, limits)
5. API Error Matrix & HTTP Status Conformance (400, 404, 413, 415, 422)
6. Error Sanitization Invariants (No raw stack traces in responses)
7. Database & Model Resilience
"""

import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.api.app import app
from src.api.schemas import AnalysisResponse, CompatibilityQueryResponse
from src.inference.utils import FROZEN_V3_CLASSES

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_IMG_DIR = PROJECT_ROOT / "data" / "processed" / "partvision-v3" / "images" / "test"

TEST_IMAGES = [
    "hitl_Car_damages_1033.png",
    "hitl_Car_damages_1050.png",
    "car25_jpg.rf.a2a62c4f3c8af7837e5ee62d1b806750.jpg",
]


@pytest.fixture(scope="session")
def client():
    """Session-scoped TestClient ensuring full model & DB lifespan."""
    with TestClient(app) as test_client:
        yield test_client


# =============================================================================
# 1. Real Image Verification Suite (Section 5)
# =============================================================================

@pytest.mark.parametrize("img_filename", TEST_IMAGES)
def test_real_image_inference_and_geometry_invariants(client: TestClient, img_filename: str):
    """
    Tests inference across 3 distinct real test images.
    Verifies:
    - HTTP 200 with valid schema
    - Every detection has valid class_id, canonical class_name, confidence in [0, 1]
    - Bbox coordinates are strictly within image dimensions and x1 < x2, y1 < y2
    - Segmentation polygons have points within bounds
    """
    img_path = TEST_IMG_DIR / img_filename
    assert img_path.exists(), f"Test image missing: {img_path}"

    with open(img_path, "rb") as f:
        img_bytes = f.read()

    response = client.post(
        "/api/analyze",
        files={"file": (img_filename, img_bytes, "image/jpeg" if img_filename.endswith(".jpg") else "image/png")},
    )

    assert response.status_code == 200, f"Failed inference on {img_filename}: {response.text}"
    data = response.json()
    validated = AnalysisResponse.model_validate(data)

    assert validated.request_id
    assert validated.image.width > 0
    assert validated.image.height > 0
    w = validated.image.width
    h = validated.image.height

    # Check each detection's geometry and taxonomy
    for det in validated.detections:
        assert 0 <= det.class_id < len(FROZEN_V3_CLASSES), f"Invalid class_id {det.class_id}"
        assert det.part_name == FROZEN_V3_CLASSES[det.class_id]
        assert 0.0 <= det.confidence <= 1.0

        # Bounding box invariants
        x1, y1, x2, y2 = det.bbox.x1, det.bbox.y1, det.bbox.x2, det.bbox.y2
        assert 0 <= x1 < x2 <= w, f"Bbox X out of bounds or inverted: {x1}, {x2} for width {w}"
        assert 0 <= y1 < y2 <= h, f"Bbox Y out of bounds or inverted: {y1}, {y2} for height {h}"

        # Segmentation polygon mask invariants
        if det.mask is not None and len(det.mask.points) > 0:
            for pt in det.mask.points:
                px, py = pt[0], pt[1]
                assert 0.0 <= px <= float(w), f"Polygon point X out of bounds: {px} > {w}"
                assert 0.0 <= py <= float(h), f"Polygon point Y out of bounds: {py} > {h}"


# =============================================================================
# 2. Compatibility Invariants & Fitment Checks (Section 6)
# =============================================================================

@pytest.mark.parametrize("part_name", ["front_bumper", "wheel", "hood", "mirror"])
def test_compatibility_canonical_parts(client: TestClient, part_name: str):
    """Verifies compatibility lookups for core canonical parts return valid fitment records."""
    response = client.get(f"/api/compatibility/{part_name}")
    assert response.status_code == 200
    data = response.json()
    compat = CompatibilityQueryResponse.model_validate(data)

    assert compat.part == part_name
    assert compat.total_matches > 0
    all_vehicles = compat.verified_vehicles + compat.unverified_vehicles
    assert len(all_vehicles) == compat.total_matches

    for fitment in all_vehicles:
        assert fitment.make
        assert fitment.model
        assert fitment.year_start <= (fitment.year_end or 2030)
        assert fitment.compatibility_status in ["compatible", "incompatible", "direct_fit"]


def test_compatibility_verified_only_filter(client: TestClient):
    """Verifies verified_only=true returns ONLY records with is_verified == True."""
    response = client.get("/api/compatibility/front_bumper?verified_only=true")
    assert response.status_code == 200
    data = response.json()
    compat = CompatibilityQueryResponse.model_validate(data)

    assert len(compat.verified_vehicles) > 0
    assert len(compat.unverified_vehicles) == 0
    for fitment in compat.verified_vehicles:
        assert fitment.verified is True


def test_wheel_specifications_present(client: TestClient):
    """Verifies wheel compatibility records include technical wheel specifications (PCD, diameter)."""
    response = client.get("/api/compatibility/wheel")
    assert response.status_code == 200
    data = response.json()
    compat = CompatibilityQueryResponse.model_validate(data)

    notes = [v.notes for v in compat.verified_vehicles if v.notes]
    assert len(notes) > 0, "Wheel compatibility records should include technical notes"
    # Check that PCD and diameter information is documented
    has_wheel_specs = any("pcd" in n.lower() or "inch" in n.lower() for n in notes)
    assert has_wheel_specs, "Wheel technical fitment notes must mention PCD or diameter specifications"


# =============================================================================
# 3. Security, Upload & Decompression Edge Cases (Section 12 & 14)
# =============================================================================

def test_null_byte_in_filename(client: TestClient):
    """Verifies filename containing null bytes is rejected with 400."""
    response = client.post(
        "/api/analyze",
        files={"file": ("test\x00malicious.jpg", b"fakebytes", "image/jpeg")},
    )
    assert response.status_code == 400
    assert "null byte" in response.json()["detail"].lower()


def test_path_traversal_filename(client: TestClient):
    """Verifies directory traversal in filename is sanitized and processed safely."""
    # Create a small 64x64 valid PNG
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), color="blue").save(buf, format="PNG")
    buf.seek(0)

    response = client.post(
        "/api/analyze",
        files={"file": ("../../../../etc/passwd.png", buf.getvalue(), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["image"]["width"] == 64


def test_empty_file_upload(client: TestClient):
    """Verifies 0-byte file is rejected with 400."""
    response = client.post(
        "/api/analyze",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_corrupt_image_bytes(client: TestClient):
    """Verifies unparseable image bytes return 400 Bad Request."""
    response = client.post(
        "/api/analyze",
        files={"file": ("corrupt.jpg", b"Not an image at all but random text bytes", "image/jpeg")},
    )
    assert response.status_code == 400
    assert "corrupt" in response.json()["detail"].lower()


def test_unsupported_media_type(client: TestClient):
    """Verifies non-image MIME types return 415 Unsupported Media Type."""
    response = client.post(
        "/api/analyze",
        files={"file": ("script.py", b"print('hello')", "text/x-python")},
    )
    assert response.status_code == 415
    assert "unsupported" in response.json()["detail"].lower()


def test_excessive_file_size(client: TestClient):
    """Verifies file exceeding MAX_UPLOAD_SIZE_BYTES (20MB) returns 413 Payload Too Large."""
    large_payload = b"0" * (20 * 1024 * 1024 + 512 * 1024)
    response = client.post(
        "/api/analyze",
        files={"file": ("giant.jpg", large_payload, "image/jpeg")},
    )
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()


# =============================================================================
# 4. API Error Matrix & Validation Checks (Section 14)
# =============================================================================

def test_validation_error_returns_422(client: TestClient):
    """Verifies invalid path/query types return standard 422 Unprocessable Entity."""
    # Invalid path parameter type: string instead of integer vehicle_id
    response = client.get("/api/vehicles/not_a_valid_integer_id")
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"
    assert "detail" in data


def test_not_found_returns_404(client: TestClient):
    """Verifies non-existent endpoints and non-existent resources return 404."""
    # Non-existent endpoint
    resp1 = client.get("/api/unknown_resource_endpoint_xyz")
    assert resp1.status_code == 404

    # Non-existent part
    resp2 = client.get("/api/parts/non_existent_part_name_12345")
    assert resp2.status_code == 404
    assert resp2.json()["error"] == "NotFoundError"

    # Non-existent vehicle
    resp3 = client.get("/api/vehicles/999999")
    assert resp3.status_code == 404
    assert resp3.json()["error"] == "NotFoundError"


def test_error_responses_do_not_leak_traces(client: TestClient):
    """Verifies all client error responses have clean JSON and do not contain Python tracebacks."""
    for url in ["/api/parts/fake_part", "/api/vehicles/99999", "/api/vehicles/invalid_int"]:
        resp = client.get(url)
        assert resp.status_code in [404, 422]
        text = resp.text
        assert "Traceback (most recent call last)" not in text
        assert "File \"" not in text
