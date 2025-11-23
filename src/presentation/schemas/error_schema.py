from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str | List[ErrorDetail] | Dict[str, Any]
    error_code: Optional[str] = None
    request_id: Optional[str] = None

