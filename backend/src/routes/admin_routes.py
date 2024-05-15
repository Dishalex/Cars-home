from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src import UserResponse
from backend.src.repository.car_repository import CarRepository
from backend.src.repository.parking import create_rate, create_or_update_rate, get_default_rate_values
from backend.src.routes.notification import telegram_notification
from backend.src.schemas.car_schemas import CarSchema, CarUpdate, NewCarResponse
from backend.src.database import get_db
from backend.src.schemas.parking_schema import ParkingRateSchema, NewParkingRateSchema
from backend.src.services.auth import auth_service
from backend.src.entity.models import User, Role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/cars", response_model=NewCarResponse, status_code=201)
async def create_car(car_data: CarSchema, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    try:
        new_car = await car_repository.add_car(car_data)
        if isinstance(new_car, dict) and 'error' in new_car:
            return JSONResponse(status_code=400, content={"message": new_car['error']})
        if new_car is None:
            return JSONResponse(status_code=400, content={"message": "Error creating the car"})
        return new_car
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


# @router.post("/parking-rates", response_model=ParkingRateSchema, status_code=201)
# async def create_parking_rate(rate_data: NewParkingRateSchema, db: AsyncSession = Depends(get_db),
#                               admin: User = Depends(auth_service.get_current_admin)):
#     if admin.role != Role.admin:
#         return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
#     new_rate = await create_rate(db, rate_data)
#     if not new_rate:
#         return JSONResponse(status_code=404, content={"message": "Error creating the parking rate"})
#         # raise HTTPException(status_code=400, detail="Error creating the parking rate")
#     return new_rate


@router.get("/default-parking-rate", response_model=ParkingRateSchema)
async def get_default_parking_rate(db: AsyncSession = Depends(get_db),
                                   admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    latest_rate = await get_default_rate_values(db)
    if not latest_rate:
        return JSONResponse(status_code=404, content={"message": "No rates found"})
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No rates found")
    return latest_rate


@router.post("/parking-rates", response_model=NewParkingRateSchema, status_code=201)
async def create_or_update_parking_rate(rate_data: NewParkingRateSchema, db: AsyncSession = Depends(get_db),
                                        admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    if not rate_data:
        return JSONResponse(status_code=400, content={"message": "No rate data provided"})
    new_rate = await create_or_update_rate(db, rate_data)
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


@router.get("/cars/parked", response_model=list[NewCarResponse], status_code=200)
async def read_parked_cars(db: AsyncSession = Depends(get_db),
                           admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=403, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    parked_cars = await car_repository.get_cars_currently_parked()
    if not parked_cars:
        return JSONResponse(status_code=404, content={"message": "No parked cars found"})
    return parked_cars


@router.get("/cars/{plate}", response_model=NewCarResponse, status_code=200)
async def read_car(plate: str, db: AsyncSession = Depends(get_db),
                   admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    car = await car_repository.get_car_by_plate(plate)
    if car is None:
        return JSONResponse(status_code=404, content={"message": "Car not found"})
    return car


@router.get("/cars", response_model=list[NewCarResponse], status_code=200)
async def read_cars(db: AsyncSession = Depends(get_db),
                    admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    cars = await car_repository.get_all_cars()
    if cars is None:
        return JSONResponse(status_code=404, content={"message": "Cars not found"})
    return cars


@router.get("/users-by-car/{plate}", response_model=list[UserResponse], status_code=200)
async def read_users_by_car(plate: str, db: AsyncSession = Depends(get_db),
                            admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=403, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    if not await car_repository.check_car_exists(plate):
        return JSONResponse(status_code=404, content={"message": "Car not found"})
    users = await car_repository.get_users_by_car_plate(plate)
    if not users:
        return JSONResponse(status_code=404, content={"message": "No users found for this car"})
    return users


@router.patch("/cars/{plate}", response_model=NewCarResponse, status_code=200)
async def update_car(plate: str, car_update: CarUpdate, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    try:
        updated_car = await car_repository.update_car(plate, car_update)
        if isinstance(updated_car, dict) and 'error' in updated_car:
            return JSONResponse(status_code=400, content={"message": updated_car['error']})
        if updated_car is None:
            return JSONResponse(status_code=404, content={"message": "Car not found"})
        return updated_car
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.patch("/cars/{plate}/ban", response_model=dict, status_code=200)
async def ban_car(plate: str, db: AsyncSession = Depends(get_db),
                  admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=403, content={"message": "Not authorized to access this resource"})

    car_repository = CarRepository(db)
    car = await car_repository.ban_car(plate)  # TODO: add users (car, users = ...) for notification

    if car is None:
        return JSONResponse(status_code=404, content={"message": "Car not found"})
    elif car:
        # for user in users:
        #     await telegram_notification("ban", user)
        return JSONResponse(status_code=200, content={"message": f"Car {plate} has been banned"})
    else:
        return JSONResponse(status_code=400, content={"message": "Error banning the car"})


@router.delete("/cars/{plate}", response_model=dict, status_code=200)
async def delete_car(plate: str, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    if not await car_repository.check_car_exists(plate):
        return JSONResponse(status_code=404, content={"message": "Car not found"})
    await car_repository.delete_car(plate)
    return JSONResponse(status_code=200, content={"message": f"Car {plate} has been deleted"})
