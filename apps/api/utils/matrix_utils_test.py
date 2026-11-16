"""
Unit tests for MatrixConverter.

Tests cover:
- Arrays become nested lists of Python floats and back
- The viewer's crisp matrix: mean over components for 3-D matrices, unchanged for 2-D
"""

import unittest

import numpy as np
import pytest

from utils.matrix_utils import MatrixConverter


@pytest.mark.unit
class TestMatrixConverter(unittest.TestCase):
    """Test cases for MatrixConverter."""

    def setUp(self):
        """Create the converter."""
        self.converter = MatrixConverter()

    def test_to_lists_and_back(self):
        """Test round trip through nested lists."""
        lists = self.converter.to_lists(np.array([[1, 2], [3, 4]]))
        self.assertEqual(lists, [[1.0, 2.0], [3.0, 4.0]])
        self.assertIsInstance(lists[0][0], float)
        np.testing.assert_array_equal(self.converter.to_array(lists), [[1.0, 2.0], [3.0, 4.0]])

    def test_crisp_2d(self):
        """Test triangular cells are averaged and crisp matrices kept."""
        fuzzy = np.array([[[0.0, 0.5, 1.0]]])
        np.testing.assert_array_equal(self.converter.crisp_2d(fuzzy), [[0.5]])
        np.testing.assert_array_equal(self.converter.crisp_2d(np.eye(2)), np.eye(2))
