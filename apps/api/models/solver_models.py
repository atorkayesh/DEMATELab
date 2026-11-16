"""
Internal solver models (numpy arrays); never returned directly.

`SolverOutput` is what every engine returns. For crisp results the `raw_*` vectors are `None`; for fuzzy and
grey results they hold the triangular (`n x 3`) or interval (`n x 2`) values.
"""

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from constants.solver_constants import SolverType, ThresholdMethod


@dataclass(frozen=True)
class SolverExpert:
    """One expert's numeric matrix and weight."""

    name: str
    weight: float
    matrix: np.ndarray


@dataclass(frozen=True)
class SolverOutput:
    """Everything an engine computes for one analysis."""

    solver_type: SolverType
    factors: List[str]
    expert_weights: List[float]
    direct_matrix: np.ndarray
    normalized_matrix: np.ndarray
    total_matrix: np.ndarray
    r: np.ndarray
    c: np.ndarray
    prominence: np.ndarray
    relation: np.ndarray
    cause_group: List[str]
    effect_group: List[str]
    threshold_method: ThresholdMethod
    threshold_value: float
    crisp_total_matrix: np.ndarray
    raw_r: Optional[np.ndarray] = None
    raw_c: Optional[np.ndarray] = None
    raw_prominence: Optional[np.ndarray] = None
    raw_relation: Optional[np.ndarray] = None


@dataclass(frozen=True)
class ClusterOutput:
    """Cluster labels of the off-diagonal cells (diagonal: -1 / "No influence")."""

    labels_numeric: np.ndarray
    labels_named: np.ndarray
