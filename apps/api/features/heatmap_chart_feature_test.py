"""
Unit tests for HeatmapChartFeature.

Tests cover:
- Standard and cluster PNGs for every solver at both resolutions
- Cluster cells are coloured by the rank of their label (matches the colourbar)
- Titles; cluster mode fails with ClusteringFailedError instead of falling back
"""

import unittest

import numpy as np
import pytest

from constants.cluster_constants import CLUSTER_NAMES
from constants.linguistic_constants import NO_INFLUENCE_LABEL
from errors.analysis_errors import ClusteringFailedError
from features.analysis_feature import analysis_feature
from features.heatmap_chart_feature import HeatmapChartFeature, HeatmapMode
from models.analysis_request_models import AnalysisRequest
from tests.parity_fixtures import parity_fixtures

CASES = [
    "weights3__dematel__average",
    "weights3__fuzzy_dematel__mmde",
    "weights3__grey_dematel__median",
    "weights3_z__fuzzy_z_dematel__first_quartile",
]


def load(name: str) -> AnalysisRequest:
    """Load a fixture request."""
    return AnalysisRequest.model_validate(parity_fixtures.parity_case(name)["request"])


@pytest.mark.unit
class TestHeatmapChartFeature(unittest.TestCase):
    """Test cases for HeatmapChartFeature."""

    def test_png_for_every_solver_and_mode(self):
        """Test both modes and resolutions."""
        feature = HeatmapChartFeature()
        for name in CASES:
            for mode in HeatmapMode:
                for dpi in (100, 300):
                    with self.subTest(case=name, mode=mode, dpi=dpi):
                        self.assertTrue(feature.render_sync(load(name), mode, dpi).startswith(b"\x89PNG"))

    def test_titles(self):
        """Test the Qt titles."""
        output = analysis_feature.solve(load(CASES[0]))
        feature = HeatmapChartFeature()
        self.assertEqual(
            feature.draw(output, HeatmapMode.STANDARD).axes[0].get_title(), "Total Relation Matrix Heatmap"
        )
        self.assertEqual(feature.draw(output, HeatmapMode.CLUSTER).axes[0].get_title(), "Cluster-Based Heatmap")

    def test_cluster_colours_match_labels(self):
        """Test every cell's colour index equals the colourbar index of its ranked label."""
        legend = [NO_INFLUENCE_LABEL, *CLUSTER_NAMES]
        feature = HeatmapChartFeature()
        for name in CASES:
            with self.subTest(case=name):
                output = analysis_feature.solve(load(name))
                figure = feature.draw(output, HeatmapMode.CLUSTER)
                codes = figure.axes[0].images[0].get_array()
                named = feature._clustering.cluster(output.crisp_total_matrix, output.factors).labels_named
                for (row, col), label in np.ndenumerate(named):
                    self.assertEqual(int(codes[row, col]), legend.index(label))
                self.assertEqual([t.get_text() for t in figure.axes[1].get_yticklabels()], legend)

    def test_cluster_failure(self):
        """Test a 2-factor cluster heatmap raises instead of drawing the standard heatmap."""
        with self.assertRaises(ClusteringFailedError):
            HeatmapChartFeature().render_sync(load("two_factors__dematel__average"), HeatmapMode.CLUSTER, 100)
