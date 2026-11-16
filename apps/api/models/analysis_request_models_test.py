"""
Unit tests for AnalysisRequest validation (Settled Decision 5).

Tests cover:
- Solver and threshold aliases; unknown values; blank threshold
- Factor names trimmed, required, unique case-sensitively; expert names trimmed and required, duplicates allowed
- Factor and expert limits; weight range; matrix shape
"""

import unittest

import pytest
from pydantic import ValidationError

from models.analysis_request_models import AnalysisRequest

N = "No influence"


def body(**overrides) -> dict:
    """Build a valid request body with overrides."""
    data = {
        "solver_type": "dematel",
        "threshold_method": "average",
        "factors": ["A", "B"],
        "experts": [{"name": "E", "weight": 1.0, "matrix": [[N, N], [N, N]]}],
    }
    return {**data, **overrides}


@pytest.mark.unit
class TestAnalysisRequest(unittest.TestCase):
    """Test cases for AnalysisRequest."""

    def _error(self, **overrides) -> str:
        with self.assertRaises(ValidationError) as context:
            AnalysisRequest.model_validate(body(**overrides))
        return str(context.exception)

    def test_aliases(self):
        """Test the Qt aliases and GUI labels."""
        cases = {"Fuzzy Z-DEMATEL": "fuzzy_z_dematel", "fz-dematel": "fuzzy_z_dematel", "Grey DEMATEL": "grey_dematel"}
        for alias, solver in cases.items():
            self.assertEqual(AnalysisRequest.model_validate(body(solver_type=alias)).solver_type, solver)
        request = AnalysisRequest.model_validate(body(threshold_method="Maximum Mean De-Entropy"))
        self.assertEqual(request.threshold_method, "mmde")
        self.assertEqual(
            AnalysisRequest.model_validate(body(threshold_method="First quartile")).threshold_method, "first_quartile"
        )

    def test_unknown_and_blank_choices(self):
        """Test unknown solver/threshold and a blank threshold."""
        self.assertIn("Unsupported solver type: topsis", self._error(solver_type="topsis"))
        self.assertIn("Unsupported threshold method: max", self._error(threshold_method="max"))
        self.assertIn("Please select a threshold method", self._error(threshold_method=" "))

    def test_factor_names(self):
        """Test trimming, blank and case-sensitive uniqueness."""
        self.assertEqual(AnalysisRequest.model_validate(body(factors=[" A ", "a"])).factors, ["A", "a"])
        self.assertIn("All factor names must be filled.", self._error(factors=["A", " "]))
        self.assertIn("Factor names must be unique.", self._error(factors=["A", "A "]))

    def test_expert_names(self):
        """Test trimming, blanks rejected, duplicates allowed."""
        expert = {"name": " E ", "weight": 0.5, "matrix": [[N, N], [N, N]]}
        request = AnalysisRequest.model_validate(body(experts=[expert, expert]))
        self.assertEqual([e.name for e in request.experts], ["E", "E"])
        self.assertIn("All expert names must be filled.", self._error(experts=[{**expert, "name": ""}]))

    def test_limits_and_shapes(self):
        """Test factor and expert counts, weight range, and matrix shape."""
        self._error(factors=["A"])
        self._error(factors=[f"F{i}" for i in range(101)])
        self._error(experts=[])
        self._error(experts=[{"name": "E", "weight": 1.2, "matrix": [[N, N], [N, N]]}])
        self.assertIn("must have shape (2, 2)", self._error(experts=[{"name": "E", "weight": 1, "matrix": [[N]]}]))
