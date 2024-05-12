from fastapi import HTTPException
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
# from backend.src.schemas.car_schema import CarCreate, CarUpdate
from backend.src.schemas.car_schemas import CarSchema, CarUpdate
from backend.src.entity.models import Car, User, user_car_association


class CarRepository:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def add_car(self, car_data: CarSchema):
        new_car = Car(**car_data.dict(exclude={'user_ids'}))

        # Перевірка, чи новий номерний знак вже існує в базі
        existing_car = await self.db.execute(select(Car).filter(Car.plate == car_data.plate))
        existing_car = existing_car.scalars().first()
        if existing_car:
            return {'error': f'The plate {car_data.plate} is already in use'}

        self.db.add(new_car)

        # Асоціація автомобіля з користувачами
        for user_id in car_data.user_ids:
            user = await self.db.get(User, user_id)
            if not user:
                await self.db.rollback()
                return {'error': f'User with id {user_id} does not exist'}
            new_car.users.append(user)
        
        await self.db.commit()
        await self.db.refresh(new_car)
        new_car.user_ids = car_data.user_ids
        return new_car

    async def get_car_by_plate(self, plate: str):
        result = await self.db.execute(
            select(Car).options(selectinload(Car.users)).where(Car.plate == plate)
        )
        car = result.scalars().first()
        if car:
            car.user_ids = [user.id for user in car.users]
        # car.history = car.history if car.history is not None else []
        return car

    async def get_all_cars(self):
        result = await self.db.execute(
            select(Car).options(selectinload(Car.users))
        )
        cars = result.scalars().unique().all()
        if cars:
            for car in cars:
                car.user_ids = [user.id for user in car.users]
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

        # Перевірка, чи новий номерний знак вже існує в базі
        existing_car = await self.db.execute(select(Car).filter(Car.plate == car_update.plate))
        existing_car = existing_car.scalars().first()
        if existing_car and existing_car.plate != plate:
            return {'error': f'The plate {car_update.plate} is already in use'}

        # Асоціація автомобіля з користувачами
        car.users.clear() # очищення списку користувачів
        for user_id in car_update.user_ids:
            user = await self.db.get(User, user_id)
            if not user:
                await self.db.rollback()
                return {'error': f'User with id {user_id} does not exist'}
            car.users.append(user)
        for var, value in car_update.dict(exclude_unset=True).items():
            setattr(car, var, value)
        await self.db.commit()
        await self.db.refresh(car)
        car.user_ids = car_update.user_ids
        return car

    async def delete_car(self, plate: str):
        car = await self.db.execute(select(Car).where(Car.plate == plate))
        car = car.scalars().first()
        if car is None:
            return {"detail": "Car not found"}

        # Видалення зв'язків з користувачами
        await self.db.execute(delete(user_car_association).where(user_car_association.c.car_id == car.id))

        await self.db.delete(car)
        await self.db.commit()
        return {"detail": "Car deleted successfully"}

    async def check_car_exists(self, plate: str):
        result = await self.db.execute(select(Car).where(Car.plate == plate))
        return result.scalars().first() is not None

