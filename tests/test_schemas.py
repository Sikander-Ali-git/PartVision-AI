"""
tests/test_schemas.py
Unit tests for PartVision V3 Pydantic schemas and serialization.
"""

import json
import pytest
from pydantic import ValidationError

from src.inference.schemas import (
    BBox,
    PolygonMask,
    Detection,
    ModelMetadata,
    ImageMetadata,
    InferenceConfig,
    InferenceSummary,
    InferenceResult,
)


def test_bbox_properties_and_validation():
    bbox = BBox(x1=100.0, y1=50.0, x2=300.0, y2=250.0)
    assert bbox.x1 == 100.0
    assert bbox.y1 == 50.0
    assert bbox.x2 == 300.0
    assert bbox.y2 == 250.0
    assert bbox.width == 200.0
    assert bbox.height == 200.0
    assert bbox.area == 40000.0


def test_bbox_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        BBox(x1=0, y1=0, x2=10, y2=10, extra_prop="invalid")


def test_polygon_mask_properties():
    points = [[10.0, 10.0], [50.0, 10.0], [50.0, 50.0], [10.0, 50.0]]
    mask = PolygonMask(format="polygon", points=points)
    assert mask.format == "polygon"
    assert mask.point_count == 4
    assert mask.points == points


def test_detection_confidence_rounding_and_bounds():
    bbox = BBox(x1=10.0, y1=10.0, x2=50.0, y2=50.0)
    det = Detection(
        class_id=7,
        class_name="front_glass",
        confidence=0.94125678,
        bbox=bbox,
        mask=None
    )
    assert det.confidence == 0.9413
    assert det.class_id == 7
    assert det.class_name == "front_glass"

    # Invalid confidence > 1.0
    with pytest.raises(ValidationError):
        Detection(class_id=7, class_name="front_glass", confidence=1.5, bbox=bbox)

    # Invalid confidence < 0.0
    with pytest.raises(ValidationError):
        Detection(class_id=7, class_name="front_glass", confidence=-0.1, bbox=bbox)

    # Invalid class_id > 18
    with pytest.raises(ValidationError):
        Detection(class_id=19, class_name="unknown", confidence=0.8, bbox=bbox)


def test_inference_result_serialization_roundtrip():
    bbox = BBox(x1=120.0, y1=85.0, x2=520.0, y2=310.0)
    mask = PolygonMask(points=[[120.0, 85.0], [520.0, 85.0], [520.0, 310.0]])
    det = Detection(
        class_id=7,
        class_name="front_glass",
        confidence=0.94,
        bbox=bbox,
        mask=mask
    )

    result = InferenceResult(
        model=ModelMetadata(
            name="PartVision YOLO11n-seg",
            version="v3",
            checkpoint="partvision_v3_yolo11n_seg_best.pt"
        ),
        image=ImageMetadata(width=1280, height=720, filename="car_sample.jpg"),
        inference=InferenceConfig(
            device="mps",
            confidence_threshold=0.25,
            iou_threshold=0.7,
            image_size=512
        ),
        detections=[det],
        summary=InferenceSummary(
            detection_count=1,
            detected_classes=["front_glass"]
        ),
        latency_ms=12.4
    )

    # Test dictionary export
    res_dict = result.to_dict()
    assert isinstance(res_dict, dict)
    assert res_dict["summary"]["detection_count"] == 1
    assert res_dict["detections"][0]["class_name"] == "front_glass"

    # Test JSON string export
    json_str = result.to_json()
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["model"]["version"] == "v3"
    assert parsed["image"]["width"] == 1280
    assert parsed["detections"][0]["bbox"]["x1"] == 120.0

    # Test round-trip reconstruction
    reconstructed = InferenceResult.model_validate_json(json_str)
    assert reconstructed.summary.detection_count == 1
    assert reconstructed.detections[0].class_name == "front_glass"
    assert reconstructed.detections[0].mask.point_count == 3


def test_get_detections_by_class():
    bbox = BBox(x1=0, y1=0, x2=10, y2=10)
    d1 = Detection(class_id=18, class_name="wheel", confidence=0.9, bbox=bbox)
    d2 = Detection(class_id=18, class_name="wheel", confidence=0.85, bbox=bbox)
    d3 = Detection(class_id=10, class_name="hood", confidence=0.92, bbox=bbox)

    result = InferenceResult(
        model=ModelMetadata(checkpoint="dummy.pt"),
        image=ImageMetadata(width=640, height=480),
        inference=InferenceConfig(device="cpu", confidence_threshold=0.25, iou_threshold=0.7, image_size=512),
        detections=[d1, d2, d3],
        summary=InferenceSummary(detection_count=3, detected_classes=["wheel", "hood"])
    )

    wheels = result.get_detections_by_class("wheel")
    assert len(wheels) == 2
    assert all(w.class_name == "wheel" for w in wheels)

    doors = result.get_detections_by_class("front_door")
    assert len(doors) == 0
