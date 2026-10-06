"""
src/inference/schemas.py
Typed Pydantic schemas for the PartVision V3 Production Inference Engine.

All bounding box and polygon mask coordinates are specified in original-image pixel space:
- (0, 0) represents the top-left corner of the image.
- x coordinates span [0, image_width].
- y coordinates span [0, image_height].
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class BBox(BaseModel):
    """
    Axis-aligned bounding box coordinates in original image pixel space.
    """
    model_config = ConfigDict(extra="forbid")

    x1: float = Field(..., description="Top-left horizontal coordinate (pixels)")
    y1: float = Field(..., description="Top-left vertical coordinate (pixels)")
    x2: float = Field(..., description="Bottom-right horizontal coordinate (pixels)")
    y2: float = Field(..., description="Bottom-right vertical coordinate (pixels)")

    @property
    def width(self) -> float:
        """Width of bounding box in pixels."""
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        """Height of bounding box in pixels."""
        return max(0.0, self.y2 - self.y1)

    @property
    def area(self) -> float:
        """Area of bounding box in square pixels."""
        return self.width * self.height


class PolygonMask(BaseModel):
    """
    Instance segmentation mask represented as ordered 2D polygon vertices.
    """
    model_config = ConfigDict(extra="forbid")

    format: str = Field(default="polygon", description="Mask format descriptor")
    points: List[List[float]] = Field(
        ...,
        description="Ordered sequence of [x, y] coordinates in original image pixel space"
    )

    @property
    def point_count(self) -> int:
        """Number of vertices in the polygon."""
        return len(self.points)


class Detection(BaseModel):
    """
    Individual detected physical part instance with bounding box and segmentation mask.
    """
    model_config = ConfigDict(extra="forbid")

    class_id: int = Field(..., ge=0, le=18, description="Class integer ID (0 to 18)")
    class_name: str = Field(..., description="Human-readable part taxonomy label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score [0.0, 1.0]")
    bbox: BBox = Field(..., description="Bounding box in original image pixels")
    mask: Optional[PolygonMask] = Field(default=None, description="Segmentation polygon in original image pixels")

    @field_validator("confidence")
    @classmethod
    def round_confidence(cls, v: float) -> float:
        return round(v, 4)


class ModelMetadata(BaseModel):
    """
    Metadata describing the frozen computer vision model.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(default="PartVision YOLO11n-seg", description="Model architecture title")
    version: str = Field(default="v3", description="Taxonomy version identifier")
    checkpoint: str = Field(..., description="Path or basename of the weights file")
    num_classes: int = Field(default=19, description="Number of taxonomy classes")


class ImageMetadata(BaseModel):
    """
    Dimensions and metadata of the input image.
    """
    model_config = ConfigDict(extra="forbid")

    width: int = Field(..., gt=0, description="Image horizontal width in pixels")
    height: int = Field(..., gt=0, description="Image vertical height in pixels")
    channels: int = Field(default=3, description="Color channel count")
    filename: Optional[str] = Field(default=None, description="Source image filename if loaded from disk")


class InferenceConfig(BaseModel):
    """
    Hyperparameters and hardware configuration used for inference.
    """
    model_config = ConfigDict(extra="forbid")

    device: str = Field(..., description="Device used for computation ('mps', 'cuda', 'cpu')")
    confidence_threshold: float = Field(..., ge=0.0, le=1.0, description="Minimum confidence cutoff")
    iou_threshold: float = Field(..., ge=0.0, le=1.0, description="NMS IoU threshold")
    image_size: int = Field(..., gt=0, description="Inference square resolution (e.g. 512)")


class InferenceSummary(BaseModel):
    """
    Aggregated high-level detection summary for API consumers.
    """
    model_config = ConfigDict(extra="forbid")

    detection_count: int = Field(..., ge=0, description="Total number of part instances detected")
    detected_classes: List[str] = Field(..., description="Distinct class names present in detections")


class InferenceResult(BaseModel):
    """
    Normalized, structured image-level result object returned by PartVisionInferenceEngine.
    """
    model_config = ConfigDict(extra="forbid")

    model: ModelMetadata
    image: ImageMetadata
    inference: InferenceConfig
    detections: List[Detection] = Field(default_factory=list)
    summary: InferenceSummary
    latency_ms: Optional[float] = Field(default=None, description="Inference latency in milliseconds")

    def to_dict(self) -> dict:
        """Serializes the result to a standard Python dictionary."""
        return self.model_dump()

    def to_json(self, indent: int = 2) -> str:
        """Serializes the result to a formatted JSON string."""
        return self.model_dump_json(indent=indent)

    def get_detections_by_class(self, class_name: str) -> List[Detection]:
        """Returns all detections corresponding to a specific part class."""
        return [d for d in self.detections if d.class_name == class_name]
