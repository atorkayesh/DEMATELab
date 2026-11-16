"""Generic response models for the DEMATELab API."""

from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel

from models.error_models import ErrorInfo

T = TypeVar("T")


class ApiResponseModel(BaseModel, Generic[T]):
    """Standard API response wrapper.

    Follows the normalized response structure:
    - success: Operation success status
    - message: Optional human-readable message
    - data: Response payload (typed)
    - metadata: Optional additional information (timing, pagination, etc.)
    - error: Public error details; `None` on success
    """

    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[ErrorInfo] = None
