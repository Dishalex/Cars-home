import random
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.entity.models import Picture


async def get_random_picture_info(session: AsyncSession) -> Tuple[str, int]:
    query = select(Picture)
    result = await session.execute(query)
    pictures = result.scalars().all()
    random_picture = random.choice(pictures)
    return random_picture.find_plate, random_picture.id
