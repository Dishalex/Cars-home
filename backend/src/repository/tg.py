from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.entity.models import History, User, Car, user_car_association


async def get_history(offset: int, limit: int, user: User, db: AsyncSession) -> Sequence[History]:
    stmt = select(History).join(Car).join(User).where(User.id == user.id).limit(limit).offset(offset)
    user_history = await db.execute(stmt)
    user_history = user_history.scalars().all()
    for history in user_history:
        history.car = history.car.plate
    return user_history
