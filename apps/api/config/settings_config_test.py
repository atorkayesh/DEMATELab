"""
Unit tests for Settings.

Tests cover:
- CORS origins parsing
- Environment variables override defaults
- Defaults without an env file
"""

import os
import unittest
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from config.settings_config import Settings


@pytest.mark.unit
class TestSettings(unittest.TestCase):
    """Test cases for Settings."""

    def test_cors_origins_list_trims_and_drops_empty(self):
        """Test comma-separated origins are trimmed and empty entries removed."""
        settings = Settings(_env_file=None, cors_origins=" http://a.test , ,http://b.test ")

        self.assertEqual(settings.cors_origins_list, ["http://a.test", "http://b.test"])

    def test_reads_environment_variables(self):
        """Test values come from environment variables."""
        env = {"APP_ENV": "production", "CORS_ORIGINS": "https://dematelab.test"}
        with patch.dict(os.environ, env, clear=False):
            settings = Settings(_env_file=None)

        self.assertEqual(settings.app_env, "production")
        self.assertEqual(settings.cors_origins_list, ["https://dematelab.test"])

    def test_defaults(self):
        """Test defaults without environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=None)

        self.assertEqual(settings.app_env, "development")
        self.assertEqual(settings.cors_origins_list, ["http://localhost:3000"])

    def test_rejects_unknown_environment(self):
        """Test APP_ENV only accepts development or production."""
        with self.assertRaises(ValidationError):
            Settings(_env_file=None, app_env="staging")
