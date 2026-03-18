"""
@author: Ali
"""
# -*- coding: utf-8 -*-


from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
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


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DEMATEL Toolkit ")
        self.resize(1400, 900)

        self.factor_name_inputs: list[QLineEdit] = []
        self.expert_name_inputs: list[QLineEdit] = []
        self.expert_weight_inputs: list[QDoubleSpinBox] = []

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
        central = QWidget()
        self.setCentralWidget(central)

        self.main_layout = QVBoxLayout(central)
        self.main_layout.setSpacing(16)

        title = QLabel("Cause-and-effect analyis with DEMATEL")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        self.main_layout.addWidget(title)

        self.main_layout.addWidget(self._build_setup_box())
        self.main_layout.addWidget(self._build_dynamic_input_area(), stretch=1)

    def _build_setup_box(self) -> QGroupBox:
        box = QGroupBox("Setup")
        layout = QFormLayout(box)

        self.solver_combo = QComboBox()
        self.solver_combo.addItems([
            "DEMATEL",
            "Fuzzy DEMATEL",
            "Grey DEMATEL",
            "Fuzzy Z-DEMATEL",
        ])
        self.solver_combo.currentTextChanged.connect(self.on_solver_changed)

        self.threshold_combo = QComboBox()
        self.threshold_combo.addItems([
            "Average",
            "First quartile",
            "Median",
            "Third quartile",
            "Maximum Mean De-Entropy",
        ])

        self.expert_count_spin = QSpinBox()
        self.expert_count_spin.setMinimum(1)
        self.expert_count_spin.setMaximum(50)
        self.expert_count_spin.setValue(2)

        self.factor_count_spin = QSpinBox()
        self.factor_count_spin.setMinimum(2)
        self.factor_count_spin.setMaximum(100)
        self.factor_count_spin.setValue(4)

        self.generate_button = QPushButton("Generate Input Forms")
        self.generate_button.clicked.connect(self.generate_input_forms)

        layout.addRow("Solver type", self.solver_combo)
        layout.addRow("Threshold method", self.threshold_combo)
        layout.addRow("Number of experts", self.expert_count_spin)
        layout.addRow("Number of factors", self.factor_count_spin)
        layout.addRow(self.generate_button)

        return box

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

    def _build_dynamic_input_area(self) -> QScrollArea:
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.dynamic_container = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_container)
        self.dynamic_layout.setSpacing(12)

        self.scroll_area.setWidget(self.dynamic_container)
        return self.scroll_area

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

    def generate_input_forms(self) -> None:
        self.clear_dynamic_layout()
        self.previous_solver_text = self.solver_combo.currentText()

        expert_count = self.expert_count_spin.value()
        factor_count = self.factor_count_spin.value()
        default_weight = round(1.0 / expert_count, 2)

        combined_box = QGroupBox("Factors and Experts")
        combined_layout = QHBoxLayout(combined_box)

        factors_box = QGroupBox("Factors")
        factors_layout = QFormLayout(factors_box)

        for i in range(factor_count):
            coded_name = f"F{i + 1}"
            field = QLineEdit(coded_name)
            self.factor_name_inputs.append(field)
            factors_layout.addRow(coded_name, field)

        experts_box = QGroupBox("Experts and Weights")
        experts_layout = QFormLayout(experts_box)

        for i in range(expert_count):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)

            name_input = QLineEdit(f"Expert {i + 1}")
            weight_input = QDoubleSpinBox()
            weight_input.setRange(0.0, 1.0)
            weight_input.setSingleStep(0.05)
            weight_input.setDecimals(2)
            weight_input.setValue(default_weight)

            self.expert_name_inputs.append(name_input)
            self.expert_weight_inputs.append(weight_input)

            row_layout.addWidget(name_input)
            row_layout.addWidget(QLabel("Weight"))
            row_layout.addWidget(weight_input)

            experts_layout.addRow(f"Expert {i + 1}", row_widget)

        combined_layout.addWidget(factors_box, 1)
        combined_layout.addWidget(experts_box, 1)

        self.dynamic_layout.addWidget(combined_box)

        self.create_matrix_button = QPushButton("Next: Create Matrix Editor")
        self.create_matrix_button.clicked.connect(self.show_matrix_editor)
        self.dynamic_layout.addWidget(self.create_matrix_button)

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

        self.matrix_editor_box = QGroupBox("Matrix Input")
        box_layout = QVBoxLayout(self.matrix_editor_box)

        note = QLabel(
            'Diagonal cells are fixed to "No influence" because a factor cannot directly influence itself.'
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #444; font-style: italic;")
        box_layout.addWidget(note)

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

        self.run_button = QPushButton("Run Analysis")
        self.run_button.clicked.connect(self.run_analysis_from_ui)
        box_layout.addWidget(self.run_button)

        self.dynamic_layout.addWidget(self.matrix_editor_box)

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
            self.show_results()
        except Exception as exc:
            QMessageBox.critical(self, "Analysis Error", str(exc))

    def show_results(self) -> None:
        if self.current_result is None:
            return

        if self.results_box is not None:
            self.results_box.deleteLater()

        from .results_viewer_widget import ResultsViewerWidget

        self.results_box = QGroupBox("Results")
        results_layout = QVBoxLayout(self.results_box)

        viewer = ResultsViewerWidget(self.current_result)
        results_layout.addWidget(viewer)

        self.dynamic_layout.addWidget(self.results_box)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())