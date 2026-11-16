"""
Unit tests for ErrorHandlers and ErrorPresenter.

Tests cover:
- AppError subclasses return their status, public message, code, and data
- Internal details never reach the response body
- Validation errors return 422 with per-field messages
- Unknown routes return 404 in the standard response shape
- Unexpected exceptions return a generic 500
"""

import unittest

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from errors.analysis_errors import AnalysisFailedError
from errors.error_handlers import ErrorHandlers
from errors.health_errors import ServiceUnhealthyError


class _Payload(BaseModel):
    """Request body and error data for the test app."""

    question: str


def _make_app() -> FastAPI:
    """Create a small app with routes that fail in each handled way."""
    app = FastAPI()
    ErrorHandlers().register(app)

    @app.get("/app-error")
    async def app_error() -> None:
        raise AnalysisFailedError("LinAlgError at secret-host", public_message="Failed to invert (I - X).")

    @app.get("/app-error-with-data")
    async def app_error_with_data() -> None:
        raise ServiceUnhealthyError(data=_Payload(question="details"))

    @app.post("/validated")
    async def validated(payload: _Payload) -> _Payload:
        return payload

    @app.get("/crash")
    async def crash() -> None:
        raise RuntimeError("password=hunter2 leaked in a traceback")

    return app


@pytest.mark.unit
class TestErrorHandlers(unittest.TestCase):
    """Test cases for ErrorHandlers and ErrorPresenter."""

    def setUp(self):
        """Create a client that returns 500 responses instead of re-raising."""
        self.client = TestClient(_make_app(), raise_server_exceptions=False)

    def test_app_error_uses_public_message_and_code(self):
        """Test an AppError returns its status, public message, and code without the detail."""
        response = self.client.get("/app-error")
        body = response.json()

        self.assertEqual(response.status_code, 422)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Failed to invert (I - X).")
        self.assertEqual(body["error"]["code"], "analysis_failed")
        self.assertNotIn("secret-host", response.text)

    def test_app_error_returns_data(self):
        """Test an AppError with data returns it in `data`."""
        response = self.client.get("/app-error-with-data")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["data"], {"question": "details"})

    def test_validation_error_lists_fields(self):
        """Test a validation error returns 422 with the invalid field."""
        response = self.client.post("/validated", json={})
        body = response.json()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(body["message"], "Invalid request")
        self.assertEqual(body["error"]["code"], "validation_error")
        self.assertEqual(body["error"]["fields"][0]["field"], "question")

    def test_unknown_route_uses_standard_shape(self):
        """Test an unknown route returns 404 as an ApiResponseModel."""
        response = self.client.get("/missing")
        body = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(body["success"])
        self.assertEqual(body["error"]["code"], "not_found")

    def test_unexpected_error_is_generic(self):
        """Test an unexpected exception returns a generic 500 without its message."""
        response = self.client.get("/crash")
        body = response.json()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(body["message"], "Something went wrong")
        self.assertEqual(body["error"]["code"], "internal_error")
        self.assertNotIn("hunter2", response.text)

    def test_validation_error_never_echoes_or_logs_input(self):
        """Test an invalid value is neither returned nor logged (it may be an API key)."""
        with self.assertLogs("errors.error_presenter", level="INFO") as logs:
            response = self.client.post("/validated", json={"question": ["sk-secret-value"]})

        self.assertEqual(response.status_code, 422)
        self.assertNotIn("sk-secret-value", response.text)
        self.assertNotIn("sk-secret-value", "\n".join(logs.output))
