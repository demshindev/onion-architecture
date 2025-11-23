from uuid import UUID

from src.domain.exceptions import UserNotFoundException
from src.infrastructure.database.unit_of_work import UnitOfWork


class DeleteUserUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, user_id: UUID) -> bool:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")
        await self.uow.users.delete(user_id)
        await self.uow.commit()
        return True

