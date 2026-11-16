"""
Unit tests for ResultSummaryFeature.

Tests cover:
- Labels (result type, threshold key and label), counts, top prominence
- Strongest relation keeps its sign; ranking follows Qt's tie order; bar ratios
"""

import unittest

import numpy as np
import pytest

from constants.solver_constants import SolverType, ThresholdMethod
from features.result_summary_feature import ResultSummaryFeature
from models.solver_models import SolverOutput


def output(prominence, relation) -> SolverOutput:
    """Build a minimal solver output."""
    empty = np.zeros((3, 3))
    return SolverOutput(
        solver_type=SolverType.GREY_DEMATEL,
        factors=["A", "B", "C"],
        expert_weights=[1.0],
        direct_matrix=empty,
        normalized_matrix=empty,
        total_matrix=empty,
        r=np.zeros(3),
        c=np.zeros(3),
        prominence=np.array(prominence, dtype=float),
        relation=np.array(relation, dtype=float),
        cause_group=["A", "C"],
        effect_group=["B"],
        threshold_method=ThresholdMethod.MMDE,
        threshold_value=0.25,
        crisp_total_matrix=empty,
    )


@pytest.mark.unit
class TestResultSummaryFeature(unittest.TestCase):
    """Test cases for ResultSummaryFeature."""

    def test_summary(self):
        """Test labels, counts, strongest relation and ranking."""
        summary = ResultSummaryFeature().summarize(output([2.0, 4.0, 2.0], [0.1, -0.5, 0.3]))

        self.assertEqual(summary.result_type_label, "Grey DEMATEL")
        self.assertEqual(
            (summary.threshold_method_key, summary.threshold_method_label), ("mmde", "Maximum Mean De-Entropy")
        )
        self.assertEqual((summary.driving_factor_count, summary.dependent_factor_count), (2, 1))
        self.assertEqual(summary.top_prominence, 4.0)
        self.assertEqual(summary.strongest_relation, -0.5)
        self.assertEqual([item.factor for item in summary.prominence_ranking], ["B", "C", "A"])
        self.assertEqual([item.bar_ratio for item in summary.prominence_ranking], [1.0, 0.5, 0.5])

    def test_zero_prominence_bar_ratio(self):
        """Test bars are 0 when the largest prominence is 0."""
        summary = ResultSummaryFeature().summarize(output([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]))
        self.assertEqual({item.bar_ratio for item in summary.prominence_ranking}, {0.0})
