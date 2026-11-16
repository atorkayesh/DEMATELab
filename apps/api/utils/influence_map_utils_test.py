"""
Unit tests for InfluenceMapGeometry.

Tests cover:
- Edges strictly above the threshold, diagonal skipped
- Line width scaling and the equal-weights midpoint
- Qt validation messages
- Mutual edges are drawn as two arrows
"""

import unittest

import numpy as np
import pytest
from matplotlib.figure import Figure

from errors.analysis_errors import InvalidAnalysisInputError
from utils.influence_map_utils import InfluenceMapGeometry


@pytest.mark.unit
class TestInfluenceMapGeometry(unittest.TestCase):
    """Test cases for InfluenceMapGeometry."""

    def setUp(self):
        """Create the helper."""
        self.geometry = InfluenceMapGeometry()

    def test_edges_strictly_above_threshold(self):
        """Test the threshold itself is not an edge and self loops are skipped."""
        total = np.array([[9.0, 0.5], [0.6, 9.0]])
        self.assertEqual(self.geometry.edges(["A", "B"], total, 0.5), [("B", "A", 0.6)])

    def test_line_width(self):
        """Test linear scaling between 0.6 and 4.0, and the midpoint for equal weights."""
        self.assertEqual(self.geometry.line_width([1.0, 2.0], 2.0), 4.0)
        self.assertEqual(self.geometry.line_width([1.0, 2.0], 1.0), 0.6)
        self.assertEqual(self.geometry.line_width([1.0, 1.0], 1.0), 2.3)

    def test_validate(self):
        """Test the Qt input checks."""
        with self.assertRaises(InvalidAnalysisInputError) as context:
            self.geometry.validate(["A"], np.zeros(1), np.zeros(1), np.zeros((1, 1)), float("nan"))
        self.assertEqual(context.exception.public_message, "Threshold must be a valid finite number.")

    def test_mutual_edges_draw_two_arrows(self):
        """Test a pair of opposite edges adds two patches."""
        ax = Figure().add_subplot(111)
        positions = {"A": (0.0, 0.0), "B": (1.0, 1.0)}
        self.geometry.draw_edges(ax, [("A", "B", 1.0), ("B", "A", 2.0)], positions)
        self.assertEqual(len(ax.patches), 2)
