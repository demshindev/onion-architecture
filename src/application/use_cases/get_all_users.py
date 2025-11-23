from typing import List, Tuple

from src.application.dto.user_dto import UserDTO
from src.infrastructure.database.unit_of_work import UnitOfWork


class GetAllUsersUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, skip: int = 0, limit: int = 100) -> Tuple[List[UserDTO], int]:
        users = await self.uow.users.get_all(skip=skip, limit=limit)
        total = await self.uow.users.count()
        return [UserDTO.from_entity(u) for u in users], total

