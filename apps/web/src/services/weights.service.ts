import { API_ENDPOINTS } from "@/constants/api.constants";
import { weightsResponseSchema } from "@/interfaces/analysis.interface";
import { apiData, jsonPost } from "@/utils/api.utils";

/** Equal default weights in thousandths for `expertCount` experts. */
export async function getDefaultWeights(
  expertCount: number,
): Promise<number[]> {
  const data = await apiData(
    API_ENDPOINTS.WEIGHTS_DEFAULTS,
    jsonPost({ expert_count: expertCount }),
    weightsResponseSchema,
  );
  return data.weights;
}

/** Weights corrected to sum to 1; rejects with "Expert weights must sum to 1." when too far off. */
export async function normalizeWeights(weights: number[]): Promise<number[]> {
  const data = await apiData(
    API_ENDPOINTS.WEIGHTS_NORMALIZE,
    jsonPost({ weights }),
    weightsResponseSchema,
  );
  return data.weights;
}
