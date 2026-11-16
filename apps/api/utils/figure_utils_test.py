"""
Unit tests for FigureRenderer.

Tests cover:
- New figures are 8 x 6 inches
- PNG output: 800 x 600 at 100 dpi; about three times wider at 300 dpi (tight crop)
"""

import struct
import unittest

import pytest

from utils.figure_utils import FigureRenderer


def png_size(content: bytes) -> tuple:
    """Read width and height from a PNG header."""
    return struct.unpack(">II", content[16:24])


@pytest.mark.unit
class TestFigureRenderer(unittest.TestCase):
    """Test cases for FigureRenderer."""

    def setUp(self):
        """Create a renderer and a figure with one plot."""
        self.renderer = FigureRenderer()
        self.figure = self.renderer.new_figure()
        self.figure.add_subplot(111).plot([0, 1], [0, 1])
        self.figure.tight_layout()

    def test_figure_size(self):
        """Test the Qt plot tab size."""
        self.assertEqual(tuple(self.figure.get_size_inches()), (8.0, 6.0))

    def test_png_sizes(self):
        """Test the display and download resolutions."""
        display = self.renderer.to_png(self.figure, 100)
        download = self.renderer.to_png(self.figure, 300)

        self.assertTrue(display.startswith(b"\x89PNG"))
        self.assertEqual(png_size(display), (800, 600))
        self.assertAlmostEqual(png_size(download)[0] / 800, 3, delta=0.3)
