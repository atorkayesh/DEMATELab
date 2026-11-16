"""Weight endpoint models."""

from typing import List

from pydantic import BaseModel, Field

from constants.solver_constants import INPUT_LIMITS


class WeightDefaultsRequest(BaseModel):
    """Number of experts to create default weights for."""

    expert_count: int = Field(ge=INPUT_LIMITS["EXPERTS_MIN"], le=INPUT_LIMITS["EXPERTS_MAX"])


class WeightNormalizeRequest(BaseModel):
    """Weights as entered."""

    weights: List[float] = Field(min_length=INPUT_LIMITS["EXPERTS_MIN"], max_length=INPUT_LIMITS["EXPERTS_MAX"])


class WeightsData(BaseModel):
    """Weights summing to 1, in thousandths."""

    weights: List[float]
