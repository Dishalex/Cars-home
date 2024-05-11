from typing import Type

from sqlalchemy import select, func, update, delete, between, DateTime, null
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src import ParkingRate
from backend.src.entity.models import ParkingRate
from backend.src.schemas.parking_schema import ParkingRateSchema, NewParkingRateSchema, ParkingRateUpdate


async def create_rate(session: AsyncSession, rate_data: NewParkingRateSchema) -> ParkingRate:
    new_rate = ParkingRate(**rate_data.dict())
    session.add(new_rate)
    await session.commit()
    await session.refresh(new_rate)
    return new_rate


async def update_rate(session: AsyncSession, rate_id: int, rate_data: ParkingRateUpdate) -> ParkingRate | None:
    statement = select(ParkingRate).where(ParkingRate.id == rate_id)
    result = await session.execute(statement)
    rate = result.unique().scalar_one_or_none()
    if rate is None:
        return None
    for var, value in rate_data.dict(exclude_unset=True).items():
        setattr(rate, var, value)
    session.add(rate)
    await session.commit()
    return rate


# async def get_latest_parking_rate_with_free_spaces(session: AsyncSession) -> ParkingRate:
#     subquery = (
#         select(func.max(ParkingRate.created_at))
#         .filter(ParkingRate.number_free_spaces > 0)
#         .scalar_subquery()
#     )
#     query = select(ParkingRate).filter(ParkingRate.created_at == subquery)
#     result = await session.execute(query)
#     return result.scalar_one_or_none()
