import type {
  AnalysisResult,
  MatrixKind,
  ResultValue,
} from "@/interfaces/result.interface";

/** A result matrix: crisp numbers, or fuzzy/grey tuples (the viewer's `_get_matrix_attr`). */
export function resultMatrix(
  result: AnalysisResult,
  kind: MatrixKind,
): ResultValue[][] {
  switch (result.solver_type) {
    case "dematel":
      return result[`${kind}_matrix`];
    case "grey_dematel":
      return result[`grey_${kind}_matrix`];
    default:
      return result[`fuzzy_${kind}_matrix`];
  }
}

/** R, C, prominence and relation per factor: tuples for fuzzy/grey, crisp numbers otherwise. */
export function resultScores(result: AnalysisResult): {
  tuples: boolean;
  rows: { factor: string; values: ResultValue[] }[];
} {
  const vectors: ResultValue[][] =
    result.solver_type === "dematel"
      ? [result.r, result.c, result.prominence, result.relation]
      : result.solver_type === "grey_dematel"
        ? [
            result.grey_r,
            result.grey_c,
            result.grey_prominence,
            result.grey_relation,
          ]
        : [
            result.fuzzy_r,
            result.fuzzy_c,
            result.fuzzy_prominence,
            result.fuzzy_relation,
          ];
  return {
    tuples: result.solver_type !== "dematel",
    rows: result.factors.map((factor, i) => ({
      factor,
      values: vectors.map((vector) => vector[i]),
    })),
  };
}

/** Whether the total relation matrix the charts use is present. */
export function hasTotalMatrix(result: AnalysisResult): boolean {
  return result.crisp_total_matrix.length > 0;
}
