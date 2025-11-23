from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Database:
    def __init__(self, database_url: str, echo: bool = False, pool_size: int = 10, max_overflow: int = 20, pool_pre_ping: bool = True):
        connect_args = {}
        if "mysql" in database_url:
            connect_args = {"connect_timeout": 10}
        
        self._engine: AsyncEngine = create_async_engine(
            database_url,
            echo=echo,
            pool_pre_ping=pool_pre_ping,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_recycle=3600,
            pool_reset_on_return="commit",
            connect_args=connect_args,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self) -> None:
        await self._engine.dispose()

    @property
    def session_factory(self) -> async_sessionmaker:
        return self._session_factory

