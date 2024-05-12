# backend/src/routes/history_routes.py
from typing import List
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import func, DateTime

from backend.src.database.db import get_db
from backend.src.repository import history as repositories_history
from backend.src.repository import picture as repositories_picture
from backend.src.schemas.history_schema import HistoryUpdatePaid, HistorySchema, HistoryUpdateCar, HistoryUpdate
from backend.src.entity.models import User, Role
from backend.src.services.auth import auth_service


router = APIRouter(prefix="/history", tags=["history"])

@router.get("/create_exit/{find_plate}/{picture_id}", response_model=HistoryUpdate)
async def create_exit(find_plate, picture_id, session: AsyncSession = Depends(get_db)):
    history = await repositories_history.create_exit(find_plate, picture_id, session)
    if history is None:
        return JSONResponse(status_code=400, content={"message": "Error creating exit car"})
    return history

@router.get("/create_entry/{find_plate}/{picture_id}", response_model=HistoryUpdate)
async def create_entry(find_plate, picture_id, session: AsyncSession = Depends(get_db)):
    history = await repositories_history.create_entry(find_plate, picture_id, session)
    if history is None:
        return JSONResponse(status_code=400, content={"message": "Error creating entry car"})
    return history

@router.get("/get_entries_by_period/{start_time}/{end_time}", response_model=List[HistorySchema])
async def get_history_entries_by_period_route(start_time: datetime, end_time: datetime,
                                              session: AsyncSession = Depends(get_db)):
    history_entries = await repositories_history.get_history_entries_by_period(start_time, end_time, session)
    return history_entries


@router.get("/get_null_car_id", response_model=List[HistorySchema])
async def get_history_entries_with_null_car_id_route(session: AsyncSession = Depends(get_db)):
    history_entries = await repositories_history.get_history_entries_with_null_car_id(session)
    return history_entries


@router.get("/get_no_paid", response_model=List[HistorySchema])
async def get_history_entries_with_null_paid(session: AsyncSession = Depends(get_db)):
    history_entries = await repositories_history.get_history_entries_with_null_paid(session)
    return history_entries


@router.patch("/update_paid/{plate}", response_model=HistoryUpdatePaid)
async def update_paid(plate: str, history_update: HistoryUpdatePaid,
                      session: AsyncSession = Depends(get_db),
                      admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    try:
        history_entry = await repositories_history.update_paid_history(plate, history_update.paid, session)
        if history_entry is None:
            return JSONResponse(status_code=404, content={"message": "History entry not found"})
        return history_entry

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.patch("/update_car_history/{plate}", response_model=HistoryUpdateCar)
async def update_car_history(plate: str, history_update: HistoryUpdateCar,
                             session: AsyncSession = Depends(get_db),
                             admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    try:
        history_entry = await repositories_history.update_car_history(plate, history_update.car_id, session)
        if history_entry is None:
            return JSONResponse(status_code=404, content={"message": "History entry not found"})
        return history_entry
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})



@router.delete("/delete_history/{plate}", response_model=dict, status_code=200)
async def delete_history(plate: str, db: AsyncSession = Depends(get_db),
                         admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    try:
        await repositories_history.delete_history(plate)

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
