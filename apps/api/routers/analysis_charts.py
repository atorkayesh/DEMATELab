"""Chart router: causal diagram and heatmaps as PNG (`dpi` 100 on screen, 300 for downloads)."""

from typing import Annotated

from fastapi import APIRouter, Query
from starlette.responses import Response

from constants.chart_constants import DISPLAY_DPI, PNG_MEDIA_TYPE, ChartDpi
from features.causal_diagram_chart_feature import causal_diagram_chart_feature
from features.heatmap_chart_feature import HeatmapMode, heatmap_chart_feature
from models.analysis_request_models import AnalysisRequest
from utils.response_utils import response_builder

router = APIRouter(prefix="/analysis/charts", tags=["charts"])

PNG_RESPONSES = {200: {"content": {PNG_MEDIA_TYPE: {}}}}


@router.post("/causal-diagram", response_class=Response, responses=PNG_RESPONSES)
async def causal_diagram(body: AnalysisRequest, dpi: Annotated[ChartDpi, Query()] = DISPLAY_DPI) -> Response:
    """
    Render the causal diagram (influence map).

    Returns:
        Response: `image/png`
    """
    return response_builder.image(await causal_diagram_chart_feature.render(body, int(dpi)), PNG_MEDIA_TYPE)


@router.post("/heatmap", response_class=Response, responses=PNG_RESPONSES)
async def heatmap(
    body: AnalysisRequest,
    mode: Annotated[HeatmapMode, Query()] = HeatmapMode.STANDARD,
    dpi: Annotated[ChartDpi, Query()] = DISPLAY_DPI,
) -> Response:
    """
    Render the standard or cluster heatmap; 422 in cluster mode when clustering fails.

    Returns:
        Response: `image/png`
    """
    return response_builder.image(await heatmap_chart_feature.render(body, mode, int(dpi)), PNG_MEDIA_TYPE)
