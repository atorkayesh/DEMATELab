import type { z } from "zod";
import { API_V1_PREFIX } from "@/constants/api.constants";
import env from "@/env";
import { readErrorMessage } from "@/utils/api-error.utils";

/** Build a full API v1 URL, e.g. `/health` → `http://localhost:50001/api/v1/health`. */
export function buildApiUrl(
  path: string,
  baseUrl: string = env.VITE_API_BASE_URL,
): string {
  return `${baseUrl}${API_V1_PREFIX}${path}`;
}

/** A non-OK API response; `message` is the API's public message (safe to show). */
export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** Call the API: `path` is below `/api/v1` and may carry a query string. No cookies: the API is public. */
export function apiFetch(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  return fetch(buildApiUrl(path), init);
}

/** `init` for a JSON POST body. */
export function jsonPost(body: unknown): RequestInit {
  return {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  };
}

/** Throw `ApiError` with the API's message when the response is not OK. */
export async function ensureOk(response: Response): Promise<Response> {
  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status);
  }
  return response;
}

/**
 * Call a JSON endpoint and return its validated `data`.
 *
 * `schema` is the `apiResponseSchema(...)` of the endpoint; a missing `data` is an error.
 */
export async function apiData<T>(
  path: string,
  init: RequestInit,
  schema: z.ZodType<{ data?: T | null }>,
): Promise<T> {
  const response = await ensureOk(await apiFetch(path, init));
  const body = schema.parse(await response.json());
  if (body.data == null) {
    throw new ApiError("The API response has no data", response.status);
  }
  return body.data;
}

/** Call a binary endpoint (XLSX, PNG) and return the file. */
export async function apiBlob(path: string, init: RequestInit): Promise<Blob> {
  const response = await ensureOk(await apiFetch(path, init));
  return response.blob();
}

/** Message of any error for display: the API's message, or the error's own. */
export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
