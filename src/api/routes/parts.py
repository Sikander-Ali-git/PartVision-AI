"""
src/api/routes/parts.py
Catalog and taxonomy browsing routes for automotive parts.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.database.repository import PartVisionRepository
from src.api.dependencies import get_repository
from src.api.schemas import (
    PartSummary,
    PartDetailResponse,
    PartCompatibilityGroup,
    CompatibleVehicleItem,
)

router = APIRouter(prefix="/api/parts", tags=["Parts Catalog"])


@router.get(
    "",
    response_model=List[PartSummary],
    summary="List all canonical automotive parts",
    description="Returns all 19 canonical PartVision V3 classes, with optional filtering by category or search term.",
)
async def list_parts(
    category: Optional[str] = Query(None, description="Filter by category (e.g. 'Exterior Body', 'Lighting')"),
    search: Optional[str] = Query(None, description="Search term matching part name or display name"),
    repo: PartVisionRepository = Depends(get_repository),
) -> List[PartSummary]:
    """Retrieves all parts with optional category filtering and search matching."""
    parts = repo.get_all_parts()

    if category:
        cat_lower = category.strip().lower()
        parts = [p for p in parts if p.category.lower() == cat_lower]

    if search:
        s_lower = search.strip().lower()
        parts = [
            p for p in parts
            if s_lower in p.part_name.lower() or s_lower in p.display_name.lower()
        ]

    return [
        PartSummary(
            id=p.id,
            part_name=p.part_name,
            display_name=p.display_name,
            category=p.category,
            description=p.description,
        )
        for p in parts
    ]


@router.get(
    "/{part_name}",
    response_model=PartDetailResponse,
    summary="Get part details and vehicle compatibility",
    description="Returns canonical part information, search aliases, and compatible vehicle fitment records.",
)
async def get_part_detail(
    part_name: str,
    repo: PartVisionRepository = Depends(get_repository),
) -> PartDetailResponse:
    """Retrieves detailed taxonomy and compatibility information for a specific part."""
    part = repo.get_part_by_name(part_name)
    if not part or part.id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Part '{part_name}' not found in canonical taxonomy.",
        )

    aliases = repo.get_aliases_for_part(part.id)
    all_compat = repo.get_compatible_vehicles(part.part_name)

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
        for c in all_compat
        if c.verified
    ]

    unverified_list = [
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
        for c in all_compat
        if not c.verified
    ]

    compat_group = PartCompatibilityGroup(
        verified_vehicles=verified_list,
        unverified_vehicles=unverified_list,
        total_matches=len(all_compat),
    )

    return PartDetailResponse(
        id=part.id,
        part_name=part.part_name,
        display_name=part.display_name,
        category=part.category,
        description=part.description,
        aliases=aliases,
        compatibility=compat_group,
    )
