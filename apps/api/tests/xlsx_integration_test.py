"""
XLSX export against workbooks exported by the Qt viewer itself (crisp, fuzzy, grey, fuzzy Z).

Tests cover:
- Sheet names and order, headers, every cell value, through the feature and the HTTP download
"""

import unittest
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook

from features.xlsx_export_feature import xlsx_export_feature
from main import app
from models.analysis_request_models import AnalysisRequest
from tests.parity_fixtures import parity_fixtures

CASES = {
    "small__dematel__mmde": ["Direct Matrix", "Normalized Matrix", "Total Relation Matrix"],
    "small__fuzzy_dematel__average": ["Fuzzy Direct Matrix", "Fuzzy Normalized Matrix", "Fuzzy Total Relation Matrix"],
    "small__grey_dematel__median": ["Grey Direct Matrix", "Grey Normalized Matrix", "Grey Total Relation Matrix"],
    "small_z__fuzzy_z_dematel__third_quartile": [
        "Fuzzy Direct Matrix",
        "Fuzzy Normalized Matrix",
        "Fuzzy Total Relation Matrix",
    ],
}


def assert_same_cells(test: unittest.TestCase, mine, qt) -> None:
    """Compare every cell: strings and layout exactly, numbers within 1e-12 (BLAS rounding between platforms)."""
    for name in qt.sheetnames:
        mine_rows, qt_rows = cell_values(mine)[name], cell_values(qt)[name]
        test.assertEqual(len(mine_rows), len(qt_rows), name)
        for mine_row, qt_row in zip(mine_rows, qt_rows, strict=True):
            test.assertEqual(len(mine_row), len(qt_row), name)
            for mine_cell, qt_cell in zip(mine_row, qt_row, strict=True):
                if isinstance(qt_cell, float):
                    test.assertAlmostEqual(mine_cell, qt_cell, delta=1e-12, msg=name)
                else:
                    test.assertEqual(mine_cell, qt_cell, name)


def cell_values(workbook) -> dict:
    """Return every sheet's values row by row."""
    return {name: [[cell.value for cell in row] for row in workbook[name].iter_rows()] for name in workbook.sheetnames}


@pytest.mark.integration
class TestXlsxExport(unittest.TestCase):
    """The API workbook equals the Qt workbook."""

    def test_feature_equals_qt_export(self):
        """Test sheet order and every cell against the Qt export."""
        for name, matrix_sheets in CASES.items():
            with self.subTest(case=name):
                request = AnalysisRequest.model_validate(parity_fixtures.parity_case(name)["request"])
                mine = load_workbook(BytesIO(xlsx_export_feature.export_sync(request)))
                qt = load_workbook(parity_fixtures.xlsx_path(name))
                self.assertEqual(mine.sheetnames, [*matrix_sheets, "R_C_Scores", "Summary"])
                self.assertEqual(mine.sheetnames, qt.sheetnames)
                assert_same_cells(self, mine, qt)

    def test_layout_details(self):
        """Test headers, the summary rows with the method key, and the crisp-in-brackets cells."""
        fuzzy = parity_fixtures.parity_case("small__fuzzy_dematel__average")
        sheets = cell_values(
            load_workbook(BytesIO(xlsx_export_feature.export_sync(AnalysisRequest.model_validate(fuzzy["request"]))))
        )
        self.assertEqual(sheets["R_C_Scores"][0], ["Factor", "R", "C", "Prominence", "Relation"])
        self.assertRegex(sheets["R_C_Scores"][1][3], r"^\(-?\d+\.\d{4}, -?\d+\.\d{4}, -?\d+\.\d{4}\) \(-?\d+\.\d{4}\)$")
        self.assertEqual(
            [row[0] for row in sheets["Summary"]],
            ["Item", "Threshold Method", "Threshold Value", "Cause Group", "Effect Group"],
        )
        self.assertEqual(sheets["Summary"][1][1], "average")
        crisp = parity_fixtures.parity_case("small__dematel__mmde")
        crisp_sheets = cell_values(
            load_workbook(BytesIO(xlsx_export_feature.export_sync(AnalysisRequest.model_validate(crisp["request"]))))
        )
        self.assertEqual(crisp_sheets["R_C_Scores"][0], ["Factor", "R", "C", "R+C", "R-C"])
        self.assertEqual(crisp_sheets["Total Relation Matrix"][0], [None, "Cost", "Quality", "Time"])
        for written, expected in zip(
            crisp_sheets["Total Relation Matrix"][1][1:], crisp["result"]["total_matrix"][0], strict=True
        ):
            self.assertAlmostEqual(written, expected, places=12)

    def test_http_download(self):
        """Test the endpoint returns the workbook as an attachment."""
        request = parity_fixtures.parity_case("small__grey_dematel__median")["request"]
        response = TestClient(app).post("/api/v1/analysis/export/xlsx", json=request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-disposition"], 'attachment; filename="dematel_results.xlsx"')
        self.assertIn("spreadsheetml", response.headers["content-type"])
        self.assertEqual(load_workbook(BytesIO(response.content)).sheetnames[0], "Grey Direct Matrix")
