"""
AI explanation providers and request settings (`llm_explanation_service.py`, `results_viewer_widget.py:51,1245`).

Keys are supplied per request by the user and never stored.
"""

from enum import Enum
from typing import Dict, Tuple


class LlmProvider(str, Enum):
    """Supported AI providers, in the Qt combo box order."""

    GEMINI = "Gemini"
    OPENAI = "OpenAI"
    AZURE_OPENAI = "Azure OpenAI"
    OPENROUTER = "OpenRouter"
    GROQ = "Groq"


# Default model per provider when the model field is blank (the results viewer's table).
DEFAULT_MODELS: Dict[LlmProvider, str] = {
    LlmProvider.GEMINI: "gemini-2.5-pro",
    LlmProvider.OPENAI: "gpt-4o-mini",
    LlmProvider.AZURE_OPENAI: "gpt-4o-mini",
    LlmProvider.OPENROUTER: "openai/gpt-4o-mini",
    LlmProvider.GROQ: "llama-3.3-70b-versatile",
}

# Chat completion URLs of the OpenAI-compatible providers.
OPENAI_COMPATIBLE_URLS: Dict[LlmProvider, str] = {
    LlmProvider.GROQ: "https://api.groq.com/openai/v1/chat/completions",
    LlmProvider.OPENROUTER: "https://openrouter.ai/api/v1/chat/completions",
    LlmProvider.OPENAI: "https://api.openai.com/v1/chat/completions",
}

OPENROUTER_HEADERS: Dict[str, str] = {
    "HTTP-Referer": "http://localhost",
    "X-Title": "DEMATELab",
}

LLM_SETTINGS = {
    "SYSTEM_MESSAGE": "You are an expert academic analyst interpreting DEMATEL results.",
    "TEMPERATURE": 0.4,
    "TIMEOUT_SECONDS": 120.0,
    "AZURE_API_VERSION": "2024-06-01",
    "AZURE_V1_SUFFIX": "/openai/v1",
}

# Accepted Azure OpenAI endpoint hosts: user-supplied endpoints must be https on one of these suffixes (SSRF guard).
AZURE_ENDPOINT_SCHEME = "https"
AZURE_ENDPOINT_PORT = 443
AZURE_ENDPOINT_HOST_SUFFIXES: Tuple[str, ...] = (
    ".openai.azure.com",
    ".cognitiveservices.azure.com",
    ".services.ai.azure.com",
)
