"""
Unit tests for ExcelMatrixParser.

Tests cover:
- Plain and labelled sheets, trimmed cells, forced diagonal
- Qt messages with their source prefixes (sheet count, wrong size)
"""

import unittest
from io import BytesIO

import pytest
from openpyxl import Workbook

from errors.import_errors import InvalidImportError
from utils.excel_matrix_utils import ExcelMatrixParser


def workbook_bytes(sheets: dict) -> bytes:
    """Build workbook bytes from rows per sheet."""
    workbook = Workbook()
    workbook.remove(workbook.active)
    for name, rows in sheets.items():
        sheet = workbook.create_sheet(name)
        for row in rows:
            sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


BODY = [["High influence", " Low influence "], ["Medium influence", None]]


@pytest.mark.unit
class TestExcelMatrixParser(unittest.TestCase):
    """Test cases for ExcelMatrixParser."""

    def setUp(self):
        """Create the parser."""
        self.parser = ExcelMatrixParser()

    def test_plain_sheet(self):
        """Test an n x n sheet: trimmed labels, diagonal forced, no names."""
        names, matrix = self.parser.parse_sheet(workbook_bytes({"S": BODY}), 2)
        self.assertIsNone(names)
        self.assertEqual(matrix, [["No influence", "Low influence"], ["Medium influence", "No influence"]])

    def test_labelled_sheet(self):
        """Test an (n+1) x (n+1) sheet returns trimmed names."""
        rows = [[None, " A", "b"], ["a", *BODY[0]], ["B ", *BODY[1]]]
        names, _ = self.parser.parse_sheet(workbook_bytes({"S": rows}), 2)
        self.assertEqual(names, ["a", "B"])

    def test_sheet_count_message(self):
        """Test the sheet count message."""
        with self.assertRaises(InvalidImportError) as context:
            self.parser.parse_workbook(workbook_bytes({"S": BODY}), 2, 2)
        self.assertEqual(
            context.exception.public_message,
            "Uploaded workbook must contain exactly 2 sheets, one for each expert. Found 1.",
        )

    def test_wrong_size_message_has_sheet_prefix(self):
        """Test workbook errors name the sheet."""
        with self.assertRaises(InvalidImportError) as context:
            self.parser.parse_workbook(workbook_bytes({"Ann": BODY}), 3, 1)
        self.assertTrue(context.exception.public_message.startswith("Sheet 'Ann': Uploaded matrix must be either"))
