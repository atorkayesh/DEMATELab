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
    raw = df.fillna("").astype(str).applymap(lambda x: x.strip())

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