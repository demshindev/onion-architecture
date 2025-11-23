from uuid import UUID
from src.domain.entities.user import User
from src.infrastructure.database.models.user_model import UserModel


class UserMapper:
    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=UUID(model.id),
            email=model.email,
            username=model.username,
            full_name=model.full_name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

