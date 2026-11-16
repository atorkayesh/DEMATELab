"""Error models: the public error block of a response and a packaged error."""

from typing import Any, List, Optional

from pydantic import BaseModel


class FieldError(BaseModel):
    """One invalid request field."""

    field: str
    message: str


class ErrorInfo(BaseModel):
    """Public error details returned in `ApiResponseModel.error`."""

    code: str
    fields: Optional[List[FieldError]] = None


class PresentedError(BaseModel):
    """An exception turned into everything a response needs. Never holds internal details."""

    status_code: int
    message: str
    error: ErrorInfo
    data: Optional[Any] = None
