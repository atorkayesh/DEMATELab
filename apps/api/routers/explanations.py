"""Explanation router: `GET /explanations/providers` (model catalogue) and `POST /explanations` (per-request key)."""

from fastapi import APIRouter
from starlette.responses import Response

from features.explanation_feature import explanation_feature
from features.explanation_providers_feature import explanation_providers_feature
from models.explanation_models import ExplanationData, ExplanationProvidersData, ExplanationRequest
from models.response_model import ApiResponseModel
from utils.response_utils import response_builder

router = APIRouter(prefix="/explanations", tags=["explanations"])


@router.get("/providers", response_model=ApiResponseModel[ExplanationProvidersData])
async def list_providers() -> Response:
    """
    AI providers with their models and cheap default model (the API's single model catalogue).

    Returns:
        Response: ApiResponseModel[ExplanationProvidersData]
    """
    return response_builder.ok(explanation_providers_feature.list_providers(), "Providers loaded")


@router.post("", response_model=ApiResponseModel[ExplanationData])
async def explain(body: ExplanationRequest) -> Response:
    """
    Explain an analysis with Gemini, OpenAI, Azure OpenAI, OpenRouter, Groq or Anthropic. The key is used once.

    Returns:
        Response: ApiResponseModel[ExplanationData]; 422 missing key/endpoint or unlisted model,
        502/504 provider failures
    """
    return response_builder.ok(await explanation_feature.explain(body), "Explanation generated")
