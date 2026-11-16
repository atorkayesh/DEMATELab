"""Classical DEMATEL engine, ported verbatim from `dematel_core.py:66-205`."""

from typing import List, Optional, Sequence

from constants.solver_constants import SolverType, ThresholdMethod
from features.threshold_feature import ThresholdFeature, threshold_feature
from models.solver_models import SolverExpert, SolverOutput
from utils.dematel_engine_utils import DematelEngineSupport, dematel_engine_support


class CrispDematelFeature:
    """Solves classical DEMATEL."""

    INVERSION_FAILED_MESSAGE = "Failed to invert (I - X). Check the input matrices."

    def __init__(self, threshold: Optional[ThresholdFeature] = None, support: Optional[DematelEngineSupport] = None):
        """
        Create the engine.

        Args:
            threshold: Threshold feature; defaults to the shared instance
            support: Shared engine steps; defaults to the shared instance
        """
        self._threshold = threshold or threshold_feature
        self._support = support or dematel_engine_support

    def solve(self, factors: List[str], experts: Sequence[SolverExpert], method: ThresholdMethod) -> SolverOutput:
        """
        Run classical DEMATEL.

        Args:
            factors: Factor names
            experts: Experts with `n x n` numeric matrices
            method: Threshold method

        Returns:
            SolverOutput: Matrices, scores, groups and threshold
        """
        names = [str(factor).strip() for factor in factors]
        size = len(names)
        self._support.validate(names, experts, ())
        direct = self._support.weighted_sum(experts, (size, size))
        normalized = self._support.normalize(direct, direct)
        total = self._support.total(normalized, self.INVERSION_FAILED_MESSAGE)
        r = total.sum(axis=1)
        c = total.sum(axis=0)
        prominence = r + c
        relation = r - c
        cause, effect = self._support.split_cause_effect(names, relation)
        return SolverOutput(
            solver_type=SolverType.DEMATEL,
            factors=names,
            expert_weights=[expert.weight for expert in experts],
            direct_matrix=direct,
            normalized_matrix=normalized,
            total_matrix=total,
            r=r,
            c=c,
            prominence=prominence,
            relation=relation,
            cause_group=cause,
            effect_group=effect,
            threshold_method=method,
            threshold_value=self._threshold.compute(total, method),
            crisp_total_matrix=total.astype(float),
        )


crisp_dematel_feature = CrispDematelFeature()
