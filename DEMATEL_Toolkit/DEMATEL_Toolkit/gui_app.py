"""
@author: Ali
"""
# -*- coding: utf-8 -*-
# f7fbfb
# 808080

from __future__ import annotations

import sys
from pathlib import Path

_ASSETS_DIR = Path(__file__).parent / "assets"

from PySide6.QtCore import Qt, QSize, Property, QPropertyAnimation, QEasingCurve
import qtawesome as qta
from PySide6.QtGui import QFontDatabase, QFont, QColor, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .analysis_service import AnalysisInput, ExpertFormData, run_analysis
from .matrix_editor_widget import MatrixEditorWidget
from .constants import (
    LINGUISTIC_TERMS,
    NO_INFLUENCE_LABEL,
    Z_LINGUISTIC_TERMS,
    Z_NO_INFLUENCE_DEFAULT,
)


class AnimatedButton(QPushButton):
    """QPushButton with smooth background-color animation on hover/press."""

    def __init__(self, *args,
                 color_normal="#eaf4f4",
                 color_hover="#d0e7e6",
                 color_pressed="#d0e7e6",
                 color_text="#2d4d4c",
                 border="none",
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._COLOR_NORMAL  = QColor(color_normal)
        self._COLOR_HOVER   = QColor(color_hover)
        self._COLOR_PRESSED = QColor(color_pressed)
        self._color_text = color_text
        self._border = border
        self.__bg = QColor(self._COLOR_NORMAL)
        self._anim = QPropertyAnimation(self, b"bgColor", self)
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._apply()

    def _get_bg(self):
        return self.__bg

    def _set_bg(self, color: QColor):
        self.__bg = color
        self._apply()

    bgColor = Property(QColor, _get_bg, _set_bg)

    def _apply(self):
        self.setStyleSheet(f"""
            QPushButton {{
                font-family: 'Inter'; font-size: 13px; font-weight: 500;
                color: {self._color_text};
                background-color: {self.__bg.name()};
                border: {self._border};
                border-radius: 5px;
                padding: 0px 16px;
                text-align: center;
            }}
        """)

    def _animate_to(self, target: QColor):
        self._anim.stop()
        self._anim.setStartValue(QColor(self.__bg))
        self._anim.setEndValue(target)
        self._anim.start()

    def enterEvent(self, event):
        self._animate_to(self._COLOR_HOVER)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(self._COLOR_NORMAL)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._anim.stop()
        self._set_bg(self._COLOR_PRESSED)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._animate_to(self._COLOR_HOVER if self.underMouse() else self._COLOR_NORMAL)
        super().mouseReleaseEvent(event)


class StepperWidget(QWidget):
    """A custom integer stepper: text field + stacked ▲/▼ buttons on the right."""

    def __init__(self, min_val: int, max_val: int, default_val: int, parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val

        self.setObjectName("stepperWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QWidget#stepperWidget {
               
                border: 1px solid #e2e5e9;
                border-radius: 4px;
            }
        """)
        self.setFixedHeight(34)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self._edit = QLineEdit(str(default_val))
        self._edit.setCursor(Qt.PointingHandCursor)
        self._edit.setStyleSheet("""
            QLineEdit {
                font-family: 'Inter'; font-size: 13px; font-weight: 400;
                color: #1e3333; background: transparent;
                border: none; padding: 0 10px;
            }
        """)
        self._edit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._edit.editingFinished.connect(self._on_edit)
        row.addWidget(self._edit, 1)

        btn_container = QWidget()
        btn_container.setFixedSize(24, 22)
        btn_container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        btn_col = QVBoxLayout(btn_container)
        btn_col.setContentsMargins(0, 0, 0, 0)
        btn_col.setSpacing(1)

        btn_base = """
            QPushButton {
                background: transparent; border: none; padding: 0;
            }
            QPushButton:hover { background: transparent; }
            QPushButton:pressed { background: transparent; }
        """
        self._up_btn = QPushButton()
        self._up_btn.setFixedSize(24, 10)
        self._up_btn.setIcon(QIcon("assets/icons/chevron-up.svg"))
        self._up_btn.setIconSize(QSize(10, 6))
        self._up_btn.setCursor(Qt.PointingHandCursor)
        self._up_btn.setStyleSheet(
            btn_base +
            "QPushButton { border-top-right-radius: 4px; }"
        )
        self._up_btn.clicked.connect(self._increment)

        self._down_btn = QPushButton()
        self._down_btn.setFixedSize(24, 10)
        self._down_btn.setIcon(QIcon("assets/icons/chevron-down.svg"))
        self._down_btn.setIconSize(QSize(10, 6))
        self._down_btn.setCursor(Qt.PointingHandCursor)
        self._down_btn.setStyleSheet(
            btn_base +
            "QPushButton { border-bottom-right-radius: 4px; }"
        )
        self._down_btn.clicked.connect(self._decrement)

        btn_col.addWidget(self._up_btn)
        btn_col.addWidget(self._down_btn)
        row.addWidget(btn_container)

    def _clamp(self, v: int) -> int:
        return max(self._min, min(self._max, v))

    def _increment(self):
        self._set_value(self._clamp(self.value() + 1))

    def _decrement(self):
        self._set_value(self._clamp(self.value() - 1))

    def _on_edit(self):
        try:
            self._set_value(self._clamp(int(self._edit.text())))
        except ValueError:
            self._edit.setText(str(self._min))

    def _set_value(self, v: int):
        self._edit.setText(str(v))

    def value(self) -> int:
        try:
            return self._clamp(int(self._edit.text()))
        except ValueError:
            return self._min


class FloatStepperWidget(QWidget):
    """Same look as StepperWidget but for float values (e.g. expert weights)."""

    def __init__(self, min_val: float, max_val: float, default_val: float,
                 step: float = 0.05, decimals: int = 2, parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._step = step
        self._decimals = decimals

        self.setObjectName("stepperWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QWidget#stepperWidget {
               
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        self.setFixedHeight(34)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self._edit = QLineEdit(f"{default_val:.{decimals}f}")
        self._edit.setCursor(Qt.PointingHandCursor)
        self._edit.setStyleSheet("""
            QLineEdit {
                font-family: 'Inter'; font-size: 13px; font-weight: 400;
                color: #1e3333; background: transparent;
                border: none; padding: 0 10px;
            }
        """)
        self._edit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._edit.editingFinished.connect(self._on_edit)
        row.addWidget(self._edit, 1)

        btn_container = QWidget()
        btn_container.setFixedSize(24, 22)
        btn_container.setStyleSheet("QWidget { background: transparent; border: none; }")
        btn_col = QVBoxLayout(btn_container)
        btn_col.setContentsMargins(0, 0, 0, 0)
        btn_col.setSpacing(1)

        btn_base = """
            QPushButton { background: transparent; border: none; padding: 0; }
            QPushButton:hover { background: transparent; }
            QPushButton:pressed { background: transparent; }
        """
        self._up_btn = QPushButton()
        self._up_btn.setFixedSize(24, 10)
        self._up_btn.setIcon(QIcon("assets/icons/chevron-up.svg"))
        self._up_btn.setIconSize(QSize(10, 6))
        self._up_btn.setCursor(Qt.PointingHandCursor)
        self._up_btn.setStyleSheet(btn_base + "QPushButton { border-top-right-radius: 4px; }")
        self._up_btn.clicked.connect(self._increment)

        self._down_btn = QPushButton()
        self._down_btn.setFixedSize(24, 10)
        self._down_btn.setIcon(QIcon("assets/icons/chevron-down.svg"))
        self._down_btn.setIconSize(QSize(10, 6))
        self._down_btn.setCursor(Qt.PointingHandCursor)
        self._down_btn.setStyleSheet(btn_base + "QPushButton { border-bottom-right-radius: 4px; }")
        self._down_btn.clicked.connect(self._decrement)

        btn_col.addWidget(self._up_btn)
        btn_col.addWidget(self._down_btn)
        row.addWidget(btn_container)

    def _clamp(self, v: float) -> float:
        return max(self._min, min(self._max, round(v, self._decimals)))

    def _increment(self):
        self._set_value(self._clamp(self.value() + self._step))

    def _decrement(self):
        self._set_value(self._clamp(self.value() - self._step))

    def _on_edit(self):
        try:
            self._set_value(self._clamp(float(self._edit.text())))
        except ValueError:
            self._edit.setText(f"{self._min:.{self._decimals}f}")

    def _set_value(self, v: float):
        self._edit.setText(f"{v:.{self._decimals}f}")

    def value(self) -> float:
        try:
            return self._clamp(float(self._edit.text()))
        except ValueError:
            return self._min


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DEMATEL Toolkit ")
        self.resize(1400, 900)
        _logo = _ASSETS_DIR / "logo.png"
        if _logo.exists():
            self.setWindowIcon(QIcon(str(_logo)))

        self.factor_name_inputs: list[QLineEdit] = []
        self.expert_name_inputs: list[QLineEdit] = []
        self.expert_weight_inputs: list[FloatStepperWidget] = []

        self.matrix_editor: MatrixEditorWidget | None = None
        self.matrix_editor_box: QGroupBox | None = None
        self.current_result = None
        self.results_box: QGroupBox | None = None

        self.current_solver_mode: str | None = None
        self.previous_solver_text: str = "DEMATEL"

        self._build_ui()

    def _solver_mode(self, solver_text: str) -> str:
        normalized = solver_text.strip().lower().replace("_", " ")
        if normalized == "fuzzy z-dematel":
            return "z"
        return "standard"

    def _build_ui(self) -> None:
        # Single scroll area covering the whole window
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_scroll.setStyleSheet("QScrollArea { background: #f7fbfb; border: none; }")
        self.setCentralWidget(main_scroll)

        container = QWidget()
        container.setObjectName("centralWidget")
        container.setStyleSheet("QWidget#centralWidget { background-color: #f7fbfb; }")
        main_scroll.setWidget(container)

        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(150, 35, 150, 35)
        self.main_layout.setSpacing(16)

        self.main_layout.addSpacing(30)

        title_block = QWidget()
        title_block.setStyleSheet("background: transparent;")
        title_block_layout = QVBoxLayout(title_block)
        title_block_layout.setContentsMargins(0, 0, 0, 0)
        title_block_layout.setSpacing(6)

        title = QLabel("DEMATEL Toolkit")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-family: 'Inter'; font-size: 24px; font-weight: 600; background: transparent; color: #2d4d4c;")
        title_block_layout.addWidget(title)

        subtitle = QLabel("Cause and Effect Analysis")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-family: 'Inter'; font-size: 13px; font-weight: 300; background: transparent; color: #9a9a9a;")
        title_block_layout.addWidget(subtitle)

        self.main_layout.addWidget(title_block)
        self.main_layout.addSpacing(6)

        self.main_layout.addWidget(self._build_setup_box())

        # Dynamic content — plain widget, no inner scroll
        self.dynamic_container = QWidget()
        self.dynamic_container.setStyleSheet("background: transparent;")
        self.dynamic_layout = QVBoxLayout(self.dynamic_container)
        self.dynamic_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_layout.setSpacing(16)
        self.main_layout.addWidget(self.dynamic_container)

        self.main_layout.addStretch()
        self.main_layout.addSpacing(30)

    def _build_setup_box(self) -> QWidget:
        card = QWidget()
        card.setObjectName("setupCard")
        card.setStyleSheet("""
            QWidget#setupCard {
                background: white;
                border-radius: 8px;
                border: 1px solid #e8e8e8;
            }
            QWidget#setupCard QLabel {
                background: transparent;
                border: none;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(24, 20, 24, 16)
        outer.setSpacing(0)

        # --- Header ---
        title_lbl = QLabel("Analysis Setup")
        title_lbl.setStyleSheet(
            "font-family: 'Inter'; font-size: 15px; font-weight: 600; color: #1e3333;"
        )
        outer.addWidget(title_lbl)

        outer.addSpacing(4)

        subtitle_lbl = QLabel("Choose your preferred solver and threshold identifier. The number of experts and factors can be defined subsequently.")
        subtitle_lbl.setStyleSheet(
            "font-family: 'Inter'; font-size: 12px; font-weight: 300; color: #9a9a9a;"
        )
        subtitle_lbl.setWordWrap(True)
        outer.addWidget(subtitle_lbl)

        outer.addSpacing(20)

        # --- 2-column grid ---
        field_label_style = (
            "font-family: 'Inter'; font-size: 12px; font-weight: 400; color: #111111;"
        )
        combo_style = """
            QComboBox {
                font-family: 'Inter'; font-size: 13px; font-weight: 400;
                color: #1e3333;
                border: 1px solid #e0e0e0; border-radius: 6px;
                padding: 4px 14px;
            }
            QComboBox:focus { border: 1px solid #bcdcdc; }
            QComboBox::drop-down { border: none; width: 28px; }
            QComboBox::down-arrow {
                image: url(assets/icons/chevron-down.svg);
                width: 10px; height: 6px;
            }
            QComboBox QAbstractItemView {
                font-family: 'Inter'; font-size: 12px; font-weight: 400;
                color: #1e3333;
                border: none; outline: none;
                padding: 0; margin: 0;
            }
            QComboBox QAbstractItemView::item {
                color: #1e3333;
                padding: 4px 10px;
                min-height: 22px;
                border: none; margin: 0;
            }
            QComboBox QAbstractItemView::item:hover,
            QComboBox QAbstractItemView::item:selected {
                background: #d0e7e6;
                color: #1e3333;
            }
        """

        def _setup_combo(combo: QComboBox) -> None:
            combo.setView(QListView())
            combo.view().setFrameShape(QFrame.Shape.NoFrame)
            combo.view().setSpacing(0)
            combo.view().viewport().setStyleSheet("border: none;")
            combo.setFixedHeight(34)
            combo.setStyleSheet(combo_style)
            combo.setCursor(Qt.PointingHandCursor)

        self.solver_combo = QComboBox()
        self.solver_combo.addItems(["DEMATEL", "Fuzzy DEMATEL", "Grey DEMATEL", "Fuzzy Z-DEMATEL"])
        self.solver_combo.currentTextChanged.connect(self.on_solver_changed)
        _setup_combo(self.solver_combo)

        self.threshold_combo = QComboBox()
        self.threshold_combo.addItems([
            "Average", "First quartile", "Median", "Third quartile", "Maximum Mean De-Entropy",
        ])
        _setup_combo(self.threshold_combo)

        self.expert_count_spin = StepperWidget(1, 50, 2)
        self.factor_count_spin = StepperWidget(2, 100, 4)

        def field_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(field_label_style)
            return lbl

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        grid.addWidget(field_label("Solver type"),       0, 0)
        grid.addWidget(self.solver_combo,                1, 0)
        grid.addWidget(field_label("Threshold method"),  0, 1)
        grid.addWidget(self.threshold_combo,             1, 1)

        grid.setRowMinimumHeight(2, 12)

        grid.addWidget(field_label("Number of experts"), 3, 0)
        grid.addWidget(self.expert_count_spin,           4, 0)
        grid.addWidget(field_label("Number of factors"), 3, 1)
        grid.addWidget(self.factor_count_spin,           4, 1)

        outer.addLayout(grid)
        outer.addSpacing(28)

        # --- Generate button ---
        self.generate_button = AnimatedButton("  Generate Input Forms")
        self.generate_button.setIcon(qta.icon("fa6s.list", color="#2d4d4c"))
        self.generate_button.setIconSize(QSize(14, 14))
        self.generate_button.clicked.connect(self.generate_input_forms)
        self.generate_button.setFixedHeight(38)
        self.generate_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.generate_button.setCursor(Qt.PointingHandCursor)
        outer.addWidget(self.generate_button)

        return card

    def on_solver_changed(self, new_solver: str) -> None:
        old_mode = self._solver_mode(self.previous_solver_text)
        new_mode = self._solver_mode(new_solver)

        if self.matrix_editor is None:
            self.previous_solver_text = new_solver
            return

        if old_mode == new_mode:
            self.previous_solver_text = new_solver
            return

        if new_mode == "z":
            message = (
                "The current matrix uses standard linguistic judgments and is not valid for "
                "Fuzzy Z-DEMATEL.\n\n"
                "Fuzzy Z-DEMATEL requires combined influence–reliability judgments.\n\n"
                "The matrix editor will be regenerated and current matrix values will be lost."
            )
        else:
            message = (
                "The current matrix uses combined influence–reliability judgments and is not "
                "valid for the selected solver.\n\n"
                "The matrix editor will be regenerated and current matrix values will be lost."
            )

        reply = QMessageBox.warning(
            self,
            "Solver Change Detected",
            message,
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )

        if reply == QMessageBox.Cancel:
            self.solver_combo.blockSignals(True)
            self.solver_combo.setCurrentText(self.previous_solver_text)
            self.solver_combo.blockSignals(False)
            return

        if self.matrix_editor_box is not None:
            self.matrix_editor_box.deleteLater()
            self.matrix_editor_box = None

        if self.results_box is not None:
            self.results_box.close()
            self.results_box.deleteLater()
            self.results_box = None

        self.matrix_editor = None
        self.current_result = None
        self.previous_solver_text = new_solver

    def clear_dynamic_layout(self) -> None:
        while self.dynamic_layout.count():
            item = self.dynamic_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.factor_name_inputs.clear()
        self.expert_name_inputs.clear()
        self.expert_weight_inputs.clear()
        self.matrix_editor = None
        self.matrix_editor_box = None
        self.current_result = None
        self.results_box = None

    def _make_card(self, obj_name: str, title: str, subtitle: str = "") -> tuple[QWidget, QVBoxLayout]:
        card = QWidget()
        card.setObjectName(obj_name)
        card.setStyleSheet(f"""
            QWidget#{obj_name} {{
                background: white;
                border-radius: 8px;
                border: 1px solid #e8e8e8;
            }}
            QWidget#{obj_name} QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-family: 'Inter'; font-size: 15px; font-weight: 600; color: #1e3333;")
        layout.addWidget(title_lbl)

        if subtitle:
            layout.addSpacing(4)
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 300; color: #9a9a9a;")
            sub_lbl.setWordWrap(True)
            layout.addWidget(sub_lbl)

        layout.addSpacing(20)
        return card, layout

    def generate_input_forms(self) -> None:
        self.clear_dynamic_layout()
        self.previous_solver_text = self.solver_combo.currentText()

        expert_count = self.expert_count_spin.value()
        factor_count = self.factor_count_spin.value()
        default_weight = round(1.0 / expert_count, 2)

        card, card_outer = self._make_card(
            "factorsCard",
            "Factors and Experts",
            "Define the factors to be analyzed and specify expert weights.",
        )

        col_lbl_style  = "font-family: 'Inter'; font-size: 13px; font-weight: 500; color: #1e3333; background: transparent;"
        row_lbl_style  = "font-family: 'Inter'; font-size: 12px; color: #9a9a9a; background: transparent;"
        input_style = """
            QLineEdit {
                font-family: 'Inter'; font-size: 13px; font-weight: 400;
                color: #1e3333; 
                border: 1px solid #e0e0e0; border-radius: 4px;
                padding: 0 10px;
            }
            QLineEdit:focus { border: 1px solid #bcdcdc; }
        """

        # ── Factors column ──────────────────────────────────────────────
        factors_col = QWidget()
        factors_col.setStyleSheet("background: transparent;")
        factors_col_layout = QVBoxLayout(factors_col)
        factors_col_layout.setContentsMargins(0, 0, 24, 0)
        factors_col_layout.setSpacing(8)

        factors_header = QLabel("Factors")
        factors_header.setStyleSheet(col_lbl_style)
        factors_col_layout.addWidget(factors_header)
        factors_col_layout.addSpacing(6)

        for i in range(factor_count):
            coded_name = f"F{i + 1}"
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(12)

            lbl = QLabel(coded_name)
            lbl.setFixedWidth(22)
            lbl.setStyleSheet(row_lbl_style)

            field = QLineEdit(coded_name)
            field.setFixedHeight(34)
            field.setStyleSheet(input_style)
            self.factor_name_inputs.append(field)

            row_layout.addWidget(lbl)
            row_layout.addWidget(field, 1)
            factors_col_layout.addWidget(row)

        factors_col_layout.addStretch()

        # ── Vertical divider ────────────────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFixedWidth(1)
        divider.setStyleSheet("background: #e8e8e8; border: none;")

        # ── Experts column ───────────────────────────────────────────────
        experts_col = QWidget()
        experts_col.setStyleSheet("background: transparent;")
        experts_col_layout = QVBoxLayout(experts_col)
        experts_col_layout.setContentsMargins(24, 0, 0, 0)
        experts_col_layout.setSpacing(8)

        experts_header = QLabel("Experts and Weights")
        experts_header.setStyleSheet(col_lbl_style)
        experts_col_layout.addWidget(experts_header)
        experts_col_layout.addSpacing(6)

        for i in range(expert_count):
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            lbl = QLabel(f"Expert {i + 1}")
            lbl.setFixedWidth(56)
            lbl.setStyleSheet(row_lbl_style)

            name_input = QLineEdit(f"Expert {i + 1}")
            name_input.setFixedHeight(34)
            name_input.setStyleSheet(input_style)

            weight_lbl = QLabel("Weight")
            weight_lbl.setStyleSheet(row_lbl_style)

            weight_input = FloatStepperWidget(0.0, 1.0, default_weight, step=0.05, decimals=2)
            weight_input.setFixedWidth(90)

            self.expert_name_inputs.append(name_input)
            self.expert_weight_inputs.append(weight_input)

            row_layout.addWidget(lbl)
            row_layout.addWidget(name_input, 1)
            row_layout.addWidget(weight_lbl)
            row_layout.addWidget(weight_input)
            experts_col_layout.addWidget(row)

        experts_col_layout.addStretch()

        # ── Assemble columns ─────────────────────────────────────────────
        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(0)
        columns_layout.addWidget(factors_col, 1)
        columns_layout.addWidget(divider)
        columns_layout.addWidget(experts_col, 1)
        card_outer.addLayout(columns_layout)
        card_outer.addSpacing(28)

        h_divider = QFrame()
        h_divider.setFrameShape(QFrame.Shape.HLine)
        h_divider.setFixedHeight(1)
        h_divider.setStyleSheet("background: #e8e8e8; border: none;")
        card_outer.addWidget(h_divider)
        card_outer.addSpacing(24)

        self.create_matrix_button = AnimatedButton(
            "  Next: Create Matrix Editor",
            color_normal="#ffffff",
            color_hover="#e6e6e6",
            color_pressed="#e6e6e6",
            border="1px solid #e0e0e0",
        )
        self.create_matrix_button.setIcon(qta.icon("fa6s.arrow-right", color="#2d4d4c"))
        self.create_matrix_button.setIconSize(QSize(13, 13))
        self.create_matrix_button.clicked.connect(self.show_matrix_editor)
        self.create_matrix_button.setFixedHeight(38)
        self.create_matrix_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.create_matrix_button.setCursor(Qt.PointingHandCursor)
        card_outer.addWidget(self.create_matrix_button)

        self.dynamic_layout.addWidget(card)

    def _validate_names_and_weights(self) -> tuple[list[str], list[str], list[float]] | None:
        factor_names = [field.text().strip() for field in self.factor_name_inputs]
        expert_names = [field.text().strip() for field in self.expert_name_inputs]
        weights = [field.value() for field in self.expert_weight_inputs]

        if any(not name for name in factor_names):
            QMessageBox.warning(self, "Input Error", "All factor names must be filled.")
            return None

        if any(not name for name in expert_names):
            QMessageBox.warning(self, "Input Error", "All expert names must be filled.")
            return None

        if len(set(factor_names)) != len(factor_names):
            QMessageBox.warning(self, "Input Error", "Factor names must be unique.")
            return None

        if abs(sum(weights) - 1.0) > 1e-8:
            QMessageBox.warning(self, "Input Error", "Expert weights must sum to 1.")
            return None

        return factor_names, expert_names, weights

    def show_matrix_editor(self) -> None:
        validated = self._validate_names_and_weights()
        if validated is None:
            return

        factor_names, expert_names, _ = validated

        if self.matrix_editor_box is not None:
            self.matrix_editor_box.deleteLater()

        card, box_layout = self._make_card(
            "matrixCard",
            "Matrix Input",
            'Diagonal cells are fixed to "No influence" because a factor cannot directly influence itself.',
        )

        selected_solver = self.solver_combo.currentText().strip().lower().replace("_", " ")
        if selected_solver == "fuzzy z-dematel":
            dropdown_terms = Z_LINGUISTIC_TERMS
            diagonal_value = Z_NO_INFLUENCE_DEFAULT
        else:
            dropdown_terms = LINGUISTIC_TERMS
            diagonal_value = NO_INFLUENCE_LABEL

        self.matrix_editor = MatrixEditorWidget(
            factor_names=factor_names,
            expert_names=expert_names,
            dropdown_terms=dropdown_terms,
            diagonal_value=diagonal_value,
        )
        box_layout.addWidget(self.matrix_editor)
        box_layout.addSpacing(28)

        run_divider = QFrame()
        run_divider.setFrameShape(QFrame.Shape.HLine)
        run_divider.setFixedHeight(1)
        run_divider.setStyleSheet("background: #e8e8e8; border: none;")
        box_layout.addWidget(run_divider)
        box_layout.addSpacing(24)

        note_lbl = QLabel("Note: Diagonal cells are fixed to \u201cNo influence,\u201d since a factor cannot directly influence itself.")
        note_lbl.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 300; color: #9a9a9a; background: transparent;")
        note_lbl.setWordWrap(True)
        box_layout.addWidget(note_lbl)
        box_layout.addSpacing(8)

        self.run_error_label = QLabel("")
        self.run_error_label.setStyleSheet("font-family: 'Inter'; font-size: 12px; font-weight: 400; color: #d02e34; background: transparent;")
        self.run_error_label.setWordWrap(True)
        self.run_error_label.hide()
        box_layout.addWidget(self.run_error_label)
        box_layout.addSpacing(16)

        self.run_button = AnimatedButton("  Run Analysis",
                                         color_normal="#448581",
                                         color_hover="#57a099",
                                         color_pressed="#57a099",
                                         color_text="#eaf4f4")
        self.run_button.setIcon(qta.icon("fa6s.play", color="#eaf4f4"))
        self.run_button.setIconSize(QSize(12, 12))
        self.run_button.clicked.connect(self.run_analysis_from_ui)
        self.run_button.setFixedHeight(38)
        self.run_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.run_button.setCursor(Qt.PointingHandCursor)
        box_layout.addWidget(self.run_button)

        self.matrix_editor_box = card
        self.dynamic_layout.addWidget(card)

    def run_analysis_from_ui(self) -> None:
        if self.matrix_editor is None:
            QMessageBox.warning(self, "Missing Input", "Create the matrix editor first.")
            return

        validated = self._validate_names_and_weights()
        if validated is None:
            return

        threshold_method = self.threshold_combo.currentText().strip()
        if not threshold_method:
            QMessageBox.warning(
                self,
                "Missing Threshold Method",
                "Please select a threshold method before running the analysis.",
            )
            return

        factor_names, expert_names, weights = validated
        matrices = self.matrix_editor.get_all_matrices()

        try:
            payload = AnalysisInput(
                solver_type=self.solver_combo.currentText(),
                factors=factor_names,
                experts=[
                    ExpertFormData(
                        name=expert_names[i],
                        weight=weights[i],
                        matrix=matrices[i],
                    )
                    for i in range(len(expert_names))
                ],
                threshold_method=threshold_method,
            )

            self.current_result = run_analysis(payload)
            if hasattr(self, "run_error_label"):
                self.run_error_label.hide()
                self.run_error_label.setText("")
            self.show_results()
        except Exception as exc:
            if hasattr(self, "run_error_label"):
                self.run_error_label.setText(str(exc))
                self.run_error_label.show()
            else:
                QMessageBox.critical(self, "Analysis Error", str(exc))

    def show_results(self) -> None:
        if self.current_result is None:
            return

        if self.results_box is not None:
            self.results_box.deleteLater()

        from .results_viewer_widget import ResultsViewerWidget

        card, results_layout = self._make_card(
            "resultsCard",
            "Results",
            "Analysis complete. Review the cause-and-effect relationships below.",
        )

        viewer = ResultsViewerWidget(self.current_result)
        results_layout.addWidget(viewer)

        self.results_box = card
        self.dynamic_layout.addWidget(card)


def main() -> None:
    app = QApplication(sys.argv)

    from .font_loader import ensure_inter_fonts
    import matplotlib
    import matplotlib.font_manager as _fm

    font_paths = ensure_inter_fonts(_ASSETS_DIR)
    for path in font_paths:
        QFontDatabase.addApplicationFont(path)
        _fm.fontManager.addfont(path)

    matplotlib.rcParams["font.family"] = ["Inter", "DejaVu Sans"]
    app.setFont(QFont("Inter"))

    app.setStyleSheet("""
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            border: 1px solid #e2e5e9;
            border-radius: 4px;
    
            padding: 0 10px;
        }

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #bcdcdc;
        }

        QComboBox::drop-down {
            border: none;
            width: 24px;
        }

        QComboBox::down-arrow {
            image: url(assets/icons/chevron-down.svg);
            width: 10px;
            height: 6px;
        }

        QSpinBox::up-button, QDoubleSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #e2e5e9;
            background: transparent;
        }

        QSpinBox::down-button, QDoubleSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid #e2e5e9;
            background: transparent;
        }

        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
            image: none;
            width: 0;
            height: 0;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 6px solid #a3a3a3;
        }

        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
            image: none;
            width: 0;
            height: 0;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid #a3a3a3;
        }

        QToolTip {
            font-family: 'Inter'; font-size: 12px; font-weight: 400;
            color: #1a1a1a;
            background: #f2f2f2;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px 14px;
        }

        QMessageBox QPushButton {
            font-family: 'Inter'; font-size: 13px; font-weight: 500;
            color: #eaf4f4;
            background-color: #386c6a;
            border: none;
            border-radius: 5px;
            padding: 6px 20px;
            min-width: 80px;
        }

        QMessageBox QPushButton:hover {
            background-color: #57a099;
        }

        QMessageBox QPushButton:pressed {
            background-color: #57a099;
        }
    """)

    logo_path = _ASSETS_DIR / "logo.png"
    if logo_path.exists():
        app.setWindowIcon(QIcon(str(logo_path)))

    def _set_macos_dock_icon():
        if not logo_path.exists():
            return
        try:
            from AppKit import NSApplication, NSImage
            image = NSImage.alloc().initWithContentsOfFile_(str(logo_path))
            NSApplication.sharedApplication().setApplicationIconImage_(image)
        except Exception:
            pass

    from PySide6.QtCore import QTimer
    QTimer.singleShot(500, _set_macos_dock_icon)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())