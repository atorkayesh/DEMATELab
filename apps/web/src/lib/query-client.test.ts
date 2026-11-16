import { describe, expect, it } from "vitest";
import { createQueryClient } from "@/lib/query-client";

describe("createQueryClient", () => {
  it("caches for 5 minutes and never retries mutations", () => {
    const client = createQueryClient();

    expect(client.getDefaultOptions().queries?.staleTime).toBe(300_000);
    expect(client.getDefaultOptions().mutations?.retry).toBe(false);
  });
});
