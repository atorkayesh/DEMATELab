"""
Unit tests for TriangularMath.

Tests cover:
- Addition and subtraction rules (l1-u2, m1-m2, u1-l2)
- Defuzzification for 1, 2 and 3 dimensions, and the error for other shapes
"""

import unittest

import numpy as np
import pytest

from errors.analysis_errors import InvalidAnalysisInputError
from utils.triangular_utils import TriangularMath


@pytest.mark.unit
class TestTriangularMath(unittest.TestCase):
    """Test cases for TriangularMath."""

    def setUp(self):
        """Create the helper and two values."""
        self.math = TriangularMath()
        self.a = np.array([[1.0, 2.0, 4.0]])
        self.b = np.array([[0.5, 1.0, 3.0]])

    def test_add(self):
        """Test component-wise addition."""
        np.testing.assert_array_equal(self.math.add(self.a, self.b), [[1.5, 3.0, 7.0]])

    def test_subtract_crosses_bounds(self):
        """Test (l1-u2, m1-m2, u1-l2)."""
        np.testing.assert_array_equal(self.math.subtract(self.a, self.b), [[-2.0, 1.0, 3.5]])

    def test_defuzzify_shapes(self):
        """Test l + ((u - l) + (m - l)) / 3 for vectors, rows and matrices."""
        expected = 1.0 + ((4.0 - 1.0) + (2.0 - 1.0)) / 3
        self.assertEqual(float(self.math.defuzzify(self.a[0])), expected)
        np.testing.assert_array_equal(self.math.defuzzify(self.a), [expected])
        np.testing.assert_array_equal(self.math.defuzzify(self.a.reshape(1, 1, 3)), [[expected]])

    def test_defuzzify_rejects_other_shapes(self):
        """Test a last dimension other than 3 is rejected."""
        with self.assertRaises(InvalidAnalysisInputError):
            self.math.defuzzify(np.zeros((2, 2)))
