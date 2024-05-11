# backend/src/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from backend.src.database.db import get_db
from backend.src.entity.models import User
from backend.src.repository import users as repositories_users
from backend.src.schemas.user_schema import UserSchema, TokenSchema, UserResponse
from backend.src.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()

# Налаштування логера
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    try:
        exist_user = await repositories_users.get_user_by_email(body.email, db)
        if exist_user:
            logger.error(f"Attempt to register with existing user: {body.full_name}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

        body.password = auth_service.get_password_hash(body.password)
        new_user = await repositories_users.create_user(body, db)
        logger.info(f"New user registered successfully: {body.full_name}")
        return new_user
    except Exception as e:
        logger.exception("Failed to register a new user")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Endpoint for user login.

    :param body: OAuth2PasswordRequestForm instance containing username and password.
    :type body: OAuth2PasswordRequestForm
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: Access token and refresh token.
    :rtype: TokenSchema
    :raises HTTPException: If the provided username is invalid or the password is incorrect.
    """
    user = await repositories_users.get_user_by_number(body.username, db)
    if user is None:
        user = await repositories_users.get_user_by_email(body.username, db)
    if user is None or not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # if not auth_service.verify_password(body.password, user.password):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if user.ban:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You were banned by an administrator")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh, db)
    return {"access_token": access_token, "refresh_token": refresh, "token_type": "bearer", }


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to refresh an access token using a refresh token.

    :param credentials: HTTPAuthorizationCredentials instance containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: New access token and refresh token.
    :rtype: TokenSchema
    :raises HTTPException: If the provided refresh token is invalid.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh, db)
    return {"access_token": access_token, "refresh_token": refresh, "token_type": "bearer", }


@router.post("/logout")
async def logout(user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to log out a user by adding their refresh token to the blacklist.

    :param user: The current authenticated user (dependency injection).
    :type user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: A message indicating successful logout.
    :rtype: dict
    """
    await auth_service.add_token_to_blacklist(user.id, user.refresh_token, db)

    return {"message": "Logout successful."}

