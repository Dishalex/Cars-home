from datetime import datetime
from typing import Optional, Union, List
from uuid import UUID

from pydantic import BaseModel, Field


class CarUpdate(BaseModel):
    """Pydantic model for validating incoming car data for updating."""
    credit: Optional[float] = None
    plate: Optional[str] = None
    model: Optional[str] = None
    ban: bool = Field(default=False, nullable=True)
    user_ids: Optional[List[int]] = None


class CarSchema(BaseModel):
    """Pydantic model for validating incoming car data."""
    credit: Optional[float]
    plate: str
    model: Optional[str]
    user_ids: List[int] = Field(default_factory=list)


class NewCarResponse(BaseModel):
    """Pydantic model for serializing car data in responses."""
    id: int
    credit: Optional[float]
    plate: str
    model: Optional[str]
    ban: Optional[bool]
    user_ids: List[int] = Field(default_factory=list)

    class Config:
        from_attributes = True
        # orm_mode = True



