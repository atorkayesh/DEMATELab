# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 13:46:13 2026

@author: Ali
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QLabel,
    QListView,
    QScrollArea,
    QSizePolicy,
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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.factor_names = factor_names
        self.dropdown_terms = dropdown_terms
        self.diagonal_value = diagonal_value
        self.cell_widgets: list[list[QComboBox]] = []

        self._build_ui()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setSizeAdjustPolicy(QScrollArea.SizeAdjustPolicy.AdjustToContents)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
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
            QScrollBar:horizontal {
                background: transparent;
                height: 4px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #c8d8d8;
                border-radius: 2px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover { background: #8ab0b0; }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal { width: 0px; }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal { background: transparent; }
        """)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        grid = QGridLayout(content)
        grid.setSpacing(4)
        grid.setContentsMargins(8, 8, 8, 8)

        grid.addWidget(QLabel(""), 0, 0)

        header_style = "font-family: 'Inter'; font-size: 12px; font-weight: 600; color: #1e3333; background: transparent;"

        for j, factor in enumerate(self.factor_names, start=1):
            label = QLabel(factor)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(header_style)
            grid.addWidget(label, 0, j)
            grid.setColumnStretch(j, 1)

        for i, factor in enumerate(self.factor_names, start=1):
            row_label = QLabel(factor)
            row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row_label.setStyleSheet(header_style + " padding-right: 12px;")
            grid.addWidget(row_label, i, 0)

            row_widgets: list[QComboBox] = []

            for j in range(1, len(self.factor_names) + 1):
                combo = QComboBox()
                combo.setView(QListView())
                combo.view().setFrameShape(QFrame.Shape.NoFrame)
                combo.view().setSpacing(0)
                combo.view().viewport().setStyleSheet("border: none;")
                combo.setFixedHeight(34)
                combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                combo.setStyleSheet("""
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
                        font-family: 'Inter'; font-size: 12px;
                        font-weight: 400;
                        color: #1e3333;
                        border: none;
                        outline: none;
                        padding: 0;
                        margin: 0;
                    }
                    QComboBox QAbstractItemView::item {
                        color: #1e3333;
                        padding: 4px 10px;
                        min-height: 22px;
                        border: none;
                        margin: 0;
                    }
                    QComboBox QAbstractItemView::item:hover,
                    QComboBox QAbstractItemView::item:selected {
                        background: #d0e7e6;
                        color: #1e3333;
                    }
                """)
                combo.addItems(self.dropdown_terms)

                if i == j:
                    combo.setCurrentText(self.diagonal_value)
                    combo.setEnabled(False)
                    combo.setStyleSheet(combo.styleSheet() + """
                        QComboBox:disabled {
                            background: #f0f0f0;
                            color: #b0b0b0;
                            border: 1px solid #e0e0e0;
                        }
                    """)
                else:
                    combo.setCurrentText(self.diagonal_value)

                grid.addWidget(combo, i, j)
                row_widgets.append(combo)

            self.cell_widgets.append(row_widgets)


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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.factor_names = factor_names
        self.expert_names = expert_names
        self.dropdown_terms = dropdown_terms
        self.diagonal_value = diagonal_value

        self.tabs: list[ExpertMatrixTab] = []

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background: white;
                border: none;
                padding-top: 30px;
            }
            QTabWidget::tab-bar {
                alignment: right;
            }
            QTabBar {
                background: #f0f0f0;
                border-radius: 8px;
                padding: 3px;
            }
            QTabBar::tab {
                font-family: 'Inter'; font-size: 12px; font-weight: 400;
                color: #9a9a9a;
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                font-weight: 500;
                color: #1e3333;
                background: white;
                border: 1px solid #e8e8e8;
            }
            QTabBar::tab:hover:!selected { color: #1e3333; }
        """)
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.tab_widget.tabBar().show()
        self.tab_widget.tabBar().setCursor(Qt.PointingHandCursor)
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