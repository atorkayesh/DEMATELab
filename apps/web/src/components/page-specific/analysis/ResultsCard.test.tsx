import { fireEvent, screen, waitFor } from "@testing-library/react";
import { toBlob } from "html-to-image";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ResultsCard } from "@/components/page-specific/analysis/ResultsCard";
import { runAnalysis } from "@/services/analysis.service";
import { getChart } from "@/services/charts.service";
import { exportXlsx } from "@/services/export.service";
import { useAnalysisStore } from "@/store/analysis.store";
import { ANALYSIS_DATA, REQUEST, STANDARD_SCALE } from "@/test/fixtures";
import { renderWithQuery } from "@/test/render";
import { ApiError } from "@/utils/api.utils";
import { saveBlob } from "@/utils/download.utils";

vi.mock("@/services/analysis.service", () => ({ runAnalysis: vi.fn() }));
vi.mock("@/services/charts.service", () => ({ getChart: vi.fn() }));
vi.mock("@/services/export.service", () => ({ exportXlsx: vi.fn() }));
vi.mock("@/utils/download.utils", () => ({ saveBlob: vi.fn() }));
vi.mock("html-to-image", () => ({
  toBlob: vi.fn(() => Promise.resolve(new Blob(["png"]))),
}));

const store = () => useAnalysisStore.getState();

/** Inputs that build exactly `REQUEST`, and results for it. */
function answerAndRun() {
  store().setSolver("dematel", STANDARD_SCALE);
  store().setThreshold("average");
  store().setExpertCount(1, [1]);
  store().setFactorCount(2);
  store().renameFactors(["A", "B"]);
  store().setCell(0, 0, 1, "High influence");
  store().setCell(0, 1, 0, "Low influence");
  store().setResults(REQUEST, ANALYSIS_DATA);
}

describe("ResultsCard", () => {
  beforeEach(() => {
    store().reset();
    vi.clearAllMocks();
    URL.createObjectURL = vi.fn(() => "blob:chart");
    URL.revokeObjectURL = vi.fn();
    answerAndRun();
  });

  it("shows the summary first, with Qt's numbers and texts", () => {
    renderWithQuery(<ResultsCard onBack={vi.fn()} />);

    expect(screen.getByText("Summary Insights")).toBeDefined();
    expect(screen.getByText("Classical DEMATEL")).toBeDefined();
    expect(screen.getByText("0.2500")).toBeDefined();
    expect(screen.getByText("+0.50")).toBeDefined();
    expect(screen.getByText("R -0.50")).toBeDefined();
    expect(screen.queryByText(/Your inputs changed/)).toBeNull();
  });

  it("switches tabs to the matrices and R/C scores", async () => {
    renderWithQuery(<ResultsCard onBack={vi.fn()} />);

    fireEvent.click(screen.getByRole("tab", { name: "Total Relation Matrix" }));
    expect(await screen.findByText("0.1235")).toBeDefined();
    fireEvent.click(screen.getByRole("tab", { name: "R/C Scores" }));
    expect(
      await screen.findByRole("columnheader", { name: "R+C" }),
    ).toBeDefined();
  });

  it("prefixes the matrix tabs for fuzzy Z results", () => {
    store().setResults(
      { ...REQUEST, solver_type: "fuzzy_z_dematel" },
      {
        ...ANALYSIS_DATA,
        result: {
          ...ANALYSIS_DATA.result,
          solver_type: "fuzzy_z_dematel",
          fuzzy_direct_matrix: [],
          fuzzy_normalized_matrix: [],
          fuzzy_total_matrix: [],
          fuzzy_r: [],
          fuzzy_c: [],
          fuzzy_prominence: [],
          fuzzy_relation: [],
        },
      },
    );
    renderWithQuery(<ResultsCard onBack={vi.fn()} />);
    expect(
      screen.getByRole("tab", { name: "Fuzzy Z Direct Matrix" }),
    ).toBeDefined();
  });

  it("loads the causal diagram from the API at display resolution", async () => {
    vi.mocked(getChart).mockResolvedValue(new Blob(["png"]));
    renderWithQuery(<ResultsCard onBack={vi.fn()} />);

    fireEvent.click(screen.getByRole("tab", { name: "Causal Diagram" }));

    expect(
      await screen.findByRole("img", { name: "Causal Diagram" }),
    ).toBeDefined();
    expect(getChart).toHaveBeenCalledWith(
      REQUEST,
      "causal-diagram",
      "standard",
      100,
    );
  });

  it("unticks the cluster heatmap and shows the API's message when clustering fails", async () => {
    vi.mocked(getChart).mockImplementation((_request, _kind, mode) =>
      mode === "cluster"
        ? Promise.reject(
            new ApiError(
              "Could not generate cluster heatmap: too few values",
              422,
            ),
          )
        : Promise.resolve(new Blob(["png"])),
    );
    renderWithQuery(<ResultsCard onBack={vi.fn()} />);
    fireEvent.click(screen.getByRole("tab", { name: "Heatmap" }));
    const checkbox = await screen.findByRole("checkbox", {
      name: "Show cluster-based heatmap",
    });

    fireEvent.click(checkbox);

    expect(
      await screen.findByText(
        "Could not generate cluster heatmap: too few values",
      ),
    ).toBeDefined();
    expect(checkbox.getAttribute("aria-checked")).toBe("false");
  });

  it("downloads the XLSX under Qt's file name", async () => {
    vi.mocked(exportXlsx).mockResolvedValue(new Blob(["xlsx"]));
    renderWithQuery(<ResultsCard onBack={vi.fn()} />);

    fireEvent.click(
      screen.getByRole("button", { name: "Export Results to XLSX" }),
    );

    await waitFor(() =>
      expect(saveBlob).toHaveBeenCalledWith(
        expect.any(Blob),
        "dematel_results.xlsx",
      ),
    );
    expect(exportXlsx).toHaveBeenCalledWith(REQUEST);
  });

  it("captures the summary in the browser and downloads summary.png", async () => {
    renderWithQuery(<ResultsCard onBack={vi.fn()} />);

    fireEvent.click(
      screen.getByRole("button", { name: "Export Summary to PNG" }),
    );

    await waitFor(() =>
      expect(saveBlob).toHaveBeenCalledWith(expect.any(Blob), "summary.png"),
    );
    expect(toBlob).toHaveBeenCalledOnce();
    expect(getChart).not.toHaveBeenCalled();
  });

  it("downloads charts at 300 dpi and shows a cluster export failure", async () => {
    vi.mocked(getChart).mockRejectedValue(
      new ApiError("Could not generate cluster heatmap: too few values", 422),
    );
    renderWithQuery(<ResultsCard onBack={vi.fn()} />);

    fireEvent.click(
      screen.getByRole("button", { name: "Export Cluster Heatmap to PNG" }),
    );

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Could not generate cluster heatmap: too few values",
    );
    expect(getChart).toHaveBeenCalledWith(REQUEST, "heatmap", "cluster", 300);
    expect(saveBlob).not.toHaveBeenCalled();
  });

  it("marks results out of date after a change and re-runs with the new inputs", async () => {
    vi.mocked(runAnalysis).mockResolvedValue(ANALYSIS_DATA);
    renderWithQuery(<ResultsCard onBack={vi.fn()} />);

    store().setThreshold("mmde");
    expect(
      await screen.findByText(
        "Your inputs changed since this analysis. Run again to update.",
      ),
    ).toBeDefined();
    expect(screen.getByText("Classical DEMATEL")).toBeDefined();

    fireEvent.click(screen.getByRole("button", { name: "Re-run" }));

    await waitFor(() =>
      expect(store().snapshot?.threshold_method).toBe("mmde"),
    );
    expect(screen.queryByText(/Your inputs changed/)).toBeNull();
  });

  it("goes back to the inputs", () => {
    const onBack = vi.fn();
    renderWithQuery(<ResultsCard onBack={onBack} />);
    fireEvent.click(screen.getByRole("button", { name: "Back to inputs" }));
    expect(onBack).toHaveBeenCalledOnce();
  });
});
