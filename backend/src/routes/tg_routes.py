from typing import Sequence

from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from telegram.tg_schema import HistoryResponse  # TODO: move to backend.src.schemas
from backend.src.services.auth import auth_service
from backend.src.database.db import get_db
from backend.src.entity.models import User, History
from backend.src.repository import users as repositories_users, tg as repositories_tg
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


@router.get('/history', response_model=Sequence[HistoryResponse])
async def get_history(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, ge=10, le=100),
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)
) -> Sequence[History] | JSONResponse:
    history = await repositories_tg.get_history(offset, limit, user, db)
    if not history:
        return JSONResponse({'message': 'History is empty'}, status.HTTP_404_NOT_FOUND)
    return history
