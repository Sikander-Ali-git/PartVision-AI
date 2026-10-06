"""
src/api/schemas.py
Typed Pydantic V2 schemas for PartVision AI REST API (Milestone 7).
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from src.inference.schemas import BBox, PolygonMask


# =============================================================================
# 1. Health & Diagnostics
# =============================================================================

class HealthResponse(BaseModel):
    """System health check and component readiness status."""
    model_config = ConfigDict(extra="forbid")

    status: str = Field(default="healthy", description="Overall service status")
    service: str = Field(default="PartVision AI API", description="Service title")
    version: str = Field(default="0.4.0", description="Semantic API version")
    model: str = Field(default="partvision_v3_yolo11n_seg", description="Loaded vision model")
    model_loaded: bool = Field(..., description="True if inference engine is loaded into memory")
    database_connected: bool = Field(..., description="True if SQLite database is queryable")


# =============================================================================
# 2. Automotive Compatibility Sub-Schemas
# =============================================================================

class CompatibleVehicleItem(BaseModel):
    """Vehicle specification and fitment details for a compatible component."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Vehicle primary key ID")
    make: str = Field(..., description="Vehicle manufacturer (e.g. Maruti Suzuki)")
    model: str = Field(..., description="Vehicle model (e.g. Swift)")
    generation: Optional[str] = Field(default=None, description="Generation code (e.g. 3rd Gen)")
    year_start: Optional[int] = Field(default=None, description="Starting model year")
    year_end: Optional[int] = Field(default=None, description="Ending model year (None if current)")
    variant: Optional[str] = Field(default=None, description="Trim or package")
    vehicle_type: Optional[str] = Field(default=None, description="Body style classification")
    compatibility_status: str = Field(..., description="Fitment status ('compatible', 'incompatible')")
    notes: Optional[str] = Field(default=None, description="Fitment notes and caveats")
    source: str = Field(..., description="Official catalog or repair manual source attribution")
    verified: bool = Field(..., description="True if verified against OEM parts catalog")


class PartCompatibilityGroup(BaseModel):
    """Categorized vehicle compatibility mappings for a single automotive part."""
    model_config = ConfigDict(extra="forbid")

    verified_vehicles: List[CompatibleVehicleItem] = Field(
        default_factory=list,
        description="Vehicles verified against OEM manufacturer parts catalogs"
    )
    unverified_vehicles: List[CompatibleVehicleItem] = Field(
        default_factory=list,
        description="Demonstration or unverified aftermarket compatibility records"
    )
    total_matches: int = Field(default=0, ge=0, description="Total number of compatible vehicles")


# =============================================================================
# 3. Image Analysis Endpoint Schemas
# =============================================================================

class DetectedPartItem(BaseModel):
    """Individual part detection with geometry, confidence, and vehicle fitment data."""
    model_config = ConfigDict(extra="forbid")

    class_id: int = Field(..., ge=0, le=18, description="Canonical class ID (0 to 18)")
    part_name: str = Field(..., description="Canonical snake_case taxonomy identifier")
    display_name: str = Field(..., description="Human-readable title (e.g. Front Bumper)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    bbox: BBox = Field(..., description="Bounding box in original image pixels")
    mask: Optional[PolygonMask] = Field(default=None, description="Polygon mask in original pixels")
    compatibility: PartCompatibilityGroup = Field(..., description="Vehicle compatibility matches")


class AnalysisSummary(BaseModel):
    """Aggregated detection summary for the analyzed image."""
    model_config = ConfigDict(extra="forbid")

    detection_count: int = Field(..., ge=0, description="Total number of part instances detected")
    detected_parts: List[str] = Field(..., description="Distinct canonical part names detected")


class AnalysisModelInfo(BaseModel):
    """Vision model identity metadata."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(default="PartVision YOLO11n-seg", description="Model architecture title")
    version: str = Field(default="v3", description="Model taxonomy release version")


class AnalysisImageInfo(BaseModel):
    """Image resolution metadata."""
    model_config = ConfigDict(extra="forbid")

    width: int = Field(..., gt=0, description="Image horizontal width in pixels")
    height: int = Field(..., gt=0, description="Image vertical height in pixels")


class AnalysisInferenceInfo(BaseModel):
    """Inference execution metadata."""
    model_config = ConfigDict(extra="forbid")

    device: str = Field(..., description="Inference compute device ('mps', 'cuda', 'cpu')")
    latency_ms: float = Field(..., ge=0.0, description="Raw model inference latency (ms)")
    total_pipeline_ms: Optional[float] = Field(
        default=None, ge=0.0, description="Full end-to-end API pipeline latency (ms)"
    )


class AnalysisResponse(BaseModel):
    """Top-level response schema for POST /api/analyze."""
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(..., description="Unique UUID for this analysis request")
    model: AnalysisModelInfo = Field(..., description="Vision model metadata")
    image: AnalysisImageInfo = Field(..., description="Source image dimensions")
    detections: List[DetectedPartItem] = Field(default_factory=list, description="List of detected parts")
    summary: AnalysisSummary = Field(..., description="Detection summary counts")
    inference: AnalysisInferenceInfo = Field(..., description="Compute device and latency")


# =============================================================================
# 4. Parts Catalog Schemas
# =============================================================================

class PartSummary(BaseModel):
    """Summary of a canonical taxonomy component."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Part primary key ID")
    part_name: str = Field(..., description="Canonical snake_case taxonomy identifier")
    display_name: str = Field(..., description="Human-readable title")
    category: str = Field(..., description="Functional component category")
    description: Optional[str] = Field(default=None, description="Detailed component description")


class PartDetailResponse(BaseModel):
    """Detailed taxonomy record including aliases and vehicle compatibility."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    part_name: str
    display_name: str
    category: str
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list, description="Common aliases and search synonyms")
    compatibility: PartCompatibilityGroup = Field(..., description="Vehicular compatibility mappings")


# =============================================================================
# 5. Vehicle Catalog Schemas
# =============================================================================

class VehicleSummary(BaseModel):
    """Automotive vehicle specification summary."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    make: str
    model: str
    generation: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    variant: Optional[str] = None
    vehicle_type: Optional[str] = None
    notes: Optional[str] = None
    display_name: str = Field(..., description="Formatted title with generation and model years")


class VehiclePartFitmentItem(BaseModel):
    """Part fitment detail for a specific vehicle."""
    model_config = ConfigDict(from_attributes=True)

    part_id: int
    part_name: str
    display_name: str
    category: str
    compatibility_status: str
    notes: Optional[str] = None
    source: str
    verified: bool


class VehicleDetailResponse(BaseModel):
    """Detailed vehicle information and list of compatible components."""
    model_config = ConfigDict(extra="forbid")

    vehicle: VehicleSummary
    compatible_parts: List[VehiclePartFitmentItem] = Field(default_factory=list)
    total_parts: int = Field(..., ge=0, description="Total count of mapped parts")


# =============================================================================
# 6. Standalone Compatibility Lookup Schema
# =============================================================================

class CompatibilityQueryResponse(BaseModel):
    """Response schema for GET /api/compatibility/{part_name}."""
    model_config = ConfigDict(extra="forbid")

    part: str = Field(..., description="Canonical part name")
    display_name: str = Field(..., description="Human-readable part title")
    verified_vehicles: List[CompatibleVehicleItem] = Field(default_factory=list)
    unverified_vehicles: List[CompatibleVehicleItem] = Field(default_factory=list)
    total_matches: int = Field(default=0, ge=0)


# =============================================================================
# 7. Error Handling Schema
# =============================================================================

class ErrorResponse(BaseModel):
    """Standardized error envelope returned across all API error statuses."""
    model_config = ConfigDict(extra="forbid")

    error: str = Field(..., description="Short error classification")
    detail: str = Field(..., description="Descriptive error explanation")
    request_id: Optional[str] = Field(default=None, description="Trace UUID if applicable")
