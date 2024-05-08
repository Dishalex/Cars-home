from datetime import datetime, timezone
from sqlalchemy import select, Integer, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..entity.models import User, History
from typing import List

async def create_history_entry(car_id: int, user_id: int, session: AsyncSession) -> History:
    entry_time = datetime.now(timezone.utc)
    history = History(entry_time=entry_time, car_id=car_id, user_id=user_id)
    session.add(history)
    await session.commit()
    return history

async def update_history_exit_time(history_id: int, session: AsyncSession) -> History:
    history = await read_history_by_id(history_id, session)
    if history:
        history.exit_time = datetime.now(timezone.utc)
        await session.commit()
    return history

async def calculate_parking_duration(entry_time: datetime, exit_time: datetime) -> float:
    duration = exit_time - entry_time
    return duration.total_seconds() / 3600 

async def calculate_parking_cost(duration_hours: float, rate_per_hour: float) -> float:
    return duration_hours * rate_per_hour

async def create_history(rate_id: int, body: History, user: User, session: AsyncSession) -> History:
    history = History(**body.model_dump(), rate_id=rate_id, user_id=user.id)
    session.add(history)
    await session.commit()
    await session.refresh(history)
    return history

async def read_histories(offset: int, limit: int, session: AsyncSession) -> List[History]:
    stmt = select(History).offset(offset).limit(limit)
    histories = await session.execute(stmt)
    return histories.scalars()

async def read_history_by_id(history_id: int, session: AsyncSession) -> History | None:
    stmt = select(History).filter(History.id == history_id)
    history = await session.execute(stmt)
    return history.scalar()

async def update_history(history_id: int, body: History, session: AsyncSession) -> History | None:
    history = await read_history_by_id(history_id, session)
    if history:
        for key, value in body.model_dump().items():
            if hasattr(history, key) and value is not None:
                setattr(history, key, value)
        await session.commit()
    return history

async def delete_history(history_id: int, session: AsyncSession) -> History | None:
    history = await read_history_by_id(history_id, session)
    if history:
        session.delete(history)
        await session.commit()
    return history
