"""
src/api/routes/analysis.py
Core computer-vision image analysis and compatibility mapping endpoint.
"""

import os
import time
import uuid
import tempfile
from pathlib import Path
from typing import List

import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.inference.engine import PartVisionInferenceEngine
from src.database.repository import PartVisionRepository
from src.api.dependencies import get_inference_engine, get_repository
from src.api.schemas import (
    AnalysisResponse,
    AnalysisModelInfo,
    AnalysisImageInfo,
    AnalysisInferenceInfo,
    AnalysisSummary,
    DetectedPartItem,
    PartCompatibilityGroup,
    CompatibleVehicleItem,
)

router = APIRouter(prefix="/api", tags=["Analysis"])

# Constraints
MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
MAX_IMAGE_DIMENSION = 8192  # Max single dimension (width or height)
MAX_IMAGE_PIXELS = 40_000_000  # Max total pixels (40 megapixels)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "application/octet-stream",  # Fallback for binary form uploads
}


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze vehicle image for parts and vehicle compatibility",
    description=(
        "Uploads an automotive image, executes V3 YOLO11n-seg instance segmentation, "
        "and resolves canonical detections to authoritative SQLite compatibility records."
    ),
)
async def analyze_image(
    file: UploadFile = File(..., description="Automotive image file (JPEG, PNG, WEBP)"),
    engine: PartVisionInferenceEngine = Depends(get_inference_engine),
    repo: PartVisionRepository = Depends(get_repository),
) -> AnalysisResponse:
    """End-to-end vision analysis pipeline integrating YOLO segmentation with SQLite fitment."""
    pipeline_start_t = time.perf_counter()
    request_id = str(uuid.uuid4())

    # 1. Validate file extension and MIME type
    filename = file.filename or "uploaded_image.jpg"
    if "\x00" in filename or "%00" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename containing null bytes.",
        )

    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image extension '{ext}'. Allowed extensions: {sorted(list(ALLOWED_EXTENSIONS))}",
        )

    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported media type '{file.content_type}'. Supported: JPEG, PNG, WEBP.",
        )

    # 2. Read contents with size limit
    contents = await file.read()
    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum allowed size of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    # 3. Validate image integrity by decoding
    img_np = np.frombuffer(contents, np.uint8)
    decoded_img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    if decoded_img is None or decoded_img.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is corrupted or not a valid readable image format.",
        )

    height, width = decoded_img.shape[:2]

    # 3b. Validate image dimensions and pixel count limits (resource safety)
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION or (width * height) > MAX_IMAGE_PIXELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Image dimensions ({width}x{height}) exceed maximum allowed limits "
                f"(maximum {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION} pixels or 40 megapixels)."
            ),
        )

    # 4. Safe temporary file processing
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            temp_file = Path(f.name)
            f.write(contents)

        # 5. Run inference with frozen M6A engine
        inference_result = engine.predict(
            image=temp_file,
            conf=0.25,
            iou=0.7,
            imgsz=512,
        )

        # 6. Hydrate each detected part with authoritative M6B compatibility records
        detected_items: List[DetectedPartItem] = []
        detected_part_names: List[str] = []

        for det in inference_result.detections:
            canonical_name = det.class_name
            if canonical_name not in detected_part_names:
                detected_part_names.append(canonical_name)

            part_obj = repo.get_part_by_name(canonical_name)
            display_title = (
                part_obj.display_name if part_obj else canonical_name.replace("_", " ").title()
            )

            # Query database for vehicular compatibility
            compat_records = repo.get_compatible_vehicles(canonical_name)

            verified_vehicles = [
                CompatibleVehicleItem(
                    id=c.vehicle.id,
                    make=c.vehicle.make,
                    model=c.vehicle.model,
                    generation=c.vehicle.generation,
                    year_start=c.vehicle.year_start,
                    year_end=c.vehicle.year_end,
                    variant=c.vehicle.variant,
                    vehicle_type=c.vehicle.vehicle_type,
                    compatibility_status=c.compatibility_status,
                    notes=c.notes,
                    source=c.source,
                    verified=c.verified,
                )
                for c in compat_records
                if c.verified
            ]

            unverified_vehicles = [
                CompatibleVehicleItem(
                    id=c.vehicle.id,
                    make=c.vehicle.make,
                    model=c.vehicle.model,
                    generation=c.vehicle.generation,
                    year_start=c.vehicle.year_start,
                    year_end=c.vehicle.year_end,
                    variant=c.vehicle.variant,
                    vehicle_type=c.vehicle.vehicle_type,
                    compatibility_status=c.compatibility_status,
                    notes=c.notes,
                    source=c.source,
                    verified=c.verified,
                )
                for c in compat_records
                if not c.verified
            ]

            compat_group = PartCompatibilityGroup(
                verified_vehicles=verified_vehicles,
                unverified_vehicles=unverified_vehicles,
                total_matches=len(compat_records),
            )

            detected_items.append(
                DetectedPartItem(
                    class_id=det.class_id,
                    part_name=canonical_name,
                    display_name=display_title,
                    confidence=det.confidence,
                    bbox=det.bbox,
                    mask=det.mask,
                    compatibility=compat_group,
                )
            )

        pipeline_elapsed_ms = (time.perf_counter() - pipeline_start_t) * 1000.0

        return AnalysisResponse(
            request_id=request_id,
            model=AnalysisModelInfo(
                name="PartVision YOLO11n-seg",
                version="v3",
            ),
            image=AnalysisImageInfo(
                width=width,
                height=height,
            ),
            detections=detected_items,
            summary=AnalysisSummary(
                detection_count=len(detected_items),
                detected_parts=detected_part_names,
            ),
            inference=AnalysisInferenceInfo(
                device=inference_result.inference.device,
                latency_ms=inference_result.latency_ms or 0.0,
                total_pipeline_ms=round(pipeline_elapsed_ms, 2),
            ),
        )

    finally:
        # 7. Guaranteed temporary upload cleanup
        if temp_file and temp_file.exists():
            try:
                os.remove(temp_file)
            except OSError:
                pass
