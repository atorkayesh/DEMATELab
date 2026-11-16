"""
Error presentation.

`ErrorPresenter` turns any exception into a `PresentedError` that is safe to return, and logs the
internal details server-side. HTTP handlers and streaming code both use it.
"""

import logging
from http import HTTPStatus
from typing import List, Optional

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from errors.app_error import AppError
from models.error_models import ErrorInfo, FieldError, PresentedError

logger = logging.getLogger(__name__)


class ErrorPresenter:
    """Packages exceptions into public errors and logs their details."""

    VALIDATION_MESSAGE = "Invalid request"
    UNEXPECTED_MESSAGE = "Something went wrong"

    def __init__(self, log: Optional[logging.Logger] = None):
        """
        Create the presenter.

        Args:
            log: Logger for internal details; defaults to this module's logger
        """
        self._log = log or logger

    def present(self, error: Exception) -> PresentedError:
        """
        Package an exception and log its details.

        Args:
            error: Any exception

        Returns:
            PresentedError: Status, public message, error block, and optional data
        """
        if isinstance(error, AppError):
            return self._present_app_error(error)
        if isinstance(error, RequestValidationError):
            return self._present_validation_error(error)
        if isinstance(error, StarletteHTTPException):
            return self._present_http_exception(error)
        self._log.exception("Unexpected error", exc_info=error)
        return PresentedError(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=self.UNEXPECTED_MESSAGE,
            error=ErrorInfo(code="internal_error"),
        )

    def _present_app_error(self, error: AppError) -> PresentedError:
        """
        Package an expected application error.

        Args:
            error: Application error

        Returns:
            PresentedError: The error's own status, message, code, and data
        """
        self._log.warning("%s: %s", error.code, error.detail)
        return PresentedError(
            status_code=error.status_code,
            message=error.public_message,
            error=ErrorInfo(code=error.code),
            data=error.data,
        )

    def _present_validation_error(self, error: RequestValidationError) -> PresentedError:
        """
        Package a request validation error with one entry per invalid field.

        Args:
            error: FastAPI validation error

        Returns:
            PresentedError: 422 with `validation_error` and the field messages
        """
        # Only field paths and error types are logged: the invalid input may hold a secret (an AI API key).
        self._log.info("Request validation failed: %s", self._error_locations(error))
        return PresentedError(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            message=self.VALIDATION_MESSAGE,
            error=ErrorInfo(code="validation_error", fields=self._field_errors(error)),
        )

    def _present_http_exception(self, error: StarletteHTTPException) -> PresentedError:
        """
        Package a framework HTTP error (unknown route, wrong method).

        Args:
            error: Starlette HTTP exception

        Returns:
            PresentedError: The same status with its standard phrase as message and code
        """
        status = HTTPStatus(error.status_code)
        return PresentedError(
            status_code=status.value,
            message=status.phrase,
            error=ErrorInfo(code=status.phrase.lower().replace(" ", "_").replace("-", "_")),
        )

    def _error_locations(self, error: RequestValidationError) -> List[str]:
        """
        List the invalid locations and error types without the submitted values.

        Args:
            error: FastAPI validation error

        Returns:
            List[str]: `location (type)` per error
        """
        return [
            f"{'.'.join(str(part) for part in item.get('loc', ()))} ({item.get('type', '')})" for item in error.errors()
        ]

    def _field_errors(self, error: RequestValidationError) -> List[FieldError]:
        """
        Convert validation errors into field entries.

        Args:
            error: FastAPI validation error

        Returns:
            List[FieldError]: Dotted field path (without the `body`/`query` prefix) and message
        """
        fields = []
        for item in error.errors():
            location = [str(part) for part in item.get("loc", ())]
            path = location[1:] if len(location) > 1 else location
            fields.append(FieldError(field=".".join(path), message=str(item.get("msg", ""))))
        return fields


error_presenter = ErrorPresenter()
