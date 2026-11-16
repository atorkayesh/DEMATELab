"""AI explanation request and response models. The API key is never stored, logged, or echoed."""

from typing import Optional

from pydantic import BaseModel, Field, SecretStr

from constants.llm_constants import LlmProvider
from models.analysis_request_models import AnalysisRequest


class ExplanationRequest(BaseModel):
    """The analysis to explain and the user's provider settings."""

    analysis: AnalysisRequest
    provider: LlmProvider
    api_key: SecretStr = Field(default=SecretStr(""), repr=False, description="Provider key; used once, never stored")
    model: Optional[str] = Field(default=None, description="Blank uses the provider's default model")
    azure_endpoint: Optional[str] = Field(default=None, description="Required for Azure OpenAI")


class ExplanationData(BaseModel):
    """The generated explanation."""

    text: str
    provider: LlmProvider
    model: str
