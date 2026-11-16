"""
Unit tests for DematelEngineSupport.

Tests cover:
- Qt validation messages (empty factors, no experts, weight range and sum, shape)
- Normalisation by the largest row/column sum and the all-"No influence" error
- Inversion failure error
- Cause group is relation >= 0
"""

import unittest

import numpy as np
import pytest

from errors.analysis_errors import AnalysisFailedError, InvalidAnalysisInputError
from models.solver_models import SolverExpert
from utils.dematel_engine_utils import ALL_NO_INFLUENCE_MESSAGE, DematelEngineSupport


@pytest.mark.unit
class TestDematelEngineSupport(unittest.TestCase):
    """Test cases for DematelEngineSupport."""

    def setUp(self):
        """Create the helper."""
        self.support = DematelEngineSupport()

    def _message(self, factors, experts, cell_shape=()):
        with self.assertRaises(InvalidAnalysisInputError) as context:
            self.support.validate(factors, experts, cell_shape)
        return context.exception.public_message

    def test_validation_messages(self):
        """Test each validation rule's Qt message."""
        ok = SolverExpert("E", 1.0, np.zeros((2, 2)))
        self.assertEqual(self._message([], [ok]), "Factors list cannot be empty.")
        self.assertEqual(self._message(["A", "B"], []), "At least one expert must be provided.")
        self.assertEqual(
            self._message(["A", "B"], [SolverExpert("E", 1.5, np.zeros((2, 2)))]),
            "Each expert weight must be between 0 and 1.",
        )
        self.assertEqual(
            self._message(["A", "B"], [SolverExpert("E", 0.5, np.zeros((2, 2)))]), "Expert weights must sum to 1."
        )
        self.assertEqual(self._message(["A", "B"], [ok], (3,)), "Matrix for expert 'E' must have shape (2, 2, 3).")

    def test_normalize(self):
        """Test division by max(row sums, column sums) and the zero-scale error."""
        direct = np.array([[0.0, 2.0], [1.0, 0.0]])
        np.testing.assert_array_equal(self.support.normalize(direct, direct), direct / 2.0)
        with self.assertRaises(AnalysisFailedError) as context:
            self.support.normalize(np.zeros((2, 2)), np.zeros((2, 2)))
        self.assertEqual(context.exception.public_message, ALL_NO_INFLUENCE_MESSAGE)

    def test_total_singular(self):
        """Test a singular (I - X) raises the given message."""
        with self.assertRaises(AnalysisFailedError) as context:
            self.support.total(np.eye(2), "Failed to invert (I - X). Check the input matrices.")
        self.assertEqual(context.exception.public_message, "Failed to invert (I - X). Check the input matrices.")

    def test_split_cause_effect_zero_is_cause(self):
        """Test relation 0 belongs to the cause group."""
        cause, effect = self.support.split_cause_effect(["A", "B", "C"], np.array([0.0, -0.1, 0.2]))
        self.assertEqual((cause, effect), (["A", "C"], ["B"]))
