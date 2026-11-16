"""
AI explanation: validates the provider settings, recomputes the analysis, builds the prompt, and calls the
provider (`llm_explanation_service.generate_dematel_explanation`, `results_viewer_widget.py:1339-1368`).
"""

import asyncio
from typing import Optional
from urllib.parse import urlsplit

from constants.llm_constants import (
    AZURE_ENDPOINT_HOST_SUFFIXES,
    AZURE_ENDPOINT_PORT,
    AZURE_ENDPOINT_SCHEME,
    DEFAULT_MODELS,
    FREE_TEXT_MODEL_PROVIDERS,
    OPENAI_COMPATIBLE_URLS,
    OPENROUTER_HEADERS,
    PROVIDER_MODELS,
    LlmProvider,
)
from errors.llm_errors import (
    InvalidAzureEndpointError,
    MissingApiKeyError,
    MissingAzureDeploymentError,
    MissingAzureEndpointError,
    UnsupportedModelError,
)
from features.analysis_feature import AnalysisFeature, analysis_feature
from features.explanation_prompt_feature import ExplanationPromptFeature, explanation_prompt_feature
from models.explanation_models import ExplanationData, ExplanationRequest
from services.gemini_service import GeminiService, gemini_service
from services.llm_provider_service import LlmProviderService, llm_provider_service


class ExplanationFeature:
    """Generates the AI explanation of an analysis."""

    def __init__(
        self,
        analysis: Optional[AnalysisFeature] = None,
        prompt: Optional[ExplanationPromptFeature] = None,
        providers: Optional[LlmProviderService] = None,
        gemini: Optional[GeminiService] = None,
    ):
        """
        Create the feature.

        Args:
            analysis: Analysis feature; defaults to the shared instance
            prompt: Prompt builder; defaults to the shared instance
            providers: OpenAI-compatible, Azure and Anthropic calls; defaults to the shared instance
            gemini: Gemini calls; defaults to the shared instance
        """
        self._analysis = analysis or analysis_feature
        self._prompt = prompt or explanation_prompt_feature
        self._providers = providers or llm_provider_service
        self._gemini = gemini or gemini_service

    async def explain(self, request: ExplanationRequest) -> ExplanationData:
        """
        Generate the explanation.

        Args:
            request: Analysis plus provider settings

        Returns:
            ExplanationData: Text, provider, and the model used

        Raises:
            MissingApiKeyError: When the key is blank
            MissingAzureEndpointError: When Azure OpenAI has no endpoint
            InvalidAzureEndpointError: When the Azure endpoint is not https on an Azure OpenAI host
            MissingAzureDeploymentError: When Azure OpenAI has no deployment name
            UnsupportedModelError: When the model is not in the provider's list (Azure takes any deployment)
        """
        api_key = request.api_key.get_secret_value().strip()
        if not api_key:
            raise MissingApiKeyError()
        provider = request.provider
        endpoint = (request.azure_endpoint or "").strip()
        if provider == LlmProvider.AZURE_OPENAI and not endpoint:
            raise MissingAzureEndpointError()
        if provider == LlmProvider.AZURE_OPENAI:
            self._check_azure_endpoint(endpoint)
        model = (request.model or "").strip()
        if provider in FREE_TEXT_MODEL_PROVIDERS and not model:
            raise MissingAzureDeploymentError()
        model = model or DEFAULT_MODELS[provider]
        if provider not in FREE_TEXT_MODEL_PROVIDERS and model not in PROVIDER_MODELS[provider]:
            raise UnsupportedModelError(f"Model {model!r} is not listed for {provider.value}")
        output = await asyncio.to_thread(self._analysis.solve, request.analysis)
        prompt = self._prompt.build_prompt(self._prompt.build_payload(output))
        if provider == LlmProvider.GEMINI:
            text = await self._gemini.generate(api_key, model, prompt)
        elif provider == LlmProvider.ANTHROPIC:
            text = await self._providers.anthropic(api_key, model, prompt)
        elif provider == LlmProvider.AZURE_OPENAI:
            text = await self._providers.azure(endpoint, api_key, model, prompt)
        else:
            headers = OPENROUTER_HEADERS if provider == LlmProvider.OPENROUTER else None
            text = await self._providers.openai_compatible(
                OPENAI_COMPATIBLE_URLS[provider], api_key, model, prompt, headers
            )
        return ExplanationData(text=text, provider=provider, model=model)

    def _check_azure_endpoint(self, endpoint: str) -> None:
        """
        Reject endpoints that are not https on an Azure OpenAI host (the server must not call arbitrary URLs).

        Args:
            endpoint: Trimmed user-supplied endpoint

        Raises:
            InvalidAzureEndpointError: When the scheme, host, credentials or port are not allowed
        """
        try:
            parts = urlsplit(endpoint)
            port = parts.port
        except ValueError as exc:
            raise InvalidAzureEndpointError(f"Unparsable Azure endpoint: {type(exc).__name__}") from exc
        host = (parts.hostname or "").lower()
        valid = (
            parts.scheme.lower() == AZURE_ENDPOINT_SCHEME
            and "@" not in parts.netloc
            and port in (None, AZURE_ENDPOINT_PORT)
            and any(host.endswith(suffix) and len(host) > len(suffix) for suffix in AZURE_ENDPOINT_HOST_SUFFIXES)
        )
        if not valid:
            raise InvalidAzureEndpointError(f"Rejected Azure endpoint host {host!r}")


explanation_feature = ExplanationFeature()
