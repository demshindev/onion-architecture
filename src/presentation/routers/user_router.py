from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.application.dto.user_dto import UserDTO
from src.application.use_cases.create_user import CreateUserUseCase
from src.application.use_cases.delete_user import DeleteUserUseCase
from src.application.use_cases.get_all_users import GetAllUsersUseCase
from src.application.use_cases.get_user import GetUserUseCase
from src.application.use_cases.update_user import UpdateUserUseCase
from src.domain.exceptions import (
    DomainException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from src.infrastructure.constants import PaginationConstants
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.exceptions import DatabaseException
from src.infrastructure.logger import logger
from src.presentation.dependencies import get_unit_of_work
from src.presentation.schemas.pagination_schema import PaginatedResponse, PaginationMeta
from src.presentation.schemas.user_schema import (
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

router = APIRouter(prefix="/users", tags=["users"])


def _domain_exception_to_http(exc: DomainException) -> HTTPException:
    if isinstance(exc, UserNotFoundException):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, UserAlreadyExistsException):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


def _dto_to_response(dto: UserDTO) -> UserResponseSchema:
    return UserResponseSchema(
        id=dto.id,
        email=dto.email,
        username=dto.username,
        full_name=dto.full_name,
        is_active=dto.is_active,
        created_at=dto.created_at,
        updated_at=dto.updated_at
    )


@router.post("", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED, summary="Create a new user")
async def create_user(request: Request, user_data: UserCreateSchema, uow: UnitOfWork = Depends(get_unit_of_work)):
    req_id = getattr(request.state, "request_id", "N/A")
    logger.info(f"Creating user: {user_data.email}", extra={"request_id": req_id})
    
    try:
        use_case = CreateUserUseCase(uow)
        dto = await use_case.execute(email=user_data.email, username=user_data.username, full_name=user_data.full_name)
        logger.info(f"User created: {dto.id}", extra={"request_id": req_id})
        return _dto_to_response(dto)
    except DomainException as e:
        logger.warning(f"Domain error: {str(e)}", extra={"request_id": req_id})
        raise _domain_exception_to_http(e)
    except DatabaseException as e:
        logger.error(f"Database error: {str(e)}", extra={"request_id": req_id}, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")


@router.get("/{user_id}", response_model=UserResponseSchema, summary="Get user by ID")
async def get_user(request: Request, user_id: UUID, uow: UnitOfWork = Depends(get_unit_of_work)):
    req_id = getattr(request.state, "request_id", "N/A")
    logger.info(f"Getting user: {user_id}", extra={"request_id": req_id})
    
    try:
        use_case = GetUserUseCase(uow)
        dto = await use_case.execute(user_id)
        return _dto_to_response(dto)
    except DomainException as e:
        logger.warning(f"Domain error: {str(e)}", extra={"request_id": req_id})
        raise _domain_exception_to_http(e)
    except DatabaseException as e:
        logger.error(f"Database error: {str(e)}", extra={"request_id": req_id}, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")


@router.get("", response_model=PaginatedResponse[UserResponseSchema], summary="Get all users")
async def get_all_users(
    request: Request,
    page: int = Query(PaginationConstants.DEFAULT_PAGE, ge=PaginationConstants.MIN_PAGE),
    page_size: int = Query(PaginationConstants.DEFAULT_PAGE_SIZE, ge=PaginationConstants.MIN_PAGE_SIZE, le=PaginationConstants.MAX_PAGE_SIZE),
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    try:
        skip = (page - 1) * page_size
        use_case = GetAllUsersUseCase(uow)
        users, total = await use_case.execute(skip=skip, limit=page_size)
        
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
        
        return PaginatedResponse(items=[_dto_to_response(u) for u in users], meta=meta)
    except DatabaseException as e:
        req_id = getattr(request.state, "request_id", "N/A")
        logger.error(f"Database error: {str(e)}", extra={"request_id": req_id}, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")


@router.put("/{user_id}", response_model=UserResponseSchema, summary="Update user")
async def update_user(request: Request, user_id: UUID, user_data: UserUpdateSchema, uow: UnitOfWork = Depends(get_unit_of_work)):
    req_id = getattr(request.state, "request_id", "N/A")
    logger.info(f"Updating user: {user_id}", extra={"request_id": req_id})
    
    try:
        use_case = UpdateUserUseCase(uow)
        dto = await use_case.execute(user_id=user_id, email=user_data.email, username=user_data.username, full_name=user_data.full_name)
        logger.info(f"User updated: {user_id}", extra={"request_id": req_id})
        return _dto_to_response(dto)
    except DomainException as e:
        logger.warning(f"Domain error: {str(e)}", extra={"request_id": req_id})
        raise _domain_exception_to_http(e)
    except DatabaseException as e:
        logger.error(f"Database error: {str(e)}", extra={"request_id": req_id}, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
async def delete_user(request: Request, user_id: UUID, uow: UnitOfWork = Depends(get_unit_of_work)):
    req_id = getattr(request.state, "request_id", "N/A")
    logger.info(f"Deleting user: {user_id}", extra={"request_id": req_id})
    
    try:
        use_case = DeleteUserUseCase(uow)
        await use_case.execute(user_id)
        logger.info(f"User deleted: {user_id}", extra={"request_id": req_id})
    except DomainException as e:
        logger.warning(f"Domain error: {str(e)}", extra={"request_id": req_id})
        raise _domain_exception_to_http(e)
    except DatabaseException as e:
        logger.error(f"Database error: {str(e)}", extra={"request_id": req_id}, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")

