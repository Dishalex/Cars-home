from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID
from sqlalchemy import func, DateTime

from pydantic import BaseModel, Field
    
    
    

class HistoryUpdate(BaseModel):
    """Pydantic model for validating incoming history data for updating."""
    entry_time: Optional[DateTime]
    exit_time: Optional[DateTime]
    parking_time: Optional[float]
    cost: Optional[float]
    paid: Optional[bool]
    car_id: Optional[Union[UUID, int]]
    picture_id: Optional[Union[UUID, int]]
    rate_id: Optional[Union[UUID, int]]


class HistorySchema(BaseModel):
    """Pydantic model for validating incoming history data."""
    entry_time: DateTime = Field(default_factory=func.now())
    exit_time: DateTime = Field(default_factory=func.now())
    parking_time: float
    cost: float
    paid: bool
    car_id: Union[UUID, int]
    picture_id: Union[UUID, int]
    rate_id: Union[UUID, int]


class HistoryResponse(BaseModel):
    """Pydantic model for serializing history data in responses."""
    id: int
    entry_time: DateTime
    exit_time: DateTime
    parking_time: float
    cost: float
    paid: bool
    car: Union[UUID, int]
    picture: Union[UUID, int]
    rate: Union[UUID, int]

