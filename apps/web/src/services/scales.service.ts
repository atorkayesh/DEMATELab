import { API_ENDPOINTS } from "@/constants/api.constants";
import {
  type ScalesData,
  scalesResponseSchema,
} from "@/interfaces/scales.interface";
import { apiData } from "@/utils/api.utils";

/** Linguistic scales, solver and threshold options, limits and weight rules. */
export function getScales(): Promise<ScalesData> {
  return apiData(
    API_ENDPOINTS.SCALES,
    { headers: { Accept: "application/json" } },
    scalesResponseSchema,
  );
}
