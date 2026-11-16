"""
Linguistic label → numeric matrix conversion for every solver.

Ported from the Qt converters (`dematel_core.py:43`, `fuzzy_dematel_core.py:46`, `grey_dematel_core.py:46`,
`fuzzy_z_dematel_core.py:17`): cells are trimmed and looked up case-sensitively. Unknown labels name the
expert, the row and column factors, and the label.
"""

from typing import Dict, List, Sequence, Tuple, Union

import numpy as np

from constants.linguistic_constants import (
    DEFAULT_FUZZY_LINGUISTIC_MAP,
    DEFAULT_GREY_LINGUISTIC_MAP,
    DEFAULT_LINGUISTIC_MAP,
    DEFAULT_Z_LINGUISTIC_MAP,
    NO_INFLUENCE_LABEL,
    Z_NO_INFLUENCE_DEFAULT,
)
from constants.solver_constants import SolverType
from errors.analysis_errors import InvalidAnalysisInputError, UnknownLinguisticTermError

ScaleValue = Union[float, Tuple[float, ...]]

# Scale and cell shape (components per cell; 0 = scalar) per solver.
_SCALES: Dict[SolverType, Tuple[Dict[str, ScaleValue], int]] = {
    SolverType.DEMATEL: (DEFAULT_LINGUISTIC_MAP, 0),
    SolverType.FUZZY_DEMATEL: (DEFAULT_FUZZY_LINGUISTIC_MAP, 3),
    SolverType.GREY_DEMATEL: (DEFAULT_GREY_LINGUISTIC_MAP, 2),
    SolverType.FUZZY_Z_DEMATEL: (DEFAULT_Z_LINGUISTIC_MAP, 3),
}


class LinguisticConversionFeature:
    """Converts linguistic matrices into the numeric form each solver needs."""

    def diagonal_label(self, solver_type: SolverType) -> str:
        """
        Return the label the GUI forces onto the diagonal for a solver.

        Args:
            solver_type: Solver

        Returns:
            str: `No influence`, or `No influence with VH reliability` for fuzzy Z-DEMATEL
        """
        return Z_NO_INFLUENCE_DEFAULT if solver_type == SolverType.FUZZY_Z_DEMATEL else NO_INFLUENCE_LABEL

    def force_diagonal(self, matrix: Sequence[Sequence[str]], solver_type: SolverType) -> List[List[str]]:
        """
        Copy a matrix with its diagonal set to the solver's no-influence label (the GUI editor's rule).

        Args:
            matrix: Linguistic matrix
            solver_type: Solver

        Returns:
            List[List[str]]: New matrix
        """
        label = self.diagonal_label(solver_type)
        return [[label if i == j else cell for j, cell in enumerate(row)] for i, row in enumerate(matrix)]

    def convert(
        self, solver_type: SolverType, matrix: Sequence[Sequence[str]], expert_name: str, factors: Sequence[str]
    ) -> np.ndarray:
        """
        Convert one expert's linguistic matrix.

        Args:
            solver_type: Solver whose scale applies
            matrix: `n x n` labels
            expert_name: Expert (for error messages)
            factors: Factor names (for error messages and the expected size)

        Returns:
            np.ndarray: `n x n` (crisp), `n x n x 3` (fuzzy, fuzzy Z) or `n x n x 2` (grey) floats

        Raises:
            UnknownLinguisticTermError: When a cell is not on the solver's scale
            InvalidAnalysisInputError: When the matrix is not `n x n`
        """
        scale, components = _SCALES[solver_type]
        size = len(factors)
        if len(matrix) != size or any(len(row) != size for row in matrix):
            raise InvalidAnalysisInputError(
                public_message=f"Matrix for expert '{expert_name}' must have shape ({size}, {size})."
            )
        rows = []
        for i, row in enumerate(matrix):
            values = []
            for j, cell in enumerate(row):
                label = str(cell).strip()
                if label not in scale:
                    raise UnknownLinguisticTermError(
                        public_message=self._unknown_message(label, expert_name, factors[i], factors[j], scale)
                    )
                values.append(scale[label])
            rows.append(values)
        numeric = np.array(rows, dtype=float)
        expected = (size, size, components) if components else (size, size)
        if numeric.shape != expected:
            raise InvalidAnalysisInputError(public_message=f"Linguistic matrix must have shape {expected}.")
        return numeric

    def _unknown_message(self, label: str, expert: str, row: str, column: str, scale: Dict[str, ScaleValue]) -> str:
        """
        Build the public message for an unknown label.

        Args:
            label: Trimmed cell value
            expert: Expert name
            row: Row (influencing) factor
            column: Column (influenced) factor
            scale: Scale that was searched

        Returns:
            str: Message naming the cell and listing the allowed values
        """
        allowed = ", ".join(scale)
        return (
            f"Unknown linguistic value {label!r} for expert '{expert}' (row '{row}', column '{column}'). "
            f"Allowed values are: {allowed}."
        )


linguistic_conversion_feature = LinguisticConversionFeature()
