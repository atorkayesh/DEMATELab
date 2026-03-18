# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 13:49:01 2026

@author: Ali
"""

# -*- coding: utf-8 -*-
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from .llm_worker import ExplanationWorker


SUPPORTED_ENGINES = ["Gemini", "OpenAI", "OpenRouter", "Groq"]


def _to_numeric_2d_array(matrix) -> np.ndarray:
    arr = np.asarray(matrix, dtype=float)
    if arr.ndim == 3:
        return arr.mean(axis=2)
    return arr


def _matrix_is_structured(matrix) -> bool:
    arr = np.asarray(matrix)
    if arr.size == 0:
        return False
    # 3D numpy arrays (fuzzy n×n×3, grey n×n×2) are structured — each cell is a vector
    if arr.ndim == 3 and arr.shape[2] in (2, 3):
        return True
    # Object arrays whose elements are lists/tuples/arrays (e.g. from Python nested lists)
    if arr.dtype == object:
        sample = arr.flat[0]
        return isinstance(sample, (list, tuple, np.ndarray))
    return False


def _format_cell_value(value) -> str:
    if isinstance(value, np.ndarray):
        value = value.tolist()

    if isinstance(value, (list, tuple)):
        if len(value) == 2:
            return f"({float(value[0]):.4f}, {float(value[1]):.4f})"
        if len(value) == 3:
            return f"({float(value[0]):.4f}, {float(value[1]):.4f}, {float(value[2]):.4f})"
        return str(value)

    try:
        return f"{float(value):.4f}"
    except Exception:
        return str(value)


class PlotTab(QWidget):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.current_zoom = 1.0
        self.title = title

        layout = QVBoxLayout(self)

        button_row = QHBoxLayout()
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")

        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)

        button_row.addWidget(self.zoom_in_button)
        button_row.addWidget(self.zoom_out_button)
        button_row.addStretch()

        layout.addLayout(button_row)
        layout.addWidget(self.canvas)

    def zoom_in(self) -> None:
        self.current_zoom *= 1.2
        self._apply_zoom()

    def zoom_out(self) -> None:
        self.current_zoom /= 1.2
        self._apply_zoom()

    def _apply_zoom(self) -> None:
        self.figure.set_size_inches(8 * self.current_zoom, 6 * self.current_zoom, forward=True)
        self.figure.tight_layout()
        self.canvas.draw()

    def save_png(self, default_name: str) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Save {self.title} as PNG",
            default_name,
            "PNG Files (*.png)",
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".png"):
            file_path += ".png"

        self.figure.savefig(file_path, format="png", dpi=300, bbox_inches="tight")


class ResultsViewerWidget(QWidget):
    def __init__(self, result, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.result = result

        self.worker_thread: QThread | None = None
        self.worker: ExplanationWorker | None = None

        self.causal_plot_tab: PlotTab | None = None
        self.heatmap_plot_tab: PlotTab | None = None

        self._build_ui()

    def _result_kind(self) -> str:
        if hasattr(self.result, "grey_total_matrix"):
            return "grey"
        if hasattr(self.result, "fuzzy_total_matrix"):
            return "fuzzy"
        if hasattr(self.result, "z_total_matrix") or hasattr(self.result, "fuzzy_z_total_matrix"):
            return "z"
        return "crisp"

    def _get_matrix_attr(self, base_name: str):
        kind = self._result_kind()
    
        if kind == "grey":
            candidates = [
                f"grey_{base_name}",
                base_name,
            ]
        elif kind in {"fuzzy", "z"}:
            candidates = [
                f"fuzzy_{base_name}",
                f"z_{base_name}",
                f"fuzzy_z_{base_name}",
                base_name,
            ]
        else:
            candidates = [base_name]
    
        for name in candidates:
            if hasattr(self.result, name):
                return getattr(self.result, name)
        return None

    def _get_raw_vector_attr(self, base_name: str):
        candidates = [
            f"grey_{base_name}",
            f"fuzzy_{base_name}",
            f"z_{base_name}",
            f"fuzzy_z_{base_name}",
        ]
        for name in candidates:
            if hasattr(self.result, name):
                return getattr(self.result, name)
        return None

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        export_row = QHBoxLayout()

        self.export_xlsx_button = QPushButton("Export Results to XLSX")
        self.export_xlsx_button.clicked.connect(self._export_results_to_xlsx)

        self.export_causal_pdf_button = QPushButton("Export Causal Diagram to PNG")
        self.export_causal_pdf_button.clicked.connect(self._export_causal_png)

        self.export_heatmap_pdf_button = QPushButton("Export Heatmap to PNG")
        self.export_heatmap_pdf_button.clicked.connect(self._export_heatmap_png)

        export_row.addWidget(self.export_xlsx_button)
        export_row.addWidget(self.export_causal_pdf_button)
        export_row.addWidget(self.export_heatmap_pdf_button)
        export_row.addStretch()

        layout.addLayout(export_row)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.tab_widget.addTab(self._create_summary_tab(), "Summary")
        self._add_matrix_tabs()
        self.tab_widget.addTab(self._create_scores_table(), "R/C Scores")
        self.tab_widget.addTab(self._create_causal_diagram_tab(), "Causal Diagram")
        self.tab_widget.addTab(self._create_heatmap_tab(), "Heatmap")
        self.tab_widget.addTab(self._create_ai_tab(), "AI Explanation")

    def _add_matrix_tabs(self) -> None:
        factors = self.result.factors
        kind = self._result_kind()
    
        matrix_specs = [
            ("direct_matrix", "Direct Matrix"),
            ("normalized_matrix", "Normalized Matrix"),
            ("total_matrix", "Total Relation Matrix"),
        ]
    
        for attr_name, title in matrix_specs:
            matrix = self._get_matrix_attr(attr_name)
            if matrix is None:
                continue
    
            if _matrix_is_structured(matrix):
                if kind == "fuzzy":
                    tab_title = f"Fuzzy {title}"
                elif kind == "grey":
                    tab_title = f"Grey {title}"
                elif kind == "z":
                    tab_title = f"Z {title}"
                else:
                    tab_title = f"Raw {title}"
    
                self.tab_widget.addTab(
                    self._create_raw_matrix_table(matrix, factors),
                    tab_title,
                )
            else:
                self.tab_widget.addTab(
                    self._create_numeric_matrix_table(matrix, factors),
                    title,
                )

    def _create_summary_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        summary = QPlainTextEdit()
        summary.setReadOnly(True)
        summary.setPlainText(self._build_summary_text())

        layout.addWidget(summary)
        return widget

    def _build_summary_text(self) -> str:
        cause = ", ".join(self.result.cause_group) if getattr(self.result, "cause_group", None) else "-"
        effect = ", ".join(self.result.effect_group) if getattr(self.result, "effect_group", None) else "-"
        threshold_method = getattr(self.result, "threshold_method", None) or "-"
        threshold_value = getattr(self.result, "threshold_value", None)
    
        if threshold_value is None:
            threshold_value_text = "-"
        else:
            threshold_value_text = f"{float(threshold_value):.4f}"
    
        kind = self._result_kind()
        if kind == "fuzzy":
            result_type = "Fuzzy DEMATEL"
        elif kind == "grey":
            result_type = "Grey DEMATEL"
        elif kind == "z":
            result_type = "Fuzzy Z-DEMATEL"
        else:
            result_type = "Classical DEMATEL"
    
        raw_prominence = self._get_raw_vector_attr("prominence")
        raw_relation = self._get_raw_vector_attr("relation")
    
        crisp_prominence = np.asarray(self.result.prominence, dtype=float)
        crisp_relation = np.asarray(self.result.relation, dtype=float)
    
        structured_raw = (
            raw_prominence is not None
            and np.asarray(raw_prominence, dtype=object).ndim == 2
            and np.asarray(raw_prominence, dtype=object).shape[1] in (2, 3)
        )
    
        if structured_raw:
            raw_p_arr = np.asarray(raw_prominence, dtype=object)
            raw_rel_arr = np.asarray(raw_relation, dtype=object)
    
            factors_block = "\n".join(
                f"- {factor}: prominence={_format_cell_value(raw_p_arr[i])} ({float(crisp_prominence[i]):.4f}), "
                f"relation={_format_cell_value(raw_rel_arr[i])} ({float(crisp_relation[i]):.4f})"
                for i, factor in enumerate(self.result.factors)
            )
        else:
            factors_block = "\n".join(
                f"- {factor}: prominence={float(p):.4f}, relation={float(r):.4f}"
                for factor, p, r in zip(
                    self.result.factors,
                    crisp_prominence,
                    crisp_relation,
                )
            )
    
        return (
            f"Result type: {result_type}\n"
            f"Threshold method: {threshold_method}\n"
            f"Threshold value: {threshold_value_text}\n\n"
            f"Cause group:\n{cause}\n\n"
            f"Effect group:\n{effect}\n\n"
            f"Final prominence and relation:\n{factors_block}"
        )

    def _create_numeric_matrix_table(self, matrix, labels: list[str]) -> QWidget:
        arr = _to_numeric_2d_array(matrix)

        table = QTableWidget(len(labels), len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setVerticalHeaderLabels(labels)

        for i in range(len(labels)):
            for j in range(len(labels)):
                table.setItem(i, j, QTableWidgetItem(f"{float(arr[i, j]):.4f}"))

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        return table

    def _create_raw_matrix_table(self, matrix, labels: list[str]) -> QWidget:
        arr = np.asarray(matrix, dtype=object)

        table = QTableWidget(len(labels), len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setVerticalHeaderLabels(labels)

        for i in range(len(labels)):
            for j in range(len(labels)):
                table.setItem(i, j, QTableWidgetItem(_format_cell_value(arr[i, j])))

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        return table

    def _create_scores_table(self) -> QWidget:
        factors = self.result.factors
    
        raw_r = self._get_raw_vector_attr("r")
        raw_c = self._get_raw_vector_attr("c")
        raw_prominence = self._get_raw_vector_attr("prominence")
        raw_relation = self._get_raw_vector_attr("relation")
    
        structured_raw = (
            raw_r is not None
            and np.asarray(raw_r, dtype=object).ndim == 2
            and np.asarray(raw_r, dtype=object).shape[1] in (2, 3)
        )
    
        if structured_raw:
            headers = ["Factor", "R", "C", "Prominence", "Relation"]
            table = QTableWidget(len(factors), len(headers))
            table.setHorizontalHeaderLabels(headers)
    
            raw_r_arr = np.asarray(raw_r, dtype=object)
            raw_c_arr = np.asarray(raw_c, dtype=object)
            raw_p_arr = np.asarray(raw_prominence, dtype=object)
            raw_rel_arr = np.asarray(raw_relation, dtype=object)
    
            for i, factor in enumerate(factors):
                table.setItem(i, 0, QTableWidgetItem(str(factor)))
                table.setItem(i, 1, QTableWidgetItem(_format_cell_value(raw_r_arr[i])))
                table.setItem(i, 2, QTableWidgetItem(_format_cell_value(raw_c_arr[i])))
                table.setItem(i, 3, QTableWidgetItem(_format_cell_value(raw_p_arr[i])))
                table.setItem(i, 4, QTableWidgetItem(_format_cell_value(raw_rel_arr[i])))
        else:
            headers = ["Factor", "R", "C", "R+C", "R-C"]
            table = QTableWidget(len(factors), len(headers))
            table.setHorizontalHeaderLabels(headers)
    
            crisp_r = np.asarray(self.result.r, dtype=float)
            crisp_c = np.asarray(self.result.c, dtype=float)
            crisp_prominence = np.asarray(self.result.prominence, dtype=float)
            crisp_relation = np.asarray(self.result.relation, dtype=float)
    
            for i, factor in enumerate(factors):
                table.setItem(i, 0, QTableWidgetItem(str(factor)))
                table.setItem(i, 1, QTableWidgetItem(f"{float(crisp_r[i]):.4f}"))
                table.setItem(i, 2, QTableWidgetItem(f"{float(crisp_c[i]):.4f}"))
                table.setItem(i, 3, QTableWidgetItem(f"{float(crisp_prominence[i]):.4f}"))
                table.setItem(i, 4, QTableWidgetItem(f"{float(crisp_relation[i]):.4f}"))
    
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        return table

    def _create_causal_diagram_tab(self) -> QWidget:
        self.causal_plot_tab = PlotTab("Causal Diagram")

        prominence = np.asarray(self.result.prominence, dtype=float)
        relation = np.asarray(self.result.relation, dtype=float)
        total_matrix_raw = self._get_matrix_attr("total_matrix")
        factors = self.result.factors

        if total_matrix_raw is None:
            placeholder = QLabel("Total relation matrix is not available.")
            placeholder.setAlignment(Qt.AlignCenter)
            self.causal_plot_tab.layout().addWidget(placeholder)
            return self.causal_plot_tab

        total_matrix = _to_numeric_2d_array(total_matrix_raw)
        ax = self.causal_plot_tab.ax

        colors = ["green" if val >= 0 else "red" for val in relation]

        ax.clear()
        ax.scatter(prominence, relation, s=700, c=colors, edgecolors="black")

        for i, factor in enumerate(factors):
            ax.text(
                float(prominence[i]),
                float(relation[i]),
                factor,
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
            )

        threshold = getattr(self.result, "threshold_value", None)
        if threshold is None:
            threshold = float(np.mean(total_matrix))

        for i in range(len(factors)):
            for j in range(len(factors)):
                if i == j:
                    continue
                weight = float(total_matrix[i, j])
                if weight >= threshold:
                    ax.annotate(
                        "",
                        xy=(prominence[j], relation[j]),
                        xytext=(prominence[i], relation[i]),
                        arrowprops=dict(
                            arrowstyle="->",
                            lw=1.0 + weight,
                            alpha=0.45,
                        ),
                    )

        ax.axhline(0, linestyle="--", linewidth=1)
        ax.axvline(float(np.mean(prominence)), linestyle=":", linewidth=1)
        ax.set_title("Cause-Effect Diagram")
        ax.set_xlabel("Prominence (R + C)")
        ax.set_ylabel("Relation (R - C)")
        ax.grid(True, alpha=0.3)

        self.causal_plot_tab.figure.tight_layout()
        self.causal_plot_tab.canvas.draw()

        return self.causal_plot_tab

    def _create_heatmap_tab(self) -> QWidget:
        self.heatmap_plot_tab = PlotTab("Heatmap")

        total_matrix_raw = self._get_matrix_attr("total_matrix")
        if total_matrix_raw is None:
            placeholder = QLabel("Total relation matrix is not available.")
            placeholder.setAlignment(Qt.AlignCenter)
            self.heatmap_plot_tab.layout().addWidget(placeholder)
            return self.heatmap_plot_tab

        matrix = _to_numeric_2d_array(total_matrix_raw)
        factors = self.result.factors
        ax = self.heatmap_plot_tab.ax

        ax.clear()
        im = ax.imshow(matrix)

        ax.set_xticks(range(len(factors)))
        ax.set_yticks(range(len(factors)))
        ax.set_xticklabels(factors, rotation=45, ha="right")
        ax.set_yticklabels(factors)

        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", color="white")

        ax.set_title("Total Relation Matrix Heatmap")
        self.heatmap_plot_tab.figure.colorbar(im, ax=ax)
        self.heatmap_plot_tab.figure.tight_layout()
        self.heatmap_plot_tab.canvas.draw()

        return self.heatmap_plot_tab

    def _create_ai_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        self.engine_combo = QComboBox()
        self.engine_combo.addItems(SUPPORTED_ENGINES)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Leave blank to use the default model")
        self._set_default_model(self.engine_combo.currentText())

        self.engine_combo.currentTextChanged.connect(self._on_engine_changed)

        form.addRow("Engine", self.engine_combo)
        form.addRow("API Key", self.api_key_input)
        form.addRow("Model", self.model_input)

        layout.addLayout(form)

        button_row = QHBoxLayout()
        self.generate_ai_button = QPushButton("Generate Explanation")
        self.generate_ai_button.clicked.connect(self._start_ai_explanation)

        self.ai_status_label = QLabel("Ready")
        self.ai_status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        button_row.addWidget(self.generate_ai_button)
        button_row.addWidget(self.ai_status_label)
        button_row.addStretch()

        layout.addLayout(button_row)

        self.ai_output = QPlainTextEdit()
        self.ai_output.setReadOnly(True)
        layout.addWidget(self.ai_output)

        return widget

    _ENGINE_DEFAULT_MODELS: dict[str, str] = {
        "Gemini": "gemini-2.5-pro",
        "OpenAI": "gpt-4o-mini",
        "OpenRouter": "openai/gpt-4o-mini",
        "Groq": "llama-3.3-70b-versatile",
    }

    def _set_default_model(self, engine: str) -> None:
        default = self._ENGINE_DEFAULT_MODELS.get(engine, "")
        self.model_input.setText(default)

    def _on_engine_changed(self, engine: str) -> None:
        self._set_default_model(engine)

    def _start_ai_explanation(self) -> None:
        engine = self.engine_combo.currentText().strip()
        api_key = self.api_key_input.text().strip()

        if not api_key:
            self.ai_status_label.setText("Please enter an API key.")
            return

        self.generate_ai_button.setEnabled(False)
        self.ai_status_label.setText("Generating explanation...")
        self.ai_output.setPlainText("")

        model = self.model_input.text().strip() or None

        self.worker_thread = QThread()
        self.worker = ExplanationWorker(
            result=self.result,
            engine=engine,
            api_key=api_key,
            model=model,
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_ai_finished)
        self.worker.error.connect(self._on_ai_error)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)

        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self._on_thread_finished)
        self.worker_thread.start()

    def _on_thread_finished(self) -> None:
        self.worker = None
        self.worker_thread = None

    def _on_ai_finished(self, text: str) -> None:
        self.ai_output.setPlainText(text)
        self.ai_status_label.setText("Done")
        self.generate_ai_button.setEnabled(True)

    def _on_ai_error(self, message: str) -> None:
        self.ai_output.setPlainText(message)
        self.ai_status_label.setText("Error")
        self.generate_ai_button.setEnabled(True)

    def _export_results_to_xlsx(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results to XLSX",
            "dematel_results.xlsx",
            "Excel Files (*.xlsx)",
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            factors = self.result.factors
            kind = self._result_kind()

            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                matrix_specs = [
                    ("direct_matrix", "Direct Matrix"),
                    ("normalized_matrix", "Normalized Matrix"),
                    ("total_matrix", "Total Relation Matrix"),
                ]

                for attr_name, title in matrix_specs:
                    matrix = self._get_matrix_attr(attr_name)
                    if matrix is None:
                        continue

                    if _matrix_is_structured(matrix):
                        if kind == "fuzzy":
                            sheet_name = f"Fuzzy {title}"
                        elif kind == "grey":
                            sheet_name = f"Grey {title}"
                        elif kind == "z":
                            sheet_name = f"Z {title}"
                        else:
                            sheet_name = f"Raw {title}"

                        df_raw = pd.DataFrame(
                            [[_format_cell_value(cell) for cell in row] for row in np.asarray(matrix, dtype=object)],
                            index=factors,
                            columns=factors,
                        )
                        df_raw.to_excel(writer, sheet_name=sheet_name[:31])
                    else:
                        df_numeric = pd.DataFrame(
                            _to_numeric_2d_array(matrix),
                            index=factors,
                            columns=factors,
                        )
                        df_numeric.to_excel(writer, sheet_name=title[:31])

                raw_r = self._get_raw_vector_attr("r")
                raw_c = self._get_raw_vector_attr("c")
                raw_prominence = self._get_raw_vector_attr("prominence")
                raw_relation = self._get_raw_vector_attr("relation")

                structured_raw = (
                    raw_r is not None
                    and np.asarray(raw_r, dtype=object).ndim == 2
                    and np.asarray(raw_r, dtype=object).shape[1] in (2, 3)
                )

                if structured_raw:
                    df_scores = pd.DataFrame(
                        {
                            "Factor": factors,
                            "R": [_format_cell_value(v) for v in np.asarray(raw_r, dtype=object)],
                            "C": [_format_cell_value(v) for v in np.asarray(raw_c, dtype=object)],
                            "Prominence": [
                                f"{_format_cell_value(v)} ({float(c):.4f})"
                                for v, c in zip(np.asarray(raw_prominence, dtype=object), np.asarray(self.result.prominence, dtype=float))
                            ],
                            "Relation": [
                                f"{_format_cell_value(v)} ({float(c):.4f})"
                                for v, c in zip(np.asarray(raw_relation, dtype=object), np.asarray(self.result.relation, dtype=float))
                            ],
                        }
                    )
                else:
                    df_scores = pd.DataFrame(
                        {
                            "Factor": factors,
                            "R": np.asarray(self.result.r, dtype=float),
                            "C": np.asarray(self.result.c, dtype=float),
                            "R+C": np.asarray(self.result.prominence, dtype=float),
                            "R-C": np.asarray(self.result.relation, dtype=float),
                        }
                    )

                df_scores.to_excel(writer, sheet_name="R_C_Scores", index=False)

                threshold_method = getattr(self.result, "threshold_method", None) or "-"
                threshold_value = getattr(self.result, "threshold_value", None)
                cause = ", ".join(self.result.cause_group) if getattr(self.result, "cause_group", None) else "-"
                effect = ", ".join(self.result.effect_group) if getattr(self.result, "effect_group", None) else "-"

                df_summary = pd.DataFrame(
                    {
                        "Item": ["Threshold Method", "Threshold Value", "Cause Group", "Effect Group"],
                        "Value": [threshold_method, threshold_value, cause, effect],
                    }
                )
                df_summary.to_excel(writer, sheet_name="Summary", index=False)

            QMessageBox.information(self, "Export Successful", "Results exported to XLSX successfully.")
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Failed to export XLSX:\n{exc}")

    def _export_causal_png(self) -> None:
        if self.causal_plot_tab is None:
            QMessageBox.warning(self, "Export Warning", "Causal diagram is not available.")
            return
        self.causal_plot_tab.save_png("causal_diagram.png")

    def _export_heatmap_png(self) -> None:
        if self.heatmap_plot_tab is None:
            QMessageBox.warning(self, "Export Warning", "Heatmap is not available.")
            return
        self.heatmap_plot_tab.save_png("heatmap.png")