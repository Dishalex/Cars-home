
from backend.src.database.db import get_db
from backend.src.repository import parking as parking_rate_repository

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.schemas.parking_schema import ParkingRateSchema

router = APIRouter(prefix="/parking-rate", tags=["parking-rate"])


@router.get("/free-spaces", response_model=ParkingRateSchema)
async def get_latest_parking_rate_with_free_spaces(session: AsyncSession = Depends(get_db)):
    return await parking_rate_repository.get_latest_parking_rate_with_free_spaces(session)
