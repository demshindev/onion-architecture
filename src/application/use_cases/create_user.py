from typing import Optional

from src.application.dto.user_dto import UserDTO
from src.domain.entities.user import User
from src.domain.exceptions import UserAlreadyExistsException
from src.infrastructure.database.unit_of_work import UnitOfWork


class CreateUserUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, email: str, username: str, full_name: Optional[str] = None) -> UserDTO:
        existing = await self.uow.users.get_by_email(email)
        if existing:
            raise UserAlreadyExistsException(f"User with email {email} already exists")

        existing = await self.uow.users.get_by_username(username)
        if existing:
            raise UserAlreadyExistsException(f"User with username {username} already exists")

        user = User.create(email=email, username=username, full_name=full_name)
        created = await self.uow.users.create(user)
        await self.uow.commit()
        return UserDTO.from_entity(created)

