import { API_ENDPOINTS } from "@/constants/api.constants";
import {
  type ExplanationData,
  type ExplanationProvider,
  type ExplanationRequest,
  explanationProvidersResponseSchema,
  explanationResponseSchema,
} from "@/interfaces/explanation.interface";
import { apiData, jsonPost } from "@/utils/api.utils";

/** Ask the API for an AI explanation. The key is only in this request's body. */
export function explain(request: ExplanationRequest): Promise<ExplanationData> {
  return apiData(
    API_ENDPOINTS.EXPLANATIONS,
    jsonPost(request),
    explanationResponseSchema,
  );
}

/** AI providers with their models and cheap default model. */
export async function getExplanationProviders(): Promise<
  ExplanationProvider[]
> {
  const data = await apiData(
    API_ENDPOINTS.EXPLANATION_PROVIDERS,
    { headers: { Accept: "application/json" } },
    explanationProvidersResponseSchema,
  );
  return data.providers;
}
