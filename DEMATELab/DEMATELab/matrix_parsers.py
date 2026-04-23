# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 18:36:36 2026

@author: Ali
"""

from __future__ import annotations

import io

import numpy as np
import pandas as pd

from .constants import DEFAULT_LINGUISTIC_MAP


NO_INFLUENCE_LABEL = "No influence"


def _normalize_standard_linguistic_label(value: str) -> str:
    text = str(value).strip()

    if text in DEFAULT_LINGUISTIC_MAP:
        return text

    raise ValueError(
        "Invalid matrix value found: "
        f"{value!r}. Allowed values are either "
        "\"No influence, Low influence, Medium influence, High influence, Extreme influence\"."
    )


def _strip_string_cells(df: pd.DataFrame) -> pd.DataFrame:
    return df.fillna("").astype(str).apply(lambda col: col.map(lambda x: x.strip()))


def _extract_matrix_body(raw: pd.DataFrame, expected_size: int | None = None) -> pd.DataFrame:
    if expected_size is not None:
        if raw.shape == (expected_size, expected_size):
            return raw

        if raw.shape == (expected_size + 1, expected_size + 1):
            return raw.iloc[1:, 1:].reset_index(drop=True)

        raise ValueError(
            f"Uploaded matrix must be either exactly {expected_size} x {expected_size} "
            f"or {expected_size + 1} x {expected_size + 1} when the first row and "
            "first column contain factor names."
        )

    if raw.shape[0] == raw.shape[1]:
        return raw

    raise ValueError("Uploaded matrix must be square.")


def _parse_standard_linguistic_labels_from_dataframe(
    df: pd.DataFrame,
    expected_size: int,
    source_label: str,
) -> list[list[str]]:
    try:
        raw = _extract_matrix_body(_strip_string_cells(df), expected_size=expected_size)
    except ValueError as exc:
        raise ValueError(f"{source_label}: {exc}") from exc

    matrix: list[list[str]] = []

    for i in range(expected_size):
        row: list[str] = []
        for j in range(expected_size):
            if i == j:
                row.append(NO_INFLUENCE_LABEL)
                continue

            try:
                row.append(_normalize_standard_linguistic_label(raw.iat[i, j]))
            except ValueError as exc:
                raise ValueError(f"{source_label}: {exc}") from exc
        matrix.append(row)

    return enforce_no_influence_diagonal_labels(matrix)


def enforce_no_influence_diagonal_labels(matrix: list[list[str]]) -> list[list[str]]:
    n = len(matrix)

    for i in range(n):
        matrix[i][i] = NO_INFLUENCE_LABEL

    return matrix


def parse_linguistic_matrix_from_text(
    text: str,
    delimiter: str | None = None,
    mapping: dict[str, float] | None = None,
) -> np.ndarray:
    """
    Example pasted text:
    No influence, Low influence, High influence
    Medium influence, No influence, Extreme influence
    Low influence, Medium influence, No influence
    """
    scale_map = mapping or DEFAULT_LINGUISTIC_MAP

    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        raise ValueError("Pasted matrix text is empty.")

    rows_raw: list[list[str]] = []

    for line in lines:
        if delimiter is not None:
            parts = [item.strip() for item in line.split(delimiter)]
        else:
            parts = [item.strip() for item in line.split(",")]

        if not parts:
            raise ValueError("One of the pasted rows is empty.")

        rows_raw.append(parts)

    if not rows_raw or any(len(row) != len(rows_raw) for row in rows_raw):
        raise ValueError("Parsed matrix must be square.")

    rows_raw = enforce_no_influence_diagonal_labels(rows_raw)

    rows: list[list[float]] = []

    for row_items in rows_raw:
        try:
            row = [scale_map[item] for item in row_items]
        except KeyError as exc:
            raise ValueError(
                f"Unknown linguistic value found: {exc}. "
                f"Allowed values are: {list(scale_map.keys())}"
            ) from exc

        rows.append(row)

    matrix = np.array(rows, dtype=float)

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Parsed matrix must be square.")

    return matrix


def parse_linguistic_matrix_from_excel_bytes(
    file_bytes: bytes,
    sheet_name: str | int = 0,
    mapping: dict[str, float] | None = None,
) -> np.ndarray:
    """
    Reads an Excel sheet where each cell contains linguistic values.
    """
    scale_map = mapping or DEFAULT_LINGUISTIC_MAP

    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name, header=None)
    raw = _extract_matrix_body(_strip_string_cells(df))

    if raw.shape[0] != raw.shape[1]:
        raise ValueError("Uploaded matrix must be square.")

    for i in range(raw.shape[0]):
        raw.iat[i, i] = NO_INFLUENCE_LABEL

    try:
        matrix = raw.replace(scale_map).to_numpy(dtype=float)
    except Exception as exc:
        raise ValueError(
            "Failed to convert uploaded Excel matrix to numeric values. "
            f"Allowed values are: {list(scale_map.keys())}"
        ) from exc

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Uploaded matrix must be square.")

    return matrix


def parse_standard_linguistic_labels_from_excel_bytes(
    file_bytes: bytes,
    expected_size: int,
    sheet_name: str | int = 0,
) -> list[list[str]]:
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name, header=None)
    source_label = "Uploaded sheet"
    if isinstance(sheet_name, str):
        source_label = f"Sheet '{sheet_name}'"

    return _parse_standard_linguistic_labels_from_dataframe(
        df=df,
        expected_size=expected_size,
        source_label=source_label,
    )


def parse_standard_linguistic_labels_from_excel_workbook_bytes(
    file_bytes: bytes,
    expected_size: int,
    expected_sheet_count: int,
) -> dict[str, list[list[str]]]:
    workbook = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None, header=None)

    if not workbook:
        raise ValueError("Uploaded workbook does not contain any sheets.")

    if len(workbook) != expected_sheet_count:
        raise ValueError(
            "Uploaded workbook must contain exactly "
            f"{expected_sheet_count} sheets, one for each expert. Found {len(workbook)}."
        )

    parsed_sheets: dict[str, list[list[str]]] = {}

    for sheet_name, df in workbook.items():
        parsed_sheets[sheet_name] = _parse_standard_linguistic_labels_from_dataframe(
            df=df,
            expected_size=expected_size,
            source_label=f"Sheet '{sheet_name}'",
        )

    return parsed_sheets
