import type { MatrixScale } from "@/interfaces/scales.interface";

/** A new `size x size` matrix: default cells, the diagonal set to the no-influence label. */
export function createMatrix(size: number, scale: MatrixScale): string[][] {
  return Array.from({ length: size }, (_, row) =>
    Array.from({ length: size }, (_, column) =>
      row === column ? scale.diagonalLabel : scale.defaultLabel,
    ),
  );
}

/** Resize keeping the cells of the remaining factors; new cells get the defaults. */
export function resizeMatrix(
  matrix: string[][],
  size: number,
  scale: MatrixScale,
): string[][] {
  return Array.from({ length: size }, (_, row) =>
    Array.from({ length: size }, (_, column) => {
      if (row === column) return scale.diagonalLabel;
      return matrix[row]?.[column] ?? scale.defaultLabel;
    }),
  );
}

/** Whether any off-diagonal cell differs from the default. */
export function matrixHasEdits(
  matrix: string[][],
  defaultLabel: string,
): boolean {
  return matrix.some((row, i) =>
    row.some((cell, j) => i !== j && cell !== defaultLabel),
  );
}

/** Whether shrinking to `size` would drop an edited cell (removed rows or columns). */
export function resizeLosesEdits(
  matrix: string[][],
  size: number,
  defaultLabel: string,
): boolean {
  return matrix.some((row, i) =>
    row.some(
      (cell, j) => i !== j && (i >= size || j >= size) && cell !== defaultLabel,
    ),
  );
}

/** Copy of an imported matrix with the diagonal forced to the no-influence label. */
export function withDiagonal(
  matrix: string[][],
  diagonalLabel: string,
): string[][] {
  return matrix.map((row, i) =>
    row.map((cell, j) => (i === j ? diagonalLabel : cell)),
  );
}

/** Default names `F1..Fn`, keeping the names already entered. */
export function resizeNames(
  names: string[],
  size: number,
  makeName: (index: number) => string,
): string[] {
  return Array.from({ length: size }, (_, i) => names[i] ?? makeName(i));
}
