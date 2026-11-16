import { z } from "zod";

/** Zod schema for the backend `ApiResponseModel` wrapper around `data`. */
export function apiResponseSchema<T extends z.ZodType>(data: T) {
  return z.object({
    success: z.boolean(),
    message: z.string().nullish(),
    data: data.nullish(),
    metadata: z.record(z.string(), z.unknown()).nullish(),
  });
}

/** One invalid request field of a 422 validation error. */
export const fieldErrorSchema = z.object({
  field: z.string(),
  message: z.string(),
});

/** Body of a non-OK response: the API's `message` and its `error` block (`code`, `fields`). */
export const apiErrorBodySchema = z.object({
  message: z.string().nullish(),
  error: z
    .union([
      z.object({
        code: z.string(),
        fields: z.array(fieldErrorSchema).nullish(),
      }),
      z.string(),
    ])
    .nullish(),
});
