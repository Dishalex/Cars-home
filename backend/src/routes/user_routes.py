# backend/src/routes/user_routes.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database.db import get_db
from backend.src.entity.models import User, Role
from backend.src.repository import users as repositories_users
from backend.src.schemas.car_schemas import NewCarResponse
from backend.src.schemas.user_schema import UserResponse, UserUpdate, AnotherUsers
from backend.src.services.auth import auth_service
from backend.src.repository.car_repository import CarRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to retrieve the information of the currently authenticated user.

    :param user: Current authenticated user (dependency injection).
    :type user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The information of the currently authenticated user.
    :rtype: UserResponse
    """
    return user


@router.get("/{username}", response_model=AnotherUsers)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to retrieve the profile of a user.

    :param user_id: ID of the user to retrieve the profile.
    :type user_id: int
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The profile of the user.
    :rtype: AnotherUsers
    """
    user_info = await repositories_users.get_user_by_userid(user_id, db)

    if not user_info:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "User not found."})

    return user_info


@router.patch("/me", response_model=UserResponse)
async def update_own_profile(
        user_update: UserUpdate,
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to update the profile of the currently authenticated user.

    :param user_update: UserUpdate instance containing the updated user information.
    :type user_update: UserUpdate
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The updated user information.
    :rtype: UserResponse
    """
    updated_user = await repositories_users.update_user(user.email, user_update, db)

    return updated_user


@router.patch("/admin/{username}/ban")
async def ban_user(
        username: str,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to ban a user by the admin.

    :param username: Username of the user to be banned.
    :type username: str
    :param current_user: Current authenticated user (dependency injection).
    :type current_user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :raises HTTPException: If the current user is not an admin or if the user to be banned is not found.
    :return: A message indicating the success of the operation.
    :rtype: dict
    """
    if not current_user.role == Role.admin:
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="You don't have permission to perform this action.",
        # )
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                            content={"message": "You don't have permission to perform this action."})

    await repositories_users.ban_user(username, db)
    return {"message": f"{username} has been banned."}


@router.get("/cars/{user_id}", response_model=list[NewCarResponse], status_code=200)
async def read_cars_by_user(user_id: int, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    if current_user.role != Role.admin and current_user.id != user_id:
        return JSONResponse(status_code=400, content={"message": "Not authorized to access this resource"})
    car_repository = CarRepository(db)
    cars = await car_repository.get_cars_by_user(user_id)
    if isinstance(cars, dict) and cars.get("error"):
        return JSONResponse(status_code=404, content={"message": cars["error"]})
    return cars

