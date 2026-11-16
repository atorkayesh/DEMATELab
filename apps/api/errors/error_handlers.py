"""
FastAPI exception handlers.

`ErrorHandlers.register` makes every failure (application errors, validation errors, unknown routes,
and unexpected exceptions) return an `ApiResponseModel` with `success: false`.
"""

from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from errors.app_error import AppError
from errors.error_presenter import ErrorPresenter, error_presenter
from utils.response_utils import ResponseBuilder, response_builder


class ErrorHandlers:
    """Registers and runs the API's exception handlers."""

    HANDLED = (AppError, RequestValidationError, StarletteHTTPException, Exception)

    def __init__(self, presenter: Optional[ErrorPresenter] = None, builder: Optional[ResponseBuilder] = None):
        """
        Create the handlers.

        Args:
            presenter: Error presenter; defaults to the shared instance
            builder: Response builder; defaults to the shared instance
        """
        self._presenter = presenter or error_presenter
        self._builder = builder or response_builder

    def register(self, app: FastAPI) -> None:
        """
        Register the handler for every handled exception type.

        Args:
            app: FastAPI application
        """
        for exception_type in self.HANDLED:
            app.add_exception_handler(exception_type, self.handle)

    async def handle(self, _: Request, error: Exception) -> Response:
        """
        Turn an exception into an error response.

        Args:
            _: Incoming request (unused)
            error: Raised exception

        Returns:
            Response: Packaged error response
        """
        return self._builder.error(self._presenter.present(error))


error_handlers = ErrorHandlers()
