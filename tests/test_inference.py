"""
tests/test_inference.py
Integration tests for the PartVision V3 production inference engine
using real frozen weights and real unseen test images.
"""

from pathlib import Path
import numpy as np
import pytest

from src.inference.engine import PartVisionInferenceEngine
from src.inference.schemas import InferenceResult
from src.inference.utils import FROZEN_V3_CLASSES

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "partvision_v3_yolo11n_seg_best.pt"
TEST_IMG_DIR = PROJECT_ROOT / "data" / "processed" / "partvision-v3" / "images" / "test"
SAMPLE_TEST_IMAGE = TEST_IMG_DIR / "hitl_Car_damages_1033.png"


@pytest.fixture(scope="session")
def engine():
    """Initializes the frozen model once for the entire test session."""
    assert MODEL_PATH.exists(), f"Frozen model missing at {MODEL_PATH}"
    return PartVisionInferenceEngine(model_path=MODEL_PATH, device="auto")


def test_invalid_model_path_raises():
    with pytest.raises(FileNotFoundError):
        PartVisionInferenceEngine(model_path="non_existent_weights.pt")


def test_invalid_image_path_raises(engine):
    with pytest.raises(FileNotFoundError):
        engine.predict("non_existent_image.jpg")


def test_engine_initialization_metadata(engine):
    assert engine.num_classes == 19
    assert engine.device in ("mps", "cuda", "cpu")
    assert engine.model_load_time_ms > 0


def test_real_image_inference(engine):
    assert SAMPLE_TEST_IMAGE.exists(), f"Sample test image missing: {SAMPLE_TEST_IMAGE}"
    result = engine.predict(SAMPLE_TEST_IMAGE, conf=0.25, iou=0.7, imgsz=512)

    assert isinstance(result, InferenceResult)
    assert result.model.version == "v3"
    assert result.image.width > 0
    assert result.image.height > 0
    assert result.summary.detection_count > 0
    assert len(result.detections) == result.summary.detection_count
    assert result.latency_ms is not None and result.latency_ms > 0


def test_confidence_sorting(engine):
    result = engine.predict(SAMPLE_TEST_IMAGE, conf=0.25)
    confidences = [d.confidence for d in result.detections]
    assert confidences == sorted(confidences, reverse=True), "Detections must be sorted descending by confidence"


def test_class_names_and_taxonomy_validity(engine):
    result = engine.predict(SAMPLE_TEST_IMAGE, conf=0.25)
    for det in result.detections:
        assert 0 <= det.class_id <= 18
        assert det.class_name in FROZEN_V3_CLASSES
        assert FROZEN_V3_CLASSES[det.class_id] == det.class_name


def test_bbox_and_mask_coordinate_boundaries(engine):
    result = engine.predict(SAMPLE_TEST_IMAGE, conf=0.25)
    w = result.image.width
    h = result.image.height

    for det in result.detections:
        # Bounding box bounds
        assert 0.0 <= det.bbox.x1 <= w
        assert 0.0 <= det.bbox.y1 <= h
        assert 0.0 <= det.bbox.x2 <= w
        assert 0.0 <= det.bbox.y2 <= h
        assert det.bbox.x1 <= det.bbox.x2
        assert det.bbox.y1 <= det.bbox.y2

        # Mask points bounds
        if det.mask is not None:
            assert det.mask.point_count >= 3
            for pt in det.mask.points:
                assert len(pt) == 2
                px, py = pt[0], pt[1]
                assert 0.0 <= px <= w, f"Mask x {px} out of bounds for width {w}"
                assert 0.0 <= py <= h, f"Mask y {py} out of bounds for height {h}"


def test_zero_detections_handling(engine):
    # Running with impossibly high confidence cutoff
    result = engine.predict(SAMPLE_TEST_IMAGE, conf=0.9999)
    assert result.summary.detection_count == 0
    assert len(result.detections) == 0
    assert result.summary.detected_classes == []


def test_blank_synthetic_image_handling(engine):
    # Pure black image
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    result = engine.predict(blank, conf=0.5)
    assert result.image.width == 640
    assert result.image.height == 480
    assert result.summary.detection_count == 0


def test_multiple_instances_of_same_class_not_merged(engine):
    # An image with multiple wheels
    result = engine.predict(SAMPLE_TEST_IMAGE, conf=0.25)
    wheel_detections = result.get_detections_by_class("wheel")
    if len(wheel_detections) >= 2:
        # Verify that wheels are distinct instances with unique bounding boxes
        b1 = wheel_detections[0].bbox
        b2 = wheel_detections[1].bbox
        assert (b1.x1, b1.y1, b1.x2, b1.y2) != (b2.x1, b2.y1, b2.x2, b2.y2)


def test_predict_and_visualize_does_not_mutate_original(engine):
    orig_bgr = np.zeros((300, 400, 3), dtype=np.uint8)
    orig_copy = orig_bgr.copy()

    result, annotated = engine.predict_and_visualize(orig_bgr, conf=0.25)

    assert annotated.shape == orig_bgr.shape
    assert np.array_equal(orig_bgr, orig_copy), "Original input array was mutated!"
