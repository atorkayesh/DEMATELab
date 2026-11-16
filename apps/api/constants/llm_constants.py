"""
AI explanation providers and request settings (`llm_explanation_service.py`, `results_viewer_widget.py:51,1245`).

Keys are supplied per request by the user and never stored.
"""

from enum import Enum
from typing import Dict, Tuple


class LlmProvider(str, Enum):
    """Supported AI providers, in alphabetical order (the order the web app lists them)."""

    ANTHROPIC = "Anthropic"
    AZURE_OPENAI = "Azure OpenAI"
    GEMINI = "Gemini"
    GROQ = "Groq"
    OPENAI = "OpenAI"
    OPENROUTER = "OpenRouter"


# Model catalogue per provider, newest and strongest first (3-7 generally available text chat models,
# checked 2026-11-16). The API validates requested models against it. Azure OpenAI is not listed: its
# "model" is the user's own deployment name, free text with no default.
PROVIDER_MODELS: Dict[LlmProvider, Tuple[str, ...]] = {
    # Source: https://aistudio.google.com/docs/models (formerly ai.google.dev/gemini-api/docs/models)
    LlmProvider.GEMINI: (
        "gemini-4-carbon",
        "gemini-4-argon",
        "gemini-4-hydrogen",
        "gemini-3.8-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    ),
    # Source: https://developers.openai.com/api/docs/models (formerly platform.openai.com/docs/models)
    LlmProvider.OPENAI: ("gpt-6-astra", "gpt-6.1-sol", "gpt-6.1-terra", "gpt-6-luna"),
    # Source: https://openrouter.ai/api/v1/models (vendor/model slugs, prices per token)
    LlmProvider.OPENROUTER: (
        "anthropic/claude-sonnet-5.5",
        "openai/gpt-6.1-sol",
        "google/gemini-4-carbon",
        "x-ai/grok-4.7",
        "qwen/qwen4-max",
        "deepseek/deepseek-v4.1-flash",
        "openai/gpt-6-luna",
    ),
    # Source: https://console.groq.com/docs/models (production models only, previews excluded)
    LlmProvider.GROQ: ("openai/gpt-oss-120b", "llama-3.3-70b-versatile", "openai/gpt-oss-20b", "llama-3.1-8b-instant"),
    # Source: model IDs supplied by the project owner (Anthropic Messages API)
    LlmProvider.ANTHROPIC: ("claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5-2"),
}

# Default (cheap) model per listed provider, used when the model field is blank; always in PROVIDER_MODELS.
DEFAULT_MODELS: Dict[LlmProvider, str] = {
    LlmProvider.GEMINI: "gemini-3.5-flash-lite",
    LlmProvider.OPENAI: "gpt-6-luna",
    LlmProvider.OPENROUTER: "openai/gpt-6-luna",
    LlmProvider.GROQ: "openai/gpt-oss-20b",
    LlmProvider.ANTHROPIC: "claude-haiku-5-5",
}

# Providers whose model field is free text (not validated against the catalogue).
FREE_TEXT_MODEL_PROVIDERS: Tuple[LlmProvider, ...] = (LlmProvider.AZURE_OPENAI,)

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

# Anthropic Messages API (https://docs.anthropic.com/en/api/messages).
ANTHROPIC_SETTINGS = {
    "URL": "https://api.anthropic.com/v1/messages",
    "VERSION": "2023-06-01",
    "MAX_TOKENS": 4096,
}

# Accepted Azure OpenAI endpoint hosts: user-supplied endpoints must be https on one of these suffixes (SSRF guard).
AZURE_ENDPOINT_SCHEME = "https"
AZURE_ENDPOINT_PORT = 443
AZURE_ENDPOINT_HOST_SUFFIXES: Tuple[str, ...] = (
    ".openai.azure.com",
    ".cognitiveservices.azure.com",
    ".services.ai.azure.com",
)
