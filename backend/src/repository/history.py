from datetime import datetime, timezone


from sqlalchemy import select, func, between, null
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.entity.models import History, Car, ParkingRate
from typing import List, Sequence, Tuple


async def find_history_exit_time(find_plate: str, picture_id: int, session: AsyncSession) -> History:
    history_entries = await get_history_entries_with_null_exit_time(session)
    found_entry = False
    car = await session.execute(select(Car).filter(Car.plate == find_plate))
    car_row = car.scalar_one_or_none()

    if car_row:
        car_id = car_row.id
        found_entry = False

        for history in history_entries:
            if history.car_id == car_id:
                found_entry = True
                history.exit_time = datetime.now()

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
                await update_parking_spaces(session)

                return history

    if not found_entry:
        history = await create_history_entry(find_plate, picture_id, session)
        return history


async def calculate_parking_duration(entry_time: datetime, exit_time: datetime) -> float:
    duration = exit_time - entry_time
    return duration / 3600.0


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


async def create_history_entry(find_plate: str, picture_id: int, session: AsyncSession) -> History:
    entry_time = datetime.now()

    car = await session.execute(select(Car).filter(Car.plate == find_plate))
    car_row = car.scalar_one_or_none()

    if car_row:
        car_id = car_row.id
    else:

        history_new = History(entry_time=entry_time, picture_id=picture_id)
        session.add(history_new)
        await session.commit()
        return history_new

    history_new = History(entry_time=entry_time, car_id=car_id, picture_id=picture_id)
    session.add(history_new)
    await session.commit()

    await update_parking_spaces(session)

    return history_new


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

    parking_rate = await session.execute(select(ParkingRate))
    parking_rate_row = parking_rate.scalar_one_or_none()

    if parking_rate_row:
        parking_rate_row.number_free_spaces = parking_rate_row.number_of_spaces - num_entries
        session.add(parking_rate_row)
        await session.commit()
