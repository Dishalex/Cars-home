from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from backend.src.schemas.car_schema import CarCreate, CarUpdate
from backend.src.entity.models import Car, User


class CarRepository:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def add_car(self, car_data: CarCreate):
        new_car = Car(**car_data.dict())
        self.db.add(new_car)
        await self.db.commit()
        await self.db.refresh(new_car)
        return new_car

    async def get_all_cars(self):
        result = await self.db.execute(
            select(Car).options(selectinload(Car.users))
        )
        cars = result.scalars().unique().all()
        return cars

    async def get_cars_by_user(self, user_id: int):
        result = await self.db.execute(
            select(Car).options(selectinload(Car.users)).join(Car.users).where(User.id == user_id)
        )
        cars = result.scalars().unique().all()
        return cars

    async def update_car(self, plate: str, car_update: CarUpdate):
        async with self.db.begin() as transaction:
            statement = select(Car).where(Car.plate == plate)
            result = await self.db.execute(statement)
            car = result.scalars().first()
            if car is None:
                return None
            for var, value in car_update.dict(exclude_unset=True).items():
                setattr(car, var, value)
            await transaction.commit()
            return car
    async def delete_car(self, plate: str):
        statement = delete(Car).where(Car.plate == plate)
        await self.db.execute(statement)
        await self.db.commit()
        return {"detail": "Car deleted"}

    async def check_car_exists(self, plate: str):
        result = await self.db.execute(select(Car).where(Car.plate == plate))
        return result.scalars().first() is not None

