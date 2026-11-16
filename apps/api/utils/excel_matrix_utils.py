"""
Excel matrix parsing, ported from `matrix_parsers.py:21-150,266-348` with the same rules and messages.

A sheet holds either an `n x n` body or an `(n+1) x (n+1)` matrix whose first row and column hold the factor
names (compared case-insensitively). Cells are trimmed; off-diagonal cells must be standard labels; the
diagonal becomes "No influence". Messages carry the Qt `{source}: ` prefixes (including Qt's doubled
"Uploaded sheet: " prefix for factor-name errors).
"""

import io
from typing import Dict, List, Optional, Tuple

import pandas as pd

from constants.import_constants import IMPORT_SETTINGS
from constants.linguistic_constants import DEFAULT_LINGUISTIC_MAP, NO_INFLUENCE_LABEL
from errors.import_errors import InvalidImportError

LabelMatrix = List[List[str]]


class ExcelMatrixParser:
    """Parses standard linguistic matrices (and optional factor names) from workbook bytes."""

    SOURCE_LABEL = IMPORT_SETTINGS["SOURCE_LABEL"]

    def parse_sheet(self, content: bytes, expected_size: int) -> Tuple[Optional[List[str]], LabelMatrix]:
        """
        Parse the first sheet (`parse_standard_linguistic_labels_and_factor_names_from_excel_bytes`).

        Args:
            content: Workbook bytes
            expected_size: Number of factors

        Returns:
            Tuple[Optional[List[str]], LabelMatrix]: Factor names (when the sheet has them) and the labels

        Raises:
            InvalidImportError: With the Qt message
        """
        frame = pd.read_excel(io.BytesIO(content), sheet_name=0, header=None, engine="openpyxl")
        return self._wrap(lambda: self._parse_frame(frame, expected_size, self.SOURCE_LABEL))

    def parse_workbook(
        self, content: bytes, expected_size: int, expected_sheet_count: int
    ) -> Tuple[Optional[List[str]], Dict[str, LabelMatrix]]:
        """
        Parse every sheet (`parse_standard_linguistic_labels_and_factor_names_from_excel_workbook_bytes`).

        Args:
            content: Workbook bytes
            expected_size: Number of factors
            expected_sheet_count: Number of experts (one sheet each)

        Returns:
            Tuple[Optional[List[str]], Dict[str, LabelMatrix]]: Factor names of the first labelled sheet, and
                the labels per sheet name in workbook order

        Raises:
            InvalidImportError: With the Qt message
        """
        workbook = pd.read_excel(io.BytesIO(content), sheet_name=None, header=None, engine="openpyxl")
        return self._wrap(lambda: self._parse_sheets(workbook, expected_size, expected_sheet_count))

    def _wrap(self, parse):
        """Run a parse step, turning its `ValueError` into `InvalidImportError` with the same text."""
        try:
            return parse()
        except ValueError as exc:
            raise InvalidImportError(str(exc), public_message=str(exc)) from exc

    def _parse_sheets(
        self, workbook: Dict[str, pd.DataFrame], expected_size: int, expected_sheet_count: int
    ) -> Tuple[Optional[List[str]], Dict[str, LabelMatrix]]:
        """Parse every sheet and check the sheet count and shared factor names."""
        if not workbook:
            raise ValueError("Uploaded workbook does not contain any sheets.")
        if len(workbook) != expected_sheet_count:
            raise ValueError(
                "Uploaded workbook must contain exactly "
                f"{expected_sheet_count} sheets, one for each expert. Found {len(workbook)}."
            )
        parsed: Dict[str, LabelMatrix] = {}
        factor_names: Optional[List[str]] = None
        for sheet_name, frame in workbook.items():
            sheet_names, matrix = self._parse_frame(frame, expected_size, f"Sheet '{sheet_name}'")
            if sheet_names is not None:
                if factor_names is None:
                    factor_names = sheet_names
                elif [name.casefold() for name in factor_names] != [name.casefold() for name in sheet_names]:
                    raise ValueError("Uploaded workbook must use the same factor names on every sheet.")
            parsed[sheet_name] = matrix
        return factor_names, parsed

    def _parse_frame(
        self, frame: pd.DataFrame, expected_size: int, source: str
    ) -> Tuple[Optional[List[str]], LabelMatrix]:
        """Parse one sheet into factor names and labels."""
        try:
            factor_names, body = self._split_names_and_body(self._strip_cells(frame), expected_size)
        except ValueError as exc:
            raise ValueError(f"{source}: {exc}") from exc
        matrix: LabelMatrix = []
        for i in range(expected_size):
            row: List[str] = []
            for j in range(expected_size):
                if i == j:
                    row.append(NO_INFLUENCE_LABEL)
                    continue
                try:
                    row.append(self._standard_label(body.iat[i, j]))
                except ValueError as exc:
                    raise ValueError(f"{source}: {exc}") from exc
            matrix.append(row)
        return factor_names, matrix

    def _strip_cells(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Turn every cell into a trimmed string, empty cells into ''."""
        return frame.astype(object).fillna("").astype(str).apply(lambda column: column.map(lambda value: value.strip()))

    def _split_names_and_body(self, raw: pd.DataFrame, size: int) -> Tuple[Optional[List[str]], pd.DataFrame]:
        """Return (None, body) for an `n x n` sheet, or (names, body) for a labelled `(n+1) x (n+1)` sheet."""
        if raw.shape == (size, size):
            return None, raw
        if raw.shape == (size + 1, size + 1):
            row_names = self._factor_names(raw.iloc[1:, 0].tolist())
            column_names = self._factor_names(raw.iloc[0, 1:].tolist())
            if [name.casefold() for name in row_names] != [name.casefold() for name in column_names]:
                raise ValueError(f"{self.SOURCE_LABEL}: Factor names in the first row and first column must match.")
            return row_names, raw.iloc[1:, 1:].reset_index(drop=True)
        raise ValueError(
            f"Uploaded matrix must be either exactly {size} x {size} "
            f"or {size + 1} x {size + 1} when the first row and "
            "first column contain factor names."
        )

    def _factor_names(self, values: List[str]) -> List[str]:
        """Trim factor names; reject blanks and case-insensitive duplicates."""
        names = [str(value).strip() for value in values]
        if any(not name for name in names):
            raise ValueError(f"{self.SOURCE_LABEL}: Factor names cannot be blank.")
        if len({name.casefold() for name in names}) != len(names):
            raise ValueError(f"{self.SOURCE_LABEL}: Factor names must be unique.")
        return names

    def _standard_label(self, value: str) -> str:
        """Return a trimmed standard label or raise the Qt "Invalid matrix value" message."""
        text = str(value).strip()
        if text in DEFAULT_LINGUISTIC_MAP:
            return text
        raise ValueError(
            "Invalid matrix value found: "
            f"{value!r}. Allowed values are either "
            '"No influence, Low influence, Medium influence, High influence, Extreme influence".'
        )


excel_matrix_parser = ExcelMatrixParser()
