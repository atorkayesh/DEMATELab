"""
Unit tests for MatrixImportFeature.

Tests cover:
- Upload checks: extension, size limit (413), unreadable workbook
- Editor checks on names and matrices (messages from the Qt matrix editor)
- Blank expert names
"""

import unittest
from io import BytesIO

import pytest
from fastapi import UploadFile

from errors.import_errors import InvalidImportError, UnsupportedFileError, UploadTooLargeError
from features.matrix_import_feature import MatrixImportFeature
from tests.parity_fixtures import parity_fixtures


def upload(name: str, content: bytes) -> UploadFile:
    """Build an UploadFile."""
    return UploadFile(file=BytesIO(content), filename=name)


@pytest.mark.unit
class TestMatrixImportFeature(unittest.IsolatedAsyncioTestCase):
    """Test cases for MatrixImportFeature."""

    def setUp(self):
        """Create the feature and load a valid workbook."""
        self.feature = MatrixImportFeature()
        _, _, self.valid = next(item for item in parity_fixtures.imports() if item[0] == "matrix_plain_3x3")

    async def test_valid_upload(self):
        """Test a valid .xlsx upload."""
        data = await self.feature.import_matrix(upload("m.XLSX", self.valid), 3)
        self.assertEqual(data.matrix[0][0], "No influence")

    async def test_upload_checks(self):
        """Test extension, size, and content checks."""
        with self.assertRaises(UnsupportedFileError):
            await self.feature.import_matrix(upload("m.csv", self.valid), 3)
        with self.assertRaises(UploadTooLargeError):
            await MatrixImportFeature(max_bytes=10).import_matrix(upload("m.xlsx", self.valid), 3)
        with self.assertRaises(UnsupportedFileError):
            await self.feature.import_matrix(upload("m.xlsx", b"not a workbook"), 3)

    def test_editor_checks(self):
        """Test the matrix editor's messages for names and matrices."""
        checks = [
            (
                lambda: self.feature._check_factor_names(["A", "B"], 3),
                "Imported factor names must match the matrix size.",
            ),
            (lambda: self.feature._check_factor_names(["A", " "], 2), "Imported factor names cannot be blank."),
            (lambda: self.feature._check_factor_names(["A", "a"], 2), "Imported factor names must be unique."),
            (lambda: self.feature._check_matrix([["No influence"]], 2), "Imported matrix must be exactly 2 x 2."),
            (
                lambda: self.feature._check_matrix([["x", "Bad"], ["Low influence", "y"]], 2),
                "Unsupported imported value: Bad",
            ),
        ]
        for check, message in checks:
            with self.subTest(message=message):
                with self.assertRaises(InvalidImportError) as context:
                    check()
                self.assertEqual(context.exception.public_message, message)

    def test_blank_expert_name(self):
        """Test expert names must be filled."""
        with self.assertRaises(InvalidImportError):
            self.feature.import_workbook_bytes(self.valid, 3, [" "])
