"""
Grey DEMATEL engine, ported verbatim from `grey_dematel_core.py:109-294`.

Normalisation divides by the scale of the upper component only (kept from Qt).
"""

from typing import List, Optional, Sequence

import numpy as np

from constants.solver_constants import SolverType, ThresholdMethod
from errors.analysis_errors import InvalidAnalysisInputError
from features.threshold_feature import ThresholdFeature, threshold_feature
from models.solver_models import SolverExpert, SolverOutput
from utils.dematel_engine_utils import DematelEngineSupport, dematel_engine_support
from utils.interval_utils import IntervalMath, interval_math
from utils.matrix_utils import MatrixConverter, matrix_converter


class GreyDematelFeature:
    """Solves grey DEMATEL with interval numbers."""

    INVERSION_FAILED_MESSAGE = "Failed to invert (I - X) for grey DEMATEL."

    def __init__(
        self,
        threshold: Optional[ThresholdFeature] = None,
        support: Optional[DematelEngineSupport] = None,
        math: Optional[IntervalMath] = None,
        converter: Optional[MatrixConverter] = None,
    ):
        """
        Create the engine.

        Args:
            threshold: Threshold feature; defaults to the shared instance
            support: Shared engine steps; defaults to the shared instance
            math: Interval arithmetic; defaults to the shared instance
            converter: Matrix conversions; defaults to the shared instance
        """
        self._threshold = threshold or threshold_feature
        self._support = support or dematel_engine_support
        self._math = math or interval_math
        self._converter = converter or matrix_converter

    def solve(self, factors: List[str], experts: Sequence[SolverExpert], method: ThresholdMethod) -> SolverOutput:
        """
        Run grey DEMATEL.

        Args:
            factors: Factor names
            experts: Experts with `n x n x 2` matrices
            method: Threshold method (applied to the whitened total matrix)

        Returns:
            SolverOutput: Interval matrices and vectors, crisp scores, groups and threshold
        """
        names = [str(factor).strip() for factor in factors]
        size = len(names)
        self._support.validate(names, experts, (2,))
        self._check_order(experts)
        direct = self._support.weighted_sum(experts, (size, size, 2))
        normalized = self._support.normalize(direct, direct[:, :, 1])
        total = np.zeros((size, size, 2), dtype=float)
        for component in range(2):
            total[:, :, component] = self._support.total(normalized[:, :, component], self.INVERSION_FAILED_MESSAGE)
        raw_r = np.zeros((size, 2), dtype=float)
        raw_c = np.zeros((size, 2), dtype=float)
        for component in range(2):
            raw_r[:, component] = total[:, :, component].sum(axis=1)
            raw_c[:, component] = total[:, :, component].sum(axis=0)
        raw_prominence = self._math.add(raw_r, raw_c)
        raw_relation = self._math.subtract(raw_r, raw_c)
        relation = self._math.whiten(raw_relation)
        cause, effect = self._support.split_cause_effect(names, relation)
        return SolverOutput(
            solver_type=SolverType.GREY_DEMATEL,
            factors=names,
            expert_weights=[expert.weight for expert in experts],
            direct_matrix=direct,
            normalized_matrix=normalized,
            total_matrix=total,
            r=self._math.whiten(raw_r),
            c=self._math.whiten(raw_c),
            prominence=self._math.whiten(raw_prominence),
            relation=relation,
            cause_group=cause,
            effect_group=effect,
            threshold_method=method,
            threshold_value=self._threshold.compute(self._math.whiten(total), method),
            crisp_total_matrix=self._converter.crisp_2d(total),
            raw_r=raw_r,
            raw_c=raw_c,
            raw_prominence=raw_prominence,
            raw_relation=raw_relation,
        )

    def _check_order(self, experts: Sequence[SolverExpert]) -> None:
        """Reject matrices whose cells break lower <= upper (Qt message)."""
        for expert in experts:
            if np.any(expert.matrix[:, :, 0] > expert.matrix[:, :, 1]):
                raise InvalidAnalysisInputError(
                    public_message=f"Grey matrix for expert '{expert.name}' must satisfy lower <= upper."
                )


grey_dematel_feature = GreyDematelFeature()
