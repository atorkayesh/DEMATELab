"""
Unit tests for ResponseBuilder.

Tests cover:
- ok() returns 200 with success, message, data, and a timestamp
- error() returns the presented status, public message, error block, and data
- stream() frames each event as one SSE `data:` line with no-cache headers
- download() and download_bytes() return attachments with the file name
- image() returns the bytes inline with the media type
"""

import json
import unittest
from typing import AsyncIterator

import pytest
from pydantic import BaseModel

from models.error_models import ErrorInfo, PresentedError
from utils.response_utils import ResponseBuilder


class _Item(BaseModel):
    """Small payload for the tests."""

    name: str


async def _events() -> AsyncIterator[_Item]:
    """Yield two events."""
    yield _Item(name="first")
    yield _Item(name="zweite Größe")


@pytest.mark.unit
class TestResponseBuilder(unittest.IsolatedAsyncioTestCase):
    """Test cases for ResponseBuilder."""

    def setUp(self):
        """Create the builder."""
        self.builder = ResponseBuilder()

    def test_ok_wraps_data(self):
        """Test ok() builds a 200 ApiResponseModel body with a timestamp."""
        response = self.builder.ok(_Item(name="x"), "Done")
        body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.media_type, "application/json")
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Done")
        self.assertEqual(body["data"], {"name": "x"})
        self.assertIsNone(body["error"])
        self.assertTrue(body["metadata"]["timestamp"].endswith("Z"))

    def test_error_uses_presented_error(self):
        """Test error() returns the presented status, message, code, and data."""
        presented = PresentedError(
            status_code=503, message="Unavailable", error=ErrorInfo(code="analysis_failed"), data=_Item(name="d")
        )

        response = self.builder.error(presented)
        body = json.loads(response.body)

        self.assertEqual(response.status_code, 503)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Unavailable")
        self.assertEqual(body["error"], {"code": "analysis_failed", "fields": None})
        self.assertEqual(body["data"], {"name": "d"})

    async def test_stream_frames_events(self):
        """Test stream() yields one `data: <json>` frame per event and sets no-cache headers."""
        response = self.builder.stream(_events())

        frames = [chunk async for chunk in response.body_iterator]

        self.assertEqual(response.headers["cache-control"], "no-cache, no-store")
        self.assertTrue(response.media_type.startswith("text/event-stream"))
        self.assertEqual(frames[0], 'data: {"name":"first"}\n\n')
        self.assertEqual(frames[1], 'data: {"name":"zweite Größe"}\n\n')

    def test_download_returns_text_attachment(self):
        """Test download() encodes text and sets the attachment header and charset."""
        response = self.builder.download("a,b\n", "export.csv", "text/csv")

        self.assertEqual(response.body, b"a,b\n")
        self.assertEqual(response.headers["content-disposition"], 'attachment; filename="export.csv"')
        self.assertTrue(response.headers["content-type"].startswith("text/csv; charset=utf-8"))

    def test_download_bytes_returns_binary_attachment(self):
        """Test download_bytes() keeps the bytes unchanged and sets the attachment header."""
        response = self.builder.download_bytes(b"PK\x03\x04", "dematel_results.xlsx", "application/zip")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"PK\x03\x04")
        self.assertEqual(response.headers["content-disposition"], 'attachment; filename="dematel_results.xlsx"')
        self.assertEqual(response.headers["content-type"], "application/zip")

    def test_image_returns_inline_bytes(self):
        """Test image() returns the bytes without an attachment header."""
        response = self.builder.image(b"\x89PNG", "image/png")

        self.assertEqual(response.body, b"\x89PNG")
        self.assertEqual(response.headers["content-type"], "image/png")
        self.assertNotIn("content-disposition", response.headers)
