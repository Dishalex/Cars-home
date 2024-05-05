import contextlib
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.src import config


class DatabaseSessionManager:
    """
    Class responsible for managing the database session using `sqlalchemy.ext.asyncio.AsyncSession`.

    :param url: The URL for the PostgreSQL database.
    :type url: str
    """

    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=self._engine,
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Context manager method to acquire and yield an asynchronous database session.
        Handles rollback on exception and ensures session closure.

        :return: An asynchronous database session.
        :rtype: AsyncSession
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronously gets the database session as an async generator yielding an AsyncSession.
    """
    async with sessionmanager.session() as session:  # noqa
        yield session
