"""
src/api/routes/vehicles.py
Vehicle catalog and vehicle-specific parts browsing routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.database.repository import PartVisionRepository
from src.api.dependencies import get_repository
from src.api.schemas import (
    VehicleSummary,
    VehicleDetailResponse,
    VehiclePartFitmentItem,
)

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles Catalog"])


@router.get(
    "",
    response_model=List[VehicleSummary],
    summary="List available automotive vehicles",
    description="Returns all vehicles in the catalog, with optional filtering by make and model.",
)
async def list_vehicles(
    make: Optional[str] = Query(None, description="Filter by vehicle make (e.g. 'Hyundai')"),
    model: Optional[str] = Query(None, description="Filter by vehicle model (e.g. 'Creta')"),
    repo: PartVisionRepository = Depends(get_repository),
) -> List[VehicleSummary]:
    """Retrieves vehicles from the database catalog with optional make/model filtering."""
    if make and model:
        vehicles = repo.get_vehicle_by_make_model(make, model)
    else:
        vehicles = repo.get_all_vehicles()
        if make:
            make_lower = make.strip().lower()
            vehicles = [v for v in vehicles if v.make.lower() == make_lower]
        if model:
            model_lower = model.strip().lower()
            vehicles = [v for v in vehicles if v.model.lower() == model_lower]

    return [
        VehicleSummary(
            id=v.id,
            make=v.make,
            model=v.model,
            generation=v.generation,
            year_start=v.year_start,
            year_end=v.year_end,
            variant=v.variant,
            vehicle_type=v.vehicle_type,
            notes=v.notes,
            display_name=v.display_name,
        )
        for v in vehicles
    ]


@router.get(
    "/{vehicle_id}",
    response_model=VehicleDetailResponse,
    summary="Get vehicle details and compatible parts",
    description="Returns vehicle metadata and all mapped automotive components with their fitment statuses.",
)
async def get_vehicle_detail(
    vehicle_id: int,
    repo: PartVisionRepository = Depends(get_repository),
) -> VehicleDetailResponse:
    """Retrieves a single vehicle and its associated compatible parts."""
    vehicle = repo.get_vehicle_by_id(vehicle_id)
    if not vehicle or vehicle.id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found in catalog.",
        )

    compatible_records = repo.get_compatible_parts(vehicle_id)

    parts_list = [
        VehiclePartFitmentItem(
            part_id=c.part.id,
            part_name=c.part.part_name,
            display_name=c.part.display_name,
            category=c.part.category,
            compatibility_status=c.compatibility_status,
            notes=c.notes,
            source=c.source,
            verified=c.verified,
        )
        for c in compatible_records
    ]

    summary = VehicleSummary(
        id=vehicle.id,
        make=vehicle.make,
        model=vehicle.model,
        generation=vehicle.generation,
        year_start=vehicle.year_start,
        year_end=vehicle.year_end,
        variant=vehicle.variant,
        vehicle_type=vehicle.vehicle_type,
        notes=vehicle.notes,
        display_name=vehicle.display_name,
    )

    return VehicleDetailResponse(
        vehicle=summary,
        compatible_parts=parts_list,
        total_parts=len(parts_list),
    )
