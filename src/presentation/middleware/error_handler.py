from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.exceptions import (
    DomainException,
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidEmailException,
    InvalidUsernameException,
)
from src.infrastructure.exceptions import DatabaseException
from src.infrastructure.logger import logger


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    req_id = getattr(request.state, "request_id", None)
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "DOMAIN_ERROR"
    
    if isinstance(exc, UserNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
        error_code = "USER_NOT_FOUND"
    elif isinstance(exc, UserAlreadyExistsException):
        status_code = status.HTTP_409_CONFLICT
        error_code = "USER_ALREADY_EXISTS"
    elif isinstance(exc, (InvalidEmailException, InvalidUsernameException)):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        error_code = "VALIDATION_ERROR"
    
    logger.warning(f"Domain exception: {error_code} - {str(exc)}", extra={"request_id": req_id, "error_code": error_code})
    
    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc), "error_code": error_code, "request_id": req_id},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    req_id = getattr(request.state, "request_id", None)
    logger.warning(f"Validation error: {exc.errors()}", extra={"request_id": req_id})
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "error_code": "VALIDATION_ERROR", "request_id": req_id},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    req_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": "HTTP_ERROR", "request_id": req_id},
    )


async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    req_id = getattr(request.state, "request_id", None)
    logger.error(f"Database exception: {str(exc)}", extra={"request_id": req_id}, exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred", "error_code": "DATABASE_ERROR", "request_id": req_id},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    req_id = getattr(request.state, "request_id", None)
    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}", extra={"request_id": req_id}, exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR", "request_id": req_id},
    )

