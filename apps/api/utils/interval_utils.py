"""
Grey interval arithmetic, ported verbatim from `grey_dematel_core.py:69-106`.

Arrays hold (lower, upper) in their last dimension. Never change a formula without regenerating the parity
fixtures from `qt-app/`.
"""

import numpy as np

from errors.analysis_errors import InvalidAnalysisInputError


class IntervalMath:
    """Addition, subtraction, and whitening of grey intervals."""

    def add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Add row-wise: [aL, aU] + [bL, bU] = [aL + bL, aU + bU].

        Args:
            a: `n x 2` intervals
            b: `n x 2` intervals

        Returns:
            np.ndarray: `n x 2` sums
        """
        result = np.zeros_like(a, dtype=float)
        result[:, 0] = a[:, 0] + b[:, 0]
        result[:, 1] = a[:, 1] + b[:, 1]
        return result

    def subtract(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Subtract row-wise: [aL, aU] - [bL, bU] = [aL - bU, aU - bL].

        Args:
            a: `n x 2` intervals
            b: `n x 2` intervals

        Returns:
            np.ndarray: `n x 2` differences
        """
        result = np.zeros_like(a, dtype=float)
        result[:, 0] = a[:, 0] - b[:, 1]
        result[:, 1] = a[:, 1] - b[:, 0]
        return result

    def whiten(self, values: np.ndarray) -> np.ndarray:
        """
        Whiten with (lower + upper) / 2.

        Args:
            values: Intervals with last dimension 2 (1, 2 or 3 dimensions)

        Returns:
            np.ndarray: Crisp values with the last dimension removed

        Raises:
            InvalidAnalysisInputError: When the last dimension is not 2
        """
        if values.ndim == 1 and values.shape[0] == 2:
            lower, upper = values
            return np.array((lower + upper) / 2, dtype=float)
        if values.ndim in (2, 3) and values.shape[-1] == 2:
            return (values[..., 0] + values[..., 1]) / 2
        raise InvalidAnalysisInputError(public_message="Input must be grey interval values with last dimension size 2.")


interval_math = IntervalMath()
