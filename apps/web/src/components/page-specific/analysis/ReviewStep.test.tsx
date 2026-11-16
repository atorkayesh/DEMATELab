import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ReviewStep } from "@/components/page-specific/analysis/ReviewStep";
import { runAnalysis } from "@/services/analysis.service";
import { useAnalysisStore } from "@/store/analysis.store";
import { ANALYSIS_DATA, SCALES, STANDARD_SCALE } from "@/test/fixtures";
import { renderWithQuery } from "@/test/render";
import { ApiError } from "@/utils/api.utils";

vi.mock("@/services/analysis.service", () => ({ runAnalysis: vi.fn() }));

const store = () => useAnalysisStore.getState();

function renderReview() {
  const props = {
    number: 9,
    onAdvance: vi.fn(),
    onBack: vi.fn(),
    onOpen: vi.fn(),
  };
  renderWithQuery(<ReviewStep scales={SCALES} {...props} />);
  return props;
}

describe("ReviewStep", () => {
  beforeEach(() => {
    store().reset();
    store().setSolver("dematel", STANDARD_SCALE);
    store().setThreshold("mmde");
    store().setExpertCount(1, [1]);
    store().setFactorCount(2);
    store().setCell(0, 0, 1, "High influence");
    vi.mocked(runAnalysis).mockReset();
  });

  it("lists every answer with an Edit link to its step", () => {
    const props = renderReview();

    expect(screen.getByText("Maximum Mean De-Entropy")).toBeDefined();
    expect(screen.getByText("Expert 1 (1.000)")).toBeDefined();
    expect(screen.getByText("F1, F2")).toBeDefined();
    expect(screen.getByText("1 edited cell")).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "Edit Factors" }));
    expect(props.onOpen).toHaveBeenCalledWith("factor-names");
    fireEvent.click(
      screen.getByRole("button", { name: "Edit Matrices: Expert 1" }),
    );
    expect(props.onOpen).toHaveBeenCalledWith("matrix-1");
  });

  it("runs the analysis, stores the results with the request, and continues", async () => {
    vi.mocked(runAnalysis).mockResolvedValue(ANALYSIS_DATA);
    const props = renderReview();

    fireEvent.click(screen.getByRole("button", { name: "Run Analysis" }));

    await waitFor(() => expect(props.onAdvance).toHaveBeenCalledOnce());
    const request = vi.mocked(runAnalysis).mock.calls[0][0];
    expect(request.threshold_method).toBe("mmde");
    expect(request.experts[0].matrix[0][1]).toBe("High influence");
    expect(store().snapshot).toEqual(request);
    expect(store().results).toEqual(ANALYSIS_DATA);
  });

  it("shows analysis errors inline", async () => {
    vi.mocked(runAnalysis).mockRejectedValue(
      new ApiError("Factor names must be unique.", 422),
    );
    const props = renderReview();

    fireEvent.click(screen.getByRole("button", { name: "Run Analysis" }));

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Factor names must be unique.",
    );
    expect(props.onAdvance).not.toHaveBeenCalled();
  });

  it("checks names again before running", () => {
    store().setFactorName(1, "F1");
    renderReview();
    fireEvent.click(screen.getByRole("button", { name: "Run Analysis" }));
    expect(screen.getByRole("alert").textContent).toBe(
      "Factor names must be unique.",
    );
    expect(runAnalysis).not.toHaveBeenCalled();
  });
});
