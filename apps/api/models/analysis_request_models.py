"""
Analysis request models.

`AnalysisRequest` is the body of every analysis-derived endpoint (analysis, export, charts, explanation).
Validation matches the Qt GUI (`gui_app.py:1922-1946`): factor names trimmed, required and unique
(case-sensitive); expert names trimmed and required (duplicates allowed); 2-100 factors and 1-50 experts.
Solver and threshold aliases follow `analysis_service.py:46-84`.
"""

from enum import Enum
from typing import Any, Dict, List, Type

from pydantic import BaseModel, Field, field_validator, model_validator

from constants.solver_constants import INPUT_LIMITS, SOLVER_ALIASES, THRESHOLD_ALIASES, SolverType, ThresholdMethod


def _normalize_choice(value: Any, aliases: Dict[str, Enum], enum_type: Type[Enum], label: str) -> Any:
    """
    Map a spelling variant to its enum value, as `analysis_service._normalize_*` does.

    Kept as a module function because both request validators share it and it is not a model method.

    Args:
        value: Submitted value
        aliases: Normalised spelling → enum member
        enum_type: Enum the value must belong to
        label: Name used in the error message (`solver type`, `threshold method`)

    Returns:
        Any: The enum member, or the value unchanged when it is not a string (Pydantic then rejects it)

    Raises:
        ValueError: When the spelling is unknown
    """
    if isinstance(value, enum_type) or not isinstance(value, str):
        return value
    normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized not in aliases:
        raise ValueError(f"Unsupported {label}: {value}")
    return aliases[normalized]


class ExpertRequest(BaseModel):
    """One expert: name, weight, and linguistic matrix (row = influencing factor)."""

    name: str = Field(description="Expert name; trimmed, required, duplicates allowed")
    weight: float = Field(ge=0, le=1, description="Weight between 0 and 1; all weights must sum to 1 (±0.005)")
    matrix: List[List[str]] = Field(description="n x n linguistic labels; the diagonal is forced to no influence")

    @field_validator("name")
    @classmethod
    def _require_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("All expert names must be filled.")
        return name


class AnalysisRequest(BaseModel):
    """Everything needed to run (or re-run) one analysis."""

    solver_type: SolverType = Field(description="dematel, fuzzy_dematel, grey_dematel or fuzzy_z_dematel (aliases ok)")
    threshold_method: ThresholdMethod = Field(
        description="average, first_quartile, median, third_quartile or mmde (aliases ok)"
    )
    factors: List[str] = Field(min_length=INPUT_LIMITS["FACTORS_MIN"], max_length=INPUT_LIMITS["FACTORS_MAX"])
    experts: List[ExpertRequest] = Field(min_length=INPUT_LIMITS["EXPERTS_MIN"], max_length=INPUT_LIMITS["EXPERTS_MAX"])

    @field_validator("solver_type", mode="before")
    @classmethod
    def _normalize_solver(cls, value: Any) -> Any:
        return _normalize_choice(value, SOLVER_ALIASES, SolverType, "solver type")

    @field_validator("threshold_method", mode="before")
    @classmethod
    def _normalize_threshold(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            raise ValueError("Please select a threshold method before running the analysis.")
        return _normalize_choice(value, THRESHOLD_ALIASES, ThresholdMethod, "threshold method")

    @field_validator("factors")
    @classmethod
    def _check_factors(cls, value: List[str]) -> List[str]:
        names = [name.strip() for name in value]
        if any(not name for name in names):
            raise ValueError("All factor names must be filled.")
        if len(set(names)) != len(names):
            raise ValueError("Factor names must be unique.")
        return names

    @model_validator(mode="after")
    def _check_matrix_shapes(self) -> "AnalysisRequest":
        size = len(self.factors)
        for expert in self.experts:
            if len(expert.matrix) != size or any(len(row) != size for row in expert.matrix):
                raise ValueError(f"Matrix for expert '{expert.name}' must have shape ({size}, {size}).")
        return self
