from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.exceptions import DatabaseException, DatabaseTransactionException
from src.infrastructure.logger import logger


class UnitOfWork(ABC):
    users: UserRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession, users: UserRepository) -> None:
        self.session = session
        self.users = users

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> bool:
        if exc_type is not None:
            try:
                await self.rollback()
            except Exception as e:
                logger.error(f"Rollback error in __aexit__: {str(e)}", exc_info=True)
        return False

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except SQLAlchemyError as e:
            try:
                await self.rollback()
            except Exception:
                pass
            logger.error(f"Commit error: {str(e)}", exc_info=True)
            raise DatabaseTransactionException(f"Failed to commit transaction: {str(e)}") from e

    async def rollback(self) -> None:
        try:
            await self.session.rollback()
        except SQLAlchemyError as e:
            logger.error(f"Rollback error: {str(e)}", exc_info=True)
            raise DatabaseTransactionException(f"Failed to rollback transaction: {str(e)}") from e
