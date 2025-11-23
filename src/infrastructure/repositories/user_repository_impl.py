from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.exceptions import DatabaseException


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        try:
            model = UserModel(
                id=str(user.id),
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return self._model_to_entity(model)
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to create user: {str(e)}") from e

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            result = await self.session.execute(select(UserModel).where(UserModel.id == str(user_id)))
            model = result.scalar_one_or_none()
            return self._model_to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to get user by id: {str(e)}") from e

    async def get_by_email(self, email: str) -> Optional[User]:
        try:
            result = await self.session.execute(select(UserModel).where(UserModel.email == email.lower().strip()))
            model = result.scalar_one_or_none()
            return self._model_to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to get user by email: {str(e)}") from e

    async def get_by_username(self, username: str) -> Optional[User]:
        try:
            result = await self.session.execute(select(UserModel).where(UserModel.username == username.strip()))
            model = result.scalar_one_or_none()
            return self._model_to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to get user by username: {str(e)}") from e

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            result = await self.session.execute(
                select(UserModel).offset(skip).limit(limit).order_by(UserModel.created_at.desc())
            )
            models = result.scalars().all()
            return [self._model_to_entity(m) for m in models]
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to get all users: {str(e)}") from e

    async def count(self) -> int:
        try:
            from sqlalchemy import func
            result = await self.session.execute(select(func.count(UserModel.id)))
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to count users: {str(e)}") from e

    async def update(self, user: User) -> User:
        try:
            result = await self.session.execute(select(UserModel).where(UserModel.id == str(user.id)))
            model = result.scalar_one_or_none()
            if not model:
                return user

            model.email = user.email
            model.username = user.username
            model.full_name = user.full_name
            model.is_active = user.is_active
            model.updated_at = user.updated_at
            await self.session.flush()
            await self.session.refresh(model)
            return self._model_to_entity(model)
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to update user: {str(e)}") from e

    async def delete(self, user_id: UUID) -> bool:
        try:
            result = await self.session.execute(select(UserModel).where(UserModel.id == str(user_id)))
            model = result.scalar_one_or_none()
            if model:
                await self.session.delete(model)
                await self.session.flush()
                return True
            return False
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to delete user: {str(e)}") from e

    @staticmethod
    def _model_to_entity(model: UserModel | None) -> User | None:
        from uuid import UUID
        if model is None:
            return None
        try:
            return User(
                id=UUID(model.id),
                email=model.email,
                username=model.username,
                full_name=model.full_name,
                is_active=model.is_active,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
        except (ValueError, TypeError) as e:
            raise DatabaseException(f"Failed to convert model to entity: {str(e)}") from e

