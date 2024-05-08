# backend/src/repository/users.py
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database.db import get_db
from backend.src.entity.models import User, Picture, Role
from backend.src.schemas.user_schema import UserSchema, UserUpdate
from backend.src.services import auth


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a user from the database based on the email.

    :param email: Email of the user to be retrieved.
    :type email: str
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The retrieved user or None if not found.
    :rtype: User or None
    """
    stmt = select(User).where(User.email == email)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Create a new user in the database.

    :param body: UserSchema instance containing user data.
    :type body: UserSchema
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The created user.
    :rtype: User
    """

    is_first_user = await check_is_first_user(db)
    if is_first_user:
        new_user = User(**body.model_dump(), role=Role.admin)
    else:
        new_user = User(**body.model_dump())

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def check_is_first_user(db: AsyncSession):
    """
    Check if the database has any users.

    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: True if the database has no users, False otherwise.
    :rtype: bool
    """
    stmt = select(User).limit(1)
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none() is None


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Update the refresh token for a user in the database.

    :param user: User instance to update.
    :type user: User
    :param token: New refresh token or None to clear the token.
    :type token: str or None
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    """
    user.refresh_token = token
    await db.commit()


async def get_user_by_username(full_name: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a user from the database based on the full name.

    :param full_name: Full name of the user to be retrieved.
    :type full_name: str
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The retrieved user or None if not found.
    :rtype: User or None
    """
    stmt = select(User).filter_by(full_name=full_name)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()
    return user


async def update_user(email: str, user_update: UserUpdate, db: AsyncSession):
    """
    Update user information in the database.

    :param email: Email of the user to be updated.
    :type email: str
    :param user_update: UserUpdate instance containing updated user data.
    :type user_update: UserUpdate
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The updated user instance or None if the user does not exist.
    :rtype: User or None
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()

    if user:
        for field, value in user_update.__dict__.items():
            if field == 'password':
                setattr(user, field, auth.auth_service.get_password_hash(value))
            else:
                setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user
    else:
        return None


async def ban_user(username: str, db: AsyncSession):
    """
    Ban a user by updating the 'ban' attribute in the database.

    :param username: Full name of the user to be banned.
    :type username: str
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: True if the user is successfully banned, False otherwise.
    :rtype: bool
    """
    stmt = select(User).filter_by(full_name=username)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()
    if user:
        user.ban = True
        await db.commit()
        return True
    else:
        return False
