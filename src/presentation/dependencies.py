from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.base import Database
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork, UnitOfWork
from src.infrastructure.repositories.user_repository_impl import SQLAlchemyUserRepository
from src.infrastructure.config import settings

_db: Database | None = None


def get_database() -> Database:
    global _db
    if _db is None:
        _db = Database(
            database_url=settings.database_url,
            echo=settings.debug,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=settings.database_pool_pre_ping,
        )
    return _db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_database().get_session():
        yield session


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return SQLAlchemyUserRepository(session)


async def get_unit_of_work(session: AsyncSession = Depends(get_db_session)) -> AsyncGenerator[UnitOfWork, None]:
    repo = SQLAlchemyUserRepository(session)
    uow = SQLAlchemyUnitOfWork(session, repo)
    async with uow:
        yield uow

