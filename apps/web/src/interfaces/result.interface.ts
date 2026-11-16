import { z } from "zod";
import { apiResponseSchema } from "@/interfaces/api.interface";

const matrix = z.array(z.array(z.number()));
const tupleMatrix = z.array(z.array(z.array(z.number())));

const baseResultSchema = z.object({
  factors: z.array(z.string()),
  expert_weights: z.array(z.number()),
  r: z.array(z.number()),
  c: z.array(z.number()),
  prominence: z.array(z.number()),
  relation: z.array(z.number()),
  cause_group: z.array(z.string()),
  effect_group: z.array(z.string()),
  threshold_method: z.string(),
  threshold_value: z.number().nullish(),
  crisp_total_matrix: matrix,
});

export const crispResultSchema = baseResultSchema.extend({
  solver_type: z.literal("dematel"),
  direct_matrix: matrix,
  normalized_matrix: matrix,
  total_matrix: matrix,
});

export const fuzzyResultSchema = baseResultSchema.extend({
  solver_type: z.enum(["fuzzy_dematel", "fuzzy_z_dematel"]),
  fuzzy_direct_matrix: tupleMatrix,
  fuzzy_normalized_matrix: tupleMatrix,
  fuzzy_total_matrix: tupleMatrix,
  fuzzy_r: matrix,
  fuzzy_c: matrix,
  fuzzy_prominence: matrix,
  fuzzy_relation: matrix,
});

export const greyResultSchema = baseResultSchema.extend({
  solver_type: z.literal("grey_dematel"),
  grey_direct_matrix: tupleMatrix,
  grey_normalized_matrix: tupleMatrix,
  grey_total_matrix: tupleMatrix,
  grey_r: matrix,
  grey_c: matrix,
  grey_prominence: matrix,
  grey_relation: matrix,
});

/** The result, discriminated by `solver_type` (fuzzy and fuzzy Z share one shape). */
export const analysisResultSchema = z.union([
  crispResultSchema,
  fuzzyResultSchema,
  greyResultSchema,
]);

export const resultSummarySchema = z.object({
  result_type_label: z.string(),
  threshold_method_key: z.string(),
  threshold_method_label: z.string(),
  threshold_value: z.number().nullish(),
  driving_factor_count: z.number().int(),
  dependent_factor_count: z.number().int(),
  top_prominence: z.number(),
  strongest_relation: z.number(),
  prominence_ranking: z.array(
    z.object({
      factor: z.string(),
      prominence: z.number(),
      relation: z.number(),
      bar_ratio: z.number(),
    }),
  ),
});

export const analysisDataSchema = z.object({
  result: analysisResultSchema,
  summary: resultSummarySchema,
  corrected_weights: z.array(z.number()),
});

export const analysisResponseSchema = apiResponseSchema(analysisDataSchema);

export type CrispResult = z.infer<typeof crispResultSchema>;
export type FuzzyResult = z.infer<typeof fuzzyResultSchema>;
export type GreyResult = z.infer<typeof greyResultSchema>;
export type AnalysisResult = z.infer<typeof analysisResultSchema>;
export type ResultSummary = z.infer<typeof resultSummarySchema>;
export type AnalysisData = z.infer<typeof analysisDataSchema>;

/** A matrix cell or vector entry: a crisp number or a fuzzy/grey tuple. */
export type ResultValue = number | number[];

/** The three result matrices, in tab order. */
export type MatrixKind = "direct" | "normalized" | "total";

/** Charts the API renders. */
export type ChartKind = "causal-diagram" | "heatmap";

export type HeatmapMode = "standard" | "cluster";
