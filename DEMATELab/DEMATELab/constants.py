# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 23:01:05 2026

@author: Ali
"""

from __future__ import annotations

from enum import Enum


class LinguisticScale(str, Enum):
    NO_INFLUENCE = "No influence"
    LOW_INFLUENCE = "Low influence"
    MEDIUM_INFLUENCE = "Medium influence"
    HIGH_INFLUENCE = "High influence"
    EXTREME_INFLUENCE = "Extreme influence"


DEFAULT_LINGUISTIC_MAP: dict[str, float] = {
    LinguisticScale.NO_INFLUENCE.value: 0.0,
    LinguisticScale.LOW_INFLUENCE.value: 1.0,
    LinguisticScale.MEDIUM_INFLUENCE.value: 2.0,
    LinguisticScale.HIGH_INFLUENCE.value: 3.0,
    LinguisticScale.EXTREME_INFLUENCE.value: 4.0,
}


DEFAULT_FUZZY_LINGUISTIC_MAP: dict[str, tuple[float, float, float]] = {
    LinguisticScale.NO_INFLUENCE.value: (0.0, 0.0, 0.25),
    LinguisticScale.LOW_INFLUENCE.value: (0.0, 0.25, 0.5),
    LinguisticScale.MEDIUM_INFLUENCE.value: (0.25, 0.5, 0.75),
    LinguisticScale.HIGH_INFLUENCE.value: (0.5, 0.75, 1.0),
    LinguisticScale.EXTREME_INFLUENCE.value: (0.75, 1.0, 1.0),
}

DEFAULT_GREY_LINGUISTIC_MAP: dict[str, tuple[float, float]] = {
    LinguisticScale.NO_INFLUENCE.value: (0.0, 0.0),
    LinguisticScale.LOW_INFLUENCE.value: (0.0, 0.25),
    LinguisticScale.MEDIUM_INFLUENCE.value: (0.25, 0.5),
    LinguisticScale.HIGH_INFLUENCE.value: (0.5, 0.75),
    LinguisticScale.EXTREME_INFLUENCE.value: (0.75, 1.0),
}

class ThresholdMethod(str, Enum):
    AVERAGE = "average"
    FIRST_QUARTILE = "first_quartile"
    MEDIAN = "median"
    THIRD_QUARTILE = "Third_quartile"
    MMDE = "mmde"


class ClusteringMethod(str, Enum):
    KMEANS = "kmeans"
    HIERARCHICAL = "hierarchical"


CLUSTER_NAMES = ["Low", "Low2Medium", "Medium2High", "High"]


LLM_MODEL = "gemini-2.5-pro"

LINGUISTIC_TERMS = list(DEFAULT_LINGUISTIC_MAP.keys())

NO_INFLUENCE_LABEL = LinguisticScale.NO_INFLUENCE.value

# -----------------------------
# Fuzzy Z-DEMATEL
# -----------------------------

Z_INFLUENCE_TERMS = [
    "No influence",
    "Low influence",
    "Medium influence",
    "High influence",
    "Very high influence",
]

Z_RELIABILITY_TERMS = [
    "VL reliability",
    "L reliability",
    "M reliability",
    "H reliability",
    "VH reliability",
]


def _make_z_label(influence: str, reliability: str) -> str:
    return f"{influence} with {reliability}"


DEFAULT_Z_LINGUISTIC_MAP: dict[str, tuple[float, float, float]] = {
    # Reliability = VL
    _make_z_label("No influence", "VL reliability"): (0.0, 0.0, 0.316),
    _make_z_label("Low influence", "VL reliability"): (0.0, 0.316, 0.632),
    _make_z_label("Medium influence", "VL reliability"): (0.316, 0.632, 0.949),
    _make_z_label("High influence", "VL reliability"): (0.632, 0.949, 1.265),
    _make_z_label("Very high influence", "VL reliability"): (0.949, 1.265, 1.265),

    # Reliability = L
    _make_z_label("No influence", "L reliability"): (0.0, 0.0, 0.548),
    _make_z_label("Low influence", "L reliability"): (0.0, 0.548, 1.096),
    _make_z_label("Medium influence", "L reliability"): (0.548, 1.096, 1.644),
    _make_z_label("High influence", "L reliability"): (1.096, 1.644, 2.192),
    _make_z_label("Very high influence", "L reliability"): (1.644, 2.192, 2.192),

    # Reliability = M
    _make_z_label("No influence", "M reliability"): (0.0, 0.0, 0.707),
    _make_z_label("Low influence", "M reliability"): (0.0, 0.707, 1.414),
    _make_z_label("Medium influence", "M reliability"): (0.707, 1.414, 2.121),
    _make_z_label("High influence", "M reliability"): (1.414, 2.121, 2.828),
    _make_z_label("Very high influence", "M reliability"): (2.121, 2.828, 2.828),

    # Reliability = H
    _make_z_label("No influence", "H reliability"): (0.0, 0.0, 0.837),
    _make_z_label("Low influence", "H reliability"): (0.0, 0.837, 1.673),
    _make_z_label("Medium influence", "H reliability"): (0.837, 1.673, 2.510),
    _make_z_label("High influence", "H reliability"): (1.673, 2.510, 3.347),
    _make_z_label("Very high influence", "H reliability"): (2.510, 3.347, 3.347),

    # Reliability = VH
    _make_z_label("No influence", "VH reliability"): (0.0, 0.0, 0.949),
    _make_z_label("Low influence", "VH reliability"): (0.0, 0.949, 1.897),
    _make_z_label("Medium influence", "VH reliability"): (0.949, 1.897, 2.846),
    _make_z_label("High influence", "VH reliability"): (1.897, 2.846, 3.795),
    _make_z_label("Very high influence", "VH reliability"): (2.846, 3.795, 3.795),
}


Z_LINGUISTIC_TERMS = list(DEFAULT_Z_LINGUISTIC_MAP.keys())

Z_NO_INFLUENCE_DEFAULT = _make_z_label("No influence", "VH reliability")