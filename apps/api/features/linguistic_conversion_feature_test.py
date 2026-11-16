"""
Unit tests for LinguisticConversionFeature.

Tests cover:
- Crisp, fuzzy, grey and Z scales; trimmed, case-sensitive lookup
- Unknown labels name the expert, row, column and label
- Diagonal labels per solver and forcing them
"""

import unittest

import numpy as np
import pytest

from constants.solver_constants import SolverType
from errors.analysis_errors import InvalidAnalysisInputError, UnknownLinguisticTermError
from features.linguistic_conversion_feature import LinguisticConversionFeature


@pytest.mark.unit
class TestLinguisticConversionFeature(unittest.TestCase):
    """Test cases for LinguisticConversionFeature."""

    def setUp(self):
        """Create the feature and a matrix."""
        self.feature = LinguisticConversionFeature()
        self.matrix = [["No influence", " High influence "], ["Extreme influence", "No influence"]]

    def test_scales(self):
        """Test each scale's numbers and shape."""
        crisp = self.feature.convert(SolverType.DEMATEL, self.matrix, "E", ["A", "B"])
        np.testing.assert_array_equal(crisp, [[0.0, 3.0], [4.0, 0.0]])
        fuzzy = self.feature.convert(SolverType.FUZZY_DEMATEL, self.matrix, "E", ["A", "B"])
        np.testing.assert_array_equal(fuzzy[0, 1], [0.5, 0.75, 1.0])
        grey = self.feature.convert(SolverType.GREY_DEMATEL, self.matrix, "E", ["A", "B"])
        self.assertEqual(grey.shape, (2, 2, 2))
        z = [["No influence with VH reliability", "Very high influence with VL reliability"]] * 2
        np.testing.assert_array_equal(
            self.feature.convert(SolverType.FUZZY_Z_DEMATEL, z, "E", ["A", "B"])[0, 1], [0.949, 1.265, 1.265]
        )

    def test_unknown_label_names_the_cell(self):
        """Test labels are case-sensitive and errors name expert, row, column and label."""
        matrix = [["No influence", "high influence"], ["Low influence", "No influence"]]
        with self.assertRaises(UnknownLinguisticTermError) as context:
            self.feature.convert(SolverType.DEMATEL, matrix, "Ann", ["Cost", "Time"])
        message = context.exception.public_message
        self.assertIn("'high influence'", message)
        self.assertIn("expert 'Ann' (row 'Cost', column 'Time')", message)

    def test_z_scale_rejects_standard_extreme(self):
        """Test the Z scale has no "Extreme influence"."""
        with self.assertRaises(UnknownLinguisticTermError):
            self.feature.convert(SolverType.FUZZY_Z_DEMATEL, self.matrix, "E", ["A", "B"])

    def test_wrong_shape(self):
        """Test a non-square matrix is rejected."""
        with self.assertRaises(InvalidAnalysisInputError):
            self.feature.convert(SolverType.DEMATEL, [["No influence"]], "E", ["A", "B"])

    def test_force_diagonal(self):
        """Test the diagonal becomes the solver's no-influence label."""
        forced = self.feature.force_diagonal(
            [["High influence", "Low influence"], ["x", "y"]], SolverType.FUZZY_Z_DEMATEL
        )
        self.assertEqual(
            forced, [["No influence with VH reliability", "Low influence"], ["x", "No influence with VH reliability"]]
        )
        self.assertEqual(self.feature.diagonal_label(SolverType.GREY_DEMATEL), "No influence")
