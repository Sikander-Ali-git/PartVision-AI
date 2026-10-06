"""
src/api/routes/compatibility.py
Direct automotive compatibility query routes for parts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.database.repository import PartVisionRepository
from src.api.dependencies import get_repository
from src.api.schemas import (
    CompatibilityQueryResponse,
    CompatibleVehicleItem,
)

router = APIRouter(prefix="/api/compatibility", tags=["Compatibility"])


@router.get(
    "/{part_name}",
    response_model=CompatibilityQueryResponse,
    summary="Query compatible vehicles for a part",
    description="Returns verified and unverified vehicle fitment records for a canonical part name or alias.",
)
async def query_compatibility(
    part_name: str,
    verified_only: bool = Query(
        False, description="If True, filters exclusively for verified OEM records"
    ),
    repo: PartVisionRepository = Depends(get_repository),
) -> CompatibilityQueryResponse:
    """Queries vehicle fitment records for a specified part, maintaining verification segregation."""
    canonical = repo.normalize_part_name(part_name)
    if not canonical:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Part '{part_name}' not recognized in taxonomy.",
        )

    part_obj = repo.get_part_by_name(canonical)
    display_title = part_obj.display_name if part_obj else canonical.replace("_", " ").title()

    compat_records = repo.get_compatible_vehicles(canonical, verified_only=verified_only)

    verified_list = [
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

    unverified_list = (
        []
        if verified_only
        else [
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
    )

    return CompatibilityQueryResponse(
        part=canonical,
        display_name=display_title,
        verified_vehicles=verified_list,
        unverified_vehicles=unverified_list,
        total_matches=len(verified_list) + len(unverified_list),
    )
