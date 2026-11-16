"""Results summary models (the numbers of the Qt summary tab, `results_viewer_widget.py:439-789`)."""

from typing import List

from pydantic import BaseModel

from constants.solver_constants import ThresholdMethod


class ProminenceRankingItem(BaseModel):
    """One row of the prominence ranking."""

    factor: str
    prominence: float
    relation: float
    bar_ratio: float


class ResultSummary(BaseModel):
    """Summary numbers; rounding is left to the client."""

    result_type_label: str
    threshold_method_key: ThresholdMethod
    threshold_method_label: str
    threshold_value: float
    driving_factor_count: int
    dependent_factor_count: int
    top_prominence: float
    strongest_relation: float
    prominence_ranking: List[ProminenceRankingItem]
