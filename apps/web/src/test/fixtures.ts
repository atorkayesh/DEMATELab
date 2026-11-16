import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import type { AnalysisData } from "@/interfaces/result.interface";
import type { MatrixScale, ScalesData } from "@/interfaces/scales.interface";

/** Test data shaped like the API's responses (see apps/api models). */

const STANDARD_TERMS = [
  "No influence",
  "Low influence",
  "Medium influence",
  "High influence",
  "Extreme influence",
];

export const SCALES: ScalesData = {
  standard: {
    solvers: ["dematel", "fuzzy_dematel", "grey_dematel"],
    terms: STANDARD_TERMS,
    default_label: "No influence",
    diagonal_label: "No influence",
    influence_terms: [],
    reliability_terms: [],
  },
  fuzzy_z: {
    solvers: ["fuzzy_z_dematel"],
    terms: [
      "No influence with VH reliability",
      "Low influence with H reliability",
    ],
    default_label: "No influence with VH reliability",
    diagonal_label: "No influence with VH reliability",
    influence_terms: ["No influence", "Low influence"],
    reliability_terms: ["VH", "H"],
  },
  solvers: [
    { key: "dematel", label: "DEMATEL" },
    { key: "fuzzy_dematel", label: "Fuzzy DEMATEL" },
    { key: "grey_dematel", label: "Grey DEMATEL" },
    { key: "fuzzy_z_dematel", label: "Fuzzy Z-DEMATEL" },
  ],
  thresholds: [
    { key: "average", label: "Average" },
    { key: "mmde", label: "Maximum Mean De-Entropy" },
  ],
  limits: {
    factors_min: 2,
    factors_max: 100,
    factors_default: 4,
    experts_min: 1,
    experts_max: 50,
    experts_default: 2,
  },
  weights: {
    decimals: 3,
    step: 0.001,
    sum_tolerance: 0.005,
    default_rule: "equal",
  },
};

export const STANDARD_SCALE: MatrixScale = {
  family: "standard",
  defaultLabel: "No influence",
  diagonalLabel: "No influence",
};

export const Z_SCALE: MatrixScale = {
  family: "fuzzy_z",
  defaultLabel: "No influence with VH reliability",
  diagonalLabel: "No influence with VH reliability",
};

export const REQUEST: AnalysisRequest = {
  solver_type: "dematel",
  threshold_method: "average",
  factors: ["A", "B"],
  experts: [
    {
      name: "Expert 1",
      weight: 1,
      matrix: [
        ["No influence", "High influence"],
        ["Low influence", "No influence"],
      ],
    },
  ],
};

export const ANALYSIS_DATA: AnalysisData = {
  result: {
    solver_type: "dematel",
    factors: ["A", "B"],
    expert_weights: [1],
    r: [0.75, 0.25],
    c: [0.25, 0.75],
    prominence: [1, 1],
    relation: [0.5, -0.5],
    cause_group: ["A"],
    effect_group: ["B"],
    threshold_method: "average",
    threshold_value: 0.25,
    crisp_total_matrix: [
      [0, 0.75],
      [0.25, 0],
    ],
    direct_matrix: [
      [0, 3],
      [1, 0],
    ],
    normalized_matrix: [
      [0, 1],
      [0.3333333, 0],
    ],
    total_matrix: [
      [0.123456, 0.75],
      [0.25, 0],
    ],
  },
  summary: {
    result_type_label: "Classical DEMATEL",
    threshold_method_key: "average",
    threshold_method_label: "Average",
    threshold_value: 0.25,
    driving_factor_count: 1,
    dependent_factor_count: 1,
    top_prominence: 1,
    strongest_relation: 0.5,
    prominence_ranking: [
      { factor: "B", prominence: 1, relation: -0.5, bar_ratio: 1 },
      { factor: "A", prominence: 1, relation: 0.5, bar_ratio: 1 },
    ],
  },
  corrected_weights: [1],
};

/** A JSON `Response` in the API's envelope. */
export function apiJson(data: unknown, status = 200): Response {
  return new Response(
    JSON.stringify(
      status < 400
        ? { success: true, message: null, data, metadata: null }
        : data,
    ),
    { status, headers: { "Content-Type": "application/json" } },
  );
}

/** A 4xx/5xx body with the API's public message. */
export function apiErrorBody(message: string, code = "invalid_input") {
  return { success: false, message, data: null, error: { code } };
}
