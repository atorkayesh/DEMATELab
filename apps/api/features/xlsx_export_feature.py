"""
XLSX export, reproducing the Qt GUI export (`results_viewer_widget.py:1397-1501`), not `export_service.py`.

Sheets in order: the three matrices (crisp: "Direct Matrix", ...; fuzzy and fuzzy Z: "Fuzzy Direct Matrix",
...; grey: "Grey Direct Matrix", ...; names cut to 31 characters), "R_C_Scores", "Summary". Crisp values are
written unrounded; fuzzy and grey cells as tuples with 4 decimals. Z sheets keep Qt's "Fuzzy" names (a file
format, unlike on-screen labels). The summary writes the threshold method key (e.g. `mmde`).
"""

import asyncio
from io import BytesIO
from typing import List, Optional

import numpy as np
import pandas as pd

from constants.solver_constants import SolverType
from features.analysis_feature import AnalysisFeature, analysis_feature
from models.analysis_request_models import AnalysisRequest
from models.solver_models import SolverOutput

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
XLSX_FILENAME = "dematel_results.xlsx"

_MATRIX_TITLES = ["Direct Matrix", "Normalized Matrix", "Total Relation Matrix"]


class XlsxExportFeature:
    """Builds the results workbook."""

    def __init__(self, analysis: Optional[AnalysisFeature] = None):
        """
        Create the feature.

        Args:
            analysis: Analysis feature used to recompute the result; defaults to the shared instance
        """
        self._analysis = analysis or analysis_feature

    async def export(self, request: AnalysisRequest) -> bytes:
        """
        Recompute the analysis and build the workbook in a worker thread.

        Args:
            request: Validated analysis request

        Returns:
            bytes: XLSX file content
        """
        return await asyncio.to_thread(self.export_sync, request)

    def export_sync(self, request: AnalysisRequest) -> bytes:
        """
        Recompute the analysis and build the workbook.

        Args:
            request: Validated analysis request

        Returns:
            bytes: XLSX file content
        """
        return self.build_workbook(self._analysis.solve(request))

    def build_workbook(self, output: SolverOutput) -> bytes:
        """
        Write the Qt sheets for one solver output.

        Args:
            output: Solver output

        Returns:
            bytes: XLSX file content
        """
        buffer = BytesIO()
        factors = output.factors
        structured = output.raw_r is not None
        prefix = self._sheet_prefix(output.solver_type)
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            matrices = [output.direct_matrix, output.normalized_matrix, output.total_matrix]
            for title, matrix in zip(_MATRIX_TITLES, matrices, strict=True):
                if structured:
                    cells = [[self.format_cell(cell) for cell in row] for row in np.asarray(matrix, dtype=float)]
                    frame = pd.DataFrame(cells, index=factors, columns=factors)
                    frame.to_excel(writer, sheet_name=f"{prefix} {title}"[:31])
                else:
                    frame = pd.DataFrame(np.asarray(matrix, dtype=float), index=factors, columns=factors)
                    frame.to_excel(writer, sheet_name=title[:31])
            self._scores_frame(output).to_excel(writer, sheet_name="R_C_Scores", index=False)
            self._summary_frame(output).to_excel(writer, sheet_name="Summary", index=False)
        return buffer.getvalue()

    def format_cell(self, value: np.ndarray) -> str:
        """
        Format a triangular or interval value as Qt's `_format_cell_value` does.

        Args:
            value: Array of 2 or 3 numbers

        Returns:
            str: `(a, b)` or `(a, b, c)` with 4 decimals
        """
        return "(" + ", ".join(f"{float(part):.4f}" for part in value) + ")"

    def _sheet_prefix(self, solver_type: SolverType) -> str:
        """Return Qt's sheet prefix: Qt never detects Z results, so fuzzy Z sheets are "Fuzzy"."""
        return "Grey" if solver_type == SolverType.GREY_DEMATEL else "Fuzzy"

    def _scores_frame(self, output: SolverOutput) -> pd.DataFrame:
        """Build the R_C_Scores sheet: raw tuples with crisp values in brackets, or crisp columns."""
        if output.raw_r is None:
            return pd.DataFrame(
                {
                    "Factor": output.factors,
                    "R": np.asarray(output.r, dtype=float),
                    "C": np.asarray(output.c, dtype=float),
                    "R+C": np.asarray(output.prominence, dtype=float),
                    "R-C": np.asarray(output.relation, dtype=float),
                }
            )
        return pd.DataFrame(
            {
                "Factor": output.factors,
                "R": [self.format_cell(value) for value in output.raw_r],
                "C": [self.format_cell(value) for value in output.raw_c],
                "Prominence": self._with_crisp(output.raw_prominence, output.prominence),
                "Relation": self._with_crisp(output.raw_relation, output.relation),
            }
        )

    def _with_crisp(self, raw: np.ndarray, crisp: np.ndarray) -> List[str]:
        """Format `(l, m, u) (crisp)` cells."""
        return [
            f"{self.format_cell(value)} ({float(number):.4f})"
            for value, number in zip(raw, np.asarray(crisp, dtype=float), strict=True)
        ]

    def _summary_frame(self, output: SolverOutput) -> pd.DataFrame:
        """Build the Summary sheet (threshold method key, threshold value, groups)."""
        cause = ", ".join(output.cause_group) if output.cause_group else "-"
        effect = ", ".join(output.effect_group) if output.effect_group else "-"
        return pd.DataFrame(
            {
                "Item": ["Threshold Method", "Threshold Value", "Cause Group", "Effect Group"],
                "Value": [output.threshold_method.value, output.threshold_value, cause, effect],
            }
        )


xlsx_export_feature = XlsxExportFeature()
