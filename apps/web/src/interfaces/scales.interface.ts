import { z } from "zod";
import { apiResponseSchema } from "@/interfaces/api.interface";

/** A selectable value and its label (solvers, threshold methods). */
export const optionSchema = z.object({ key: z.string(), label: z.string() });

/** Linguistic terms of a solver family; new cells and the diagonal use its labels. */
export const scaleFamilySchema = z.object({
  solvers: z.array(z.string()),
  terms: z.array(z.string()),
  default_label: z.string(),
  diagonal_label: z.string(),
  influence_terms: z.array(z.string()).default([]),
  reliability_terms: z.array(z.string()).default([]),
});

export const scalesDataSchema = z.object({
  standard: scaleFamilySchema,
  fuzzy_z: scaleFamilySchema,
  solvers: z.array(optionSchema),
  thresholds: z.array(optionSchema),
  limits: z.object({
    factors_min: z.number().int(),
    factors_max: z.number().int(),
    factors_default: z.number().int(),
    experts_min: z.number().int(),
    experts_max: z.number().int(),
    experts_default: z.number().int(),
  }),
  weights: z.object({
    decimals: z.number().int(),
    step: z.number(),
    sum_tolerance: z.number(),
    default_rule: z.string(),
  }),
});

export const scalesResponseSchema = apiResponseSchema(scalesDataSchema);

export type Option = z.infer<typeof optionSchema>;
export type ScaleFamily = z.infer<typeof scaleFamilySchema>;
export type ScalesData = z.infer<typeof scalesDataSchema>;

/** Which family a solver belongs to: its terms decide the matrix values. */
export type ScaleFamilyKey = "standard" | "fuzzy_z";

/** The family fields the store needs to fill and reset matrices. */
export interface MatrixScale {
  family: ScaleFamilyKey;
  defaultLabel: string;
  diagonalLabel: string;
}
