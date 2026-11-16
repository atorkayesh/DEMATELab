"""Conversions between numpy arrays and the nested float lists the API returns."""

from typing import Any, List

import numpy as np


class MatrixConverter:
    """Converts arrays to JSON-ready lists and computes the viewer's crisp matrix."""

    def to_lists(self, values: np.ndarray) -> Any:
        """
        Convert an array of any dimension into nested lists of Python floats.

        Args:
            values: Numeric array

        Returns:
            Any: `List[float]`, `List[List[float]]` or deeper, matching the array's shape
        """
        return np.asarray(values, dtype=float).tolist()

    def to_array(self, values: List[Any]) -> np.ndarray:
        """
        Convert nested lists into a float array.

        Args:
            values: Nested lists of numbers

        Returns:
            np.ndarray: Float array
        """
        return np.asarray(values, dtype=float)

    def crisp_2d(self, matrix: np.ndarray) -> np.ndarray:
        """
        Reduce a total matrix to `n x n` as the Qt viewer does (`_to_numeric_2d_array`).

        Fuzzy and grey cells are averaged over their components; crisp matrices are returned as floats.

        Args:
            matrix: `n x n`, `n x n x 3` or `n x n x 2` matrix

        Returns:
            np.ndarray: `n x n` matrix
        """
        array = np.asarray(matrix, dtype=float)
        if array.ndim == 3:
            return array.mean(axis=2)
        return array


matrix_converter = MatrixConverter()
