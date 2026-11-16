import { API_ENDPOINTS } from "@/constants/api.constants";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import {
  type AnalysisData,
  analysisResponseSchema,
} from "@/interfaces/result.interface";
import { apiData, jsonPost } from "@/utils/api.utils";

/** Run the analysis: result, summary numbers and the corrected weights. */
export function runAnalysis(request: AnalysisRequest): Promise<AnalysisData> {
  return apiData(
    API_ENDPOINTS.ANALYSIS,
    jsonPost(request),
    analysisResponseSchema,
  );
}
