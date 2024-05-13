from typing import Type

from sqlalchemy import select, func, update, delete, between, DateTime, null
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src import ParkingRate
from backend.src.entity.models import ParkingRate
from backend.src.schemas.parking_schema import ParkingRateSchema, NewParkingRateSchema, ParkingRateUpdate


async def create_rate(session: AsyncSession, rate_data: ParkingRateSchema) -> ParkingRate:
    new_rate = ParkingRate(**rate_data.dict())
    session.add(new_rate)
    await session.commit()
    await session.refresh(new_rate)
    return new_rate

#
# async def update_rate(session: AsyncSession, rate_id: int, rate_data: ParkingRateUpdate) -> ParkingRate | None:
#     statement = select(ParkingRate).where(ParkingRate.id == rate_id)
#     result = await session.execute(statement)
#     rate = result.unique().scalar_one_or_none()
#     if rate is None:
#         return None
#     for var, value in rate_data.dict(exclude_unset=True).items():
#         setattr(rate, var, value)
#     session.add(rate)
#     await session.commit()
#     return rate


async def get_default_rate_values(session: AsyncSession):
    latest_rate = await session.execute(
        select(ParkingRate)
        .order_by(ParkingRate.created_at.desc())
        .limit(1)
    )
    latest_rate = latest_rate.scalars().first()
    return latest_rate


async def create_or_update_rate(session: AsyncSession, rate_data: NewParkingRateSchema) -> ParkingRate:
    latest_rate = await session.execute(
        select(ParkingRate).order_by(ParkingRate.created_at.desc()).limit(1)
    )
    latest_rate = latest_rate.scalars().first()

    new_rate_data = {
        "rate_per_hour": rate_data.rate_per_hour if rate_data.rate_per_hour is not None else (latest_rate.rate_per_hour if latest_rate else 10.0),
        "rate_per_day": rate_data.rate_per_day if rate_data.rate_per_day is not None else (latest_rate.rate_per_day if latest_rate else 5.0),
        "number_of_spaces": rate_data.number_of_spaces if rate_data.number_of_spaces is not None else (latest_rate.number_of_spaces if latest_rate else 100),
    }

    new_rate = ParkingRate(**new_rate_data)
    session.add(new_rate)
    await session.commit()
    await session.refresh(new_rate)
    return new_rate


# async def get_latest_parking_rate_with_free_spaces(session: AsyncSession) -> ParkingRate:
#     subquery = (
#         select(func.max(ParkingRate.created_at))
#         .filter(ParkingRate.number_free_spaces > 0)
#         .scalar_subquery()
#     )
#     query = select(ParkingRate).filter(ParkingRate.created_at == subquery)
#     result = await session.execute(query)
#     return result.scalar_one_or_none()
