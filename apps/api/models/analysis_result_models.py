"""
Analysis result models, with the Qt result field names.

Crisp results use unprefixed matrices (`n x n`); fuzzy and fuzzy Z results `fuzzy_*` (`n x n x 3`, vectors
`n x 3`); grey results `grey_*` (`n x n x 2`, vectors `n x 2`). Every result carries the crisp `r`, `c`,
`prominence`, `relation` vectors and `crisp_total_matrix` (what charts and clustering use).
"""

from typing import Annotated, List, Literal, Union

from pydantic import BaseModel, Field

from constants.solver_constants import ThresholdMethod

Matrix = List[List[float]]
IntervalMatrix = List[List[List[float]]]


class BaseAnalysisResult(BaseModel):
    """Fields every solver returns."""

    factors: List[str]
    expert_weights: List[float]
    r: List[float]
    c: List[float]
    prominence: List[float]
    relation: List[float]
    cause_group: List[str]
    effect_group: List[str]
    threshold_method: ThresholdMethod
    threshold_value: float
    crisp_total_matrix: Matrix


class CrispAnalysisResult(BaseAnalysisResult):
    """Classical DEMATEL result."""

    solver_type: Literal["dematel"] = "dematel"
    direct_matrix: Matrix
    normalized_matrix: Matrix
    total_matrix: Matrix


class FuzzyAnalysisResult(BaseAnalysisResult):
    """Fuzzy DEMATEL or fuzzy Z-DEMATEL result (triangular numbers l, m, u)."""

    solver_type: Literal["fuzzy_dematel", "fuzzy_z_dematel"]
    fuzzy_direct_matrix: IntervalMatrix
    fuzzy_normalized_matrix: IntervalMatrix
    fuzzy_total_matrix: IntervalMatrix
    fuzzy_r: Matrix
    fuzzy_c: Matrix
    fuzzy_prominence: Matrix
    fuzzy_relation: Matrix


class GreyAnalysisResult(BaseAnalysisResult):
    """Grey DEMATEL result (intervals lower, upper)."""

    solver_type: Literal["grey_dematel"] = "grey_dematel"
    grey_direct_matrix: IntervalMatrix
    grey_normalized_matrix: IntervalMatrix
    grey_total_matrix: IntervalMatrix
    grey_r: Matrix
    grey_c: Matrix
    grey_prominence: Matrix
    grey_relation: Matrix


AnalysisResult = Annotated[
    Union[CrispAnalysisResult, FuzzyAnalysisResult, GreyAnalysisResult], Field(discriminator="solver_type")
]
