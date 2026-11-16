"""AI provider catalogue for the web app: providers, their models, and the cheap default model."""

from constants.llm_constants import DEFAULT_MODELS, FREE_TEXT_MODEL_PROVIDERS, PROVIDER_MODELS, LlmProvider
from models.explanation_models import ExplanationProvider, ExplanationProvidersData


class ExplanationProvidersFeature:
    """Publishes the model catalogue the explanation request is validated against."""

    def list_providers(self) -> ExplanationProvidersData:
        """
        Return every provider with its models.

        Returns:
            ExplanationProvidersData: Providers in display order
        """
        return ExplanationProvidersData(
            providers=[
                ExplanationProvider(
                    id=provider,
                    label=provider.value,
                    models=list(PROVIDER_MODELS.get(provider, ())),
                    default_model=DEFAULT_MODELS.get(provider),
                    free_text_model=provider in FREE_TEXT_MODEL_PROVIDERS,
                )
                for provider in LlmProvider
            ]
        )


explanation_providers_feature = ExplanationProvidersFeature()
