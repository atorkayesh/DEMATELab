"""
Unit tests for ScalesFeature.

Tests cover:
- Standard and Z terms, defaults, options, limits and weight rules
"""

import unittest

import pytest

from features.scales_feature import ScalesFeature


@pytest.mark.unit
class TestScalesFeature(unittest.TestCase):
    """Test cases for ScalesFeature."""

    def test_scales(self):
        """Test the GUI's scales and options."""
        data = ScalesFeature().get_scales()

        self.assertEqual(data.standard.terms[-1], "Extreme influence")
        self.assertEqual(data.standard.diagonal_label, "No influence")
        self.assertEqual(len(data.fuzzy_z.terms), 25)
        self.assertEqual(data.fuzzy_z.default_label, "No influence with VH reliability")
        self.assertEqual(data.fuzzy_z.influence_terms[-1], "Very high influence")
        self.assertEqual(
            [o.label for o in data.solvers], ["DEMATEL", "Fuzzy DEMATEL", "Grey DEMATEL", "Fuzzy Z-DEMATEL"]
        )
        self.assertEqual(data.thresholds[-1].model_dump(), {"key": "mmde", "label": "Maximum Mean De-Entropy"})
        self.assertEqual((data.limits.factors_max, data.limits.experts_max, data.limits.factors_default), (100, 50, 4))
        self.assertEqual((data.weights.decimals, data.weights.sum_tolerance), (3, 0.005))
