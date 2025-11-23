from uuid import UUID

from src.application.dto.user_dto import UserDTO
from src.domain.exceptions import UserNotFoundException
from src.infrastructure.database.unit_of_work import UnitOfWork


class GetUserUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, user_id: UUID) -> UserDTO:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")
        return UserDTO.from_entity(user)

