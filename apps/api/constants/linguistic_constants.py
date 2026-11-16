"""
Linguistic scales, copied verbatim from the Qt app (`qt-app/DEMATELab/DEMATELab/constants.py:13-132`).

Labels are case-sensitive after trimming. Never change a value without regenerating the parity fixtures
from `qt-app/` (see AGENTS.md, Numerical parity).
"""

from enum import Enum
from typing import Dict, List, Tuple


class LinguisticScale(str, Enum):
    """Terms of the standard scale (DEMATEL, fuzzy DEMATEL, grey DEMATEL)."""

    NO_INFLUENCE = "No influence"
    LOW_INFLUENCE = "Low influence"
    MEDIUM_INFLUENCE = "Medium influence"
    HIGH_INFLUENCE = "High influence"
    EXTREME_INFLUENCE = "Extreme influence"


DEFAULT_LINGUISTIC_MAP: Dict[str, float] = {
    LinguisticScale.NO_INFLUENCE.value: 0.0,
    LinguisticScale.LOW_INFLUENCE.value: 1.0,
    LinguisticScale.MEDIUM_INFLUENCE.value: 2.0,
    LinguisticScale.HIGH_INFLUENCE.value: 3.0,
    LinguisticScale.EXTREME_INFLUENCE.value: 4.0,
}

DEFAULT_FUZZY_LINGUISTIC_MAP: Dict[str, Tuple[float, float, float]] = {
    LinguisticScale.NO_INFLUENCE.value: (0.0, 0.0, 0.25),
    LinguisticScale.LOW_INFLUENCE.value: (0.0, 0.25, 0.5),
    LinguisticScale.MEDIUM_INFLUENCE.value: (0.25, 0.5, 0.75),
    LinguisticScale.HIGH_INFLUENCE.value: (0.5, 0.75, 1.0),
    LinguisticScale.EXTREME_INFLUENCE.value: (0.75, 1.0, 1.0),
}

DEFAULT_GREY_LINGUISTIC_MAP: Dict[str, Tuple[float, float]] = {
    LinguisticScale.NO_INFLUENCE.value: (0.0, 0.0),
    LinguisticScale.LOW_INFLUENCE.value: (0.0, 0.25),
    LinguisticScale.MEDIUM_INFLUENCE.value: (0.25, 0.5),
    LinguisticScale.HIGH_INFLUENCE.value: (0.5, 0.75),
    LinguisticScale.EXTREME_INFLUENCE.value: (0.75, 1.0),
}

LINGUISTIC_TERMS: List[str] = list(DEFAULT_LINGUISTIC_MAP.keys())

NO_INFLUENCE_LABEL = LinguisticScale.NO_INFLUENCE.value

Z_INFLUENCE_TERMS: List[str] = [
    "No influence",
    "Low influence",
    "Medium influence",
    "High influence",
    "Very high influence",
]

Z_RELIABILITY_TERMS: List[str] = [
    "VL reliability",
    "L reliability",
    "M reliability",
    "H reliability",
    "VH reliability",
]

Z_LABEL_TEMPLATE = "{influence} with {reliability}"

DEFAULT_Z_LINGUISTIC_MAP: Dict[str, Tuple[float, float, float]] = {
    # Reliability = VL
    "No influence with VL reliability": (0.0, 0.0, 0.316),
    "Low influence with VL reliability": (0.0, 0.316, 0.632),
    "Medium influence with VL reliability": (0.316, 0.632, 0.949),
    "High influence with VL reliability": (0.632, 0.949, 1.265),
    "Very high influence with VL reliability": (0.949, 1.265, 1.265),
    # Reliability = L
    "No influence with L reliability": (0.0, 0.0, 0.548),
    "Low influence with L reliability": (0.0, 0.548, 1.096),
    "Medium influence with L reliability": (0.548, 1.096, 1.644),
    "High influence with L reliability": (1.096, 1.644, 2.192),
    "Very high influence with L reliability": (1.644, 2.192, 2.192),
    # Reliability = M
    "No influence with M reliability": (0.0, 0.0, 0.707),
    "Low influence with M reliability": (0.0, 0.707, 1.414),
    "Medium influence with M reliability": (0.707, 1.414, 2.121),
    "High influence with M reliability": (1.414, 2.121, 2.828),
    "Very high influence with M reliability": (2.121, 2.828, 2.828),
    # Reliability = H
    "No influence with H reliability": (0.0, 0.0, 0.837),
    "Low influence with H reliability": (0.0, 0.837, 1.673),
    "Medium influence with H reliability": (0.837, 1.673, 2.510),
    "High influence with H reliability": (1.673, 2.510, 3.347),
    "Very high influence with H reliability": (2.510, 3.347, 3.347),
    # Reliability = VH
    "No influence with VH reliability": (0.0, 0.0, 0.949),
    "Low influence with VH reliability": (0.0, 0.949, 1.897),
    "Medium influence with VH reliability": (0.949, 1.897, 2.846),
    "High influence with VH reliability": (1.897, 2.846, 3.795),
    "Very high influence with VH reliability": (2.846, 3.795, 3.795),
}

Z_LINGUISTIC_TERMS: List[str] = list(DEFAULT_Z_LINGUISTIC_MAP.keys())

Z_NO_INFLUENCE_DEFAULT = "No influence with VH reliability"
