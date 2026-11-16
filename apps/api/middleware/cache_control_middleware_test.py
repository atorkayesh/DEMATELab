"""
Unit tests for CacheControlMiddleware.

Tests cover:
- Responses under /api/ get `Cache-Control: no-store`
- A response that sets its own Cache-Control keeps it
- Paths outside /api/ are untouched
"""

import unittest

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import PlainTextResponse

from middleware.cache_control_middleware import CacheControlMiddleware


def _make_app() -> FastAPI:
    """Create a small app with API and non-API routes."""
    app = FastAPI()
    app.add_middleware(CacheControlMiddleware)

    @app.get("/api/plain")
    async def plain() -> PlainTextResponse:
        return PlainTextResponse("ok")

    @app.get("/api/own-header")
    async def own_header() -> PlainTextResponse:
        return PlainTextResponse("ok", headers={"Cache-Control": "no-cache, no-store"})

    @app.get("/outside")
    async def outside() -> PlainTextResponse:
        return PlainTextResponse("ok")

    return app


@pytest.mark.unit
class TestCacheControlMiddleware(unittest.TestCase):
    """Test cases for CacheControlMiddleware."""

    def setUp(self):
        """Create the test client."""
        self.client = TestClient(_make_app())

    def test_api_response_gets_no_store(self):
        """Test an API response without its own header gets `no-store`."""
        self.assertEqual(self.client.get("/api/plain").headers["cache-control"], "no-store")

    def test_existing_header_is_kept(self):
        """Test a response's own Cache-Control header is not replaced."""
        self.assertEqual(self.client.get("/api/own-header").headers["cache-control"], "no-cache, no-store")

    def test_non_api_path_is_untouched(self):
        """Test paths outside /api/ get no Cache-Control header."""
        self.assertNotIn("cache-control", self.client.get("/outside").headers)
