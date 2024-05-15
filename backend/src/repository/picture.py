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


async def create_picture(session: AsyncSession, find_plate: str, url: str, cloudinary_public_id: str) -> Picture:
    picture = Picture(find_plate=find_plate, url=url, cloudinary_public_id=cloudinary_public_id)
    session.add(picture)
    await session.commit()
    await session.refresh(picture)
    return picture
