import { describe, expect, it } from "vitest";
import { STANDARD_SCALE } from "@/test/fixtures";
import {
  createMatrix,
  matrixHasEdits,
  resizeLosesEdits,
  resizeMatrix,
  resizeNames,
  withDiagonal,
} from "@/utils/matrix.utils";

const N = "No influence";
const H = "High influence";

describe("matrix utils", () => {
  it("creates default matrices with the no-influence diagonal", () => {
    expect(createMatrix(2, STANDARD_SCALE)).toEqual([
      [N, N],
      [N, N],
    ]);
  });

  it("keeps the remaining cells when growing or shrinking", () => {
    const matrix = [
      [N, H],
      [H, N],
    ];
    expect(resizeMatrix(matrix, 3, STANDARD_SCALE)).toEqual([
      [N, H, N],
      [H, N, N],
      [N, N, N],
    ]);
    expect(resizeMatrix(matrix, 1, STANDARD_SCALE)).toEqual([[N]]);
  });

  it("detects edits, and edits a shrink would drop", () => {
    const matrix = [
      [N, N, H],
      [N, N, N],
      [N, N, N],
    ];
    expect(matrixHasEdits(matrix, N)).toBe(true);
    expect(matrixHasEdits(createMatrix(3, STANDARD_SCALE), N)).toBe(false);
    expect(resizeLosesEdits(matrix, 2, N)).toBe(true);
    expect(resizeLosesEdits(matrix, 3, N)).toBe(false);
  });

  it("forces the diagonal of imported matrices", () => {
    expect(
      withDiagonal(
        [
          [H, H],
          [H, H],
        ],
        N,
      ),
    ).toEqual([
      [N, H],
      [H, N],
    ]);
  });

  it("resizes names keeping the entered ones", () => {
    expect(resizeNames(["X"], 3, (i) => `F${i + 1}`)).toEqual([
      "X",
      "F2",
      "F3",
    ]);
    expect(resizeNames(["X", "Y"], 1, (i) => `F${i + 1}`)).toEqual(["X"]);
  });
});
