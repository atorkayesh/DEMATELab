"""
Unit tests for ClusteringFeature.

Tests cover:
- Diagonal is -1 / "No influence"; clusters named by ascending centre
- Fewer than 4 off-diagonal values gives the Qt message
"""

import unittest

import numpy as np
import pytest

from errors.analysis_errors import ClusteringFailedError
from features.clustering_feature import ClusteringFeature


@pytest.mark.unit
class TestClusteringFeature(unittest.TestCase):
    """Test cases for ClusteringFeature."""

    def test_clusters_ranked_by_value(self):
        """Test the smallest values are Low and the largest High."""
        matrix = np.array([[9.0, 0.1, 0.2], [1.0, 9.0, 2.0], [3.0, 3.1, 9.0]])
        clusters = ClusteringFeature().cluster(matrix, ["A", "B", "C"])

        self.assertEqual(clusters.labels_numeric[0, 0], -1)
        self.assertEqual(clusters.labels_named[1, 1], "No influence")
        self.assertEqual(clusters.labels_named[0, 1], "Low")
        self.assertEqual(clusters.labels_named[2, 1], "High")

    def test_too_few_values(self):
        """Test the 2-factor case fails with Qt's message."""
        with self.assertRaises(ClusteringFailedError) as context:
            ClusteringFeature().cluster(np.eye(2), ["A", "B"])
        self.assertEqual(
            context.exception.public_message,
            "Could not generate cluster heatmap: At least 4 off-diagonal matrix values are required for 4-group "
            "clustering.",
        )
