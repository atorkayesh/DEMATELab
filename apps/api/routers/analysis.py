"""Analysis router: `POST /analysis` (result, summary, corrected weights)."""

from fastapi import APIRouter
from starlette.responses import Response

from features.analysis_feature import analysis_feature
from models.analysis_request_models import AnalysisRequest
from models.analysis_response_models import AnalysisResponseData
from models.response_model import ApiResponseModel
from utils.response_utils import response_builder

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=ApiResponseModel[AnalysisResponseData])
async def run_analysis(body: AnalysisRequest) -> Response:
    """
    Run DEMATEL, fuzzy, grey, or fuzzy Z-DEMATEL.

    Returns:
        Response: ApiResponseModel[AnalysisResponseData]; 422 for invalid input or a failed analysis
    """
    return response_builder.ok(await analysis_feature.analyze(body), "Analysis completed")
