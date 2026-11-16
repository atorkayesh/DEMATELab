"""
Unit tests for CausalDiagramChartFeature.

Tests cover:
- PNG output for every solver at both resolutions
- Nodes are green only for relation > 0 (Qt's colour rule)
"""

import unittest

import pytest

from features.analysis_feature import analysis_feature
from features.causal_diagram_chart_feature import CausalDiagramChartFeature
from models.analysis_request_models import AnalysisRequest
from tests.parity_fixtures import parity_fixtures

CASES = [
    "small__dematel__average",
    "small__fuzzy_dematel__mmde",
    "small__grey_dematel__median",
    "small_z__fuzzy_z_dematel__first_quartile",
]


@pytest.mark.unit
class TestCausalDiagramChartFeature(unittest.TestCase):
    """Test cases for CausalDiagramChartFeature."""

    def test_png_for_every_solver(self):
        """Test PNG bytes for every solver at 100 and 300 dpi."""
        feature = CausalDiagramChartFeature()
        for name in CASES:
            request = AnalysisRequest.model_validate(parity_fixtures.parity_case(name)["request"])
            for dpi in (100, 300):
                with self.subTest(case=name, dpi=dpi):
                    self.assertTrue(feature.render_sync(request, dpi).startswith(b"\x89PNG"))

    def test_node_colours(self):
        """Test cause (relation > 0) nodes are green and the others red."""
        request = AnalysisRequest.model_validate(parity_fixtures.parity_case(CASES[0])["request"])
        output = analysis_feature.solve(request)
        figure = CausalDiagramChartFeature().draw(output)
        colours = figure.axes[0].collections[0].get_facecolors()
        for relation, colour in zip(output.relation, colours, strict=True):
            self.assertEqual(colour[1] > 0.4, relation > 0)
