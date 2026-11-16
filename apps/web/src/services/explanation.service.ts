import { API_ENDPOINTS } from "@/constants/api.constants";
import {
  type ExplanationData,
  type ExplanationRequest,
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
