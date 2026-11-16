import { z } from "zod";

export const envSchema = z.object({
  VITE_APP_ENV: z.enum(["development", "production"]).default("development"),
  // Origin of the API, e.g. http://localhost:50001. Empty means same origin
  // (production, where Nginx serves the web app and /api/ together).
  VITE_API_BASE_URL: z.union([z.literal(""), z.url()]).default(""),
});

export type Env = z.infer<typeof envSchema>;

export function parseEnv(raw: Record<string, unknown>): Env {
  const result = envSchema.safeParse(raw);
  if (!result.success) {
    const keys = result.error.issues.map((issue) => String(issue.path[0]));
    const error = new Error(`Invalid values in .env:\n${keys.join("\n")}`);
    error.stack = "";
    throw error;
  }
  return {
    ...result.data,
    VITE_API_BASE_URL: result.data.VITE_API_BASE_URL.replace(/\/+$/, ""),
  };
}

const env = parseEnv({
  VITE_APP_ENV: import.meta.env.VITE_APP_ENV,
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
});

export default env;
