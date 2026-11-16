import { API_ENDPOINTS } from "@/constants/api.constants";
import {
  type HealthCheckData,
  healthResponseSchema,
} from "@/interfaces/health.interface";
import { apiFetch } from "@/utils/api.utils";

/**
 * Fetch the API health check.
 *
 * A 503 still returns health data, so it resolves instead of throwing. Network errors and other
 * statuses throw.
 */
export async function getHealth(): Promise<HealthCheckData> {
  const response = await apiFetch(API_ENDPOINTS.HEALTH, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok && response.status !== 503) {
    throw new Error(`Health check failed with status ${response.status}`);
  }

  const body = healthResponseSchema.parse(await response.json());
  if (!body.data) {
    throw new Error("Health check response has no data");
  }
  return body.data;
}
