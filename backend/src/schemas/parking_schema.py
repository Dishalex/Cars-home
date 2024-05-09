from typing import Optional, Union
from uuid import UUID
from sqlalchemy import func, DateTime

from pydantic import BaseModel, Field


class ParkingRateUpdate(BaseModel):
    """Pydantic model for validating incoming ParkingRate data for updating."""
    rate_per_hour: float
    rate_per_day: float
    number_of_spaces: int
    number_free_spaces: int
    history: Union[UUID, int]


class ParkingRateSchema(BaseModel):
    """Pydantic model for validating incoming ParkingRate data."""
    rate_per_hour: float
    rate_per_day: float
    number_of_spaces: int
    number_free_spaces: int
    history: Union[UUID, int]
