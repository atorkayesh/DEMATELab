"""
Cache-Control middleware.

API responses must never be cached by browsers or proxies. This pure ASGI middleware adds
`Cache-Control: no-store` to responses under `/api/` that do not set their own header, and works
with streaming responses.
"""

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from constants.app_constants import CACHE_CONTROL_SETTINGS


class CacheControlMiddleware:
    """Adds a default `Cache-Control` header to API responses."""

    def __init__(
        self,
        app: ASGIApp,
        path_prefix: str = CACHE_CONTROL_SETTINGS["PATH_PREFIX"],
        value: str = CACHE_CONTROL_SETTINGS["VALUE"],
    ):
        """
        Wrap an ASGI app.

        Args:
            app: Wrapped ASGI application
            path_prefix: Only paths starting with this prefix get the header
            value: Header value to set
        """
        self._app = app
        self._path_prefix = path_prefix
        self._value = value

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handle one ASGI call.

        Args:
            scope: ASGI scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] != "http" or not scope["path"].startswith(self._path_prefix):
            await self._app(scope, receive, send)
            return

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                if "cache-control" not in headers:
                    headers["Cache-Control"] = self._value
            await send(message)

        await self._app(scope, receive, send_with_header)
