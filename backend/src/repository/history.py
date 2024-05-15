from datetime import datetime, timedelta, time

from sqlalchemy import select, between, null, and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.src.entity.models import History, ParkingRate, Car
from typing import List, Sequence, Tuple
from backend.src.repository.car_repository import CarRepository
import csv

from backend.src.routes.notification import telegram_notification


async def create_exit(find_plate: str, picture_id: int, session: AsyncSession):
    history_entries = await get_history_entries_with_null_exit_time(session)
    number_free_spaces, rate_id = await update_parking_spaces(session)
    number_free_spaces += 1
    rate_id=int(rate_id)
    picture_id = int(picture_id)

    exit_time = datetime.now()
    car_repository = CarRepository(session)
    car_row = await car_repository.get_car_by_plate(find_plate)
    if car_row:
        for history in history_entries:
            if history.car_id == car_row.id:

                history.exit_time = exit_time
                history.number_free_spaces = number_free_spaces
                history.rate_id = rate_id

                rate_per_hour, rate_per_day = await get_parking_rates_for_date(history.entry_time, session)

                duration_hours = await calculate_parking_duration(history.entry_time, history.exit_time)

                if duration_hours > 24:
                    cost = await calculate_parking_cost(duration_hours, rate_per_day)
                else:
                    cost = await calculate_parking_cost(duration_hours, rate_per_hour)

                history.parking_time = duration_hours
                history.cost = cost

                car_row.credit -= cost
                session.add(car_row)

                if car_row.credit >= 0:
                    history.paid = True
                else:
                    await telegram_notification("limit", car_row)

                await session.commit()
                await session.refresh(history)
                return history
    else:
        history_new = History(
            exit_time=exit_time, picture_id=picture_id, number_free_spaces=number_free_spaces,rate_id=rate_id)
        session.add(history_new)
        await session.commit()
        await session.refresh(history_new)
        return history_new

    return None


async def create_entry(find_plate: str, picture_id: int, session: AsyncSession) -> History:
    entry_time = datetime.now()
    number_free_spaces,rate_id = await update_parking_spaces(session)
    number_free_spaces -= 1
    

    car_repository = CarRepository(session)
    car_row = await car_repository.get_car_by_plate(find_plate)
    picture_id = int(picture_id)
    if car_row:
        car_id = car_row.id
    else:

        history_new = History(entry_time=entry_time, picture_id=picture_id,
                              number_free_spaces=number_free_spaces, rate_id=rate_id,
                      exit_time=None)
        session.add(history_new)
        await session.commit()
        await session.refresh(history_new)
        return history_new

    history_new = History(entry_time=entry_time, car_id=car_id, picture_id=picture_id,
                          number_free_spaces=number_free_spaces, rate_id=rate_id,
                      exit_time=None)
    session.add(history_new)
    await session.commit()
    await session.refresh(history_new)
    return history_new


async def calculate_parking_duration(entry_time: datetime, exit_time: datetime) -> float:
    duration = exit_time - entry_time
    hours = duration / timedelta(hours=1)
    return round(hours, 2)


async def calculate_parking_cost(duration_hours: float, rate_per_hour: float) -> float:
    cost = round(duration_hours * rate_per_hour, 2)
    return cost


async def get_parking_rates_for_date(entry_time: datetime, session: AsyncSession) -> Tuple[float, float]:
    rates = await session.execute(
        select(ParkingRate).filter(ParkingRate.created_at <= entry_time)
        .order_by(ParkingRate.created_at.desc()).limit(1)
    )
    rate_row = rates.scalars().first()
    if rate_row:
        return rate_row.rate_per_hour, rate_row.rate_per_day
    else:
        default_rate_per_hour = ParkingRate.rate_per_hour.default.arg
        default_rate_per_day = ParkingRate.rate_per_day.default.arg
        return default_rate_per_hour, default_rate_per_day

async def get_history_entries_with_null_exit_time(session: AsyncSession) -> Sequence[History]:

    stmt = select(History).filter(
        or_(History.exit_time.is_(None), History.exit_time == func.now()))
    result = await session.execute(stmt)
    history_entries = result.unique().scalars().all()
    return history_entries


async def get_history_entries_by_period(start_time: datetime, end_time: datetime, session: AsyncSession) -> Sequence[History]:

    start_time = datetime.combine(start_time.date(), time.min)
    end_time = datetime.combine(end_time.date(), time.max)

    query = select(History).join(Car).filter(
        History.entry_time.between(start_time, end_time)
    )
    result = await session.execute(query)
    history_entries = result.unique().scalars().all()
    return history_entries


async def get_history_entries_by_period_car (start_time: datetime, end_time: datetime, car_id: int, session: AsyncSession) -> Sequence[History]:
    start_time = datetime.combine(start_time.date(), time.min)
    end_time = datetime.combine(end_time.date(), time.max)

    query = select(History).join(Car).filter(
        History.entry_time.between(start_time, end_time),
        History.car_id == car_id
    )
    result = await session.execute(query)
    history_entries = result.unique().scalars().all()
    return history_entries


#TODO Додати номер автомобіля за id автомобіля
    # async def get_history(offset: int, limit: int, user: User, db: AsyncSession) -> Sequence[History]:
    #     stmt = select(History).join(Car)
    #     user_history = await db.execute(stmt)
    #     user_history = user_history.scalars().all()
    #     for history in user_history:
    #         history.car = history.car.plate
    #     return user_history


from datetime import timedelta

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    return f"{days}d {hours}h {minutes}m"

async def save_history_to_csv(history_entries: Sequence[History], file_path: str):
    fieldnames = [
        'entry_time',
        'exit_time',
        'parking_time',
        'cost',
        'paid',
        'number_free_spaces',
        'plate'
    ]

    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in history_entries:
            parking_duration = timedelta(hours=entry.parking_time) if entry.parking_time is not None else None
            entry_dict = {
                'entry_time': entry.entry_time.strftime('%Y-%m-%d %H:%M') if entry.entry_time else None,
                'exit_time': entry.exit_time.strftime('%Y-%m-%d %H:%M') if entry.exit_time else None,
                'parking_time': format_timedelta(parking_duration) if parking_duration else None,
                'cost': f"{entry.cost:.2f}" if entry.cost is not None else None,
                'paid': entry.paid,
                'number_free_spaces': entry.number_free_spaces,
                'plate': entry.car.plate
            }
            writer.writerow(entry_dict)



async def get_history_entries_with_null_car_id(session: AsyncSession) -> Sequence[History]:
    query = select(History).filter(History.car_id == null())
    result = await session.execute(query)
    history_entries = result.unique().scalars().all()
    return history_entries


async def get_history_entries_with_null_paid(session: AsyncSession) -> Sequence[History]:
    query = select(History).filter(History.paid == False)
    result = await session.execute(query)
    history_entries = result.unique().scalars().all()
    return history_entries


async def update_parking_spaces(session: AsyncSession) -> Tuple[int, int]:
    history_entries = await get_history_entries_with_null_exit_time(session)
    num_entries = len(history_entries)

    latest_parking_rate = await get_latest_parking_rate(session)
    latest_parking_rate_spaces = latest_parking_rate.number_of_spaces if latest_parking_rate else 0

    number_free_spaces = latest_parking_rate_spaces - num_entries

    if number_free_spaces == 0:
        number_free_spaces = 100
    rate_id = latest_parking_rate.id if latest_parking_rate else 0
    return number_free_spaces, latest_parking_rate.id


async def get_latest_parking_rate(session: AsyncSession):
    query = select(ParkingRate).order_by(desc(ParkingRate.created_at)).limit(1)
    result = await session.execute(query)
    parking_rate = result.unique().scalar_one_or_none()
    return parking_rate


async def get_latest_parking_rate_with_free_spaces(session: AsyncSession):
    query = select(History).order_by(desc(History.created_at)).limit(1)
    result = await session.execute(query)
    latest_entry = result.unique().scalar_one_or_none()
    if latest_entry:
        return f"free spaces -  {latest_entry.number_free_spaces}"
    return "No data available"

async def update_paid_history( plate: str,  paid: bool, session: AsyncSession):
    statement = select(History).where(
        and_(History.car.has(plate=plate), History.paid == False)
    )
    result = await session.execute(statement)
    history_entry = result.unique().scalars().first()

    if history_entry is None:
        return None

    history_entry.paid = paid

    await session.commit()
    await session.refresh(history_entry)
    return history_entry


async def update_car_history( plate: str, car_id: int, session: AsyncSession):
    statement = select(History).where(
        and_(History.picture.has(find_plate=plate), History.car_id == null())
    )
    result = await session.execute(statement)
    history_entry = result.unique().scalars().first()

    if history_entry is None:
        return None

    history_entry.car_id = car_id

    await session.commit()
    await session.refresh(history_entry)
    return history_entry


