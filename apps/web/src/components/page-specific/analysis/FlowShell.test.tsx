import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { FlowShell } from "@/components/page-specific/analysis/FlowShell";
import { getScales } from "@/services/scales.service";
import { getDefaultWeights } from "@/services/weights.service";
import { useAnalysisStore } from "@/store/analysis.store";
import { SCALES, STANDARD_SCALE } from "@/test/fixtures";
import { renderWithQuery } from "@/test/render";
import { questionSteps } from "@/utils/flow.utils";

const router = vi.hoisted(() => ({
  search: {} as { step?: string },
  navigate: vi.fn(),
}));

vi.mock("@tanstack/react-router", () => ({
  useSearch: () => router.search,
  useNavigate: () => router.navigate,
  Navigate: ({ search }: { search: { step: string } }) => (
    <p>redirect:{search.step}</p>
  ),
}));
vi.mock("@/services/scales.service", () => ({ getScales: vi.fn() }));
vi.mock("@/services/weights.service", () => ({
  getDefaultWeights: vi.fn(),
  normalizeWeights: vi.fn(),
}));

const store = () => useAnalysisStore.getState();

function openStep(step: string) {
  router.search = { step };
  return renderWithQuery(<FlowShell />);
}

describe("FlowShell", () => {
  beforeEach(() => {
    store().reset();
    router.navigate.mockReset();
    vi.mocked(getScales).mockResolvedValue(SCALES);
  });

  it("redirects without a step to the first question", async () => {
    openStep("");
    expect(await screen.findByText("redirect:solver")).toBeDefined();
  });

  it("redirects to the first unanswered step when earlier steps are missing", async () => {
    store().markAnswered("solver");
    openStep("factors");
    expect(await screen.findByText("redirect:threshold")).toBeDefined();
  });

  it("selects by letter and continues with Enter", async () => {
    openStep("solver");
    const group = await screen.findByRole("radiogroup", {
      name: "Solver type",
    });
    fireEvent.keyDown(group, { key: "c" });
    const checked = screen.getByRole("radio", { checked: true });
    fireEvent.keyDown(checked, { key: "Enter" });

    expect(store().solver).toBe("grey_dematel");
    expect(store().answered).toEqual(["solver"]);
    expect(router.navigate).toHaveBeenCalledWith({
      search: { step: "threshold" },
    });
  });

  it("goes back with Shift+Enter and with the Back button", async () => {
    store().setSolver("dematel", STANDARD_SCALE);
    store().markAnswered("solver");
    openStep("threshold");
    const radio = await screen.findByRole("radio", { name: /Average/ });
    fireEvent.keyDown(radio, { key: "Enter", shiftKey: true });
    expect(router.navigate).toHaveBeenLastCalledWith({
      search: { step: "solver" },
    });
    expect(store().threshold).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Back" }));
    expect(router.navigate).toHaveBeenCalledTimes(2);
  });

  it("opens an answered step from the step list", async () => {
    store().markAnswered("solver");
    openStep("threshold");
    fireEvent.click(await screen.findByRole("button", { name: /Solver/ }));
    expect(router.navigate).toHaveBeenCalledWith({
      search: { step: "solver" },
    });
    expect(
      screen.getByRole("button", { name: /Factors$/ }).hasAttribute("disabled"),
    ).toBe(true);
  });

  it("fetches default weights for the expert count, then continues", async () => {
    vi.mocked(getDefaultWeights).mockResolvedValue([0.334, 0.333, 0.333]);
    store().setSolver("dematel", STANDARD_SCALE);
    store().markAnswered("solver");
    store().markAnswered("threshold");
    openStep("experts");
    const input = await screen.findByRole("textbox", {
      name: "Number of experts",
    });
    fireEvent.change(input, { target: { value: "3" } });
    fireEvent.click(screen.getByRole("button", { name: "OK" }));

    await waitFor(() => expect(store().expertCount).toBe(3));
    expect(getDefaultWeights).toHaveBeenCalledWith(3, expect.anything());
    expect(store().experts.map((expert) => expert.weight)).toEqual([
      0.334, 0.333, 0.333,
    ]);
    expect(router.navigate).toHaveBeenCalledWith({
      search: { step: "factors" },
    });
  });

  it("focuses the selected choice, not the first one", async () => {
    store().setSolver("dematel", STANDARD_SCALE);
    store().setThreshold("mmde");
    store().markAnswered("solver");
    openStep("threshold");
    const selected = await screen.findByRole("radio", {
      name: "Maximum Mean De-Entropy",
    });
    expect(document.activeElement).toBe(selected);
  });

  it("focuses Run on the review step", async () => {
    store().setSolver("dematel", STANDARD_SCALE);
    store().setThreshold("average");
    store().setExpertCount(1, [1]);
    store().setFactorCount(2);
    for (const step of questionSteps(1).slice(0, -1))
      store().markAnswered(step);
    openStep("review");
    const run = await screen.findByRole("button", { name: "Run Analysis" });
    expect(document.activeElement).toBe(run);
  });

  it("shows an error with a retry when the scales cannot load", async () => {
    vi.mocked(getScales).mockRejectedValue(new Error("down"));
    openStep("solver");
    expect(
      await screen.findByText(
        "The analysis options could not be loaded from the API.",
      ),
    ).toBeDefined();
  });
});
