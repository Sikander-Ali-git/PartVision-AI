"""
src/database
PartVision AI Structured Automotive Compatibility Database Module.
"""

from src.database.connection import (
    get_db_connection,
    db_session,
    DEFAULT_DB_PATH,
    SCHEMA_SQL,
)
from src.database.models import (
    Vehicle,
    Part,
    PartAlias,
    Compatibility,
    CompatibilityDetail,
)
from src.database.repository import PartVisionRepository

__all__ = [
    "get_db_connection",
    "db_session",
    "DEFAULT_DB_PATH",
    "SCHEMA_SQL",
    "Vehicle",
    "Part",
    "PartAlias",
    "Compatibility",
    "CompatibilityDetail",
    "PartVisionRepository",
]
