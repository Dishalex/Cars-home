from backend.src import auth_service
from backend.src.entity.models import User
from backend.src.database.db import get_db
# from backend.src.repository import parking as parking_rate_repository
from backend.src.repository import history as repositories_history

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.schemas.parking_schema import ParkingRateSchema
from backend.src.schemas.history_schema import HistoryUpdate

router = APIRouter(prefix="/parking-rate", tags=["parking-rate"])

# @router.get("/free-spaces", response_model=ParkingRateSchema)
# async def get_latest_parking_rate_with_free_spaces(session: AsyncSession = Depends(get_db)):
#     return await parking_rate_repository.get_latest_parking_rate_with_free_spaces(session)


@router.get("/free-spaces", response_model=str)
async def get_latest_parking_rate_with_free_spaces(
        user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db)
):
    return await repositories_history.get_latest_parking_rate_with_free_spaces(session)
