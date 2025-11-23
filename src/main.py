import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.exceptions import DomainException
from src.infrastructure.config import settings
from src.infrastructure.exceptions import DatabaseException
from src.infrastructure.logger import logger
from src.presentation.dependencies import get_database
from src.presentation.middleware.error_handler import (
    database_exception_handler,
    domain_exception_handler,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from src.presentation.middleware.request_id import RequestIDMiddleware
from src.presentation.routers.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    db = get_database()
    try:
        await db.create_tables()
        logger.info("Tables initialized")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise
    yield
    logger.info("Application shutdown")
    await db.close()


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(user_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/health", tags=["health"])
async def health():
    from sqlalchemy import text
    db = get_database()
    try:
        async for session in db.get_session():
            await session.execute(text("SELECT 1"))
            break
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {"status": "error", "database": "disconnected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

