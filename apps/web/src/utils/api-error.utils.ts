import { apiErrorBodySchema } from "@/interfaces/api.interface";

/** Pydantic prefixes messages raised by validators; the text after it is the Qt message. */
const VALUE_ERROR_PREFIX = /^Value error, /;

/**
 * Message of a non-OK API response. A 422 validation error carries the useful text in its first
 * field (e.g. "Factor names must be unique."); otherwise the API's public `message`, else the status.
 */
export async function readErrorMessage(response: Response): Promise<string> {
  const fallback = `Request failed (${response.status})`;
  try {
    const body = apiErrorBodySchema.parse(await response.json());
    if (typeof body.error === "string") return body.message || body.error;
    const field = body.error?.fields?.[0];
    if (field) return field.message.replace(VALUE_ERROR_PREFIX, "");
    return body.message || fallback;
  } catch {
    return fallback;
  }
}
