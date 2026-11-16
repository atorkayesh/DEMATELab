"""
Unit tests for ThresholdFeature.

Tests cover:
- Average, quartiles and median over the whole matrix (diagonal included)
- MMDE is delegated
"""

import unittest
from unittest.mock import MagicMock

import numpy as np
import pytest

from constants.solver_constants import ThresholdMethod
from features.threshold_feature import ThresholdFeature


@pytest.mark.unit
class TestThresholdFeature(unittest.TestCase):
    """Test cases for ThresholdFeature."""

    def setUp(self):
        """Create the feature with a mocked MMDE."""
        self.mmde = MagicMock()
        self.mmde.compute.return_value = 0.42
        self.feature = ThresholdFeature(self.mmde)
        self.matrix = np.array([[0.0, 1.0], [2.0, 3.0]])

    def test_statistics(self):
        """Test numpy's mean, quantiles and median over all four cells."""
        self.assertEqual(self.feature.compute(self.matrix, ThresholdMethod.AVERAGE), 1.5)
        self.assertEqual(self.feature.compute(self.matrix, ThresholdMethod.FIRST_QUARTILE), 0.75)
        self.assertEqual(self.feature.compute(self.matrix, ThresholdMethod.MEDIAN), 1.5)
        self.assertEqual(self.feature.compute(self.matrix, ThresholdMethod.THIRD_QUARTILE), 2.25)

    def test_mmde_delegated(self):
        """Test MMDE uses the MMDE feature."""
        self.assertEqual(self.feature.compute(self.matrix, ThresholdMethod.MMDE), 0.42)
        self.mmde.compute.assert_called_once()
