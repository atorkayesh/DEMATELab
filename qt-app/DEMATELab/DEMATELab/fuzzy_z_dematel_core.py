# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 11:56:09 2026

@author: Ali
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .constants import DEFAULT_Z_LINGUISTIC_MAP


def z_linguistic_to_fuzzy_matrix(
    matrix: Sequence[Sequence[str]],
    mapping: dict[str, tuple[float, float, float]] | None = None,
) -> np.ndarray:
    scale_map = mapping or DEFAULT_Z_LINGUISTIC_MAP

    try:
        fuzzy = np.array(
            [[scale_map[str(cell).strip()] for cell in row] for row in matrix],
            dtype=float,
        )
    except KeyError as exc:
        raise ValueError(
            f"Unknown Z-linguistic value found: {exc}. "
            f"Allowed values are: {list(scale_map.keys())}"
        ) from exc

    if fuzzy.ndim != 3 or fuzzy.shape[0] != fuzzy.shape[1] or fuzzy.shape[2] != 3:
        raise ValueError("Z-linguistic matrix must have shape (n, n, 3).")

    return fuzzy