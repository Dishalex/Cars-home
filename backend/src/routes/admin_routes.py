from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.repository.car_repository import CarRepository
from backend.src.repository.parking import create_rate, update_rate
from backend.src.schemas.car_schemas import CarSchema, CarUpdate, CarResponse, NewCarResponse
from backend.src.schemas.history_schema import HistoryUpdate, HistorySchema
from backend.src.database import get_db
from backend.src.schemas.parking_schema import ParkingRateSchema, NewParkingRateSchema, ParkingRateUpdate
from backend.src.services.auth import auth_service
from backend.src.repository import history as repositories_history
from backend.src.entity.models import User, Role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/cars", response_model=NewCarResponse, status_code=201)
async def create_car(car_data: CarSchema, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    new_car = await car_repository.add_car(car_data)

    if new_car is None:
        # raise HTTPException(status_code=400, detail="Error creating the car")
        return JSONResponse(status_code=400, content={"message": "Error creating the car"})
    # response_data = NewCarResponse.from_orm(new_car)
    # return response_data
    return new_car


@router.post("/parking-rates", response_model=ParkingRateSchema, status_code=201)
async def create_parking_rate(rate_data: NewParkingRateSchema, db: AsyncSession = Depends(get_db),
                              admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    new_rate = await create_rate(db, rate_data)
    if not new_rate:
        return JSONResponse(status_code=404, content={"message": "Error creating the parking rate"})
        # raise HTTPException(status_code=400, detail="Error creating the parking rate")
    return new_rate


# @router.patch("/parking-rates/{rate_id}", status_code=201)
# async def update_parking_rate(rate_id: int, rate_data: ParkingRateUpdate, db: AsyncSession = Depends(get_db),
#                               admin: User = Depends(auth_service.get_current_admin)):
#     if admin.role != Role.admin:
#         return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
#     new_rate = await update_rate(db, rate_id, rate_data)
#     if not new_rate:
#         return JSONResponse(status_code=404, content={"message": "Error updating the parking rate"})
#     else:
#         return {"message": "Parking rate updated successfully"}


@router.get("/cars/{plate}", response_model=NewCarResponse, status_code=200)
async def read_car(plate: str, db: AsyncSession = Depends(get_db),
                   admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    car = await car_repository.get_car_by_plate(plate)
    if car is None:
        # return JSONResponse(status_code=404, content={"message": "Car not found"})
        raise HTTPException(status_code=400, detail="Error creating the car")
    return car


@router.get("/cars", response_model=list[NewCarResponse], status_code=200)
async def read_cars(db: AsyncSession = Depends(get_db),
                    admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    return await car_repository.get_all_cars()


@router.get("/cars/{user_id}", response_model=list[NewCarResponse], status_code=200)
async def read_cars_by_user(user_id: int, db: AsyncSession = Depends(get_db),
                            admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    return await car_repository.get_cars_by_user(user_id)


@router.patch("/cars/{plate}", response_model=dict, status_code=200)
async def update_car(plate: str, car_update: CarUpdate, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    try:
        updated_car = await car_repository.update_car(plate, car_update)
        if updated_car is None:
            return JSONResponse(status_code=404, content={"message": "Car not found"})
        return {"message": "Car updated successfully"}
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.delete("/cars/{plate}", response_model=dict, status_code=200)
async def delete_car(plate: str, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    if not await car_repository.check_car_exists(plate):
        return JSONResponse(status_code=404, content={"message": "Car not found"})
    await car_repository.delete_car(plate)
    return JSONResponse(status_code=200, content={"message": "Car deleted successfully"})


@router.put("/update_paid/{plate}", response_model=HistorySchema)
async def update_paid(plate: str, history_update: HistoryUpdate,
                      session: AsyncSession = Depends(get_db),
                      admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    try:
        history_entry = await repositories_history.update_paid(plate, history_update, session)
        if history_entry is None:
            return JSONResponse(status_code=404, content={"message": "History entry not found"})
        return history_entry
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.put("/update_car_history/{plate}", response_model=HistorySchema)
async def update_car_history(plate: str, history_update: HistoryUpdate,
                             session: AsyncSession = Depends(get_db),
                             admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    try:
        history_entry = await repositories_history.update_car_history(plate, history_update, session)
        if history_entry is None:
            return JSONResponse(status_code=404, content={"message": "History entry not found"})
        return history_entry
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
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

