export const EXPLANATION_TEXT = {
  TITLE: "AI-Assisted Interpretation",
  NOTE: "This section provides an AI-assisted interpretation of the DEMATEL results. Upon configuring the model and supplying an API key, a structured explanation is generated, outlining the key cause–effect relationships, factor roles, and overall system dynamics.",
  PROVIDER: "AI Provider",
  API_KEY: "API Key",
  SHOW_KEY: "Show API key",
  HIDE_KEY: "Hide API key",
  KEY_PRIVACY:
    "Your API key is only sent to the AI provider for this request. It is never saved, stored in a database or logged.",
  MODEL: "Model",
  AZURE_MODEL_PLACEHOLDER: "Your Azure deployment name, e.g. gpt-4o-mini",
  PROVIDERS_ERROR: "The AI providers could not be loaded.",
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

/** Toast shown when generating the explanation fails (the API's message is the description). */
export const EXPLANATION_TOAST = {
  ERROR_TITLE: "Could not generate the explanation",
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
