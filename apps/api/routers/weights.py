"""Weights router: `/weights/defaults` and `/weights/normalize` (the GUI's weight rules)."""

from fastapi import APIRouter
from starlette.responses import Response

from features.weight_normalization_feature import weight_normalization_feature
from models.response_model import ApiResponseModel
from models.weight_models import WeightDefaultsRequest, WeightNormalizeRequest, WeightsData
from utils.response_utils import response_builder

router = APIRouter(prefix="/weights", tags=["weights"])


@router.post("/defaults", response_model=ApiResponseModel[WeightsData])
async def default_weights(body: WeightDefaultsRequest) -> Response:
    """
    Equal default weights in thousandths, the remainder to the first experts.

    Returns:
        Response: ApiResponseModel[WeightsData]
    """
    return response_builder.ok(
        WeightsData(weights=weight_normalization_feature.default_weights(body.expert_count)), "Default weights"
    )


@router.post("/normalize", response_model=ApiResponseModel[WeightsData])
async def normalize_weights(body: WeightNormalizeRequest) -> Response:
    """
    Correct weights within ±0.005 of 1; 422 "Expert weights must sum to 1." otherwise.

    Returns:
        Response: ApiResponseModel[WeightsData]
    """
    return response_builder.ok(
        WeightsData(weights=weight_normalization_feature.normalize(body.weights)), "Weights corrected"
    )
