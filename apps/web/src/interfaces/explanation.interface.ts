import { z } from "zod";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import { apiResponseSchema } from "@/interfaces/api.interface";

/** One AI provider from `GET /explanations/providers`: the API owns the model catalogue. */
export const explanationProviderSchema = z.object({
  id: z.string(),
  label: z.string(),
  models: z.array(z.string()),
  default_model: z.string().nullable(),
  free_text_model: z.boolean(),
});

export const explanationProvidersDataSchema = z.object({
  providers: z.array(explanationProviderSchema),
});

export const explanationProvidersResponseSchema = apiResponseSchema(
  explanationProvidersDataSchema,
);

export type ExplanationProvider = z.infer<typeof explanationProviderSchema>;

/** Body of `POST /explanations`. Built only inside the request; never stored or cached. */
export interface ExplanationRequest {
  analysis: AnalysisRequest;
  provider: string;
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
