from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database.db import get_db
from backend.src.entity.models import User
from backend.src.repository import users as repositories_users
from backend.src.schemas.user_schema import UserResponse

router = APIRouter(prefix='/telegram', tags=['telegram'])


@router.get('/user/{phone_number}', response_model=UserResponse)
async def get_user(
        phone_number: str,
        db: AsyncSession = Depends(get_db)
) -> User | JSONResponse:
    user = await repositories_users.get_user_by_number(phone_number, db)
    if not user:
        return JSONResponse({'message': 'User not found'}, status.HTTP_404_NOT_FOUND)
    return user
