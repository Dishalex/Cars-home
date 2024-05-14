from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.entity.models import History, User, Car


async def get_history(offset: int, limit: int, user: User, db: AsyncSession) -> Sequence[Car]:
    # stmt = select(History).join(Car).join(User).where(User.id == user.id).limit(limit).offset(offset)
    # user_history = await db.execute(stmt)
    # user_history = user_history.scalars().all()
    # for history in user_history:
    #     history.car = history.car.plate
    print(user)
    stmt = select(Car)
    user_history = await db.execute(stmt)
    user_history = user_history.scalars().unique().all()
    print(user_history[0])
    return user_history
