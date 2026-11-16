"""
Results summary numbers, from the Qt summary tab (`results_viewer_widget.py:439-789`).

The ranking uses `np.argsort(prominence)[::-1]` exactly as Qt, so ties keep Qt's reversed index order.
"""

import numpy as np

from constants.solver_constants import RESULT_TYPE_LABELS, THRESHOLD_LABELS
from models.solver_models import SolverOutput
from models.summary_models import ProminenceRankingItem, ResultSummary


class ResultSummaryFeature:
    """Builds the summary block of an analysis."""

    def summarize(self, output: SolverOutput) -> ResultSummary:
        """
        Compute the summary numbers.

        Args:
            output: Solver output

        Returns:
            ResultSummary: Labels, threshold, group sizes, top prominence, strongest relation, ranking
        """
        prominence = np.asarray(output.prominence, dtype=float)
        relation = np.asarray(output.relation, dtype=float)
        return ResultSummary(
            result_type_label=RESULT_TYPE_LABELS[output.solver_type],
            threshold_method_key=output.threshold_method,
            threshold_method_label=THRESHOLD_LABELS[output.threshold_method],
            threshold_value=float(output.threshold_value),
            driving_factor_count=len(output.cause_group),
            dependent_factor_count=len(output.effect_group),
            top_prominence=float(np.max(prominence)),
            strongest_relation=float(relation[int(np.argmax(np.abs(relation)))]),
            prominence_ranking=self._ranking(output.factors, prominence, relation),
        )

    def _ranking(self, factors: list, prominence: np.ndarray, relation: np.ndarray) -> list:
        """Rank factors by prominence (descending, Qt tie order) with each bar's share of the largest |prominence|."""
        max_prominence = float(np.max(np.abs(prominence))) if len(prominence) > 0 else 1.0
        return [
            ProminenceRankingItem(
                factor=factors[index],
                prominence=float(prominence[index]),
                relation=float(relation[index]),
                bar_ratio=float(prominence[index]) / max_prominence if max_prominence > 0 else 0.0,
            )
            for index in np.argsort(prominence)[::-1]
        ]


result_summary_feature = ResultSummaryFeature()
