"""Scales endpoint models: linguistic terms, solver and threshold options, limits."""

from typing import List

from pydantic import BaseModel


class Option(BaseModel):
    """A selectable value and its label."""

    key: str
    label: str


class ScaleFamily(BaseModel):
    """Linguistic terms of a solver family; new cells and the diagonal use `default_label`."""

    solvers: List[str]
    terms: List[str]
    default_label: str
    diagonal_label: str
    influence_terms: List[str] = []
    reliability_terms: List[str] = []


class InputLimits(BaseModel):
    """GUI limits for the setup form."""

    factors_min: int
    factors_max: int
    factors_default: int
    experts_min: int
    experts_max: int
    experts_default: int


class WeightRules(BaseModel):
    """How weights are entered and corrected."""

    decimals: int
    step: float
    sum_tolerance: float
    default_rule: str


class ScalesData(BaseModel):
    """Everything the setup form and matrix editor need."""

    standard: ScaleFamily
    fuzzy_z: ScaleFamily
    solvers: List[Option]
    thresholds: List[Option]
    limits: InputLimits
    weights: WeightRules
