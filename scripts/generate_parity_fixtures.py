"""
Generate the numerical parity fixtures for `apps/api` from the legacy Qt app in `qt-app/`.

Run from the repository root with the Qt environment (never from `apps/api`, which must not import `qt-app/`):

    uv run --frozen --python 3.13 --project qt-app/DEMATELab python scripts/generate_parity_fixtures.py

It follows the Qt GUI path for every case: the GUI weight correction (`gui_app._normalize_weight_inputs`), the
matrix editor's diagonal (forced to the solver's no-influence label), `analysis_service.run_analysis`, the viewer's
crisp total matrix (`_to_numeric_2d_array`), its prominence ranking, and `clustering_service.cluster_total_matrix`.
Imports go through `matrix_parsers` and the real matrix editor widgets (offscreen Qt).

Output (overwritten on every run):
    apps/api/tests/fixtures/parity/<case>__<solver>__<threshold>.json
    apps/api/tests/fixtures/imports/<name>.xlsx and <name>.json
    apps/api/tests/fixtures/xlsx/<case>__<solver>__<threshold>.xlsx (the Qt viewer's own XLSX export)
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np  # noqa: E402
from DEMATELab import results_viewer_widget  # noqa: E402
from DEMATELab.analysis_service import AnalysisInput, ExpertFormData, run_analysis  # noqa: E402
from DEMATELab.clustering_service import cluster_total_matrix  # noqa: E402
from DEMATELab.constants import LINGUISTIC_TERMS, NO_INFLUENCE_LABEL, Z_NO_INFLUENCE_DEFAULT  # noqa: E402
from DEMATELab.gui_app import _equal_weight_defaults, _normalize_weight_inputs  # noqa: E402
from DEMATELab.matrix_editor_widget import ExpertMatrixTab, MatrixEditorWidget  # noqa: E402
from DEMATELab.matrix_parsers import (  # noqa: E402
    parse_standard_linguistic_labels_and_factor_names_from_excel_bytes,
    parse_standard_linguistic_labels_and_factor_names_from_excel_workbook_bytes,
)
from DEMATELab.results_viewer_widget import ResultsViewerWidget, _to_numeric_2d_array  # noqa: E402
from openpyxl import Workbook  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
PARITY_DIR = REPO_ROOT / "apps/api/tests/fixtures/parity"
IMPORTS_DIR = REPO_ROOT / "apps/api/tests/fixtures/imports"
XLSX_DIR = REPO_ROOT / "apps/api/tests/fixtures/xlsx"
XLSX_CASES = [
    ("small", "dematel", "mmde"),
    ("small", "fuzzy_dematel", "average"),
    ("small", "grey_dematel", "median"),
    ("small_z", "fuzzy_z_dematel", "third_quartile"),
]
EXAMPLES_DIR = REPO_ROOT / "data/examples"

STANDARD_SOLVERS = ["dematel", "fuzzy_dematel", "grey_dematel"]
Z_SOLVERS = ["fuzzy_z_dematel"]
THRESHOLDS = ["average", "first_quartile", "median", "third_quartile", "mmde"]

N, L, M, H, E = "No influence", "Low influence", "Medium influence", "High influence", "Extreme influence"


def z(influence: str, reliability: str) -> str:
    """Build a Z label as the Qt constants do."""
    return f"{influence} with {reliability} reliability"


def _case(factors, experts, solvers):
    return {"factors": factors, "experts": experts, "solvers": solvers}


def _expert(name, weight, matrix):
    return {"name": name, "weight": weight, "matrix": matrix}


def build_cases() -> dict:
    """Deterministic cases; diagonals are deliberately not always no-influence (the GUI forces them)."""
    cases = {}
    small_factors = ["Cost", "Quality", "Time"]
    cases["small"] = _case(
        small_factors,
        [
            _expert("Expert 1", 0.6, [[H, L, H], [M, N, E], [L, M, N]]),
            _expert("Expert 2", 0.4, [[N, M, L], [H, N, M], [E, L, N]]),
        ],
        STANDARD_SOLVERS,
    )
    cases["small_z"] = _case(
        small_factors,
        [
            _expert(
                "Expert 1",
                0.6,
                [
                    [z("High influence", "H"), z("Low influence", "M"), z("High influence", "VH")],
                    [z("Medium influence", "L"), z("No influence", "VH"), z("Very high influence", "H")],
                    [z("Low influence", "VL"), z("Medium influence", "M"), z("No influence", "VH")],
                ],
            ),
            _expert(
                "Expert 2",
                0.4,
                [
                    [z("No influence", "VH"), z("Medium influence", "H"), z("Low influence", "L")],
                    [z("High influence", "M"), z("No influence", "VH"), z("Medium influence", "VH")],
                    [z("Very high influence", "VL"), z("Low influence", "H"), z("No influence", "VH")],
                ],
            ),
        ],
        Z_SOLVERS,
    )
    four = ["C1", "C2", "C3", "C4"]
    weights3_experts = [
        [[N, L, M, H], [E, N, L, M], [H, E, N, L], [M, H, E, N]],
        [[N, H, L, N], [M, N, E, L], [L, M, N, H], [E, N, M, N]],
        [[N, M, M, E], [L, N, H, M], [N, L, N, M], [H, M, L, N]],
    ]
    cases["weights3"] = _case(
        four,
        [
            _expert(f"Expert {i + 1}", w, m)
            for i, (w, m) in enumerate(zip([0.334, 0.333, 0.333], weights3_experts, strict=True))
        ],
        STANDARD_SOLVERS,
    )
    cases["weights_rounding"] = _case(
        four,
        [_expert(f"Expert {i + 1}", 0.3333, m) for i, m in enumerate(weights3_experts)],
        STANDARD_SOLVERS,
    )
    reliabilities = ["VL", "L", "M", "H", "VH"]
    influences = ["No influence", "Low influence", "Medium influence", "High influence", "Very high influence"]
    weights3_z = [
        [[z(influences[(i + j + k) % 5], reliabilities[(i * 2 + j + k) % 5]) for j in range(4)] for i in range(4)]
        for k in range(3)
    ]
    cases["weights3_z"] = _case(
        four,
        [
            _expert(f"Expert {i + 1}", w, m)
            for i, (w, m) in enumerate(zip([0.334, 0.333, 0.333], weights3_z, strict=True))
        ],
        Z_SOLVERS,
    )
    cases["zero"] = _case(
        small_factors,
        [_expert("Expert 1", 0.5, [[N] * 3 for _ in range(3)]), _expert("Expert 2", 0.5, [[N] * 3 for _ in range(3)])],
        # Not fuzzy: there "No influence" is (0, 0, 0.25), so Qt does not raise; it inverts a singular (I - X)
        # and returns values around 1e15 that depend on the BLAS library (not a reproducible fixture).
        ["dematel", "grey_dematel"],
    )
    # Invariant under swapping factors 1<->2 and 3<->4: repeated total-matrix values (MMDE stable sort) and pairs of
    # equal prominences (ranking tie order), while (I - X) stays invertible (row sums differ).
    tie = [[N, M, H, L], [M, N, L, H], [M, N, N, L], [N, M, L, N]]
    cases["mmde_tie"] = _case(four, [_expert("Expert 1", 1.0, tie)], STANDARD_SOLVERS)
    z_terms = {
        N: z("No influence", "M"),
        L: z("Low influence", "M"),
        M: z("Medium influence", "M"),
        H: z("High influence", "M"),
    }
    cases["mmde_tie_z"] = _case(
        four, [_expert("Expert 1", 1.0, [[z_terms[cell] for cell in row] for row in tie])], Z_SOLVERS
    )
    cases["two_factors"] = _case(["A", "B"], [_expert("Expert 1", 1.0, [[N, H], [L, N]])], STANDARD_SOLVERS)
    cases["two_factors_z"] = _case(
        ["A", "B"],
        [_expert("Expert 1", 1.0, [[z("No influence", "VH"), z("High influence", "H")], [z("Low influence", "M"), N]])],
        Z_SOLVERS,
    )
    for case_name, file_name in [
        ("fuzzy_example", "Example Data - Fuzzy DEMATEL.xlsx"),
        ("grey_example", "Example Data - Grey DEMATEL.xlsx"),
    ]:
        cases[case_name] = example_case(EXAMPLES_DIR / file_name)
    return cases


def example_case(path: Path) -> dict:
    """Read an example workbook with the Qt workbook parser; equal default weights, sheet names as experts."""
    import pandas as pd

    content = path.read_bytes()
    sheets = pd.read_excel(path, sheet_name=None, header=None)
    first = next(iter(sheets.values()))
    size = first.shape[0] - 1
    factor_names, matrices = parse_standard_linguistic_labels_and_factor_names_from_excel_workbook_bytes(
        file_bytes=content, expected_size=size, expected_sheet_count=len(sheets)
    )
    weights = _equal_weight_defaults(len(matrices))
    experts = [_expert(name, weight, matrix) for (name, matrix), weight in zip(matrices.items(), weights, strict=True)]
    return _case(factor_names, experts, STANDARD_SOLVERS)


def to_jsonable(value):
    """Convert numpy values and containers into plain JSON values (floats keep their exact repr)."""
    if isinstance(value, np.ndarray):
        return to_jsonable(value.tolist())
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, np.generic):
        return value.item()
    return value


def run_gui_analysis(case: dict, solver: str, threshold: str):
    """Run one case the way the GUI does: corrected weights, forced diagonal, `run_analysis`."""
    diagonal = Z_NO_INFLUENCE_DEFAULT if solver == "fuzzy_z_dematel" else NO_INFLUENCE_LABEL
    corrected = _normalize_weight_inputs([expert["weight"] for expert in case["experts"]])
    editor_matrices = [
        [[diagonal if i == j else cell for j, cell in enumerate(row)] for i, row in enumerate(expert["matrix"])]
        for expert in case["experts"]
    ]
    payload = AnalysisInput(
        solver_type=solver,
        factors=[name.strip() for name in case["factors"]],
        experts=[
            ExpertFormData(name=expert["name"].strip(), weight=weight, matrix=matrix)
            for expert, weight, matrix in zip(case["experts"], corrected, editor_matrices, strict=True)
        ],
        threshold_method=threshold,
    )
    return corrected, run_analysis(payload)


def generate_xlsx(cases: dict) -> int:
    """Export each XLSX case through the Qt results viewer's own export (save dialog stubbed)."""
    if XLSX_DIR.exists():
        shutil.rmtree(XLSX_DIR)
    XLSX_DIR.mkdir(parents=True)
    for case_name, solver, threshold in XLSX_CASES:
        _, result = run_gui_analysis(cases[case_name], solver, threshold)
        path = XLSX_DIR / f"{case_name}__{solver}__{threshold}.xlsx"
        viewer = ResultsViewerWidget(result)
        results_viewer_widget.QFileDialog.getSaveFileName = staticmethod(
            lambda *args, target=path, **kwargs: (str(target), "")
        )
        viewer._export_results_to_xlsx()
    return len(XLSX_CASES)


def run_case(case: dict, solver: str, threshold: str) -> dict:
    """Run one case the way the GUI does and package the request and every expected output."""
    request = {
        "solver_type": solver,
        "threshold_method": threshold,
        "factors": case["factors"],
        "experts": case["experts"],
    }
    fixture = {"request": request, "numpy_version": np.__version__}
    try:
        fixture["corrected_weights"], result = run_gui_analysis(case, solver, threshold)
    except ValueError as exc:
        fixture["corrected_weights"] = _normalize_weight_inputs([expert["weight"] for expert in case["experts"]])
        fixture["error_message"] = str(exc)
        return fixture
    fixture["result"] = {field.name: to_jsonable(getattr(result, field.name)) for field in dataclasses.fields(result)}
    total = getattr(result, "total_matrix", None)
    if total is None:
        total = getattr(result, "grey_total_matrix", None)
    if total is None:
        total = result.fuzzy_total_matrix
    crisp_total = _to_numeric_2d_array(total)
    prominence = np.asarray(result.prominence, dtype=float)
    relation = np.asarray(result.relation, dtype=float)
    fixture["crisp_total_matrix"] = to_jsonable(crisp_total)
    fixture["summary_order"] = to_jsonable(np.argsort(prominence)[::-1])
    fixture["strongest_relation"] = float(relation[int(np.argmax(np.abs(relation)))])
    try:
        clustering = cluster_total_matrix(total_matrix=crisp_total, factor_names=result.factors)
        fixture["cluster"] = {
            "labels_named": to_jsonable(clustering.labels_named),
            "labels_numeric": to_jsonable(clustering.labels_numeric),
        }
    except ValueError as exc:
        fixture["cluster"] = {"error_message": str(exc)}
    return fixture


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def generate_parity(cases: dict) -> int:
    if PARITY_DIR.exists():
        shutil.rmtree(PARITY_DIR)
    PARITY_DIR.mkdir(parents=True)
    count = 0
    for case_name, case in cases.items():
        for solver in case["solvers"]:
            for threshold in THRESHOLDS:
                write_json(PARITY_DIR / f"{case_name}__{solver}__{threshold}.json", run_case(case, solver, threshold))
                count += 1
    return count


def write_workbook(path: Path, sheets: dict) -> None:
    """Write a workbook with one sheet per entry; `None` cells stay empty."""
    workbook = Workbook()
    workbook.remove(workbook.active)
    for sheet_name, rows in sheets.items():
        sheet = workbook.create_sheet(sheet_name)
        for row in rows:
            sheet.append(row)
    workbook.save(path)


def labelled(names: list, body: list) -> list:
    """Add a header row and column of factor names around a matrix body."""
    return [[None, *names]] + [[name, *row] for name, row in zip(names, body, strict=True)]


def import_cases() -> dict:
    """Hand-made workbooks: (kind, factor_count, expert_names, sheets) per fixture name."""
    body3 = [[N, L, H], [M, N, E], [L, M, None]]
    body4 = [[None, " Low influence ", M, H], [E, N, L, M], [H, E, None, L], [M, H, E, N]]
    return {
        "matrix_plain_3x3": ("matrix", 3, None, {"Sheet1": body3}),
        "matrix_labelled_4x4": ("matrix", 4, None, {"Sheet1": labelled([" Alpha", "Beta", "Gamma ", "Delta"], body4)}),
        "matrix_wrong_size": ("matrix", 4, None, {"Sheet1": body3}),
        "matrix_unknown_label": ("matrix", 3, None, {"Sheet1": [[N, "low influence", H], [M, N, E], [L, M, N]]}),
        "matrix_empty_cell": ("matrix", 3, None, {"Sheet1": [[N, None, H], [M, N, E], [L, M, N]]}),
        "matrix_numeric_cell": ("matrix", 3, None, {"Sheet1": [[N, 3, H], [M, N, E], [L, M, N]]}),
        "matrix_mismatched_names": (
            "matrix",
            3,
            None,
            {"Sheet1": [[None, "A", "B", "C"], ["A", *body3[0]], ["B", *body3[1]], ["X", *body3[2]]]},
        ),
        "matrix_blank_names": (
            "matrix",
            3,
            None,
            {"Sheet1": [[None, "A", "B", "C"], ["A", *body3[0]], [None, *body3[1]], ["C", *body3[2]]]},
        ),
        "matrix_duplicate_names": ("matrix", 3, None, {"Sheet1": labelled(["A", "a", "C"], body3)}),
        "matrix_numeric_names": ("matrix", 3, None, {"Sheet1": labelled([1, 2, 3], body3)}),
        "workbook_by_name": (
            "workbook",
            3,
            ["alice", " Bob "],
            {"Bob": body3, "Alice": [[N, H, H], [L, N, L], [E, E, N]]},
        ),
        "workbook_by_order": ("workbook", 3, ["Alice", "Bob"], {"S1": body3, "S2": [[N, H, H], [L, N, L], [E, E, N]]}),
        "workbook_duplicate_experts": (
            "workbook",
            3,
            ["Alice", "alice"],
            {"Alice": body3, "Other": [[N, H, H], [L, N, L], [E, E, N]]},
        ),
        "workbook_labelled": (
            "workbook",
            3,
            ["E1", "E2"],
            {"E1": labelled(["A", "B", "C"], body3), "E2": labelled(["a", "b", "c"], body3)},
        ),
        "workbook_mixed_labels": ("workbook", 3, ["E1", "E2"], {"E1": body3, "E2": labelled(["A", "B", "C"], body3)}),
        "workbook_wrong_sheet_count": ("workbook", 3, ["E1", "E2", "E3"], {"E1": body3, "E2": body3}),
        "workbook_differing_names": (
            "workbook",
            3,
            ["E1", "E2"],
            {"E1": labelled(["A", "B", "C"], body3), "E2": labelled(["A", "B", "D"], body3)},
        ),
        "workbook_unknown_label": (
            "workbook",
            3,
            ["E1", "E2"],
            {"E1": body3, "E2": [[N, "Very high influence", H], [M, N, E], [L, M, N]]},
        ),
        "workbook_wrong_size": ("workbook", 4, ["E1", "E2"], {"E1": body3, "E2": body3}),
    }


def qt_matrix_import(content: bytes, factor_count: int) -> dict:
    """Mirror `ExpertMatrixTab._import_matrix_from_xlsx` with a real tab."""
    tab = ExpertMatrixTab(
        factor_names=[f"F{i + 1}" for i in range(factor_count)],
        dropdown_terms=LINGUISTIC_TERMS,
        diagonal_value=NO_INFLUENCE_LABEL,
    )
    factor_names, matrix = parse_standard_linguistic_labels_and_factor_names_from_excel_bytes(
        file_bytes=content, expected_size=len(tab.factor_names)
    )
    if factor_names is not None:
        tab._apply_imported_factor_names(factor_names)
    tab.set_matrix(matrix)
    return {"factor_names": list(tab.factor_names) if factor_names is not None else None, "matrix": tab.get_matrix()}


def qt_workbook_import(content: bytes, factor_count: int, expert_names: list) -> dict:
    """Mirror `MatrixEditorWidget._import_all_matrices_from_xlsx` with a real editor."""
    editor = MatrixEditorWidget(
        factor_names=[f"F{i + 1}" for i in range(factor_count)],
        expert_names=list(expert_names),
        dropdown_terms=LINGUISTIC_TERMS,
        diagonal_value=NO_INFLUENCE_LABEL,
    )
    factor_names, workbook_matrices = parse_standard_linguistic_labels_and_factor_names_from_excel_workbook_bytes(
        file_bytes=content, expected_size=len(editor.factor_names), expected_sheet_count=len(editor.tabs)
    )
    if factor_names is not None:
        editor._apply_imported_factor_names(factor_names)
    editor._apply_workbook_matrices(workbook_matrices)
    # The editor's own condition for matching sheets to experts by name (matrix_editor_widget.py:644-651).
    sheet_names = {name.strip().casefold() for name in workbook_matrices}
    by_name = all(name.strip().casefold() in sheet_names for name in editor.expert_names)
    return {
        "factor_names": list(editor.factor_names) if factor_names is not None else None,
        "matrices": [
            {"expert_name": name, "matrix": matrix}
            for name, matrix in zip(expert_names, editor.get_all_matrices(), strict=True)
        ],
        "matched_by": "name" if by_name else "order",
    }


def generate_imports() -> int:
    if IMPORTS_DIR.exists():
        shutil.rmtree(IMPORTS_DIR)
    IMPORTS_DIR.mkdir(parents=True)
    cases = import_cases()
    for name, source, count, experts in [
        ("fuzzy_example", "Example Data - Fuzzy DEMATEL.xlsx", 18, ["Expert A"]),
        ("grey_example", "Example Data - Grey DEMATEL.xlsx", 14, ["expert 2", "Expert 1"]),
    ]:
        shutil.copyfile(EXAMPLES_DIR / source, IMPORTS_DIR / f"{name}.xlsx")
        cases[name] = ("workbook", count, experts, None)
        cases[f"{name}_matrix"] = ("matrix", count, None, None)
        shutil.copyfile(EXAMPLES_DIR / source, IMPORTS_DIR / f"{name}_matrix.xlsx")
    for name, (kind, count, experts, sheets) in cases.items():
        path = IMPORTS_DIR / f"{name}.xlsx"
        if sheets is not None:
            write_workbook(path, sheets)
        fixture = {"kind": kind, "file": path.name, "factor_count": count, "expert_names": experts}
        try:
            if kind == "matrix":
                fixture["expected"] = qt_matrix_import(path.read_bytes(), count)
            else:
                fixture["expected"] = qt_workbook_import(path.read_bytes(), count, experts)
        except ValueError as exc:
            fixture["error_message"] = str(exc)
        write_json(IMPORTS_DIR / f"{name}.json", fixture)
    return len(cases)


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    all_cases = build_cases()
    print(f"Parity fixtures: {generate_parity(all_cases)}")
    print(f"Import fixtures: {generate_imports()}")
    print(f"XLSX fixtures: {generate_xlsx(all_cases)}")
