"""
Threshold methods, ported from the three identical `compute_threshold` methods of the Qt engines
(`dematel_core.py:150-175`): applied to the whole crisp/defuzzified/whitened total matrix, diagonal included.
"""

from typing import Optional

import numpy as np

from constants.solver_constants import ThresholdMethod
from errors.analysis_errors import InvalidAnalysisInputError
from features.mmde_threshold_feature import MmdeThresholdFeature, mmde_threshold_feature


class ThresholdFeature:
    """Computes the threshold value of a total relation matrix."""

    def __init__(self, mmde: Optional[MmdeThresholdFeature] = None):
        """
        Create the feature.

        Args:
            mmde: MMDE implementation; defaults to the shared instance
        """
        self._mmde = mmde or mmde_threshold_feature

    def compute(self, matrix: np.ndarray, method: ThresholdMethod) -> float:
        """
        Compute the threshold.

        Args:
            matrix: `n x n` crisp total relation matrix
            method: Threshold method

        Returns:
            float: Threshold value

        Raises:
            InvalidAnalysisInputError: When the matrix is empty
        """
        values = matrix.flatten()
        if values.size == 0:
            raise InvalidAnalysisInputError(public_message="Threshold calculation requires matrix values.")
        if method == ThresholdMethod.AVERAGE:
            return float(np.mean(values))
        if method == ThresholdMethod.FIRST_QUARTILE:
            return float(np.quantile(values, 0.25))
        if method == ThresholdMethod.MEDIAN:
            return float(np.median(values))
        if method == ThresholdMethod.THIRD_QUARTILE:
            return float(np.quantile(values, 0.75))
        return self._mmde.compute(matrix)


threshold_feature = ThresholdFeature()
