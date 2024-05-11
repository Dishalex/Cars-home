from datetime import datetime, timedelta

from sqlalchemy import select, between, null, and_, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.entity.models import History, Car, ParkingRate
from typing import List, Sequence, Tuple
from backend.src.schemas.history_schema import HistoryUpdate


async def create_exit(find_plate: str, picture_id: int, session: AsyncSession):
    history_entries = await get_history_entries_with_null_exit_time(session)
    number_free_spaces = await update_parking_spaces(session)
    number_free_spaces +=1

    exit_time = datetime.now()
    car = await session.execute(select(Car).filter(Car.plate == find_plate))
    car_row = car.scalar_one_or_none()
    if car_row:
        for history in history_entries:
            if history.car_id == car_row.id:

                history.exit_time = exit_time
                history.number_free_spaces = number_free_spaces

                rate_per_hour, rate_per_day = get_parking_rates_for_date(history.entry_time)

                duration_hours = await calculate_parking_duration(history.entry_time, history.exit_time)

                if duration_hours > 24:
                    cost = await calculate_parking_cost(24, rate_per_day) + await calculate_parking_cost(
                        duration_hours - 24, rate_per_hour)
                else:
                    cost = await calculate_parking_cost(duration_hours, rate_per_hour)

                history.parking_time = duration_hours
                history.cost = cost

                car_row.credit -= cost
                session.add(car_row)

                if car_row.credit >= 0:
                    history.paid = True

                await session.commit()
                return history
    else:
        history_new = History(exit_time=exit_time, picture_id=picture_id, number_free_spaces=number_free_spaces)
        session.add(history_new)
        await session.commit()
        return history_new

    return None


async def create_entry(find_plate: str, picture_id: int, session: AsyncSession) -> History:
    entry_time = datetime.now()
    number_free_spaces = await update_parking_spaces(session)
    # number_free_spaces -= 1
    car = await session.execute(select(Car).filter(Car.plate == find_plate))
    car_row = car.unique().scalar_one_or_none()

    if car_row:
        car_id = car_row.id
    else:

        history_new = History(entry_time=entry_time, picture_id=picture_id, number_free_spaces=number_free_spaces)
        session.add(history_new)
        await session.commit()
        return history_new

    history_new = History(entry_time=entry_time, car_id=car_id, picture_id=picture_id,
                          number_free_spaces=number_free_spaces)
    session.add(history_new)
    await session.commit()

    return history_new


async def calculate_parking_duration(entry_time: datetime, exit_time: datetime) -> float:
    duration = exit_time - entry_time
    hours = duration / timedelta(hours=1)
    return hours


async def calculate_parking_cost(duration_hours: float, rate_per_hour: float) -> float:
    return duration_hours * rate_per_hour


async def get_parking_rates_for_date(entry_time: datetime, session: AsyncSession) -> Tuple[float, float]:
    rates = await session.execute(
        select(ParkingRate).filter(ParkingRate.created_at <= entry_time)
        .order_by(ParkingRate.created_at.desc()).limit(1)
    )
    rate_row = rates.scalar_one_or_none()
    if rate_row:
        return rate_row.rate_per_hour, rate_row.rate_per_day
    else:
        return ParkingRate.rate_per_hour.default.arg, ParkingRate.rate_per_day.default.arg


async def get_history_entries_with_null_exit_time(session: AsyncSession) -> Sequence[History]:
    stmt = select(History).filter(History.exit_time.is_(None))
    result = await session.execute(stmt)
    history_entries = result.scalars().all()
    return history_entries


async def get_history_entries_by_period(start_time: datetime, end_time: datetime, session: AsyncSession) -> Sequence[
    History]:
    query = select(History).filter(between(History.entry_time, start_time, end_time))
    result = await session.execute(query)
    history_entries = result.scalars().all()
    return history_entries


async def get_history_entries_with_null_car_id(session: AsyncSession) -> Sequence[History]:
    query = select(History).filter(History.car_id == null())
    result = await session.execute(query)
    history_entries = result.scalars().all()
    return history_entries


async def get_history_entries_with_null_paid(session: AsyncSession) -> Sequence[History]:
    query = select(History).filter(History.paid == False)
    result = await session.execute(query)
    history_entries = result.scalars().all()
    return history_entries


async def update_parking_spaces(session: AsyncSession):
    history_entries = await get_history_entries_with_null_exit_time(session)
    num_entries = len(history_entries)

    latest_parking_rate = await get_latest_parking_rate(session)
    latest_parking_rate_spaces = latest_parking_rate.number_of_spaces if latest_parking_rate else 0

    number_free_spaces = latest_parking_rate_spaces - num_entries

    if number_free_spaces == 0:
        number_free_spaces = 100

    return number_free_spaces


async def get_latest_parking_rate(session: AsyncSession):
    query = select(ParkingRate).order_by(desc(ParkingRate.created_at)).limit(1)
    result = await session.execute(query)
    parking_rate = result.scalar_one_or_none()
    return parking_rate


async def get_latest_parking_rate_with_free_spaces(session: AsyncSession):
    query = select(History).order_by(desc(History.created_at)).limit(1)
    result = await session.execute(query)
    latest_entry = result.scalar_one_or_none()
    if latest_entry:
        return latest_entry.number_free_spaces
    return None


async def update_paid(self, plate: str, history_update: HistoryUpdate):
    statement = select(History).where(
        and_(History.car.has(plate=plate), History.paid == False)
    )
    result = await self.db.execute(statement)
    history_entry = result.scalars().first()

    if history_entry is None:
        return None

    for var, value in history_update.dict(exclude_unset=True).items():
        setattr(history_entry, var, value)

    await self.db.commit()
    await self.db.refresh(history_entry)
    return history_entry


async def update_car_history(self, plate: str, history_update: HistoryUpdate):
    statement = select(History).where(
        and_(History.picture.has(find_plate=plate), History.car_id == null())
    )
    result = await self.db.execute(statement)
    history_entry = result.scalars().first()

    if history_entry is None:
        return None

    for var, value in history_update.dict(exclude_unset=True).items():
        setattr(history_entry, var, value)

    await self.db.commit()
    await self.db.refresh(history_entry)
    return history_entry


async def delete_history(self, plate: str):
    statement = delete(History).where(History.car.has(plate=plate))
    await self.db.execute(statement)
    await self.db.commit()
    return {"detail": "History deleted"}
