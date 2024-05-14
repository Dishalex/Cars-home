# backend/src/routes/history_routes.py
from typing import List
from datetime import datetime, timedelta
from fastapi.responses import FileResponse, JSONResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database.db import get_db
from backend.src.repository import history as repositories_history
from backend.src.schemas.history_schema import HistoryUpdatePaid, HistoryGet, HistoryUpdateCar, HistoryUpdate, HistorySchema
from backend.src.entity.models import User, Role
from backend.src.services.auth import auth_service
from backend.src.repository.car_repository import CarRepository


router = APIRouter(prefix="/history", tags=["history"])

@router.get("/create_entry/{find_plate}/{picture_id}", response_model=HistoryUpdate)
async def create_entry(find_plate, picture_id, session: AsyncSession = Depends(get_db)):
    history = await repositories_history.create_entry(find_plate, picture_id, session)
    if history is None:
        return JSONResponse(status_code=400, content={"message": "Error creating entry car"})
    return history


@router.get("/create_exit/{find_plate}/{picture_id}", response_model=HistoryUpdate)
async def create_exit(find_plate, picture_id, session: AsyncSession = Depends(get_db)):
    history = await repositories_history.create_exit(find_plate, picture_id, session)
    if history is None:
        return JSONResponse(status_code=400, content={"message": "Error creating exit car"})
    return history



@router.get("/get_no_paid", response_model=List[HistoryUpdate])
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
    

@router.get("/get_null_car_id", response_model=List[HistoryUpdate])
async def get_history_entries_with_null_car_id_route(session: AsyncSession = Depends(get_db)):
    history_entries = await repositories_history.get_history_entries_with_null_car_id(session)
    return history_entries


@router.patch("/update_car_in_history/{plate}", response_model=HistoryUpdateCar)
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
    


@router.get("/get_all_entries_by_period/{start_date}/{end_date}")
async def get_history_entries_by_period_route(start_date: str, end_date: str, session: AsyncSession = Depends(get_db),
                             admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

        end_datetime += timedelta(days=1)
        end_datetime -= timedelta(microseconds=1)
    except ValueError:
        return JSONResponse(status_code=400, content={"message": "Invalid date format. Please provide dates in ISO format (YYYY-MM-DD)"})

    history_entries = await repositories_history.get_history_entries_by_period(start_datetime, end_datetime, session)
    file_path = "backend/history_entries.csv"
    await repositories_history.save_history_to_csv(history_entries, file_path)
    # return history_entries


@router.get("/get_car_entries_by_period/{start_date}/{end_date}/{car_id}")
async def get_history_entries_by_period_route(start_date: str, end_date: str, car_id: int,
                                              current_user: User = Depends(auth_service.get_current_user), 
                                              session: AsyncSession = Depends(get_db)):
    
    car_repository = CarRepository(session)
    user_id = await car_repository.get_user_id_by_car_id(car_id)
    if user_id == None:
        return JSONResponse(status_code=400, content={"message": f"No user found with car {car_id}"}) 
    if current_user.role != Role.admin and current_user.id != user_id:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})   
    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

        end_datetime += timedelta(days=1)
        end_datetime -= timedelta(microseconds=1)
    except ValueError:
        return JSONResponse(status_code=400, content={"message": "Invalid date format. Please provide dates in ISO format (YYYY-MM-DD)"})

    history_entries = await repositories_history.get_history_entries_by_period_car(start_datetime, end_datetime, car_id, session)
    
    
    file_path = "backend/history_entries.csv"
    await repositories_history.save_history_to_csv(history_entries, file_path)

    # return FileResponse(file_path)


