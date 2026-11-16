export const QUERY_KEYS = {
  SCALES: ["scales"],
  CHART: "chart",
} as const;

export const MUTATION_KEYS = {
  DEFAULT_WEIGHTS: ["weights", "defaults"],
  NORMALIZE_WEIGHTS: ["weights", "normalize"],
  RUN_ANALYSIS: ["analysis", "run"],
  IMPORT_MATRIX: ["imports", "matrix"],
  IMPORT_WORKBOOK: ["imports", "workbook"],
  EXPORT_FILE: ["export"],
  EXPLANATION: ["explanation"],
} as const;
