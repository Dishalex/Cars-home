# backend/src/services/auth.py
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # noqa
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.conf.config import config
from backend.src.database.db import get_db
from backend.src.entity.models import Blacklisted
from backend.src.repository import users as repository_users


class Auth:
    """Class handling authentication operations such as password hashing, JWT token creation, and token blacklisting."""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM

    def verify_password(self, plain_password: str, hashed_password: str):
        """
        Verify the given plain password against the hashed password.

        :param plain_password: Plain text password.
        :type plain_password: str
        :param hashed_password: Hashed password.
        :type hashed_password: str
        :return: True if the passwords match, False otherwise.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generate the hash for the given password.

        :param password: Plain text password.
        :type password: str
        :return: Hashed password.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create an access token.

        :param data: Payload data to be encoded in the token.
        :type data: dict
        :param expires_delta: Expiry time for the token.
        :type expires_delta: Optional[float]
        :return: Encoded access token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a refresh token.

        :param data: Payload data to be encoded in the token.
        :type data: dict
        :param expires_delta: Expiry time for the token.
        :type expires_delta: Optional[float]
        :return: Encoded refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode the refresh token and retrieve the email from the payload.

        :param refresh_token: Encoded refresh token.
        :type refresh_token: str
        :return: Email extracted from the token payload.
        :rtype: str
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    @staticmethod
    async def add_token_to_blacklist(user_id: int, token: str, db: AsyncSession = Depends(get_db)):
        """
        Add a token to the blacklist.

        :param user_id: User ID associated with the token.
        :type user_id: int
        :param token: Token to be blacklisted.
        :type token: str
        :param db: Async database session.
        """
        existing_token = select(Blacklisted).filter_by(token=token)
        existing_token = await db.execute(existing_token)
        existing_token = existing_token.scalar_one_or_none()
        if not existing_token:
            new_blacklisted_token = Blacklisted(user_id=user_id, token=token)
            db.add(new_blacklisted_token)
            await db.commit()

    @staticmethod
    async def is_token_blacklisted(token: str, db: AsyncSession = Depends(get_db)):
        """
        Check if a token is blacklisted.

        :param token: Token to be checked.
        :type token: str
        :param db: Async database session.
        :type db: AsyncSession
        :return: Blacklisted token record if found, None otherwise.
        :rtype: Blacklisted | None
        """
        stmt = select(Blacklisted).filter_by(token=token)
        blacklisted_token = await db.execute(stmt)
        blacklisted_token = blacklisted_token.scalar_one_or_none()
        return blacklisted_token

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        Get the current authenticated user.

        :param token: Encoded JWT token.
        :type token: str
        :param db: Async database session.
        :type db: AsyncSession
        :return: Current authenticated user.
        :rtype: User
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        if await self.is_token_blacklisted(token, db):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is blacklisted. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        if user.ban:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account has been banned.")
        return user


auth_service = Auth()
