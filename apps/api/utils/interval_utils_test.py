"""
Unit tests for IntervalMath.

Tests cover:
- Addition and subtraction rules ([aL - bU, aU - bL])
- Whitening for 1, 2 and 3 dimensions, and the error for other shapes
"""

import unittest

import numpy as np
import pytest

from errors.analysis_errors import InvalidAnalysisInputError
from utils.interval_utils import IntervalMath


@pytest.mark.unit
class TestIntervalMath(unittest.TestCase):
    """Test cases for IntervalMath."""

    def setUp(self):
        """Create the helper and two intervals."""
        self.math = IntervalMath()
        self.a = np.array([[1.0, 3.0]])
        self.b = np.array([[0.5, 2.0]])

    def test_add(self):
        """Test bound-wise addition."""
        np.testing.assert_array_equal(self.math.add(self.a, self.b), [[1.5, 5.0]])

    def test_subtract_crosses_bounds(self):
        """Test [aL - bU, aU - bL]."""
        np.testing.assert_array_equal(self.math.subtract(self.a, self.b), [[-1.0, 2.5]])

    def test_whiten_shapes(self):
        """Test (lower + upper) / 2 for vectors, rows and matrices."""
        self.assertEqual(float(self.math.whiten(self.a[0])), 2.0)
        np.testing.assert_array_equal(self.math.whiten(self.a), [2.0])
        np.testing.assert_array_equal(self.math.whiten(self.a.reshape(1, 1, 2)), [[2.0]])

    def test_whiten_rejects_other_shapes(self):
        """Test a last dimension other than 2 is rejected."""
        with self.assertRaises(InvalidAnalysisInputError):
            self.math.whiten(np.zeros((2, 3)))
