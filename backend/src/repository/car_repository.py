from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
# from backend.src.schemas.car_schema import CarCreate, CarUpdate
from backend.src.schemas.car_schemas import CarSchema, CarUpdate
from backend.src.entity.models import Car, User


class CarRepository:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def add_car(self, car_data: CarSchema):
        new_car = Car(**car_data.dict(exclude={'user_ids'}))
        self.db.add(new_car)

        # Асоціація автомобіля з користувачами
        for user_id in car_data.user_ids:
            user = await self.db.get(User, user_id)
            if user:
                new_car.users.append(user)
        
        await self.db.commit()
        await self.db.refresh(new_car)
        new_car.user_ids = car_data.user_ids
        return new_car

    # async def add_car(self, car_data: CarSchema):
    #     new_car = Car(**car_data.dict(exclude={'users'}))  # створення автомобіля без поля users
    #     self.db.add(new_car)
    #     await self.db.commit()
    #     await self.db.refresh(new_car)
    #
    #     # Додавання користувачів до автомобіля
    #     if car_data.users:
    #         user_query = select(User).where(User.id.in_(car_data.users))
    #         users = await self.db.scalars(user_query).all()
    #         for user in users:
    #             new_car.users.append(user)
    #         await self.db.commit()
    #
    #     return new_car


    async def get_car_by_plate(self, plate: str):
        result = await self.db.execute(select(Car).where(Car.plate == plate))
        car = result.scalars().first()
        # car.history = car.history if car.history is not None else []
        return car

    async def get_all_cars(self):
        result = await self.db.execute(
            select(Car).options(selectinload(Car.users))
        )
        cars = result.scalars().unique().all()
        # TODO список користувачів до кожного автомобіля 
        return cars

    async def get_cars_by_user(self, user_id: int):
        result = await self.db.execute(
            select(Car).options(selectinload(Car.users)).join(Car.users).where(User.id == user_id)
        )
        cars = result.scalars().unique().all()
        return cars

    async def update_car(self, plate: str, car_update: CarUpdate):

        statement = select(Car).where(Car.plate == plate)
        result = await self.db.execute(statement)
        car = result.scalars().first()
        if car is None:
            return None
        for var, value in car_update.dict(exclude_unset=True).items():
            setattr(car, var, value)
        await self.db.commit()
        await self.db.refresh(car)
        return car


    async def delete_car(self, plate: str):
        statement = delete(Car).where(Car.plate == plate)
        await self.db.execute(statement)
        await self.db.commit()
        return {"detail": "Car deleted"}

    async def check_car_exists(self, plate: str):
        result = await self.db.execute(select(Car).where(Car.plate == plate))
        return result.scalars().first() is not None

