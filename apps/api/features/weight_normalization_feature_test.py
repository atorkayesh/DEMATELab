"""
Unit tests for WeightNormalizationFeature.

Tests cover:
- Default weights for 1, 2, 3 and 7 experts (remainder to the first experts)
- Correction within ±0.005 (3 experts at 0.3333, over and under), from the last expert backwards
- Rejection outside the tolerance and of a non-positive total
"""

import unittest

import pytest

from errors.analysis_errors import InvalidWeightsError
from features.weight_normalization_feature import WeightNormalizationFeature


@pytest.mark.unit
class TestWeightNormalizationFeature(unittest.TestCase):
    """Test cases for WeightNormalizationFeature."""

    def setUp(self):
        """Create the feature."""
        self.feature = WeightNormalizationFeature()

    def test_default_weights(self):
        """Test equal thousandths with the remainder on the first experts."""
        self.assertEqual(self.feature.default_weights(1), [1.0])
        self.assertEqual(self.feature.default_weights(2), [0.5, 0.5])
        self.assertEqual(self.feature.default_weights(3), [0.334, 0.333, 0.333])
        self.assertEqual(self.feature.default_weights(7), [0.143, 0.143, 0.143, 0.143, 0.143, 0.143, 0.142])

    def test_under_one_adds_to_last_expert(self):
        """Test 3 x 0.3333 (total 0.9999) becomes 0.333, 0.333, 0.334."""
        self.assertEqual(self.feature.normalize([0.3333, 0.3333, 0.3333]), [0.333, 0.333, 0.334])

    def test_over_one_removes_from_last_expert(self):
        """Test a total of 1.004 is corrected on the last expert."""
        self.assertEqual(self.feature.normalize([0.5, 0.504]), [0.5, 0.5])

    def test_exact_weights_unchanged(self):
        """Test weights that already sum to 1."""
        self.assertEqual(self.feature.normalize([0.334, 0.333, 0.333]), [0.334, 0.333, 0.333])

    def test_outside_tolerance_rejected(self):
        """Test totals beyond ±0.005 and a zero total are rejected with the Qt message."""
        for weights in ([0.5, 0.4], [0.6, 0.406], [0.0, 0.0]):
            with self.subTest(weights=weights):
                with self.assertRaises(InvalidWeightsError) as context:
                    self.feature.normalize(weights)
                self.assertEqual(context.exception.public_message, "Expert weights must sum to 1.")
