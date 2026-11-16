"""Explanation router: `POST /explanations` (AI explanation with a per-request provider key)."""

from fastapi import APIRouter
from starlette.responses import Response

from features.explanation_feature import explanation_feature
from models.explanation_models import ExplanationData, ExplanationRequest
from models.response_model import ApiResponseModel
from utils.response_utils import response_builder

router = APIRouter(prefix="/explanations", tags=["explanations"])


@router.post("", response_model=ApiResponseModel[ExplanationData])
async def explain(body: ExplanationRequest) -> Response:
    """
    Explain an analysis with Gemini, OpenAI, Azure OpenAI, OpenRouter or Groq. The key is used once.

    Returns:
        Response: ApiResponseModel[ExplanationData]; 422 missing key/endpoint, 502/504 provider failures
    """
    return response_builder.ok(await explanation_feature.explain(body), "Explanation generated")
