"""
Steps shared by the three DEMATEL engines, ported from the identical copies in `dematel_core.py`,
`fuzzy_dematel_core.py` and `grey_dematel_core.py` (validation, weighted sum, normalisation, inversion,
cause/effect split). Messages are the Qt ones.
"""

from typing import List, Sequence, Tuple

import numpy as np

from errors.analysis_errors import AnalysisFailedError, InvalidAnalysisInputError
from models.solver_models import SolverExpert

ALL_NO_INFLUENCE_MESSAGE = (
    'All matrix cells are set to "No influence". Please assign at least one causal relationship before running '
    "the analysis."
)


class DematelEngineSupport:
    """Engine steps that do not depend on the number type (crisp, triangular, interval)."""

    def validate(self, factors: List[str], experts: Sequence[SolverExpert], cell_shape: Tuple[int, ...]) -> None:
        """
        Check factors, weights and matrix shapes as the Qt engines' `_validate` does.

        Args:
            factors: Trimmed factor names
            experts: Experts with numeric matrices
            cell_shape: `()` for crisp, `(3,)` for triangular, `(2,)` for interval cells

        Raises:
            InvalidAnalysisInputError: With the Qt message for the first failed rule
        """
        if not factors:
            raise InvalidAnalysisInputError(public_message="Factors list cannot be empty.")
        if not experts:
            raise InvalidAnalysisInputError(public_message="At least one expert must be provided.")
        weights = [expert.weight for expert in experts]
        if any(weight < 0 or weight > 1 for weight in weights):
            raise InvalidAnalysisInputError(public_message="Each expert weight must be between 0 and 1.")
        if not np.isclose(sum(weights), 1.0, atol=1e-8):
            raise InvalidAnalysisInputError(public_message="Expert weights must sum to 1.")
        size = len(factors)
        expected = (size, size, *cell_shape)
        shape_text = ", ".join(str(part) for part in expected)
        for expert in experts:
            if expert.matrix.shape != expected:
                raise InvalidAnalysisInputError(
                    public_message=f"Matrix for expert '{expert.name}' must have shape ({shape_text})."
                )

    def weighted_sum(self, experts: Sequence[SolverExpert], shape: Tuple[int, ...]) -> np.ndarray:
        """
        Sum the weighted expert matrices in expert order.

        Args:
            experts: Experts with numeric matrices
            shape: Shape of every matrix

        Returns:
            np.ndarray: Weighted direct matrix
        """
        weighted = np.zeros(shape, dtype=float)
        for expert in experts:
            weighted += expert.weight * expert.matrix
        return weighted

    def normalize(self, direct: np.ndarray, scale_source: np.ndarray) -> np.ndarray:
        """
        Divide by the largest row or column sum of `scale_source` (the upper component for fuzzy and grey).

        Args:
            direct: Weighted direct matrix
            scale_source: `n x n` matrix whose sums give the scale

        Returns:
            np.ndarray: Normalised matrix

        Raises:
            AnalysisFailedError: When every cell is "No influence" (scale 0)
        """
        scale = max(scale_source.sum(axis=1).max(), scale_source.sum(axis=0).max())
        if np.isclose(scale, 0.0):
            raise AnalysisFailedError(public_message=ALL_NO_INFLUENCE_MESSAGE)
        return direct / scale

    def total(self, normalized: np.ndarray, failure_message: str) -> np.ndarray:
        """
        Compute X (I - X)^-1 for one `n x n` component.

        Args:
            normalized: Normalised `n x n` matrix
            failure_message: Qt message when the inversion fails

        Returns:
            np.ndarray: Total relation matrix

        Raises:
            AnalysisFailedError: When (I - X) is singular
        """
        identity = np.eye(normalized.shape[0])
        try:
            inverse = np.linalg.inv(identity - normalized)
        except np.linalg.LinAlgError as exc:
            raise AnalysisFailedError(f"{failure_message} ({exc})", public_message=failure_message) from exc
        return normalized @ inverse

    def split_cause_effect(self, factors: Sequence[str], relation: np.ndarray) -> Tuple[List[str], List[str]]:
        """
        Split factors into the cause group (relation >= 0) and the effect group (relation < 0).

        Args:
            factors: Factor names
            relation: Crisp relation values

        Returns:
            Tuple[List[str], List[str]]: Cause group, effect group
        """
        cause = [factor for factor, value in zip(factors, relation, strict=True) if value >= 0]
        effect = [factor for factor, value in zip(factors, relation, strict=True) if value < 0]
        return cause, effect


dematel_engine_support = DematelEngineSupport()
