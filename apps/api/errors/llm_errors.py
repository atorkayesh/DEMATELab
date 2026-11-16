"""AI explanation errors. Public messages never contain the API key or the provider's raw response."""

from http import HTTPStatus

from errors.app_error import AppError


class MissingApiKeyError(AppError):
    """No API key was supplied."""

    code = "missing_api_key"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "Please enter an API key."


class MissingAzureEndpointError(AppError):
    """Azure OpenAI needs an endpoint."""

    code = "missing_azure_endpoint"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "Azure OpenAI endpoint is required."


class InvalidAzureEndpointError(AppError):
    """The Azure OpenAI endpoint is not an https URL on an Azure OpenAI host."""

    code = "invalid_azure_endpoint"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "Enter a valid Azure OpenAI endpoint, for example https://YOUR-RESOURCE-NAME.openai.azure.com."


class LlmAuthError(AppError):
    """The provider rejected the key (401/403)."""

    code = "llm_auth_failed"
    status_code = HTTPStatus.BAD_GATEWAY
    public_message = "The AI provider rejected the API key."


class LlmRateLimitError(AppError):
    """The provider rate limit was reached (429)."""

    code = "llm_rate_limited"
    status_code = HTTPStatus.BAD_GATEWAY
    public_message = "The AI provider rate limit was reached. Try again later."


class LlmTimeoutError(AppError):
    """The provider did not answer in time."""

    code = "llm_timeout"
    status_code = HTTPStatus.GATEWAY_TIMEOUT
    public_message = "The AI provider did not answer in time."


class LlmProviderError(AppError):
    """Any other provider failure (HTTP error, unreachable, unexpected response)."""

    code = "llm_provider_error"
    status_code = HTTPStatus.BAD_GATEWAY
    public_message = "The AI provider could not be reached."
