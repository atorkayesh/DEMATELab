import { afterEach, describe, expect, it, vi } from "vitest";
import { getExplanationProviders } from "@/services/explanation.service";
import { EXPLANATION_PROVIDERS } from "@/test/fixtures";

function mockFetch(body: unknown) {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("getExplanationProviders", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("loads the providers from the API's catalogue endpoint", async () => {
    const fetchMock = mockFetch({
      success: true,
      message: "Providers loaded",
      data: { providers: EXPLANATION_PROVIDERS },
      metadata: null,
    });
    await expect(getExplanationProviders()).resolves.toEqual(
      EXPLANATION_PROVIDERS,
    );
    expect(String(fetchMock.mock.calls[0][0])).toMatch(
      /\/api\/v1\/explanations\/providers$/,
    );
  });

  it("rejects a response that does not match the schema", async () => {
    mockFetch({
      success: true,
      message: "ok",
      data: { providers: [{ id: "Gemini" }] },
      metadata: null,
    });
    await expect(getExplanationProviders()).rejects.toThrow();
  });
});
