# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 13:46:13 2026

@author: Ali
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListView,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


from .matrix_parsers import (
    NO_INFLUENCE_LABEL,
    parse_standard_linguistic_labels_from_excel_workbook_bytes,
    parse_standard_linguistic_labels_from_excel_bytes,
)


class NoWheelComboBox(QComboBox):
    """QComboBox that ignores mouse wheel events to prevent accidental value changes."""

    def wheelEvent(self, event: QWheelEvent) -> None:
        # Ignore wheel events - values should only change via dropdown selection
        event.ignore()


class SyncedScrollArea(QScrollArea):
    """QScrollArea with synced scrollbars for frozen headers."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)


class ExpertMatrixTab(QWidget):
    def __init__(
        self,
        factor_names: list[str],
        dropdown_terms: list[str],
        diagonal_value: str,
        import_all_callback=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.factor_names = factor_names
        self.dropdown_terms = dropdown_terms
        self.diagonal_value = diagonal_value
        self._supports_standard_xlsx_import = (
            self.diagonal_value == NO_INFLUENCE_LABEL
            and set(self.dropdown_terms) == {
                "No influence",
                "Low influence",
                "Medium influence",
                "High influence",
                "Extreme influence",
            }
        )
        self._import_all_callback = import_all_callback
        self.cell_widgets: list[list[NoWheelComboBox]] = []
        self.import_message_label: QLabel | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        header_style = "font-family: 'Inter'; font-size: 12px; font-weight: 600; color: #1e3333; background: white;"
        scroll_style = """
            QScrollArea { background: white; border: none; }
            QScrollBar:horizontal, QScrollBar:vertical {
                background: transparent;
                border: none;
            }
            QScrollBar:horizontal { height: 26px; margin-top: 18px; }
            QScrollBar:vertical { width: 26px; margin-left: 18px; }
            QScrollBar::handle:horizontal {
                background: #c8d8d8;
                border-radius: 3px;
                min-width: 30px;
                max-height: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c8d8d8;
                border-radius: 3px;
                min-height: 30px;
                max-width: 6px;
            }
            QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover { background: #8ab0b0; }
            QScrollBar::add-line, QScrollBar::sub-line { width: 0px; height: 0px; }
            QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
        """

        # Calculate row header width based on longest factor name
        row_header_width = 70

        # Main grid layout: [corner | col headers] / [row headers | data cells]
        matrix_container = QWidget()
        matrix_container.setStyleSheet("background: white;")
        matrix_grid = QGridLayout(matrix_container)
        matrix_grid.setSpacing(0)
        matrix_grid.setContentsMargins(8, 8, 8, 8)

        # --- Top-left corner (empty) ---
        corner = QWidget()
        corner.setFixedSize(row_header_width, 34)
        corner.setStyleSheet("background: white;")
        matrix_grid.addWidget(corner, 0, 0)

        # --- Column headers (scrolls horizontally, synced with data) ---
        col_header_scroll = SyncedScrollArea()
        col_header_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        col_header_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        col_header_scroll.setFixedHeight(34)
        col_header_scroll.setStyleSheet(scroll_style)

        col_header_content = QWidget()
        col_header_content.setStyleSheet("background: white;")
        col_header_layout = QHBoxLayout(col_header_content)
        col_header_layout.setSpacing(10)
        col_header_layout.setContentsMargins(0, 0, 0, 0)

        for factor in self.factor_names:
            label = QLabel(factor)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(header_style)
            label.setFixedWidth(185)
            label.setFixedHeight(34)
            col_header_layout.addWidget(label)

        col_header_scroll.setWidget(col_header_content)
        matrix_grid.addWidget(col_header_scroll, 0, 1)

        # --- Row headers (scrolls vertically, synced with data) ---
        row_header_scroll = SyncedScrollArea()
        row_header_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        row_header_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        row_header_scroll.setFixedWidth(row_header_width)
        row_header_scroll.setStyleSheet(scroll_style)

        row_header_content = QWidget()
        row_header_content.setStyleSheet("background: white;")
        row_header_layout = QVBoxLayout(row_header_content)
        row_header_layout.setSpacing(10)
        row_header_layout.setContentsMargins(0, 0, 0, 0)

        for factor in self.factor_names:
            label = QLabel(factor)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet(header_style + " padding-right: 12px;")
            label.setFixedHeight(34)
            row_header_layout.addWidget(label)

        row_header_scroll.setWidget(row_header_content)
        matrix_grid.addWidget(row_header_scroll, 1, 0)

        # --- Data cells (scrolls both ways) ---
        data_scroll = SyncedScrollArea()
        data_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        data_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        data_scroll.setStyleSheet(scroll_style)
        data_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        data_content = QWidget()
        data_content.setStyleSheet("background: white;")
        data_grid = QGridLayout(data_content)
        data_grid.setSpacing(10)
        data_grid.setContentsMargins(0, 0, 0, 0)

        for i in range(len(self.factor_names)):
            row_widgets: list[NoWheelComboBox] = []

            for j in range(len(self.factor_names)):
                combo = NoWheelComboBox()
                combo.setView(QListView())
                combo.view().setFrameShape(QFrame.Shape.NoFrame)
                combo.view().setSpacing(0)
                combo.view().viewport().setStyleSheet("border: none;")
                combo.setFixedHeight(34)
                combo.setFixedWidth(185)
                combo.addItems(self.dropdown_terms)

                if i == j:
                    combo.setCurrentText(self.diagonal_value)
                    combo.setEnabled(False)
                    combo.setStyleSheet("""
                        QComboBox {
                            font-family: 'Inter'; font-size: 13px; font-weight: 400;
                            color: #b0b0b0;
                            background: #f0f0f0;
                            border: 1px solid #e0e0e0; border-radius: 6px;
                            padding: 4px 14px;
                        }
                        QComboBox::drop-down { border: none; width: 28px; }
                        QComboBox::down-arrow {
                            image: url(assets/icons/chevron-down.svg);
                            width: 10px; height: 6px;
                        }
                    """)
                else:
                    combo.setCurrentText(self.diagonal_value)
                    combo.setProperty("default_value", self.diagonal_value)
                    combo.currentTextChanged.connect(
                        lambda text, c=combo: self._update_combo_style(c, text)
                    )
                    self._apply_combo_style(combo, is_selected=False)

                data_grid.addWidget(combo, i, j)
                row_widgets.append(combo)

            self.cell_widgets.append(row_widgets)

        data_scroll.setWidget(data_content)
        matrix_grid.addWidget(data_scroll, 1, 1)

        # Sync horizontal scroll between column headers and data
        data_scroll.horizontalScrollBar().valueChanged.connect(
            col_header_scroll.horizontalScrollBar().setValue
        )
        col_header_scroll.horizontalScrollBar().valueChanged.connect(
            data_scroll.horizontalScrollBar().setValue
        )

        # Sync vertical scroll between row headers and data
        data_scroll.verticalScrollBar().valueChanged.connect(
            row_header_scroll.verticalScrollBar().setValue
        )
        row_header_scroll.verticalScrollBar().valueChanged.connect(
            data_scroll.verticalScrollBar().setValue
        )

        # Set matrix container to expand
        matrix_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        outer_layout.addWidget(matrix_container, 1)
        outer_layout.addSpacing(14)

        import_row = QHBoxLayout()
        import_row.setContentsMargins(0, 0, 0, 0)

        self.import_button = self._create_import_button("Import Matrix from XLSX")
        self.import_button.clicked.connect(self._import_matrix_from_xlsx)
        import_row.addWidget(self.import_button)

        if self._supports_standard_xlsx_import and self._import_all_callback is not None:
            self.import_all_button = self._create_import_button("Import All Experts from XLSX")
            self.import_all_button.clicked.connect(self._import_all_callback)
            import_row.addWidget(self.import_all_button)

        import_row.addStretch()
        outer_layout.addLayout(import_row)

        self.import_message_label = QLabel("")
        self.import_message_label.setWordWrap(True)
        self.import_message_label.setVisible(False)
        self.import_message_label.setStyleSheet("""
            QLabel {
                font-family: 'Inter';
                font-size: 11px;
                font-weight: 500;
                color: #c62828;
                background: transparent;
                padding-top: 4px;
            }
        """)
        outer_layout.addWidget(self.import_message_label)

    def _create_import_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedHeight(34)
        button.setStyleSheet("""
            QPushButton {
                font-family: 'Inter'; font-size: 12px; font-weight: 500;
                color: #1e3333;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 0 16px;
            }
            QPushButton:hover {
                border: 1px solid #bcdcdc;
                background: #f7fbfb;
            }
            QPushButton:pressed {
                background: #d0e7e6;
            }
        """)
        return button

    def _update_combo_style(self, combo: NoWheelComboBox, text: str) -> None:
        """Update combo background based on whether value differs from default."""
        default_value = combo.property("default_value")
        is_selected = text != default_value
        self._apply_combo_style(combo, is_selected)

    def _apply_combo_style(self, combo: NoWheelComboBox, is_selected: bool) -> None:
        """Apply the appropriate style based on selection state."""
        if is_selected:
            # Subtle green tint to indicate selection
            bg_color = "#e8f5f4"
        else:
            # Default white background
            bg_color = "white"

        combo.setStyleSheet(f"""
            QComboBox {{
                font-family: 'Inter'; font-size: 13px; font-weight: 400;
                color: #1e3333;
                background: {bg_color};
                border: 1px solid #e0e0e0; border-radius: 6px;
                padding: 4px 14px;
            }}
            QComboBox:focus {{ border: 1px solid #bcdcdc; }}
            QComboBox::drop-down {{ border: none; width: 28px; }}
            QComboBox::down-arrow {{
                image: url(assets/icons/chevron-down.svg);
                width: 10px; height: 6px;
            }}
            QComboBox QAbstractItemView {{
                font-family: 'Inter'; font-size: 12px;
                font-weight: 400;
                color: #1e3333;
                border: none;
                outline: none;
                padding: 0;
                margin: 0;
            }}
            QComboBox QAbstractItemView::item {{
                color: #1e3333;
                padding: 4px 10px;
                min-height: 22px;
                border: none;
                margin: 0;
            }}
            QComboBox QAbstractItemView::item:hover,
            QComboBox QAbstractItemView::item:selected {{
                background: #d0e7e6;
                color: #1e3333;
            }}
        """)

    def set_import_message(self, message: str | None) -> None:
        if self.import_message_label is None:
            return

        text = (message or "").strip()
        self.import_message_label.setText(text)
        self.import_message_label.setVisible(bool(text))

    def clear_import_message(self) -> None:
        self.set_import_message("")

    def _import_matrix_from_xlsx(self) -> None:
        if not self._supports_standard_xlsx_import:
            QMessageBox.information(
                self,
                "Import Not Available",
                "XLSX import currently supports only the standard linguistic scale:\n"
                "No influence, Low influence, Medium influence, High influence, Extreme influence.",
            )
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Matrix from XLSX",
            "",
            "Excel Files (*.xlsx)",
        )
        if not file_path:
            return

        self.clear_import_message()

        try:
            with open(file_path, "rb") as handle:
                matrix = parse_standard_linguistic_labels_from_excel_bytes(
                    file_bytes=handle.read(),
                    expected_size=len(self.factor_names),
                )
            self.set_matrix(matrix)
        except ValueError as exc:
            self.set_import_message(f"Import failed: {exc}")
        except Exception as exc:
            self.set_import_message(f"Import failed: {exc}")

    def set_matrix(self, matrix: list[list[str]]) -> None:
        expected_size = len(self.factor_names)
        if len(matrix) != expected_size or any(len(row) != expected_size for row in matrix):
            raise ValueError(
                f"Imported matrix must be exactly {expected_size} x {expected_size}."
            )

        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                combo = self.cell_widgets[i][j]
                if i == j:
                    combo.setCurrentText(self.diagonal_value)
                    continue

                if value not in self.dropdown_terms:
                    raise ValueError(f"Unsupported imported value: {value}")

                combo.setCurrentText(value)

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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.factor_names = factor_names
        self.expert_names = expert_names
        self.dropdown_terms = dropdown_terms
        self.diagonal_value = diagonal_value
        self._supports_standard_xlsx_import = (
            self.diagonal_value == NO_INFLUENCE_LABEL
            and set(self.dropdown_terms) == {
                "No influence",
                "Low influence",
                "Medium influence",
                "High influence",
                "Extreme influence",
            }
        )

        self.tabs: list[ExpertMatrixTab] = []

        self._build_ui()

    def _set_import_message_for_all_tabs(self, message: str | None) -> None:
        for tab in self.tabs:
            tab.set_import_message(message)

    def _clear_import_messages(self) -> None:
        self._set_import_message_for_all_tabs("")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background: white;
                border: none;
                padding-top: 10px;
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
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tab_widget.tabBar().show()
        self.tab_widget.tabBar().setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.tab_widget)

        for expert_name in self.expert_names:
            tab = ExpertMatrixTab(
                factor_names=self.factor_names,
                dropdown_terms=self.dropdown_terms,
                diagonal_value=self.diagonal_value,
                import_all_callback=self._import_all_matrices_from_xlsx if self._supports_standard_xlsx_import else None,
            )
            self.tabs.append(tab)
            self.tab_widget.addTab(tab, expert_name)

    def _create_import_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedHeight(34)
        button.setStyleSheet("""
            QPushButton {
                font-family: 'Inter'; font-size: 12px; font-weight: 500;
                color: #1e3333;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 0 16px;
            }
            QPushButton:hover {
                border: 1px solid #bcdcdc;
                background: #f7fbfb;
            }
            QPushButton:pressed {
                background: #d0e7e6;
            }
        """)
        return button

    def _import_all_matrices_from_xlsx(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import All Expert Matrices from XLSX",
            "",
            "Excel Files (*.xlsx)",
        )
        if not file_path:
            return

        self._clear_import_messages()

        try:
            with open(file_path, "rb") as handle:
                workbook_matrices = parse_standard_linguistic_labels_from_excel_workbook_bytes(
                    file_bytes=handle.read(),
                    expected_size=len(self.factor_names),
                    expected_sheet_count=len(self.tabs),
                )
            self._apply_workbook_matrices(workbook_matrices)
        except ValueError as exc:
            self._set_import_message_for_all_tabs(f"Import failed: {exc}")
        except Exception as exc:
            self._set_import_message_for_all_tabs(f"Import failed: {exc}")
        else:
            self._clear_import_messages()

    def _apply_workbook_matrices(
        self,
        workbook_matrices: dict[str, list[list[str]]],
    ) -> None:
        normalized_sheet_map = {
            sheet_name.strip().casefold(): matrix
            for sheet_name, matrix in workbook_matrices.items()
        }
        normalized_expert_names = [name.strip().casefold() for name in self.expert_names]

        if all(name in normalized_sheet_map for name in normalized_expert_names):
            ordered_matrices = [normalized_sheet_map[name] for name in normalized_expert_names]
        else:
            ordered_matrices = list(workbook_matrices.values())

        for tab, matrix in zip(self.tabs, ordered_matrices):
            tab.set_matrix(matrix)

    def get_all_matrices(self) -> list[list[list[str]]]:
        return [tab.get_matrix() for tab in self.tabs]
