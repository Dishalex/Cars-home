from sqlalchemy import select, func, between, DateTime, null
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.entity.models import ParkingRate


async def get_latest_parking_rate_with_free_spaces(session: AsyncSession) -> ParkingRate:
    subquery = (
        select(func.max(ParkingRate.created_at))
        .filter(ParkingRate.number_free_spaces > 0)
        .scalar_subquery()
    )
    query = select(ParkingRate).filter(ParkingRate.created_at == subquery)
    result = await session.execute(query)
    return result.scalar_one_or_none()
