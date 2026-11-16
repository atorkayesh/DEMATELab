import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiHealthCard } from "@/components/page-specific/status/ApiHealthCard";
import { getHealth } from "@/services/health.service";

vi.mock("@/services/health.service", () => ({ getHealth: vi.fn() }));

function renderCard() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <ApiHealthCard />
    </QueryClientProvider>,
  );
}

function rowState(container: HTMLElement) {
  return container.querySelector("[data-state]")?.getAttribute("data-state");
}

describe("ApiHealthCard", () => {
  afterEach(() => {
    vi.mocked(getHealth).mockReset();
  });

  it("shows the API checking while loading", () => {
    vi.mocked(getHealth).mockReturnValue(new Promise(() => {}));

    const { container } = renderCard();

    expect(screen.getAllByText("Checking…")).toHaveLength(2);
    expect(rowState(container)).toBe("checking");
  });

  it("shows the API operational", async () => {
    vi.mocked(getHealth).mockResolvedValue({
      status: "healthy",
      services: { api: { status: "up" } },
    });

    const { container } = renderCard();

    expect(
      await screen.findByText(/^All systems operational · Last checked /),
    ).toBeDefined();
    expect(rowState(container)).toBe("operational");
  });

  it("shows an outage when the API is unreachable", async () => {
    vi.mocked(getHealth).mockRejectedValue(new Error("network"));

    const { container } = renderCard();

    expect(await screen.findByText("The API is unreachable")).toBeDefined();
    expect(rowState(container)).toBe("outage");
  });
});
