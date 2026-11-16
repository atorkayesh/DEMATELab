import { beforeEach, describe, expect, it } from "vitest";
import { useAnalysisStore } from "@/store/analysis.store";
import {
  ANALYSIS_DATA,
  REQUEST,
  STANDARD_SCALE,
  Z_SCALE,
} from "@/test/fixtures";

const N = "No influence";
const H = "High influence";
const store = () => useAnalysisStore.getState();

/** Solver, 2 experts and 3 factors answered. */
function setUp() {
  store().setSolver("dematel", STANDARD_SCALE);
  store().setThreshold("average");
  store().setExpertCount(2, [0.5, 0.5]);
  store().setFactorCount(3);
}

describe("analysis store", () => {
  beforeEach(() => store().reset());

  it("creates default names, weights and matrices once the counts are known", () => {
    setUp();
    expect(store().factors).toEqual(["F1", "F2", "F3"]);
    expect(store().experts).toEqual([
      { name: "Expert 1", weight: 0.5 },
      { name: "Expert 2", weight: 0.5 },
    ]);
    expect(store().matrices).toHaveLength(2);
    expect(store().matrices[0][0]).toEqual([N, N, N]);
    expect(store().weightsReset).toBe(false);
  });

  it("keeps names and cells of the remaining factors when resized", () => {
    setUp();
    store().setFactorName(0, "Cost");
    store().setCell(0, 0, 1, H);
    store().setFactorCount(4);
    expect(store().factors).toEqual(["Cost", "F2", "F3", "F4"]);
    expect(store().matrices[0][0]).toEqual([N, H, N, N]);
    store().setFactorCount(2);
    expect(store().factors).toEqual(["Cost", "F2"]);
    expect(store().matrices[0]).toEqual([
      [N, H],
      [N, N],
    ]);
  });

  it("keeps remaining experts, adds defaults, resets weights and notes it", () => {
    setUp();
    store().setExpertName(0, "Ann");
    store().setCell(0, 1, 0, H);
    store().setExpertCount(3, [0.334, 0.333, 0.333]);
    expect(store().experts.map((expert) => expert.name)).toEqual([
      "Ann",
      "Expert 2",
      "Expert 3",
    ]);
    expect(store().experts.map((expert) => expert.weight)).toEqual([
      0.334, 0.333, 0.333,
    ]);
    expect(store().matrices[0][1][0]).toBe(H);
    expect(store().matrices[2][1][0]).toBe(N);
    expect(store().weightsReset).toBe(true);
    store().setExpertCount(1, [1]);
    expect(store().matrices).toHaveLength(1);
    expect(store().experts).toEqual([{ name: "Ann", weight: 1 }]);
  });

  it("forgets removed experts' matrix steps, so adding them back is unanswered", () => {
    setUp();
    store().markAnswered("matrix-1");
    store().markAnswered("matrix-2");
    store().setExpertCount(1, [1]);
    expect(store().answered).toEqual(["matrix-1"]);
    store().setExpertCount(2, [0.5, 0.5]);
    expect(store().answered).toEqual(["matrix-1"]);
  });

  it("keeps matrices within a solver family and resets them across families", () => {
    setUp();
    store().setCell(0, 0, 1, H);
    store().setSolver("grey_dematel", STANDARD_SCALE);
    expect(store().matrices[0][0][1]).toBe(H);
    store().setSolver("fuzzy_z_dematel", Z_SCALE);
    expect(store().matrices[0][0]).toEqual([
      Z_SCALE.defaultLabel,
      Z_SCALE.defaultLabel,
      Z_SCALE.defaultLabel,
    ]);
  });

  it("changes only the edited row, so other cells keep their identity", () => {
    setUp();
    const before = store().matrices;
    store().setCell(1, 2, 0, H);
    const after = store().matrices;
    expect(after[0]).toBe(before[0]);
    expect(after[1][0]).toBe(before[1][0]);
    expect(after[1][2]).not.toBe(before[1][2]);
  });

  it("applies imports with the diagonal forced, and renames factors", () => {
    setUp();
    store().applyImportedMatrix(1, [
      [H, H, H],
      [H, H, H],
      [H, H, H],
    ]);
    expect(store().matrices[1][1]).toEqual([H, N, H]);
    store().applyImportedWorkbook([
      [
        [H, H, H],
        [N, N, N],
        [N, N, N],
      ],
    ]);
    expect(store().matrices[0][0]).toEqual([N, H, H]);
    expect(store().matrices[1][1]).toEqual([H, N, H]);
    store().renameFactors(["X", "Y", "Z"]);
    expect(store().factors).toEqual(["X", "Y", "Z"]);
  });

  it("writes corrected weights back and records answered steps once", () => {
    setUp();
    store().applyCorrectedWeights([0.6, 0.4]);
    expect(store().experts.map((expert) => expert.weight)).toEqual([0.6, 0.4]);
    store().markAnswered("solver");
    store().markAnswered("solver");
    expect(store().answered).toEqual(["solver"]);
  });

  it("stores results with their request snapshot and its hash", () => {
    store().setResults(REQUEST, ANALYSIS_DATA);
    expect(store().snapshot).toBe(REQUEST);
    expect(store().results).toBe(ANALYSIS_DATA);
    expect(store().snapshotHash).not.toBe("");
  });
});
