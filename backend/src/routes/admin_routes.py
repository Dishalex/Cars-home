from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from backend.src.schemas.car_schema import CarCreate, CarUpdate, CarResponse, SimpleResponse
from backend.src.repository.car_repository import CarRepository
from backend.src.database.db import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/cars", response_model=CarResponse, status_code=201)
async def add_car(car: CarCreate, db: AsyncSession = Depends(get_db)):
    car_repository = CarRepository(db)
    return await car_repository.add_car(car)

@router.get("/cars", response_model=list[CarResponse], status_code=200)
async def read_cars(db: AsyncSession = Depends(get_db)):
    car_repository = CarRepository(db)
    return await car_repository.get_all_cars()

@router.get("/cars/{user_id}", response_model=list[CarResponse], status_code=200)
async def read_cars_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    car_repository = CarRepository(db)
    return await car_repository.get_cars_by_user(user_id)


@router.put("/cars/{plate}", response_model=SimpleResponse, status_code=200)
async def update_car(plate: str, car_update: CarUpdate, db: AsyncSession = Depends(get_db)):
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


@router.delete("/cars/{plate}", response_class=JSONResponse)
async def delete_car(plate: str, db: AsyncSession = Depends(get_db)):
    car_repository = CarRepository(db)
    if not await car_repository.check_car_exists(plate):
        return JSONResponse(status_code=404, content={"message": "Car not found"})
    await car_repository.delete_car(plate)
    return JSONResponse(status_code=200, content={"message": "Car deleted successfully"})

