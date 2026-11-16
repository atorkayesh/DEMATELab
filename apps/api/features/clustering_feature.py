"""
Four-group clustering of the total relation matrix, ported verbatim from `clustering_service.py:52-144`.

The off-diagonal cells are clustered with KMeans (4 clusters, `random_state=42`, `n_init="auto"`); clusters
are named by ascending centre (Low … High); the diagonal is -1 / "No influence".
"""

from typing import List

import numpy as np
from sklearn.cluster import KMeans

from constants.cluster_constants import CLUSTER_NAMES, CLUSTER_SETTINGS
from constants.linguistic_constants import NO_INFLUENCE_LABEL
from errors.analysis_errors import ClusteringFailedError
from models.solver_models import ClusterOutput


class ClusteringFeature:
    """Clusters the cells of a crisp total relation matrix."""

    CLUSTER_ERROR_PREFIX = "Could not generate cluster heatmap: "
    TOO_FEW_VALUES_MESSAGE = "At least 4 off-diagonal matrix values are required for 4-group clustering."

    def cluster(self, total_matrix: np.ndarray, factors: List[str]) -> ClusterOutput:
        """
        Cluster the off-diagonal cells.

        Args:
            total_matrix: `n x n` crisp total relation matrix (the viewer's matrix)
            factors: Factor names (must match the matrix size)

        Returns:
            ClusterOutput: Numeric labels (-1 on the diagonal) and named labels

        Raises:
            ClusteringFailedError: With the Qt message when the matrix is unusable or too small
        """
        matrix = np.asarray(total_matrix, dtype=float)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise self._error("total_matrix must be a square matrix.")
        if matrix.shape[0] == 0:
            raise self._error("total_matrix cannot be empty.")
        if len(factors) != matrix.shape[0]:
            raise self._error("factor_names length must match total_matrix size.")

        off_diagonal = ~np.eye(matrix.shape[0], dtype=bool)
        samples = np.asarray(matrix[off_diagonal], dtype=float).reshape(-1, 1)
        if samples.shape[0] < CLUSTER_SETTINGS["MIN_VALUES"]:
            raise self._error(self.TOO_FEW_VALUES_MESSAGE)

        model = KMeans(
            n_clusters=CLUSTER_SETTINGS["N_CLUSTERS"],
            random_state=CLUSTER_SETTINGS["RANDOM_STATE"],
            n_init=CLUSTER_SETTINGS["N_INIT"],
        )
        labels_flat = model.fit_predict(samples)
        ordered = np.argsort(np.asarray(model.cluster_centers_.ravel(), dtype=float))
        rank_names = {int(cluster_id): CLUSTER_NAMES[rank] for rank, cluster_id in enumerate(ordered)}

        labels_numeric = np.full(matrix.shape, CLUSTER_SETTINGS["DIAGONAL_CODE"], dtype=int)
        labels_numeric[off_diagonal] = labels_flat
        labels_named = np.full(matrix.shape, NO_INFLUENCE_LABEL, dtype=object)
        labels_named[off_diagonal] = [rank_names[int(label)] for label in labels_flat]
        return ClusterOutput(labels_numeric=labels_numeric, labels_named=labels_named)

    def _error(self, reason: str) -> ClusteringFailedError:
        """Wrap a Qt clustering message the way the heatmap warning shows it."""
        return ClusteringFailedError(reason, public_message=f"{self.CLUSTER_ERROR_PREFIX}{reason}")


clustering_feature = ClusteringFeature()
