# backend/src/routes/history_routes.py
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import func, DateTime

from backend.src.database.db import get_db
from backend.src.repository import history as repositories_history
from backend.src.repository import picture as repositories_picture
from backend.src.schemas.history_schema import HistoryUpdate, HistorySchema, HistoryResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/find_exit_time", response_model=HistorySchema)
async def find_history_exit_time_route(session: AsyncSession = Depends(get_db)):
    find_plate, picture_id = await repositories_picture.get_random_picture_info(session)
    history = await repositories_history.find_history_exit_time(find_plate, picture_id, session)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")
    return history


@router.get("/get_entries_by_period/{start_time}/{end_time}", response_model=List[HistorySchema])
async def get_history_entries_by_period_route(start_time: datetime, end_time: datetime,
                                              session: AsyncSession = Depends(get_db)):
    history_entries = await repositories_history.get_history_entries_by_period(start_time, end_time, session)
    return history_entries


@router.get("/get_entries_with_null_car_id", response_model=List[HistorySchema])
async def get_history_entries_with_null_car_id_route(session: AsyncSession = Depends(get_db)):
    history_entries = await repositories_history.get_history_entries_with_null_car_id(session)
    return history_entries


@router.get("/get_entries_no_paid", response_model=List[HistorySchema])
async def get_history_entries_with_null_paid(session: AsyncSession = Depends(get_db)):
    history_entries = await repositories_history.get_history_entries_with_null_paid(session)
    return history_entries
