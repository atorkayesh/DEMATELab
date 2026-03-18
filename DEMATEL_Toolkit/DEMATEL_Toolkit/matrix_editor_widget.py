# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 13:46:13 2026

@author: Ali
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class ExpertMatrixTab(QWidget):
    def __init__(
        self,
        factor_names: list[str],
        dropdown_terms: list[str],
        diagonal_value: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.factor_names = factor_names
        self.dropdown_terms = dropdown_terms
        self.diagonal_value = diagonal_value
        self.cell_widgets: list[list[QComboBox]] = []

        self._build_ui()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        grid = QGridLayout(content)
        grid.setSpacing(4)
        grid.setContentsMargins(8, 8, 8, 8)

        # Anchor content to top-left so it doesn't stretch to fill scroll area
        content.setSizePolicy(
            content.sizePolicy().horizontalPolicy(),
            content.sizePolicy().verticalPolicy(),
        )

        grid.addWidget(QLabel(""), 0, 0)

        for j, factor in enumerate(self.factor_names, start=1):
            label = QLabel(factor)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-weight: 600;")
            grid.addWidget(label, 0, j)

        for i, factor in enumerate(self.factor_names, start=1):
            row_label = QLabel(factor)
            row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row_label.setStyleSheet("font-weight: 600;")
            grid.addWidget(row_label, i, 0)

            row_widgets: list[QComboBox] = []

            for j in range(1, len(self.factor_names) + 1):
                combo = QComboBox()
                combo.addItems(self.dropdown_terms)

                if i == j:
                    combo.setCurrentText(self.diagonal_value)
                    combo.setEnabled(False)
                else:
                    combo.setCurrentText(self.diagonal_value)

                grid.addWidget(combo, i, j)
                row_widgets.append(combo)

            self.cell_widgets.append(row_widgets)

        # Push everything to the top-left — eliminates the gap
        grid.setRowStretch(len(self.factor_names) + 1, 1)
        grid.setColumnStretch(len(self.factor_names) + 1, 1)

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)

    def get_matrix(self) -> list[list[str]]:
        matrix: list[list[str]] = []

        for i, row in enumerate(self.cell_widgets):
            matrix_row: list[str] = []
            for j, combo in enumerate(row):
                if i == j:
                    matrix_row.append(self.diagonal_value)
                else:
                    matrix_row.append(combo.currentText())
            matrix.append(matrix_row)

        return matrix


class MatrixEditorWidget(QWidget):
    def __init__(
        self,
        factor_names: list[str],
        expert_names: list[str],
        dropdown_terms: list[str],
        diagonal_value: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.factor_names = factor_names
        self.expert_names = expert_names
        self.dropdown_terms = dropdown_terms
        self.diagonal_value = diagonal_value

        self.tabs: list[ExpertMatrixTab] = []

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        for expert_name in self.expert_names:
            tab = ExpertMatrixTab(
                factor_names=self.factor_names,
                dropdown_terms=self.dropdown_terms,
                diagonal_value=self.diagonal_value,
            )
            self.tabs.append(tab)
            self.tab_widget.addTab(tab, expert_name)

    def get_all_matrices(self) -> list[list[list[str]]]:
        return [tab.get_matrix() for tab in self.tabs]