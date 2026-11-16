"""
Base class for every expected API error.

Subclasses set `code`, `status_code`, and `public_message`. The `detail` passed in is logged and
never returned to clients; `data` is returned with the error when a failure still has a useful body
(for example the health details of an unhealthy system).
"""

from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel


class AppError(Exception):
    """
    Expected failure with a stable code and a message that is safe to show.

    Attributes:
        code: Stable machine-readable error code
        status_code: HTTP status the error maps to
        public_message: Message returned to clients
        detail: Internal description, logged only
        data: Optional payload returned with the error
    """

    code: str = "internal_error"
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    public_message: str = "Something went wrong"

    def __init__(
        self,
        detail: Optional[str] = None,
        *,
        data: Optional[BaseModel] = None,
        public_message: Optional[str] = None,
        code: Optional[str] = None,
    ):
        """
        Create the error.

        Args:
            detail: Internal description for the logs; defaults to the public message
            data: Optional payload returned with the error
            public_message: Overrides the class's public message
            code: Overrides the class's code (e.g. to keep the code of the error that caused this one)
        """
        if public_message is not None:
            self.public_message = public_message
        if code is not None:
            self.code = code
        self.detail = detail or self.public_message
        self.data = data
        super().__init__(self.detail)
