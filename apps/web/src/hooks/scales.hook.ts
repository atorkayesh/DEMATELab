import { useQuery } from "@tanstack/react-query";
import { QUERY_KEYS } from "@/constants/query.constants";
import type { MatrixScale, ScalesData } from "@/interfaces/scales.interface";
import { getScales } from "@/services/scales.service";

/** Scales, options and limits from the API; they never change while the app runs. */
export function useScales() {
  return useQuery({
    queryKey: QUERY_KEYS.SCALES,
    queryFn: getScales,
    staleTime: Number.POSITIVE_INFINITY,
  });
}

/** The matrix scale of `solver`: the fuzzy Z family for its solvers, the standard one otherwise. */
export function scaleForSolver(
  scales: ScalesData,
  solver: string,
): MatrixScale {
  const isZ = scales.fuzzy_z.solvers.includes(solver);
  const family = isZ ? scales.fuzzy_z : scales.standard;
  return {
    family: isZ ? "fuzzy_z" : "standard",
    defaultLabel: family.default_label,
    diagonalLabel: family.diagonal_label,
  };
}

/** Terms a matrix cell can take for `scale`. */
export function termsForScale(
  scales: ScalesData,
  scale: MatrixScale,
): string[] {
  return scale.family === "fuzzy_z"
    ? scales.fuzzy_z.terms
    : scales.standard.terms;
}
