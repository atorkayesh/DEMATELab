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

from PySide6.QtCore import Qt, QEvent, QPoint, QThread
from PySide6.QtWidgets import QToolTip
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
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
        self.canvas.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.current_zoom = 1.0
        self.title = title

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidget(self.canvas)
        self._scroll_area.setWidgetResizable(False)
        self._scroll_area.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self._scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        _zoom_btn_style = """
            QPushButton {
                font-family: 'Inter'; font-size: 12px; font-weight: 400;
                color: #9a9a9a;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 7px 20px;
            }
            QPushButton:hover { color: #1e3333; }
            QPushButton:pressed { color: #1e3333; font-weight: 500; }
        """

        _zoom_bar = QWidget()
        _zoom_bar.setStyleSheet("QWidget { background: #f0f0f0; border-radius: 8px; }")
        _zoom_bar_layout = QHBoxLayout(_zoom_bar)
        _zoom_bar_layout.setContentsMargins(3, 3, 3, 3)
        _zoom_bar_layout.setSpacing(2)

        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.setStyleSheet(_zoom_btn_style)
        self.zoom_in_button.setCursor(Qt.PointingHandCursor)
        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.setStyleSheet(_zoom_btn_style)
        self.zoom_out_button.setCursor(Qt.PointingHandCursor)

        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)

        _zoom_bar_layout.addWidget(self.zoom_in_button)
        _zoom_bar_layout.addWidget(self.zoom_out_button)
        _zoom_bar.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        zoom_row = QHBoxLayout()
        zoom_row.setContentsMargins(0, 0, 0, 0)
        zoom_row.addWidget(_zoom_bar)
        zoom_row.addStretch()

        layout.addLayout(zoom_row)
        layout.addSpacing(20)
        layout.addWidget(self._scroll_area)

    def zoom_in(self) -> None:
        self.current_zoom *= 1.2
        self._apply_zoom()

    def zoom_out(self) -> None:
        self.current_zoom /= 1.2
        self._apply_zoom()

    def _apply_zoom(self) -> None:
        w_in = 8 * self.current_zoom
        h_in = 6 * self.current_zoom
        dpi = self.figure.dpi
        self.figure.set_size_inches(w_in, h_in, forward=False)
        self.canvas.setFixedSize(int(w_in * dpi), int(h_in * dpi))
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
        export_row.setSpacing(2)

        _export_btn_style = """
            QPushButton {
                font-family: 'Inter'; font-size: 12px; font-weight: 400;
                color: #9a9a9a;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 7px 28px;
            }
            QPushButton:hover { color: #1e3333; }
            QPushButton:pressed { color: #1e3333; font-weight: 500; }
        """

        _export_bar = QWidget()
        _export_bar.setStyleSheet("QWidget { background: transparent; }")
        _export_bar_layout = QHBoxLayout(_export_bar)
        _export_bar_layout.setContentsMargins(0, 0, 0, 0)
        _export_bar_layout.setSpacing(6)

        self.export_xlsx_button = QPushButton("Export Results to XLSX")
        self.export_xlsx_button.setStyleSheet(_export_btn_style)
        self.export_xlsx_button.setCursor(Qt.PointingHandCursor)
        self.export_xlsx_button.clicked.connect(self._export_results_to_xlsx)

        self.export_causal_pdf_button = QPushButton("Export Causal Diagram to PNG")
        self.export_causal_pdf_button.setStyleSheet(_export_btn_style)
        self.export_causal_pdf_button.setCursor(Qt.PointingHandCursor)
        self.export_causal_pdf_button.clicked.connect(self._export_causal_png)

        self.export_heatmap_pdf_button = QPushButton("Export Heatmap to PNG")
        self.export_heatmap_pdf_button.setStyleSheet(_export_btn_style)
        self.export_heatmap_pdf_button.setCursor(Qt.PointingHandCursor)
        self.export_heatmap_pdf_button.clicked.connect(self._export_heatmap_png)

        _export_bar_layout.addWidget(self.export_xlsx_button)
        _export_bar_layout.addWidget(self.export_causal_pdf_button)
        _export_bar_layout.addWidget(self.export_heatmap_pdf_button)

        export_row.addWidget(_export_bar)
        export_row.addStretch()

        layout.addLayout(export_row)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 8px;
            }
            QTabBar { background: transparent; }
            QTabBar::tab { width: 0px; height: 0px; padding: 0; margin: 0; border: none; }
        """)
        self.tab_widget.tabBar().hide()
        self.tab_widget.setFixedHeight(350)

        self.tab_widget.addTab(self._create_summary_tab(), "Summary")
        self._add_matrix_tabs()
        self.tab_widget.addTab(self._create_scores_table(), "R/C Scores")
        self.tab_widget.addTab(self._create_causal_diagram_tab(), "Causal Diagram")
        self.tab_widget.addTab(self._create_heatmap_tab(), "Heatmap")
        self.tab_widget.addTab(self._create_ai_tab(), "AI Explanation")

        # Custom full-width tab bar
        self._tab_buttons: list[QPushButton] = []
        tab_bar_container = QWidget()
        tab_bar_container.setStyleSheet("QWidget { background: #f0f0f0; border-radius: 8px; }")
        tab_bar_layout = QHBoxLayout(tab_bar_container)
        tab_bar_layout.setContentsMargins(3, 3, 3, 3)
        tab_bar_layout.setSpacing(2)

        _tab_btn_active = """
            QPushButton {
                font-family: 'Inter'; font-size: 12px; font-weight: 500;
                color: #1e3333;
                background: white;
                border: 1px solid #e8e8e8;
                border-radius: 6px;
                padding: 8px 6px;
            }
        """
        _tab_btn_inactive = """
            QPushButton {
                font-family: 'Inter'; font-size: 12px; font-weight: 400;
                color: #9a9a9a;
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px 6px;
            }
            QPushButton:hover { color: #1e3333; }
        """

        for i in range(self.tab_widget.count()):
            label = self.tab_widget.tabText(i)
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet(_tab_btn_active if i == 0 else _tab_btn_inactive)
            btn.clicked.connect(lambda _, idx=i: self._switch_tab(idx))
            tab_bar_layout.addWidget(btn)
            self._tab_buttons.append(btn)

        self._tab_btn_active_style = _tab_btn_active
        self._tab_btn_inactive_style = _tab_btn_inactive

        layout.addWidget(tab_bar_container)
        layout.addWidget(self.tab_widget)

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

    def _switch_tab(self, index: int) -> None:
        self.tab_widget.setCurrentIndex(index)
        for i, btn in enumerate(self._tab_buttons):
            btn.setStyleSheet(self._tab_btn_active_style if i == index else self._tab_btn_inactive_style)
        label = self.tab_widget.tabText(index)
        if label in ("Causal Diagram", "Heatmap"):
            self.tab_widget.setFixedHeight(600)
        else:
            self.tab_widget.setFixedHeight(350)

    def _create_summary_tab(self) -> QWidget:
        # ── Data ───────────────────────────────────────────────────────────
        kind = self._result_kind()
        result_type = {"fuzzy": "Fuzzy DEMATEL", "grey": "Grey DEMATEL", "z": "Fuzzy Z-DEMATEL"}.get(kind, "Classical DEMATEL")
        cause   = ", ".join(self.result.cause_group)  if getattr(self.result, "cause_group",  None) else "\u2014"
        effect  = ", ".join(self.result.effect_group) if getattr(self.result, "effect_group", None) else "\u2014"
        t_method = getattr(self.result, "threshold_method", None) or "\u2014"
        t_value  = getattr(self.result, "threshold_value",  None)
        t_value_text = f"{float(t_value):.4f}" if t_value is not None else "\u2014"

        raw_prominence = self._get_raw_vector_attr("prominence")
        raw_relation   = self._get_raw_vector_attr("relation")
        crisp_prominence = np.asarray(self.result.prominence, dtype=float)
        crisp_relation   = np.asarray(self.result.relation,   dtype=float)
        structured_raw = (
            raw_prominence is not None
            and np.asarray(raw_prominence, dtype=object).ndim == 2
            and np.asarray(raw_prominence, dtype=object).shape[1] in (2, 3)
        )
        if structured_raw:
            raw_p   = np.asarray(raw_prominence, dtype=object)
            raw_rel = np.asarray(raw_relation,   dtype=object)
            factors_lines = "\n".join(
                f"- {f}: prominence={_format_cell_value(raw_p[i])} ({float(crisp_prominence[i]):.4f}), "
                f"relation={_format_cell_value(raw_rel[i])} ({float(crisp_relation[i]):.4f})"
                for i, f in enumerate(self.result.factors)
            )
        else:
            factors_lines = "\n".join(
                f"- {f}: prominence={float(p):.4f}, relation={float(r):.4f}"
                for f, p, r in zip(self.result.factors, crisp_prominence, crisp_relation)
            )

        # ── Helpers ────────────────────────────────────────────────────────
        _card_style = "QFrame { background: rgba(244, 250, 250, 0.65); border: none; border-radius: 8px; }"

        def _info_card(label: str, value: str) -> QFrame:
            frame = QFrame()
            frame.setStyleSheet(_card_style)
            lay = QVBoxLayout(frame)
            lay.setContentsMargins(12, 10, 12, 10)
            lay.setSpacing(5)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-family: 'Inter'; font-size: 10px; font-weight: 600; color: #9a9a9a; background: transparent;")
            val = QLabel(value)
            val.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 400; color: #1e3333; background: transparent;")
            val.setWordWrap(True)
            lay.addWidget(lbl)
            lay.addWidget(val)
            lay.addStretch()
            return frame


        # ── Root ───────────────────────────────────────────────────────────
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ── Left panel (col-span-2) ────────────────────────────────────────
        left = QFrame()
        left.setStyleSheet(_card_style)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(12, 12, 12, 12)
        left_lay.setSpacing(10)

        title_row = QHBoxLayout()
        title_lbl = QLabel("Summary Insights")
        title_lbl.setStyleSheet("font-family: 'Inter'; font-size: 14px; font-weight: 700; color: #2d4d4c; background: transparent;")
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        left_lay.addLayout(title_row)

        sub_lbl = QLabel("Key signals from the DEMATEL analysis, highlighting the most important relationships for quick insight.")
        sub_lbl.setStyleSheet("font-family: 'Inter'; font-size: 11px; font-weight: 300; color: #9a9a9a; background: transparent;")
        sub_lbl.setWordWrap(True)
        left_lay.addWidget(sub_lbl)

        # ── Stat card values ───────────────────────────────────────────────
        n_cause  = len(self.result.cause_group)  if getattr(self.result, "cause_group",  None) else 0
        n_effect = len(self.result.effect_group) if getattr(self.result, "effect_group", None) else 0
        top_prominence = float(np.max(crisp_prominence))
        rel_idx = int(np.argmax(np.abs(crisp_relation)))
        strongest_rel = float(crisp_relation[rel_idx])
        strongest_rel_str = f"+{strongest_rel:.4f}" if strongest_rel >= 0 else f"{strongest_rel:.4f}"

        _stat_cards = [
            ("Driving Factors",   str(n_cause),                       "Majority of factors act as system drivers."),
            ("Dependent Factors", str(n_effect),                      "Primarily influenced factor in the system."),
            ("Top Prominence",    f"{top_prominence:.4f}",            "Highest overall importance among factors."),
            ("Strongest Relation", strongest_rel_str,                 "Strongest net driving influence detected."),
        ]

        def _stat_box(title: str, value: str, desc: str) -> QFrame:
            box = QFrame()
            box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            box.setStyleSheet("QFrame { background: rgba(255, 255, 255, 0.65); border-radius: 8px; }")
            lay = QVBoxLayout(box)
            lay.setContentsMargins(10, 10, 10, 10)
            lay.setSpacing(2)
            t = QLabel(title)
            t.setStyleSheet("font-family: 'Inter'; font-size: 10px; font-weight: 300; color: #9a9a9a; background: transparent;")
            v = QLabel(value)
            v.setStyleSheet("font-family: 'Inter'; font-size: 20px; font-weight: 700; color: #315b59; background: transparent;")
            d = QLabel(desc)
            d.setStyleSheet("font-family: 'Inter'; font-size: 10px; font-weight: 300; color: #9a9a9a; background: transparent;")
            d.setWordWrap(True)
            lay.addWidget(t)
            lay.addStretch()
            lay.addWidget(v)
            lay.addStretch()
            lay.addWidget(d)
            return box

        boxes_grid = QGridLayout()
        boxes_grid.setSpacing(8)
        boxes_grid.setRowStretch(0, 1)
        boxes_grid.setRowStretch(1, 1)
        boxes_grid.setColumnStretch(0, 1)
        boxes_grid.setColumnStretch(1, 1)
        for i, (title, value, desc) in enumerate(_stat_cards):
            boxes_grid.addWidget(_stat_box(title, value, desc), i // 2, i % 2)
        left_lay.addLayout(boxes_grid, 1)

        # ── Right panel (col-span-8) ───────────────────────────────────────
        right = QWidget()
        right.setStyleSheet("background: transparent;")
        right_grid = QGridLayout(right)
        right_grid.setContentsMargins(0, 0, 0, 0)
        right_grid.setSpacing(10)
        right_grid.setColumnStretch(0, 1)
        right_grid.setColumnStretch(1, 1)
        right_grid.setRowStretch(0, 1)
        right_grid.setRowStretch(1, 1)

        def _analysis_config_card() -> QFrame:
            frame = QFrame()
            frame.setStyleSheet(_card_style)
            lay = QVBoxLayout(frame)
            lay.setContentsMargins(16, 14, 16, 14)
            lay.setSpacing(10)

            title = QLabel("Analysis Configuration")
            title.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 600; color: #2d4d4c; background: transparent;")
            lay.addWidget(title)
            lay.addStretch()

            _label_style = "font-family: 'Inter'; font-size: 10px; font-weight: 300; color: #c8c8c8; background: transparent;"
            _value_style = "font-family: 'Inter'; font-size: 11px; font-weight: 400; color: #315b59; background: transparent;"

            for lbl_text, val_text in [("Result Type", result_type), ("Threshold Method", t_method), ("Threshold Value", t_value_text)]:
                row = QHBoxLayout()
                row.setSpacing(6)
                lbl = QLabel(lbl_text)
                lbl.setStyleSheet(_label_style)
                val = QLabel(val_text)
                val.setStyleSheet(_value_style)
                row.addWidget(lbl)
                row.addStretch()
                row.addWidget(val)
                lay.addLayout(row)

            lay.addStretch()
            return frame

        right_grid.addWidget(_analysis_config_card(), 0, 0)
        def _cause_group_card() -> QFrame:
            frame = QFrame()
            frame.setStyleSheet(_card_style)
            lay = QVBoxLayout(frame)
            lay.setContentsMargins(16, 14, 16, 14)
            lay.setSpacing(10)

            title = QLabel("Cause Group (Driving Factors)")
            title.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 600; color: #2d4d4c; background: transparent;")
            lay.addWidget(title)

            badges_widget = QWidget()
            badges_widget.setStyleSheet("background: transparent;")
            badges_layout = QHBoxLayout(badges_widget)
            badges_layout.setContentsMargins(0, 0, 0, 0)
            badges_layout.setSpacing(6)
            badges_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            factors = [f.strip() for f in cause.split(",")] if cause and cause != "—" else []
            for factor in factors:
                badge = QLabel(factor)
                badge.setAlignment(Qt.AlignCenter)
                badge.setFixedSize(28, 28)
                badge.setStyleSheet(
                    "QLabel { background: #4e9965; color: #f3faf5; border-radius: 14px;"
                    " font-family: 'Inter'; font-size: 9px; font-weight: 600; }"
                )
                badges_layout.addWidget(badge)

            if not factors:
                empty = QLabel("—")
                empty.setStyleSheet("font-family: 'Inter'; font-size: 12px; color: #b5b5b5; background: transparent;")
                badges_layout.addWidget(empty)

            badges_layout.addStretch()
            lay.addWidget(badges_widget)
            lay.addStretch()
            return frame

        def _effect_group_card() -> QFrame:
            frame = QFrame()
            frame.setStyleSheet(_card_style)
            lay = QVBoxLayout(frame)
            lay.setContentsMargins(16, 14, 16, 14)
            lay.setSpacing(10)

            title = QLabel("Effect Group (Dependent Factors)")
            title.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 600; color: #2d4d4c; background: transparent;")
            lay.addWidget(title)

            badges_widget = QWidget()
            badges_widget.setStyleSheet("background: transparent;")
            badges_layout = QHBoxLayout(badges_widget)
            badges_layout.setContentsMargins(0, 0, 0, 0)
            badges_layout.setSpacing(6)
            badges_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            factors = [f.strip() for f in effect.split(",")] if effect and effect != "—" else []
            for factor in factors:
                badge = QLabel(factor)
                badge.setAlignment(Qt.AlignCenter)
                badge.setFixedSize(28, 28)
                badge.setStyleSheet(
                    "QLabel { background: #f97816; color: #fff4e5; border-radius: 14px;"
                    " font-family: 'Inter'; font-size: 9px; font-weight: 600; }"
                )
                badges_layout.addWidget(badge)

            if not factors:
                empty = QLabel("—")
                empty.setStyleSheet("font-family: 'Inter'; font-size: 12px; color: #b5b5b5; background: transparent;")
                badges_layout.addWidget(empty)

            badges_layout.addStretch()
            lay.addWidget(badges_widget)
            lay.addStretch()
            return frame

        right_grid.addWidget(_cause_group_card(),                               0, 1)
        right_grid.addWidget(_effect_group_card(),                              1, 0)
        def _prominence_relation_card() -> QFrame:
            frame = QFrame()
            frame.setStyleSheet(_card_style)
            outer = QVBoxLayout(frame)
            outer.setContentsMargins(16, 14, 16, 14)
            outer.setSpacing(8)

            title = QLabel("Prominence and Relation Analysis")
            title.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 600; color: #2d4d4c; background: transparent;")
            outer.addWidget(title)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setStyleSheet("""
                QScrollArea { background: transparent; border: none; }
                QScrollBar:vertical {
                    background: transparent;
                    width: 4px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #c8d8d8;
                    border-radius: 2px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover { background: #8ab0b0; }
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical { height: 0px; }
                QScrollBar::add-page:vertical,
                QScrollBar::sub-page:vertical { background: transparent; }
            """)

            rows_widget = QWidget()
            rows_widget.setStyleSheet("background: transparent;")
            rows_lay = QVBoxLayout(rows_widget)
            rows_lay.setContentsMargins(0, 0, 0, 0)
            rows_lay.setSpacing(4)

            max_p = float(np.max(np.abs(crisp_prominence))) if len(crisp_prominence) > 0 else 1.0

            # sort by prominence descending
            order = np.argsort(crisp_prominence)[::-1]

            for i in order:
                f      = self.result.factors[i]
                p_val  = float(crisp_prominence[i])
                r_val  = float(crisp_relation[i])
                r_sign = f"+{r_val:.4f}" if r_val >= 0 else f"{r_val:.4f}"

                row_w = QWidget()
                row_w.setStyleSheet("background: transparent;")
                row_h = QHBoxLayout(row_w)
                row_h.setContentsMargins(0, 4, 0, 4)
                row_h.setSpacing(8)

                # factor name
                name_lbl = QLabel(f)
                name_lbl.setFixedWidth(28)
                name_lbl.setStyleSheet("font-family: 'Inter'; font-size: 10px; font-weight: 600; color: #2d4d4c; background: transparent;")

                # bar
                bar = QProgressBar()
                bar.setRange(0, 1000)
                bar.setValue(int((p_val / max_p) * 1000) if max_p > 0 else 0)
                bar.setTextVisible(False)
                bar.setFixedHeight(6)
                bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                bar.setStyleSheet("""
                    QProgressBar { background: #e0ecec; border-radius: 3px; border: none; }
                    QProgressBar::chunk { background: #386c6a; border-radius: 3px; }
                """)

                # prominence value
                p_lbl = QLabel(f"P {p_val:.4f}")
                p_lbl.setFixedWidth(68)
                p_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                p_lbl.setStyleSheet("font-family: 'Inter'; font-size: 10px; font-weight: 400; color: #9a9a9a; background: transparent;")

                # relation value
                r_lbl = QLabel(f"R {r_sign}")
                r_lbl.setFixedWidth(74)
                r_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                r_lbl.setStyleSheet("font-family: 'Inter'; font-size: 10px; font-weight: 400; color: #9a9a9a; background: transparent;")

                row_h.addWidget(name_lbl)
                row_h.addWidget(bar)
                row_h.addWidget(p_lbl)
                row_h.addWidget(r_lbl)
                rows_lay.addWidget(row_w)

            rows_lay.addStretch()
            scroll.setWidget(rows_widget)
            outer.addWidget(scroll)
            return frame


        right_grid.addWidget(_prominence_relation_card(),                       1, 1)

        main_layout.addWidget(left,  4)
        main_layout.addWidget(right, 8)

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
        return self._make_styled_table(
            len(labels), len(labels), labels, labels,
            lambda i, j: f"{float(arr[i, j]):.4f}"
        )

    def _make_styled_table(self, rows, cols, h_labels, v_labels, cell_fn) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet("background: white;")
        lay = QVBoxLayout(wrapper)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(0)

        table = QTableWidget(rows, cols)
        table.setHorizontalHeaderLabels(h_labels)
        table.setVerticalHeaderLabels(v_labels)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setShowGrid(True)
        table.setFocusPolicy(Qt.NoFocus)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)

        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem(cell_fn(i, j))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)

        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                gridline-color: #e8e8e8;
                font-family: 'Inter'; font-size: 12px; font-weight: 400; color: #2d2d2d;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border: none;
            }
            QTableWidget::item:selected { background: #f4fafa; color: #1e3333; }
            QHeaderView::section {
                background: white;
                font-family: 'Inter'; font-size: 12px; font-weight: 600; color: #5a5a5a;
                border: none;
                border-bottom: 1px solid #e8e8e8;
                border-right: 1px solid #e8e8e8;
                padding: 8px 12px;
            }
            QHeaderView { background: white; }
            QScrollBar:vertical {
                background: transparent; width: 4px; margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c8d8d8; border-radius: 2px; min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #8ab0b0; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
            QScrollBar:horizontal {
                background: transparent; height: 4px; margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #c8d8d8; border-radius: 2px; min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover { background: #8ab0b0; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }
        """)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        lay.addWidget(table)
        return wrapper

    def _create_raw_matrix_table(self, matrix, labels: list[str]) -> QWidget:
        arr = np.asarray(matrix, dtype=object)
        return self._make_styled_table(
            len(labels), len(labels), labels, labels,
            lambda i, j: _format_cell_value(arr[i, j])
        )

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
            raw_r_arr   = np.asarray(raw_r,          dtype=object)
            raw_c_arr   = np.asarray(raw_c,          dtype=object)
            raw_p_arr   = np.asarray(raw_prominence, dtype=object)
            raw_rel_arr = np.asarray(raw_relation,   dtype=object)
            data = [
                [str(f), _format_cell_value(raw_r_arr[i]), _format_cell_value(raw_c_arr[i]),
                 _format_cell_value(raw_p_arr[i]), _format_cell_value(raw_rel_arr[i])]
                for i, f in enumerate(factors)
            ]
        else:
            headers = ["Factor", "R", "C", "R+C", "R-C"]
            crisp_r          = np.asarray(self.result.r,          dtype=float)
            crisp_c          = np.asarray(self.result.c,          dtype=float)
            crisp_prominence = np.asarray(self.result.prominence, dtype=float)
            crisp_relation   = np.asarray(self.result.relation,   dtype=float)
            data = [
                [str(f), f"{float(crisp_r[i]):.4f}", f"{float(crisp_c[i]):.4f}",
                 f"{float(crisp_prominence[i]):.4f}", f"{float(crisp_relation[i]):.4f}"]
                for i, f in enumerate(factors)
            ]

        return self._make_styled_table(
            len(factors), len(headers), headers, factors,
            lambda i, j: data[i][j]
        )

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
        ax.set_title("Cause-Effect Diagram", fontfamily="Inter", fontsize=10, fontweight="normal", color="#2d4d4c")
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

        ax.set_title("Total Relation Matrix Heatmap", fontfamily="Inter", fontsize=10, fontweight="normal", color="#2d4d4c")
        self.heatmap_plot_tab.figure.colorbar(im, ax=ax)
        self.heatmap_plot_tab.figure.tight_layout()
        self.heatmap_plot_tab.canvas.draw()

        return self.heatmap_plot_tab

    def _create_ai_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("AI-Assisted Interpretation")
        title.setStyleSheet("font-family: 'Inter'; font-size: 14px; font-weight: 600; color: #2d4d4c; background: transparent;")
        layout.addWidget(title)

        note = QLabel(
            "This section provides an AI-assisted interpretation of the DEMATEL results. "
            "Upon configuring the model and supplying an API key, a structured explanation is generated, "
            "outlining the key cause–effect relationships, factor roles, and overall system dynamics."
        )
        note.setWordWrap(True)
        note.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 400; color: #aaaaaa; background: transparent;")
        layout.addWidget(note)

        layout.addSpacing(16)

        _field_lbl_style = "font-family: 'Inter'; font-size: 12px; font-weight: 400; color: #111111; background: transparent;"
        _combo_style = """
            QComboBox {
                font-family: 'Inter'; font-size: 13px; font-weight: 400;
                color: #1e3333;
                border: 1px solid #e0e0e0; border-radius: 6px;
                padding: 4px 14px;
            }
            QComboBox:focus { border: 1px solid #bcdcdc; }
            QComboBox::drop-down { border: none; width: 28px; }
            QComboBox QAbstractItemView {
                font-family: 'Inter'; font-size: 12px; font-weight: 400;
                color: #1e3333; border: none; outline: none; padding: 0; margin: 0;
            }
            QComboBox QAbstractItemView::item {
                color: #1e3333; padding: 4px 10px; min-height: 22px; border: none; margin: 0;
            }
            QComboBox QAbstractItemView::item:hover,
            QComboBox QAbstractItemView::item:selected { background: #d0e7e6; color: #1e3333; }
        """
        _input_style = """
            QLineEdit {
                font-family: 'Inter'; font-size: 13px; font-weight: 400;
                color: #1e3333;
                border: 1px solid #e0e0e0; border-radius: 6px;
                padding: 4px 14px;
            }
            QLineEdit:focus { border: 1px solid #bcdcdc; }
        """

        self.engine_combo = QComboBox()
        self.engine_combo.addItems(SUPPORTED_ENGINES)
        self.engine_combo.setStyleSheet(_combo_style)
        self.engine_combo.setFixedHeight(34)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setStyleSheet(_input_style)
        self.api_key_input.setFixedHeight(34)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Leave blank to use the default model")
        self.model_input.setStyleSheet(_input_style)
        self.model_input.setFixedHeight(34)

        self._set_default_model(self.engine_combo.currentText())
        self.engine_combo.currentTextChanged.connect(self._on_engine_changed)

        form_container = QWidget()
        form_container.setStyleSheet("background: transparent;")
        form_grid = QGridLayout(form_container)
        form_grid.setContentsMargins(0, 0, 0, 0)
        form_grid.setHorizontalSpacing(16)
        form_grid.setVerticalSpacing(6)
        form_grid.setColumnStretch(0, 1)
        form_grid.setColumnStretch(1, 1)
        form_grid.setColumnStretch(2, 1)

        for col, (lbl_text, w) in enumerate([("Engine", self.engine_combo), ("API Key", self.api_key_input), ("Model", self.model_input)]):
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet(_field_lbl_style)
            form_grid.addWidget(lbl, 0, col)
            form_grid.addWidget(w,   1, col)

        layout.addWidget(form_container)

        self.ai_status_label = QLabel("")
        self.ai_status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.ai_status_label.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 400; color: #d02e34; background: transparent;")
        layout.addWidget(self.ai_status_label)

        self.ai_output = QPlainTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setMaximumHeight(180)
        layout.addWidget(self.ai_output)

        layout.addStretch()

        self.generate_ai_button = QPushButton("  Generate Explanation")
        self.generate_ai_button.setStyleSheet("""
            QPushButton {
                font-family: 'Inter'; font-size: 13px; font-weight: 500;
                color: #2d4d4c;
                background-color: #eaf4f4;
                border: none; border-radius: 5px;
                padding: 0px 16px; text-align: center;
            }
            QPushButton:hover { background-color: #d0e7e6; }
            QPushButton:pressed { background-color: #d0e7e6; }
        """)
        self.generate_ai_button.setFixedHeight(38)
        self.generate_ai_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.generate_ai_button.setCursor(Qt.PointingHandCursor)
        self.generate_ai_button.clicked.connect(self._start_ai_explanation)
        layout.addWidget(self.generate_ai_button)

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
