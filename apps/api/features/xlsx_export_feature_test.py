"""
Unit tests for XlsxExportFeature.

Tests cover:
- Cell formatting with 4 decimals
- Sheet prefixes per solver (Z keeps "Fuzzy"), via the shared sheet order
"""

import unittest
from io import BytesIO

import numpy as np
import pytest
from openpyxl import load_workbook

from features.xlsx_export_feature import XlsxExportFeature
from models.analysis_request_models import AnalysisRequest
from tests.parity_fixtures import parity_fixtures


@pytest.mark.unit
class TestXlsxExportFeature(unittest.TestCase):
    """Test cases for XlsxExportFeature."""

    def test_format_cell(self):
        """Test tuples are formatted like Qt's `_format_cell_value`."""
        feature = XlsxExportFeature()
        self.assertEqual(feature.format_cell(np.array([0.1, 0.25, 1 / 3])), "(0.1000, 0.2500, 0.3333)")
        self.assertEqual(feature.format_cell(np.array([0.0, 1.0])), "(0.0000, 1.0000)")

    def test_z_sheets_are_named_fuzzy(self):
        """Test the Z export keeps Qt's sheet names."""
        request = AnalysisRequest.model_validate(
            parity_fixtures.parity_case("small_z__fuzzy_z_dematel__mmde")["request"]
        )
        names = load_workbook(BytesIO(XlsxExportFeature().export_sync(request))).sheetnames
        self.assertEqual(names[0], "Fuzzy Direct Matrix")
        self.assertEqual(names[-2:], ["R_C_Scores", "Summary"])
