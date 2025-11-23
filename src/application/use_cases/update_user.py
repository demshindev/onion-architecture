from typing import Optional
from uuid import UUID

from src.application.dto.user_dto import UserDTO
from src.domain.exceptions import UserNotFoundException, UserAlreadyExistsException
from src.infrastructure.database.unit_of_work import UnitOfWork


class UpdateUserUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, user_id: UUID, email: Optional[str] = None, username: Optional[str] = None, full_name: Optional[str] = None) -> UserDTO:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")

        if email and email != user.email:
            existing = await self.uow.users.get_by_email(email)
            if existing:
                raise UserAlreadyExistsException(f"User with email {email} already exists")

        if username and username != user.username:
            existing = await self.uow.users.get_by_username(username)
            if existing:
                raise UserAlreadyExistsException(f"User with username {username} already exists")

        user.update(email=email, username=username, full_name=full_name)
        updated = await self.uow.users.update(user)
        await self.uow.commit()
        return UserDTO.from_entity(updated)

