import { afterEach, describe, expect, it, vi } from "vitest";
import { getHealth } from "@/services/health.service";

const healthyBody = {
  success: true,
  message: "System is healthy",
  data: {
    status: "healthy",
    services: { api: { status: "up", response_time_ms: null, error: null } },
  },
  metadata: { timestamp: "2026-10-26T12:00:00Z" },
};

const unhealthyBody = {
  success: false,
  message: "System is unhealthy",
  data: {
    status: "unhealthy",
    services: {
      api: {
        status: "down",
        response_time_ms: null,
        error: "The API is down",
      },
    },
  },
  metadata: null,
};

function mockFetch(status: number, body: unknown) {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    }),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("getHealth", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls the health endpoint and returns the data", async () => {
    const fetchMock = mockFetch(200, healthyBody);

    const health = await getHealth();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:50001/api/v1/health",
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );
    expect(health.status).toBe("healthy");
    expect(health.services.api.status).toBe("up");
  });

  it("returns unhealthy data for a 503 instead of throwing", async () => {
    mockFetch(503, unhealthyBody);

    const health = await getHealth();

    expect(health.status).toBe("unhealthy");
    expect(health.services.api.error).toBe("The API is down");
  });

  it("throws for other error statuses", async () => {
    mockFetch(500, { detail: "boom" });

    await expect(getHealth()).rejects.toThrow("status 500");
  });

  it("throws when the response does not match the schema", async () => {
    mockFetch(200, { success: true, data: { status: "unknown" } });

    await expect(getHealth()).rejects.toThrow();
  });

  it("propagates network errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("fail")));

    await expect(getHealth()).rejects.toThrow("fail");
  });
});
