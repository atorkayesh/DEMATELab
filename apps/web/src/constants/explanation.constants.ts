import type { Provider } from "@/interfaces/explanation.interface";

/**
 * Default model per provider (the Qt results viewer's table, also the API's `DEFAULT_MODELS`). The
 * API does not publish it, so the field is prefilled from here; a blank model uses the API's default.
 */
export const DEFAULT_MODELS: Record<Provider, string> = {
  Gemini: "gemini-2.5-pro",
  OpenAI: "gpt-4o-mini",
  "Azure OpenAI": "gpt-4o-mini",
  OpenRouter: "openai/gpt-4o-mini",
  Groq: "llama-3.3-70b-versatile",
};

export const AZURE_PROVIDER: Provider = "Azure OpenAI";

export const EXPLANATION_TEXT = {
  TITLE: "AI-Assisted Interpretation",
  NOTE: "This section provides an AI-assisted interpretation of the DEMATEL results. Upon configuring the model and supplying an API key, a structured explanation is generated, outlining the key cause–effect relationships, factor roles, and overall system dynamics.",
  ENGINE: "Engine",
  API_KEY: "API Key",
  MODEL: "Model",
  MODEL_PLACEHOLDER: "Leave blank to use the default model",
  AZURE_MODEL_PLACEHOLDER: "Enter the Azure deployment name",
  GENERATE: "Generate Explanation",
  OUTPUT_LABEL: "Explanation",
} as const;

/** Status line under the button (Qt's texts). */
export const EXPLANATION_STATUS = {
  MISSING_KEY: "Please enter an API key.",
  MISSING_ENDPOINT: "Azure OpenAI endpoint is required.",
  PENDING: "Generating explanation...",
  DONE: "Done",
  ERROR: "Error",
} as const;

/** Qt's "Azure OpenAI Endpoint" dialog. */
export const AZURE_DIALOG_TEXT = {
  TITLE: "Azure OpenAI Endpoint",
  PROMPT: "Enter your Azure OpenAI endpoint, for example:",
  EXAMPLE: "https://YOUR-RESOURCE-NAME.openai.azure.com",
  PLACEHOLDER: "https://YOUR-RESOURCE-NAME.openai.azure.com",
  OK: "OK",
  CANCEL: "Cancel",
} as const;
