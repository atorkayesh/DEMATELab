# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 15:43:15 2026

@author: Ali
"""

# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font

from .clustering_service import cluster_total_matrix, plot_clustered_heatmap
from .dematel_visualization import DematelPlotInput, DematelPlotStyle, plot_dematel_influence_map


def _defuzzify_matrix(matrix: np.ndarray) -> np.ndarray:
    if np.isscalar(matrix[0][0]):
        return np.array(matrix, dtype=float)

    n = len(matrix)
    result = np.zeros((n, n), dtype=float)

    for i in range(n):
        for j in range(n):
            l, m, u = matrix[i][j]
            result[i, j] = (l + m + u) / 3

    return result


def _write_matrix_sheet(ws, title: str, matrix, labels: list[str], decimals: int = 4) -> None:
    ws.title = title

    ws.cell(row=1, column=1, value="")
    for j, label in enumerate(labels, start=2):
        cell = ws.cell(row=1, column=j, value=label)
        cell.font = Font(bold=True)

    for i, label in enumerate(labels, start=2):
        cell = ws.cell(row=i, column=1, value=label)
        cell.font = Font(bold=True)

    for i in range(len(labels)):
        for j in range(len(labels)):
            value = matrix[i][j]
            if hasattr(value, "__len__") and not np.isscalar(value):
                text = "(" + ", ".join(f"{float(x):.{decimals}f}" for x in value) + ")"
                ws.cell(row=i + 2, column=j + 2, value=text)
            else:
                ws.cell(row=i + 2, column=j + 2, value=float(value))


def _write_summary_sheet(wb: Workbook, result) -> None:
    ws = wb.active
    ws.title = "Summary"

    rows = [
        ("Factors", ", ".join(result.factors)),
        ("Cause group", ", ".join(result.cause_group) if result.cause_group else "-"),
        ("Effect group", ", ".join(result.effect_group) if result.effect_group else "-"),
        ("Threshold method", result.threshold_method or "-"),
        ("Threshold value", result.threshold_value if result.threshold_value is not None else "-"),
    ]

    for idx, (key, value) in enumerate(rows, start=1):
        ws.cell(row=idx, column=1, value=key).font = Font(bold=True)
        ws.cell(row=idx, column=2, value=value)

    start_row = 8
    ws.cell(row=start_row, column=1, value="Factor").font = Font(bold=True)
    ws.cell(row=start_row, column=2, value="Prominence").font = Font(bold=True)
    ws.cell(row=start_row, column=3, value="Relation").font = Font(bold=True)

    for i, factor in enumerate(result.factors, start=start_row + 1):
        idx = i - (start_row + 1)
        ws.cell(row=i, column=1, value=factor)
        ws.cell(row=i, column=2, value=float(result.prominence[idx]))
        ws.cell(row=i, column=3, value=float(result.relation[idx]))


def export_results_to_xlsx(result, output_path: str | Path) -> Path:
    output_path = Path(output_path)

    wb = Workbook()
    _write_summary_sheet(wb, result)

    if hasattr(result, "fuzzy_direct_matrix"):
        _write_matrix_sheet(wb.create_sheet(), "Fuzzy Direct", result.fuzzy_direct_matrix, result.factors)
        _write_matrix_sheet(wb.create_sheet(), "Fuzzy Normalized", result.fuzzy_normalized_matrix, result.factors)
        _write_matrix_sheet(wb.create_sheet(), "Fuzzy Total", result.fuzzy_total_matrix, result.factors)
        defuzzified_total = _defuzzify_matrix(result.fuzzy_total_matrix)
        _write_matrix_sheet(wb.create_sheet(), "Defuzzified Total", defuzzified_total, result.factors)
    else:
        _write_matrix_sheet(wb.create_sheet(), "Direct Matrix", result.direct_matrix, result.factors)
        _write_matrix_sheet(wb.create_sheet(), "Normalized Matrix", result.normalized_matrix, result.factors)
        _write_matrix_sheet(wb.create_sheet(), "Total Matrix", result.total_matrix, result.factors)

    wb.save(output_path)
    return output_path


def export_results_to_pdf(result, output_path: str | Path) -> Path:
    output_path = Path(output_path)

    if hasattr(result, "fuzzy_total_matrix"):
        total_for_plot = _defuzzify_matrix(result.fuzzy_total_matrix)
    else:
        total_for_plot = result.total_matrix

    threshold = result.threshold_value
    if threshold is None:
        threshold = float(np.mean(total_for_plot))

    plot_input = DematelPlotInput(
        factors=result.factors,
        prominence=result.prominence,
        relation=result.relation,
        total_matrix=total_for_plot,
        threshold=threshold,
    )

    # export the DEMATEL influence map directly as a PDF
    plot_dematel_influence_map(
        data=plot_input,
        style=DematelPlotStyle(figsize=(8, 6), dpi=300),
        save_path=output_path,
        show=False,
    )

    return output_path


def export_clustered_heatmap_to_pdf(
    result,
    output_path: str | Path,
    method: str = "kmeans",
) -> Path:
    output_path = Path(output_path)

    if hasattr(result, "fuzzy_total_matrix"):
        total_for_plot = _defuzzify_matrix(result.fuzzy_total_matrix)
    else:
        total_for_plot = result.total_matrix

    clustering_result = cluster_total_matrix(
        total_matrix=total_for_plot,
        factor_names=result.factors,
        method=method,
    )

    plot_clustered_heatmap(
        clustering_result=clustering_result,
        save_path=output_path,
        show=False,
        figsize=(8, 6),
        dpi=300,
    )

    return output_path