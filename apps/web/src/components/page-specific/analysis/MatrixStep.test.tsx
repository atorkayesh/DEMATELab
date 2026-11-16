import { fireEvent, screen, waitFor } from "@testing-library/react";
import {
  afterAll,
  beforeAll,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";
import { ExpertMatrixStep } from "@/components/page-specific/analysis/ExpertMatrixStep";
import { importMatrix, importWorkbook } from "@/services/import.service";
import { useAnalysisStore } from "@/store/analysis.store";
import { MATRIX_GRID } from "@/constants/analysis.constants";
import { SCALES, STANDARD_SCALE, Z_SCALE } from "@/test/fixtures";
import { renderWithQuery, stubLayout } from "@/test/render";
import { ApiError } from "@/utils/api.utils";

vi.mock("@/services/import.service", () => ({
  importMatrix: vi.fn(),
  importWorkbook: vi.fn(),
}));

const store = () => useAnalysisStore.getState();
const nav = () => ({ number: 7, onAdvance: vi.fn(), onBack: vi.fn() });
const H = "High influence";

function setUp(solver = "dematel", scale = STANDARD_SCALE) {
  store().setSolver(solver, scale);
  store().setExpertCount(2, [0.5, 0.5]);
  store().setFactorCount(3);
}

function upload(testId: string) {
  const input = screen.getByTestId(testId);
  fireEvent.change(input, {
    target: { files: [new File(["x"], "m.xlsx")] },
  });
}

describe("ExpertMatrixStep", () => {
  let restoreLayout: () => void;
  beforeAll(() => {
    restoreLayout = stubLayout();
  });
  afterAll(() => restoreLayout());
  beforeEach(() => {
    store().reset();
    vi.mocked(importMatrix).mockReset();
    vi.mocked(importWorkbook).mockReset();
  });

  it("shows one select per cell with a fixed diagonal and highlights edits", () => {
    setUp();
    renderWithQuery(<ExpertMatrixStep expert={0} scales={SCALES} {...nav()} />);

    expect(screen.getByRole("heading").textContent).toBe(
      "Expert 1 of 2: Expert 1",
    );
    const cell = screen.getByRole("combobox", { name: "F1 → F2" });
    expect(
      (screen.getByRole("combobox", { name: "F1 → F1" }) as HTMLSelectElement)
        .disabled,
    ).toBe(true);
    expect(cell.querySelectorAll("option")).toHaveLength(5);

    fireEvent.change(cell, { target: { value: H } });
    expect(store().matrices[0][0][1]).toBe(H);
    expect(cell.getAttribute("data-edited")).toBe("true");
  });

  it("renders only the visible window of a 100 x 100 matrix", () => {
    store().setSolver("dematel", STANDARD_SCALE);
    store().setExpertCount(1, [1]);
    store().setFactorCount(100);
    renderWithQuery(<ExpertMatrixStep expert={0} scales={SCALES} {...nav()} />);

    // stubLayout's 1000 x 600 viewport, plus the overscan on both sides of each axis.
    const window = (viewport: number, item: number) =>
      Math.ceil(viewport / item) + 1 + 2 * MATRIX_GRID.OVERSCAN;
    const cells = screen.getAllByRole("combobox").length;
    expect(cells).toBeGreaterThanOrEqual(
      Math.floor(600 / MATRIX_GRID.ROW_HEIGHT) *
        Math.floor(1000 / MATRIX_GRID.CELL_WIDTH.standard),
    );
    expect(cells).toBeLessThanOrEqual(
      window(600, MATRIX_GRID.ROW_HEIGHT) *
        window(1000, MATRIX_GRID.CELL_WIDTH.standard),
    );
    expect(screen.getByRole("combobox", { name: "F1 → F2" })).toBeDefined();
    expect(screen.queryByRole("combobox", { name: "F100 → F99" })).toBeNull();
  });

  it("focuses the first editable cell, not the hidden file inputs", () => {
    setUp();
    renderWithQuery(<ExpertMatrixStep expert={0} scales={SCALES} {...nav()} />);
    expect(document.activeElement).toBe(
      screen.getByRole("combobox", { name: "F1 → F2" }),
    );
  });

  it("does not continue when Enter is pressed in a cell", () => {
    setUp();
    const props = nav();
    renderWithQuery(<ExpertMatrixStep expert={0} scales={SCALES} {...props} />);
    fireEvent.keyDown(screen.getByRole("combobox", { name: "F1 → F2" }), {
      key: "Enter",
    });
    expect(props.onAdvance).not.toHaveBeenCalled();
  });

  it("imports a matrix and renames the factors everywhere", async () => {
    setUp();
    vi.mocked(importMatrix).mockResolvedValue({
      factor_names: ["Cost", "Time", "Risk"],
      matrix: [
        ["No influence", H, H],
        ["No influence", "No influence", "No influence"],
        ["No influence", "No influence", "No influence"],
      ],
    });
    renderWithQuery(<ExpertMatrixStep expert={1} scales={SCALES} {...nav()} />);

    upload("matrix-file");

    await waitFor(() =>
      expect(store().factors).toEqual(["Cost", "Time", "Risk"]),
    );
    expect(vi.mocked(importMatrix).mock.calls[0][1]).toBe(3);
    expect(store().matrices[1][0]).toEqual(["No influence", H, H]);
    expect(screen.getByRole("combobox", { name: "Cost → Time" })).toBeDefined();
  });

  it("imports all experts from the first matrix step", async () => {
    setUp();
    vi.mocked(importWorkbook).mockResolvedValue({
      factor_names: null,
      matched_by: "order",
      matrices: [0, 1].map((e) => ({
        expert_name: `Expert ${e + 1}`,
        matrix: [
          ["No influence", H, "No influence"],
          ["No influence", "No influence", "No influence"],
          ["No influence", "No influence", "No influence"],
        ],
      })),
    });
    renderWithQuery(<ExpertMatrixStep expert={0} scales={SCALES} {...nav()} />);

    upload("workbook-file");

    await waitFor(() => expect(store().matrices[1][0][1]).toBe(H));
    expect(vi.mocked(importWorkbook).mock.calls[0][2]).toEqual([
      "Expert 1",
      "Expert 2",
    ]);
  });

  it("shows import errors inline with Qt's prefix", async () => {
    setUp();
    vi.mocked(importMatrix).mockRejectedValue(
      new ApiError("Imported matrix must be exactly 3 x 3.", 422),
    );
    renderWithQuery(<ExpertMatrixStep expert={0} scales={SCALES} {...nav()} />);

    upload("matrix-file");

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Import failed: Imported matrix must be exactly 3 x 3.",
    );
  });

  it("hides Import All only on later steps", () => {
    setUp();
    renderWithQuery(<ExpertMatrixStep expert={1} scales={SCALES} {...nav()} />);
    expect(
      screen.queryByRole("button", { name: "Import All Experts from XLSX" }),
    ).toBeNull();
    expect(
      screen.getByRole("button", { name: "Import Matrix from XLSX" }),
    ).toBeDefined();
  });

  it("for Z hides Import All and explains why import is not available", () => {
    setUp("fuzzy_z_dematel", Z_SCALE);
    renderWithQuery(<ExpertMatrixStep expert={0} scales={SCALES} {...nav()} />);

    expect(
      screen.queryByRole("button", { name: "Import All Experts from XLSX" }),
    ).toBeNull();
    fireEvent.click(
      screen.getByRole("button", { name: "Import Matrix from XLSX" }),
    );
    expect(screen.getByText("Import Not Available")).toBeDefined();
    expect(
      screen.getByText(/supports only the standard linguistic scale/),
    ).toBeDefined();
    expect(
      screen
        .getByRole("combobox", { name: "F1 → F2" })
        .querySelectorAll("option"),
    ).toHaveLength(2);
  });
});
