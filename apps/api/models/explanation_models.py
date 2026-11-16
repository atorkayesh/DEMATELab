"""AI explanation request and response models. The API key is never stored, logged, or echoed."""

from typing import List, Optional

from pydantic import BaseModel, Field, SecretStr

from constants.llm_constants import LlmProvider
from models.analysis_request_models import AnalysisRequest


class ExplanationRequest(BaseModel):
    """The analysis to explain and the user's provider settings."""

    analysis: AnalysisRequest
    provider: LlmProvider
    api_key: SecretStr = Field(default=SecretStr(""), repr=False, description="Provider key; used once, never stored")
    model: Optional[str] = Field(default=None, description="Blank uses the default model; Azure needs a deployment")
    azure_endpoint: Optional[str] = Field(default=None, description="Required for Azure OpenAI")


class ExplanationData(BaseModel):
    """The generated explanation."""

    text: str
    provider: LlmProvider
    model: str


class ExplanationProvider(BaseModel):
    """One AI provider and its model catalogue."""

    id: LlmProvider = Field(description="Value to send as `provider`")
    label: str
    models: List[str] = Field(description="Selectable models, newest and strongest first; empty for free text")
    default_model: Optional[str] = Field(description="Cheap default used when the model is blank; none for Azure")
    free_text_model: bool = Field(description="True when the model is a free-text deployment name (Azure OpenAI)")


class ExplanationProvidersData(BaseModel):
    """Every AI provider, in display order."""

    providers: List[ExplanationProvider]
