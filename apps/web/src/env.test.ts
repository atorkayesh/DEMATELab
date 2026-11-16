import { describe, expect, it } from "vitest";
import { parseEnv } from "@/env";

describe("parseEnv", () => {
  it("accepts an API origin and strips trailing slashes", () => {
    const env = parseEnv({
      VITE_APP_ENV: "production",
      VITE_API_BASE_URL: "http://localhost:50001/",
    });

    expect(env).toEqual({
      VITE_APP_ENV: "production",
      VITE_API_BASE_URL: "http://localhost:50001",
    });
  });

  it("accepts an empty API origin for same-origin requests", () => {
    expect(parseEnv({ VITE_API_BASE_URL: "" }).VITE_API_BASE_URL).toBe("");
  });

  it("applies defaults when values are missing", () => {
    expect(parseEnv({})).toEqual({
      VITE_APP_ENV: "development",
      VITE_API_BASE_URL: "",
    });
  });

  it("rejects invalid values and names the offending keys", () => {
    expect(() =>
      parseEnv({ VITE_APP_ENV: "staging", VITE_API_BASE_URL: "not a url" }),
    ).toThrow(/VITE_APP_ENV[\s\S]*VITE_API_BASE_URL/);
  });
});
