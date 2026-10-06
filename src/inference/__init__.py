"""
src/inference
PartVision AI Production Inference Module for V3 YOLO11n-seg.
"""

from src.inference.engine import PartVisionInferenceEngine
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
from src.inference.utils import (
    FROZEN_V3_CLASSES,
    CLASS_NAME_TO_ID,
    CLASS_ID_TO_NAME,
    select_optimal_device,
    load_image,
)
from src.inference.visualize import draw_detections, save_annotated_image

__all__ = [
    "PartVisionInferenceEngine",
    "BBox",
    "PolygonMask",
    "Detection",
    "ModelMetadata",
    "ImageMetadata",
    "InferenceConfig",
    "InferenceSummary",
    "InferenceResult",
    "FROZEN_V3_CLASSES",
    "CLASS_NAME_TO_ID",
    "CLASS_ID_TO_NAME",
    "select_optimal_device",
    "load_image",
    "draw_detections",
    "save_annotated_image",
]
