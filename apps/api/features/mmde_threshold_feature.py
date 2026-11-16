"""
Maximum Mean De-Entropy (MMDE) threshold, ported verbatim from `mmde_service.py:29-134`.

Edges are stable-sorted by value (descending); prefixes of the dispatch and receiver node sequences are
scored by mean de-entropy (natural log), the first maximum wins, and the threshold is the smallest total
matrix value over the selected dispatch x receiver pairs.
"""

from math import log
from typing import List, Sequence, Tuple

import numpy as np

from errors.analysis_errors import AnalysisFailedError, InvalidAnalysisInputError


class MmdeThresholdFeature:
    """Computes the MMDE threshold of a square matrix."""

    def compute(self, total_matrix: np.ndarray) -> float:
        """
        Compute the MMDE threshold.

        Args:
            total_matrix: Square crisp (or defuzzified/whitened) total relation matrix

        Returns:
            float: Threshold value

        Raises:
            InvalidAnalysisInputError: When the matrix is not square
            AnalysisFailedError: When no pair value can be selected
        """
        matrix = np.asarray(total_matrix, dtype=float)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise InvalidAnalysisInputError(public_message="MMDE requires a square matrix.")

        sorted_edges = self._sorted_edges_desc(matrix)
        dispatch_nodes = sorted(set(self._best_prefix([edge[1] for edge in sorted_edges])))
        receiver_nodes = sorted(set(self._best_prefix([edge[2] for edge in sorted_edges])))
        values = [float(matrix[d - 1, r - 1]) for d in dispatch_nodes for r in receiver_nodes]
        if not values:
            raise AnalysisFailedError(public_message="MMDE could not identify any pair values.")
        return float(min(values))

    def _sorted_edges_desc(self, matrix: np.ndarray) -> List[Tuple[float, int, int]]:
        """List every cell as (value, row, column), 1-based, stable-sorted by value descending."""
        size = matrix.shape[0]
        edges = [(float(matrix[i, j]), i + 1, j + 1) for i in range(size) for j in range(size)]
        edges.sort(key=lambda edge: edge[0], reverse=True)
        return edges

    def _best_prefix(self, node_sequence: List[int]) -> Tuple[int, ...]:
        """Return the prefix with the highest mean de-entropy (the first one on ties)."""
        prefixes = [tuple(node_sequence[:k]) for k in range(1, len(node_sequence) + 1)]
        scores = [self._mean_deentropy(prefix) for prefix in prefixes]
        return prefixes[int(np.argmax(scores))]

    def _mean_deentropy(self, prefix: Sequence[int]) -> float:
        """Return (max entropy - entropy) / number of distinct nodes for one prefix."""
        unique_count = len(set(prefix))
        if unique_count == 0:
            return 0.0
        length = len(prefix)
        probabilities = [prefix.count(value) / length for value in set(prefix)]
        entropy = -sum(p * log(p) for p in probabilities if p > 0)
        uniform = 1.0 / unique_count
        max_entropy = -unique_count * (uniform * log(uniform))
        return (max_entropy - entropy) / unique_count


mmde_threshold_feature = MmdeThresholdFeature()
