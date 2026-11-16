"""Scales router: `/scales` (linguistic terms, options, limits)."""

from fastapi import APIRouter
from starlette.responses import Response

from features.scales_feature import scales_feature
from models.response_model import ApiResponseModel
from models.scale_models import ScalesData
from utils.response_utils import response_builder

router = APIRouter(prefix="/scales", tags=["scales"])


@router.get("", response_model=ApiResponseModel[ScalesData])
async def get_scales() -> Response:
    """
    Linguistic scales per solver family, solver and threshold options, limits and weight rules.

    Returns:
        Response: ApiResponseModel[ScalesData]
    """
    return response_builder.ok(scales_feature.get_scales(), "Scales loaded")
