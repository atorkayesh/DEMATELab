"""
Solver types, threshold methods, their aliases and labels, and the GUI input limits.

Aliases and normalisation follow `analysis_service.py:46-84` of the Qt app; labels follow the Qt combo
boxes (`gui_app.py:1611-1620`) and the results viewer (`results_viewer_widget.py:442`).
"""

from enum import Enum
from typing import Dict


class SolverType(str, Enum):
    """Supported solvers."""

    DEMATEL = "dematel"
    FUZZY_DEMATEL = "fuzzy_dematel"
    GREY_DEMATEL = "grey_dematel"
    FUZZY_Z_DEMATEL = "fuzzy_z_dematel"


class ThresholdMethod(str, Enum):
    """Supported threshold methods."""

    AVERAGE = "average"
    FIRST_QUARTILE = "first_quartile"
    MEDIAN = "median"
    THIRD_QUARTILE = "third_quartile"
    MMDE = "mmde"


# Normalised spelling (trimmed, lower case, spaces and hyphens as underscores) → solver.
SOLVER_ALIASES: Dict[str, SolverType] = {
    "dematel": SolverType.DEMATEL,
    "fuzzy_dematel": SolverType.FUZZY_DEMATEL,
    "fuzzydematel": SolverType.FUZZY_DEMATEL,
    "grey_dematel": SolverType.GREY_DEMATEL,
    "greydematel": SolverType.GREY_DEMATEL,
    "fuzzy_z_dematel": SolverType.FUZZY_Z_DEMATEL,
    "fuzzyzdematel": SolverType.FUZZY_Z_DEMATEL,
    "z_dematel": SolverType.FUZZY_Z_DEMATEL,
    "fz_dematel": SolverType.FUZZY_Z_DEMATEL,
}

THRESHOLD_ALIASES: Dict[str, ThresholdMethod] = {
    "average": ThresholdMethod.AVERAGE,
    "first_quartile": ThresholdMethod.FIRST_QUARTILE,
    "median": ThresholdMethod.MEDIAN,
    "third_quartile": ThresholdMethod.THIRD_QUARTILE,
    "mmde": ThresholdMethod.MMDE,
    "maximum_mean_de_entropy": ThresholdMethod.MMDE,
}

SOLVER_LABELS: Dict[SolverType, str] = {
    SolverType.DEMATEL: "DEMATEL",
    SolverType.FUZZY_DEMATEL: "Fuzzy DEMATEL",
    SolverType.GREY_DEMATEL: "Grey DEMATEL",
    SolverType.FUZZY_Z_DEMATEL: "Fuzzy Z-DEMATEL",
}

RESULT_TYPE_LABELS: Dict[SolverType, str] = {
    SolverType.DEMATEL: "Classical DEMATEL",
    SolverType.FUZZY_DEMATEL: "Fuzzy DEMATEL",
    SolverType.GREY_DEMATEL: "Grey DEMATEL",
    SolverType.FUZZY_Z_DEMATEL: "Fuzzy Z-DEMATEL",
}

THRESHOLD_LABELS: Dict[ThresholdMethod, str] = {
    ThresholdMethod.AVERAGE: "Average",
    ThresholdMethod.FIRST_QUARTILE: "First quartile",
    ThresholdMethod.MEDIAN: "Median",
    ThresholdMethod.THIRD_QUARTILE: "Third quartile",
    ThresholdMethod.MMDE: "Maximum Mean De-Entropy",
}

# Limits and defaults of the GUI steppers (`gui_app.py:1622-1623`).
INPUT_LIMITS = {
    "FACTORS_MIN": 2,
    "FACTORS_MAX": 100,
    "FACTORS_DEFAULT": 4,
    "EXPERTS_MIN": 1,
    "EXPERTS_MAX": 50,
    "EXPERTS_DEFAULT": 2,
}
