"""
Triangular fuzzy number arithmetic, ported verbatim from `fuzzy_dematel_core.py:69-110`.

Arrays hold (l, m, u) in their last dimension. Never change a formula without regenerating the parity
fixtures from `qt-app/`.
"""

import numpy as np

from errors.analysis_errors import InvalidAnalysisInputError


class TriangularMath:
    """Addition, subtraction, and defuzzification of triangular fuzzy numbers."""

    def add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Add row-wise: (l1, m1, u1) + (l2, m2, u2) = (l1+l2, m1+m2, u1+u2).

        Args:
            a: `n x 3` values
            b: `n x 3` values

        Returns:
            np.ndarray: `n x 3` sums
        """
        result = np.zeros_like(a, dtype=float)
        result[:, 0] = a[:, 0] + b[:, 0]
        result[:, 1] = a[:, 1] + b[:, 1]
        result[:, 2] = a[:, 2] + b[:, 2]
        return result

    def subtract(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Subtract row-wise: (l1, m1, u1) - (l2, m2, u2) = (l1-u2, m1-m2, u1-l2).

        Args:
            a: `n x 3` values
            b: `n x 3` values

        Returns:
            np.ndarray: `n x 3` differences
        """
        result = np.zeros_like(a, dtype=float)
        result[:, 0] = a[:, 0] - b[:, 2]
        result[:, 1] = a[:, 1] - b[:, 1]
        result[:, 2] = a[:, 2] - b[:, 0]
        return result

    def defuzzify(self, values: np.ndarray) -> np.ndarray:
        """
        Defuzzify with l + ((u - l) + (m - l)) / 3.

        Args:
            values: Triangular values with last dimension 3 (1, 2 or 3 dimensions)

        Returns:
            np.ndarray: Crisp values with the last dimension removed

        Raises:
            InvalidAnalysisInputError: When the last dimension is not 3
        """
        if values.ndim == 1 and values.shape[0] == 3:
            low, mid, up = values
            return np.array(low + ((up - low) + (mid - low)) / 3, dtype=float)
        if values.ndim in (2, 3) and values.shape[-1] == 3:
            low = values[..., 0]
            mid = values[..., 1]
            up = values[..., 2]
            return low + ((up - low) + (mid - low)) / 3
        raise InvalidAnalysisInputError(
            public_message="Input must be triangular fuzzy values with last dimension size 3."
        )


triangular_math = TriangularMath()
