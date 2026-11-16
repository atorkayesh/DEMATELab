import { z } from "zod";
import { apiResponseSchema } from "@/interfaces/api.interface";

/** One expert as sent to the API: name, weight, and the linguistic matrix (row = influencing factor). */
export interface ExpertRequest {
  name: string;
  weight: number;
  matrix: string[][];
}

/** Body of every analysis-derived endpoint (analysis, export, charts, explanation). */
export interface AnalysisRequest {
  solver_type: string;
  threshold_method: string;
  factors: string[];
  experts: ExpertRequest[];
}

/** Expert name and weight as entered. */
export interface ExpertInput {
  name: string;
  weight: number;
}

export const weightsDataSchema = z.object({ weights: z.array(z.number()) });

export const weightsResponseSchema = apiResponseSchema(weightsDataSchema);

/** Ids of the flow steps; `matrix-{i}` is expert i's matrix (1-based). */
export type FixedStepId =
  | "solver"
  | "threshold"
  | "experts"
  | "factors"
  | "factor-names"
  | "expert-weights"
  | "review"
  | "results";

export type StepId = FixedStepId | `matrix-${number}`;

/** What the flow shell gives every question step. */
export interface StepProps {
  /** 1-based position shown above the question. */
  number: number;
  /** Mark the step answered and open the next one. */
  onAdvance: () => void;
  /** Open the previous step; null on the first step. */
  onBack: (() => void) | null;
}

/** Search params of `/`: the open step; anything invalid is dropped (the guard then redirects). */
export const flowSearchSchema = z.object({
  step: z.string().optional().catch(undefined),
});
