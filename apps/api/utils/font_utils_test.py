"""
Unit tests for FontRegistrar.

Tests cover:
- The bundled Inter fonts are registered and become the default family
- An empty folder registers nothing (no download)
"""

import tempfile
import unittest
from pathlib import Path

import pytest
from matplotlib import font_manager, rcParams

from utils.font_utils import FontRegistrar


@pytest.mark.unit
class TestFontRegistrar(unittest.TestCase):
    """Test cases for FontRegistrar."""

    def test_registers_bundled_inter(self):
        """Test the nine Inter files are registered and Inter is the first family."""
        paths = FontRegistrar().register_inter_fonts()

        self.assertEqual(len(paths), 9)
        self.assertEqual(rcParams["font.family"], ["Inter", "DejaVu Sans"])
        self.assertIn("Inter", {font.name for font in font_manager.fontManager.ttflist})

    def test_empty_folder_registers_nothing(self):
        """Test a folder without fonts returns no paths."""
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(FontRegistrar(Path(folder)).register_inter_fonts(), [])
