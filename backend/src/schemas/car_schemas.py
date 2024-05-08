from datetime import datetime
from typing import Optional, Union, List
from uuid import UUID

from pydantic import BaseModel, Field


class CarUpdate(BaseModel):
    """Pydantic model for validating incoming car data for updating."""
    credit: Optional[float]
    plate: Optional[str]
    model: Optional[str]
    ban: Optional[bool]


class CarSchema(BaseModel):
    """Pydantic model for validating incoming car data."""
    credit: Optional[float]
    plate: str
    model: Optional[str]
    ban: Optional[bool]


class CarResponse(BaseModel):
    """Pydantic model for serializing car data in responses."""
    id: int
    credit: Optional[float]
    plate: str
    model: Optional[str]
    ban: Optional[bool]
    history: List[Union[UUID, int]]
    blacklisted_tokens: List[Union[UUID, int]]
    users: List[Union[UUID, int]]

    class Config:
        orm_mode = True