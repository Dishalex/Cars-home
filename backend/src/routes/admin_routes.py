
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.repository.car_repository import CarRepository
from backend.src.schemas.car_schemas import CarSchema, CarUpdate, CarResponse, NewCarResponse
from backend.src.database import get_db
from backend.src.services.auth import auth_service
from backend.src.entity.models import User, Role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/cars", response_model=NewCarResponse, status_code=201)
async def create_car(car_data: CarSchema, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    car_repository = CarRepository(db)
    new_car = await car_repository.add_car(car_data)
    if new_car is None:
        # raise HTTPException(status_code=400, detail="Error creating the car")
        return JSONResponse(status_code=400, content={"message": "Error creating the car"})
    return NewCarResponse.from_orm(new_car)


@router.get("/cars/{plate}", response_model=NewCarResponse, status_code=200)
async def read_car(plate: str, db: AsyncSession = Depends(get_db),
                   admin: User = Depends(auth_service.get_current_admin)):
    car_repository = CarRepository(db)
    car = await car_repository.get_car_by_plate(plate)
    print(car)
    if car is None:
        return JSONResponse(status_code=404, content={"message": "Car not found"})
        # raise HTTPException(status_code=400, detail="Error creating the car")

    return car


@router.get("/cars", response_model=list[NewCarResponse], status_code=200)
async def read_cars(db: AsyncSession = Depends(get_db),
                    admin: User = Depends(auth_service.get_current_admin)):
    car_repository = CarRepository(db)
    return await car_repository.get_all_cars()


@router.get("/cars/{user_id}", response_model=list[NewCarResponse], status_code=200)
async def read_cars_by_user(user_id: int, db: AsyncSession = Depends(get_db),
                            admin: User = Depends(auth_service.get_current_admin)):
    car_repository = CarRepository(db)
    return await car_repository.get_cars_by_user(user_id)


@router.patch("/cars/{plate}", response_model=dict, status_code=200)
async def update_car(plate: str, car_update: CarUpdate, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
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
    car_repository = CarRepository(db)
    if not await car_repository.check_car_exists(plate):
        return JSONResponse(status_code=404, content={"message": "Car not found"})
    await car_repository.delete_car(plate)
    return JSONResponse(status_code=200, content={"message": "Car deleted successfully"})
