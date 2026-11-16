"""
Excel matrix imports: one sheet for one expert, or a workbook with one sheet per expert.

Ports the Qt import flow: the parsers (`utils/excel_matrix_utils.py`), the editor checks on imported names
and matrices (`matrix_editor_widget.py:370-378,451-468`), and the workbook → expert mapping
(`matrix_editor_widget.py:640-656`: by name when every expert name matches a sheet name, trimmed and
case-insensitive; otherwise by order).
"""

import asyncio
import zipfile
from io import BytesIO
from typing import Dict, List, Optional

from fastapi import UploadFile
from openpyxl import load_workbook

from constants.import_constants import IMPORT_SETTINGS
from constants.linguistic_constants import LINGUISTIC_TERMS, NO_INFLUENCE_LABEL
from errors.import_errors import InvalidImportError, UnsupportedFileError, UploadTooLargeError
from models.import_models import ExpertMatrix, MatrixImportData, WorkbookImportData
from utils.excel_matrix_utils import ExcelMatrixParser, LabelMatrix, excel_matrix_parser


class MatrixImportFeature:
    """Reads uploaded workbooks into linguistic matrices."""

    def __init__(
        self, parser: Optional[ExcelMatrixParser] = None, max_bytes: int = IMPORT_SETTINGS["MAX_UPLOAD_BYTES"]
    ):
        """
        Create the feature.

        Args:
            parser: Excel parser; defaults to the shared instance
            max_bytes: Largest accepted upload
        """
        self._parser = parser or excel_matrix_parser
        self._max_bytes = max_bytes

    async def import_matrix(self, file: UploadFile, factor_count: int) -> MatrixImportData:
        """
        Import the first sheet as one expert's matrix.

        Args:
            file: Uploaded `.xlsx` file
            factor_count: Number of factors

        Returns:
            MatrixImportData: Factor names (if the sheet has them) and the matrix
        """
        content = await self._read(file)
        return await asyncio.to_thread(self.import_matrix_bytes, content, factor_count)

    async def import_workbook(self, file: UploadFile, factor_count: int, expert_names: List[str]) -> WorkbookImportData:
        """
        Import one sheet per expert.

        Args:
            file: Uploaded `.xlsx` file
            factor_count: Number of factors
            expert_names: Expert names in GUI order

        Returns:
            WorkbookImportData: Factor names, one matrix per expert, and how sheets were matched
        """
        content = await self._read(file)
        return await asyncio.to_thread(self.import_workbook_bytes, content, factor_count, expert_names)

    def import_matrix_bytes(self, content: bytes, factor_count: int) -> MatrixImportData:
        """
        Import the first sheet of workbook bytes.

        Args:
            content: Workbook bytes
            factor_count: Number of factors

        Returns:
            MatrixImportData: Factor names (if any) and the matrix

        Raises:
            InvalidImportError: With the Qt parser or editor message
        """
        factor_names, matrix = self._parser.parse_sheet(content, factor_count)
        names = self._check_factor_names(factor_names, factor_count)
        return MatrixImportData(factor_names=names, matrix=self._check_matrix(matrix, factor_count))

    def import_workbook_bytes(self, content: bytes, factor_count: int, expert_names: List[str]) -> WorkbookImportData:
        """
        Import every sheet of workbook bytes and assign them to experts.

        Args:
            content: Workbook bytes
            factor_count: Number of factors
            expert_names: Expert names in GUI order

        Returns:
            WorkbookImportData: Factor names (if any), one matrix per expert, and `matched_by`

        Raises:
            InvalidImportError: With the Qt parser or editor message
        """
        if any(not name.strip() for name in expert_names):
            raise InvalidImportError(public_message="All expert names must be filled.")
        factor_names, sheets = self._parser.parse_workbook(content, factor_count, len(expert_names))
        names = self._check_factor_names(factor_names, factor_count)
        by_sheet: Dict[str, LabelMatrix] = {sheet.strip().casefold(): matrix for sheet, matrix in sheets.items()}
        keys = [name.strip().casefold() for name in expert_names]
        matched_by_name = all(key in by_sheet for key in keys)
        ordered = [by_sheet[key] for key in keys] if matched_by_name else list(sheets.values())
        return WorkbookImportData(
            factor_names=names,
            matrices=[
                ExpertMatrix(expert_name=name, matrix=self._check_matrix(matrix, factor_count))
                for name, matrix in zip(expert_names, ordered, strict=True)
            ],
            matched_by="name" if matched_by_name else "order",
        )

    async def _read(self, file: UploadFile) -> bytes:
        """Read an upload, enforcing the size limit and checking it is an `.xlsx` workbook."""
        filename = (file.filename or "").lower()
        if not filename.endswith(IMPORT_SETTINGS["ALLOWED_EXTENSIONS"]):
            raise UnsupportedFileError(f"Rejected upload {file.filename!r}")
        content = await file.read(self._max_bytes + 1)
        if len(content) > self._max_bytes:
            raise UploadTooLargeError(f"Upload {file.filename!r} exceeds {self._max_bytes} bytes")
        try:
            load_workbook(BytesIO(content), read_only=True).close()
        except (zipfile.BadZipFile, KeyError, OSError, ValueError) as exc:
            raise UnsupportedFileError(f"openpyxl could not read {file.filename!r}: {exc}") from exc
        return content

    def _check_factor_names(self, factor_names: Optional[List[str]], factor_count: int) -> Optional[List[str]]:
        """Apply the editor's checks to imported factor names (`update_factor_names`)."""
        if factor_names is None:
            return None
        if len(factor_names) != factor_count:
            raise InvalidImportError(public_message="Imported factor names must match the matrix size.")
        cleaned = [str(name).strip() for name in factor_names]
        if any(not name for name in cleaned):
            raise InvalidImportError(public_message="Imported factor names cannot be blank.")
        if len({name.casefold() for name in cleaned}) != len(cleaned):
            raise InvalidImportError(public_message="Imported factor names must be unique.")
        return cleaned

    def _check_matrix(self, matrix: LabelMatrix, factor_count: int) -> LabelMatrix:
        """Apply the editor's `set_matrix` checks and force the diagonal to "No influence"."""
        if len(matrix) != factor_count or any(len(row) != factor_count for row in matrix):
            raise InvalidImportError(public_message=f"Imported matrix must be exactly {factor_count} x {factor_count}.")
        checked: LabelMatrix = []
        for i, row in enumerate(matrix):
            checked_row = []
            for j, value in enumerate(row):
                if i == j:
                    checked_row.append(NO_INFLUENCE_LABEL)
                    continue
                if value not in LINGUISTIC_TERMS:
                    raise InvalidImportError(public_message=f"Unsupported imported value: {value}")
                checked_row.append(value)
            checked.append(checked_row)
        return checked


matrix_import_feature = MatrixImportFeature()
