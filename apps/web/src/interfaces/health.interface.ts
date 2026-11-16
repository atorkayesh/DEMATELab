import { z } from "zod";
import { apiResponseSchema } from "@/interfaces/api.interface";

export const serviceStatusSchema = z.object({
  status: z.enum(["up", "down"]),
  response_time_ms: z.number().nullish(),
  error: z.string().nullish(),
});

export const healthCheckDataSchema = z.object({
  status: z.enum(["healthy", "unhealthy"]),
  services: z.record(z.string(), serviceStatusSchema),
});

export const healthResponseSchema = apiResponseSchema(healthCheckDataSchema);

export type ServiceStatus = z.infer<typeof serviceStatusSchema>;
export type HealthCheckData = z.infer<typeof healthCheckDataSchema>;

/** Display state of the API row and of the system overall. */
export type RowState = "operational" | "outage" | "checking";
