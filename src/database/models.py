"""
src/database/models.py
Typed data models for the PartVision SQLite Compatibility Database.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class Vehicle(BaseModel):
    """
    Represents an automotive vehicle record.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    make: str = Field(..., description="Vehicle manufacturer (e.g. 'Maruti Suzuki', 'Hyundai')")
    model: str = Field(..., description="Vehicle model name (e.g. 'Swift', 'Creta')")
    generation: Optional[str] = Field(default=None, description="Platform or generation code (e.g. '3rd Gen')")
    year_start: Optional[int] = Field(default=None, description="Starting production model year")
    year_end: Optional[int] = Field(default=None, description="Ending production model year (None if current)")
    variant: Optional[str] = Field(default=None, description="Trim or engine variant")
    vehicle_type: Optional[str] = Field(default=None, description="Body style / class ('Hatchback', 'SUV', etc.)")
    notes: Optional[str] = Field(default=None, description="Platform or engineering details")

    @property
    def display_name(self) -> str:
        """Formatted vehicle title."""
        years = f"{self.year_start}–{self.year_end or 'Present'}" if self.year_start else ""
        gen = f" ({self.generation})" if self.generation else ""
        return f"{self.make} {self.model}{gen} [{years}]".strip()


class Part(BaseModel):
    """
    Represents an automotive part taxonomy entry.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    part_name: str = Field(..., description="Canonical snake_case part identifier (matches V3 classes)")
    display_name: str = Field(..., description="Human-readable part title")
    category: str = Field(..., description="Component functional category")
    description: Optional[str] = Field(default=None, description="Detailed component description")


class PartAlias(BaseModel):
    """
    Alternate search term or colloquial synonym mapping to a canonical part.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    part_id: int = Field(..., description="Foreign key to parts.id")
    alias: str = Field(..., description="Alternative query string")


class Compatibility(BaseModel):
    """
    Compatibility mapping between a vehicle and a part.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    vehicle_id: int = Field(..., description="Foreign key to vehicles.id")
    part_id: int = Field(..., description="Foreign key to parts.id")
    compatibility_status: str = Field(
        default="compatible",
        description="Fitment status ('compatible', 'direct_fit', 'incompatible', 'requires_modification')"
    )
    notes: Optional[str] = Field(default=None, description="Fitment notes or generation specifics")
    source: str = Field(..., description="Documentation or catalog source attribution")
    verified: int = Field(
        default=0,
        description="1 if verified against OEM/catalog data; 0 if demonstration/unverified"
    )


class CompatibilityDetail(BaseModel):
    """
    Enriched compatibility record including complete vehicle and part metadata.
    """
    model_config = ConfigDict(from_attributes=True)

    compatibility_id: int
    vehicle: Vehicle
    part: Part
    compatibility_status: str
    notes: Optional[str] = None
    source: str
    verified: bool

    @property
    def is_verified(self) -> bool:
        return self.verified
