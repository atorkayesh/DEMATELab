import { z } from "zod";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import { apiResponseSchema } from "@/interfaces/api.interface";

/** AI providers, in the Qt combo box order (the API's `LlmProvider` values). */
export const PROVIDERS = [
  "Gemini",
  "OpenAI",
  "Azure OpenAI",
  "OpenRouter",
  "Groq",
] as const;

export type Provider = (typeof PROVIDERS)[number];

/** Body of `POST /explanations`. Built only inside the request; never stored or cached. */
export interface ExplanationRequest {
  analysis: AnalysisRequest;
  provider: Provider;
  api_key: string;
  model?: string | null;
  azure_endpoint?: string | null;
}

export const explanationDataSchema = z.object({
  text: z.string(),
  provider: z.string(),
  model: z.string(),
});

export const explanationResponseSchema = apiResponseSchema(
  explanationDataSchema,
);

export type ExplanationData = z.infer<typeof explanationDataSchema>;
