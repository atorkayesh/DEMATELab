"""
Response packaging.

`ResponseBuilder` builds every HTTP response the API returns, so routers stay one statement and
all bodies share the `ApiResponseModel` shape and timestamp metadata. Models serialize by alias. File
downloads (XLSX exports, PNG charts) are built here too.
"""

from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any, AsyncIterator, Dict

from pydantic import BaseModel
from starlette.responses import Response, StreamingResponse

from models.error_models import PresentedError
from models.response_model import ApiResponseModel


class ResponseBuilder:
    """Builds JSON, server-sent-event, and file download responses."""

    JSON_MEDIA_TYPE = "application/json"
    STREAM_MEDIA_TYPE = "text/event-stream; charset=utf-8"
    STREAM_HEADERS = {"Cache-Control": "no-cache, no-store"}

    def ok(self, data: Any, message: str) -> Response:
        """
        Build a successful JSON response.

        Args:
            data: Response payload (usually a Pydantic model)
            message: Human-readable message

        Returns:
            Response: 200 with `success: true`
        """
        body = ApiResponseModel[Any](success=True, message=message, data=data, metadata=self._metadata())
        return self._json(body, HTTPStatus.OK)

    def error(self, presented: PresentedError) -> Response:
        """
        Build an error JSON response.

        Args:
            presented: Error packaged by `ErrorPresenter`

        Returns:
            Response: The error's status with `success: false` and the public error block
        """
        body = ApiResponseModel[Any](
            success=False,
            message=presented.message,
            data=presented.data,
            metadata=self._metadata(),
            error=presented.error,
        )
        return self._json(body, presented.status_code)

    def stream(self, events: AsyncIterator[BaseModel]) -> StreamingResponse:
        """
        Build a server-sent-event stream with one `data:` line per event.

        Args:
            events: Async iterator of event models

        Returns:
            StreamingResponse: `text/event-stream` response
        """
        return StreamingResponse(
            self._sse_lines(events),
            media_type=self.STREAM_MEDIA_TYPE,
            headers=self.STREAM_HEADERS,
        )

    def download(self, content: str, filename: str, media_type: str) -> Response:
        """
        Build a file download (for example an export).

        Args:
            content: File content
            filename: Suggested file name (ASCII, no quotes)
            media_type: MIME type, e.g. `text/csv`

        Returns:
            Response: 200 with `Content-Disposition: attachment`
        """
        return Response(
            content=content.encode("utf-8"),
            status_code=HTTPStatus.OK,
            media_type=f"{media_type}; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    def download_bytes(self, content: bytes, filename: str, media_type: str) -> Response:
        """
        Build a binary file download (for example an XLSX export).

        Args:
            content: File content
            filename: Suggested file name (ASCII, no quotes)
            media_type: MIME type, e.g. `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

        Returns:
            Response: 200 with `Content-Disposition: attachment`
        """
        return Response(
            content=content,
            status_code=HTTPStatus.OK,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    def image(self, content: bytes, media_type: str) -> Response:
        """
        Build an inline image response (for example a PNG chart shown in the browser).

        Args:
            content: Image bytes
            media_type: MIME type, e.g. `image/png`

        Returns:
            Response: 200 with the image as the body
        """
        return Response(content=content, status_code=HTTPStatus.OK, media_type=media_type)

    async def _sse_lines(self, events: AsyncIterator[BaseModel]) -> AsyncIterator[str]:
        """
        Serialize events as SSE frames.

        Args:
            events: Async iterator of event models

        Yields:
            str: `data: <json>` followed by a blank line
        """
        async for event in events:
            yield f"data: {event.model_dump_json(by_alias=True)}\n\n"

    def _json(self, body: ApiResponseModel[Any], status_code: int) -> Response:
        """
        Serialize a response body.

        Args:
            body: Response model
            status_code: HTTP status

        Returns:
            Response: JSON response
        """
        return Response(
            content=body.model_dump_json(by_alias=True), status_code=status_code, media_type=self.JSON_MEDIA_TYPE
        )

    def _metadata(self) -> Dict[str, str]:
        """
        Return the metadata every response carries.

        Returns:
            Dict[str, str]: `timestamp` in UTC ISO 8601 with a `Z` suffix
        """
        return {"timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}


response_builder = ResponseBuilder()
