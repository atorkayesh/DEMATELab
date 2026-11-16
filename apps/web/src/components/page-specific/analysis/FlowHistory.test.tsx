import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  createMemoryHistory,
  createRootRoute,
  createRoute,
  createRouter,
  RouterProvider,
} from "@tanstack/react-router";
import { act, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { FlowShell } from "@/components/page-specific/analysis/FlowShell";
import { flowSearchSchema } from "@/interfaces/analysis.interface";
import { getScales } from "@/services/scales.service";
import { useAnalysisStore } from "@/store/analysis.store";
import { SCALES, STANDARD_SCALE } from "@/test/fixtures";

vi.mock("@/services/scales.service", () => ({ getScales: vi.fn() }));
vi.mock("@/services/weights.service", () => ({
  getDefaultWeights: vi.fn(),
  normalizeWeights: vi.fn(),
}));

const store = () => useAnalysisStore.getState();

/** The `/` route with a real router on a memory history, as in the app. */
function renderFlow(step: string) {
  const rootRoute = createRootRoute();
  const indexRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/",
    validateSearch: flowSearchSchema,
    component: FlowShell,
  });
  const history = createMemoryHistory({ initialEntries: [`/?step=${step}`] });
  const router = createRouter({
    routeTree: rootRoute.addChildren([indexRoute]),
    history,
  });
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
  return history;
}

const heading = () => screen.findByRole("heading", { level: 1 });

describe("flow history", () => {
  beforeEach(() => {
    store().reset();
    vi.mocked(getScales).mockResolvedValue(SCALES);
  });

  it("moves between steps with browser Back and Forward", async () => {
    store().setSolver("dematel", STANDARD_SCALE);
    store().markAnswered("solver");
    const history = renderFlow("solver");
    const solverTitle = (await heading()).textContent;

    act(() => screen.getByRole("button", { name: "OK" }).click());
    await waitFor(async () =>
      expect((await heading()).textContent).not.toBe(solverTitle),
    );
    const thresholdTitle = (await heading()).textContent;
    expect(history.location.search).toBe("?step=threshold");

    act(() => history.back());
    await waitFor(async () =>
      expect((await heading()).textContent).toBe(solverTitle),
    );
    expect(history.location.search).toBe("?step=solver");

    act(() => history.forward());
    await waitFor(async () =>
      expect((await heading()).textContent).toBe(thresholdTitle),
    );
    expect(history.location.search).toBe("?step=threshold");
  });
});
